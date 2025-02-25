# routes/payment_routes.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

# Import PaymentService (handles db logic inside)
from services.payment_service import PaymentService

payment_bp = Blueprint("payment", __name__)

# ✅ Generate Razorpay Order
@payment_bp.route("/create-payment", methods=["POST"])
@jwt_required()
def create_payment():
    user_id = get_jwt_identity()
    data = request.json
    amount = data.get("amount")

    if not amount or amount <= 0:
        return jsonify({"error": "Invalid payment amount"}), 400

    return jsonify(PaymentService.create_payment(user_id, amount))

# ✅ Confirm Payment
@payment_bp.route("/confirm-payment", methods=["POST"])
@jwt_required()
def confirm_payment():
    user_id = get_jwt_identity()
    data = request.json
    transaction_id = data.get("transaction_id")
    razorpay_payment_id = data.get("razorpay_payment_id")
    amount = data.get("amount")

    if not transaction_id or not razorpay_payment_id or not amount:
        return jsonify({"error": "Missing required payment details"}), 400

    return jsonify(PaymentService.confirm_payment(
        user_id, transaction_id, razorpay_payment_id, amount
    ))
