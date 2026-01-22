"""Test básico para verificar envío de emails."""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.notifications import notifier

def test_send_test_email():
    """Envía un email de prueba."""
    notifier._send_email(
        subject="🧪 Test de notificaciones",
        body="Este es un email de prueba del sistema de monitoreo de cortes."
    )
    print("✅ Email enviado. Revisa tu bandeja de entrada.")

if __name__ == "__main__":
    test_send_test_email()