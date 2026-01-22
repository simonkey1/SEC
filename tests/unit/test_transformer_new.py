import pytest
from datetime import date
from core.tranformer import SecDataTransformer

@pytest.fixture
def transformer():
    return SecDataTransformer()

def test_transform_empty_data(transformer):
    """Debe retornar lista vacía si no hay datos."""
    assert transformer.transform([]) == []

def test_parse_server_time_list(transformer):
    """Debe parsear correctamente el formato de lista que devuelve el Scraper."""
    raw_server = [{"FECHA": "20/01/2026 15:30"}]
    ts, ref_date = transformer._parse_server_time(raw_server)
    
    # El transformer actual devuelve YYYY-MM-DD HH:MM:SS
    assert ts == "2026-01-20 15:30:00"
    assert ref_date == date(2026, 1, 20)

def test_puerto_montt_aggregation(transformer):
    """
    Caso crítico: Si hay múltiples filas para la misma comuna/empresa/fecha,
    el transformador debe sumarlas en una sola.
    """
    raw_data = [
        {
            "NOMBRE_REGION": "LOS LAGOS",
            "NOMBRE_COMUNA": "PUERTO MONTT",
            "NOMBRE_EMPRESA": "SAESA",
            "FECHA_INT_STR": "19/01/2026",
            "CLIENTES_AFECTADOS": 10,
            "ACTUALIZADO_HACE": "5 min"
        },
        {
            "NOMBRE_REGION": "LOS LAGOS",
            "NOMBRE_COMUNA": "PUERTO MONTT",
            "NOMBRE_EMPRESA": "SAESA",
            "FECHA_INT_STR": "19/01/2026",
            "CLIENTES_AFECTADOS": 15,
            "ACTUALIZADO_HACE": "5 min"
        }
    ]
    
    result = transformer.transform(raw_data)
    
    assert len(result) == 1
    assert result[0]["CLIENTES_AFECTADOS"] == 25
    assert result[0]["COMUNA"] == "PUERTO MONTT"

def test_calculation_antiquity(transformer):
    """Debe calcular correctamente los días de antigüedad respecto al servidor."""
    server_time = "22/01/2026 12:00"
    raw_data = [
        {
            "NOMBRE_REGION": "O'HIGGINS",
            "NOMBRE_COMUNA": "RANCAGUA",
            "NOMBRE_EMPRESA": "CGE",
            "FECHA_INT_STR": "20/01/2026", # 2 días antes
            "CLIENTES_AFECTADOS": 100,
            "ACTUALIZADO_HACE": "10 min"
        }
    ]
    
    result = transformer.transform(raw_data, server_time_raw=server_time)
    assert result[0]["DIAS_ANTIGUEDAD"] == 2
