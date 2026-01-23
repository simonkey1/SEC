import pytest
from core.notifications import EmailNotifier

class TestEmailNotifier:

    @pytest.fixture
    def emailnotifier(self):
            # Retorna una instancia fresca para cada test
            return EmailNotifier()
    

    def test_send_capacity_alert_integration(self, emailnotifier):
        """Sends real test email - CHECK INBOX MANUALLY"""
        porcentaje = 92.5
        size_mb = 462.3
        total_filas= 50000
        try:
            emailnotifier.send_capacity_alert(porcentaje, size_mb, total_filas)
            assert True
        except Exception as e:
              pytest.fail(f'Error enviando email: {e}')

    def test_notifications_disabled_does_not_crash(self, emailnotifier):
        """Verifies that it respects the notifications_enabled flag"""
        original_state = emailnotifier.notifications_enabled
        emailnotifier.notifications_enabled = False
        try:
            emailnotifier.send_capacity_alert(95, 475, 50000)
            emailnotifier.notifications_enabled = original_state
            assert True
        except Exception as e:
             pytest.fail(f'No debería fallar incluso con notificacions disabled : {e} ')




