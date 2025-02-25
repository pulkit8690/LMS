# services/payment_service.py

import razorpay
import os
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from flask import jsonify

# Import the single db instance
from models import db
from models.transaction_model import BorrowedBook, PaymentRecord

# Load Razorpay API Key from environment variables
razorpay_client = razorpay.Client(auth=(
    os.getenv("RAZORPAY_KEY_ID"),
    os.getenv("RAZORPAY_SECRET_KEY")
))

class PaymentService:
    """Handles fine payments via Razorpay API."""

    @staticmethod
    def create_payment(user_id, amount):
        """Creates a Razorpay order for fine payment."""
        try:
            amount = float(amount)  # Ensure amount is a valid number
            if amount <= 0:
                return jsonify({"error": "Invalid payment amount"}), 400

            order = razorpay_client.order.create({
                "amount": int(amount * 100),  # Convert to paisa
                "currency": "INR",
                "payment_capture": "1",  # Auto-capture payment
                "notes": {"user_id": user_id}
            })

            return jsonify({"order_id": order["id"], "amount": amount}), 200

        except ValueError:
            return jsonify({"error": "Invalid amount format"}), 400
        except razorpay.errors.BadRequestError as e:
            return jsonify({"error": f"Razorpay error: {str(e)}"}), 400
        except Exception as e:
            return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

    @staticmethod
    def confirm_payment(user_id, transaction_id, razorpay_payment_id, amount):
        """Stores successful payment in the database and clears fines."""
        try:
            # Check if this transaction was already processed
            existing_payment = PaymentRecord.query.filter_by(transaction_id=transaction_id).first()
            if existing_payment:
                return jsonify({"error": "Transaction already processed"}), 400

            # Mark any pending fines as paid
            pending_fines = BorrowedBook.query.filter(
                BorrowedBook.user_id == user_id,
                BorrowedBook.fine_amount > 0,
                BorrowedBook.fine_paid.is_(False)
            ).all()

            if not pending_fines:
                return jsonify({"message": "No pending fines to pay."}), 200

            for fine in pending_fines:
                fine.fine_paid = True

            # Store a new payment record
            payment_record = PaymentRecord(
                user_id=user_id,
                amount=amount,
                transaction_id=transaction_id,
                razorpay_payment_id=razorpay_payment_id,
                payment_status="completed"
            )

            db.session.add(payment_record)
            db.session.commit()
            return jsonify({"message": "Fine payment successful"}), 200

        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({"error": f"Database error: {str(e)}"}), 500
        except Exception as e:
            return jsonify({"error": f"Unexpected error: {str(e)}"}), 500
