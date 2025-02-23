import razorpay
import os
from backend.models import db, BorrowedBook, PaymentRecord
from datetime import datetime
from flask import jsonify

# ✅ Load Razorpay API Key
razorpay_client = razorpay.Client(auth=(os.getenv("RAZORPAY_KEY_ID"), os.getenv("RAZORPAY_SECRET_KEY")))

class PaymentService:
    """Handles fine payments via Razorpay API."""

    @staticmethod
    def create_payment(user_id, amount):
        """Creates a Razorpay order for fine payment."""
        if amount <= 0:
            return {"error": "Invalid amount"}, 400

        try:
            order = razorpay_client.order.create({
                "amount": int(amount * 100),  # Convert to paisa
                "currency": "INR",
                "payment_capture": "1",  # Auto-capture payment
                "notes": {"user_id": user_id}
            })
            return {"order_id": order["id"]}, 200

        except Exception as e:
            return {"error": str(e)}, 500

    @staticmethod
    def confirm_payment(user_id, transaction_id, razorpay_payment_id, amount):
        """Stores successful payment in the database and clears fines."""
        # ✅ Check if transaction ID already exists
        existing_payment = PaymentRecord.query.filter_by(transaction_id=transaction_id).first()
        if existing_payment:
            return {"error": "Transaction already processed"}, 400

        # ✅ Mark fines as paid
        pending_fines = BorrowedBook.query.filter(
            BorrowedBook.user_id == user_id, 
            BorrowedBook.fine_amount > 0,
            BorrowedBook.fine_paid.is_(False)
        ).all()

        if not pending_fines:
            return {"message": "No pending fines to pay."}, 200

        for fine in pending_fines:
            fine.fine_paid = True  # ✅ Mark fine as paid

        # ✅ Store payment record
        payment_record = PaymentRecord(
            user_id=user_id,
            amount=amount,
            transaction_id=transaction_id,
            razorpay_payment_id=razorpay_payment_id,
            payment_status="completed"
        )

        db.session.add(payment_record)
        db.session.commit()
        return {"message": "Fine payment successful"}, 200
