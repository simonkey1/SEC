# tests/integration/test_supabase_repository_integration.py

import pytest
from core.database import SupabaseRepository

@pytest.fixture
def repo():
    """Shared fixture for SupabaseRepository instance"""
    return SupabaseRepository()


class TestGetOrCreateGeografia:
    
    def test_creates_new_geografia_when_not_exists(self, repo):
        """Test that new geografia record is created"""
        id_geo = repo.get_or_create_geografia("TEST_REGION_XYZ", "TEST_COMUNA_XYZ")
        
        assert id_geo > 0
        
        # Cleanup
        repo.supabase.table('dim_geografia').delete().eq('id_geografia', id_geo).execute()
    
    def test_returns_existing_geografia_id(self, repo):
        """Test that same ID is returned for existing geografia"""
        # Primera llamada - crea
        id_geo_1 = repo.get_or_create_geografia("METROPOLITANA", "SANTIAGO")
        
        # Segunda llamada - retorna existente
        id_geo_2 = repo.get_or_create_geografia("METROPOLITANA", "SANTIAGO")
        
        assert id_geo_1 == id_geo_2


class TestGetOrCreateEmpresa:
    
    def test_creates_new_empresa_when_not_exists(self, repo):
        """Test that new empresa record is created"""
        id_emp = repo.get_or_create_empresa("TEST_EMPRESA_XYZ")
        
        assert id_emp > 0
        
        # Cleanup
        repo.supabase.table('dim_empresa').delete().eq('id_empresa', id_emp).execute()
    
    def test_returns_existing_empresa_id(self, repo):
        """Test that same ID is returned for existing empresa"""
        id_emp_1 = repo.get_or_create_empresa("ENEL DISTRIBUCION")
        id_emp_2 = repo.get_or_create_empresa("ENEL DISTRIBUCION")
        
        assert id_emp_1 == id_emp_2


class TestGetOrCreateTiempo:
    
    def test_creates_new_tiempo_when_not_exists(self, repo):
        """Test that new tiempo record is created"""
        id_tiempo = repo.get_or_create_tiempo("2026-01-23 14:30:00")
        
        assert id_tiempo == 202601231430  # Formato YYYYMMDDHHMM
        
        # Cleanup
        repo.supabase.table('dim_tiempo').delete().eq('id_tiempo', id_tiempo).execute()
    
    def test_returns_existing_tiempo_id(self, repo):
        """Test that same ID is returned for existing tiempo"""
        id_tiempo_1 = repo.get_or_create_tiempo("2026-01-23 14:30:00")
        id_tiempo_2 = repo.get_or_create_tiempo("2026-01-23 14:30:00")
        
        assert id_tiempo_1 == id_tiempo_2
        assert id_tiempo_1 == 202601231430


class TestSaveRecords:
    
    def test_inserts_new_records_successfully(self, repo):
        """Test that save_records inserts fact table correctly"""
        
        # Datos mock del transformer
        registros = [{
            'REGION': 'TEST_REGION',
            'COMUNA': 'TEST_COMUNA',
            'EMPRESA': 'TEST_EMPRESA',
            'TIMESTAMP': '2026-01-23 14:30:00',
            'CLIENTES_AFECTADOS': 100,
            'ID_UNICO': 'test_hash_12345'
        }]
        
        resultado = repo.save_records(registros)
        
        assert resultado['insertados'] == 1
        assert resultado['duplicados'] == 0
        assert resultado['errores'] == 0
        
        # Cleanup: borrar fact + dimensiones creadas
        repo.supabase.table('fact_interrupciones').delete().eq('hash_id', 'test_hash_12345').execute()
        repo.supabase.table('dim_geografia').delete().eq('nombre_region', 'TEST_REGION').execute()
        repo.supabase.table('dim_empresa').delete().eq('nombre_empresa', 'TEST_EMPRESA').execute()
        repo.supabase.table('dim_tiempo').delete().eq('id_tiempo', 202601231430).execute()
    
    def test_handles_duplicate_records(self, repo):
        """Test that duplicate hash_id is handled correctly"""
        registros = [{
            'REGION': 'METROPOLITANA',
            'COMUNA': 'SANTIAGO',
            'EMPRESA': 'ENEL DISTRIBUCION',
            'TIMESTAMP': '2026-01-23 15:00:00',
            'CLIENTES_AFECTADOS': 50,
            'ID_UNICO': 'duplicate_hash_test_99999'
        }]
        
        # Primera inserción
        resultado_1 = repo.save_records(registros)
        assert resultado_1['insertados'] == 1
        
        # Segunda inserción (duplicado)
        resultado_2 = repo.save_records(registros)
        assert resultado_2['duplicados'] == 1
        assert resultado_2['insertados'] == 0
        
        # Cleanup
        repo.supabase.table('fact_interrupciones').delete().eq('hash_id', 'duplicate_hash_test_99999').execute()