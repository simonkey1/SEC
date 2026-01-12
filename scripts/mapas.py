import geopandas as gpd
import os

# Cargar el GeoJSON con todas las comunas
geojson = gpd.read_file("comunas.geojson")

# Crear la carpeta 'mapas' si no existe
os.makedirs("mapas", exist_ok=True)

# Crear mapas separados para cada región
for region in geojson["Region"].unique():
    region_sanitized = region.replace(" ", "_").replace("'", "").replace("ñ", "n")
    region_geojson = geojson[geojson["Region"] == region]
    
    # Guardar cada región como un archivo GeoJSON en la carpeta 'mapas'
    region_geojson.to_file(f"mapas/{region_sanitized}.geojson", driver="GeoJSON")

print("✅ Archivos GeoJSON por región creados en la carpeta 'mapas'")
