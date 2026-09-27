# IMP-001 — M01 Validate & Desurvey

## 1. Identificación

- **Implementation ID:** IMP-001
- **Module:** M01 — Validate & Desurvey
- **Date:** 2026-09-27
- **Group:** G04
- **Participants:** Jorge Martín Sánchez Linares, Erwin Segundo Olivera Cercado, Alesandra Briyit Guevara Díaz
- **Status:** IN_PROGRESS

---

## 2. Problema minero

Preparar, validar y desurveyar las tablas de sondajes del release, y presentar
las trayectorias y los intervalos ya posicionados en una visualización 3D
interactiva en el sistema cartesiano local.

## 3. Objetivo

Cargar y validar las fuentes, calcular trayectorias y posicionar intervalos
según las decisiones aprobadas, y visualizar esos resultados calculados sin
reprocesar su geometría ni modificar los archivos fuente.

## 4. Inputs

| Variable | Significado | Unidad | Origen | Obligatorio | Validación |
|---|---|---|---|---|---|
| Collar | Ubicación, orientación inicial e identificación del pozo | Según `data_dictionary.csv`; identificadores: UNKNOWN | `data/raw/collar.csv` | Sí | Esquema, tipos, nulos, conteo del manifest e identificador de pozo |
| Survey | Orientaciones medidas a profundidad | m y degree según diccionario | `data/raw/survey.csv` | Sí | Esquema, tipos, nulos, conteo del manifest y referencia a collar |
| Assay | Intervalos geoquímicos observados | m, percent y g/t según diccionario | `data/raw/assay.csv` | Sí | Esquema, tipos, nulos, conteo del manifest, identificador de muestra y referencia a collar |
| Lithology | Intervalos litológicos observados | m según diccionario | `data/raw/lithology.csv` | Sí | Esquema, tipos, nulos, conteo del manifest y referencia a collar |
| Density | Muestras de densidad observadas | m y t/m3 según diccionario | `data/raw/density.csv` | Sí | Esquema, tipos, nulos, conteo del manifest, identificador de muestra y referencia a collar |
| Alteration | Intervalos de alteración cuando estén disponibles | m según diccionario | `data/raw/alteration.csv` | Sí | Esquema y conteo del manifest; 0 registros se reportan como no disponibles |
| Diccionario | Definiciones de campos, unidades y tipos | No aplica | `data/raw/data_dictionary.csv` | Sí | Columnas requeridas y definiciones aplicables a cada tabla |
| Manifest | Identidad del release, archivos y conteos publicados | No aplica | `data/raw/release_manifest.json` | Sí | Archivos, conteos e identidad del dataset/proyecto |
| Trayectoria calculada | Estaciones XYZ previamente desurveyadas | m | `data/processed/drillhole_trajectory.csv` / memoria del pipeline | Sí | Coordenadas finitas y MD existente |
| Intervalos posicionados | XYZ de FROM/MID/TO y atributos observados | m para coordenadas; unidades analíticas conservadas | `data/processed/lithology_xyz.csv`, `assay_xyz.csv` / memoria del pipeline | Sí para las capas correspondientes | Esquema requerido para la capa |

## 5. Outputs

| Variable / resultado | Significado | Unidad | Destino |
|---|---|---|---|
| `M01Inputs.tables` | Encabezados y filas CSV cargadas como texto, por archivo | Según campos originales | Memoria |
| `M01Inputs.data_dictionary` | Diccionario leído | No aplica | Memoria |
| `M01Inputs.manifest` | Manifest leído como objeto JSON | No aplica | Memoria |
| `Trajectory.table` | Coordenadas XYZ en cada estación survey distinta | m | Memoria / `data/processed/drillhole_trajectory.csv` |
| Tablas posicionadas | Campos fuente conservados más MD medio y XYZ en FROM/MID/TO | m para MD y coordenadas | `data/processed/assay_xyz.csv`, `lithology_xyz.csv`, `density_xyz.csv` |
| `ValidationReport.findings` | Hallazgos con regla, severidad, tabla, fila, sondaje, campo, valor y condición esperada | No aplica | Memoria |
| Findings M01 | Hallazgos individuales, incluidos warnings de desurvey | No aplica | `outputs/tables/m01_validation_findings.csv` |
| Resumen | Conteos por regla, severidad y tabla; incluye reglas sin findings | No aplica | `outputs/tables/m01_validation_summary.csv` |
| Visualización 3D | Collars etiquetados, trayectorias, litología y opción de assay coloreada por `cu_pct`; indica que no hay topografía | m en ejes XYZ | `outputs/figures/m01_exploration_3d.html` |
| Figuras estáticas de validación | Planta, sección litológica proyectada y Cu ponderado por longitud según cota y litología | m y unidades de `cu_pct` | `outputs/figures/m01_planta.png`, `m01_seccion_litologia.png`, `m01_cu_cota_litologia.png` |
| Métricas espaciales por pozo | Vecino de trayectoria más próximo, distancia 3D, profundidad vertical, cota de fondo y Cu en los últimos 10 m | m y `cu_pct` | `outputs/tables/m01_validacion_espacial.csv` |

## 6. Supuestos

Los valores CSV se conservan como texto al cargar y el validador interpreta los
tipos declarados por el diccionario.

| ID | Supuesto | Justificación | Impacto |
|---|---|---|---|
| SUP-01 | Tolerancia de redondeo numérico de `1e-9 m` para comparar longitudes, límites de profundidad, continuidad de intervalos y límites de posicionamiento. | Las profundidades y longitudes del release se publican con nueve decimales; se evita sensibilidad a redondeo de representación binaria. | Diferencias absolutas menores o iguales a `1e-9 m` se tratan como igualdad en esas comparaciones. No es tolerancia geológica ni operacional. |
| SUP-02 | La cobertura de densidad es la unión de intervalos válidos recortada a `[0, final_depth_m]`; no tiene umbral de aceptación. | El plan define cobertura informativa y no especifica umbral. | El porcentaje es descriptivo; no implica representatividad. |
| SUP-03 | La equivalencia entre `CAMPAIGN_0X` y `C0X` no se confirma automáticamente. | Las tablas y el manifest usan formatos distintos; el equipo indicó que la equivalencia está pendiente. | Se emite WARNING cuando el identificador de tabla no coincide literalmente con el manifest. |
| SUP-04 | Positioning interpola linealmente XYZ entre estaciones consecutivas de la trayectoria ya desurveyada. | El contrato pide interpolar XYZ y prohíbe recalcular/desduplicar la lógica de desurvey; no define otra interpolación. | Los XYZ de intervalos son interpolaciones sobre los segmentos entre estaciones, no una nueva evaluación de la curva minimum-curvature dentro del tramo. |
| SUP-05 | La profundidad vertical se calcula como Z del collar menos Z de la última estación; el Cu de los últimos 10 m se pondera por longitud de intersección con ese tramo. | DECISION-01 establece Z positivo hacia arriba; los ensayos son intervalos que pueden cruzar el límite del tramo final. | Si la cobertura de assay es parcial, el promedio usa solo longitud con datos y la tabla reporta también `cu_covered_length_last_10m_m`. |
| SUP-06 | Las bandas de 50 m para `mid_z` se anclan en múltiplos de 50 m respecto de Z=0 (`floor(mid_z / 50) * 50`). | Se requiere agrupar en bandas de 50 m y no se especificó otro origen de bandas. | Cada ensayo se asigna a una sola banda por su cota media; el Cu de la combinación banda/litología se pondera por longitud del assay. |

## 7. Lógica minera

Esta etapa valida el contrato documentado y las reglas aprobadas del plan de
validación de ETAPA 3. Cada finding tiene `rule_id`, severidad (`ERROR`,
`WARNING` o `INFO`), tabla, fila, sondaje, campo, valor observado y condición
esperada.

Reglas M01 implementadas:

- **Collar:** `hole_id` único, `final_depth_m > 0` y coordenadas `x/y/z`
  numéricas y finitas; todos `ERROR`.
- **Survey:** referencia a collar, profundidad no negativa, secuencia ordenada,
  estación en cero y profundidad dentro del collar; orientación numérica y
  finita. Duplicado idéntico genera `WARNING` y se deduplica; duplicado
  contradictorio es `ERROR`.
- **Intervalos:** orden `from_m < to_m`, largo, límites y gaps/overlaps para
  assay, lithology y density. Overlaps son `ERROR` en assay/lithology y
  `WARNING` en density; gaps son `WARNING` en assay/lithology e `INFO` en
  density; las otras reglas son `ERROR`.
- **Assay:** leyes numéricas y no negativas (`ERROR`); ceros (`INFO`) sin
  interpretación como bajo límite de detección.
- **Density:** dato numérico finito y positivo (`ERROR`); cobertura por pozo
  (`INFO`, sin umbral).
- **Alteration:** tabla vacía (`INFO`), no equivale a ausencia geológica.
- **Campañas:** diferencia de nomenclatura frente al manifest (`WARNING`),
  pendiente de confirmación.

Brechas se evalúan también contra los extremos `[0, final_depth_m]`; overlaps y
gaps se detectan por profundidad, independiente del orden de las filas.

**ETAPA 7:** minimum curvature calcula el desplazamiento acumulado entre cada
par de estaciones usando la dirección definida por azimuth horario desde +Y y
dip desde la horizontal. La primera estación MD 0 se ancla exactamente al XYZ
del collar; se utiliza la orientación survey para continuar. Survey idéntico
repetido a igual MD genera WARNING y se deduplica; orientaciones contradictorias
a igual MD son ERROR. No se agregan estaciones y no se extrapola después de la
última medición.

Positioning calcula `MID = (FROM + TO) / 2` y obtiene XYZ de FROM/MID/TO por
interpolación lineal entre estaciones de la trayectoria ya calculada. Intervalos
fuera del rango medido producen ERROR y no se devuelve una tabla posicionada
parcial.

## 8. Diseño computacional

### Módulos / archivos

- `src/m01/loader.py`: lectura de collar, survey, assay, lithology, density,
  alteration, diccionario y manifest; fuentes abiertas en modo lectura.
- `src/m01/validator.py`: validación contractual y reglas aprobadas de M01.
- `src/m01/validation_report.py`: escritura de findings y resumen por regla.
- `src/m01/desurvey.py`: minimum curvature, comparación collar/survey en MD 0
  y escritura de la trayectoria por estación.
- `src/m01/positioning.py`: posicionamiento genérico de intervalos y escritura
  de salidas; no recalcula trayectoria.
- `src/m01/visualizer.py`: genera una figura Plotly desde tablas ya calculadas;
  no calcula ni modifica geometría.
- `src/m01/validation_plots.py`: genera figuras estáticas y métricas espaciales
  leyendo `drillhole_trajectory.csv`, `lithology_xyz.csv` y `assay_xyz.csv` de
  `data/processed/`; no lee `data/raw/` ni recalcula trayectoria/posicionamiento.
- `main.py`: orquestación de carga, validación, desurvey y posicionamiento; no
  contiene reglas ni cálculos geométricos y llama a visualización/figuras de
  control al final.
- `tests/m01/test_m01_data_contract.py`: pruebas contractuales con el release.
- `tests/m01/test_m01_validation_rules.py`: casos en memoria y salida de reportes.
- `tests/m01/test_desurvey.py`: casos A/B/C, collar, duplicados, MD 0,
  orientación constante y release.
- `tests/m01/test_positioning.py`: interpolación FROM/MID/TO, preservación de
  campos, intervalos fuera de rango y tabla vacía.
- `tests/m01/test_visualizer.py`: capas 3D, selector litología/assay y HTML
  autocontenido.
- `tests/m01/test_validation_plots.py`: creación de PNG y comprobación de
  distancia, profundidad vertical, cota de fondo y promedio de Cu final.

### Funciones / clases principales

- `load_m01_inputs(raw_dir) -> M01Inputs`
- `validate_m01_inputs(inputs) -> ValidationReport`
- `calculate_trajectory(collar, survey) -> Trajectory`
- `position_intervals(trajectory, intervals, from_field, to_field) -> CsvTable`
- `write_validation_outputs(report, output_dir) -> None`
- `write_trajectory(trajectory, output_path) -> None`
- `write_positioned_table(table, output_path) -> None`
- `build_exploration_figure(collar, trajectory, lithology, assay) -> Figure`
- `write_exploration_html(collar, trajectory, lithology, assay, output_path) -> Path`
- `generate_validation_plots(processed_dir, figures_dir, metrics_path) -> dict[str, Path]`
- `CsvTable`, `M01Inputs`, `ValidationFinding`, `ValidationReport`

### Contratos aún no implementados

| Módulo | Input previsto | Output previsto |
|---|---|---|
| `visualizer.py` | Trayectoria y resultados de posicionamiento | Visualización de inspección |
| `exporter.py` | Resultados acordados de M01 | Archivos derivados fuera de `data/raw/` |

Exportación adicional permanece fuera del alcance actual.

### Dependencias relevantes

- Biblioteca estándar de Python para carga y validación.
- `plotly` para generar la visualización interactiva; se agregó a
  `requirements.txt`. Ya estaba disponible en el entorno, por lo que no se
  instalaron dependencias.
- `matplotlib` para producir figuras estáticas; está declarado en
  `requirements.txt` y se instaló en el entorno al no estar disponible.

## 9. Etapas de implementación

### Etapa 1 — Inventario de datos

- **Fecha:** previa a la implementación; fecha exacta no registrada.
- **Objetivo:** conocer los archivos disponibles y sus campos antes de definir
  el tratamiento computacional.
- **Trabajo realizado:** inventario de archivos, columnas, tipos, unidades
  documentadas, claves, relaciones y dudas del release.
- **Resultado:** identificado EXP03/DS04, incluidos los datos disponibles y
  `alteration.csv` vacío.
- **Pendiente:** utilizar el inventario como base del modelo conceptual.

### Etapa 2 — Modelo conceptual

- **Fecha:** previa a la implementación; fecha exacta no registrada.
- **Objetivo:** definir cómo se organiza el trabajo de M01.
- **Trabajo realizado:** el equipo completó el modelo conceptual antes de
  implementar.
- **Resultado:** separación modular entre carga, validación y etapas posteriores;
  este registro no reinterpreta las decisiones conceptuales del equipo.
- **Pendiente:** usar las definiciones aprobadas al implementar etapas posteriores.

### Etapa 3 — Plan de validación y T1

- **Fecha:** previa a la implementación de esta etapa; fecha exacta no registrada.
- **Objetivo:** acordar reglas y severidades antes de codificarlas.
- **Trabajo realizado:** según el equipo, se aprobó el plan de validación. El
  historial Git confirma que el commit `c40b793` agregó
  `outputs/tables/T1_audit_summary_DS04_EXP03.xlsx`.
- **Resultado:** el plan suministrado para esta implementación se toma como
  contrato de validación; el Excel T1 se conserva sin cambios.
- **Pendiente:** revisar con el equipo los findings producidos por Gate 5.

### Etapa 4 — Arquitectura, loader y contrato inicial

- **Fecha:** 2026-09-27.
- **Objetivo:** definir módulos e implementar la carga y validación del contrato
  de datos.
- **Trabajo realizado:** se acordó avanzar con loader, validator y pruebas;
  desurvey, positioning, visualizer y exporter quedaron sin implementación.
  Se añadieron el loader y las primeras reglas contractuales.
- **Resultado:** nueve pruebas iniciales pasaron con `unittest`.
- **Pendiente:** incorporar las reglas del plan aprobado en ETAPA 3.

### Etapa 5 — Reglas, findings y ejecución

- **Fecha:** 2026-09-27.
- **Objetivo:** implementar las reglas aprobadas, pruebas en memoria, CSV de
  findings/resumen y orquestación.
- **Trabajo realizado:** se añadieron findings estructurados con severidad,
  reglas de collar/survey/intervalos/assay/density/alteration/campañas, escritura
  de reportes y orquestación mínima en `main.py`.
- **Resultado:** 22 pruebas pasaron; `main.py` generó 11,062 findings:
  0 ERROR, 15 WARNING y 11,047 INFO. El resumen por regla suma 11,062.
- **Pendiente:** revisión y aprobación del equipo; no avanzar a desurvey.

### Etapa 6 — Revisión de decisiones geométricas

- **Fecha:** 2026-09-27.
- **Objetivo:** contrastar las decisiones geométricas del equipo con los
  metadatos y observaciones reales antes de escribir código de desurvey.
- **Trabajo realizado:** se revisaron `data_dictionary.csv`,
  `data/raw/README.md`, las 35 filas de collar y las 270 estaciones survey; se
  registraron DECISION-01 a DECISION-06 y los tres casos manuales de control.
- **Resultado:** MD 0 existe en los 35 sondajes y collar/survey coinciden
  exactamente en azimuth y dip. Cada sondaje tiene una sola orientación survey
  distinta a lo largo de sus estaciones. Los metadatos confirman coordenadas
  locales y metros, pero no CRS/EPSG ni que X/Y sean globalmente Easting/Northing.
- **Pendiente en esa etapa:** aprobación del equipo antes de implementar
  desurvey. GATE 6 fue posteriormente aprobado antes de iniciar ETAPA 7.

### Etapa 7 — Desurvey y positioning inicial

- **Fecha:** 2026-09-27.
- **Objetivo:** implementar las decisiones geométricas aprobadas y obtener
  coordenadas XYZ reproducibles para estaciones e intervalos.
- **Trabajo realizado:** se implementó minimum curvature, controles de MD 0 y
  estaciones duplicadas, posicionamiento lineal FROM/MID/TO, integración en
  `main.py` y pruebas unitarias/sobre el release.
- **Resultado:** 36 pruebas PASS; `main.py` calculó 270 estaciones para 35
  sondajes y posicionó 5,817 intervalos (5,275 assay, 117 lithology, 425
  density). Validación independiente: primeros XYZ coinciden con collar,
  últimas profundidades coinciden con `final_depth_m`, MD crece y no se
  observaron desplazamientos por segmento mayores que el avance medido. Los
  ocho hashes de archivos fuente del manifest coinciden. Main reportó ERROR=0,
  WARNING=15, INFO=11,047 (11,062 findings).
- **Aprobación del equipo (GATE 7):** APROBADA. El equipo confirmó 36 pruebas
  PASS y `main.py` con 0 ERROR. La verificación tangencial independiente tuvo
  diferencia máxima `< 1e-9 m` en las 270 estaciones. Para `CR-C01-001`, Z va
  de `3312 m` en MD 0 a `3083.26 m` en MD 230.
- **Pendiente:** no se implementaron visualizer ni exporter en esta etapa;
  visualizer se implementó en ETAPA 8.

### Etapa 8 — Visualización 3D interactiva

- **Fecha:** 2026-09-27.
- **Objetivo:** visualizar resultados ya calculados, sin recalcular desurvey ni
  positioning.
- **Trabajo realizado:** `visualizer.py` construye capas de collars etiquetados,
  trayectorias, intervalos litológicos categóricos y assay coloreado por
  `cu_pct`, seleccionables desde un menú. Los ejes indican metros, el título
  declara sistema cartesiano local sin CRS/EPSG (DECISION-06), y se señala la
  ausencia de topografía del release. El HTML incluye Plotly embebido para uso
  sin conexión; `main.py` lo genera al final.
- **Resultado:** 39 pruebas PASS; `main.py` generó
  `outputs/figures/m01_exploration_3d.html`. El pipeline conservó sus conteos de
  salida: 270 estaciones/35 sondajes, 5,817 intervalos y findings
  ERROR=0, WARNING=15, INFO=11,047.
- **Aprobación del equipo:** APROBADA. El equipo abrió el HTML y confirmó que
  muestra correctamente collars, trayectorias e intervalos.
- **Pendiente:** exporter continúa fuera de alcance.

### Etapa 9 — Validación espacial: figuras y métricas desde productos procesados

- **Fecha:** 2026-09-27.
- **Objetivo:** producir figuras estáticas de control y métricas por sondaje
  exclusivamente a partir de resultados existentes en `data/processed/`.
- **Trabajo realizado:** `validation_plots.py` genera planta con campañas,
  sección litológica proyectada en azimut 145° y Cu por bandas de 50 m y
  litología. Calcula distancias mínimas exactas entre segmentos de las
  polilíneas XYZ de sondajes diferentes, y métricas de profundidad vertical,
  cota de fondo y Cu ponderado por longitud en los últimos 10 m. Los collars
  se obtienen de las estaciones MD=0; las campañas, de tablas intervalares
  procesadas.
- **Resultado:** 40 pruebas PASS; `main.py` genera las tres figuras PNG y
  `m01_validacion_espacial.csv` con 35 filas. La distancia mínima global
  observada es 5.9793 m entre CR-C03-001 y CR-C03-005; todas las filas tienen
  10 m de cobertura assay en el último tramo. Los ocho hashes raw del manifest
  permanecieron iguales.
- **Pendiente:** revisión y aprobación del equipo.

## 10. Decisiones

### DECISION-TECH-01 — Lectura CSV sin dependencias

**Problema:** cargar CSV sin añadir dependencias ni alterar fuentes.

**Alternativas consideradas:**

- A. Incorporar una librería tabular externa.
- B. Utilizar `csv` de la biblioteca estándar y preservar valores como texto.

**Alternativa seleccionada:** B.

**Justificación:** el alcance actual solo requiere leer filas, encabezados y
metadatos; no se requiere una nueva dependencia.

**Impacto:** la interpretación de los tipos queda centralizada en el validador.

### DECISION-TECH-02 — Visualización HTML autocontenida

**Problema:** compartir una vista 3D interactiva de resultados de M01 sin
requerir conexión externa para cargar la biblioteca JavaScript.

**Alternativas consideradas:**

- A. HTML que carga Plotly desde un CDN.
- B. HTML con Plotly embebido.

**Alternativa seleccionada:** B, usando `include_plotlyjs=True`.

**Justificación:** el artefacto requerido debe ser autocontenido e interactivo.

**Impacto:** el HTML tiene mayor tamaño, pero no depende de red en el momento
  de abrirlo.

### DECISION-01 — Sistema XYZ local

**Decisión del equipo:** X = Easting, Y = Northing, Z = elevación; Z positivo
hacia arriba. Coordenadas expresadas en metros.

**Evidencia del release:** `data_dictionary.csv` define `x` y `y` como
coordenadas cartesianas locales, `z` como elevación, y asigna `m` a las tres.
`data/raw/README.md` confirma un sistema cartesiano local y unidades métricas.

**Evaluación:** la unidad y la interpretación de Z como elevación están
respaldadas por los metadatos. Que el eje X sea específicamente Easting y el eje
Y Northing no se puede confirmar con el diccionario o README: no se documenta
orientación de ejes ni CRS. Se registra como convención local adoptada por el
equipo, no como georreferenciación demostrada.

### DECISION-02 — Convención de azimuth

**Decisión del equipo:** grados, 0° hacia +Y/Norte, 90° hacia +X/Este, sentido
horario.

**Evidencia del release:** el diccionario define `azimuth_deg` en grados. Los
valores observados en collar/survey abarcan `0°` a `325.000000001°`; entre los
valores están 0°, 90°, 180° y 270°.

**Evaluación:** unidad y rango numérico son consistentes con la decisión. Los
valores por sí solos no demuestran el eje de referencia ni el sentido de giro;
esas partes quedan registradas como convención acordada por el equipo, no como
hecho inferido únicamente del dataset.

### DECISION-03 — Convención de dip

**Decisión del equipo:** grados medidos desde la horizontal; negativos hacia
abajo y `-90°` vertical descendente.

**Evidencia del release:** `dip_deg` está documentado en grados. Los valores
observados abarcan `-85°` a `-71.925397240°`, tanto en collar como en survey.

**Evaluación:** unidad y signos observados son consistentes con la convención
adoptada; el release no documenta por sí solo el plano de referencia del dip.

### DECISION-04 — Autoridad en MD = 0

**Decisión del equipo:** survey gobierna la trayectoria. Si existe estación
survey en MD 0, se compara con collar; diferencia absoluta mayor que `0.1°` en
azimuth o dip produce `WARNING`. Si falta la estación, se produce `ERROR`.

**Evidencia del release:** los 35 pozos tienen estación survey en `depth_m = 0`.
En los 35, azimuth y dip coinciden exactamente con los respectivos valores del
collar (diferencia absoluta máxima observada: `0°` para ambos).

**Evaluación:** el comportamiento acordado es consistente con los registros
actuales. La tolerancia `0.1°` es una regla de decisión del equipo, no un valor
derivado del dataset. El control de estación faltante no se activa con este
release.

### DECISION-05 — Método de desurvey

**Decisión del equipo:** usar Minimum Curvature para interpolar la trayectoria
entre estaciones.

**Evidencia del release:** al ordenar las 270 estaciones por pozo y profundidad,
cada uno de los 35 pozos tiene un solo par distinto `(azimuth_deg, dip_deg)`;
no se observan cambios de orientación dentro de un mismo pozo. El rango
observado global es azimuth `0°`–`325.000000001°` y dip
`-85°`–`-71.925397240°`.

**Evaluación:** la selección es consistente con la intención de representar una
transición gradual entre estaciones. Con orientaciones constantes a lo largo
de cada pozo, tangential, balanced tangential y minimum curvature deben dar la
misma trayectoria geométrica, salvo diferencias de redondeo numérico; esta
equivalencia queda como control comparativo cuando se implemente el desurvey.
La observación de orientación constante aplica a este release, no a otros
datasets.

### DECISION-06 — CRS/EPSG

**Estado:** ACCEPTED — NON-BLOCKING LIMITATION.

**Decisión del equipo:** M01 trabaja en el sistema cartesiano local del release;
no hará transformaciones ni georreferenciación global.

**Evidencia del release:** `data/raw/README.md` describe coordenadas del sistema
cartesiano local. Ni dicho README ni `data_dictionary.csv` proporcionan
identificador CRS/EPSG.

**Limitación:** los resultados no permiten afirmar una ubicación global ni
transformar de forma defendible a otro CRS.

## Casos manuales de control para desurvey

Estos resultados de control se ejecutaron en ETAPA 7 sobre casos sintéticos.

| Caso | Orientación | Comportamiento esperado |
|---|---|---|
| A — Vertical | Dip `-90°` | X aproximadamente constante, Y aproximadamente constante y Z disminuye al aumentar MD. |
| B — Horizontal Este | Azimuth `90°`, dip `0°` | X aumenta; Y y Z aproximadamente constantes. |
| C — Inclinado Este | Azimuth `90°`, dip `-45°` | X aumenta, Z disminuye y Y aproximadamente constante. |

“Aproximadamente constante” refleja tolerancia numérica del cálculo; no fija
una tolerancia geométrica adicional.

## 11. Archivos creados o modificados

```text
src/m01/__init__.py
src/m01/loader.py
src/m01/validator.py
src/m01/validation_report.py
src/m01/desurvey.py
src/m01/positioning.py
tests/m01/__init__.py
tests/m01/test_m01_data_contract.py
tests/m01/test_m01_validation_rules.py
tests/m01/test_desurvey.py
tests/m01/test_positioning.py
src/m01/visualizer.py
tests/m01/test_visualizer.py
src/m01/validation_plots.py
tests/m01/test_validation_plots.py
main.py
requirements.txt
data/processed/drillhole_trajectory.csv
data/processed/assay_xyz.csv
data/processed/lithology_xyz.csv
data/processed/density_xyz.csv
outputs/tables/m01_validation_findings.csv
outputs/tables/m01_validation_summary.csv
outputs/figures/m01_exploration_3d.html
outputs/figures/m01_planta.png
outputs/figures/m01_seccion_litologia.png
outputs/figures/m01_cu_cota_litologia.png
outputs/tables/m01_validacion_espacial.csv
docs/implementation/IMP-001_m01_validate_desurvey.md
```

## 12. Pruebas realizadas

### Comandos ejecutados

```text
python -m unittest discover -s tests -v
python main.py
```

Ejecutados desde la raíz `C:\Proyecto_Plan\PlanMinUPN-G04` con el entorno
Python existente. `git diff --check` no reportó errores.

### Resultado real de ETAPA 7

- **Status:** PASS
- **Tests passed:** 36
- **Tests failed:** 0
- **Aprobación del equipo (GATE 7):** APROBADA.
- **Verificación tangencial independiente del equipo:** diferencia máxima
  `< 1e-9 m` en las 270 estaciones.
- **Control reportado para `CR-C01-001`:** Z = `3312 m` en MD 0 y Z =
  `3083.26 m` en MD 230.

### Ejecución de `main.py` sobre el release

- **Trayectoria:** 270 estaciones para 35 sondajes.
- **Intervalos posicionados:** assay 5,275; lithology 117; density 425; total
  5,817.
- **Controles del release:** primer XYZ igual al collar en los 35 sondajes;
  última profundidad igual a `final_depth_m` en los 35; MD creciente y único;
  todas las coordenadas finitas; sin incrementos espaciales mayores al
  incremento MD.
- **Estaciones añadidas/extrapoladas:** ninguna.
- **Alteration:** tabla vacía aceptada sin error por el positioning genérico.
- **Salidas:** `data/processed/drillhole_trajectory.csv`,
  `assay_xyz.csv`, `lithology_xyz.csv`, `density_xyz.csv`.

- **Findings:** 11,062
- **ERROR:** 0
- **WARNING:** 15 (`CAMPAIGN_ID_EQUIVALENCE`)
- **INFO:** 11,047 (`ASSAY_GRADE_ZERO`: 10,551; `INTERVAL_GAP_DENSITY`: 460;
  `DENSITY_COVERAGE`: 35; `ALTERATION_UNAVAILABLE`: 1)
- **Salidas:** `outputs/tables/m01_validation_findings.csv` y
  `outputs/tables/m01_validation_summary.csv`
- **Datos fuente:** los ocho hashes publicados en el manifest siguen
  coincidiendo; `data/raw/` no se modificó.

### Resultado real de ETAPA 8

- **Comando:** `python -m unittest discover -s tests -v`
- **Resultado:** PASS; 39 pruebas aprobadas, 0 fallidas.
- **Comando:** `python main.py`
- **Resultado:** PASS; 270 estaciones de trayectoria para 35 sondajes; 5,817
  intervalos posicionados; ERROR=0, WARNING=15, INFO=11,047.
- **Visualización:** `outputs/figures/m01_exploration_3d.html` generado como
  HTML completo con Plotly JavaScript embebido, selector Litología/Assay
  `cu_pct`, ejes XYZ en metros, sistema cartesiano local sin CRS/EPSG y aviso
  de topografía no disponible.
- **Dependencias:** Plotly 7.1.0 ya estaba instalado en el entorno; se agregó
  `plotly` a `requirements.txt`, sin instalar librerías.
- **Aprobación del equipo (ETAPA 8):** APROBADA; el HTML fue abierto y se
  verificó visualmente que muestra collars, trayectorias e intervalos.

### Resultado real de ETAPA 9

- **Prueba focal:** `python -m unittest tests.m01.test_validation_plots -v` —
  PASS, 1 prueba.
- **Suite completa:** `python -m unittest discover -s tests -v` — PASS, 40
  pruebas, 0 fallidas.
- **Ejecución:** `python main.py` — PASS; 270 estaciones/35 sondajes, 5,817
  intervalos, findings ERROR=0, WARNING=15, INFO=11,047.
- **Figuras generadas:** `outputs/figures/m01_planta.png`,
  `m01_seccion_litologia.png` y `m01_cu_cota_litologia.png`.
- **Tabla generada:** `outputs/tables/m01_validacion_espacial.csv`, 35 filas.
  Incluye `nearest_other_hole_id`, `minimum_trajectory_distance_3d_m`,
  `vertical_depth_m`, `bottom_elevation_m`, `cu_mean_last_10m_pct` y
  `cu_covered_length_last_10m_m`.
- **Resultado espacial:** mínimo global de 5.979267 m entre CR-C03-001 y
  CR-C03-005. La profundidad vertical observada abarca 222.552–428.008 m y la
  cota de fondo 3059.530–3097.320 m. Cu de últimos 10 m tiene cobertura de
  10.0 m en los 35 sondajes.
- **Datos fuente:** los ocho hashes listados por el manifest coinciden; no se
  modificó `data/raw/`.
- **Dependencia:** matplotlib 3.11.2 disponible tras instalar la dependencia ya
  declarada en `requirements.txt`.

## 13. Validación minera

- [ ] Unidades consistentes.
- [ ] Signos económicos correctos cuando corresponda.
- [ ] Magnitudes razonables.
- [ ] Restricciones operacionales respetadas.
- [x] Casos geométricos A/B/C y comparación tangencial ejecutados.
- [x] Primer XYZ de cada pozo igual al collar.
- [x] Última profundidad coincide con `final_depth_m` en el release.
- [x] Continuidad discreta y MD creciente revisados.
- [x] Posicionamiento de intervalos dentro de la trayectoria revisado.
- [x] Visualización usa exclusivamente geometría e intervalos calculados.
- [x] HTML interactivo generado y autocontenido.
- [x] Ausencia de topografía indicada sin inventarla.
- [x] Figuras de validación generadas desde `data/processed/`.
- [x] Distancias entre trayectorias calculadas en segmentos XYZ, sin muestreo
  ni reprocesamiento de desurvey.
- [x] Métricas por sondaje y cobertura de Cu de último tramo revisadas.

### Evidencia / comentario

Los casos A/B/C y control tangencial pasan. En el release, se observaron 35
trayectorias completas hasta `final_depth_m`; no se añadieron estaciones. La
posición de intervalos conserva los atributos analíticos. El visualizador usa
los XYZ ya calculados en las tablas del pipeline; no hay fuente topográfica en
este release, por lo que la figura lo indica en el título. Persisten 15
warnings de campaña y 11,047 INFO de Gate 5, no relacionados con la geometría.
El equipo aprobó GATE 7 con la comparación tangencial independiente y aprobó
ETAPA 8 tras abrir y revisar el HTML.

## 14. Limitaciones y pendientes

### LIMITATION-01

El XYZ entre estaciones de posicionamiento usa interpolación lineal entre
estaciones calculadas; no reevalúa la curva minimum-curvature en MD intermedios.
No hay CRS/EPSG global según la limitación aceptada en DECISION-06.

### FUTURE-01

La visualización representa las trayectorias mediante los segmentos de
estaciones disponibles y posiciona cada intervalo litológico como el segmento
FROM–TO ya calculado. No incorpora topografía porque el release no contiene esa
superficie. Las etapas 7 y 8 fueron aprobadas por el equipo. Exportación
adicional continúa pendiente y fuera del alcance. ETAPA 9 generó métricas de
control a partir de las polilíneas y los intervalos procesados.

## 15. Uso del agente de IA

- [x] Arquitectura.
- [x] Implementación.
- [x] Pruebas.
- [x] Documentación.

Comentario: implementación de la carga de datos, validación contractual,
pruebas automatizadas y registro inicial de trazabilidad.

## 16. Checklist de cierre

- [x] Problema minero documentado.
- [x] Inputs documentados.
- [x] Unidades verificadas en la fuente documental.
- [x] Supuestos identificados.
- [ ] Lógica minera documentada y validada.
- [ ] Implementación terminada para M01.
- [x] Pruebas ejecutadas.
- [x] Validación computacional realizada para el alcance implementado.
- [ ] Validación minera de desurvey realizada.
- [x] Archivos modificados registrados.
- [x] Limitaciones registradas.
- [x] Registro actualizado.

**M01 permanece `IN_PROGRESS`.**
