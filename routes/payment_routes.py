from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.payment_service import PaymentService

payment_bp = Blueprint("payment", __name__)

# ✅ Generate Razorpay Order (Frontend Calls This First)
@payment_bp.route("/create-payment", methods=["POST"])
@jwt_required()
def create_payment():
    """Creates a Razorpay order for fine payment."""
    user_id = get_jwt_identity()
    data = request.json
    amount = data.get("amount")

    return jsonify(PaymentService.create_payment(user_id, amount))

# ✅ Confirm Payment (Razorpay Webhook or User Confirmation)
@payment_bp.route("/confirm-payment", methods=["POST"])
@jwt_required()
def confirm_payment():
    """Confirms a successful payment and marks fines as paid."""
    user_id = get_jwt_identity()
    data = request.json
    transaction_id = data.get("transaction_id")
    razorpay_payment_id = data.get("razorpay_payment_id")
    amount = data.get("amount")

    return jsonify(PaymentService.confirm_payment(user_id, transaction_id, razorpay_payment_id, amount))
