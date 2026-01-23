from core.database import check_database_capacity

import pytest

def test_health_check_returns_correct_structure():
    
    resultado = check_database_capacity(threshold_percent=85)

    assert isinstance(resultado, dict)
    assert "size_mb" in resultado
    assert "porcentaje" in resultado
    assert "alert_sent" in resultado
    assert "total_filas" in resultado
    assert isinstance(resultado['porcentaje'], float)
    assert isinstance(resultado['size_mb'], float)
    assert isinstance(resultado['total_filas'], int)
    assert isinstance(resultado['alert_sent'], bool)

def test_health_check_triggers_alert_at_threshold():
    """Verifies alert triggers correctly based on threshold"""
    # threshold=0 debería siempre triggear alerta
    resultado = check_database_capacity(threshold_percent=0)
    assert resultado['alert_sent'] == True
    
    # threshold=100 nunca debería triggear
    resultado = check_database_capacity(threshold_percent=100)
    assert resultado['alert_sent'] == False