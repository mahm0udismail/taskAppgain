# from flask import Flask, request, jsonify
# from flask_sqlalchemy import SQLAlchemy
# from flask_mail import Mail, Message
# import os
# from services import validate_stock, process_payment, send_email

# app = Flask(__name__)

# # Configurations
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///orders.db'
# app.config['MAIL_SERVER'] = 'smtp.gmail.com'
# app.config['MAIL_PORT'] = 587
# app.config['MAIL_USE_TLS'] = True
# app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
# app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')

# db = SQLAlchemy(app)
# mail = Mail(app)

# # Models
# from models import Product, Order

# @app.route('/order', methods=['POST'])
# def place_order():
#     data = request.json
#     product_id = data['product_id']
#     quantity = data['quantity']
#     customer_email = data['email']

#     # Validate stock
#     if not validate_stock(product_id, quantity):
#         return jsonify({"error": "Insufficient stock"}), 400

#     # Process payment
#     payment_status = process_payment(data['payment_details'])
#     if not payment_status:
#         return jsonify({"error": "Payment failed"}), 400

#     # Update stock and save order
#     product = Product.query.get(product_id)
#     product.stock -= quantity
#     db.session.commit()

#     order = Order(product_id=product_id, quantity=quantity, email=customer_email)
#     db.session.add(order)
#     db.session.commit()

#     # Send confirmation email
#     send_email(customer_email, order)

#     return jsonify({"message": "Order placed successfully", "order_id": order.id}), 201

# if __name__ == '__main__':
#     app.run(debug=True)




from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail

# Initialize extensions
db = SQLAlchemy()
mail = Mail()

def create_app():
    app = Flask(__name__)

    # Configurations
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://your_username:your_password@localhost/your_database_name'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'your-email@gmail.com'
    app.config['MAIL_PASSWORD'] = 'your-email-password'

    # Initialize extensions
    db.init_app(app)
    mail.init_app(app)

    # Import models and create database tables
    with app.app_context():
        from models import Product, Order  # Avoid circular import
        db.create_all()

    # Register routes
    from routes import order_bp
    app.register_blueprint(order_bp)

    return app
