"""Test para verificar el envío de emails."""
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv
from core.notifications import send_capacity_alert

if __name__ == "__main__":
    load_dotenv()
    
    print("📧 Enviando email de prueba...")
    
    if send_capacity_alert(porcentaje=87.5, size_mb=437.5):
        print("✅ Email enviado correctamente! Revisa tu bandeja de entrada.")
    else:
        print("❌ Error enviando email. Revisa la configuración en .env")