#!/usr/bin/env python3
"""
Verificador de resultados entre versiones del código

Este script compara los archivos de resultados generados por diferentes versiones
para verificar que producen resultados idénticos.

Uso: python verificador_resultados.py <version_base> <version_comparar>
Ejemplo: python verificador_resultados.py anexo_v2 anexo_v4
"""

import pandas as pd
import numpy as np
import os
import sys

def comparar_archivos(ruta_base, ruta_comparar, nombre_archivo):
    """
    Compara dos archivos de resultados y verifica que sean idénticos.
    
    Args:
        ruta_base: Ruta al directorio de la versión base
        ruta_comparar: Ruta al directorio de la versión a comparar
        nombre_archivo: Nombre del archivo a comparar
        
    Returns:
        dict: Resultados de la comparación
    """
    archivo_base = os.path.join(ruta_base, nombre_archivo)
    archivo_comparar = os.path.join(ruta_comparar, nombre_archivo)
    
    resultados = {
        'archivo': nombre_archivo,
        'existe_base': os.path.exists(archivo_base),
        'existe_comparar': os.path.exists(archivo_comparar),
        'tamano_base': None,
        'tamano_comparar': None,
        'filas_base': None,
        'filas_comparar': None,
        'columnas_base': None,
        'columnas_comparar': None,
        'identicos': False,
        'diferencias': []
    }
    
    # Verificar existencia
    if not resultados['existe_base']:
        resultados['diferencias'].append(f"Archivo no existe en {ruta_base}: {archivo_base}")
        return resultados
    
    if not resultados['existe_comparar']:
        resultados['diferencias'].append(f"Archivo no existe en {ruta_comparar}: {archivo_comparar}")
        return resultados
    
    # Obtener tamaños
    resultados['tamano_base'] = os.path.getsize(archivo_base)
    resultados['tamano_comparar'] = os.path.getsize(archivo_comparar)
    
    # Cargar datos
    try:
        df_base = pd.read_csv(archivo_base, sep='|', low_memory=False)
        df_comparar = pd.read_csv(archivo_comparar, sep='|', low_memory=False)
        
        resultados['filas_base'] = len(df_base)
        resultados['filas_comparar'] = len(df_comparar)
        resultados['columnas_base'] = list(df_base.columns)
        resultados['columnas_comparar'] = list(df_comparar.columns)
        
        # Comparar dimensiones
        if len(df_base) != len(df_comparar):
            resultados['diferencias'].append(f"Diferencia en número de filas: base={len(df_base)}, comparar={len(df_comparar)}")
        
        if list(df_base.columns) != list(df_comparar.columns):
            resultados['diferencias'].append(f"Diferencia en columnas: base={list(df_base.columns)}, comparar={list(df_comparar.columns)}")
        
        # Comparar valores
        if len(df_base) == len(df_comparar) and list(df_base.columns) == list(df_comparar.columns):
            # Ordenar por las mismas columnas para comparación
            columnas_orden = ['ID', 'FECHA_ATENCION', 'DIAGNOSTICO']
            columnas_disponibles = [c for c in columnas_orden if c in df_base.columns]
            
            if columnas_disponibles:
                df_base_sorted = df_base.sort_values(by=columnas_disponibles).reset_index(drop=True)
                df_comparar_sorted = df_comparar.sort_values(by=columnas_disponibles).reset_index(drop=True)
                
                # Comparar columna por columna
                for columna in df_base.columns:
                    if columna not in df_comparar.columns:
                        resultados['diferencias'].append(f"Columna {columna} no existe en versión a comparar")
                        continue
                    
                    # Manejar valores NaN en la comparación
                    valores_iguales = (df_base_sorted[columna].fillna('NaN') == df_comparar_sorted[columna].fillna('NaN')).all()
                    
                    if not valores_iguales:
                        # Encontrar diferencias específicas manualmente
                        diferencias_idx = []
                        for i in range(len(df_base_sorted)):
                            val_base = df_base_sorted.iloc[i][columna]
                            val_comparar = df_comparar_sorted.iloc[i][columna]
                            # Manejar NaN
                            if pd.isna(val_base):
                                val_base = 'NaN'
                            if pd.isna(val_comparar):
                                val_comparar = 'NaN'
                            
                            if str(val_base) != str(val_comparar):
                                diferencias_idx.append(i)
                        
                        if len(diferencias_idx) > 0:
                            primeros_5 = diferencias_idx[:5]
                            ejemplos = []
                            for idx in primeros_5:
                                ejemplos.append(f"fila {idx}: base='{df_base_sorted.iloc[idx][columna]}', comparar='{df_comparar_sorted.iloc[idx][columna]}'")
                            resultados['diferencias'].append(f"Diferencias en columna '{columna}': {len(diferencias_idx)} diferencias. Ejemplos: {', '.join(ejemplos)}")
        
        # Verificar si son idénticos
        resultados['identicos'] = len(resultados['diferencias']) == 0
        
    except Exception as e:
        resultados['diferencias'].append(f"Error al comparar: {str(e)}")
    
    return resultados

def generar_resumen_comparacion(resultados_comparacion, version_base, version_comparar):
    """
    Genera un resumen de la comparación.
    
    Args:
        resultados_comparacion: Lista de resultados de comparación
        version_base: Nombre de la versión base
        version_comparar: Nombre de la versión a comparar
        
    Returns:
        str: Resumen formateado
    """
    total_archivos = len(resultados_comparacion)
    archivos_identicos = sum(1 for r in resultados_comparacion if r['identicos'])
    archivos_con_diferencias = total_archivos - archivos_identicos
    
    resumen = []
    resumen.append("=" * 80)
    resumen.append(f"RESUMEN DE COMPARACIÓN: {version_base} vs {version_comparar}")
    resumen.append("=" * 80)
    resumen.append(f"Total de archivos comparados: {total_archivos}")
    resumen.append(f"Archivos idénticos: {archivos_identicos}")
    resumen.append(f"Archivos con diferencias: {archivos_con_diferencias}")
    resumen.append("")
    
    if archivos_con_diferencias > 0:
        resumen.append("ARCHIVOS CON DIFERENCIAS:")
        resumen.append("-" * 40)
        for resultado in resultados_comparacion:
            if not resultado['identicos']:
                resumen.append(f"  • {resultado['archivo']}:")
                for diff in resultado['diferencias']:
                    resumen.append(f"      - {diff}")
                resumen.append("")
    
    # Detalles por archivo
    resumen.append("DETALLES POR ARCHIVO:")
    resumen.append("-" * 40)
    
    for resultado in resultados_comparacion:
        estado = "✓ IDÉNTICO" if resultado['identicos'] else "✗ DIFERENTE"
        resumen.append(f"  {resultado['archivo']}: {estado}")
        if resultado['existe_base'] and resultado['existe_comparar']:
            resumen.append(f"    Tamaño: {version_base}={resultado['tamano_base']:,} bytes, {version_comparar}={resultado['tamano_comparar']:,} bytes")
            resumen.append(f"    Filas: {version_base}={resultado['filas_base']:,}, {version_comparar}={resultado['filas_comparar']:,}")
            resumen.append(f"    Columnas: {len(resultado['columnas_base'])} columnas")
    
    resumen.append("=" * 80)
    
    return "\n".join(resumen)

def main():
    """Función principal del verificador."""
    
    # Verificar argumentos
    if len(sys.argv) != 3:
        print("Uso: python verificador_resultados.py <version_base> <version_comparar>")
        print("Ejemplo: python verificador_resultados.py anexo_v2 anexo_v4")
        sys.exit(1)
    
    version_base = sys.argv[1]
    version_comparar = sys.argv[2]
    
    print(f"Iniciando verificación de resultados: {version_base} vs {version_comparar}")
    
    # Definir rutas
    dir_base = f"data/intermediate/{version_base}"
    dir_comparar = f"data/intermediate/{version_comparar}"
    
    # Verificar que existen los directorios
    if not os.path.exists(dir_base):
        print(f"ERROR: Directorio {dir_base} no existe")
        sys.exit(1)
    
    if not os.path.exists(dir_comparar):
        print(f"ERROR: Directorio {dir_comparar} no existe")
        sys.exit(1)
    
    # Obtener lista de archivos en la versión base
    archivos_base = [f for f in os.listdir(dir_base) if f.endswith('.txt')]
    
    if not archivos_base:
        print(f"ERROR: No se encontraron archivos .txt en {dir_base}")
        sys.exit(1)
    
    print(f"Encontrados {len(archivos_base)} archivos en {dir_base}")
    
    # Comparar cada archivo
    resultados_comparacion = []
    
    for archivo in sorted(archivos_base):
        print(f"  Comparando: {archivo}...")
        resultado = comparar_archivos(dir_base, dir_comparar, archivo)
        resultados_comparacion.append(resultado)
    
    # Generar y mostrar resumen
    resumen = generar_resumen_comparacion(resultados_comparacion, version_base, version_comparar)
    print(resumen)
    
    # Guardar resumen en archivo
    with open("comparacion_resultados.txt", "w") as f:
        f.write(resumen)
    
    print(f"Resumen guardado en: comparacion_resultados.txt")
    
    # Verificar si todos son idénticos
    todos_identicos = all(r['identicos'] for r in resultados_comparacion)
    
    if todos_identicos:
        print(f"\n✅ ¡TODOS LOS ARCHIVOS SON IDÉNTICOS!")
        print(f"   La versión {version_comparar} mantiene la misma lógica que {version_base}.")
    else:
        print(f"\n❌ HAY DIFERENCIAS EN LOS RESULTADOS")
        print(f"   Revisar los detalles arriba.")
        sys.exit(1)

if __name__ == "__main__":
    main()