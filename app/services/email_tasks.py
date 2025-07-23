import logging
from app.services.celery import celery_app
from app.services.email_service import send_email

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, max_retries=3)
def send_appointment_confirmation(self, to_email: str, appointment_date: str):
    subject = "Підтвердження запису на обслуговування"
    message = f"Ваш запис на {appointment_date} створено!"
    try:
        send_email(to_email, subject, message)
        logger.info(f"Appointment confirmation email sent to {to_email}")
    except Exception as e:
        logger.error(f"Error sending appointment confirmation email to {to_email}: {e}")
        raise self.retry(exc=e, countdown=10)
