from unittest.mock import MagicMock

import pytest

from config import URL_SEC_GET_HORA_SERVER, URL_SEC_GET_POR_FECHA
from core.scraper import SECScraper
from core.tranformer import SecDataTransformer


def test_scraper_to_transformer_pipeline():
    """TEST: Valida flujo completo Scraper → Transformer"""
    # 1. Scraper captura datos
    scraper = SECScraper()

    mock_data = [{"FECHA": "20/01/2024 10:00"}]
    mock_hora = MagicMock()
    mock_hora.url = URL_SEC_GET_HORA_SERVER
    mock_hora.status = 200
    mock_hora.json.return_value = mock_data
    scraper.handle_response(mock_hora)

    mock_cortes = [
        {
            "NOMBRE_REGION": "METROPOLITANA",
            "NOMBRE_COMUNA": "SANTIAGO",
            "NOMBRE_EMPRESA": "ENEL",
            "CLIENTES_AFECTADOS": 100,
            "FECHA_INT_STR": "18/01/2024",
            "ACTUALIZADO_HACE": "5 min",
        }
    ]
    mock_response = MagicMock()
    mock_response.url = URL_SEC_GET_POR_FECHA
    mock_response.status = 200
    mock_response.json.return_value = mock_cortes
    scraper.handle_response(mock_response)

    # 2. Transformer procesa
    transformer = SecDataTransformer()
    result = transformer.transform(scraper.registros, scraper.hora_server)

    # 3. Validaciones end-to-end
    assert len(result) == 1
    assert result[0]["COMUNA"] == "SANTIAGO"
    assert result[0]["DIAS_ANTIGUEDAD"] == 2  # 20 - 18 = 2
    assert "ID_UNICO" in result[0]
