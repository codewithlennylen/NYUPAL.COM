# using SendGrid's Python Library
# https://github.com/sendgrid/sendgrid-python
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from ..config import SENDGRID_API_KEY, SENDGRID_DEFAULT_EMAIL


def send_mail(recipients: list, subject: str, body_text: str):
    """Use this function to send email(s) to a number of recipients

    Args:
        recipients (list): list of email addresses(str) to send email_message to
        subject (str): Email Subject
        body_text (str): email content (HTML Content)

    Returns:
        bool: Email status. True = success
    """
    message = Mail(
        from_email=SENDGRID_DEFAULT_EMAIL,  # works with sendgrid registered email address
        to_emails=recipients,
        subject=subject,
        html_content=body_text
    )

    #* send message
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(f"Email response.status_code: {response.status_code}")
        print(f"Email response.body: {response.body}")
        print(f"Email response.headers: {response.headers}")

        return True

    except Exception as e:
        print(f"Email Exception: {e}")

        return False
