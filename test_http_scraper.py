"""Quick test script for HTTP scraper."""
from core.scraper_http import SECScraperHTTP

print("Testing HTTP scraper...")
bot = SECScraperHTTP()
result = bot.run()

print(f"\n✅ Test completado")
print(f"Registros capturados: {len(result['data'])}")
print(f"Hora server: {result['hora_server']}")

if result['data']:
    print(f"\nPrimer registro:")
    print(result['data'][0])
