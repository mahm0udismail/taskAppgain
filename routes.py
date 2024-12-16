from flask import Blueprint, request, jsonify
from models import Product, Order
from app import db
from services import validate_stock, process_payment, send_email
import paypalrestsdk
from flask_jwt_extended import jwt_required

order_bp = Blueprint('orders', __name__)

@order_bp.route('/order', methods=['POST'])
@jwt_required()
def place_order():
    try:
        data = request.json
        product_id = data['product_id']
        quantity = data['quantity']
        customer_email = data['email']

        # Validate stock
        if not validate_stock(product_id, quantity):
            return jsonify({"error": "Insufficient stock"}), 400

        # Process payment
        approval_url = process_payment({
            "amount": data['payment_details']['amount'],
            "product_id": product_id
        })

        if not approval_url:
            return jsonify({"error": "Payment initiation failed"}), 400

        # Create an order with "Pending" status
        order = Order(product_id=product_id, quantity=quantity, email=customer_email, status="Pending")
        db.session.add(order)
        db.session.commit()

        # Send confirmation email
        from app import create_app
        app = create_app()  # Create app to get 'mail' instance
        try:
            send_email(customer_email, order, app.extensions['mail'])
        except Exception as e:
            # Log the error and notify the user
            return jsonify({"error": "Failed to send confirmation email", "details": str(e)}), 500

        # Return approval URL for payment
        return jsonify({
            "message": "Order created successfully. Approve payment to proceed.",
            "order_id": order.id,
            "approval_url": approval_url
        }), 201

    except KeyError as e:
        return jsonify({"error": f"Missing required data: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500


@order_bp.route('/products', methods=['GET'])
@jwt_required()
def get_all_products():
    try:
        products = Product.query.all()
        result = [
            {
                "id": product.id, 
                "name": product.name, 
                "price": product.price,
                "stock": product.stock,
            }
            for product in products
        ]
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": "An error occurred while fetching products", "details": str(e)}), 500


@order_bp.route('/orders', methods=['GET'])
@jwt_required()
def get_all_orders():
    try:
        # Query for all orders and join with products
        orders = db.session.query(
            Order.id,
            Product.name.label('product_name'),
            Order.quantity,
            Product.price,
            Order.email,
            Order.status
        ).join(Product, Product.id == Order.product_id).all()

        # Prepare the response
        result = [
            {
                "id": order.id,
                "product_name": order.product_name,
                "quantity": order.quantity,
                "total_price": order.quantity * order.price,
                "email": order.email,
                "status": order.status
            } for order in orders
        ]
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": "An error occurred while fetching orders", "details": str(e)}), 500


@order_bp.route('/payment/execute', methods=['POST'])
@jwt_required()
def execute_payment():
    try:
        payment_id = request.json.get('payment_id')
        payer_id = request.json.get('payer_id')

        payment = paypalrestsdk.Payment.find(payment_id)

        if payment.execute({"payer_id": payer_id}):
            # Update order status to "Completed"
            order = Order.query.filter_by(id=request.json.get('order_id')).first()
            if order:
                order.status = "Completed"
                db.session.commit()

            customer_email = order.email
            # Send confirmation email
            from app import create_app
            app = create_app()  # Create app to get 'mail' instance
            try:
                send_email(customer_email, order, app.extensions['mail'])
            except Exception as e:
                return jsonify({"error": "Failed to send confirmation email", "details": str(e)}), 500

            return jsonify({"message": "Payment executed successfully", "order_id": order.id}), 200
        else:
            print(payment.error)  # Log error for debugging
            return jsonify({"error": "Payment execution failed", "details": payment.error}), 400

    except KeyError as e:
        return jsonify({"error": f"Missing required data: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500
