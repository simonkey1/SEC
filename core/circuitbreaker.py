from enum import Enum
import datetime
import logging

class States(Enum):
    OPEN = 1
    CLOSED = 2
    HALF_OPEN = 3

class CircuitBreaker():

    def __init__(self, failure_treshold=3, recovery_timeout=600):
        self.failure_treshold = failure_treshold
        self.recovery_timeout = recovery_timeout
        
        self.state = States.CLOSED      
        self.fail_counter = 0           
        self.last_failure_time = None   
    
    def puede_ejecutar(self):
            match self.state:
                  case States.CLOSED | States.HALF_OPEN:
                        return True
                  case States.OPEN:
                        time_now = datetime.datetime.now()
                        diff = (time_now - self.last_failure_time).total_seconds()
                        if diff >= self.recovery_timeout:
                              self.state = States.HALF_OPEN
                              return True
                        return False
    def registrar_exito(self):
            self.state = States.CLOSED
            self.fail_counter = 0
            self.last_failure_time = None
                  
    def registrar_fallo(self):
           if self.state == States.HALF_OPEN:
                 self.fail_counter = self.failure_treshold
           else:
                 self.fail_counter += 1
           if self.fail_counter >= self.failure_treshold:
                 self.state = States.OPEN
                 self.last_failure_time = datetime.datetime.now()
                 logging.warning(f'Circuit Breaker ABIERTO después d {self.fail_counter} fallos')
           