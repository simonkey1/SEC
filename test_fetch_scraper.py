"""
Script de prueba para el scraper con fetch directo.
"""
import sys
sys.path.append(".")

from core.scraper_alternative import SECScraperAlternative

if __name__ == "__main__":
    print("🧪 Probando scraper ALTERNATIVO (fetch directo)...\n")
    
    scraper = SECScraperAlternative()
    resultado = scraper.run()
    
    datos = resultado.get("data", [])
    hora_server = resultado.get("hora_server")
    
    print(f"\n📊 Resultados:")
    print(f"   - Registros capturados: {len(datos)}")
    print(f"   - Hora del servidor: {hora_server}")
    
    if datos:
        print(f"\n📝 Primer registro de ejemplo:")
        print(f"   {datos[0]}")
