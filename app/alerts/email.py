from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from dotenv import load_dotenv
import os

# Load .env variables
load_dotenv()

conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("ALERT_EMAIL"),
    MAIL_PASSWORD=os.getenv("ALERT_EMAIL_PASSWORD"),
    MAIL_FROM=os.getenv("ALERT_EMAIL"),
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",

    # ✅ CORRECT FLAGS (NEW VERSION)
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,

    USE_CREDENTIALS=True
)

async def send_alert_email(subject: str, body: str, to_email: str):
    message = MessageSchema(
        subject=subject,
        recipients=[to_email],
        body=body,
        subtype="plain"
    )

    fm = FastMail(conf)
    await fm.send_message(message)
