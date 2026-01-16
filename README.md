---
title: "⚡ Monitoreo en Tiempo Real del Suministro Eléctrico (SEC Chile) ⚡"
description: "Infraestructura modular para la extracción, procesamiento y visualización geográfica de cortes de luz en Chile."
author: "Simon Gomez"
---

## 📌 Visión del Proyecto

Este proyecto ha evolucionado de un simple script de scraping a una **infraestructura modular robusta** diseñada para alimentar un futuro tablero web interactivo. El objetivo es captar la realidad del suministro eléctrico en Chile, superando las limitaciones de visualización de la plataforma oficial de la SEC.

### 🚀 Objetivos Actuales

1.  **Extracción de Alta Fidelidad**: Intercepción de APIs internas (`GetPorFecha`) en lugar de parsing de HTML cambiante.
2.  **Ingeniería de Datos**: Sincronización con el reloj del servidor (`GetHoraServer`) y agregación inteligente de datos fragmentados (Efecto Puerto Montt).
3.  **Arquitectura Modular**: Código desacoplado siguiendo principios de diseño OOP para escalabilidad.
4.  **Visualización Web**: (En desarrollo) Transición de PowerBI a una aplicación web personalizada con mapas GIS.

---

## 🏗️ Arquitectura del Sistema

El proyecto se divide en módulos especializados dentro de la carpeta `core/`:

### 1. [core/scraper.py](core/scraper.py) (Extracción)

Utiliza **Playwright** para actuar como un "man-in-the-middle".

- Intercepta la respuesta JSON de `GetPorFecha` que alimenta los mapas oficiales.
- Captura la hora oficial del servidor mediante `GetHoraServer` para garantizar que los cálculos de antigüedad sean exactos, independientemente de la zona horaria del cliente.

### 2. [core/tranformer.py](core/tranformer.py) (Lógica y Limpieza)

El corazón del procesamiento de datos.

- **Agregación**: Resuelve el problema de datos fragmentados donde una misma comuna/empresa aparece en múltiples filas (ej. Puerto Montt). Realiza un `groupby` y suma los afectados.
- **Métricas de Antigüedad**: Calcula `DIAS_ANTIGUEDAD` comparando la fecha de inicio del corte con la hora oficial del servidor capturada.
- **ID Único Sensible**: Genera una llave compuesta (`ID_UNICO`) que incluye la magnitud de afectados, permitiendo detectar cambios en la severidad del corte en tiempo real.

### 3. [core/database.py](core/database.py) (Persistencia)

Gestiona la escritura en `outputs/`.

- Mantiene un **Histórico** (`clientes_afectados_historico.csv`) sin duplicados.
- Genera un snapshot de **Tiempo Real** (`clientes_afectados_tiempo_real.csv`) para consumo inmediato de visualizadores.
- Implementa codificación `utf-8-sig` para compatibilidad nativa con Excel y PowerBI.

### 4. [helper/check_variacion_historica.py](helper/check_variacion_historica.py) (Monitoreo)

Replica lógica analítica avanzada (tipo DAX) para comparar snapshots en tiempo real. 
- Compara el impacto total de afectados entre la ejecución actual y la anterior.
- Genera un "Health Check" por consola para validar la consistencia de los datos recolectados.

---

## 🚀 Instalación y Uso

### Preparar el entorno

```bash
# Crear entorno virtual
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate

# Instalar dependencias
pip install playwright pandas
playwright install chromium
```

### Ejecución

El orquestador principal ahora funciona como un **servicio de monitoreo continuo**:

```bash
python scripts/end.py
```

**Lo que hace el script:**
1.  **Loop Infinito**: Se ejecuta cada 5 minutos automáticamente.
2.  **Extracción Dinámica**: Llama al scraper para obtener el estado actual de la SEC.
3.  **Transformación y persistencia**: Procesa los datos y actualiza los CSVs.
4.  **Validación de Variación**: Ejecuta el `Health Check` para informar cambios significativos en el número de clientes afectados directamente en la terminal.

---

## 🔍 Análisis Técnico: El "Efecto Puerto Montt"

Durante la ingeniería inversa, detectamos que la SEC reporta cortes en "pedazos" técnicos. Por ejemplo, Puerto Montt podía tener 10 filas de 1 cliente cada una. Nuestra lógica de **Transformación** consolida estos datos para mostrar el impacto real por comuna, sumando los afectados en una única entrada representativa.

---

## 📊 Visualización Geographic & GIS

### 🗺️ Procesamiento de Mapas

Contamos con una infraestructura de mapas basada en archivos GeoJSON y Shapefiles (ESRI) organizada por jerarquía territorial:
- **Nivel Nacional**: `maps/poligonos_chile/`
- **Nivel Regional/Provincial/Comunal**: Polígonos detallados con codificación oficial.

Además, el script `scripts/mapas.py` permite **regionalizar** el GeoJSON nacional, subdividiéndolo en archivos independientes por cada región de Chile para optimizar la carga en visores web ligeros.

### 🌐 Próximos Pasos: El Dashboard Web

El enfoque se ha desplazado hacia una plataforma web propia que utilice los archivos generados y los polígonos GeoJSON en `maps/` para crear una experiencia de usuario superior (GIS) con capas de calor y tendencias temporales.

### 📈 Legacy: Análisis en PowerBI

Si prefieres utilizar herramientas No-Code, los archivos generados siguen siendo compatibles con PowerBI. Hemos movido la guía técnica detallada y los fragmentos de código M/DAX a su propio documento:

👉 **[Guía de Configuración para PowerBI](docs/powerbi_legacy.md)** y la página web: https://sec2025.netlify.app/

---

## 🛠️ Automatización

Puedes automatizar la ejecución mediante el Programador de Tareas (Windows) o Crontab (Linux) ejecutando el script `scripts/end.py`.

```bash
# Ejemplo simple de .bat para Windows (@echo off etc...)
python scripts/end.py
```

---

_Gracias por seguir el desarrollo de este proyecto. El monitoreo transparente de servicios básicos es un pilar para la resiliencia ciudadana._ 💜
