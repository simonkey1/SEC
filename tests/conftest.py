import pytest


@pytest.fixture
def complete_sec_record():
    """Fixture: Retorna un registro completo válido de la SEC (incluye campos legacy en 0)."""
    return {
        # Campos activos
        "MES_INT": 1,
        "ANHO_INT": 2024,
        "NOMBRE_REGION": "METROPOLITANA",
        "NOMBRE_COMUNA": "SANTIAGO",
        "NOMBRE_EMPRESA": "ENEL",
        "CLIENTES_AFECTADOS": 100,
        "ACTUALIZADO_HACE": "2 Dias 0 Horas 0 Minutos",
        "FECHA_INT_STR": "18/01/2024",
        # Campos legacy (siempre en 0 según estructura real de la SEC)
        "HORA": 0,
        "DIA": 0,
        "MES": 0,
        "ANHO": 0,
    }


@pytest.fixture
def mock_server_time_fixture():
    """Fixture: Simula la respuesta de hora del servidor de la SEC."""
    return [{"FECHA": "20/01/2024 10:00"}]
