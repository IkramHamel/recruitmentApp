import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
from src.core.config import config
from src.internal.notification.mailing.schemas import MailRequest,BulkMailRequest


# Function to send a single email
def send_mail(email_request: MailRequest):
    """Function to send a single email."""

    # Check if the SMTP environment variables are set
    if not all([config.SMTP_SENDER_EMAIL, config.SMTP_SENDER_PASSWORD, config.SMTP_SERVER]):
        raise ValueError("SMTP configuration is missing in the environment variables.")

    try:
        # Set up the server and login
        with smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT) as server:
            server.starttls()  # Secure the connection
            server.login(config.SMTP_SENDER_EMAIL, config.SMTP_SENDER_PASSWORD)
            
            # Prepare the email content
            msg = MIMEMultipart()
            msg['From'] = formataddr(('Sender', config.SMTP_SENDER_EMAIL))
            msg['To'] = ', '.join(email_request.recipient_emails)
            msg['Subject'] = email_request.subject
            
            # Check content type and create the right MIME type
            if email_request.content_type == 'html':
                msg.attach(MIMEText(email_request.body, 'html'))
            else:
                msg.attach(MIMEText(email_request.body, 'plain'))

            # Send the email
            server.sendmail(config.SMTP_SENDER_EMAIL, email_request.recipient_emails, msg.as_string())
            print("Email sent successfully!")

    except Exception as e:
        print(f"Failed to send email: {e}")
        raise

# Function to send an email to multiple recipients
def bulk_send(email_request: BulkMailRequest):
    """Function to send an email to multiple recipients."""
    if not email_request.recipients:
        raise ValueError("Recipient emails must not be empty.")

    # Send the email individually to each recipient
    for recipient in email_request.recipients:
        # Prepare the single recipient MailRequest schema
        single_email_request = MailRequest(
            subject=email_request.subject,
            recipient_emails=[recipient],
            body=email_request.body,
            content_type=email_request.content_type
        )
        send_mail(single_email_request)
