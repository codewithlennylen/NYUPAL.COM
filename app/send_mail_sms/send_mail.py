# using SendGrid's Python Library
# https://github.com/sendgrid/sendgrid-python
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from app.config import SENDGRID_API_KEY, SENDGRID_DEFAULT_EMAIL


def send_mail(recipients: list, subject: str, body_text: str, sender: str = SENDGRID_DEFAULT_EMAIL):
    """Use this function to send email(s) to a number of recipients

    Args:
        recipients (list): list of email addresses(str) to send email_message to
        subject (str): Email Subject
        body_text (str): email content (HTML Content)

    Returns:
        bool: Email status. True = success
    """
    #! custom sender forbidden for now. We'll use default email (registered to sendgrid)
        
    recipients = recipients[0] if len(recipients) == 1 else recipients
    message = Mail(
        from_email=sender,  # works with sendgrid registered email address
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

        #? Hard-coded error code. Bad Idea but will work for now. [FAILED]
        # if response.status_code == 403:
        #     return False

        return True

    except Exception as e:
        print(f"Email Exception: {e}")

        return False
