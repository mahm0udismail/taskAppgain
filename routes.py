from flask import Blueprint, request, jsonify
from models import Product, Order
from app import db
from services import validate_stock, process_payment, send_email

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
    # payment_status = process_payment(data['payment_details'])
    # if not payment_status:
    #     return jsonify({"error": "Payment failed"}), 400

    # Update stock and save order
    product = Product.query.get(product_id)
    product.stock -= quantity
    db.session.commit()

    order = Order(product_id=product_id, quantity=quantity, email=customer_email)
    db.session.add(order)
    db.session.commit()

    # Send confirmation email
    # send_email(customer_email, order)

    return jsonify({"message": "Order placed successfully", "order_id": order.id}), 201




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