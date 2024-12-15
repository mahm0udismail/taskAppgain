from models import Product
from app import db, mail
from flask_mail import Message
import requests
import paypalrestsdk
from dotenv import load_dotenv
import os

load_dotenv()
paypal_client_id = os.getenv("PAYPAL_CLIENT_ID")
paypal_client_secret = os.getenv("PAYPAL_CLIENT_SECRET")

# Configure PayPal SDK
paypalrestsdk.configure({
    "mode": "sandbox",  # Use "live" for production
    "client_id": paypal_client_id,  # Replace with your PayPal sandbox app client ID
    "client_secret": paypal_client_secret  # Replace with your PayPal sandbox app client secret
})

def validate_stock(product_id, quantity):
    product = Product.query.get(product_id)
    return product and product.stock >= quantity



def process_payment(payment_details):
    """
    Process payment using PayPal
    """
    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"
        },
        "transactions": [{
            "amount": {
                "total": str(payment_details['amount']),
                "currency": "USD"
            },
            "description": f"Purchase for product ID {payment_details.get('product_id')}"
        }],
        "redirect_urls": {
            "return_url": "http://localhost:5000/payment/execute",
            "cancel_url": "http://localhost:5000/payment/cancel"
        }
    })

    if payment.create():
        # Return the approval URL for the user to approve the payment
        for link in payment.links:
            if link.rel == "approval_url":
                return link.href
    else:
        print(payment.error)  # Log error for debugging
        return None
    


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
