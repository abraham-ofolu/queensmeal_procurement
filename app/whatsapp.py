import os
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

# Load credentials ONLY from environment variables
TWILIO_SID = os.environ.get("TWILIO_SID")
TWILIO_TOKEN = os.environ.get("TWILIO_TOKEN")
TWILIO_WHATSAPP_FROM = os.environ.get("TWILIO_WHATSAPP_FROM")
DIRECTOR_PHONE = os.environ.get("DIRECTOR_PHONE")


def send_whatsapp(message: str):
    """
    Production-safe WhatsApp sender.
    - Never crashes the app
    - Uses env vars only
    - Falls back to console logging
    """

    # If credentials are missing → simulate
    if not all([TWILIO_SID, TWILIO_TOKEN, TWILIO_WHATSAPP_FROM, DIRECTOR_PHONE]):
        print("📱 WhatsApp (SIMULATION MODE)")
        print(message)
        print("-" * 60)
        return

    try:
        client = Client(TWILIO_SID, TWILIO_TOKEN)
        client.messages.create(
            from_=TWILIO_WHATSAPP_FROM,
            to=DIRECTOR_PHONE,
            body=message,
        )
        print("📱 WhatsApp sent successfully")

    except TwilioRestException as e:
        # NEVER break procurement workflow
        print("⚠️ WhatsApp FAILED — non-blocking")
        print(str(e))
        print("Message content:")
        print(message)
        print("-" * 60)
