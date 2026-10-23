# T2 M01B — Evidencia G04

## Alcance y modo

- **Protocolo:** EXAM_T2_M01B v1.0.
- **Modo al crear este registro:** ALIGNMENT_RECOVERY; estado de sesión posterior actualizado a EVALUATION_PLAN conceptual (P0 solamente) bajo RECOVERY_BLOCKED.
- **BASE_VERIFIED:** No.
- Solo lectura para inspección de código/datos; esta autorización posterior creó tres documentos de trazabilidad. No se implementó código, no se instalaron dependencias, no se modificó `data/raw/` ni la plantilla de IMP, y no se hizo commit ni push.

## Fuentes leídas realmente

- Gobernanza: `AGENTS.md`, `.aiassistant/rules/00_course_governance.md`, `.github/copilot-instructions.md`, `.github/CODEOWNERS`, `.github/pull_request_template.md`, `docs/templates/MODULE_IMPLEMENTATION_TEMPLATE.md`.
- Examen: `docs/exam/T2_M01B/01_AGENT_EXAM_M01B.md`, `docs/exam/T2_M01B/02_SCENARIO_EXAM_M01B.md`.
- Documentación del proyecto: `docs/PROJECT.md`, `docs/STATUS.md`, `docs/DATA.md`, `docs/implementation/IMP-001_m01_validate_desurvey.md`, `README.md`.
- Código M01 inspeccionado: `main.py`, `src/m01/loader.py`, `validator.py`, `validation_report.py`, `desurvey.py`, `positioning.py`, `visualizer.py`, `validation_plots.py`.
- Pruebas M01 inspeccionadas: `tests/m01/test_desurvey.py`, `test_positioning.py`, `test_visualizer.py`, `test_m01_data_contract.py`, `test_m01_validation_rules.py`, `test_validation_plots.py`.
- Datos/salidas inspeccionados: fuentes en `data/raw/`, derivados `data/processed/assay_xyz.csv`, `density_xyz.csv`, `drillhole_trajectory.csv`, `lithology_xyz.csv`; reportes y figuras bajo `outputs/`, incluido `outputs/figures/m01_exploration_3d.html`.
- No se encontró `docs/implementation/IMP-002*` antes de crear este registro. No se encontró archivo de topografía local por nombre de archivo/candidato.

## Evidencia de Git

Comprobación local realizada durante el diagnóstico:

```text
git status -sb
## feature/t2-m01b-block-model
?? docs/exam/

git rev-parse --short HEAD
b22c297
```

La consulta de estado detallada indicó dos elementos sin seguimiento bajo `docs/exam/`, ninguno staged/modified y ningún conflicto. No se alteraron ni limpiaron.

**Salida de terminal proporcionada literalmente por el estudiante; no ejecutada independientemente por el agente:**

```text
git fetch origin
git branch -r
  origin/HEAD -> origin/main
  origin/feature/m01-architecture
  origin/main
```

El estudiante la interpreta como evidencia de que el remoto tiene solo `main` y `feature/m01-architecture`, sin ramas M01B. Se conserva como evidencia aportada, no como consulta remota independiente de esta sesión.

## Evidencia de datos de origen

### Assay, residuos y contactos

Operaciones PowerShell de solo lectura ejecutadas sobre `data/raw/assay.csv`, `lithology.csv` y `collar.csv`, con `Import-Csv`; longitudes calculadas como `to_m - from_m`. Contactos contados por sondaje al ordenar intervalos litológicos por `from_m`/`to_m` y comprobar que `to_m` del intervalo precedente coincide con `from_m` del siguiente. Se usó tolerancia numérica de `1e-8` para comparaciones geométricas.

Resultados reales:

```text
assay_total=5275
assay_exact_2m=5245
assay_residual_lt_2m=30
assay_other_not_2m=0
lith_total=117
contacts_contiguous_adjacent=82
assay_2m_crossing_internal_lith_contact=57
```

Todos los 30 intervalos menores de 2 m son residuos terminales: uno por cada uno de 30 sondajes, último intervalo del sondaje, y su `to_m` coincide con `collar.final_depth_m`; la comprobación reportó cero excepciones. Sus longitudes van de **0,050936 a 1,984641 m** y 11 son menores de 0,5 m.

### División geométrica por contactos

Se contrastaron los 57 intervalos assay de exactamente 2 m con límites contiguos de litología en el mismo sondaje. Cada contacto cae en el punto medio del ensayo:

```text
crossing_rows=57
distinct_holes=35
all_holes_1m_plus_1m=True
unexpected_split_count=0
split_length_distribution=1.000000+1.000000:57
crossing_fraction_percent=1.081
```

Los 114 segmentos 1 m + 1 m son una consecuencia geométrica propuesta; **no se generaron en archivos ni son ensayes analíticos independientes**. Cada mitad heredaría una ley medida en el intervalo original de 2 m, supuesto reconocido por el estudiante.

### Transiciones dirigidas de litología

Los códigos se tomaron de los intervalos litológicos adyacentes en orden de profundidad, sin inferir su semántica:

```text
REG->DIO:31
DIO->POR:10
REG->POR:8
POR->BRX:5
BRX->POR:2
DIO->REG:1
crossings_count=57
unique_samples=57
```

Los conteos suman los 57 cruces. `data/raw/data_dictionary.csv` describe el campo `lith_code` como código categórico, pero no asigna una interpretación geológica a REG/DIO/POR/BRX. El único contacto DIO→REG queda como observación a revisar, no como error verificado.

### Litología y Cu de residuos terminales

La litología se comprobó mediante solape de cada residuo con intervalos litológicos del mismo `hole_id`; la suma de solapes coincide con la longitud de cada residuo:

```text
residuals=30
length_range_m=0.050936..1.984641
length_lt_0_5m=11
lith_code_counts=BRX:6, DIO:2, POR:22
dominant_lithology_por_or_brx=28
assay_cu_mean_unweighted_pct=0.442266
assay_cu_mean_length_weighted_pct=0.393821
cu_gt_0_3_pct_count=20
unmatched_or_partial_lith_coverage=0
```

El promedio no ponderado da el mismo peso a cada muestra; el promedio ponderado por longitud usa la longitud de cada residuo. No se verificó ni adoptó un cut-off; por tanto, el recuento `Cu > 0,3 %` no valida por sí mismo una “zona mineralizada”.

### Integridad del release

Los ocho hashes SHA-256 de archivos del manifest fueron comparados con `Get-FileHash`; todos coincidieron:

```text
README.md hash_match=True
alteration.csv hash_match=True
assay.csv hash_match=True
collar.csv hash_match=True
data_dictionary.csv hash_match=True
density.csv hash_match=True
lithology.csv hash_match=True
survey.csv hash_match=True
```

Manifest: dataset `DS04`, release `EXP03`, `synthetic_data=true`, 35 holes, 270 surveys, 5.275 assays, 117 intervalos litológicos, 425 muestras de densidad y cero intervalos de alteración.

## Código, derivados, pruebas y topografía

- **Arquitectura:** `main.py` coordina M01; capacidades modulares bajo `src/m01/`; pruebas bajo `tests/m01/`.
- **Derivados M01 presentes:** 5.275 filas assay XYZ, 117 lithology XYZ, 425 density XYZ y 270 estaciones de trayectoria; encabezados/filas contados directamente en `data/processed/`.
- **Visualización:** `outputs/figures/m01_exploration_3d.html` existe (5.720.873 bytes al inspeccionarse); el código declara sistema cartesiano local sin CRS/EPSG y topografía no disponible. Es visualización exploratoria M01, no visualizador de bloques.
- **Pruebas M01:** `IMP-001` registra históricamente 36 pruebas PASS en Etapa 7, 39 en Etapa 8 y 40 en Etapa 9, además de ejecuciones de `python main.py`. El 2026-10-23 se ejecutó el comando de pruebas autorizado que se detalla abajo; no se ejecutó `main.py`.
- **Compositing:** no se encontró módulo, prueba ni CSV de composites; no se generó ni probó ninguno.
- **Topografía:** no se encontró superficie local; `IMP-001` indica que el release no contiene topografía. B09 permanece BLOCKED.

### Ejecución actual autorizada de pruebas

Comando exacto, ejecutado desde `C:\Proyecto_Plan\PlanMinUPN-G04`:

```text
python -m unittest discover -s tests -v
```

Python invocado por el comando: `C:\Users\jorge\AppData\Local\Programs\Python\Python312\python.exe`.

Extracto literal de la salida real:

```text
Ran 38 tests in 1.242s

FAILED (errors=2)
ModuleNotFoundError: No module named 'matplotlib'
ModuleNotFoundError: No module named 'plotly'
EXIT_CODE=1
```

Interpretación de la salida: 36 tests individuales terminaron en `ok`; dos módulos no pudieron importarse (`m01.test_validation_plots` requiere `matplotlib` y `m01.test_visualizer` requiere `plotly`). El proceso terminó con exit code **1**. No se instalaron dependencias ni se ejecutó `main.py`; no se generaron salidas mediante esta ejecución. Este resultado acredita pruebas actuales parciales de M01, no pruebas M01B.

La evidencia histórica de IMP-001 se distingue por etapa: Etapa 7 registra 36 pruebas PASS, Etapa 8 registra 39 y Etapa 9 registra 40 pruebas PASS. La ejecución actual con 36 `ok` y dos errores de importación no sustituye ni invalida retrospectivamente esos resultados históricos.

### Entorno virtual del proyecto

El estudiante informó que el fallo anterior se debió a ejecutar con Python del sistema, no con su `.venv`, donde `requirements.txt` declara `plotly` y `matplotlib`. El entorno Python detectado por PyCharm para `main.py` es Python 3.12.10 en `C:\Proyecto_Plan\.venv\Scripts\python.exe`. Una primera invocación de `.\.venv\Scripts\python.exe` desde la carpeta del repositorio no encontró ese ejecutable porque el entorno está en la raíz `C:\Proyecto_Plan\.venv`; después se usó la ruta absoluta correcta.

El estudiante declaró haber ejecutado en su terminal, con `.venv` activo:

```text
python -m unittest discover -s tests -v
```

Sin embargo, en su mensaje el campo de salida aparece como texto de ejemplo (`[pega aquí las últimas líneas, por ejemplo ...]`), no como una transcripción real. Por fidelidad, no se registra el resultado de su terminal como salida literal confirmada.

Ejecución independiente actual con el intérprete `.venv`, desde `C:\Proyecto_Plan\PlanMinUPN-G04`:

```text
C:\Proyecto_Plan\.venv\Scripts\python.exe -m unittest discover -s tests -v
Ran 40 tests in 2.916s
OK
EXIT_CODE=0
```

Esta ejecución actual tuvo 40 tests PASS y exit code 0. No se ejecutó `main.py`, no se instalaron dependencias y no se modificaron código ni datos. Los tests `test_validation_plots`/`test_visualizer` escriben archivos solo dentro de directorios temporales de prueba. Este suite contiene pruebas M01 existentes; no hay pruebas M01B.

## Auditoría de cobertura B06 — subconjunto elegido por el estudiante

Comprobación de solo lectura sobre `data/raw/assay.csv`, `lithology.csv` y `collar.csv`. Por cada sondaje, se ordenaron intervalos por `from_m`/`to_m`; se verificó inicio en 0 m, final igual a `collar.final_depth_m`, suma de longitudes igual a profundidad final y ausencia de gaps/overlaps, con tolerancia numérica `1e-8`. Se comprobó nulidad de `hole_id`, `from_m`, `to_m` y duplicidad de claves `hole_id/from_m` y `hole_id/from_m/to_m`.

```text
assay holes=35 rows=5275 bad_coverage_holes=0 total_interval_length=10518.328249553
assay null_hole_from_to_rows=0 duplicate_hole_from_groups=0 duplicate_hole_from_to_groups=0
lithology holes=35 rows=117 bad_coverage_holes=0 total_interval_length=10518.328249553
lithology null_hole_from_to_rows=0 duplicate_hole_from_groups=0 duplicate_hole_from_to_groups=0
```

En los ensayes:

```text
cu_pct null_or_non_numeric=0 negative=0 zero=1
mo_pct null_or_non_numeric=0 negative=0 zero=5275
au_gt null_or_non_numeric=0 negative=0 zero=5275
```

El reporte existente `outputs/tables/m01_validation_summary.csv` clasifica `ASSAY_GRADE_NONNEGATIVE` como ERROR con 0 hallazgos e `ASSAY_GRADE_ZERO` como INFO con 10.551 hallazgos. La comprobación de `m01_validation_findings.csv` confirma 1 INFO de Cu cero, 5.275 INFO de Mo cero y 5.275 INFO de Au cero. No se infiere significado económico, límite de detección ni significado litológico de estos ceros/códigos.

**Alcance:** se comprobaron los elementos de auditoría de intervalos previstos en B06: cobertura y longitudes por sondaje, gaps/overlaps, contactos, nulos/duplicados, unidades/campos documentados y resultados analíticos negativos/cero con severidades del reporte. B06 queda **VERIFIED** para esta auditoría de datos. No se auditó QA/QC analítico ni se interpretó la semántica geológica de códigos; no hay soporte en el release para esas tareas y no se declaran como parte verificada.

## Verificación de anclaje y paridad de contactos — B07

Lectura de `data/raw/assay.csv` y `data/raw/lithology.csv` con un script inline de Python (biblioteca estándar `csv`), sin escrituras. Se comprobaron los 5.275 `from_m` mediante tolerancia numérica `1e-8` para múltiplos de 2. Para contactos, se ordenaron los intervalos litológicos por `hole_id` y `from_m`; se contó el inicio del intervalo siguiente cuando cambiaba `lith_code`.

Comando ejecutado desde PowerShell:

```powershell
@'
import csv
from pathlib import Path
root = Path(r'C:\Proyecto_Plan\PlanMinUPN-G04\data\raw')
with (root / 'assay.csv').open(newline='', encoding='utf-8-sig') as f:
    assays = list(csv.DictReader(f))
from_values = [float(r['from_m']) for r in assays]
not_even = [v for v in from_values if abs(v / 2 - round(v / 2)) > 1e-8]
with (root / 'lithology.csv').open(newline='', encoding='utf-8-sig') as f:
    lith = list(csv.DictReader(f))
groups = {}
for r in lith:
    groups.setdefault(r['hole_id'], []).append(r)
contacts = []
for hole, rows in groups.items():
    rows.sort(key=lambda r: float(r['from_m']))
    for prev, curr in zip(rows, rows[1:]):
        if prev['lith_code'] != curr['lith_code']:
            contacts.append((hole, float(curr['from_m']), prev['lith_code'], curr['lith_code']))
even = [c for c in contacts if abs(c[1] / 2 - round(c[1] / 2)) <= 1e-8]
odd = [c for c in contacts if abs(c[1] - round(c[1])) <= 1e-8 and int(round(c[1])) % 2 == 1]
other = [c for c in contacts if c not in even and c not in odd]
print(f'assay_rows={len(assays)} from_m_not_multiple_of_2={len(not_even)}')
print(f'assay_from_m_unique={len(set(from_values))} first_values={sorted(set(from_values))[:8]}')
print(f'internal_contacts={len(contacts)} even_meter={len(even)} odd_meter={len(odd)} other_noninteger={len(other)}')
print('contact_depth_examples_even=', sorted(set(c[1] for c in even))[:10])
print('contact_depth_examples_odd=', sorted(set(c[1] for c in odd))[:10])
'@ | python -
```

```text
assay_rows=5275 from_m_not_multiple_of_2=0
assay_from_m_unique=218 first_values=[0.0, 2.0, 4.0, 6.0, 8.0, 10.0, 12.0, 14.0]
internal_contacts=82 even_meter=25 odd_meter=57 other_noninteger=0
contact_depth_examples_even= [2.0, 8.0, 10.0, 16.0, 38.0, 42.0, 50.0, 70.0, 122.0, 156.0]
contact_depth_examples_odd= [5.0, 7.0, 9.0, 11.0, 13.0, 15.0, 17.0, 19.0, 51.0, 75.0]
```

La evidencia respalda el alineamiento de `from_m` assay a la grilla anclada en 0 m y la división geométrica en contactos internos impares. Es una verificación de intervalos, no una construcción de composites ni una prueba de agregación ponderada.

## Verificación de múltiples ensayes por bin/litología — B07

Se realizó una intersección de solo lectura de intervalos assay y lithology por sondaje, recortando cada intersección a bins de 2 m anclados en 0 m. Se agruparon aportes por sondaje, bin y `lith_code`, contando IDs/filas assay y filas de litología de origen. No se generó archivo de composites.

Comando ejecutado desde PowerShell:

```powershell
@'
import csv
from collections import defaultdict
from pathlib import Path
root = Path(r'C:\Proyecto_Plan\PlanMinUPN-G04\data\raw')
def read(name):
    with (root / name).open(newline='', encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))
assays, lith = read('assay.csv'), read('lithology.csv')
by_hole_a, by_hole_l = defaultdict(list), defaultdict(list)
for i, r in enumerate(assays):
    by_hole_a[r['hole_id']].append((i, float(r['from_m']), float(r['to_m']), r['sample_id']))
for i, r in enumerate(lith):
    by_hole_l[r['hole_id']].append((i, float(r['from_m']), float(r['to_m']), r['lith_code']))
contributors = defaultdict(lambda: {'assays': set(), 'lith_rows': set(), 'length': 0.0})
for hole, arows in by_hole_a.items():
    for ai, af, at, sample in arows:
        for li, lf, lt, code in by_hole_l[hole]:
            start, end = max(af, lf), min(at, lt)
            if end <= start:
                continue
            pos = start
            while pos < end - 1e-10:
                bin_idx = int(pos // 2)
                stop = min(end, (bin_idx + 1) * 2.0)
                key = (hole, bin_idx, code)
                contributors[key]['assays'].add((ai, sample))
                contributors[key]['lith_rows'].add(li)
                contributors[key]['length'] += stop - pos
                pos = stop
assay_multi = [(k,v) for k,v in contributors.items() if len(v['assays']) > 1]
lith_multi = [(k,v) for k,v in contributors.items() if len(v['lith_rows']) > 1]
all_bins = {(k[0], k[1]) for k in contributors}
print(f'assay_rows={len(assays)} lithology_rows={len(lith)} hole_bins_with_lith_contribution={len(all_bins)}')
print(f'hole_bin_lith_groups={len(contributors)} groups_with_multiple_assay_intervals_same_lith={len(assay_multi)}')
print(f'groups_with_multiple_lithology_rows_same_code={len(lith_multi)}')
print(f'groups_with_multiple_assay_intervals_and_same_lith_rows={sum(1 for k,v in assay_multi if len(v["lith_rows"]) > 1)}')
print('sample_multi_assay_groups=', assay_multi[:5])
'@ | python -
```

Salida real:

```text
assay_rows=5275 lithology_rows=117 hole_bins_with_lith_contribution=5275
hole_bin_lith_groups=5332 groups_with_multiple_assay_intervals_same_lith=0
groups_with_multiple_lithology_rows_same_code=0
groups_with_multiple_assay_intervals_and_same_lith_rows=0
sample_multi_assay_groups= []
```

Por lo tanto, no se encontró ningún bin de 2 m que contenga más de un intervalo assay de la misma litología; tampoco se encontró un grupo con varias filas lithology del mismo código. Los bins en contactos impares aportan segmentos de litologías distintas, no varios ensayes distintos de la misma litología. Esto permite especificar la regla conceptual del grupo sin ambigüedad para el dataset actual:

- Intersectar assay y lithology por `hole_id` y profundidad.
- Usar bins nominales de 2 m anclados en MD 0 m, y no permitir que una fila composite atraviese un contacto.
- Para segmentos con soporte assay heredado, usar la ley medida original; la división geométrica en contacto no crea una nueva medición.
- Calcular una ley ponderada como `sum(ley * longitud aportada) / sum(longitud aportada)` si un bin/litología recibe varios aportes.
- Registrar longitud cubierta; marcar como parcial toda fila con longitud menor de 2 m; no imputar ley cero al tramo faltante.
- Conservar residuos terminales con su longitud real.

La regla quedó **VERIFIED en B07 como decisión documentada** antes de autorizar B08. En ese momento no existía la salida; la ejecución autorizada posterior generó y comprobó las 144 filas parciales esperadas.

## Matriz B00–B10

| ID | Estado | Evidencia / límite |
|---|---|---|
| B00 | VERIFIED | Rama/HEAD/estado local y arquitectura inspeccionados |
| B01 | VERIFIED | Fuentes, manifest, diccionario y ocho hashes coincidentes |
| B02 | VERIFIED | Loader/validator; suite M01 actual con `.venv`: 40 PASS, exit code 0 |
| B03 | VERIFIED | Derivados de trayectoria y XYZ presentes; límites de interpolación anotados en IMP-001 |
| B04 | VERIFIED | Visualizador/HTML M01 presentes; no equivale al modelo de bloques |
| B05 | PARTIAL | IMP-002 registra baseline actual y evidencia M01B; no existía baseline histórico previo |
| B06 | VERIFIED | Auditoría de intervalos assay/lithology, contactos, cobertura, longitudes, nulos/duplicados y reglas Cu/Mo/Au contrastadas con reportes; QA/QC/semántica de códigos no afirmadas |
| B07 | VERIFIED | Regla reproducible del grupo documentada: grilla de 2 m desde collar, segmentación en contactos, agregación ponderada por longitud y registro de parciales; no implementada |
| B08 | VERIFIED (computacional) | Implementación, 7 pruebas específicas, CSV y métricas de integridad confirmados; no equivale a validación geológica |
| B09 | RECOVERY_BLOCKED | No se encontró fuente topográfica local; clasificación aire/roca no verificable |
| B10 | VERIFIED | Suite completa `.venv`: 47 PASS (40 M01 + 7 B08), exit code 0; comando/generación/resultados trazables |

## Evaluaciones conversacionales y ayuda

Las respuestas literales y alternativas elegidas se conservan en `docs/exam/T2_M01B_PLAN_G04.md`. Evaluaciones registradas durante esta conversación:

- Priorizar auditoría B06–B08: **CORRECTA, H0**.
- Dividir ensayes que cruzan contacto: **CORRECTA, H0**; la longitud fue verificada después.
- Conservar residuos cortos con su longitud: **CORRECTA, H0**, con distinción entre promedio Cu no ponderado y ponderado.
- Recuento inicial de transiciones: el agente lo calificó **PARCIAL, H0** al señalar que faltaba DIO→REG.
- Recuento corregido con seis transiciones dirigidas: **CORRECTA, H2**; la secuencia PARCIAL → CORRECTA queda registrada y no sustituida por una transcripción reconstruida.
- Mantener baseline previo como faltante y no reconstruirlo: **CORRECTA, H0**, indicando que la salida de ramas remotas fue aportada por el estudiante.
- Soporte nominal de compositing de 2 m: **CORRECTA, H0**; distingue soporte del composite de tamaño de bloque y reconoce que los tramos de contacto/residuales son más cortos.
- Anclaje de bins en el collar y no cruce de contactos: **CORRECTA, H0**; los múltiplos y paridad alegados fueron comprobados en lectura.
- Media ponderada por longitud y registro de cobertura parcial: **CORRECTA, H0**; verificada la ausencia de bins con varios ensayes de una misma litología en el dataset actual. B07 queda VERIFIED como decisión documentada; B08 sigue sin implementación ni pruebas.
- `composite_id` por sondaje más secuencia determinista de cuatro dígitos: **CORRECTA, H0**. Lectura de assay por sondaje: 35 sondajes, 115–218 assays por sondaje; cuatro dígitos son suficientes para el conteo actual.
- Interpretación de resultados como consistencia computacional y no validación geológica: **CORRECTA, H0**. Cu ponderado, procedencia por muestra, código AIR y ausencia de topografía se verificaron de nuevo en lectura.
- Política de conservar los cinco códigos observados sin asignar significados no documentados y marcar `AIR` para revisión: **CORRECTA, H0**; conteos, longitudes, tramo/fuente AIR y Cu=0 verificados independientemente.
- `composite_id` único con `sample_id` de procedencia: **CORRECTA, H0**. Las 5.332 filas y 57 sample IDs duplicados son un total esperado según la regla, no salida producida; el formato reproducible del ID queda pendiente de definir.

El gate B08 fue aprobado por el estudiante para los tres archivos especificados. B08 queda VERIFIED computacionalmente y B10 VERIFIED. No se aprueba `BASE_VERIFIED` ni se inicia `EVALUATION_PLAN`: B09 está `RECOVERY_BLOCKED` y B05 permanece PARTIAL.

## Archivos creados con autorización

```text
docs/implementation/IMP-002_m01b_block_model_preparation.md
docs/exam/T2_M01B_PLAN_G04.md
docs/exam/T2_M01B_EVIDENCE_G04.md
```

## B08 — compositing autorizado, ejecución y resultados reales

**Alcance autorizado:** `src/m01/compositing.py`, `tests/m01/test_compositing.py` y `data/processed/m01b_composites.csv`. Se usó exclusivamente `C:\Proyecto_Plan\.venv\Scripts\python.exe`. No se modificaron `data/raw/`, `main.py` ni gobernanza; no se instalaron dependencias, no se ejecutó `main.py` y no se hizo commit/push.

### Pruebas específicas

Comando exacto desde `C:\Proyecto_Plan\PlanMinUPN-G04`:

```text
C:\Proyecto_Plan\.venv\Scripts\python.exe -m unittest discover -s tests\m01 -p test_compositing.py -v
```

Salida real:

```text
test_composite_ids_are_stable_in_depth_order (test_compositing.CompositingTests.test_composite_ids_are_stable_in_depth_order) ... ok
test_contact_splits_assay_and_preserves_source_id (test_compositing.CompositingTests.test_contact_splits_assay_and_preserves_source_id) ... ok
test_current_release_matches_expected_composite_invariants (test_compositing.CompositingTests.test_current_release_matches_expected_composite_invariants) ... ok
test_incomplete_lithology_coverage_is_rejected (test_compositing.CompositingTests.test_incomplete_lithology_coverage_is_rejected) ... ok
test_out_of_trajectory_composite_is_rejected_without_extrapolation (test_compositing.CompositingTests.test_out_of_trajectory_composite_is_rejected_without_extrapolation) ... ok
test_short_terminal_assay_is_partial_and_not_zero_filled (test_compositing.CompositingTests.test_short_terminal_assay_is_partial_and_not_zero_filled) ... ok
test_weighted_grade_is_based_on_contributing_lengths (test_compositing.CompositingTests.test_weighted_grade_is_based_on_contributing_lengths) ... ok

----------------------------------------------------------------------
Ran 7 tests in 0.204s

OK
EXIT_CODE=0
```

### Generación reproducible

Comando exacto desde `C:\Proyecto_Plan\PlanMinUPN-G04`:

```text
C:\Proyecto_Plan\.venv\Scripts\python.exe -m src.m01.compositing
```

Salida real:

```text
composites_written=5332
output=C:\Proyecto_Plan\PlanMinUPN-G04\data\processed\m01b_composites.csv
EXIT_CODE=0
```

### Suite completa posterior a las pruebas de compositing

Comando ejecutado desde la raíz del repositorio con el intérprete autorizado:

```text
C:\Proyecto_Plan\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

La salida real informó `Ran 47 tests in 1.351s`, `OK`, exit code **0**. Los 47 PASS incluyen 40 pruebas M01 existentes y las 7 nuevas de compositing. Salida final exacta:

```text
----------------------------------------------------------------------
Ran 47 tests in 1.351s

OK
EXIT_CODE=0
```

### Comparación de métricas esperadas y observadas

| Métrica | Esperado | Observado | Diferencia |
|---|---:|---:|---:|
| Filas composite | 5.332 | 5.332 | 0 |
| Filas con longitud de 2 m | 5.188 | 5.188 | 0 |
| Filas parciales | 144 | 144 | 0 |
| `sample_id` repetidos dos veces | 57 | 57 | 0 |
| IDs `composite_id` únicos | 5.332 | 5.332 | 0 |

Comprobaciones de soporte/posicionamiento:

```text
composite_length_m=10518.328249553 assay_length_m=10518.328249553 source_length_mismatches=0
lithology_support_mismatches=0 output_rows_with_xyz=5332
```

Todos los ocho hashes SHA-256 del manifest (`README.md` y siete archivos fuente) siguen coincidiendo:

```text
README.md exists=True hash_match=True
alteration.csv exists=True hash_match=True
assay.csv exists=True hash_match=True
collar.csv exists=True hash_match=True
data_dictionary.csv exists=True hash_match=True
density.csv exists=True hash_match=True
lithology.csv exists=True hash_match=True
survey.csv exists=True hash_match=True
```

No se encontró discrepancia respecto a los conteos esperados. El CSV contiene las columnas de procedencia, bins, intervalos, longitudes, marca parcial, litología, leyes y XYZ; se añadió `source_sample_ids` (JSON) para conservar todos los IDs de assay si en otra configuración se agregaran varias fuentes a un composite. En este release cada fila conserva un solo `sample_id`.

**Estado tras la interpretación del estudiante:** B08 **VERIFIED (computacional)**. La aceptación del estudiante reconoce que consistencia de conteos/soporte no valida geológicamente los datos. No se generó un block model y B09/topografía permanece `RECOVERY_BLOCKED`.

### Interpretación formativa y verificación independiente posterior

El estudiante aceptó la evidencia de compositing con la limitación de que las mitades de ensayes heredados no son mediciones independientes y los tramos parciales no tienen soporte de 2 m. También identificó una fila codificada `AIR` que debe revisarse en P1; se conserva el código como dato observado sin interpretar que representa aire físico.

Comprobaciones de solo lectura con el `.venv` sobre `assay.csv` y `m01b_composites.csv`:

```text
assay_cu_length_weighted_pct=0.252487149710
composite_cu_length_weighted_pct=0.252487149710
composites_with_cu_not_matching_source=0
air_composites=1 lith_codes={'AIR': 1, 'BRX': 412, 'DIO': 2017, 'POR': 2751, 'REG': 151}
air_rows=[('CR-C02-002_0001', 'CR-C02-002-A0001', '0.0', '2.0', '2.0', '0.0')]
unique_lith_code_per_row=True
```

La verificación también confirma cero discrepancias de longitud total, soporte por `sample_id` y soporte contra litología, coordenadas XYZ en 5.332 filas, y 8/8 hashes SHA-256 del manifest coincidentes. El valor `0.252487149710 %` es un promedio ponderado por longitud; no es validación económica, geoestadística ni de recursos.

**Estado global antes de la decisión P0:** `BASE_VERIFIED` no aprobado. B09 requiere topografía local verificable para la clasificación aire/roca y permanece `RECOVERY_BLOCKED`; B05 se mantiene PARTIAL porque el baseline histórico M01B no existe. El escenario permite solo planificación conceptual mientras persistan esos bloqueos críticos.

## P0 — Continuación conceptual bajo RECOVERY_BLOCKED

El estudiante eligió continuar en P0 de manera conceptual, dejando la clase topográfica como `TOPO_UNKNOWN`. Su elección y justificación literal están registradas en `docs/exam/T2_M01B_PLAN_G04.md`, Decisión 14. Evidencia existente: `data/raw/` contiene solo los ocho archivos del manifest, sin fuente topográfica; el escenario permite únicamente planificación conceptual al faltar un requisito crítico. Se mantiene `BASE_VERIFIED=No`, B09=`RECOVERY_BLOCKED`, y no hay autorización de código/resultado adicional.

### P0.1 — Orden de etapas mientras B09 está bloqueado

Comprobación de solo lectura con `.venv`, sobre `lithology.csv`, `m01b_composites.csv`, `drillhole_trajectory.csv` y `m01_validacion_espacial.csv`:

```text
lithology_codes= ['AIR', 'BRX', 'DIO', 'POR', 'REG']
composite_lith_counts= {'AIR': 1, 'BRX': 412, 'DIO': 2017, 'POR': 2751, 'REG': 151}
trajectory_holes= 35 rows= 270
collar_z_range= 3288.0 3524.0
trajectory_bottom_z_range= 3059.5304807122184 3097.3195543127063
trajectory_xy_extent= 552.9701312319958 565.2999132331461
spatial_rows= 35 distance_count= 35 distance_min= 5.979267032068487 median= 19.999999999500123 max= 92.7361849549496
topography_files= []
```

El estudiante eligió A: P1 primero; comparar opciones P2 con XYZ reales y límite superior provisional/`TOPO_UNKNOWN`; consultar topografía en paralelo; detener clasificación AIR/ROCK hasta verificar P3. Evaluación: **CORRECTA, H0** como secuencia conceptual. Las cifras verifican la evidencia que citó. No se calcularon candidatos de malla ni se produjeron salidas P2; esas decisiones siguen pendientes. El escenario autoriza planificación conceptual, no generación/validación ante B09 crítico.

Estado conversacional: `EVALUATION_PLAN` conceptual bajo `RECOVERY_BLOCKED`; P0 sigue en elaboración y P1.2 ya decidió preservar `AIR` con `REVIEW/UNKNOWN`, sin extensión volumétrica ni traducción a `topo_status=AIR`.

### P1.1 — códigos observados y soporte

Verificación de solo lectura posterior a la respuesta del estudiante, con el `.venv`, en `data/processed/m01b_composites.csv`, `data/raw/lithology.csv` y `data/raw/assay.csv`:

```text
counts= {'AIR': 1, 'BRX': 412, 'DIO': 2017, 'POR': 2751, 'REG': 151}
lengths= {'AIR': 2.0, 'BRX': 809.262, 'DIO': 3989.848, 'POR': 5455.218, 'REG': 262.0}
air_composites= CR-C02-002_0001, hole_id=CR-C02-002, MD 0.0-2.0, length=2.0, Cu=0.0
air_lith_rows= hole_id=CR-C02-002, MD 0.000000000-2.000000000, lith_code=AIR
air_source_assays= sample_id=CR-C02-002-A0001, Cu=0.000000000
```

Se confirma la respuesta como **CORRECTA, H0**. Evidencia del código AIR se conserva sin inferencia de su significado físico; los conteos son soporte de observaciones por categoría, no estimaciones de volumen.

### P1.2 — tratamiento conceptual de `AIR`

Respuesta literal del estudiante:

> A. Preservo AIR como código observado separado, marcado REVIEW/UNKNOWN; lo excluyo de la extensión volumétrica de dominios y no lo traduzco a topo_status=AIR hasta aclarar su significado y contar con topografía verificada.
>
> Evidencia del repositorio: AIR aparece una sola vez en m01b_composites.csv (CR-C02-002_0001, MD 0–2 m, Cu = 0), proviene de lithology.csv y está inmediatamente sobre REG desde 2 m. En el repositorio no hay un diccionario de códigos ni una superficie topográfica que permitan confirmar si es aire físico.
>
> Ventaja: mantengo la trazabilidad con la fuente sin afirmar que es roca ni que es aire, y evito que un único tramo de 2 m defina por sí solo un volumen o una condición topográfica.
>
> Limitación: ese tramo de 2 m queda sin dominio asignado y la duda sobre su significado (aire físico, tramo sin recuperación o convención de registro) solo se resuelve con la definición oficial del código o con la topografía en P3. Si resultara ser roca, habría que reincorporarlo.

Evaluación: **CORRECTA, H0**. La opción preserva la etiqueta fuente y separa el código litológico del estado físico/topográfico. No se infiere roca o aire físico, ni se usa el único tramo para definir volumen. Esta decisión es conceptual; no se modifican datos ni se inicia clasificación.

### P1.3 — uso conceptual de contactos litológicos

Respuesta literal del estudiante:

> B. Uso los contactos como evidencia observada, pero solo trataría como límite duro uno cuya continuidad y significado geológico hayan sido validados; en los demás mantengo explícita la incertidumbre (por ejemplo, con un flag de proximidad a contacto o UNKNOWN en zonas disputadas).
>
> Evidencia del repositorio: lithology.csv registra 82 contactos internos en los 35 sondajes, con transiciones REG→DIO (31), DIO→POR (10), REG→POR (8), POR→BRX (5), BRX→POR (2) y DIO→REG (1). Las distancias 3D mínimas entre trayectorias van de 5.98 a 92.74 m (mediana 20 m, outputs/tables/m01_validacion_espacial.csv). No hay en el repositorio secciones interpretadas, superficies de contacto ni un modelo geológico que demuestre cómo continúan los contactos entre sondajes. Los compósitos ya respetan los contactos dentro de cada sondaje (B07/B08), así que no mezclan códigos.
>
> Ventaja: respeto el contacto donde está observado sin inventar superficies continuas entre sondajes separados hasta 93 m. Las transiciones poco frecuentes (BRX→POR 2, DIO→REG 1) no se convierten en límites regionales.
>
> Limitación: sin límites duros validados, los bloques cercanos a un contacto o entre sondajes con códigos distintos tendrán una asignación más incierta y podrán quedar como UNKNOWN. Reducir esa incertidumbre exige interpretación geológica (secciones, criterio del docente) que no está en el repositorio.

Evaluación: **CORRECTA, H0**. La política diferencia contactos observados a lo largo de sondajes de superficies geológicas continuas en 3D y conserva la incertidumbre donde no hay interpretación validada. Los compósitos que respetan contactos acreditan separación local, no continuidad entre sondajes.

Siguiente decisión propuesta: P1.4, cómo representar zonas entre sondajes con códigos diferentes cuando no hay un límite geológico validado. Evidencia disponible en registros previos: 35 trayectorias; distancia mínima 3D entre vecinas 5,979–92,736 m, mediana 20,000 m; no hay superficies interpretadas. B09 sigue `RECOVERY_BLOCKED`, así que esta es una decisión conceptual y no autoriza generar bloques ni clasificarlos.

### P1.4 — representación de zonas sin dominio respaldado

Respuesta literal del estudiante:

> A. En zonas donde los sondajes vecinos muestran códigos distintos y no hay un límite geológico validado, dejo el dominio como UNKNOWN con la causa identificada (por ejemplo, CONFLICTING_CODES o INSUFFICIENT_SUPPORT) y documento qué permitiría reclasificarlo.
>
> Evidencia del repositorio: hay 82 contactos internos registrados en lithology.csv pero ninguna superficie de contacto interpretada ni sección geológica en el repositorio. Las distancias 3D mínimas entre trayectorias vecinas llegan a 92.736 m (mediana 20 m, outputs/tables/m01_validacion_espacial.csv), así que entre sondajes alejados no hay observaciones que indiquen dónde está el cambio de código. Los únicos códigos documentados son REG, DIO, POR, BRX y AIR; no existe una categoría de transición en los datos.
>
> Ventaja: el modelo muestra de forma explícita dónde falta evidencia, en vez de rellenar el volumen con un código que podría estar equivocado, y no se crean litologías que no aparecen en los datos.
>
> Limitación: la cobertura del modelo quedará incompleta, y en zonas de contactos frecuentes (por ejemplo REG→DIO, 31 transiciones) puede haber muchos bloques UNKNOWN. Para reclasificarlos haría falta un criterio de soporte definido en P4 (distancia máxima al compósito y concordancia de códigos vecinos), una interpretación geológica validada por el docente o más perforación.

Evaluación: **CORRECTA, H0**. La decisión diferencia falta de evidencia de una categoría geológica y evita propagación automática. `CONFLICTING_CODES` e `INSUFFICIENT_SUPPORT` quedan como causas propuestas, no como códigos ya implementados. La posibilidad de muchos bloques UNKNOWN y la necesidad de un criterio P4 son limitaciones pertinentes.

### P1.5 — procedencia y estado de asignación

Respuesta literal del estudiante:

> A. Cada asignación provisional debería guardar: dominio (lith_code), fuente(s) de soporte (composite_id y, por trazabilidad, sample_id), distancia al soporte (y, si el método lo usa, número de compósitos de apoyo), regla/versión aplicada y estado o causa de incertidumbre (assignment_status ASSIGNED/UNKNOWN/UNASSIGNED con causa como CONFLICTING_CODES o INSUFFICIENT_SUPPORT). Si falta la evidencia mínima, el bloque queda UNKNOWN.
>
> Evidencia del repositorio: m01b_composites.csv ya trae composite_id único, sample_id/source_sample_ids, lith_code y coordenadas XYZ, así que la procedencia puede rastrearse hasta el ensaye original. Además, el contrato mínimo de la sección 7 de docs/exam/T2_M01B/02_SCENARIO_EXAM_M01B.md incluye assignment_status, support_distance_or_count y uncertainty_or_review_flag por bloque. Las distancias entre trayectorias varían de 5.979 a 92.736 m, por lo que el soporte será muy distinto de un bloque a otro y debe quedar registrado individualmente.
>
> Ventaja: cualquier asignación se puede auditar y reproducir (de qué compósito viene, a qué distancia y con qué regla), y si la regla cambia en P4 se puede identificar qué bloques se ven afectados por la versión.
>
> Limitación: el modelo tendrá más columnas y ocupará más memoria, y estos metadatos documentan cómo se asignó el dominio, pero no lo convierten en una interpretación geológica validada. La distancia por sí sola tampoco garantiza continuidad geológica.

Verificación del contrato (lectura de `docs/exam/T2_M01B/02_SCENARIO_EXAM_M01B.md`, sección de esquema de bloque): enumera `assignment_status` como `ASSIGNED / UNKNOWN / UNASSIGNED / NOT_APPLICABLE`, `support_distance_or_count` “si el método lo define” y `uncertainty_or_review_flag` “según definición aprobada”. El archivo de composites tiene `composite_id`, `sample_id`, `source_sample_ids`, `lith_code` y coordenadas FROM/MID/TO XYZ.

Evaluación: **CORRECTA, H0**. Coinciden con el contrato los campos mínimos propuestos de procedencia, soporte e incertidumbre. Precisión: `NOT_APPLICABLE` es un estado adicional en el esquema del escenario; los tres enumerados por el estudiante son estados propuestos, no la enumeración completa. Estos metadatos documentan la asignación, pero no validan continuidad geológica.

### Evidencia de cálculo conceptual P2.1 (solo lectura)

Comando de lectura ejecutado desde el workspace:

```powershell
& 'C:\Proyecto_Plan\.venv\Scripts\python.exe' -c "import csv, math; p=r'C:\Proyecto_Plan\PlanMinUPN-G04\data\processed\drillhole_trajectory.csv'; rows=list(csv.DictReader(open(p, newline='', encoding='utf-8-sig'))); a={k:[float(r[k]) for r in rows] for k in ('x','y','z')}; s={k:max(v)-min(v) for k,v in a.items()}; print('rows',len(rows)); print('bounds', {k:(min(v),max(v)) for k,v in a.items()}); print('spans',s); print('candidates', {dims: math.ceil(s['x']/dims[0])*math.ceil(s['y']/dims[1])*math.ceil(s['z']/dims[2]) for dims in ((10,10,5),(20,20,10),(40,40,20))})"
```

Resultado real: 270 filas; X bounds 242422.632507442–242975.602638674 (span 552.9701312319958 m), Y bounds 8196180.479701123–8196745.779614356 (span 565.2999132331461 m), Z bounds 3059.5304807122184–3524.0 (span 464.4695192877816 m). Conteos usando `ceil(span/dim)` sobre el envolvente sin padding: 10×10×5 m = 296.856; 20×20×10 m = 38.164; 40×40×20 m = 5.040. Exit code 0. Esta estimación no fija origen, alineación ni padding y el Z superior basado en collar no es topografía; por tanto, no es un grid generado ni una geometría aprobada.

### P2.1 — escala candidata de celdas

Respuesta literal del estudiante:

> B. Defiendo 20 × 20 × 10 m como escala candidata para continuar conceptualmente en P2.
>
> Evidencia del repositorio: la mediana de la distancia 3D mínima entre trayectorias vecinas es 20 m (rango 5.979–92.736 m, outputs/tables/m01_validacion_espacial.csv). Como es la distancia de máximo acercamiento, el espaciamiento típico entre sondajes es igual o mayor, así que celdas horizontales de 10 m (A) implicarían una resolución que los datos no tienen entre sondajes. En vertical, dz = 10 m equivale a 5 compósitos de 2 m (m01b_composites.csv), por lo que cada celda queda atravesada por varios compósitos donde hay sondaje. No es dx = dy = dz = longitud del compósito.
>
> Ventaja: 38,164 bloques es manejable para generar, probar y visualizar en 3D. El tamaño horizontal es coherente con el espaciamiento observado, sin falsa resolución, y dz = 10 m todavía permite representar los cambios de litología en profundidad (82 contactos internos).
>
> Limitación: con 20 m en planta, las zonas donde los sondajes están separados hasta 93 m seguirán sin soporte (quedarán UNKNOWN), y en zonas densas de contactos (REG→DIO) una celda de 10 m de alto puede contener más de un código, lo que exigirá una regla de desempate o un flag en P4. El conteo es provisional: falta definir origen, alineación y padding, y el límite superior depende de la topografía, que sigue bloqueada (B09).

Verificación de solo lectura de `outputs/tables/m01_validacion_espacial.csv`: 35 trayectorias con `minimum_trajectory_distance_3d_m`; mínimo 5,979267 m, mediana 19,9999999995 m y máximo 92,736185 m. El campo representa distancia 3D mínima de acercamiento entre la trayectoria y la trayectoria vecina identificada, no espaciamiento horizontal muestreado en todos los niveles. La cota usada aquí sí apoya que la separación puede ser grande, pero no sustenta por sí sola que `dx=10 m` tenga falsa resolución ni que toda separación sea igual o mayor al mínimo 3D. El conteo 38.164 ya consta del cálculo de envolvente sin padding para la candidata 20×20×10 m; `dz=10 m` equivale aritméticamente a cinco longitudes objetivo de 2 m, no garantiza varios composites en cada bloque ni cambios representables en celdas sin sondaje.

Evaluación: **PARCIAL, H1**. Se conserva 20×20×10 m como escala candidata defendible por costo/propósito conceptual, no aprobada. Debe compararse el espaciamiento horizontal y la cobertura vertical locales antes de sostener la resolución. La posible mezcla de códigos en una celda y sus reglas de asignación son cuestiones de P4, no resultados verificados sin grid.

Siguiente decisión: P2.2, política conceptual para origen y alineación. B09 permanece `RECOVERY_BLOCKED`; no se genera grid ni se clasifica aire/roca.

### P2.2 — origen y alineación del grid

Respuesta literal del estudiante:

> B. Redondeo el origen a múltiplos del tamaño de bloque: X y Y a múltiplos de 20 m y Z a múltiplos de 10 m, alineado a los ejes X/Y/Z del dataset y con Z superior provisional.
>
> Evidencia del repositorio: con los mínimos observados (X = 242422.633, Y = 8196180.480, Z = 3059.530) y la extensión de las 270 estaciones de drillhole_trajectory.csv, el origen redondeado queda en X0 = 242420, Y0 = 8196180, Z0 = 3050, y los máximos (≈ 242975.6 / 8196745.8 / 3524.0) se cubren con 28 × 29 × 48 = 38,976 bloques, frente a 38,164 anclando en los mínimos exactos: solo 812 bloques más (≈ 2.1 %), que corresponden a una capa adicional en Z y a bordes de pocos metros.
>
> Ventaja: el origen y los límites de celda no dependen de los datos de un release concreto. Si se agregan sondajes o cambia el mínimo observado, los índices i, j, k de los bloques existentes se mantienen, y las coordenadas de centros y esquinas son números redondos fáciles de verificar en pruebas (centro = origen + (índice + 0.5) × tamaño).
>
> Limitación: se agregan celdas de padding sin soporte de datos, que quedarán UNKNOWN o fuera de la envolvente. Los múltiplos se refieren a coordenadas sin CRS/EPSG documentado, así que la alineación no está garantizada con un sistema oficial. Además, la cota superior de 3530 m es provisional hasta tener topografía, y nz puede cambiar en P3.

Verificación de solo lectura con el `.venv` sobre las 270 filas de `data/processed/drillhole_trajectory.csv`: mínimos `(242422.632507442, 8196180.479701123, 3059.5304807122184)`, máximos `(242975.602638674, 8196745.779614356, 3524.0)`. Con origen `(242420, 8196180, 3050)` y tamaños `(20,20,10)`, `n=(28,29,48)`, total **38.976**, bordes máximos `(242980,8196760,3530)`. Con origen exacto en mínimos, `n=(28,29,47)`, total **38.164**; delta **812 (2,13 %)**. Exit code 0. No se generó malla.

Evaluación: **CORRECTA, H0**. Los valores y conteos son correctos. La estabilidad de índices al agregar datos requiere mantener fija la base coordenada, orientación, origen y dimensiones; el redondeo por sí solo no establece CRS/EPSG ni convención oficial. El límite superior sigue provisional y no equivale a topografía.

Siguiente decisión: P2.3, padding adicional y manejo del límite superior provisional. El envolvente observado ya cabe en 38.976 celdas; un bloque extra en cada cara daría 30×31×50 = 46.500. La ausencia de topografía y margen minero documentado debe mantenerse explícita. No generar grid ni cerrar B09.

### P2.3 — padding adicional y límite provisional

Respuesta literal del estudiante:

> A. No añado padding completo más allá del necesario para cubrir las trayectorias: mantengo 28 × 29 × 48 = 38,976 celdas con origen (242420, 8196180, 3050) y límite (242980, 8196760, 3530), con todos los límites provisionales y Z superior a revisar con la topografía en P3.
>
> Evidencia del repositorio: el redondeo del origen ya agrega bordes parciales para cubrir los extremos de las 270 estaciones de drillhole_trajectory.csv (las 35 trayectorias quedan dentro). Añadir una celda en cada cara daría 30 × 31 × 50 = 46,500 celdas: 7,524 celdas más (+19.3 %), todas fuera del envolvente de los sondajes y sin compósitos que las respalden. En el repositorio no hay una extensión de proyecto aprobada ni un margen minero documentado que justifique ampliar el volumen.
>
> Ventaja: el modelo se limita al volumen donde hay información, evita extrapolar dominios a zonas sin datos y mantiene un tamaño manejable para pruebas y visualización 3D.
>
> Limitación: si más adelante se justifica una zona periférica (por ejemplo, para un pit o para la topografía oficial con mayor cobertura), habrá que ampliar la malla y recalcular el conteo. Los bloques de la periferia actual siguen teniendo poco soporte. La cota superior de 3530 m depende de los collars y no de la superficie real, así que nz puede cambiar en P3.

Verificación de solo lectura con `.venv` en `data/processed/drillhole_trajectory.csv`: 270 estaciones, 35 `hole_id`; cero estaciones fuera de los límites candidatos. Conteo `28×29×48 = 38.976`; con un bloque adicional en cada cara `30×31×50 = 46.500`; diferencia 7.524, equivalente a 19,304 % del conteo base. Exit code 0. Esto solo demuestra cobertura del envolvente de trayectorias, no que los límites sean suficientes para una extensión minera.

Evaluación: **CORRECTA, H0**. Se justifica no añadir padding completo sin requerimiento documentado y se mantienen provisionalidad y riesgo de ampliación por topografía/proyecto. No se generó una malla ni se asignaron estados a bloques.

Siguiente decisión: P2.4, convención de ejes y elevación vertical. La tabla de trayectorias usa coordenadas X/Y/Z; Z de collar es mayor que Z de fondo, pero CRS/datum no están documentados. No transformar coordenadas ni integrar topografía hasta verificarla; B09 sigue `RECOVERY_BLOCKED`.

### P2.4 — convención de ejes y elevación vertical

Respuesta literal del estudiante:

> A. Conservo X/Y/Z sin rotación, alineando la malla a los ejes del dataset, con Z numérico positivo hacia arriba (elevación); declaro CRS y datum como desconocidos y confirmaré la compatibilidad antes de integrar cualquier topografía.
>
> Evidencia del repositorio: en drillhole_trajectory.csv la Z de los collars (3288–3524 m) es mayor que la de los fondos (3059.530–3097.320 m), lo que confirma que Z crece hacia arriba. Esto es coherente con las convenciones de desurvey definidas en M01 (IMP-001, commit 1e26f5f), que ya produjeron los XYZ de m01b_composites.csv. Las campañas no tienen todas el mismo azimut (en la T1 se usó 145° como dominante solo para C01/C02), así que no hay una única tendencia que justifique una rotación local. Ningún archivo de data/raw/ documenta CRS, EPSG ni datum.
>
> Ventaja: la malla queda en el mismo sistema que trayectorias y compósitos, sin transformaciones que podrían introducir errores. Las pruebas de índices y centros son directas, y el visualizador 3D puede superponer bloques y sondajes sin conversión.
>
> Limitación: si los cuerpos o contactos tienen una orientación oblicua a X/Y, una malla no rotada los representa en escalera. Además, sin CRS ni datum conocidos no puedo garantizar que una topografía futura use el mismo sistema: habrá que comprobar coordenadas, elevaciones y unidades antes de integrarla en P3.

Comprobaciones de solo lectura: 35 sondajes; collar Z 3288–3524 m; Z de fondo 3059,5304807122184–3097,3195543127063 m. El commit `1e26f5f` existe y corresponde al registro de convenciones geométricas/desurvey de IMP-001. Ese documento define las convenciones del equipo para azimuth/dip y método; no aporta CRS/datum. No se encontraron tokens EPSG/CRS/datum en los archivos de `data/raw/`. La respuesta se evalúa **CORRECTA, H0**: conserva el sistema sin transformación injustificada, reconoce el sentido Z observado y deja por confirmar la compatibilidad geodésica antes de P3. Z creciente en estos sondajes no identifica un datum vertical absoluto.

### Cálculo de solo lectura para revisar espaciamiento horizontal

Sobre las estaciones de profundidad 0 de las 35 trayectorias, la distancia XY al collar más cercano por sondaje tiene mínimo 20,000 m, mediana 60,000 m y máximo 92,195 m. Como verificación adicional de la decisión P2.1, se calcularon conteos para `dz=10 m` y envolvente de trayectoria (Z 3050–3530 m), redondeando origen X/Y a múltiplos del ancho horizontal: 20 m produce `28×29×48 = 38.976`; 40 m produce `15×15×48 = 10.800`; 60 m produce `10×10×48 = 4.800`. Son candidatos conceptuales; no se generó grid. Los espaciamientos de collar no equivalen a espaciamientos a todas las profundidades.

Siguiente decisión: P2.5, revisar el tamaño horizontal candidato con la distribución de distancias XY de collares y los conteos comparativos. Esta pregunta busca completar la justificación PARCIAL de P2.1; no aprueba malla ni topografía.

### P2.5 — revisión de escala horizontal con datos de espaciamiento

Respuesta literal del estudiante:

> A. Mantengo 20 × 20 m en planta con dz = 10 m provisional (38,976 bloques) como candidato conceptual para P2.
>
> Métrica real: la distancia XY al collar más cercano es de 20.000 m mínimo, 60.000 m mediana y 92.195 m máximo, y la distancia 3D mínima entre trayectorias tiene mediana de 20 m porque los sondajes inclinados se acercan en profundidad. Un tamaño horizontal de 20 m equivale a 1/3 de la mediana de espaciamiento en collar, dentro del rango práctico de 1/3 a 1/2 del espaciamiento, y coincide con el espaciamiento mínimo. 40 m sería ≈ 2/3 y 60 m sería igual a la mediana, de modo que la mayoría de los bloques tendría como mucho un sondaje.
>
> Corrección de conteo: con 40 × 40 × 10 m y el origen (242420, 8196180, 3050), nx = 560/40 = 14, ny = ceil(580/40) = 15, nz = 48, por lo que el total es 14 × 15 × 48 = 10,080 bloques, no 10,800.
>
> Ventaja: con una asignación categórica, celdas de 20 m respetan mejor los contactos observados (82 internos) y las zonas de sondajes cercanos, sin llegar a celdas más finas que el espaciamiento mínimo. 38,976 bloques sigue siendo manejable para probar y visualizar.
>
> Limitación: en las zonas donde los collars están a 60–92 m, muchos bloques de 20 m quedarán sin soporte directo (UNKNOWN), y el tamaño puede sugerir más detalle del que hay entre sondajes. Por eso la asignación debe incluir distancia al soporte y causa de UNKNOWN. La escala es provisional y no autoriza generar la malla; B09 sigue bloqueado.

Verificación/corrección: se recalcularon conteos para 40×40×10 m con las mismas extensiones XYZ. Manteniendo el origen `(242420, 8196180, 3050)` usado para 20 m, resulta `14×15×48 = 10.080`. Aplicando la regla previa de alinear el origen a múltiplos del tamaño de cada candidato, el origen de 40 m es `(242400, 8196160, 3050)` y el total resulta `15×15×48 = 10.800`. Ambos son aritméticamente correctos bajo sus respectivos orígenes; el origen común no es múltiplo de 40 y por tanto no cumple la regla de alineación decidida para cada tamaño. No se generó grid.

Evaluación: **PARCIAL, H1**. La mediana y rango XY al vecino más cercano en collar se verifican; apoyan la variabilidad de densidad, pero no determinan soporte por bloque a profundidad. La razón 1/3–1/2 es una heurística no sustentada por una fuente o validación específica de este ejercicio. Afirmar que la mayoría de bloques grandes contendrá como mucho un sondaje y que 20 m respeta mejor contactos requiere análisis espacial de bloques/P4; sigue siendo una hipótesis. Se mantiene 20×20×10 m como candidata de trabajo, no escala aprobada.

Siguiente paso: aclarar si se mantiene esta candidata con afirmaciones moderadas, se comparan tamaños con origen común explícito o se pospone la selección hasta estudiar espaciamiento/cobertura a profundidad. P2.1 sigue PARCIAL; B09 permanece `RECOVERY_BLOCKED`.

Revisión de P2.1 — respuesta literal del estudiante:

> A. Mantengo 20 × 20 × 10 m como candidata conceptual, con afirmaciones moderadas: es una escala plausible, no una resolución demostrada, y la verificación espacial del soporte y de los contactos queda para P4.
>
> Evidencia del repositorio: la distancia XY al collar más cercano varía entre 20 y 92.195 m (mediana 60 m) y la distancia 3D mínima entre trayectorias tiene mediana de 20 m, lo que muestra densidad de datos variable. Ya están registradas tres alternativas con sus conteos: 20 × 20 × 10 m = 38,976; 40 × 40 × 10 m = 10,800 (origen alineado a 40 m, 242400 / 8196160 / 3050; corrijo mi conteo de 10,080, que usaba un origen no alineado con la regla de P2.2); 60 × 60 × 10 m = 4,800. La regla de 1/3–1/2 del espaciamiento la uso solo como heurística, no como validación.
>
> Ventaja: puedo avanzar a P3/P4 con una escala candidata definida y trazable. La decisión puede revisarse con evidencia real en P4 (cuántos bloques quedan con soporte, a qué distancia y cuántos con códigos en conflicto), en vez de discutirla solo con distancias en collar.
>
> Limitación: todavía no demuestro que 20 m represente adecuadamente los contactos ni que haya soporte a profundidad en cada bloque. Si en P4 resulta una proporción muy alta de UNKNOWN o celdas con varios códigos, habrá que reconsiderar 40 × 40 × 10 m. La escala sigue siendo provisional y no autoriza generar la malla; B09 sigue bloqueado.

Evaluación revisada: **CORRECTA, H0**. Se moderan las afirmaciones previas no demostradas; la heurística queda identificada como tal; la corrección del conteo 40×40×10 m usa el origen alineado de P2.2. Se mantiene 20×20×10 m como candidata conceptual y se difiere a P4 la verificación de soporte y contactos. No implica resolución demostrada ni autorización de malla.

### P2.6 — identificadores e índices reproducibles

Microteoría y alternativas planteadas: la decisión debe fijar base de índices, correspondencia de ejes, formato de ID y orden de recorrido. El escenario exige identificadores únicos, índices, centros/dimensiones/volumen, y pruebas de orden/reproducibilidad, pero deja el formato a la implementación autorizada. Alternativas: (A) índices base cero, ejes i→X/j→Y/k→Z, ID determinista derivado de índices y orden de recorrido explícito; (B) índices base uno e ID secuencial ordenado; (C) ID por centro redondeado sin índices.

La pregunta P2.6 está pendiente de respuesta; no se ha aprobado ni generado grid. B09 sigue `RECOVERY_BLOCKED`.

Respuesta literal P2.6:

> A. Índices base cero con i→X, j→Y, k→Z; block_id determinista calculado desde (i, j, k) como block_id = i + j·nx + k·nx·ny, con recorrido k exterior, después j, e i interior.
>
> Evidencia del escenario y la arquitectura: la sección 7 de docs/exam/T2_M01B/02_SCENARIO_EXAM_M01B.md pide block_id, index_i, index_j, index_k, center_x/y/z, dx/dy/dz y nominal_volume, y P2 exige pruebas de IDs únicos, orden e índices, centro/esquinas correctos y reproducibilidad. En B08 ya usamos una convención determinista (composite_id = hole_id + secuencia), así que mantengo el mismo criterio. Con la candidata 20 × 20 × 10 m y origen (242420, 8196180, 3050): nx = 28, ny = 29, nz = 48, los IDs van de 0 a 38,975, y el centro se obtiene como center_x = 242420 + (i + 0.5)·20, center_y = 8196180 + (j + 0.5)·20, center_z = 3050 + (k + 0.5)·10.
>
> Ventaja: el ID y la ubicación se pueden reconstruir uno desde el otro sin depender del orden de las filas en el archivo, lo que permite probar unicidad, índices y centros con casos simples (por ejemplo, block_id 0 → (0, 0, 0) → centro (242430, 8196190, 3055)). Base cero coincide con Python/numpy y evita errores de media celda.
>
> Limitación: el block_id depende de nx y ny, por lo que si cambia la extensión (por ejemplo, con la topografía en P3 o con otro tamaño de bloque) cambian los IDs y no son comparables entre versiones. Por eso hay que guardar también i, j, k y registrar la versión de la geometría. Base cero puede confundir a quien lea la tabla esperando índices desde 1.

Verificación de lectura/cálculo: `nx=28`, `ny=29`, `nz=48`; enumeración con `k` exterior, `j` intermedio, `i` interior produjo 38.976 IDs únicos, mínimo 0, máximo 38.975. Verificados ejemplos en límites de eje: `id=27` corresponde a `(27,0,0)`, `id=28` a `(0,1,0)`, `id=812` a `(0,0,1)` y último ID `(27,28,47)`. Centro de `(0,0,0)` es `(242430,8196190,3055)` y volumen nominal es `20×20×10=4.000 m³`. Exit code 0. Esto comprueba la fórmula especificada, no un grid ya producido.

Evaluación: **CORRECTA, H0**. Fórmula, recorrido, unicidad esperada, índices y centro de ejemplo son consistentes. La dependencia de IDs respecto de `nx/ny` queda documentada; geometría/versionado deben guardarse. `P2_GRID` continúa pendiente.

### P2.7 — tratamiento conceptual de celdas de borde

Microteoría y opciones presentadas: celdas completas uniformes conservan dimensiones/volumen nominal, pero pueden extenderse fuera del envolvente de sondajes; celdas parciales ajustan el borde pero requieren dimensiones y volumen por celda; recortar extremos puede perder cobertura. La topografía ausente impide determinar fracción de roca.

Evidencia registrada para la pregunta: con 20×20×10 m, volumen nominal 4.000 m³; límite candidato `(242980,8196760,3530)` frente a máximos de trayectoria aproximados `(242975,603,8196745,780,3524)`. No hay grid generado ni fracción de roca calculada.

Respuesta literal P2.7:

> A. Mantengo celdas completas de 20 × 20 × 10 m con volumen nominal uniforme de 4,000 m³ y documento que parte del borde queda fuera de la envolvente de los sondajes, sin llamarlo volumen de roca.
>
> Evidencia del escenario: la sección 7 de docs/exam/T2_M01B/02_SCENARIO_EXAM_M01B.md indica que nominal_volume es el volumen de la celda, no el volumen neto de roca, y que este último requiere una regla de ocupación aparte (que aquí no existe, porque falta la topografía). Los márgenes que agrega el redondeo son pequeños frente al tamaño de celda: ≈ 2.6 m (X mín), 0.5 m (Y mín), 9.5 m (Z mín), 4.4 m (X máx), 14.2 m (Y máx) y 6 m (Z máx), es decir, menos de una celda en cada cara.
>
> Ventaja: geometría regular y simple. Todas las celdas tienen el mismo dx/dy/dz y volumen, los centros siguen la fórmula origen + (índice + 0.5)·tamaño y las pruebas de centros, esquinas y volúmenes son directas. Ninguna estación de trayectoria queda fuera de la malla.
>
> Limitación: las celdas de borde incluyen volumen sin perforación, que no debe interpretarse como roca con soporte; esas celdas deberán quedar UNKNOWN o marcadas en P4. El volumen nominal total (38,976 × 4,000 m³) no es volumen de roca: en la parte superior puede incluir aire, y eso solo se resolverá con topografía en P3 (B09 sigue bloqueado).

Verificación de solo lectura con 270 estaciones: márgenes del límite candidato respecto del envolvente de trayectoria: X mín 2,6325 m, X máx 4,3974 m; Y mín 0,4797 m, Y máx 14,2204 m; Z mín 9,5305 m, Z máx 6,0000 m. No hay estaciones fuera del envolvente. Conteo conceptual 38.976; volumen nominal de celda 4.000 m³; total nominal aritmético 155.904.000 m³. Este total es volumen geométrico de celdas, no volumen de roca. Exit code 0.

Evaluación: **CORRECTA, H0**. La elección de celdas completas y la distinción entre volumen nominal y volumen de roca coinciden con la sección 7 del escenario. El estado UNKNOWN/flag para bordes sin soporte se propone para P4, no se generó. B09 y el gate P2_GRID siguen sin resolverse.

### P4.1 — regla conceptual de asignación categórica

Pregunta conceptual registrada: seleccionar principio de soporte cuando P4 sea viable, sin fijar números no validados. Alternativas: (A) composite más cercano dentro de distancia máxima; (B) mayoría de k composites más cercanos, con desempate/soporte explícitos; (C) asignar solo si los composites dentro de un radio aprobado concuerdan, si no `UNKNOWN`. Evidencia disponible: composites con XYZ, códigos observados y procedencia; AIR se mantiene en revisión; no hay superficies interpretadas, topografía ni umbral aprobado. B09 y P2_GRID siguen bloqueados, por lo que no se clasifica ningún bloque.

Respuesta literal P4.1:

> C. Asigno un código solo si todos los composites dentro de un radio aprobado concuerdan; si hay conflicto o soporte insuficiente, el bloque queda UNKNOWN con causa (CONFLICTING_CODES o INSUFFICIENT_SUPPORT). El radio no lo fijo todavía porque no hay un umbral validado.
>
> Evidencia del repositorio: es coherente con lo que registré en P1.3 y P1.4 (T2_M01B_PLAN_G04.md). Los 82 contactos internos de lithology.csv son evidencia observada, pero no hay superficies de contacto interpretadas que validen su continuidad, y en zonas con códigos en disputa decidí dejar UNKNOWN en lugar de propagar un código. m01b_composites.csv tiene 5,332 composites con XYZ, lith_code y procedencia, y 57 sample_id repetidos en dos segmentos: con la regla de concordancia esos segmentos no pesan doble en ninguna votación, porque no se cuentan votos.
>
> Ventaja: no se inventa ninguna frontera ni se elige un código por mayoría donde los datos se contradicen. Cada bloque asignado tiene soporte unánime, y cada UNKNOWN tiene una causa auditable, con composite_id de soporte y distancia, como se definió en P1.5.
>
> Limitación: la cobertura será menor que con vecino más cercano o mayoría. Cerca de cada contacto (sobre todo en las 31 transiciones REG→DIO) y en las zonas donde los collars están a 60–92 m, muchos bloques quedarán UNKNOWN. El resultado depende mucho del radio: uno grande aumenta los conflictos y uno pequeño aumenta el soporte insuficiente, por lo que habrá que comparar al menos dos radios cuando se autorice la implementación.

Comprobación de lectura ejecutada con `.venv` sobre `data/processed/m01b_composites.csv`: `composites 5332`, todas con XYZ; códigos `AIR`, `BRX`, `DIO`, `POR`, `REG`; `repeated_sample_ids 57`, `exactly_twice 57`, `max_count 2`; una fila AIR (`CR-C02-002_0001`, fuente `CR-C02-002-A0001`). La semántica de AIR permanece según P1.2; no se clasifica como estado topográfico.

Evaluación: **CORRECTA, H0**. La regla de concordancia evita resolver con una mayoría arbitraria y conserva incertidumbre con causa. Como no hay votación, los segmentos derivados no duplican votos; aun así, al definir métricas de soporte debe distinguirse número de segmentos geométricos de número de mediciones originales, conservando sus códigos segmentados al contacto. La comparación de radios queda pendiente y no se presenta como prueba ejecutada. No hay asignación de bloques; P4_GEO_ASSIGN no aprobado.

### P4.2 — métrica de soporte para ensayes partidos

Pregunta conceptual siguiente: los 57 `sample_id` repetidos corresponden a una medición analítica partida geométricamente; se presentan alternativas para (A) conservar segmentos pero contar fuentes únicas y tratar códigos distintos de una fuente como conflicto, (B) escoger solo el segmento más cercano por fuente, o (C) excluir ensayes partidos del soporte. Se requiere elegir con evidencia, ventaja y limitación. Sin asignación ejecutada, sin radio definido y sin autorización de código.

Respuesta literal P4.2:

> A. Conservo ambos segmentos como soporte espacial y litológico, cuento support_count por sample_id único (no por segmento) y marco CONFLICTING_CODES/UNKNOWN si una misma fuente aparece con códigos distintos dentro del soporte relevante.
>
> Evidencia del repositorio: en m01b_composites.csv hay 57 sample_id repetidos exactamente dos veces; todos son ensayes de 2 m partidos 1 m + 1 m por un contacto de lithology.csv (1.081 % de los 5,275 ensayes, en 35 sondajes). El lith_code de cada segmento proviene del registro litológico y no del ensaye, así que cada mitad es una observación litológica válida en su posición. Lo que comparten es la misma medición analítica (cu_pct heredado), que en T2 no se usa para estimar ley a bloques.
>
> Ventaja: se conserva la evidencia espacial a ambos lados del contacto, que es justo donde la asignación es más delicada, sin inflar el número de fuentes analíticas independientes. Es coherente con P4.1: un sample_id partido dentro del radio de un bloque implica códigos distintos, y por lo tanto el bloque queda UNKNOWN por CONFLICTING_CODES en lugar de tomar un lado arbitrariamente.
>
> Limitación: hay que guardar y probar dos métricas distintas (segmentos y sample_id únicos), lo que añade complejidad. Además, cerca de esos 57 contactos aumentarán los bloques UNKNOWN. Contar por sample_id tampoco resuelve que los composites de un mismo sondaje estén correlacionados entre sí: el soporte sigue concentrado a lo largo de cada trayectoria.

Verificación independiente sobre `m01b_composites.csv`: 5.332 composites; 57 fuentes repetidas exactamente dos veces (114 filas); las 57 parejas son tramos de 1 m con el mismo `cu_pct` y distinto `lith_code`, distribuidas en 35 sondajes; 57/5.275 = 1,0805687 % (≈1,081 %). Las transiciones de esas parejas coinciden con conteos previamente registrados. Exit code 0. La verificación demuestra la estructura de la tabla, no independencia ni validez geológica.

Evaluación: **CORRECTA, H0**. Contar fuentes únicas y preservar ambos segmentos geométricos evita inflar soporte analítico y perder el lado litológico del contacto. Correlación entre composites del mismo sondaje permanece como limitación no resuelta. No se fijó radio ni se calcularon asignaciones.

### P4.3 — análisis de sensibilidad de radios

Microteoría: radios pequeños tienden a aumentar `UNKNOWN/INSUFFICIENT_SUPPORT`; radios grandes pueden aumentar cobertura y conflictos. Comparar sensibilidad exige reportar cobertura, conflictos, distancia y fuentes únicas, sin escoger solo el radio que maximice asignaciones.

Evidencia: 5.332 segmentos, 5.275 `sample_id` únicos (57 ensayes partidos), distancia XY a collar vecino 20–92,195 m (mediana 60 m). Tamaño candidato 20×20×10 m, no grid aprobado; no hay radio validado, topografía ni asignación ejecutada.

La respuesta pendiente debe elegir: (A) al menos dos radios motivados por la distribución observada y comparar métricas; (B) escenarios geométricos derivados de fracciones de la diagonal de celda, declarados no validados; (C) posponer escenarios hasta disponer de grid/topografía. No se proponen números validados ni se ejecuta código.

Respuesta literal P4.3:

> A. Compararía al menos dos radios motivados por la distribución de distancias observada y, para cada uno, reportaría bloques ASSIGNED/UNKNOWN (separando CONFLICTING_CODES de INSUFFICIENT_SUPPORT), distancia al soporte y número de sample_id únicos. Elegiría por el balance entre cobertura y ambigüedad, no por maximizar asignaciones.
>
> Evidencia del repositorio: la distancia XY al collar más cercano va de 20 a 92.195 m (mediana 60 m) y la distancia 3D mínima entre trayectorias tiene mediana de 20 m (outputs/tables/m01_validacion_espacial.csv). Con esa distribución, como escenarios de prueba (no umbrales validados) compararía un radio cercano a 20 m, que solo alcanza sondajes próximos, y otro cercano a 30 m (la mitad de la mediana en collar), que alcanza el sondaje vecino en zonas típicas. Como referencia geométrica, la media diagonal de una celda de 20 × 20 × 10 m es 15 m, así que un radio menor que eso dejaría sin soporte incluso parte de la propia celda atravesada. El conteo usaría las 5,275 fuentes únicas, no los 5,332 segmentos (P4.2).
>
> Ventaja: los radios no son arbitrarios: se relacionan con el espaciamiento real de los sondajes. Las métricas permiten ver con números cuánto se gana en cobertura y cuánto aumentan los conflictos al ampliar el radio, en vez de elegir el que "llena" más el modelo.
>
> Limitación: la comparación muestra el comportamiento de la regla, pero no valida geológicamente ningún radio. Las distancias en collar no representan el espaciamiento a profundidad, y el resultado dependerá de la malla y de la topografía, que siguen pendientes (P2_GRID y B09). Los valores de 20 y 30 m son candidatos de prueba, no parámetros aprobados.

Evaluación: **CORRECTA, H0**. La respuesta plantea un análisis de sensibilidad y declara 20/30 m como escenarios no validados. La distancia XY de collar y la distancia 3D mínima son métricas distintas; ninguna valida por sí sola el radio a profundidad. La media diagonal geométrica es `sqrt(20²+20²+10²)/2 = 15 m`; sirve de referencia de escala, no garantiza que todos los puntos de una celda atravesada tengan soporte. Se conserva el recuento por `sample_id` de P4.2. Sin asignación ejecutada ni radio aprobado.

### P4.4 — soporte correlacionado por sondaje

Respuesta literal del estudiante:

> A. Reporto por bloque tanto n_sample_ids únicos como n_holes distintos, sin fijar ahora un mínimo de asignación; ambos quedan como evidencia de soporte junto con la distancia (P1.5).
>
> Evidencia del repositorio: los 5,275 sample_id únicos están distribuidos en solo 35 sondajes, con 115 a 218 ensayes por sondaje, así que el soporte está muy concentrado a lo largo de cada trayectoria. Con celdas de 20 × 20 × 10 m y collars separados al menos 20 m (mediana 60 m), lo esperable es que muchas celdas sean atravesadas por un solo sondaje: un bloque podría tener unos 5 compósitos de 2 m (dz = 10 m) y aun así n_holes = 1.
>
> Ventaja: se distinguen dos tipos de soporte, cuánta información hay y de cuántos lugares independientes proviene. Esto permite reconocer en P5 si un bloque asignado por concordancia descansa en un único sondaje, que no aporta evidencia de continuidad lateral, o en varios. Además, las métricas quedan disponibles para fijar un mínimo justificado después de comparar radios (P4.3).
>
> Limitación: son dos columnas más que hay que calcular y probar, y ninguna mide continuidad geológica. n_holes no tiene en cuenta que dos sondajes pueden ser casi paralelos o converger (el par más cercano está a 5.979 m), por lo que dos sondajes no siempre son dos observaciones independientes. El mínimo de asignación sigue sin fijarse.

Verificación de lectura sobre `assay.csv` y `m01b_composites.csv`: 5.275 assays y `sample_id` únicos en 35 sondajes, 115–218 assays/hole; composites 5.332 filas, 5.275 fuentes únicas y 35 holes. El cálculo previo de collar XY vecino dio 20–92,195 m (mediana 60 m), mientras que la distancia mínima 3D entre trayectorias incluye acercamiento en profundidad y su mínimo es 5,979 m; son medidas distintas. No se ha construido la malla ni calculado qué bloques atraviesa cada hole.

Evaluación: **CORRECTA, H0**. Registrar `n_sample_ids` y `n_holes` por separado, junto con distancia, distingue cantidad de fuentes analíticas de número de trayectorias, sin imponer un mínimo no validado. La concentración lineal y posible correlación por sondaje siguen siendo limitaciones; la expectativa de muchos bloques con un solo hole es plausible pero no se ha medido por bloque. No se ejecutaron asignaciones.

### P4.5 — política para composites con código `AIR`

Microteoría: `AIR` aparece en la tabla litológica, pero su significado no está documentado y P1.2 lo conserva como código observado separado, `REVIEW/UNKNOWN`, fuera de la extensión volumétrica y sin traducirlo a `topo_status=AIR`. Incluirlo como soporte para dominios rocosos podría contaminar una asignación; eliminarlo sin registro perdería trazabilidad. Excluirlo de los dominios de roca y mantener su procedencia permite evitar ambas inferencias hasta obtener diccionario/topografía.

Evidencia/faltantes: solo hay una fila AIR (`CR-C02-002_0001`, MD 0–2 m), proveniente de `lithology.csv`, inmediatamente sobre REG desde 2 m. No existe diccionario que defina AIR ni topografía oficial. No hay regla de elegibilidad implementada ni asignaciones.

Opciones conceptuales: (A) excluir AIR como soporte de dominios rocosos, conservarlo con `REVIEW/UNKNOWN` e indicar no participación, sin inferir `topo_status=AIR`; (B) incluir el código literal como dominio candidato distinto de estado topográfico, marcando para revisión cualquier uso; (C) omitirlo de salida de asignación, aceptando perder trazabilidad.

Pregunta P4.5 pendiente: elegir A/B/C y justificar con evidencia, ventaja y limitación. No cambia composites ni asigna bloques; `P2_GRID`, `P4_GEO_ASSIGN` y B09 siguen bloqueados.

Respuesta literal P4.5:

> A. Excluyo el composite AIR como soporte de dominios rocosos, lo conservo con REVIEW/UNKNOWN en la tabla y registro explícitamente que no participó en la asignación; no infiero topo_status = AIR.
>
> Evidencia del repositorio: es un único composite, CR-C02-002_0001 (MD 0–2 m, junto al collar, Cu = 0), seguido de REG desde 2 m. Su código proviene de lithology.csv, pero no existe en el repositorio un diccionario que lo defina ni una topografía verificada (B09 bloqueado). Es coherente con P1.2, donde decidí preservarlo separado y excluirlo de la extensión volumétrica de dominios, y con P1.5, donde exigí registrar la procedencia de cada asignación.
>
> Ventaja: se evita que un código de significado incierto actúe como dominio rocoso o genere conflictos artificiales con REG en los bloques cercanos al collar de CR-C02-002, y la exclusión queda trazable (se sabe qué composite se dejó fuera y por qué).
>
> Limitación: si AIR resultara ser roca (por ejemplo, un tramo sin recuperación), se pierde 2 m de soporte en la parte superior de ese sondaje, y los bloques cercanos podrían quedar con menos soporte o UNKNOWN. El significado real del código solo se resolverá con una definición oficial o con la topografía en P3.

Verificación de lectura: una fila AIR (`CR-C02-002_0001`, MD 0–2 m, Cu 0), fuente `lithology.csv`; el siguiente intervalo composite es REG desde MD 2 m. No se encontró diccionario oficial ni topografía; evidencia previa mantiene B09 bloqueado. Evaluación: **CORRECTA, H0**. Coherente con P1.2 y P1.5; AIR se conservaría trazable, marcado para revisión y sin participación en dominios rocosos, sin inferir `topo_status`. No se modificó la tabla ni se asignó bloque.

### P4.6 — geometría usada para medir soporte

Respuesta literal del estudiante:

> A. Mido la distancia 3D entre el centro del bloque y el punto medio del composite (mid_x, mid_y, mid_z), aplicando un radio máximo aprobado y la regla de concordancia de códigos (P4.1), contando soporte por sample_id único (P4.2).
>
> Evidencia del repositorio: en m01b_composites.csv los composites miden como máximo 2 m (5,188 de 2 m y 144 parciales más cortos), así que cualquier punto del segmento está a 1 m o menos de su punto medio. Por desigualdad triangular, la diferencia entre la distancia al punto medio y la distancia mínima al segmento es como máximo 1 m, frente a radios de prueba cercanos a 20 y 30 m (P4.3), es decir, ≤ 5 %. Todas las filas tienen mid_x/mid_y/mid_z calculados con el positioning de M01.
>
> Ventaja: el cálculo es simple, rápido y fácil de probar con casos controlados (distancia punto-punto), y es coherente con los radios definidos en P4.3. Cada composite aporta un único punto, sin decisiones adicionales sobre segmentos parciales.
>
> Limitación: un composite que pasa justo por el borde del radio puede quedar dentro o fuera por menos de 1 m de diferencia, y los parciales cortos se representan igual que uno de 2 m. Tampoco considera directamente si el segmento atraviesa la celda: un bloque cruzado por un sondaje quedaría siempre dentro del radio, pero la regla no lo distingue de uno cercano. Si en P5 aparecen casos límite, se podría comparar con la distancia al segmento (opción B).

Verificación de lectura sobre `m01b_composites.csv`: 5.332 filas; 5.188 de 2 m y 144 parciales; longitud máxima 2 m; todas tienen `mid_x/mid_y/mid_z`. Para segmentos de longitud ≤2 m, distancia midpoint–segmento ≤1 m; esto es 5 % de 20 m y 3,33 % de 30 m. Evaluación: **CORRECTA, H0**. La elección es simple y las limitaciones están identificadas. Matiz: si un segmento atraviesa una celda 20×20×10 m, hay un punto del segmento a ≤15 m del centro; su punto medio puede estar hasta 1 m más lejos, de modo que queda dentro de radios 20/30 m, pero no necesariamente de un radio inferior a 16 m. No se ha calculado soporte ni se ha fijado radio.

### P4.7 — casos límite del umbral de distancia

Respuesta literal P4.7:

> Acepto la precisión de P4.6: lo que afirmé sobre los bloques atravesados por un sondaje solo vale para radios de 16 m o más, condición que cumplen los escenarios de prueba de 20 y 30 m.
>
> A. Aplico estrictamente distance <= radio, guardo la distancia de cada fuente en la salida y reviso la estabilidad de la asignación al comparar radios en P5.
>
> Evidencia del repositorio: la diferencia máxima entre la distancia al punto medio y la distancia al segmento es 1 m, porque ningún composite supera 2 m (5,188 de 2 m y 144 parciales en m01b_composites.csv). Los dos radios de prueba de P4.3 (≈ 20 y ≈ 30 m) difieren en 10 m, así que la comparación entre ellos ya captura una sensibilidad mucho mayor que el error geométrico de 1 m. Además, en P1.5 decidí guardar la distancia al soporte por bloque, por lo que los casos cercanos al umbral se pueden identificar después sin otra regla.
>
> Ventaja: la regla es simple, determinista y fácil de probar (un caso justo en el umbral, uno a 0.5 m dentro y uno a 0.5 m fuera). No introduce una tolerancia arbitraria que no está validada, y la distancia guardada permite auditar cualquier caso límite.
>
> Limitación: una fuente a menos de 1 m del umbral puede entrar o quedar fuera según se mida al punto medio o al segmento, y eso puede cambiar un bloque de ASSIGNED a UNKNOWN (o al revés). Si en P5 la proporción de casos límite resulta importante, habría que aplicar la prueba centro–segmento (opción C) en esos casos.

Evaluación: **CORRECTA, H0**. Se acepta la condición para radios ≥16 m; los escenarios de 20/30 m la cumplen, aunque no son radios aprobados. La cota geométrica de ≤1 m no significa que comparar radios separados por 10 m capture todos los cambios de clasificación; la respuesta mantiene la sensibilidad al punto medio como limitación y propone revisar estabilidad en P5. `distance <= radio` y casos dentro/en/fuera son reglas reproducibles; guardar distancia por fuente permite auditar. Sin radio fijado ni asignación ejecutada.

### P4.8 — precedencia del estado topográfico

Respuesta literal:

> A. Asigno litología solo a bloques con topo_status = ROCK confirmado; los bloques AIR, OUTSIDE_TOPO_COVERAGE y TOPO_UNKNOWN quedan sin dominio, con su causa registrada (assignment_status NOT_APPLICABLE para AIR y UNASSIGNED con causa topográfica para los otros dos).
>
> Evidencia del escenario: en la etapa P4 de docs/exam/T2_M01B/02_SCENARIO_EXAM_M01B.md se pide la "prioridad de AIR, OUTSIDE_TOPO_COVERAGE, TOPO_UNKNOWN sobre una asignación geológica automática", y la sección 7 advierte que un bloque AIR no es un bloque de roca UNKNOWN y que no deben confundirse en tabla ni visualización. En el repositorio no hay topografía (B09 RECOVERY_BLOCKED), y la cota superior provisional de 3530 m está por encima de varios collars (rango 3288–3524 m), por lo que parte del grid candidato podría ser aire.
>
> Ventaja: se evita asignar litología a celdas que podrían estar sobre la superficie o fuera de la cobertura, y se separan claramente las causas: no es roca, no se sabe si es roca, o es roca sin soporte suficiente. Es coherente con P1.2 y P4.5, donde no inferí topo_status a partir del código AIR.
>
> Limitación: mientras B09 siga bloqueado, todos los bloques serían TOPO_UNKNOWN, así que con esta regla no se asignaría litología a ningún bloque. Los bloques PARTIAL (cortados por la superficie) también quedarían sin dominio, aunque tengan una parte de roca con soporte; para incluirlos haría falta una regla de fracción de ocupación que no está definida. Por eso, la implementación de P4 depende de que el docente entregue la topografía o autorice explícitamente otro tratamiento.

Evaluación: **CORRECTA, H0**. El escenario da prioridad a `AIR`, `OUTSIDE_TOPO_COVERAGE` y `TOPO_UNKNOWN` sobre asignación automática, y separa explícitamente `AIR` de roca `UNKNOWN`. `NOT_APPLICABLE` para `AIR` y `UNASSIGNED` con causa topográfica para los otros dos estados hacen auditable esa distinción. La falta de topografía impide calcular estados; no se ejecutó clasificación. `PARTIAL` queda pendiente de una regla de ocupación. Sin asignación litológica ni aprobación de `P4_GEO_ASSIGN`.

### P4.9 — tratamiento de bloques PARTIAL

Respuesta literal:

> A. Dejo los bloques PARTIAL sin dominio (assignment_status UNASSIGNED, causa PARTIAL_TOPO) hasta definir y validar una regla de ocupación; como camino futuro, esa regla podría ser la de la opción C (fracción de roca registrada y umbral aprobado con análisis de sensibilidad).
>
> Evidencia del escenario y del repositorio: la sección 7 de docs/exam/T2_M01B/02_SCENARIO_EXAM_M01B.md indica que nominal_volume es volumen de la celda y no volumen neto de roca, y que para determinar este último se requiere una regla o fracción de ocupación aparte, que si no se implementó debe declararse. En el repositorio no hay topografía (B09 RECOVERY_BLOCKED) ni fracciones calculadas, así que no hay forma de saber qué parte de cada celda es roca. Es coherente con lo que registré en P4.8, donde señalé que PARTIAL quedaría sin dominio por esa misma falta de regla.
>
> Ventaja: no se asigna litología a volumen que podría ser aire, no se confunde el volumen nominal de 4,000 m³ con volumen de roca, y la causa PARTIAL_TOPO distingue estos bloques de los UNKNOWN por falta de soporte geológico.
>
> Limitación: justo bajo la superficie, donde los sondajes empiezan y suele haber soporte (por ejemplo, REG cerca de los collars), muchos bloques quedarían sin dominio, y el modelo tendría una "capa vacía" en el contacto con la topografía. Para recuperar esos bloques hace falta la topografía oficial, calcular la fracción de roca por celda y aprobar un umbral con evidencia.

Evaluación: **CORRECTA, H0**. La sección 7 separa `nominal_volume` del volumen neto de roca y exige declarar una regla de ocupación si se calcula este último. Sin topografía ni fracciones, dejar `PARTIAL` como `UNASSIGNED` con causa `PARTIAL_TOPO` evita atribuir litología o volumen de roca sin evidencia. La propuesta de fracción, umbral aprobado y sensibilidad es futura, no un parámetro ya definido. La pérdida de bloques con soporte cerca de superficie es una limitación pertinente. No se calcularon ocupaciones ni se implementó asignación.

### P4.10 — dependencias y orden de evaluación

Respuesta literal:

> A. Primero resuelvo B09: obtener la topografía oficial y verificar coordenadas, CRS/datum (si constan), unidades, elevaciones y cobertura frente a los collars. Luego cierro P2_GRID (ajustando la cota superior y nz con la superficie real), apruebo las reglas, parámetros (radios de prueba 20/30 m) y pruebas de P4, y finalmente paso su gate de implementación.
>
> Evidencia del estado actual: B09 está en RECOVERY_BLOCKED porque no hay topografía en el repositorio (8 archivos del manifest, ninguno topográfico); la cota superior de 3530 m y nz = 48 son provisionales, basados en los collars (3288–3524 m). En P4.8 y P4.9 definí que solo los bloques ROCK reciben litología y que PARTIAL queda UNASSIGNED, así que sin topo_status no hay ningún bloque elegible. Los radios de 20 y 30 m son escenarios de prueba, no parámetros aprobados.
>
> Ventaja: cada etapa se implementa sobre una base verificada. La malla no tendrá que rehacerse cuando llegue la superficie, y las distancias y estados de P4 no se calcularán sobre celdas que podrían ser aire. El orden respeta las dependencias reales: topografía → grid → reglas → asignación.
>
> Limitación: mientras no llegue la topografía, ninguna etapa con código (P2_GRID, P3, P4, P6) puede avanzar, y el examen queda en plan conceptual. Por eso he consultado al docente: si no puede entregar la topografía y autoriza explícitamente otro tratamiento (por ejemplo, generar la malla con todos los bloques en TOPO_UNKNOWN), presentaré esa autorización para revisar este orden.

Evaluación: **CORRECTA, H0**. El orden B09 → `P2_GRID` → reglas/parámetros/pruebas → gate P4 respeta dependencias y evita calcular estados topográficos o soporte sobre geometría no verificada. La evidencia mantiene cota 3530 m y `nz=48` provisionales; radios 20/30 m son escenarios, no parámetros aprobados. La consulta al docente no constituye autorización recibida: solo una respuesta explícita permitiría reconsiderar el tratamiento. Matiz: esto bloquea las etapas de implementación dependientes de topografía, pero no el trabajo conceptual; no se ha implementado ni autorizado código.

### P5.1 — validación computacional y validación minera

Respuesta literal:

> A. Exijo dos evidencias separadas, cada una con su propia condición de aceptación.
>
> Computacional: invariantes y reproducibilidad, por ejemplo 38,976 block_id únicos de 0 a 38,975; índices i, j, k coherentes con block_id = i + j·nx + k·nx·ny; centros según origen + (índice + 0.5)·tamaño; volumen nominal de 4,000 m³ en todas las celdas; las 270 estaciones dentro del envolvente; reglas de asignación probadas con casos controlados (concordancia, conflicto, sin soporte, umbral del radio, AIR excluido, TOPO_UNKNOWN sin dominio), y reejecución con los mismos inputs y parámetros que da el mismo resultado (mismo hash).
>
> Minera: una revisión independiente de cobertura y bloques sin soporte, contactos y extrapolación, proporción y ubicación de UNKNOWN por causa, comparación de radios de 20/30 m, y relación aire/roca frente a la topografía.
>
> Condición: acepto el resultado como READY_FOR_REVIEW solo si todas las invariantes computacionales pasan (o una falla se corrige o se aprueba explícitamente un alcance parcial), y la revisión minera queda registrada con hallazgos ERROR/WARNING/INFO y sus limitaciones. Aun así no declaro MINING_VALIDATED.
>
> Evidencia del escenario: la etapa P5 de docs/exam/T2_M01B/02_SCENARIO_EXAM_M01B.md obliga a distinguir comprobación computacional (estructura, IDs, centros, volúmenes, reglas reproducibles, reejecución) de validación minera (soporte real, tamaño de bloque, aire/roca real, contactos, extrapolación, incertidumbres). Indica que si falla una invariante importante no se declara READY_FOR_REVIEW, y que el gate P5_VALIDATION no equivale a validación geológica aunque la suite esté verde. Lo mismo pasó en B08: 47 pruebas PASS mostraron consistencia computacional, pero no validación geológica.
>
> Ventaja: cada tipo de evidencia responde a una pregunta distinta (¿el código hace lo que dice la regla? / ¿la regla tiene sentido para estos datos?), y ninguna puede ocultar las fallas de la otra.
>
> Limitación: la validación minera depende de criterio y no tiene un PASS automático. Sin topografía (B09) ni una interpretación geológica de referencia, solo se podrá documentar la coherencia y las incertidumbres, no confirmar que la asignación es geológicamente correcta. Además, todavía no hay malla ni asignación para validar.

Evaluación: **CORRECTA, H0**. La separación y las condiciones de aceptación siguen el escenario; una suite verde no sustituye la revisión minera y `MINING_VALIDATED` permanece distinto. El ejemplo de 38.976 bloques, IDs 0–38.975 y volumen nominal 4.000 m³ corresponde a la malla candidata, no a geometría aprobada; la topografía puede cambiar extensión y `nz`. Las 270 estaciones dentro del envolvente candidato se verificaron antes, pero no determinan aire/roca. El hash es un criterio de reproducibilidad si la serialización y metadatos también son deterministas. B08 demuestra que 47 pruebas computacionales PASS no validaron geología. No existe malla ni resultado P5 actual.

### P5.2 — priorización de diagnósticos y hallazgos

Respuesta literal:

> A. Defino los criterios antes de ver los resultados, ligados a requisitos ya aprobados: ERROR = una invariante computacional fallida (IDs duplicados, índices o centros incorrectos, volumen no positivo, estación fuera del envolvente, regla que no reproduce su caso controlado, reejecución distinta); WARNING = limitación o soporte bajo que restringe el alcance sin ser error (bloques UNKNOWN por INSUFFICIENT_SUPPORT o CONFLICTING_CODES, n_holes = 1, casos a menos de 1 m del radio, PARTIAL_TOPO, AIR en revisión); INFO = contexto descriptivo (conteos por estado topográfico y por código, distribución por profundidad, distancias). No fijo umbrales mineros de cobertura ni de UNKNOWN.
>
> Evidencia del escenario y del repositorio: la etapa P5 de docs/exam/T2_M01B/02_SCENARIO_EXAM_M01B.md pide clasificar hallazgos ERROR/WARNING/INFO con criterios documentados, sugiere diagnósticos sin prescribir números (celdas totales, estados topográficos, clasificadas/UNKNOWN, recuentos por código, distancias, áreas sin cobertura, secciones, profundidad y casos cerca de contactos) e indica que si falla una invariante importante no se declara READY_FOR_REVIEW. En M01 ya usamos esa misma convención: el validator de T1 clasificó 0 ERROR, 15 WARNING y 11,047 INFO (outputs/tables/m01_validation_summary.csv).
>
> Ventaja: la clasificación no depende de cómo se vea el resultado, sino de reglas fijadas antes, lo que evita ajustar el criterio para que el modelo "pase". Solo un ERROR bloquea READY_FOR_REVIEW, mientras que los WARNING quedan como límites explícitos del alcance.
>
> Limitación: sin umbrales mineros validados, un modelo con muchos UNKNOWN podría quedar sin ningún ERROR y técnicamente aprobado en lo computacional, aunque sea poco útil. Decidir si esa cobertura es aceptable sigue siendo un juicio minero que debe declararse en la revisión, no un PASS automático.

Verificación: se sumó la columna `finding_count` del CSV mediante lectura local: 91 reglas (77 clasificadas ERROR, 10 WARNING, 4 INFO); los totales son 0 ERROR, 15 WARNING y 11.047 INFO. La evidencia del estudiante es correcta. Evaluación: **CORRECTA, H0**. Criterios previos trazables; `UNKNOWN`/soporte bajo se reportan como limitación para la revisión minera, no como defecto computacional automático. No se fijan umbrales de cobertura ni se ejecutan diagnósticos P5.

### P5.3 — interpretación de cobertura UNKNOWN

Respuesta literal recibida en dos partes:

> A. Desgloso los UNKNOWN por causa (INSUFFICIENT_SUPPORT, CONFLICTING_CODES, causas topográficas como TOPO_UNKNOWN/PARTIAL_TOPO, y AIR en revisión) y por ubicación (secciones por coordenada, profundidad y periferia de la malla), y los contrasto con soporte (n_sample_ids, n_holes), distancia al soporte, cercanía a contactos, estado topográfico y comparación de radios de 20/30 m. Documento qué indica cada diagnóstico y no acepto ni rechazo el modelo por un porcentaje global.
>
> Criterios P4/P5: en P1.4 y P4.1 definí que UNKNOWN debe llevar una causa identificada, y en P1.5, P4.2 y P4.4 que cada bloque guarde distancia, fuentes y número de sondajes, justamente para poder hacer este desglose. La etapa P5 del escenario sugiere revisar clasificadas/UNKNOWN, distancias, áreas sin cobertura, secciones, distribución por profundidad y casos cerca de contactos.
>
> Criterio de interpretación: un UNKNOWN concentrado en la periferia o entre sondajes a 60–92 m, por INSUFFICIENT_SUPPORT, indica cautela apropiada por falta de datos. Concentrado en contactos frecuentes (REG→DIO) por CONFLICTING_CODES, refleja incertidumbre real del contacto. Pero si aparece UNKNOWN en bloques atravesados por un sondaje con un único código, o si el cambio de 20 a 30 m altera mucho la clasificación, eso exige revisar el método. Reducir el radio no disminuye
>
> Completo P5.3 (respuesta A):
>
> Frase completa: reducir el radio no disminuye los UNKNOWN; al contrario, aumenta los de causa INSUFFICIENT_SUPPORT, porque menos composites quedan dentro del radio. Cambiar a vecino más cercano sí los reduce, pero porque deja de exigir concordancia y puede cruzar contactos no validados (P1.3, P4.1), no porque mejore el soporte.
>
> AIR separado de UNKNOWN: el composite AIR (CR-C02-002_0001) no es un UNKNOWN de roca. Según P4.5 queda excluido del soporte con REVIEW/UNKNOWN como marca del código, y un bloque con topo_status = AIR queda assignment_status NOT_APPLICABLE (P4.8). En el desglose lo reporto en una categoría aparte, fuera del porcentaje de UNKNOWN de roca.
>
> Precisión aceptada: un UNKNOWN en un bloque atravesado por un sondaje no demuestra por sí solo un fallo. Solo indicaría revisar el método si el bloque es ROCK elegible, tiene soporte dentro del radio con un único código y no existe otra causa registrada (topográfica, conflicto o AIR).
>
> Ventaja: el desglose distingue falta de datos, conflicto real de códigos, condición topográfica y posible falla de la regla, y muestra dónde actuar (más perforación, interpretación de contactos o ajuste justificado) sin forzar la cobertura.
>
> Limitación: requiere criterio y no da un PASS automático. Mientras B09 siga bloqueado, la causa topográfica dominará todos los bloques y ocultará las demás, y sin una interpretación geológica de referencia no puedo confirmar si un conflicto refleja la geología real o solo la regla.

Evaluación de primera respuesta completa: **PARCIAL, H1**. Se completan ventaja, limitación, separación de `AIR` y la condición para investigar bloques atravesados. `AIR` queda en categoría aparte, consistente con `NOT_APPLICABLE`/revisión, no como `UNKNOWN` de roca. Matiz técnico: al reducir el radio pueden aumentar casos `INSUFFICIENT_SUPPORT`, pero también desaparecer conflictos; el efecto neto depende de los datos. Vecino más cercano puede disminuir `UNKNOWN` al eliminar concordancia, pero no mejora soporte y puede cruzar contactos. La afirmación sobre predominio topográfico requiere condicionarse a una política alternativa autorizada; no hay distribución observada. Se solicitó precisar ambos matices.

Complemento literal:

> A. Ajusto los dos puntos:
>
> 1. Un radio menor tiende a aumentar los UNKNOWN por INSUFFICIENT_SUPPORT, porque quedan menos fuentes dentro del radio, pero también puede eliminar algunos CONFLICTING_CODES, porque un radio menor incluye menos códigos distintos (por ejemplo, deja fuera el otro lado de un contacto). El efecto neto sobre el total de UNKNOWN depende del resultado y solo se podrá medir comparando los radios de 20 y 30 m en P5 por causa, no por total.
>
> 2. Que la causa topográfica domine es una posibilidad condicionada: solo ocurriría si se generara la malla con todos los bloques en TOPO_UNKNOWN, bajo un tratamiento autorizado por el docente. No es una distribución verificada, porque hoy no existe malla ni asignación.
>
> Justificación: mantengo la tendencia esperada porque guía qué diagnósticos preparar (desglose por causa y por radio), pero sin presentarla como conclusión, coherente con P5.2: los criterios se fijan antes y los efectos se confirman con resultados reales.

Evaluación final: **CORRECTA, H0**. Distingue la tendencia para `INSUFFICIENT_SUPPORT` del efecto neto por posibles conflictos que desaparecen; plantea medirlo por causa al comparar escenarios 20/30 m. `TOPO_UNKNOWN` dominante queda condicionado a una política autorizada de malla, no como resultado actual. Radios no aprobados, sin malla/asignación ni análisis ejecutado.

### P6.1 — objetivo y capas del visualizador 3D

Respuesta literal:

> A. Diseño el visualizador como herramienta de auditoría: trayectorias y composites/contactos de control; la malla solo cuando P2_GRID esté aprobado; bloques coloreados por lith_code (REG, DIO, POR, BRX), sin colorear por Cu porque en T2 no se estima ley; estados UNKNOWN/UNASSIGNED (por causa) y NOT_APPLICABLE/AIR con colores o capas separadas y distinguibles de la roca asignada; topografía solo después de verificar su cobertura en P3; e incluyendo límites de la malla, ejes con unidades (m), leyenda y cortes/filtros por coordenada, estado y código.
>
> Evidencia y capacidades del repositorio: src/m01/visualizer.py ya genera con Plotly outputs/figures/m01_exploration_3d.html con collars, trayectorias e intervalos en XYZ, y en la T1 la figura declara que no hay topografía en el release. m01b_composites.csv tiene from/mid/to XYZ y lith_code para las 5,332 filas, así que los composites y contactos de control pueden añadirse sin otro cálculo. La malla candidata tendría 38,976 celdas, demasiadas para verlas todas a la vez sin ocultar el interior, por lo que los cortes y filtros son necesarios, no opcionales.
>
> Ventaja: permite auditar visualmente lo que se decidió en P1–P5: si los bloques asignados están cerca de su soporte, dónde se concentran los UNKNOWN por causa, cómo se comportan cerca de los contactos y, cuando exista, la relación con la superficie. Reutiliza la herramienta y el estilo ya probados en M01.
>
> Limitación: hoy solo se pueden mostrar sondajes y composites, porque no hay topografía, malla ni asignación. Con 38,976 celdas, el HTML puede ser pesado (el de M01 ya ocupa ≈ 5.7 MB) y los colores de los bloques pueden dar una falsa impresión de continuidad geológica, aunque se distingan los UNKNOWN. La visualización ayuda a revisar, pero no reemplaza la validación P5.

Verificación: `src/m01/visualizer.py` utiliza Plotly y construye collares, trayectorias, intervalos litológicos y dropdown entre litología y assay coloreado por Cu; `outputs/figures/m01_exploration_3d.html` mide 5.720.873 bytes; `m01b_composites.csv` tiene 5.332 filas con XYZ FROM/MID/TO y `lith_code`. Evaluación **CORRECTA, H0**. Diseño de auditoría y evitar color por Cu son coherentes con P6. No está demostrado que la vista actual permita filtros por coordenada/estado/código ni que los 38.976 bloques puedan renderizarse eficientemente. No hay topografía, malla ni asignación T2; no se eligió dependencia ni se implementó el visualizador.

### P6.2 — filtros, cortes y volumen renderizado

Respuesta literal:

> A. Conservo la tabla completa de bloques como fuente y en el visualizador filtro por lith_code y por estado (ASSIGNED, UNKNOWN por causa, UNASSIGNED, NOT_APPLICABLE), además de cortes por coordenada (nivel k, sección i o j). Solo renderizo la selección e indico en pantalla cuántos bloques se muestran y cuántos quedan ocultos por el filtro.
>
> Justificación con la malla candidata y las capacidades actuales: con 28 × 29 × 48 = 38,976 celdas, un corte en planta tiene 28 × 29 = 812 bloques, una sección por X 29 × 48 = 1,392 y una sección por Y 28 × 48 = 1,344, es decir, entre el 2 % y el 3.6 % de la malla. Es una carga pequeña comparada con lo que ya muestra visualizer.py, que con Plotly renderiza collars, trayectorias e intervalos litológicos y alterna capas con un menú (HTML actual de 5,720,873 bytes). Los filtros por bloque todavía no existen y habría que implementarlos y probarlos.
>
> Ventaja: la inspección es exacta y reproducible. Cada bloque mostrado es el bloque real de la tabla, sin muestreo ni reducción, y el conteo de ocultos deja claro que no se está omitiendo información del modelo, solo de la vista. Las secciones por i/j/k coinciden con los índices de P2.6, así que un bloque de la tabla se puede ubicar directamente en la vista.
>
> Limitación: si se selecciona un filtro grande (por ejemplo, todos los bloques de POR o todos los UNKNOWN), el render puede volver a ser pesado y tapar el interior. Además, ver por cortes exige recorrer varias secciones para entender la continuidad 3D. El rendimiento real no se ha medido porque la malla no está generada.

Evaluación: **CORRECTA, H0**. Aritmética de cortes confirmada con la malla candidata: `k` 812 (2,08 %), `i` 1.392 (3,57 %), `j` 1.344 (3,45 %). Conservar la tabla completa y señalar recuentos visibles/ocultos hace explícita la selección; limitación de filtros grandes y comprensión tridimensional por cortes es válida. El HTML M01 no prueba rendimiento del render de bloques. No existe malla, filtros ni perfil de rendimiento; gate `P6_VISUALIZER` no aprobado.

Enfoque P6 conceptual resultante: reutilizar Plotly ya disponible como opción base (sin instalar dependencia nueva), con pruebas/revisión pendientes del gate P6. Esto registra una dirección de diseño, no implementación.

### Síntesis de estado P0–P6 y PLAN_APPROVED

El escenario define `PLAN_APPROVED` como plan construido mediante respuestas defendidas con decisiones, gates y dependencias explícitas, y señala que este gate no autoriza código. La secuencia P0 fue defendida (B09/topografía y compatibilidad → grid → reglas y pruebas → asignación → validación → visualización); P1–P6 tienen decisiones conceptuales, alternativas consideradas, dependencias y bloqueos registrados. Se registra **`PLAN_APPROVED` conceptual bajo `RECOVERY_BLOCKED`**, separado de `BASE_VERIFIED` (que sigue NO verificado). Esto no levanta B09 ni autoriza malla/asignación/visualizador. Gates pendientes: `P2_GRID`, `P3_TOPO`, `P4_GEO_ASSIGN`, `P5_VALIDATION`, `P6_VISUALIZER` y `READY_FOR_REVIEW`; no hay resultados P2–P6 ni `MINING_VALIDATED`. No hubo código, instalación, commit o push por este registro.
