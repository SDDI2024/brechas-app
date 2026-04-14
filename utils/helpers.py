"""
Utilidades auxiliares para Brechas CLI
"""

import os
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def crear_directorios(carpeta_salida):
    """
    Crea la estructura de directorios necesaria.
    
    Args:
        carpeta_salida: Nombre de la carpeta de trabajo
    
    Returns:
        tuple: (ruta_intermedio, ruta_resultados)
    """
    dir_intermedio = f"data/intermediate/{carpeta_salida}"
    dir_resultados = f"data/results/{carpeta_salida}"
    
    os.makedirs(dir_intermedio, exist_ok=True)
    os.makedirs(dir_resultados, exist_ok=True)
    
    logger.info(f"Directorios creados: {dir_intermedio}, {dir_resultados}")
    return dir_intermedio, dir_resultados

def validar_archivo_csv(ruta_archivo, columnas_requeridas=None):
    """
    Valida que un archivo CSV tenga la estructura básica requerida.
    
    Args:
        ruta_archivo: Ruta al archivo CSV
        columnas_requeridas: Lista de columnas requeridas (opcional)
    
    Returns:
        tuple: (bool, str) - (es_valido, mensaje)
    """
    if not os.path.exists(ruta_archivo):
        return False, f"Archivo no encontrado: {ruta_archivo}"
    
    try:
        # Leer solo las primeras líneas para validación
        df_muestra = pd.read_csv(ruta_archivo, nrows=10, sep='|', encoding='ISO-8859-1', low_memory=False)
        
        if columnas_requeridas:
            columnas_faltantes = [col for col in columnas_requeridas if col not in df_muestra.columns]
            if columnas_faltantes:
                return False, f"Columnas faltantes: {', '.join(columnas_faltantes)}"
        
        # Verificar que tenga datos
        if len(df_muestra) == 0:
            return False, "Archivo vacío"
        
        return True, f"Archivo válido: {len(df_muestra.columns)} columnas, muestra de {len(df_muestra)} registros"
        
    except Exception as e:
        return False, f"Error leyendo archivo: {e}"

def mostrar_progreso(actual, total, texto="Procesando"):
    """
    Muestra una barra de progreso simple en consola.
    
    Args:
        actual: Iteración actual
        total: Total de iteraciones
        texto: Texto a mostrar
    """
    porcentaje = (actual / total) * 100
    barra = "█" * int(porcentaje / 2) + "░" * (50 - int(porcentaje / 2))
    
    print(f"\r{texto}: |{barra}| {porcentaje:.1f}% ({actual}/{total})", end="", flush=True)
    
    if actual == total:
        print()  # Nueva línea al completar

def obtener_columnas_requeridas():
    """
    Devuelve las columnas requeridas según AGENTS.MD.
    
    Returns:
        list: Lista de columnas requeridas
    """
    return [
        'CENTRO',
        'FECHA_ATENCION',
        'FECNACIMPACIENTE',
        'ACTIVIDAD',
        'SERVICIO',
        'ID'
    ]

def formatear_tiempo(segundos):
    """
    Formatea segundos a un string legible.
    
    Args:
        segundos: Tiempo en segundos
    
    Returns:
        str: Tiempo formateado
    """
    if segundos < 60:
        return f"{segundos:.1f} segundos"
    elif segundos < 3600:
        minutos = segundos / 60
        return f"{minutos:.1f} minutos"
    else:
        horas = segundos / 3600
        return f"{horas:.1f} horas"

def verificar_configuracion():
    """
    Verifica que los archivos de configuración necesarios existan.
    
    Returns:
        tuple: (bool, str) - (config_ok, mensaje)
    """
    config_dir = "config"
    
    # Verificar directorio config
    if not os.path.exists(config_dir):
        return False, f"Directorio de configuración no encontrado: {config_dir}"
    
    # Verificar archivos de votos por grupo etario
    grupos = ['A', 'B', 'C', 'D', 'E']
    tipos = ['A', 'C']
    
    archivos_faltantes = []
    for grupo in grupos:
        for tipo in tipos:
            archivo = f"{config_dir}/DF_CONSOLIDADO_{grupo}_respuesta_votos_{tipo}.txt"
            if not os.path.exists(archivo):
                archivos_faltantes.append(os.path.basename(archivo))
    
    if archivos_faltantes:
        return False, f"Archivos de votos faltantes: {', '.join(archivos_faltantes[:3])}..."
    
    # Verificar archivo de códigos
    archivo_codigos = f"{config_dir}/codigos.xlsx"
    if not os.path.exists(archivo_codigos):
        return False, f"Archivo de códigos no encontrado: {archivo_codigos}"
    
    return True, "Configuración verificada correctamente"