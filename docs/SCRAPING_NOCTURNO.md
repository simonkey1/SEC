# Script para ejecutar el scraping nocturno de forma segura

## Características del Scraper Robusto

✅ **Sistema de Checkpoints**
- Guarda progreso cada 50 puntos
- Puedes interrumpir y reanudar
- No pierdes datos si algo falla

✅ **Reintentos Automáticos**
- 3 intentos por cada punto
- Espera incremental (5s, 10s, 15s)
- Continúa aunque fallen algunos puntos

✅ **Logging Detallado**
- Archivo de log con timestamp
- Progreso cada 10 puntos
- Velocidad y tiempo restante

✅ **Recuperación Automática**
- Si se interrumpe, guarda progreso
- Ejecuta de nuevo y continúa donde quedó
- Limpia checkpoints al completar

---

## Cómo Ejecutar

### Paso 1: Activar entorno virtual
```powershell
.\.venv\Scripts\Activate.ps1
```

### Paso 2: Ejecutar scraper
```powershell
python scripts\scrape_2017_robusto.py
```

### Paso 3: Dejar corriendo
- Minimiza la ventana
- Deja el PC encendido
- Ve a dormir 😴

---

## Monitoreo (Opcional)

Si quieres ver el progreso sin abrir la ventana:

```powershell
# Ver últimas 20 líneas del log
Get-Content logs\scrape_2017_*.log -Tail 20 -Wait
```

---

## Si Algo Sale Mal

### Caso 1: Se interrumpe el scraping
```powershell
# Simplemente vuelve a ejecutar
python scripts\scrape_2017_robusto.py

# Automáticamente continúa desde donde quedó
```

### Caso 2: Quieres pausar manualmente
```
Ctrl + C en la terminal

# Para reanudar:
python scripts\scrape_2017_robusto.py
```

### Caso 3: Verificar progreso
```powershell
# Ver checkpoint actual
Get-Content outputs\checkpoint_2017.json
```

---

## Archivos Generados

Durante el scraping:
- `outputs/checkpoint_2017.json` - Progreso actual
- `outputs/ano_2017_partial.json` - Datos parciales
- `logs/scrape_2017_YYYYMMDD_HHMMSS.log` - Log detallado

Al completar:
- `outputs/ano_2017_completo_con_hash.json` - Datos finales
- Checkpoints se eliminan automáticamente

---

## Estimaciones

- **Inicio**: ~00:10 (cuando ejecutes)
- **Fin**: ~05:30 (5.3 horas después)
- **Puntos totales**: 1,460
- **Checkpoints**: 29 (cada 50 puntos)
- **Tamaño final**: ~120 MB

---

## Checklist Pre-Scraping

- [ ] PC conectado a corriente
- [ ] Internet estable
- [ ] Entorno virtual activado
- [ ] Suficiente espacio en disco (>500 MB)
- [ ] Configuración de suspensión desactivada

### Desactivar Suspensión (Windows)

```powershell
# Evitar que el PC se suspenda
powercfg /change standby-timeout-ac 0
powercfg /change monitor-timeout-ac 30
```

---

## Después del Scraping

Mañana cuando despiertes:

1. **Verificar que terminó**
   ```powershell
   # Ver últimas líneas del log
   Get-Content logs\scrape_2017_*.log -Tail 50
   ```

2. **Validar datos**
   ```powershell
   python scripts\analyze_2017.py
   ```

3. **Upload a Supabase**
   ```powershell
   python scripts\upload_to_supabase.py
   ```

---

## Contacto de Emergencia

Si algo falla y necesitas ayuda:
- Revisa el log más reciente en `logs/`
- Verifica el checkpoint en `outputs/checkpoint_2017.json`
- El scraper siempre puede reanudarse

---

## ¡Buena suerte! 🚀

El scraper está diseñado para ser 100% confiable.
Duerme tranquilo, mañana tendrás todos los datos de 2017.
