from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import settings
import smtplib

from logger import log_print


class EmailClient:

    def __init__(self):
        self.user = settings.EMAIL_USER
        self.password = settings.EMAIL_PASSWORD

    def send_email(self, recipient, subject, body):
        to = recipient if isinstance(recipient, list) else [recipient]
        if not recipient:
            return  # exit when there is no recipients

        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = self.user
        msg['To'] = ", ".join(to)
        msg.attach(MIMEText(body, 'html'))

        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.ehlo()
            server.starttls()
            server.login(self.user, self.password)
            server.sendmail(self.user, to, msg.as_string())
            server.close()
        except Exception as e:
            log_print(f"failed to send mail: {e}", message_type=3)
