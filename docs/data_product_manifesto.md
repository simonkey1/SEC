# Manifesto del Producto de Datos: "Estado de la Red"

## 1. La Narrativa Central (Hipótesis Validada)
> *"La inversión en transmisión es efectiva, pero no es mágica. Su éxito depende de la geografía (Clima) y la maturacion temporal (Lag)."*

Hemos pasado de "La inversión no sirve" (Correlación -0.14) a una visión matizada probada por 4 casos de estudio:
1.  **Éxito Inmediato**: Proyectos quirúrgicos (Arica/Santiago) bajan cortes al instante (-70%).
2.  **Éxito Tardío (Lag)**: Grandes carreteras (Cardones-Polpaico) tardan 3 años en estabilizar el sistema (-17%).
3.  **Desafío Estructural**: En el Sur (Los Lagos), el clima extremo anula las mejoras de inversión (+4%).

---

## 2. Visualizaciones Seleccionadas ("The Keepers")
Estas son las 5 visualizaciones que pasarán al Frontend, y por qué:

### A. El Mapa de Calor "Social ROI" (Ineficiencia)
*   **Fuente**: `social_roi_analysis.py`
*   **Por qué**: Es la métrica de negocio definitiva. Muestra que **Ñuble** es un "Hoyo Negro" (55k afectados/M$ invertido) vs **Antofagasta** (230 afectados/M$).
*   **Mejora**: Se agregaron tooltips explicando el "Lag" (Proyectos 2027) para no ser injustos.

### B. La Galería de Desastres (Time-Series)
*   **Fuente**: `batch_visualize_events.py` (Mega View)
*   **Por qué**: Permite auditoría evento por evento. Muestra la "firma" de cada tormenta (recuperación rápida vs lenta).
*   **Uso**: Drill-down para ingenieros/auditores.

### C. El Ranking de la Vergüenza (Empresas)
*   **Fuente**: `company_ranking_analysis.py`
*   **Por qué**: Separa el volumen (CGE) de la severidad (Chilquinta). Es transparencia pura para el usuario final.

### D. El Monitor en Tiempo Real (Zapping)
*   **Fuente**: `time_series_zapping.py`
*   **Por qué**: Muestra el pulso "minuto a minuto". Es esencial para ver la estabilidad diaria.

### E. La Evidencia de Inversión (Antes/Después)
*   **Fuente**: `validate_improvement.py`
*   **Por qué**: Muestra gráficamente el impacto de los 4 grandes proyectos (Barras Antes vs Después). Es la prueba de que el sistema avanza.

---

## 3. Metodología de Métricas
¿Usamos estándares internacionales? **Sí, adaptados.**

*   **SAIFI Proxy (Frecuencia)**: Usamos `total_eventos / total_clientes`.
    *   *Ajuste*: Filtramos micro-cortes (<1 min) para limpiar ruido.
*   **SAIDI Proxy (Duración)**: Usamos `clientes_afectados * horas_corte`.
    *   *Ponderación*: No tratamos igual un corte en una zona densa que en una rural. El "Market Map" normaliza esto por densidad poblacional.
*   **Social ROI (Propia)**: `Clientes Afectados / Inversión MMU$`.
    *   *Innovación*: Métrica única de este proyecto para medir eficiencia de gasto público.

---

## 4. Estado Actual (Status Check)
| Capa | Estado | Conclusión |
| :--- | :--- | :--- |
| **Ingesta (Raw)** | ✅ Completado | 6.2M registros, limpio de ceros falsos. |
| **Contexto** | ✅ Completado | Hitos climáticos y fechas de inauguración validadas. |
| **Análisis** | ✅ Completado | Hipótesis de "Lag" confirmada estadísticamente. |
| **Backend** | ⏸️ Pendiente | Scripts listos, esperando luz verde para `sync_dashboard_data.py`. |
| **Frontend** | ⏳ En espera | Diseño definido por las visualizaciones "Keepers". |

Estamos listos para construir. No falta ningún dato.
