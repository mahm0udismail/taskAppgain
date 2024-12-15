from flask import Flask, request, jsonify

mock_app = Flask(__name__)

@mock_app.route('/api/pay', methods=['POST'])
def process_payment():
    data = request.json
    if 'card_number' in data and 'amount' in data:
        return jsonify({"status": "success"}), 200
    return jsonify({"error": "Invalid payment details"}), 400

if __name__ == '__main__':
    mock_app.run(port=5001)
