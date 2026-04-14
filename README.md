# Brechas CLI - Aplicación para Cálculo de Brechas de Recursos Humanos

Aplicación CLI sencilla y funcional para calcular brechas de recursos humanos de forma automatizada en el sistema de salud, basada en la lógica de la publicación titulada [Development of a methodology to determine the gap in medical professionals in outpatient care based on the epidemiological profile of demand](https://amp.cmp.org.pe/index.php/AMP/article/view/3583).

## 📁 Estructura del proyecto

```
brechas-app-v1/
├── brechas_cli.py              # Punto de entrada principal
├── core/                       # Lógica principal
│   ├── __init__.py
│   ├── procesador.py          # Procesamiento de asignaciones
│   └── analizador.py          # Análisis y gráficos
├── utils/                      # Utilidades
│   ├── __init__.py
│   └── helpers.py             # Funciones auxiliares
├── config/                     # Archivos de configuración
├── data/                       # Datos de entrada y resultados
│   ├── origen/                # Datos de atenciones médicas
│   ├── intermediate/          # Resultados intermedios
│   └── results/               # Resultados finales
└── README.md              # Esta documentación
```

## Instalación

```bash
# Clonar el repositorio
git clone https://github.com/SDDI2024/brechas-app.git

cd brechas-app

# Instalar entorno virtual

## En linux
python3 -m venv -venv

## En windows
python -m venv -venv

# Instalar dependencias
pip install -r requirements.txt

# Crear las carpetas de data

mkdir -p data/origen data/intermediate data/results
```

**Dependencias principales:**
- pandas
- openpyxl  
- matplotlib
- numpy


## 🚀 Uso básico

1. **Ejecutar la aplicación**:
   ```bash
   python brechas_cli.py
   ```

2. **Seguir los 6 pasos interactivos mejorados**:

   **Paso 1**: 📁 Nombre de carpeta de trabajo
   - Ejemplo: `analisis_2024`
   - Se crean automáticamente los directorios necesarios

   **Paso 2**: 📅 Año de cálculo (ej: 2024)
   - Requisitos específicos para el año seleccionado
   - Variables obligatorias y consideraciones importantes

   **Paso 3**: 📂 Selección de archivo de datos
   - Exploración automática de `data/origen/`
   - Lista interactiva de archivos disponibles
   - Información de tamaño de archivos

   **Paso 4**: 📊 Tipo de análisis
   - Opción 1: **3D** - Primeros 3 dígitos del CIE-10
   - Opción 2: **4D** - Todos los dígitos del CIE-10

   **Paso 5**: ⚡ Ejecución de asignaciones
   - Información en tiempo real sobre combinaciones procesadas
   - Tiempos de ejecución por combinación
   - Resumen completo al finalizar

   **Paso 6**: 📈 Análisis de resultados y gráficos
   - Tablas cruzadas en Excel
   - Cálculo de brechas de recursos humanos
   - Métricas de tiempo de ejecución

## 📋 Requisitos previos

### Archivos de configuración (en `config/`):
- `codigos.xlsx` - Códigos de centros y servicios
- `DF_CONSOLIDADO_*_respuesta_votos_*.txt` - Datos de concenso de expertos por diagnóstico y por grupo etario (10 archivos que están contenidos en el aplicativo)

Nota: Estos datos podrían varíar si se cambia el ámbito de análisis (otra red asistencial de salud) o si hay cambios en los consensos de los diagnósticos, por lo que el aplicativo puede adaptarse a otras realidades.

### Datos de entrada (en `data/origen/`):
- Archivos CSV con datos de atenciones médicas
- Formato: separado por pipes (`|`), codificación ISO-8859-1
- Columnas obligatorias:
  1. `CENTRO` - Código de centro de atención
  2. `FECHA_ATENCION` - Fecha en formato dd/mm/YYYY
  3. `FECNACIMPACIENTE` - Fecha nacimiento en formato dd/mm/YYYY
  4. `ACTIVIDAD` - Descripción de actividad
  5. `SERVICIO` - Servicio de atención
  6. `ID` - Identificación única encriptada

### Periodo de datos de entrada:
- Si se quiere realizar el cálculo de la brecha de recursos humanos para el año 2024, se requerirán las atenciones en consulta externa de las IPRESS con población adscrita de los años 2022 y 2023.

## 🔧 Tipos de análisis

### 3D
- Usa los primeros 3 dígitos del código CIE-10
- Análisis de asignación de demanda que favorece tanto a Medicina Familiar (MF) como a Medicina General (MG)

### 4D
- Usa todos los dígitos del código CIE-10
- Análisis de asignación de demanda que favorece tanto a Medicina Familiar (MF) como a Medicina General (MG)

## 📊 Resultados generados

### Resultados Intermedios (`data/intermediate/[carpeta]/`):
- 10 archivos `Resultado_[Grupo]_[Tipo]_[Dígitos]D_Nuevo.txt` (5 grupos × 2 tipos)
- Formato: CSV separado por pipes
- Contienen asignaciones de cada atención
- Estructura idéntica a `anexo_v4_completo.py`

### Resultados Finales (`data/results/[carpeta]/`):
1. **Tablas cruzadas** (`tabla_cruzada_[Tipo]_[Dígitos]D_[carpeta].xlsx`)
   - Distribución de atenciones por servicio y centro
   - 4 hojas: original, solo asignadas, solo NO asignadas, completa

2. **Cálculo de brechas RRHH** (`rrhh_[Tipo]_[Dígitos]D_2023_[carpeta].xlsx`)
   - Recursos humanos necesarios por centro
   - 4 hojas: rrhh_original, rrhh_con_asignacion, rrhh_solo_sin_asignacion, rrhh_completa

3. **Gráficos dumbbell** (`grafico_dumbbell_[Tipo]_[Dígitos]D_rrhh_comparacion_2023_[carpeta].png`)
   - Comparación visual RRHH original vs completa
   - Diferencias codificadas por color (verde=aumento, rojo=disminución)
   - Todos los servicios ordenados por diferencia absoluta

4. **Métricas de tiempo de ejecución**:
   - `tiempo_asignaciones_[carpeta].md` - Solo Paso 5 (lo que más demora)

## Lógica del algoritmo de asignación de atenciones

### Parámetros de entrada:
- `atenciones`: DataFrame con atenciones de un grupo etario específico
- `resultados`: DataFrame con resultados de votos (CIE-10, _resultado, _k)
- `numero_digitos_cie_10`: 3 o 4 dígitos para matching de diagnósticos

### Inicialización:
1. Suprime advertencias FutureWarning para evitar ruido en la salida
2. Crea columna `'RESULTADO DE TIPO ATENCION'` con valor `'SIN ASIGNACION'`
3. Crea columna `'REVISADO'` con valor `'N'` (no revisado)
4. Convierte `'FECHA_ATENCION'` a datetime con formato `'%d/%m/%Y'` para operaciones de fecha

### Procesamiento por diagnóstico:
Para cada fila en `resultados`:
- `a` = código CIE-10 (ej: `'B34.0'`)
- `b` = resultado (`'MG'`, `'MF'`, o nombre de especialidad)
- `c` = valor `_k` (1-5)

#### 1. Matching de diagnósticos:
- **Si `numero_digitos_cie_10 == 3`**: 
  - Extrae primeros 3 caracteres: `a[:3]` (ej: `'B34'`)
  - Crea regex escapado: `re.escape(a[:3])`
  - Filtra: `atenciones['DIAGNOSTICO'].str.match(a_regex)`
  - **Ejemplo**: `'B34.0'` busca `'B34*'` (coincide con B34.0, B34.1, B34.9, etc.)
- **Si `numero_digitos_cie_10 == 4`**:
  - Comparación exacta: `atenciones['DIAGNOSTICO'] == a`
  - **Ejemplo**: `'B34.0'` solo coincide con `'B34.0'`

**Filtro adicional**: `(atenciones['REVISADO'] == 'N')` → procesa solo atenciones no revisadas

#### 2. Caso MG/MF:
Si `b == 'MG'` o `b == 'MF'`:
- Todas las atenciones coincidentes se asignan directamente a `b`
- Se marcan como revisadas (`'REVISADO' = 'S'`)
- **No hay ventana temporal** para estos casos

#### 3. Caso especialista (b):
Si `b != 'MG'` y `b != 'MF'` (especialidad como `'HEMATOLOGIA'`):

**3.1. Filtro de atenciones 2023:**
- `Prime_Atenciones_2023` = atenciones coincidentes del año 2023
- Si hay atenciones 2023, se ordenan por fecha ascendente

**3.2. Procesamiento por atención 2023:**
Para cada atención 2023 del paciente:
- `e_id` = ID del paciente
- `primer_fecha_atencion_2023` = fecha de la atención 2023 actual
- `f_un_anio_atras` = `primer_fecha_atencion_2023 - timedelta(days=365)`

**3.3. Ventana temporal:**
Filtra atenciones del mismo paciente que cumplan:
1. Mismo ID: `Prime_Atenciones_G['id'] == e_id`
2. **Fecha >= f_un_anio_atras**: `Prime_Atenciones_G['FECHA_ATENCION'] >= f_un_anio_atras`
3. No revisadas: `Prime_Atenciones_G['REVISADO'] == 'N'`

**NOTA IMPORTANTE**: El uso de `>=` (mayor o igual) es intencional y correcto. Incluye la fecha exacta de un año atrás.

**3.4. Reglas de asignación según `_k`:**
- `c == 1`: Todas → Especialista (`b`)
- `c == 2`: Primera → MF, resto → Especialista  
- `c == 3`: Primeras 2 → MF, resto → Especialista  
- `c == 4`: Primeras 3 → MF, resto → Especialista
- `c == 5`: Primeras 4 → MF, resto → Especialista

### Ejemplo de aplicación:
Si se está calculando la brecha de RRHH para el año 2024. Se requieren las atenciones de los años 2022 y 2023.

**Datos del paciente**:
- Atenciones D50.0: 19/01/2022, 15/04/2022, 10/09/2022, 15/03/2023, 20/06/2023
- Se selecciona todas las atenciones del 2023 (el año anterior al periodo de cálculo de brecha de RRHH que para el ejemplo es 2024). Se identifica la Primera atención 2023: 15/03/2023
- Se crea una ventana temporal con `f_un_anio_atras`: 15/03/2022 (15/03/2023 - 365 días)

**Ventana temporal**:
- `FECHA_ATENCION >= 15/03/2022`
- **Incluye**: 15/04/2022, 10/09/2022, 15/03/2023, 20/06/2023
- **Excluye**: 19/01/2022 (fuera de ventana)

**Aplicación con `_k = 3`**:
1. 19/01/2022 → No procesada (fuera de la ventana)
2. 15/04/2022 → MF (primera atención dentro de la ventana)
3. 10/09/2022 → MF (segunda atención dentro de la ventana)  
4. 15/03/2023 → HEMATOLOGIA (tercera y siguientes)
5. 20/06/2023 → HEMATOLOGIA (tercera y siguientes)

## Reglas para el cálculo de RRHH según demanda de atenciones (DIRECTIVANº 012 ·GG-ESSALUD-2015) 

### Extensión de uso: 45%
### Concentración 
- Nivel I: 3.5
- Nivel II (Hospital general) H II y H I: 3.5
- Nivel II (Hospital especializado): 4
- Nivel III: 4
### Rendimiento para todas las especialidades
- Nivel II: 5
- Nivel I: 5

### Especialidades con rendimiento diferenciado
- Geriatría, Genética, Rehabilitación, Psiquiatría: Rendimiento promedio: 3
- En pacientes con TS-MSR/VJH: Rendimiento promedio de 3 en todos los niveles de atención. 

## Distribución de promedio de horas de personal médico para consulta
- Nivel II - Hospital especializado: 60h
- Nivel II - H II: 60h
- Nivel II - H I: 100h
- Nivel I: 100h

Nota: Para los médicos de familia así como para los médicos generales el número de horas asignadas a la consulta ambulatoria siempre será 100 horas, independientemente del nivel de la IPRESS.

---

**¡Listo para calcular brechas de recursos humanos!** 🎯