import smtplib
import ssl
from django.core.mail.backends.smtp import EmailBackend

class InsecureEmailBackend(EmailBackend):
    def open(self):
        context = ssl._create_unverified_context()  # Disable SSL certificate verification
        self.connection = smtplib.SMTP(self.host, self.port)
        self.connection.starttls(context=context)  # Use the insecure context
        self.connection.login(self.username, self.password)
        return self.connection
