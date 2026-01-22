import smtplib
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

class EmailNotifier:
    """Gestor centralizado de notificaciones por email."""
    
    def __init__(self):
        load_dotenv()
        self.sender = os.getenv("EMAIL_SENDER")
        self.password = os.getenv("EMAIL_PASSWORD")
        self.recipient = os.getenv("EMAIL_RECIPIENT")
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.enabled = os.getenv("EMAIL_NOTIFICATIONS_ENABLED", "true").lower() == "true"

        if not all([self.sender, self.password, self.recipient]):
            logger.warning("⚠️ Credenciales de email incompletas. Las notificaciones no funcionarán.")
    
    def _send_email(self, subject: str, body: str):
        """Método interno para enviar emails.
        
        Args:
            subject (str): Asunto del email
            body (str): Cuerpo del mensaje
        """

        if not self.enabled:  # Nueva validación
            logger.info(f"📧 [SIMULADO] Email: {subject}")
            return

        try:
            msg = MIMEText(body, 'plain', 'utf-8')
            msg['Subject'] = subject
            msg['From'] = self.sender
            msg['To'] = self.recipient

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender, self.password)
                server.sendmail(self.sender, self.recipient, msg.as_string())
            
            logger.info(f"📧 Email enviado: {subject}")
            
        except Exception as e:
            logger.error(f"❌ Error enviando email: {e}")
    
    def send_capacity_alert(self, porcentaje: float, size_mb: float):
        """Alerta de capacidad de base de datos."""
        subject = f"⚠️ Base de datos al {porcentaje:.1f}% de capacidad"
        body = f"""
Base de datos de cortes eléctricos - Alerta de capacidad

📊 Uso actual: {porcentaje:.2f}%
💾 Tamaño: {size_mb:.2f} MB / 500 MB (free tier)

⚠️ Acciones recomendadas:
- Ejecutar limpieza de datos antiguos (cleanup_old_data.py)
- Revisar políticas de retención
- Considerar migración a plan pago si es necesario

--
Sistema de Monitoreo de Cortes Eléctricos
        """
        self._send_email(subject, body)
    
    def send_scraper_error(self, error_msg: str, intentos: int):
        """Alerta de error en el scraper."""
        subject = f"🔴 Error en scraper SEC (Intento {intentos})"
        body = f"""
El scraper de datos SEC ha fallado.

❌ Error: {error_msg}
🔄 Intentos realizados: {intentos}

El sistema continuará intentando automáticamente.

--
Sistema de Monitoreo de Cortes Eléctricos
        """
        self._send_email(subject, body)
    
    def send_circuit_breaker_open(self, failures: int):
        """Alerta de Circuit Breaker abierto."""
        subject = "🚨 Circuit Breaker ABIERTO - Scraper detenido"
        body = f"""
El Circuit Breaker se ha activado por múltiples fallos consecutivos.

⚠️ Fallos detectados: {failures}
🛑 Estado: OPEN (scraper detenido temporalmente)

El sistema se reactivará automáticamente después del período de cooldown.

--
Sistema de Monitoreo de Cortes Eléctricos
        """
        self._send_email(subject, body)
    
    def send_data_quality_alert(self, issue: str):
        """Alerta de calidad de datos."""
        subject = "⚠️ Problema de calidad de datos"
        body = f"""
Se detectó un problema en la calidad de los datos scrapeados.

🔍 Problema: {issue}

Revisa los logs para más detalles.

--
Sistema de Monitoreo de Cortes Eléctricos
        """
        self._send_email(subject, body)


# Instancia global para reutilizar
notifier = EmailNotifier()

# Funciones de conveniencia (backward compatibility)
def send_capacity_alert(porcentaje: float, size_mb: float):
    """Wrapper para compatibilidad con código existente."""
    notifier.send_capacity_alert(porcentaje, size_mb)

def send_email(subject: str, body: str):
    """Wrapper genérico."""
    notifier._send_email(subject, body)