"""SMTP Client for sending encrypted emails via Gmail"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config.settings import SMTP_SERVER, SMTP_PORT


class SMTPClient:
    """Send emails via Gmail SMTP with SSL"""

    def __init__(self, email: str, app_password: str):
        self.email = email
        self.password = app_password

    def send(self, to: str, subject: str, body: str) -> dict:
        """
        Send an email.
        Returns {"success": True/False, "message": "..."}
        """
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = self.email
            msg['To'] = to
            msg['Subject'] = subject

            part = MIMEText(body, 'plain', 'utf-8')
            msg.attach(part)

            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
                server.login(self.email, self.password)
                server.sendmail(self.email, to, msg.as_string())

            return {"success": True, "message": f"Email sent successfully to {to}"}

        except smtplib.SMTPAuthenticationError:
            return {
                "success": False,
                "message": "Authentication failed. Check your Gmail App Password.",
            }
        except smtplib.SMTPException as e:
            return {"success": False, "message": f"SMTP error: {str(e)}"}
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}
