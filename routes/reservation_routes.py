# routes/reservation_routes.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

# Import the ReservationService (handles all db logic)
from services.reservation_service import ReservationService

reservation_bp = Blueprint("reservation", __name__)

# ✅ Reserve a Book
@reservation_bp.route("/reserve/<int:book_id>", methods=["POST"])
@jwt_required()
def reserve_book(book_id):
    user_id = get_jwt_identity()

    if not book_id or book_id <= 0:
        return jsonify({"error": "Invalid book ID"}), 400

    return jsonify(ReservationService.reserve_book(user_id, book_id))

# ✅ Cancel a Reservation
@reservation_bp.route("/cancel/<int:book_id>", methods=["DELETE"])
@jwt_required()
def cancel_reservation(book_id):
    user_id = get_jwt_identity()

    if not book_id or book_id <= 0:
        return jsonify({"error": "Invalid book ID"}), 400

    return jsonify(ReservationService.cancel_reservation(user_id, book_id))
