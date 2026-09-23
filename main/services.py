import secrets
import string
import logging
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


def generate_temporary_password(length=10):
    """
    Generate a secure random temporary password containing uppercase,
    lowercase, digits, and special characters.
    """
    chars = string.ascii_letters + string.digits + "@#$%"
    # Ensure at least one from each required set
    pwd = [
        secrets.choice(string.ascii_uppercase),
        secrets.choice(string.ascii_lowercase),
        secrets.choice(string.digits),
        secrets.choice("@#$%"),
    ]
    pwd += [secrets.choice(chars) for _ in range(length - 4)]
    secrets.SystemRandom().shuffle(pwd)
    return "".join(pwd)


def send_temp_password_email(user, student, temp_password):
    """
    Send ONLY a temporary password to the student's email (no verification link).
    Used for new registrations.
    """
    try:
        subject = "Welcome to SCOPE INDIA – Your Temporary Login Password"
        message_body = (
            f"Dear {student.first_name} {student.last_name},\n\n"
            f"Welcome to SCOPE INDIA – Full Stack Training Institute!\n\n"
            f"Your registration has been received successfully.\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"  YOUR TEMPORARY LOGIN CREDENTIALS\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"  Email    : {user.email}\n"
            f"  Password : {temp_password}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"IMPORTANT: This is a one-time temporary password.\n"
            f"When you first log in, you will be prompted to create\n"
            f"your own permanent password.\n\n"
            f"Please keep this password safe and do NOT share it.\n\n"
            f"Best Regards,\n"
            f"SCOPE INDIA Admissions Team\n"
            f"https://scopeindia.org\n"
        )

        send_mail(
            subject=subject,
            message=message_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        logger.error(f"Error sending temp password email to {user.email}: {e}")
        return False


def send_password_reset_temp_email(user):
    """
    Generate a new temporary password, update the user's password, set
    force_password_change=True, and email the temp password (NO reset link).
    Used for forgot-password / password-reset flow.
    Returns (success: bool, temp_password: str)
    """
    try:
        temp_pwd = generate_temporary_password(10)

        # Update user's password to the new temp password
        user.set_password(temp_pwd)
        user.save()

        # Mark student as needing a password change
        if hasattr(user, 'student_profile'):
            student = user.student_profile
            student.force_password_change = True
            student.temp_password_created_at = timezone.now()
            student.save()

        subject = "SCOPE INDIA – Password Reset (Temporary Password)"
        message_body = (
            f"Hello {user.first_name or user.username},\n\n"
            f"We received a request to reset the password for your SCOPE INDIA account.\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"  YOUR TEMPORARY LOGIN PASSWORD\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"  Email    : {user.email}\n"
            f"  Password : {temp_pwd}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"Use this temporary password to log in. You will be asked\n"
            f"to create a new permanent password immediately after login.\n\n"
            f"If you did not request this reset, please contact us immediately.\n\n"
            f"Warm Regards,\n"
            f"SCOPE INDIA Support Team\n"
            f"https://scopeindia.org\n"
        )

        send_mail(
            subject=subject,
            message=message_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        return True, temp_pwd
    except Exception as e:
        logger.error(f"Error sending password reset email to {user.email}: {e}")
        return False, None


def send_contact_email(contact_instance):
    """
    Send notification to admin regarding contact submission and auto-reply to user.
    """
    try:
        # Email to Admin
        subject_admin = f"New Contact Enquiry: {contact_instance.subject}"
        message_admin = (
            f"You received a new enquiry via the SCOPE INDIA contact form.\n\n"
            f"From: {contact_instance.name} ({contact_instance.email})\n"
            f"Subject: {contact_instance.subject}\n"
            f"Message:\n{contact_instance.message}\n\n"
            f"Date: {contact_instance.created_at}"
        )
        send_mail(
            subject=subject_admin,
            message=message_admin,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['info@scopeindia.org', settings.DEFAULT_FROM_EMAIL],
            fail_silently=True,
        )

        # Auto-acknowledgement to sender
        subject_sender = "Thank you for contacting SCOPE INDIA"
        message_sender = (
            f"Dear {contact_instance.name},\n\n"
            f"Thank you for contacting SCOPE INDIA. We have received your message regarding '{contact_instance.subject}'.\n\n"
            f"Our academic counselors will get back to you shortly.\n\n"
            f"Best regards,\n"
            f"SCOPE INDIA Admissions Team"
        )
        send_mail(
            subject=subject_sender,
            message=message_sender,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[contact_instance.email],
            fail_silently=True,
        )
        return True
    except Exception as e:
        logger.error(f"Error in send_contact_email: {e}")
        return False
