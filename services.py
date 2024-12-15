from models import Product
from app import db, mail
from flask_mail import Message
import requests

def validate_stock(product_id, quantity):
    product = Product.query.get(product_id)
    return product and product.stock >= quantity

def process_payment(payment_details):
    response = requests.post('http://mock-payment-gateway/api/pay', json=payment_details)
    return response.status_code == 200

def send_email(email, order):
    msg = Message(
        subject="Order Confirmation",
        recipients=[email],
        html=f"""
        <h1>Order Confirmation</h1>
        <p>Order ID: {order.id}</p>
        <p>Product ID: {order.product_id}</p>
        <p>Quantity: {order.quantity}</p>
        <p>Status: {order.status}</p>
        """,
    )
    mail.send(msg)
