import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

class EmailNotifier:
    def __init__(self, smtp_server, smtp_port, sender_email, sender_password, recipient_emails):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.recipient_emails = recipient_emails

    def send_email(self, subject, message):
        try:
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = ", ".join(self.recipient_emails)
            msg['Subject'] = subject

            msg.attach(MIMEText(message, 'plain'))

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                print("Calling starttls...")
                server.starttls()
                print("starttls called successfully.")
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, self.recipient_emails, msg.as_string())

            print("Email sent successfully.")
        except Exception as e:
            logging.error(f"Failed to send email: {e}")
            print(f"Failed to send email: {e}")
