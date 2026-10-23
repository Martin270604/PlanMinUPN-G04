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
- **B09: RECOVERY_BLOCKED**; no se encontró fuente topográfica local; no se puede validar la clasificación aire/roca.
- **B10: VERIFIED**; 7 pruebas específicas y 47 pruebas totales PASS en `.venv`, con comandos y resultado de generación trazables.
- El estado de base completo no está verificado. No se inicia `EVALUATION_PLAN` hasta resolver los requisitos críticos o declarar bloqueos conforme al protocolo.
- `BASE_VERIFIED` no se aprueba porque B09 es crítico y `RECOVERY_BLOCKED`; B05 permanece PARTIAL por ausencia de historia previa M01B. Mientras persistan bloqueos críticos, continuar solo con planificación conceptual. No instalar dependencias, editar otras fuentes, hacer commit o push sin autorización separada.
- **Modo posterior a la interpretación:** EVALUATION_PLAN conceptual (P0 solamente) bajo RECOVERY_BLOCKED, a elección del estudiante y conforme al escenario; no significa que BASE_VERIFIED se haya aprobado.
- **Continuación conceptual:** el estudiante eligió ordenar P1 primero; comparar alternativas de geometría P2 solo conceptualmente con XYZ y límites superiores provisionales/`TOPO_UNKNOWN`; consultar al docente y no clasificar AIR/ROCK antes de P3. Evidencia espacial y limitaciones constan en `docs/exam/T2_M01B_EVIDENCE_G04.md`. BASE_VERIFIED continúa No y no se autoriza generación de malla.
- **P1 conceptual:** se mantiene cada `lith_code` como categoría observada independiente, sin semántica geológica inventada; `AIR` queda marcado para revisión. La evaluación y conteos se registran en `docs/exam/T2_M01B_PLAN_G04.md` y `docs/exam/T2_M01B_EVIDENCE_G04.md`. La siguiente decisión pendiente es el tratamiento conceptual de `AIR`; no se crea ni remapea ningún dato.

## 13. Uso del agente de IA

- [x] Explicación conceptual y evaluación formativa.
- [x] Auditoría de lectura de datos y repositorio.
- [x] Documentación de evidencia y decisiones con autorización.
- [x] Ejecución de pruebas M01 con el entorno virtual existente (40 PASS).
- [x] Implementación de compositing bajo gate aprobado.
- [x] Pruebas M01B (7 específicas) y suite completa (47 PASS).
- [x] Interpretación formativa del estudiante sobre consistencia de composites y limitaciones.
- [ ] Validación geológica de composites o bloques.

## 14. Estado

**IMP-002 permanece `IN_PROGRESS`.** El compositing está implementado, probado y generado; su etapa aún no se declara validada hasta recibir la interpretación del estudiante. No hay modelo de bloques terminado o validado.
