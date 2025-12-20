from flask_mail import Message
from app.extensions import mail

DEPARTMENTS = {
    "procurement": ["procurement@queensmeal.com"],
    "finance": ["finance@queensmeal.com"],
    "director": ["aofolu87@gmail.com"],
}

def notify(subject, body, to_roles=None, extra_emails=None):
    recipients = []

    if to_roles:
        for role in to_roles:
            recipients.extend(DEPARTMENTS.get(role, []))

    if extra_emails:
        recipients.extend(extra_emails)

    if not recipients:
        return

    msg = Message(
        subject=subject,
        recipients=list(set(recipients)),
        body=body,
    )

    mail.send(msg)
