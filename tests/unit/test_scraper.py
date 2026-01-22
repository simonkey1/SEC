
import sys
import os
# Esto le dice a Python: "La raíz del proyecto también es un lugar donde buscar archivos"
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
import unittest
from unittest.mock import MagicMock
from core.scraper import SECScraper
from datetime import datetime, timedelta
from config import URL_SEC_GET_POR_FECHA, URL_SEC_GET_HORA_SERVER, STATUS_CODE, METHOD_POST

class TestScraper(unittest.TestCase):
    """Tests para verificar que scraper funciona correctamente"""
   
    def create_mock_response(self, url, json_data, status=STATUS_CODE, method=METHOD_POST):
        """Fábrica de objetos response para evitar boilerplate"""
        mock = MagicMock()
        mock.url = url
        mock.status = status
        mock.request.method = method
        mock.json.return_value = json_data
        return mock
    def test_hora_server_format_valido(self):
        """✅ Verifica que el formato de fecha sea el esperado por el Transformer"""
        bot = SECScraper()
        mock_data = [{"FECHA": "19/01/2026 15:30"}]
        bot.handle_response(self.create_mock_response(URL_SEC_GET_HORA_SERVER, mock_data))
    
    # Aquí solo probamos que NO explote al parsear
        try:
            datetime.strptime(bot.hora_server, "%d/%m/%Y %H:%M")
        except ValueError:
            pytest.fail("La SEC cambió el formato de fecha esperado")

    def test_get_hora_server_success(self):
        """✅ GetHoraServer devuelve hora válida"""
        bot = SECScraper()
        fecha_test = "19/01/2026 18:57"
        data = [{"FECHA": fecha_test}]
        mock = self.create_mock_response(URL_SEC_GET_HORA_SERVER, data)
        bot.handle_response(mock)
        assert bot.hora_server == fecha_test
        assert isinstance(bot.hora_server, str)
        assert bot.hora_server is not None
        
    
    def test_get_hora_server_reasonable(self):
        """✅ GetHoraServer devuelve hora razonable (no futuro lejano)"""
        bot = SECScraper()
        date_format = '%d/%m/%Y %H:%M'
        fecha_test = "19/01/2025 18:57"
        data = [{"FECHA": fecha_test}]
        mock = self.create_mock_response(URL_SEC_GET_HORA_SERVER, data)
        bot.handle_response(mock)
        date_obj = datetime.strptime(bot.hora_server, date_format)
        assert date_obj < datetime.now() + timedelta(days=1)
    
    def test_handle_response_success(self):
        """✅ handle_response captura datos cuando la URL es correcta"""
        # Mock respuesta SEC
        bot = SECScraper()
        data = [
            {
                "MES_INT": 1,
                "ANHO_INT": 2026,
                "HORA": 0,
                "DIA": 0,
                "MES": 0,
                "ANHO": 0,
                "NOMBRE_REGION": "Metropolitana",
                "NOMBRE_COMUNA": "Renca",
                "NOMBRE_EMPRESA": "ENEL",
                "CLIENTES_AFECTADOS": 1,
                "ACTUALIZADO_HACE": "0 Dias 0 Horas 17 Minutos ",
                "FECHA_INT_STR": "19/1/2026"

                }
            ]
        
        mock = self.create_mock_response(URL_SEC_GET_POR_FECHA, data)
        bot.handle_response(mock)
        assert len(bot.registros) == 1
        assert bot.registros[0]['NOMBRE_COMUNA'] == "Renca"
    
    def test_scrape_sec_data_empty(self):
        """✅ Scraper maneja respuesta vacía de SEC"""
        bot = SECScraper()
        mock = self.create_mock_response(URL_SEC_GET_POR_FECHA, [])
        bot.handle_response(mock)
        assert bot.registros == []
    
    # def test_scrape_sec_timeout(self, mock_get):
    #     """✅ SECScraper maneja timeout de SEC"""
    #     mock_get.side_effect = requests.Timeout("SEC timeout")
        
    #     with pytest.raises(requests.Timeout):
    #         SECScraper.run()
    
    def test_scrape_sec_invalid_json(self):
        """✅ SECScraper maneja JSON inválido"""
        bot = SECScraper()
        mock = self.create_mock_response(URL_SEC_GET_POR_FECHA, None)
        mock.json.side_effect = ValueError("Sintaxis inválida")
        
        bot.handle_response(mock)
        assert len(bot.registros) == 0

# Ejecutar: pytest tests/test_scraper.py -v