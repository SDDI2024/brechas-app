#!/usr/bin/env python3
"""
Brechas CLI - Aplicación sencilla para cálculo de brechas de recursos humanos

Sigue los 6 pasos definidos en AGENTS.MD manteniendo la lógica exacta
de anexo_v4_completo.py pero con interfaz amigable.
"""

import os
import sys
import logging
from datetime import datetime

# Configurar logging intermedio
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

def paso1_carpeta_salida():
    """Solicita nombre de carpeta para resultados y verifica si ya existe con datos"""
    print("\n" + "=" * 60)
    print("PASO 1: CARPETA DE TRABAJO")
    print("=" * 60)
    
    while True:
        carpeta = input("📁 Ingrese nombre para carpeta de trabajo (ej: analisis_2024): ").strip()
        
        if not carpeta:
            print("❌ El nombre no puede estar vacío")
            continue
            
        # Validación simple
        if any(c in carpeta for c in ' /\\:*?"<>|'):
            print("❌ El nombre no puede contener caracteres especiales o espacios")
            continue
        
        # Verificar si la carpeta ya existe y tiene datos
        dir_intermedio = f"data/intermediate/{carpeta}"
        dir_resultados = f"data/results/{carpeta}"
        
        # Verificar si la carpeta intermedia existe y tiene archivos
        carpeta_existe = os.path.exists(dir_intermedio)
        
        if carpeta_existe:
            try:
                # Buscar archivos de resultados según especificaciones AGENTS.md
                archivos_txt = [f for f in os.listdir(dir_intermedio) 
                               if f.endswith('.txt')]
                
                if archivos_txt:
                    # Analizar qué tipo de archivos existen
                    archivos_3d = [f for f in archivos_txt if '_3D_' in f]
                    archivos_4d = [f for f in archivos_txt if '_4D_' in f]
                    archivos_otros = [f for f in archivos_txt if '_3D_' not in f and '_4D_' not in f]
                    
                    print(f"\n⚠️  La carpeta '{carpeta}' ya existe y contiene {len(archivos_txt)} archivos .txt")
                    print(f"   Ubicación: {dir_intermedio}/")
                    
                    # Mostrar análisis según especificaciones AGENTS.md
                    if archivos_3d and archivos_4d:
                        print(f"\n📊 ANÁLISIS DE ARCHIVOS EXISTENTES:")
                        print(f"   • Archivos 3D encontrados: {len(archivos_3d)}")
                        print(f"   • Archivos 4D encontrados: {len(archivos_4d)}")
                        print(f"\n¿Qué desea hacer?")
                        print(f"   1. Pasar al Paso 6 con análisis 3D")
                        print(f"   2. Pasar al Paso 6 con análisis 4D")
                        print(f"   3. Sobrescribir carpeta y comenzar desde Paso 2")
                        print(f"   4. Usar otro nombre de carpeta")
                        
                        while True:
                            opcion = input("\nSeleccione opción (1-4): ").strip()
                            
                            if opcion == "1":
                                print(f"✅ Continuando desde Paso 6 usando datos 3D existentes")
                                os.makedirs(dir_resultados, exist_ok=True)
                                return carpeta, True, 3  # True indica saltar al Paso 6, 3 dígitos
                            elif opcion == "2":
                                print(f"✅ Continuando desde Paso 6 usando datos 4D existentes")
                                os.makedirs(dir_resultados, exist_ok=True)
                                return carpeta, True, 4  # True indica saltar al Paso 6, 4 dígitos
                            elif opcion == "3":
                                print(f"⚠️  Sobrescribiendo carpeta '{carpeta}'...")
                                import shutil
                                if os.path.exists(dir_intermedio):
                                    shutil.rmtree(dir_intermedio)
                                if os.path.exists(dir_resultados):
                                    shutil.rmtree(dir_resultados)
                                break  # Salir del bucle interno y continuar con creación
                            elif opcion == "4":
                                print(f"🔁 Ingrese un nuevo nombre de carpeta...")
                                break  # Salir del bucle interno para pedir nuevo nombre
                            else:
                                print("❌ Opción no válida. Por favor seleccione 1-4")
                        
                        if opcion == "4":
                            continue  # Pedir nuevo nombre de carpeta
                        elif opcion == "3":
                            # Continuar con la creación de directorios
                            pass
                            
                    elif archivos_3d and not archivos_4d:
                        print(f"\n📊 ANÁLISIS DE ARCHIVOS EXISTENTES:")
                        print(f"   • Solo archivos 3D encontrados: {len(archivos_3d)}")
                        print(f"\n¿Qué desea hacer?")
                        print(f"   1. Pasar al Paso 6 con análisis 3D")
                        print(f"   2. Sobrescribir carpeta y comenzar desde Paso 2")
                        print(f"   3. Usar otro nombre de carpeta")
                        
                        while True:
                            opcion = input("\nSeleccione opción (1-3): ").strip()
                            
                            if opcion == "1":
                                print(f"✅ Continuando desde Paso 6 usando datos 3D existentes")
                                os.makedirs(dir_resultados, exist_ok=True)
                                return carpeta, True, 3
                            elif opcion == "2":
                                print(f"⚠️  Sobrescribiendo carpeta '{carpeta}'...")
                                import shutil
                                if os.path.exists(dir_intermedio):
                                    shutil.rmtree(dir_intermedio)
                                if os.path.exists(dir_resultados):
                                    shutil.rmtree(dir_resultados)
                                break
                            elif opcion == "3":
                                print(f"🔁 Ingrese un nuevo nombre de carpeta...")
                                break
                            else:
                                print("❌ Opción no válida. Por favor seleccione 1-3")
                        
                        if opcion == "3":
                            continue
                        elif opcion == "2":
                            pass
                            
                    elif archivos_4d and not archivos_3d:
                        print(f"\n📊 ANÁLISIS DE ARCHIVOS EXISTENTES:")
                        print(f"   • Solo archivos 4D encontrados: {len(archivos_4d)}")
                        print(f"\n¿Qué desea hacer?")
                        print(f"   1. Pasar al Paso 6 con análisis 4D")
                        print(f"   2. Sobrescribir carpeta y comenzar desde Paso 2")
                        print(f"   3. Usar otro nombre de carpeta")
                        
                        while True:
                            opcion = input("\nSeleccione opción (1-3): ").strip()
                            
                            if opcion == "1":
                                print(f"✅ Continuando desde Paso 6 usando datos 4D existentes")
                                os.makedirs(dir_resultados, exist_ok=True)
                                return carpeta, True, 4
                            elif opcion == "2":
                                print(f"⚠️  Sobrescribiendo carpeta '{carpeta}'...")
                                import shutil
                                if os.path.exists(dir_intermedio):
                                    shutil.rmtree(dir_intermedio)
                                if os.path.exists(dir_resultados):
                                    shutil.rmtree(dir_resultados)
                                break
                            elif opcion == "3":
                                print(f"🔁 Ingrese un nuevo nombre de carpeta...")
                                break
                            else:
                                print("❌ Opción no válida. Por favor seleccione 1-3")
                        
                        if opcion == "3":
                            continue
                        elif opcion == "2":
                            pass
                            
                    elif archivos_otros:
                        print(f"\n⚠️  Archivos procesados incompletos encontrados: {len(archivos_otros)}")
                        print(f"   • Estos archivos no siguen el patrón 3D/4D")
                        print(f"   • Se recomienda comenzar desde Paso 2")
                        
                        while True:
                            opcion = input("\n¿Sobrescribir carpeta y comenzar desde Paso 2? (s/n): ").strip().lower()
                            
                            if opcion == 's':
                                print(f"⚠️  Sobrescribiendo carpeta '{carpeta}'...")
                                import shutil
                                if os.path.exists(dir_intermedio):
                                    shutil.rmtree(dir_intermedio)
                                if os.path.exists(dir_resultados):
                                    shutil.rmtree(dir_resultados)
                                break
                            elif opcion == 'n':
                                print(f"🔁 Ingrese un nuevo nombre de carpeta...")
                                break
                            else:
                                print("❌ Por favor ingrese 's' o 'n'")
                        
                        if opcion == 'n':
                            continue
                        elif opcion == 's':
                            pass
                            
                else:
                    # Carpeta existe pero está vacía
                    print(f"\n📁 La carpeta '{carpeta}' existe pero está vacía")
                    print(f"   Continuando desde Paso 2...")
                    
            except Exception as e:
                print(f"⚠️  Error verificando carpeta existente: {e}")
                # Continuar con creación normal
        
        # Crear directorios (si no existen o fueron eliminados)
        try:
            os.makedirs(dir_intermedio, exist_ok=True)
            os.makedirs(dir_resultados, exist_ok=True)
            
            if not carpeta_existe:
                print(f"✅ Directorios creados:")
                print(f"   • {dir_intermedio}")
                print(f"   • {dir_resultados}")
            
            return carpeta, False, None  # False indica que NO saltamos al Paso 6, None para dígitos
            
        except Exception as e:
            print(f"❌ Error creando directorios: {e}")
            continue

def paso2_anio_calculo():
    """Solicita año y muestra requisitos detallados según AGENTS.MD"""
    print("\n" + "=" * 60)
    print("PASO 2: AÑO DE CÁLCULO")
    print("=" * 60)
    
    while True:
        try:
            anio = input("📅 ¿Para qué año desea calcular la brecha de recursos humanos? (ej: 2024): ").strip()
            anio_int = int(anio)
            
            if anio_int < 2000 or anio_int > 2100:
                print("❌ Por favor ingrese un año entre 2000 y 2100")
                continue
            
            # Mostrar información detallada según AGENTS.MD
            print(f"\n" + "=" * 60)
            print(f"📋 INFORMACIÓN PARA EL AÑO {anio_int}")
            print("=" * 60)
            
            print(f"\nPara un cálculo adecuado de la brecha de recursos humanos en {anio_int}, necesitará:")
            print(f"\n1. 📊 DATOS DE ATENCIONES MÉDICAS:")
            print(f"   • Todas las atenciones médicas de consulta externa de IPRESS con población adscrita")
            print(f"   • Período requerido: años {anio_int-2} y {anio_int-1}")
            print(f"   • Formato: Archivo CSV separado por pipes (|)")
            print(f"   • Codificación: ISO-8859-1")
            
            print(f"\n2. 🔍 VARIABLES OBLIGATORIAS (requisito mínimo):")
            print(f"   1. CENTRO: Código de centro de atención")
            print(f"   2. FECHA_ATENCION: Fecha de atención en formato dd/mm/YYYY")
            print(f"   3. FECNACIMPACIENTE: Fecha de nacimiento del paciente en formato dd/mm/YYYY")
            print(f"   4. ACTIVIDAD: Descripción de actividad en consulta externa")
            print(f"   5. SERVICIO: Servicio de atención")
            print(f"   6. ID: Identificación única encriptada (puede ser DNI encriptado)")
            
            print(f"\n3. ⚠️  CONSIDERACIONES IMPORTANTES:")
            print(f"   • Los datos deben incluir diagnósticos CIE-10")
            print(f"   • Se excluirán automáticamente atenciones del centro '001'")
            print(f"   • Solo se procesarán actividades válidas:")
            print(f"     - ATENCION  MEDICA AMBULATORIA")
            print(f"     - ATENCION EN MEDICINA COMPLEMENTARIA")
            print(f"   • Se excluirán servicios específicos (medicina ocupacional, etc.)")
            
            print(f"\n4. 📁 ARCHIVOS DE CONFIGURACIÓN NECESARIOS:")
            print(f"   • codigos.xlsx: Códigos de centros y servicios, rendimientos")
            print(f"   • DF_CONSOLIDADO_*_respuesta_votos_*.txt: Datos de votos por grupo etario")
            print(f"   • Ubicación: config/")
            
            print(f"\n" + "=" * 60)
            
            return anio_int
            
        except ValueError:
            print("❌ Por favor ingrese un año válido (número)")
            continue

def paso3_ruta_datos():
    """Muestra archivos disponibles, verifica requisitos y solicita selección"""
    print("\n" + "=" * 60)
    print("PASO 3: ORIGEN DE DATOS")
    print("=" * 60)
    
    print("🔍 Explorando archivos en data/origen/...")
    
    # Listar archivos recursivamente
    archivos = []
    for root, dirs, files in os.walk("data/origen"):
        for file in files:
            if file.lower().endswith(('.csv', '.txt')):
                ruta_completa = os.path.join(root, file)
                archivos.append(ruta_completa)
    
    if not archivos:
        print("❌ No se encontraron archivos CSV o TXT en data/origen/")
        print("   Por favor coloque los archivos de datos en data/origen/")
        sys.exit(1)
    
    # Mostrar lista numerada
    print(f"\n📂 Archivos disponibles ({len(archivos)} encontrados):")
    for i, archivo in enumerate(archivos, 1):
        nombre = os.path.basename(archivo)
        tamaño = os.path.getsize(archivo) / (1024*1024)  # MB
        print(f"  {i:2d}. {nombre:<50} ({tamaño:.1f} MB)")
    
    # Selección
    while True:
        try:
            seleccion = input(f"\n📂 Seleccione archivo (1-{len(archivos)}): ").strip()
            if not seleccion:
                print("❌ Por favor ingrese un número")
                continue
                
            idx = int(seleccion) - 1
            if 0 <= idx < len(archivos):
                ruta_seleccionada = archivos[idx]
                nombre_archivo = os.path.basename(ruta_seleccionada)
                print(f"✅ Seleccionado: {nombre_archivo}")
                
                # Verificar requisitos del archivo
                print(f"\n🔍 Verificando requisitos del archivo...")
                
                try:
                    # Intentar leer el archivo para verificar columnas
                    import pandas as pd
                    
                    df_muestra = None
                    
                    # Determinar separador basado en extensión
                    if nombre_archivo.lower().endswith('.csv'):
                        # Intentar leer con diferentes separadores
                        for sep in ['|', ';', ',', '\t']:
                            try:
                                df_muestra = pd.read_csv(
                                    ruta_seleccionada, 
                                    nrows=5, 
                                    sep=sep,
                                    encoding='ISO-8859-1',
                                    low_memory=False
                                )
                                if len(df_muestra.columns) > 1:
                                    print(f"   • Separador detectado: '{sep}'")
                                    break
                            except:
                                continue
                    else:  # .txt
                        df_muestra = pd.read_csv(
                            ruta_seleccionada, 
                            nrows=5, 
                            sep='|',
                            encoding='ISO-8859-1',
                            low_memory=False
                        )
                        print(f"   • Separador: '|' (estándar para TXT)")
                    
                    if df_muestra is None or len(df_muestra.columns) == 0:
                        print(f"⚠️  No se pudo leer el archivo correctamente")
                        print(f"   Continuando sin verificación completa...")
                        return ruta_seleccionada
                    
                    # Columnas obligatorias según AGENTS.md
                    columnas_obligatorias = [
                        'CENTRO', 'FECHA_ATENCION', 'FECNACIMPACIENTE',
                        'ACTIVIDAD', 'SERVICIO', 'ID'
                    ]
                    
                    columnas_archivo = [col.upper() for col in df_muestra.columns]
                    columnas_faltantes = []
                    
                    for col_obligatoria in columnas_obligatorias:
                        if col_obligatoria not in columnas_archivo:
                            columnas_faltantes.append(col_obligatoria)
                    
                    if columnas_faltantes:
                        print(f"\n⚠️  ADVERTENCIA: Columnas obligatorias faltantes:")
                        for col in columnas_faltantes:
                            print(f"   • {col}")
                        print(f"\n   Columnas disponibles en el archivo:")
                        for col in columnas_archivo[:10]:  # Mostrar primeras 10
                            print(f"     - {col}")
                        if len(columnas_archivo) > 10:
                            print(f"     - ... y {len(columnas_archivo) - 10} más")
                        
                        print(f"\n📋 REQUISITOS MÍNIMOS (según AGENTS.md):")
                        print(f"   1. CENTRO: Código de centro de atención")
                        print(f"   2. FECHA_ATENCION: Fecha en formato dd/mm/YYYY")
                        print(f"   3. FECNACIMPACIENTE: Fecha nacimiento dd/mm/YYYY")
                        print(f"   4. ACTIVIDAD: Descripción de actividad")
                        print(f"   5. SERVICIO: Servicio de atención")
                        print(f"   6. ID: Identificación única encriptada")
                        
                        while True:
                            continuar = input(f"\n¿Continuar a pesar de las advertencias? (s/n): ").strip().lower()
                            if continuar == 's':
                                print(f"✅ Continuando con el archivo seleccionado")
                                return ruta_seleccionada
                            elif continuar == 'n':
                                print(f"🔁 Seleccione otro archivo...")
                                break
                            else:
                                print("❌ Por favor ingrese 's' o 'n'")
                        
                        if continuar == 'n':
                            continue  # Volver a pedir selección
                    else:
                        print(f"✅ Todas las columnas obligatorias están presentes")
                        print(f"   • Filas de muestra: {len(df_muestra)}")
                        print(f"   • Columnas totales: {len(columnas_archivo)}")
                        return ruta_seleccionada
                        
                except Exception as e:
                    print(f"⚠️  Error verificando archivo: {e}")
                    print(f"   Continuando sin verificación completa...")
                    return ruta_seleccionada
                    
            else:
                print(f"❌ Por favor seleccione un número entre 1 y {len(archivos)}")
                
        except ValueError:
            print("❌ Por favor ingrese un número válido")
            continue

def paso4_tipo_analisis():
    """Solicita tipo de análisis (3D o 4D) con explicación detallada"""
    print("\n" + "=" * 60)
    print("PASO 4: TIPO DE ANÁLISIS")
    print("=" * 60)
    
    print("📊 TIPOS DE ANÁLISIS DISPONIBLES:")
    print("\n" + "-" * 40)
    print("1. 3D - ANÁLISIS CON PRIMEROS 3 DÍGITOS DEL CIE-10")
    print("-" * 40)
    print("   • Usa solo los primeros 3 dígitos del código CIE-10")
    print("   • Ejemplo: 'I10' (Hipertensión esencial)")
    print("   • Nivel de agregación: Categoría principal")
    print("   • Favorece tanto a MF (C) como a MG (A)")
    print("   • Menor precisión pero más rápido")
    print("   • Recomendado para análisis general")
    
    print("\n" + "-" * 40)
    print("2. 4D - ANÁLISIS CON TODOS LOS DÍGITOS DEL CIE-10")
    print("-" * 40)
    print("   • Usa todos los dígitos del código CIE-10")
    print("   • Ejemplo: 'I10.0' (Hipertensión esencial benigna)")
    print("   • Nivel de agregación: Subcategoría específica")
    print("   • Favorece tanto a MF (C) como a MG (A)")
    print("   • Mayor precisión pero más lento")
    print("   • Recomendado para análisis detallado")
    
    print("\n" + "=" * 60)
    print("📋 CONSIDERACIONES:")
    print("   • Ambos análisis consideran escenarios A y C")
    print("   • Escenario A: Favorece a Medicina General (MG)")
    print("   • Escenario C: Favorece a Medicina Familiar (MF)")
    print("   • Los resultados incluyen comparación entre escenarios")
    
    while True:
        opcion = input("\n🔢 Seleccione tipo de análisis (1 o 2): ").strip()
        
        if opcion == "1":
            print("\n✅ ANÁLISIS 3D SELECCIONADO")
            print("   • Dígitos CIE-10: 3 (ej: I10)")
            print("   • Nivel: Categoría principal")
            print("   • Precisión: General")
            return 3
        elif opcion == "2":
            print("\n✅ ANÁLISIS 4D SELECCIONADO")
            print("   • Dígitos CIE-10: 4 (ej: I10.0)")
            print("   • Nivel: Subcategoría específica")
            print("   • Precisión: Detallada")
            return 4
        else:
            print("❌ Por favor seleccione 1 o 2")

def paso5_ejecutar_asignaciones(carpeta_salida, anio, ruta_datos, digitos_cie):
    """Ejecuta el algoritmo de asignación"""
    print("\n" + "=" * 60)
    print("PASO 5: EJECUCIÓN DE ASIGNACIONES")
    print("=" * 60)
    
    print(f"⚡ Ejecutando asignaciones...")
    print(f"   • Carpeta: {carpeta_salida}")
    print(f"   • Año: {anio}")
    print(f"   • Datos: {os.path.basename(ruta_datos)}")
    print(f"   • Dígitos CIE-10: {digitos_cie}")
    
    try:
        # Importar y ejecutar procesador
        from core.procesador import ProcesadorBrechas
        
        procesador = ProcesadorBrechas(
            carpeta_salida=carpeta_salida,
            anio_calculo=anio,
            ruta_datos=ruta_datos,
            digitos_cie=digitos_cie
        )
        
        logger.info("Iniciando procesamiento de asignaciones...")
        resultado = procesador.ejecutar_asignaciones()
        
        if resultado:
            logger.info("✅ Asignaciones completadas exitosamente")
            return True
        else:
            logger.error("❌ Error en asignaciones")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error ejecutando asignaciones: {e}")
        return False

def paso6_analizar_resultados(carpeta_salida, digitos_cie, anio_calculo=None):
    """Ejecuta análisis de resultados y genera gráficos"""
    print("\n" + "=" * 60)
    print("PASO 6: ANÁLISIS DE RESULTADOS Y GRÁFICOS")
    print("=" * 60)
    
    print(f"📈 Generando análisis y gráficos...")
    print(f"   • Dígitos CIE-10: {digitos_cie}")
    
    try:
        # Importar y ejecutar analizador
        from core.analizador import AnalizadorResultados
        
        # Si no se proporciona año (cuando se salta desde datos existentes), usar año actual - 1
        if anio_calculo is None:
            import datetime
            anio_calculo = datetime.datetime.now().year - 1
            print(f"   • Año calculado automáticamente: {anio_calculo}")
        
        analizador = AnalizadorResultados(
            carpeta_salida=carpeta_salida,
            digitos_cie=digitos_cie,
            anio_calculo=anio_calculo
        )
        
        logger.info("Iniciando análisis de resultados...")
        resultado = analizador.ejecutar_analisis()
        
        if resultado:
            logger.info("✅ Análisis y gráficos generados exitosamente")
            return True
        else:
            logger.error("❌ Error en análisis de resultados")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error ejecutando análisis: {e}")
        return False

def verificar_configuracion():
    """Verifica que los archivos de configuración necesarios existan"""
    archivos_necesarios = [
        'codigos.xlsx',
        'DF_CONSOLIDADO_A_respuesta_votos_A.txt',
        'DF_CONSOLIDADO_A_respuesta_votos_C.txt',
        'DF_CONSOLIDADO_B_respuesta_votos_A.txt',
        'DF_CONSOLIDADO_B_respuesta_votos_C.txt',
        'DF_CONSOLIDADO_C_respuesta_votos_A.txt',
        'DF_CONSOLIDADO_C_respuesta_votos_C.txt',
        'DF_CONSOLIDADO_D_respuesta_votos_A.txt',
        'DF_CONSOLIDADO_D_respuesta_votos_C.txt',
        'DF_CONSOLIDADO_E_respuesta_votos_A.txt',
        'DF_CONSOLIDADO_E_respuesta_votos_C.txt'
    ]
    
    archivos_faltantes = []
    for archivo in archivos_necesarios:
        ruta = os.path.join('config', archivo)
        if not os.path.exists(ruta):
            archivos_faltantes.append(archivo)
    
    if archivos_faltantes:
        print("⚠️  ADVERTENCIA: Archivos de configuración faltantes:")
        for archivo in archivos_faltantes:
            print(f"   • {archivo}")
        print(f"\n   Ubicación esperada: config/")
        print(f"   Estos archivos son necesarios para el cálculo correcto.")
        
        while True:
            continuar = input("\n¿Continuar a pesar de las advertencias? (s/n): ").strip().lower()
            if continuar == 's':
                print("✅ Continuando con configuración incompleta")
                return True
            elif continuar == 'n':
                print("❌ Proceso cancelado por el usuario")
                return False
            else:
                print("❌ Por favor ingrese 's' o 'n'")
    else:
        print("✅ Todos los archivos de configuración están presentes")
        return True

def main():
    """Función principal"""
    print("=" * 60)
    print("BRECHAS CLI - Cálculo de Brechas de Recursos Humanos")
    print("=" * 60)
    print(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print()
    
    # Verificar configuración antes de comenzar
    if not verificar_configuracion():
        return
    
    try:
        # Paso 1: Carpeta de trabajo (ahora retorna 3 valores)
        carpeta_salida, saltar_a_paso6, digitos_existentes = paso1_carpeta_salida()
        
        if saltar_a_paso6 and digitos_existentes:
            # El usuario eligió usar datos existentes, saltar al Paso 6
            print("\n" + "=" * 60)
            print("SALTANDO A ANÁLISIS CON DATOS EXISTENTES")
            print("=" * 60)
            
            # Ya sabemos los dígitos CIE-10 usados en los datos existentes
            digitos_cie = digitos_existentes
            
            # Confirmación para análisis
            print("\n" + "=" * 60)
            print("CONFIRMACIÓN PARA ANÁLISIS")
            print("=" * 60)
            print(f"• Carpeta de trabajo: {carpeta_salida}")
            print(f"• Dígitos CIE-10: {digitos_cie}")
            print(f"• Datos existentes en: data/intermediate/{carpeta_salida}/")
            
            confirmar = input("\n¿Continuar con el análisis de resultados? (s/n): ").strip().lower()
            if confirmar != 's':
                print("❌ Análisis cancelado por el usuario")
                return
            
            # Solo ejecutar Paso 6: Análisis y gráficos
            inicio_analisis = datetime.now()
            
            if paso6_analizar_resultados(carpeta_salida, digitos_cie):
                fin_analisis = datetime.now()
                duracion_analisis = fin_analisis - inicio_analisis
                
                print("\n" + "=" * 60)
                print("🎉 ANÁLISIS COMPLETADO EXITOSAMENTE")
                print("=" * 60)
                print(f"📊 Resultados finales: data/results/{carpeta_salida}/")
                print(f"⏱️  Tiempo de análisis: {duracion_analisis}")
                print("\n¡Gracias por usar Brechas CLI!")
            else:
                print("\n❌ Error en análisis de resultados")
                print("   Revise los logs para más detalles")
            
            return  # Terminar ejecución después del análisis
        
        # Flujo normal (comenzar desde Paso 2)
        # Paso 2: Año de cálculo
        anio = paso2_anio_calculo()
        
        # Paso 3: Origen de datos
        ruta_datos = paso3_ruta_datos()
        
        # Paso 4: Tipo de análisis
        digitos_cie = paso4_tipo_analisis()
        
        # Confirmación
        print("\n" + "=" * 60)
        print("CONFIRMACIÓN DE PARÁMETROS")
        print("=" * 60)
        print(f"• Carpeta de trabajo: {carpeta_salida}")
        print(f"• Año de cálculo: {anio}")
        print(f"• Archivo de datos: {os.path.basename(ruta_datos)}")
        print(f"• Dígitos CIE-10: {digitos_cie}")
        
        confirmar = input("\n¿Continuar con el procesamiento? (s/n): ").strip().lower()
        if confirmar != 's':
            print("❌ Proceso cancelado por el usuario")
            return
        
        # Paso 5: Ejecutar asignaciones
        print("\n" + "=" * 60)
        print("INICIANDO PROCESAMIENTO")
        print("=" * 60)
        
        inicio_total = datetime.now()
        
        if paso5_ejecutar_asignaciones(carpeta_salida, anio, ruta_datos, digitos_cie):
            print("\n" + "=" * 60)
            print("ASIGNACIONES COMPLETADAS")
            print("=" * 60)
            
            # Paso 6: Análisis y gráficos
            if paso6_analizar_resultados(carpeta_salida, digitos_cie, anio):
                fin_total = datetime.now()
                duracion = fin_total - inicio_total
                
                print("\n" + "=" * 60)
                print("🎉 PROCESO COMPLETADO EXITOSAMENTE")
                print("=" * 60)
                print(f"📁 Resultados intermedios: data/intermediate/{carpeta_salida}/")
                print(f"📊 Resultados finales: data/results/{carpeta_salida}/")
                print(f"⏱️  Tiempo total: {duracion}")
                print("\n¡Gracias por usar Brechas CLI!")
            else:
                print("\n❌ Error en análisis de resultados")
                print("   Revise los logs para más detalles")
        else:
            print("\n❌ Error en asignaciones")
            print("   Revise los logs para más detalles")
            
    except KeyboardInterrupt:
        print("\n\n❌ Proceso interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()