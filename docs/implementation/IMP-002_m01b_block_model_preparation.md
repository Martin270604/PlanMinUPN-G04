# IMP-002 — M01B Block Model Preparation

## 1. Identificación

- **Implementation ID:** IMP-002
- **Module:** M01B — preparación de datos para modelo de bloques geológico preliminar
- **Date:** 2026-10-23
- **Group:** G04
- **Participants:** Jorge Martín Sánchez Linares, Erwin Segundo Olivera Cercado, Alesandra Briyit Guevara Díaz.
- **Status:** IN_PROGRESS

Este registro comienza durante T2 como recuperación documentada de M01B. No afirma que hubiera un baseline, decisiones, composites o pruebas de compositing anteriores. Se actualiza únicamente con evidencia y decisiones reales de la sesión.

## 2. Problema minero

Preparar datos de sondajes para una representación categórica preliminar de litología en bloques, conservando soporte, contactos, procedencia e incertidumbre. La división geométrica de un ensayo no crea mediciones analíticas nuevas ni determina por sí sola un dominio geológico.

## 3. Objetivo

Documentar el estado comprobado de M01B, las decisiones del estudiante, los artefactos que se produzcan con autorización independiente, sus pruebas y sus limitaciones. Al inicio de este registro no se han generado composites ni un modelo de bloques.

## 4. Inputs

| Variable | Significado | Unidad | Origen | Validación disponible |
|---|---|---|---|---|
| Assay | Intervalos analíticos con ley de Cu y otros campos | m; Cu en % según `data/raw/data_dictionary.csv` | `data/raw/assay.csv` | Conteos de longitudes/residuos y cruces realizados en lectura; no son pruebas de compositing |
| Lithology | Intervalos observados con `lith_code` | m | `data/raw/lithology.csv` | Contactos contiguos y cobertura de residuos verificados en lectura |
| Collar | Profundidad final declarada por sondaje | m | `data/raw/collar.csv` | Usado para comprobar que el residuo terminal alcanza `final_depth_m` |
| Manifest/diccionario | Conteos, procedencia, campos y unidades | No aplica | `data/raw/release_manifest.json`, `data/raw/data_dictionary.csv` | Ocho hashes SHA-256 del manifest comparados con archivos; todos coincidieron |

Los datos originales de `data/raw/` son inmutables y no fueron modificados.

## 5. Outputs

| Variable / resultado | Significado | Unidad | Destino |
|---|---|---|---|
| Registro contemporáneo de baseline y decisiones | Evidencia de recuperación y faltantes de M01B | No aplica | Este IMP y `docs/exam/T2_M01B_EVIDENCE_G04.md` |
| Plan conversacional incremental | Decisiones y estado del examen, no un plan resuelto | No aplica | `docs/exam/T2_M01B_PLAN_G04.md` |
| Composites | **No generados** al inicio de este registro | m y unidades analíticas de origen | Pendiente de decisiones, gate y autorización de implementación |
| Modelo de bloques | **No generado** | Coordenadas/unidades pendientes de definir | Fuera del estado actual |

## 6. Supuestos y decisiones

### DECISION-01 — Prioridad de recuperación

- **Alternativa elegida:** A — auditar assay/litología y establecer reglas de compositado como prioridad.
- **Justificación del estudiante:** transcripción literal en `docs/exam/T2_M01B_PLAN_G04.md`.
- **Evidencia comprobada:** 5.275 ensayes; 5.245 de 2 m y 30 residuos; 82 contactos internos contiguos; 57 ensayes de 2 m cruzan contactos.
- **Limitación:** la decisión no resuelve la disponibilidad de topografía (B09).

### DECISION-02 — Ensayes que cruzan contactos

- **Alternativa elegida:** A — dividir geométricamente en el contacto y conservar la ley original asociada a ambos segmentos con trazabilidad del mismo `sample_id`.
- **Conteo comprobado:** los 57 cruces se dividen en 1 m + 1 m; son 114 segmentos derivados.
- **Supuesto/limitación:** cada segmento hereda la ley medida en el intervalo original de 2 m. La ley real de cada mitad es desconocida; no contar los segmentos como dos ensayes independientes.

### DECISION-03 — Tramos cortos

- **Alternativa elegida:** A — conservar los tramos cortos con longitud real y distinguir su tipo (contacto o residuo), sin excluirlos ni unirlos de forma automática.
- **Evidencia comprobada:** 30 residuos terminales de 0,050936–1,984641 m; 11 menores de 0,5 m. Por cruce de contactos hay 114 segmentos de 1 m. Estos grupos suman 144 tramos cortos derivados/terminales en el conteo presentado, pero su combinación y tratamiento en composites no está implementada.
- **Limitación:** soporte variable; futuras etapas deberán decidir el uso de estos tramos y cualquier criterio mínimo con justificación.

### DECISION-04 — Clasificación de contactos cruzados

Se registran seis transiciones dirigidas por profundidad: REG→DIO 31; DIO→POR 10; REG→POR 8; POR→BRX 5; BRX→POR 2; DIO→REG 1. No se infiere significado geológico a partir de los nombres de código. DIO→REG se conserva como observación para revisar, no como error, dado que el diccionario consultado no explica la semántica geológica de los códigos.

### DECISION-05 — Baseline M01B ausente

- **Alternativa elegida:** C — no reconstruir decisiones ni resultados históricos que carecen de evidencia; documentar la recuperación iniciada durante T2.
- **Límite de verificación:** el estudiante proporcionó salida de `git fetch origin` y `git branch -r` que muestra solo `origin/main` y `origin/feature/m01-architecture`. Esta salida se conserva como evidencia aportada por el estudiante; no fue ejecutada independientemente en esta sesión.

### DECISION-06 — Artefactos de trazabilidad

El estudiante autorizó crear este IMP y los dos documentos T2 con contenido inicial de recuperación. Esa autorización cubre documentación exclusivamente; no autoriza código, cambios en fuentes, modificaciones de plantilla protegida, commit ni push.

### DECISION-07 — Soporte nominal de compositing

- **Alternativa elegida:** A — longitud objetivo/nominal de 2 m; respetar contactos y conservar tramos más cortos con longitud real.
- **Justificación:** 5.245 de 5.275 ensayes observados tienen soporte de 2 m; no hay altura de banco ni diseño minero en el repo que justifique otro soporte. El T2 no estima leyes a bloques.
- **Evidencia/limitación:** 57 intervalos de 2 m cruzan contactos y generan 114 segmentos geométricos de 1 m; 30 residuos terminales son variables. No se crean mediciones nuevas; para subtramos derivados se debe conservar trazabilidad al `sample_id` original y la cautela de que la ley por mitad no fue medida.
- **Separación de escalas:** la longitud nominal de composite no prescribe el tamaño del bloque; este queda pendiente de P2 y del espaciamiento real entre sondajes.

### DECISION-08 — Anclaje de bins

- **Alternativa elegida:** B — bins nominales de 2 m anclados en 0 m del collar; no cruzar contactos, ponderar por longitud y conservar tramos parciales.
- **Evidencia comprobada en lectura:** los 5.275 valores `from_m` son múltiplos de 2; de los 82 contactos internos, 25 son de profundidad par y 57 impar. No se encontraron contactos internos no enteros.
- **Consecuencia para estos datos:** la grilla anclada al collar coincide con los inicios assay; los contactos pares coinciden con límites de ensaye y los impares bisecan geométricamente los intervalos de 2 m.

### DECISION-09 — Agregación y soporte parcial

- **Alternativa elegida:** A — media ponderada por longitud aportada; registrar longitud cubierta, marcar soportes menores de 2 m como parciales y no rellenar faltantes con ley cero.
- **Justificación/limitación:** un tramo de residuo corto no debe recibir igual peso que un assay de 2 m. La ponderación supone ley uniforme en cada intervalo assay; no es una medición nueva.
- **Verificación específica:** al intersectar assays y litología con bins de 2 m anclados en 0 m, se encontraron cero grupos sondaje/bin/litología con más de un intervalo assay y cero grupos con más de una fila lithology del mismo código.
- **Regla conceptual documentada:** intersecar assay y lithology por `hole_id`/MD; usar bins 2 m desde MD 0; no atravesar contactos; heredar la ley assay para cada segmento derivado; si varios aportes entran en una combinación bin/litología, calcular `sum(ley * longitud aportada) / sum(longitud aportada)`; registrar longitud cubierta, marcar parcial si es <2 m y no imputar cero; conservar residuos terminales.
- **Estado:** B07 VERIFIED como decisión documentada y reproducible para este dataset; no se implementó ni probó el algoritmo M01B (B08).

### DECISION-10 — Identificador y procedencia de composite

- **Alternativa elegida:** A — `composite_id` único por fila, conservando el `sample_id` original como vínculo de procedencia y repitiéndolo en segmentos derivados del mismo assay.
- **Conteo esperado, no generado:** 5.332 filas (5.275 assays más una fila adicional para cada uno de los 57 ensayos partidos); 57 valores `sample_id` aparecerían en dos filas cada uno.
- **Limitación:** el identificador debe ser determinista y estable entre ejecuciones. Su formato aún no está fijado; no existe tabla de composites.

### DECISION-11 — Formato determinista de identificador

- **Alternativa elegida:** A — `hole_id` más índice secuencial de cuatro dígitos por profundidad, ordenado por `from_m` y `to_m`; ejemplo aportado: `CR-C01-001_0001`.
- **Comprobación:** 35 sondajes; entre 115 y 218 ensayes por sondaje en la fuente, por lo que el ancho de cuatro dígitos cubre el dataset actual. Ordenar y reiniciar índice por sondaje permite regeneración estable mientras las entradas/reglas no cambien.
- **Límite:** los índices derivados pueden cambiar si cambia la fuente o la regla. `sample_id` se conservará para la trazabilidad permanente a la medición original.

### Gate B08 — aprobado y ejecutado

El estudiante aprobó explícitamente el alcance de `src/m01/compositing.py`, `tests/m01/test_compositing.py` y `data/processed/m01b_composites.csv`, exigiendo el intérprete `.venv`, ejecución de las pruebas específicas seguida de la suite completa, comando de generación reproducible y comparación literal de conteos, sin cambiar `data/raw/`, `main.py` o gobernanza, instalar, commit o push.

La función `build_composites(assay, lithology, trajectory, target_length_m=2.0) -> CsvTable` valida entradas/cobertura, segmenta por contacto y bin, pondera por longitud aportada, marca parciales sin imputar ley cero, asigna IDs `hole_id_####` por orden de profundidad y calcula FROM/MID/TO con `position_intervals` sin extrapolar. Se generó el CSV, con 5.332 filas; detalles, columnas y resultados de pruebas se registran en `docs/exam/T2_M01B_EVIDENCE_G04.md`. El estudiante interpretó los resultados y B08 se declara VERIFIED computacionalmente, no geológicamente.

## 7. Diseño computacional

La implementación M01B aprobada está aislada en `src/m01/compositing.py`; no modifica la orquestación `main.py`. M01 aporta `CsvTable` y el posicionador existente. La salida se escribe en `data/processed/m01b_composites.csv`; las pruebas residen en `tests/m01/test_compositing.py`.

## 8. Etapas de implementación / recuperación

### Etapa 1 — 2026-10-23: diagnóstico y auditoría de lectura

- **Objetivo:** comprobar el estado M01/M01B sin modificar archivos.
- **Trabajo realizado:** lectura de gobernanza, escenario de examen, documentación del proyecto, IMP-001, fuentes/derivados M01, pruebas y outputs. Conteos de longitudes, residuos, contactos y cruces calculados desde las fuentes originales mediante comandos PowerShell de solo lectura.
- **Resultado:** evidencia M01 presente; no se encontró IMP-002, código de compositing, composites o topografía local. Conteos y limitaciones constan en `docs/exam/T2_M01B_EVIDENCE_G04.md`.
- **Pendiente:** auditoría completa B06, decidir reglas completas B07, implementar y probar B08 tras gate, resolver B05 incrementalmente, y localizar/verificar topografía para B09.

### Etapa 2 — 2026-10-23: inicio del registro

- **Objetivo:** conservar contemporáneamente el diagnóstico y las decisiones iniciales de recuperación.
- **Trabajo realizado:** creación autorizada de este IMP y los dos documentos de examen.
- **Resultado:** se registra una línea base M01B incompleta, sin atribuir trabajos previos inexistentes.
- **Pendiente:** confirmar el contenido inicial y continuar por decisiones. No hay gate aprobado para implementación de código.

### Etapa 3 — 2026-10-23: especificación conceptual B07

- **Objetivo:** definir una regla de compositado específica para el grupo y contrastar su premisa de alineación con las fuentes.
- **Trabajo realizado:** verificación en lectura de `from_m` assay y paridad de contactos; intersección por sondaje entre assay, lithology y bins 2 m anclados en 0 m; comprobación de número de intervalos assay/litología por bin y código litológico.
- **Resultado:** B07 VERIFIED como regla documentada: separar contactos, ponderar aportes por longitud si aplica, conservar residuos parciales y declarar su soporte sin imputar ley cero. La geometría observada presenta 114 segmentos parciales en contactos y 30 residuos, como resultado esperado, no como composites generados.
- **Pendiente al cierre de Etapa 3:** B08 implementar, probar y producir la tabla bajo gate; el resto de bloqueos B05/B09/B10 persiste según la matriz de evidencia. Etapa 4 registra la resolución posterior de B08.

### Etapa 4 — 2026-10-23: implementación y generación autorizadas B08

- **Autorización:** aprobación explícita del estudiante para crear únicamente `src/m01/compositing.py`, `tests/m01/test_compositing.py` y `data/processed/m01b_composites.csv`; ejecutar con `C:\Proyecto_Plan\.venv\Scripts\python.exe`; no cambiar `data/raw/`, `main.py` o gobernanza; no instalar, commit o push.
- **Función:** `build_composites(assay, lithology, trajectory, target_length_m=2.0) -> CsvTable`; verifica columnas, números, intervalos y cobertura litológica; corta en contactos y bins anclados en 0; pondera leyes por longitud aportada; registra longitud cubierta, soporte nominal y parcialidad sin imputar ley cero; genera IDs estables `hole_id_####`; calcula FROM/MID/TO con `position_intervals` M01 y rechaza falta de cobertura XYZ.
- **Comando de generación:** `C:\Proyecto_Plan\.venv\Scripts\python.exe -m src.m01.compositing` desde la raíz del repositorio. Resultado real: `composites_written=5332`, salida `data/processed/m01b_composites.csv`, exit code 0.
- **Pruebas específicas:** `C:\Proyecto_Plan\.venv\Scripts\python.exe -m unittest discover -s tests\m01 -p test_compositing.py -v`; 7 PASS, `OK`, exit code 0.
- **Suite completa posterior:** `C:\Proyecto_Plan\.venv\Scripts\python.exe -m unittest discover -s tests -v`; 47 PASS (40 M01 + 7 compositing), `OK`, exit code 0. Tiempos y salidas constan en EVIDENCE.
- **Conteos esperados vs. reales:** 5.332 filas = 5.332; filas de 2 m 5.188 = 5.188; parciales 144 = 144; sample IDs repetidos dos veces 57 = 57; IDs compuestos únicos 5.332. Diferencias: ninguna.
- **Validación descriptiva de soporte:** longitud total compuesta 10.518,328249553 m, igual a la suma assay; cero diferencias por source `sample_id` y cero incongruencias entre soporte de composite y litología; 5.332 filas tienen XYZ no vacío. Los ocho hashes SHA-256 del manifest siguen coincidiendo.
- **Interpretación del estudiante:** el resultado es consistente computacionalmente, no una validación geológica; duplicaciones de `sample_id` representan las mismas mediciones partidas y los parciales no se tratan como soporte de 2 m. Identificó un composite de 2 m con `lith_code=AIR` para revisión en P1; no se infiere que el código signifique aire físico.
- **Verificación posterior:** Cu ponderado por longitud antes/después `0.252487149710 %`; cero composites difieren del Cu del assay fuente; una fila `AIR`; longitud total y soporte por muestra/litología coincidentes; 8/8 hashes del manifest coinciden.
- **Estado:** B08 VERIFIED en sentido computacional; esto no acredita validación geológica/económica ni block model. No se generó bloque geológico; topografía/aire-roca sigue `RECOVERY_BLOCKED`.

## 9. Pruebas realizadas

### Comandos / comprobaciones

- Las comprobaciones de datos fueron scripts PowerShell de solo lectura que importaron `data/raw/assay.csv`, `lithology.csv`, `collar.csv` y `release_manifest.json`, calcularon longitudes, cruces por sondaje, solapes con litología y SHA-256. Resultados literales y resumen de operaciones: `docs/exam/T2_M01B_EVIDENCE_G04.md`.
- El estudiante aportó como salida de terminal:

```text
git fetch origin
git branch -r
  origin/HEAD -> origin/main
  origin/feature/m01-architecture
  origin/main
```

- No se ejecutaron pruebas del modelo de bloques.

### Resultado real

- **Status compositing tests:** 7 PASS, exit code 0; full suite 47 PASS, exit code 0.
- **Pruebas históricas M01:** `IMP-001` registra 36 pruebas PASS en Etapa 7, 39 en Etapa 8 y 40 en Etapa 9. Una ejecución actual con Python del sistema terminó con exit code 1: 36 pruebas pasaron y dos módulos no se pudieron importar por dependencias ausentes (`matplotlib`, `plotly`). La ejecución actual con `C:\Proyecto_Plan\.venv\Scripts\python.exe -m unittest discover -s tests -v` terminó con **40 PASS**, `OK`, exit code 0. Ninguna es una prueba M01B.

## 10. Validación minera

- **Composites M01B:** generados y comprobados en conteos/soporte; validación minera formativa espera interpretación del estudiante.
- **Modelo de bloques / dominios:** no generado ni validado.
- **Interpretación de leyes en mitades de ensayes:** pendiente; el valor repetido es una atribución derivada bajo el supuesto de ley uniforme, no una nueva observación.
- **Topografía:** no disponible localmente durante el diagnóstico; clasificación aire/roca bloqueada.
- Los conteos auditados son comprobaciones descriptivas de archivos, no validación minera de un modelo.

## 11. Archivos creados o modificados

```text
docs/implementation/IMP-002_m01b_block_model_preparation.md
docs/exam/T2_M01B_PLAN_G04.md
docs/exam/T2_M01B_EVIDENCE_G04.md
src/m01/compositing.py
tests/m01/test_compositing.py
data/processed/m01b_composites.csv
```

No se modificaron `data/raw/`, archivos de gobernanza ni `docs/templates/MODULE_IMPLEMENTATION_TEMPLATE.md`. No se hizo commit ni push.

## 12. Limitaciones y pendientes

- **B05: PARTIAL**: la falta de baseline previo queda documentada y no se reconstruye historia inexistente; sí existe evidencia contemporánea nueva de implementación y pruebas.
- **B06: VERIFIED** para la auditoría de datos assay/lithology prevista: cobertura 0–`final_depth_m`, suma de longitudes por sondaje, gaps/overlaps, contactos, claves nulas/duplicadas, campos/unidades y valores negativos/cero de Cu/Mo/Au contrastados con los reportes. QA/QC y semántica de códigos no se interpretan y quedan fuera de lo verificado.
- **B07: VERIFIED** como regla conceptual documentada y reproducible para el grupo: grilla 2 m anclada en collar, separación en contactos, agregación ponderada por longitud si hay varios aportes, cobertura parcial explícita y conservación de residuos. No implica implementación.
- **B08: VERIFIED (computacional)**; código, 7 pruebas específicas, suite completa y tabla con conteos/soporte conformes. No equivale a validación geológica.
- **B09: VERIFIED (uso relativo local, actualización 2026-10-24)**; `Topopl.csv` fue verificado con hash, esquema, cobertura muestreada y compatibilidad relativa con collars. El CSV no declara unidades/CRS/datum; no hay superficie interpolada ni clasificación aire/roca.
- **B10: VERIFIED**; 7 pruebas específicas y 47 pruebas totales PASS en `.venv`, con comandos y resultado de generación trazables.
- **Estado actualizado 2026-10-24:** `BASE_VERIFIED=SI` para continuar el plan con topografía en el marco cartesiano local; B05 permanece PARTIAL por ausencia de baseline histórico. Esta transición no autoriza implementación.
- **Modo actual:** EVALUATION_PLAN conceptual P0-P6, tras la nueva evidencia B09 y de acuerdo con las decisiones conservadas; no hay autorización de generación de malla.
- **Reapertura P2/P3:** el maximo Topopl observado dentro de la huella candidata es 3554 m, frente al limite previo 3530 m. Si se conservan origen z=3050 m y dz=10 m, se requieren al menos nz=51, zmax=3560 m, y 41,412 bloques con nx=28, ny=29. No son parametros aprobados ni una malla generada. P3 debe definir el tratamiento/interpolacion y comprobar cobertura de la superficie por celda antes de asignar estados topograficos.
- **P1 conceptual:** se mantiene cada `lith_code` como categoría observada independiente, sin semántica geológica inventada; `AIR` queda marcado `REVIEW/UNKNOWN` y excluido del soporte geológico según la decisión conceptual registrada. No se crea ni remapea ningún dato.

## 15. Actualizacion B09 — 2026-10-24

El estudiante reporta que el docente entrego el archivo oficial `data/raw/Topopl.csv`. En lectura independiente se confirmo SHA-256 `1724a97f1fa6f6a059def896d1ba566b1e23d6f78781034bf2e3f53d2d4b1887`, 218,112 filas con campos `PID,X,Y,Z`, valores finitos, cero nulos/duplicados PID/XYZ, y 99.1972 % de Z enteros. Sus extensiones son X `242090.504105–243287.725586`, Y `8195892.194946–8197095.651855`, Z `3120.858516–3596.0`. Dentro de la huella XY candidata se contaron 63,375 puntos y Z `3246–3554 m`.

Control de cobertura muestreado a 20 m en la huella (870 consultas): distancia al punto mas cercano min `0.007 m`, mediana `1.725 m`, p95 `6.038 m`, max `17.427 m`. Control collar-superficie IDW8 con ponderacion `1/d^2`, sobre 35 collars: residuos `z_collar-z_IDW8` min `-1.365264 m`, max `1.118721 m`, mediana absoluta `0.308264 m`; distancia XY al punto mas cercano mediana `1.332593 m`, maxima `5.347814 m`. Este metodo de control no se presenta como el interpolador oficial o el mismo usado por el estudiante.

El collar esta documentado en metros y coordenadas cartesianas locales; el CSV topografico no declara unidades, CRS/EPSG ni datum. El encaje observado es consistente con uso relativo en ese marco local, pero no prueba una referencia geodesica ni autoriza conversion. B09 se actualiza a `VERIFIED` unicamente para superposicion local, con esta limitacion registrada. La superficie no se interpolo y no se clasifico aire/roca.

El antiguo limite z=3530 m no contiene el maximo puntual observado de 3554 m dentro de la huella. Conservando z0=3050 m y dz=10 m, el minimo limite de celda siguiente seria zmax=3560 m y nz=51; con nx=28 y ny=29, 41,412 celdas. Reabrir y aprobar P2 sigue pendiente. P3_TOPO tambien sigue pendiente de la representacion/interpolacion elegida y su comprobacion por celda. No se modifico ningun archivo de `data/raw/`; no hubo instalacion, staging, commit ni push.

La seleccion conceptual posterior del estudiante es `nz=51` (k=0–50, celdas 3550–3560 m en la capa superior), con conteo 41,412. Se registra como propuesta, no como aprobacion del gate P2_GRID. Aunque la interpolacion lineal/IDW con pesos positivos y normalizados no supera el maximo de los datos que usa, el maximo 3554 m solo se comprobo dentro de la huella; el conjunto topografico total incluye cotas hasta 3596 m fuera de ella. La suficiencia del limite y cualquier clasificacion de la capa siguiente como AIR dependen del dominio/vecindarios que se aprueben en P3.

El estudiante eligio conceptualmente para P3 los puntos Topopl dentro de la huella mas un buffer de 20 m, rectangulo X `242400–243000`, Y `8196160–8196780`. Verificacion de lectura: 73,309 puntos, Zmax=3554 m; buffer de 40 m: 83,317 puntos, mismo Zmax; huella sin buffer: 63,375, Zmax=3554 m. Se evaluo PARCIAL — H1: conteos reproducidos y limite maximo matematico correcto para interpolacion convexa, pero el conteo no prueba cobertura en todos los bordes. P3 debe examinar cobertura espacial antes de interpolar.

Se definió conceptualmente el gate P2_GRID con origen `(242420,8196180,3050) m`, celdas `20×20×10 m`, conteos `28×29×51`, salida `data/processed/m01b_block_grid.csv` y 41,412 bloques. El gate fue aprobado e implementado en la sección 16. P2 separa geometría nominal de la futura clasificación topográfica P3 y de la asignación P4.

## 16. Implementacion P2_GRID — 2026-10-24

El estudiante aprobo el gate P2_GRID con alcance restringido a generar la geometria acordada. Se implemento `src/m01/block_model.py`, se añadieron `tests/m01/test_block_model.py` y `data/processed/m01b_block_grid.csv`. No se incorporaron estados topograficos, dominios litologicos, leyes ni interpolacion. Comando exacto, desde la raiz:

```powershell
& 'C:\Proyecto_Plan\.venv\Scripts\python.exe' -m src.m01.block_model
```

Resultado de generacion: `blocks_written=41412`, exit code 0. El archivo generado tiene 41.412 filas, IDs unicos/contiguos 0–41.411, centros correctos en extremos `(242430,8196190,3055)` y `(242970,8196750,3555)`, dimensiones únicas `(20,20,10)` y volumen nominal único de `4000`. Las 270 estaciones de `drillhole_trajectory.csv` estan dentro de los limites aprobados. SHA-256 de la salida: `7c458acd98e3c60e09689c063f1a662d317b999fee2542f49fc32b6d2f76e5b6`.

Pruebas específicas: `& 'C:\Proyecto_Plan\.venv\Scripts\python.exe' -m unittest tests.m01.test_block_model -v` — 7 PASS, exit code 0. Suite completa: `& 'C:\Proyecto_Plan\.venv\Scripts\python.exe' -m unittest discover -s tests -v` — 54 PASS, exit code 0. Las pruebas verifican las invariantes de cada fila y serializacion reproducible byte por byte, además de rechazar dimensiones de celda no positivas y estaciones fuera de limites.

El CSV representa volumen nominal de celda, no volumen neto de roca. La malla no clasifica AIR/ROCK ni se declara `MINING_VALIDATED`; la incertidumbre sobre cobertura, método de interpolación y referencia topográfica sigue para P3. No se modificó `data/raw/`, `main.py` ni gobernanza, no se instalaron dependencias y no hubo commit/push. P3 y P4 permanecen fuera del alcance autorizado.

### Semantica de coordenadas del CSV

En `data/processed/m01b_block_grid.csv`, las columnas `x`, `y`, `z` son las coordenadas del **centro** de cada bloque, calculadas como `origin_axis + (index + 0.5) * cell_size`. No representan esquina inferior ni origen. La prueba del primer y último centro confirma esta convención. Se conserva el nombre de campos autorizado en el gate; cualquier renombrado a `center_x/center_y/center_z` requerirá una etapa autorizada posterior y actualización coordinada de consumidores, pruebas y contrato.

El estudiante interpretó P2_GRID como consistente computacionalmente y señaló que P3 aún debe decidir aire/roca; esta interpretación no constituye `MINING_VALIDATED`. Las notas conceptuales P3.1–P3.4 que siguen registran el estado de cada decisión antes de la aprobación e implementación posteriores, que se documentan en la sección 17.

### Decisión conceptual P3.1 — IDW

El estudiante propone IDW con `k=8`, potencia `2`, limitado a los 73.309 puntos del rectángulo de huella más buffer de 20 m. El método y rango convexo son conceptualmente reproducibles si los pesos se normalizan y son no negativos; los parámetros no están validados. Para los 812 centros XY de columnas del grid, la distancia al octavo vecino en ese dominio tiene mediana 6.396 m, p95 12.799 m y máximo 21.313 m. Por tanto, el control previo de la distancia al vecino más cercano no basta para afirmar que los ocho vecinos siempre estén a pocos metros o que el suavizado sea despreciable frente a dz=10 m. No se calculó la superficie. Evaluación registrada: PARCIAL — H1.

La decisión sobre qué estado asignar cuando el soporte sea distante (umbral 10 m, 20 m, reporte sin corte duro o umbral derivado de validación espacial) sigue pendiente. P3 continúa conceptual y no autorizado para implementación.

El estudiante eligió conceptualmente un corte de 20 m sobre distancia al vecino más cercano y registrar también la distancia al octavo vecino. Para los 812 centros XY, vecino más cercano máximo observado = 13.140 m, así que el corte no excluye ninguno de ellos en la medición actual; no está probado que detecte huecos en los centros existentes. El octavo vecino alcanza 21.313 m. Umbral no validado con errores verticales. Evaluación PARCIAL — H1. Se distingue `OUTSIDE_TOPO_COVERAGE` (fuera del dominio fuente) de `TOPO_UNKNOWN` (dentro del dominio, soporte bajo). La regla AIR/ROCK/PARTIAL está pendiente de respuesta P3.3; no se calculó superficie ni se implementó código.

Para las 870 esquinas XY (29×30), se verificó dentro del dominio de 20 m la distancia al vecino más cercano: mediana 1.725 m, máximo 17.427 m; ninguna excede el umbral propuesto. El estudiante propone clases por mínimos/máximos de las cuatro cotas IDW, con `ROCK`, `AIR`, `PARTIAL` o estados desconocidos. Evaluación PARCIAL — H1: conteos y regla son reproducibles, pero los extremos IDW pueden ocurrir entre esquinas; no garantiza con certeza geométrica que el bloque entero quede de un lado. No se calculó superficie/clasificación ni fracción de roca. La prioridad de estados cuando algunas esquinas no tienen soporte queda pendiente de P3.4.

La respuesta P3.4 define una consolidación conservadora por prioridad: `OUTSIDE_TOPO_COVERAGE` si alguna esquina sale del dominio; si no, `TOPO_UNKNOWN` si alguna distancia nearest >20 m; si las cuatro consultas son válidas, aplicar clases geométricas y guardar la distancia máxima nearest por bloque. Verificación: 870/870 esquinas dentro del dominio, nearest máximo 17.427 m y ninguna >20 m. Evaluación CORRECTA — H0. Todos son elegibles para clasificación geométrica, sin inferir el resultado de clases.

Se propuso el gate `P3_TOPO` con `src/m01/topography.py`, `tests/m01/test_topography.py`, `data/processed/m01b_topography_vertices.csv` y `data/processed/m01b_block_topography.csv`. Incluye IDW k=8/potencia 2, soporte >20 m, reglas por cuatro esquinas, estados agregados/prioridad, casos sintéticos, holdout espacial P5 y límites. El gate fue aprobado e implementado en la sección 17. P4/P6 quedan excluidos.

## 17. Implementación P3_TOPO — 2026-10-24

El estudiante aprobó el gate P3_TOPO con los parámetros acordados. `src/m01/topography.py` filtra los puntos Topopl a la ventana cerrada X `242400–243000`, Y `8196160–8196780`, calcula IDW con `k=8`, potencia 2 y pesos normalizados, registra distancias al vecino 1 y 8, aplica nearest-distance `>20 m` como `TOPO_UNKNOWN`, y usa estados por vértice compartido. Para cada bloque, prioridad de una esquina fuera del dominio (`OUTSIDE_TOPO_COVERAGE`), luego soporte insuficiente (`TOPO_UNKNOWN`), y solo con cuatro elevaciones válidas: `ROCK` si el techo ≤ mínimo de cotas; `AIR` si la base ≥ máximo; si no `PARTIAL`. Se guarda la distancia nearest máxima por bloque. No se calcula fracción ni se altera el volumen nominal.

Salidas generadas:

- `data/processed/m01b_topography_vertices.csv`: 870 vértices (29×30), `z_topo` entre 3245.600835 y 3554.000000 m; hash SHA-256 `9275729217ea792cd51dffbbece511a196da0edc2acbebb17596f63a9b2c38ae`.
- `data/processed/m01b_block_topography.csv`: 41.412 block_id; estados ROCK=25.732, AIR=13.770, PARTIAL=1.910, TOPO_UNKNOWN=0 y OUTSIDE_TOPO_COVERAGE=0; hash SHA-256 `66b54da3243a37644bd581e096149ca1738e05542d9968aa6fa3679e16866d30`.

Comando de generación ejecutado desde la raíz:

```powershell
& 'C:\Proyecto_Plan\.venv\Scripts\python.exe' -m src.m01.topography
```

Retorno 0; salida confirmó 73.309 puntos en dominio, 870 vértices, 41.412 bloques y todos los estados. Reejecución produjo los mismos hashes. Los 35 collars tienen estimación de superficie válida; residuo `z_collar-z_surface`: min −1.365264 m, max +1.118721 m, mediana absoluta 0.308264 m. Esta comparación reutiliza los datos del control anterior y no representa una validación independiente/holdout.

Pruebas: `& 'C:\Proyecto_Plan\.venv\Scripts\python.exe' -m unittest tests.m01.test_topography -v` — 10 PASS, exit code 0; suite completa `& 'C:\Proyecto_Plan\.venv\Scripts\python.exe' -m unittest discover -s tests -v` — 64 PASS, exit code 0. Se probaron coincidencia exacta, IDW/rango/repetibilidad, plano horizontal y plano inclinado, ROCK/AIR/PARTIAL con igualdad de techo/base, umbral inclusive, fuera de dominio, UNKNOWN, prioridad, salidas reales y archivos reproducibles.

Este resultado solo verifica la computación. La regla de cuatro vértices puede no captar extrema curvatura interior; PARTIAL no es fracción ni volumen neto de roca. Umbral 20 m, IDW8/potencia 2 no tienen validación externa. Se requiere interpretar los resultados y ejecutar revisión minera/holdout en P5 antes de llamarlo validado. No se modificaron `data/raw/`, `m01b_block_grid.csv`, `main.py` o gobernanza; no se instalaron dependencias ni hubo commit/push. P4 y P6 no están autorizados.

## 13. Uso del agente de IA

- [x] Explicación conceptual y evaluación formativa.
- [x] Auditoría de lectura de datos y repositorio.
- [x] Documentación de evidencia y decisiones con autorización.
- [x] Ejecución de pruebas M01 con el entorno virtual existente (40 PASS).
- [x] Implementación de compositing bajo gate aprobado.
- [x] Pruebas M01B (7 específicas) y suite completa (47 PASS).
- [x] Interpretación formativa del estudiante sobre consistencia de composites y limitaciones.
- [x] Implementación visual P6 bajo gate aprobado (7 pruebas específicas, HTML autónomo).
- [ ] Revisión visual humana del HTML y revisión geológica independiente de los bloques.
- [ ] Validación geológica de composites o bloques.

## 14. Estado

**IMP-002 permanece `IN_PROGRESS`.** Compositing, grid, clasificación topográfica preliminar, asignación P4, holdout P5 y visualización P6 están implementados y probados. La revisión visual humana y geológica independiente siguen pendientes; no hay modelo de bloques validado.

## 18. Implementación P4_GEO_ASSIGN — 2026-10-24

El estudiante aprobó el gate P4_GEO_ASSIGN para asignar solo bloques `ROCK`, comparando radios de 20 y 30 m como escenarios de sensibilidad. La respuesta literal, su dato real, ventaja y limitación están registrados en `docs/exam/T2_M01B_PLAN_G04.md`. Esta implementación categórica no demuestra continuidad ni valida ninguno de los radios.

`src/m01/geological_assignment.py` toma `m01b_block_grid.csv`, `m01b_block_topography.csv` y `m01b_composites.csv`. Calcula distancia euclidiana 3D desde centro a punto medio y aplica `distance <= radio`; exige concordancia entre códigos. Reporta conteos por composite, `sample_id` único y `hole_id`, distancia mínima y registros de cada composite con su distancia. El único composite `AIR` (`CR-C02-002_0001`) se excluye y documenta como excluido. El cálculo usa numpy por chunks de 256 bloques ROCK y evalúa ambos umbrales usando cada matriz de distancias por chunk una sola vez; no instala ni utiliza SciPy.

Salida generada: `data/processed/m01b_block_assignment.csv`, 82.824 filas, una por bloque y escenario. Radio 20 m: ASSIGNED REG=0, DIO=1.011, POR=1.517, BRX=113; UNKNOWN INSUFFICIENT_SUPPORT=22.730 y CONFLICTING_CODES=361; NOT_APPLICABLE=13.770; UNASSIGNED/PARTIAL_TOPO=1.910; total=41.412. Radio 30 m: ASSIGNED REG=4, DIO=1.953, POR=2.896, BRX=131; UNKNOWN INSUFFICIENT_SUPPORT=19.562 y CONFLICTING_CODES=1.186; NOT_APPLICABLE=13.770; UNASSIGNED/PARTIAL_TOPO=1.910; total=41.412.

Comando exacto ejecutado desde la raíz: `& 'C:\Proyecto_Plan\.venv\Scripts\python.exe' -m src.m01.geological_assignment`; exit code 0 y tiempo 12.527 s. Pruebas específicas: 11 PASS, exit code 0. Suite completa: `& 'C:\Proyecto_Plan\.venv\Scripts\python.exe' -m unittest discover -s tests -v` — 75 PASS, exit code 0. Validaciones de salida: no hay lith_code en bloques no ROCK; `CR-C02-002_0001` no está en soportes; distribuciones suman 41.412 por radio. No se modificaron datos fuente, grid, salidas P3, `main.py` o gobernanza, ni hubo instalación, commit o push. P5 y P6 no están autorizados y no se declara `MINING_VALIDATED`.

El estudiante interpretó la diferencia de cobertura/conflicto y decidió conservar ambos radios sin preferir uno antes de P5. Conteos, porcentajes y el aumento de conflictos fueron revisados contra el CSV; se señaló que la escasez de `REG` asignado no se atribuye solo a `PARTIAL_TOPO`, porque REG aparece como soporte en bloques ROCK conflictivos. Esta interpretación no constituye validación minera; P5 comienza como revisión/planificación y P6 sigue no autorizado.

## 19. Implementación P5_VALIDATION — 2026-10-24

El gate P5_VALIDATION fue aprobado para un holdout leave-one-hole-out sobre los 35 sondajes, manteniendo radios de 20 y 30 m. La aprobación literal, los datos/justificación del estudiante y la evaluación están registrados en PLAN y EVIDENCE. Por cada pliegue se excluyen todos los composites del sondaje retenido; para formar referencias se usan bloques ROCK con un código observado único. Ambigüedades por par `(hole_id, block_id)` se reportan por separado. Los composites AIR se excluyen del soporte.

`src/m01/validation.py` reutiliza `build_geological_assignment` de `src/m01/geological_assignment.py`; no duplica la regla P4. Los puntos medios de composites se mapean a bloques de la malla. Cobertura = asignados/referencias elegibles; concordancia = concordantes/asignados. Las métricas por litología están en `outputs/tables/m01b_holdout_by_hole.csv`; los diagnósticos por severidad están en `outputs/tables/m01b_validation_diagnostics.csv`.

**Control de diagnósticos previo a documentar:** 0 ERROR, 14 WARNING y 8 INFO. Al no existir ERROR, se generaron y conservaron ambos CSV; los avisos señalan soporte limitado (incluidos `n_holes=1`), referencias ambiguas y exclusiones topográficas. No se transformaron en criterio de validación geológica.

| Radio | Litología | Elegibles | Asignados | Concordantes | UNKNOWN insuficiente | UNKNOWN conflicto | Ambiguos por código | Cobertura | Concordancia |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 20 m | Total | 1,049 | 120 | 112 | 902 | 27 | 37 únicas | 11.439% | 93.333% |
| 20 m | REG | 0 | 0 | 0 | 0 | 0 | 3 | N/A | N/A |
| 20 m | DIO | 395 | 45 | 44 | 347 | 3 | 21 | 11.392% | 97.778% |
| 20 m | POR | 569 | 40 | 36 | 521 | 8 | 35 | 7.030% | 90.000% |
| 20 m | BRX | 85 | 35 | 32 | 34 | 16 | 15 | 41.176% | 91.429% |
| 30 m | Total | 1,049 | 219 | 198 | 740 | 90 | 37 únicas | 20.877% | 90.411% |
| 30 m | REG | 0 | 0 | 0 | 0 | 0 | 3 | N/A | N/A |
| 30 m | DIO | 395 | 97 | 94 | 288 | 10 | 21 | 24.557% | 96.907% |
| 30 m | POR | 569 | 106 | 95 | 428 | 35 | 35 | 18.629% | 89.623% |
| 30 m | BRX | 85 | 16 | 9 | 24 | 45 | 15 | 18.824% | 56.250% |

Las ambigüedades por código pueden solaparse; 37 es el total de referencias ambiguas únicas y no la suma de la columna por litología. REG tiene cero referencias elegibles, así que sus métricas son N/A y no permiten inferir ausencia geológica. Con 30 m aumenta la cobertura total, mientras baja la concordancia condicional; los resultados, en particular por litología con pocos casos, requieren interpretación y revisión minera. No se elige radio.

**Comandos ejecutados desde la raíz** `C:\Proyecto_Plan\PlanMinUPN-G04` con el intérprete existente:

```powershell
& 'C:\Proyecto_Plan\.venv\Scripts\python.exe' -m unittest tests.m01.test_validation -v
& 'C:\Proyecto_Plan\.venv\Scripts\python.exe' -m src.m01.validation
& 'C:\Proyecto_Plan\.venv\Scripts\python.exe' -m unittest discover -s tests -v
```

Pruebas específicas: 6 PASS, exit code 0 (6.755 s). Generación: exit code 0 (4.574 s). Suite completa: 81 PASS, exit code 0; duración medida externamente 53.594 s (unittest reportó 51.306 s). Hashes de las salidas: holdout `A65DC0EF3E7EA8CE1DAB8008D8496EBC0F5BFE33654E3CBD13550C0E0F774E2F`; diagnósticos `17137DCFFD1EEF4367EE77D84A87BD8ECBA0B0527ABA0F42C2F0CD015DC8A46B`.

P5 verifica computacionalmente la regla por validación cruzada interna, no valida la continuidad de dominios ni reemplaza la revisión geológica. `MINING_VALIDATED` y `READY_FOR_REVIEW` no se declaran; la interpretación del estudiante está registrada y una revisión geológica independiente sigue sin establecerse. En el momento de redactar este párrafo, el gate P6 aún estaba pendiente; la aprobación e implementación se documentan en la actualización posterior. Se respetaron las restricciones: no se modificaron datos fuente, grid, salidas P3/P4, `main.py` o gobernanza; no hubo instalaciones, commit ni push.

### Interpretación P5 y gate visual (2026-10-24)

En la evaluación inicial, antes de la aclaración posterior, se registró **PARCIAL — H1** por falta de ámbito para los conteos de contactos. La aclaración del estudiante y el recálculo de los 57 ensayes que cruzan contactos reconciliaron los conteos; la evaluación actualizada CORRECTA — H0 y sus evidencias constan en la sección siguiente.

El gate P6_VISUALIZER se propuso, pero está **pendiente de aprobación**. No se ha autorizado código/HTML P6, selección de radios, ni cambios a los datos. La propuesta conserva ambos radios, utiliza Plotly existente y requiere filtros/cortes con conteos visibles/ocultos, estados distinguibles y controles de prueba; no equivale a validación minera ni a cierre de IMP-002.

### Actualización — aclaración de P5 e implementación P6 (2026-10-24)

La aclaración del estudiante define 5 contactos POR→BRX y 2 BRX→POR como los que ocurren dentro de los 57 ensayes que cruzan contactos, no como conteos del archivo completo. La verificación de `assay.csv` y `lithology.csv` confirma 57 cruces y esos conteos direccionales; el conjunto completo conserva 11 y 5, respectivamente. El estudiante acepta la distinción y mantiene el cuerpo angosto como hipótesis. La interpretación P5 se actualiza a CORRECTA — H0 para conservar ambos radios; no se infiere causalidad ni validez minera.

El estudiante aprobó el gate P6_VISUALIZER. Implementación: `src/m01/block_visualizer.py`, `tests/m01/test_block_visualizer.py` y `outputs/figures/m01b_block_model_3d.html`. La respuesta literal y los detalles de alcance están en PLAN/EVIDENCE.

La salida es HTML autocontenido Plotly de 18,325,116 bytes (SHA-256 `C18082B5B1690509489B4AAFE0AEA90A60D5B84B6F245F643F510870806E796C`), ejecutado con `& 'C:\Proyecto_Plan\.venv\Scripts\python.exe' -m src.m01.block_visualizer` desde la raíz; exit code 0, 6.516 s. Inicialmente representa solo los 2,641 bloques ASSIGNED del escenario de 20 m, con topografía basada en 870 vértices y las 270 estaciones de trayectoria; no renderiza los 41,412 cuboides de una vez. Los controles permiten radios, estado/causa/código, cortes i/j/k y capas; leyenda diferencia códigos ASSIGNED, UNKNOWN por causa, AIR y PARTIAL, sin color por Cu.

Pruebas específicas: 7 PASS, exit code 0. Suite completa posterior: 88 tests PASS, exit code 0; 53.968 s externos y 51.572 s según unittest. Se verificaron los filtros, geometría de cuboides, consistencia de categorías, superficie sin extrapolación, título/unidades y HTML autocontenido/reproducible. La inspección visual reportada por el estudiante y su interpretación CORRECTA — H0 quedan registradas en PLAN/EVIDENCE; se observan patrones de proximidad, no continuidad geológica. El estudiante autorizó commit/push limitado a archivos P2–P6 y documentación, sin ejecutar `git add`, con suite completa antes del commit y push solo a la rama feature. La grilla P2 vigente de 51 capas tiene secciones `i=1,479`, `j=1,428`, `k=812`; la mención de 1,344 corresponde a una grilla previa. Se mantienen ambas alternativas de radio y no se declara `MINING_VALIDATED` ni `READY_FOR_REVIEW`. Sin instalaciones, merge o push a main.
### Correccion del whitespace del HTML P6 (precommit)

El chequeo del indice detecto trailing whitespace en el HTML autocontenido. El generador ahora elimina whitespace al final de cada linea, sin alterar la escena ni el contenido funcional. Regenerado con `& 'C:\Proyecto_Plan\.venv\Scripts\python.exe' -m src.m01.block_visualizer`: exit code 0, 7.043 s; 18,325,093 bytes; SHA-256 `908365C3F39541E34047DBC90896D635111B2C99698DD731602A5D09AA39D95D`. Pruebas especificas: 7 PASS, exit code 0. Suite completa: `& 'C:\Proyecto_Plan\.venv\Scripts\python.exe' -m unittest discover -s tests -v`, 88 PASS, exit code 0, 56.652 s externos (54.329 s unittest). Confirmacion del indice y publicacion siguen pendientes.
