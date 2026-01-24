import httpx
import sys

def test_connectivity(url):
    print(f"🔍 Probando: {url}")
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(url, follow_redirects=True)
            print(f"✅ Respuesta: {response.status_code}")
            print(f"📋 Headers: {dict(response.headers)}")
            return True
    except Exception as e:
        print(f"❌ Error conectando a {url}: {str(e)}")
        return False

if __name__ == "__main__":
    urls = [
        "https://www.google.com",  # Control
        "https://www.sec.cl",      # Home
        "https://apps.sec.cl/INTONLINEv1/index.aspx" # App
    ]
    
    results = {}
    for url in urls:
        results[url] = test_connectivity(url)
        print("-" * 50)
    
    if not results.get("https://apps.sec.cl/INTONLINEv1/index.aspx"):
        print("\n🚨 CONCLUSIÓN: La sub-app 'apps.sec.cl' está bloqueada para este IP de GitHub.")
    else:
        print("\n🚀 CONCLUSIÓN: Conectividad básica disponible, el problema puede ser el navegador/JS.")
