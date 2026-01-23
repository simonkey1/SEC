import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv


class EmailNotifier:

    def __init__(self):
        load_dotenv()
        self.user = os.environ.get("GMAIL_USER")
        self.key: str = os.environ.get("GMAIL_APP_PASSWORD")
        self.alert = os.environ.get("ALERT_EMAIL")
        self.notifications_enabled = (
            os.getenv("EMAIL_NOTIFICATIONS_ENABLED", "false").lower() == "true"
        )
        self.port = 465
        self.host = "smtp.gmail.com"

    def _send_email(self, subject, body):
        if not self.notifications_enabled:
            return
        msg = MIMEMultipart()

        msg["From"] = self.user
        msg["To"] = self.alert
        msg["Subject"] = subject

        msg.attach(MIMEText(body, "html"))
        try:
            server = smtplib.SMTP_SSL(self.host, self.port)
            server.login(self.user, self.key)
            server.send_message(msg)
            server.quit()
        except Exception as e:
            print(f"Error enviando email: {e}")

    def send_capacity_alert(self, porcentaje, size_mb, total_filas):

        subject = f"⚠️ Alerta: Base de datos al {porcentaje}%"

        body = f"""
                    <h2>Alerta de Capacidad</h2>
                    <p>Tu base de datos está al {porcentaje}%</p>
                    <ul>
                        <li>Tamaño: {size_mb} MB</li>
                        <li>Registros: {total_filas}</li>
                    </ul>
                    """  # Triple comillas porque es multi-línea

        self._send_email(subject, body)
