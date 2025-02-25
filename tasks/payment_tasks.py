# tasks/payment_tasks.py

from celery_config import celery
from services.payment_service import PaymentService

@celery.task
def create_payment_task(user_id, amount):
    """
    Example Celery task to create a new Razorpay order asynchronously.
    """
    return PaymentService.create_payment(user_id, amount)

@celery.task
def confirm_payment_task(user_id, transaction_id, razorpay_payment_id, amount):
    """
    Example Celery task to confirm a payment asynchronously.
    """
    return PaymentService.confirm_payment(user_id, transaction_id, razorpay_payment_id, amount)
