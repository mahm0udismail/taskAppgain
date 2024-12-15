from flask import Blueprint, request, jsonify
from models import Product, Order
from app import db
from services import validate_stock, process_payment, send_email
import paypalrestsdk

order_bp = Blueprint('orders', __name__)

@order_bp.route('/order', methods=['POST'])
def place_order():
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
    # send_email(customer_email, order)
    
    # Return approval URL for payment
    return jsonify({
        "message": "Order created successfully. Approve payment to proceed.",
        "order_id": order.id,
        "approval_url": approval_url
    }), 201


@order_bp.route('/products', methods=['GET'])
def get_all_products():
    products = Product.query.all()
    result = [
        {
            "id": product.id, 
            "name": product.name, 
            "price": product.price,
            "stock":product.stock,
        }
        for product in products
    ]
    return jsonify(result)

@order_bp.route('/orders', methods=['GET'])
def get_all_orders():
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



@order_bp.route('/payment/execute', methods=['POST'])
def execute_payment():
    payment_id = request.json.get('payment_id')
    payer_id = request.json.get('payer_id')

    payment = paypalrestsdk.Payment.find(payment_id)

    if payment.execute({"payer_id": payer_id}):
        # Update order status to "Completed"
        order = Order.query.filter_by(id=request.json.get('order_id')).first()
        if order:
            order.status = "Completed"
            db.session.commit()

        return jsonify({"message": "Payment executed successfully", "order_id": order.id}), 200
    else:
        print(payment.error)  # Log error for debugging
        return jsonify({"error": "Payment execution failed"}), 400