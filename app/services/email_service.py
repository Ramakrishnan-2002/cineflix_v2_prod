from fastapi import BackgroundTasks
from fastapi_mail import MessageSchema, MessageType
from ..configs.mailer import mail
from ..middlewares.logger import get_logger

logger = get_logger(__name__)

class EmailService:
    @staticmethod
    async def send_email_async(recipients: list[str], subject:str, body:str):
        message = MessageSchema(subject=subject, recipients=recipients ,body=body,subtype=MessageType.html)
        await mail.send_message(message)
        logger.info(f"Email sent to {', '.join(recipients)}")
        return {"message": "email has been sent"}
    
    @classmethod
    def send_password_reset_email(cls, background_tasks: BackgroundTasks, email:str,name:str,token:str ):
        logger.info(f"Scheduling password reset email for {email}")
        reset_link = f"https://localhost:8000/reset-password?token={token}"
        email_body = f"""
        <p>Hi {name},</p>
        <p>You requested a password reset. Click the link below to reset your password:</p>
        <p><a href="{reset_link}">Reset Password</a></p>
        <p>If you did not request a password reset, please ignore this email.</p>
        """
        background_tasks.add_task(cls.send_email_async, recipients=[email], subject="Password Reset Request", body=email_body)
        logger.info(f"Password reset email scheduled for {email}")
        return {"message": "Password reset email scheduled"}

email_service = EmailService()