# emailer.py
import os
import base64
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import SCOPES, SENDER_EMAIL


def authenticate_gmail():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds


def create_message(sender, to, subject, message_text):
    message = MIMEMultipart()
    message['to'] = to
    message['from'] = f"Your Name <{sender}>"
    message['subject'] = subject

    msg = MIMEText(message_text)
    message.attach(msg)

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {'raw': raw}


def send_message(service, user_id, message):
    try:
        message = service.users().messages().send(userId=user_id, body=message).execute()
        print(f"Message Id: {message['id']}")
        return message
    except HttpError as error:
        print(f'An error occurred: {error}')
        raise


def send_email(to, subject, message_text):
    creds = authenticate_gmail()
    service = build('gmail', 'v1', credentials=creds)
    message = create_message(SENDER_EMAIL, to, subject, message_text)
    return send_message(service, 'me', message)


if __name__ == "__main__":
    # Test the email sending functionality
    to_email = "test@example.com"
    subject = "Test Email"
    message_text = "This is a test email sent from the Email Scraper application."
    send_email(to_email, subject, message_text)