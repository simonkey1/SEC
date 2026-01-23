# ========================================
# PASO 1: Imagen base
# ========================================
# Pista: Usa python:3.12-slim como base
FROM python:3.12-slim


# ========================================
# PASO 2: Variables de entorno
# ========================================
ENV PYTHONUNBUFFERED=1
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright


# ========================================
# PASO 3: Dependencias del sistema
# ========================================
RUN apt-get update && apt-get install -y \
    wget ca-certificates fonts-liberation \
    && rm -rf /var/lib/apt/lists/*


# ========================================
# PASO 4: Directorio de trabajo
# ========================================
WORKDIR /app


# ========================================
# PASO 5: Copiar requirements primero
# ========================================
COPY requeriments.txt .



# ========================================
# PASO 6: Instalar dependencias Python
# ========================================
RUN pip install --no-cache-dir -r requeriments.txt


# ========================================
# PASO 7: Instalar navegadores Playwright
# ========================================
# Instala las dependencias del sistema necesarias para Chromium
RUN playwright install-deps chromium
RUN playwright install chromium


# ========================================
# PASO 8: Copiar todo el código
# ========================================
COPY . .


# ========================================
# PASO 9: Comando por defecto
# ========================================
CMD ["python", "scripts/end.py"]
