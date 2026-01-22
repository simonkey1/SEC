# tests/test_transformer.py

from datetime import datetime, timedelta
from core.tranformer import SecDataTransformer

class TestTransformer:
    """Tests para verificar transformaciones correctas"""
    
    def test_corte_id_same_event(self):
        """✅ MISMO corte (reportado múltiples veces) = MISMO corte_id"""
        server_time = "20/01/2026 10:00"
        transformer = SecDataTransformer()
        # Minuto 0
        raw_data_1 = [{
            'NOMBRE_COMUNA': 'Puerto Montt',
            'NOMBRE_EMPRESA': 'SAESA',
            'ACTUALIZADO_HACE': '0 Dias 0 Horas 14 Minutos',
            'CLIENTES_AFECTADOS': 10
        }]
        result1 = transformer.transform(raw_data_1, server_time)
        result2 = transformer.transform(raw_data_1, server_time_raw=server_time)
        
        assert result1[0]["ID_UNICO"] == result2[0]["ID_UNICO"]

        result3 = transformer.transform(raw_data_1, server_time_raw="20/01/2026 10:05")
        assert result1[0]["ID_UNICO"] != result3[0]["ID_UNICO"]
        
        # Minuto 5 (mismo corte, 19 min después)
        server_time_2 = "20/01/2026 10:19"
        raw_data_2 = [{
            'NOMBRE_COMUNA': 'Puerto Montt',
            'NOMBRE_EMPRESA': 'SAESA',
            'ACTUALIZADO_HACE': '0 Dias 0 Horas 19 Minutos',
            'CLIENTES_AFECTADOS': 10
        }]
        transformed_2 = SecDataTransformer.transform(raw_data_2, server_time_2)
        corte_id_2 = transformed_2[0]['corte_id']
        
    
    def test_corte_id_different_events(self):
        """✅ Cortes DIFERENTES = corte_ids DIFERENTES"""
        hora_servidor = datetime(2026, 1, 15, 8, 30, 0)
        
        raw_data = [
            {
                'NOMBRE_COMUNA': 'Puerto Montt',
                'NOMBRE_EMPRESA': 'SAESA',
                'ACTUALIZADO_HACE': '0 Dias 0 Horas 14 Minutos',
                'CLIENTES_AFECTADOS': 10
            },
            {
                'NOMBRE_COMUNA': 'Valdivia',  # ← DIFERENTE
                'NOMBRE_EMPRESA': 'SAESA',
                'ACTUALIZADO_HACE': '0 Dias 0 Horas 5 Minutos',
                'CLIENTES_AFECTADOS': 1
            }
        ]
        
        transformed = SecDataTransformer.transform(raw_data, hora_servidor)
        
        assert transformed[0]['corte_id'] != transformed[1]['corte_id']
    
    def test_fecha_inicio_calculation(self):
        """✅ Cálculo de fecha_inicio_corte es correcto"""
        hora_servidor = datetime(2026, 1, 15, 8, 30, 0)
        
        raw_data = [{
            'NOMBRE_COMUNA': 'Puerto Montt',
            'NOMBRE_EMPRESA': 'SAESA',
            'ACTUALIZADO_HACE': '0 Dias 0 Horas 14 Minutos',
            'CLIENTES_AFECTADOS': 10
        }]
        
        transformed = SecDataTransformer.transform(raw_data, hora_servidor)
        fecha_inicio = transformed[0]['fecha_inicio_corte']
        
        # Debe ser: 08:30 - 14 min = 08:16
        expected = datetime(2026, 1, 15, 8, 16, 0)
        assert fecha_inicio == expected
    
    def test_actualizado_hace_parsing(self):
        """✅ ACTUALIZADO_HACE se parsea correctamente"""
        test_cases = [
            ('0 Dias 0 Horas 14 Minutos', timedelta(minutes=14)),
            ('0 Dias 1 Horas 30 Minutos', timedelta(hours=1, minutes=30)),
            ('1 Dias 2 Horas 15 Minutos', timedelta(days=1, hours=2, minutes=15)),
            ('0 Dias 0 Horas 0 Minutos', timedelta(0))
        ]
        
        for actualizado_str, expected_timedelta in test_cases:
            parsed = SecDataTransformer.parse_actualizado_hace(actualizado_str)
            assert parsed == expected_timedelta

# Ejecutar: pytest tests/test_transformer.py -v