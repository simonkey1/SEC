# core/health_checker.py (completo)
from circuitbreaker import CircuitBreaker
import datetime
from ..helper import get_hora_server
from .scraper import SECScraper
from .tranformer import SecDataTransformer
from .database import save_data_csv
from .logger import logger
from datetime import timedelta
import time



class HealthChecker:
    """Monitorea salud del pipeline"""
    
    def __init__(self):
        self.failed_attempts = 0
        self.circuit_breaker = CircuitBreaker(threshold=3)
        self.last_success = None
        self.execution_log = []
    
    def check_sec_health(self) -> dict:
        """
        Verifica connectivity con SEC.
        
        Retorna: {
            'is_healthy': bool,
            'message': str,
            'hora_servidor': datetime,
            'response_time_ms': float
        }
        """
        if not self.circuit_breaker.is_healthy():
            return {
                'is_healthy': False,
                'message': 'Circuit breaker abierto (3 fallos consecutivos)',
                'hora_servidor': None,
                'response_time_ms': None
            }
        
        try:
            import time
            start = time.time()
            hora = get_hora_server()
            response_time = (time.time() - start) * 1000
            
            self.circuit_breaker.record_success()
            self.failed_attempts = 0
            self.last_success = datetime.now()
            
            return {
                'is_healthy': True,
                'message': 'SEC responding',
                'hora_servidor': hora,
                'response_time_ms': response_time
            }
        
        except Exception as e:
            self.failed_attempts += 1
            self.circuit_breaker.record_failure()
            
            logger.error(f"SEC health check failed (attempt {self.failed_attempts}): {e}")
            
            return {
                'is_healthy': False,
                'message': f'SEC down: {e}',
                'hora_servidor': None,
                'response_time_ms': None
            }
    
    def log_execution(self, execution_data: dict):
        """
        Log de ejecución para SLA reporting.
        
        execution_data = {
            'timestamp': datetime,
            'status': 'success' | 'partial' | 'error',
            'rows_extracted': int,
            'rows_transformed': int,
            'rows_failed': int,
            'errors': list
        }
        """
        self.execution_log.append(execution_data)
        logger.info(f"Execution: {execution_data['status']}, {execution_data['rows_transformed']} rows")
    
    def get_sla_report(self, days: int = 7) -> dict:
        """
        SLA report: últimos N días.
        
        Retorna: {
            'period_days': int,
            'total_executions': int,
            'successful': int,
            'partial': int,
            'failed': int,
            'success_rate': float,
            'avg_rows_per_execution': float
        }
        """
        cutoff = datetime.now() - timedelta(days=days)
        recent = [e for e in self.execution_log if e['timestamp'] > cutoff]
        
        if not recent:
            return {'error': 'No data'}
        
        successful = len([e for e in recent if e['status'] == 'success'])
        partial = len([e for e in recent if e['status'] == 'partial'])
        failed = len([e for e in recent if e['status'] == 'error'])
        
        total_rows = sum(e.get('rows_transformed', 0) for e in recent)
        
        return {
            'period_days': days,
            'total_executions': len(recent),
            'successful': successful,
            'partial': partial,
            'failed': failed,
            'success_rate': (successful / len(recent)) * 100,
            'avg_rows_per_execution': total_rows / len(recent) if recent else 0
        }

# Uso en scripts/end.py:
def main():
    health_checker = HealthChecker()
    
    while True:
        # 1. Health check
        health = health_checker.check_sec_health()
        if not health['is_healthy']:
            logger.critical(f"Pipeline stopping: {health['message']}")
            break
        
        # 2. Scrape, transform, load
        try:
            raw_data = SECScraper.scrape_sec_data()
            transformed, failed = SecDataTransformer.transform(raw_data, health['hora_servidor'])
            save_data_csv(transformed)
            
            health_checker.log_execution({
                'timestamp': datetime.now(),
                'status': 'success' if len(failed) == 0 else 'partial',
                'rows_extracted': len(raw_data),
                'rows_transformed': len(transformed),
                'rows_failed': len(failed),
                'errors': [f['error'] for f in failed]
            })
        
        except Exception as e:
            health_checker.log_execution({
                'timestamp': datetime.now(),
                'status': 'error',
                'rows_extracted': 0,
                'rows_transformed': 0,
                'rows_failed': 0,
                'errors': [str(e)]
            })
        
        time.sleep(300)  # 5 minutos