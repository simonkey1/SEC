"""Sistema de notificaciones por email usando Gmail."""
import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)

def send_capacity_alert(porcentaje: float, size_mb: float):
    """Envía alerta por Gmail cuando la capacidad está alta.
    
    Args:
        porcentaje (float): Porcentaje de capacidad usado
        size_mb (float): Tamaño en MB de la base de datos
        
    Returns:
        bool: True si el email se envió correctamente
    """
    sender_email = os.getenv("GMAIL_USER")
    receiver_email = os.getenv("ALERT_EMAIL")
    password = os.getenv("GMAIL_APP_PASSWORD")
    
    if not all([sender_email, receiver_email, password]):
        logger.error("❌ Faltan credenciales de email en .env")
        return False
    
    # Crear mensaje
    message = MIMEMultipart("alternative")
    message["Subject"] = f"🚨 Alerta: Base de datos al {porcentaje:.1f}%"
    message["From"] = sender_email
    message["To"] = receiver_email
    
    # Cuerpo del email (texto plano)
    text = f"""
Hola,

Tu base de datos de Supabase ha alcanzado el {porcentaje:.1f}% de capacidad ({size_mb:.1f} MB / 500 MB).

Es momento de generar un backup manual. Ejecuta el siguiente comando en tu PC:

    python scripts/backup_manual.py

Esto descargará todos los datos históricos a tu máquina local.

--
Sistema de monitoreo automático SEC
Proyecto: Monitoreo de Cortes Eléctricos Chile
    """
    
    # Cuerpo HTML (opcional, más bonito)
    html = f"""
<html>
  <body>
    <h2 style="color: #ff6b6b;">🚨 Alerta de Capacidad</h2>
    <p>Tu base de datos de Supabase ha alcanzado:</p>
    <div style="background: #f8f9fa; padding: 20px; border-left: 4px solid #ff6b6b;">
      <h3 style="margin: 0;">{porcentaje:.1f}% de capacidad</h3>
      <p style="margin: 5px 0;">📊 {size_mb:.1f} MB / 500 MB</p>
    </div>
    <h3>Acción requerida:</h3>
    <p>Ejecuta el siguiente comando en tu PC para descargar el backup:</p>
    <pre style="background: #2d3748; color: #68d391; padding: 10px; border-radius: 5px;">
python scripts/backup_manual.py
    </pre>
    <hr>
    <p style="color: #718096; font-size: 12px;">
      Sistema de monitoreo automático<br>
      Proyecto: Monitoreo de Cortes Eléctricos Chile
    </p>
  </body>
</html>
    """
    
    # Adjuntar ambas versiones
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")
    message.attach(part1)
    message.attach(part2)
    
    try:
        # Conectar a Gmail SMTP
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        
        logger.info(f"✅ Email de alerta enviado a {receiver_email}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error enviando email: {e}")
        # Fallback: mostrar en consola
        print(f"\n{'='*60}")
        print(f"🚨 ALERTA: DB al {porcentaje:.1f}% ({size_mb:.1f} MB)")
        print("Ejecuta: python scripts/backup_manual.py")
        print(f"{'='*60}\n")
        return False