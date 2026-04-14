#!/usr/bin/env python3
"""
Verificador detallado de resultados - Enfocado en la columna RESULTADO DE TIPO ATENCION

Este script realiza una comparación más profunda, especialmente en la columna
de resultados que es la más crítica para verificar que la lógica del algoritmo
se mantiene idéntica.

Uso: python verificador_detallado.py <version_base> <version_comparar>
Ejemplo: python verificador_detallado.py anexo_v2 anexo_v4
"""

import pandas as pd
import os
import sys
from collections import Counter

def analizar_distribucion_resultados(df, nombre_archivo):
    """
    Analiza la distribución de valores en la columna RESULTADO DE TIPO ATENCION.
    
    Args:
        df: DataFrame con los datos
        nombre_archivo: Nombre del archivo para referencia
        
    Returns:
        dict: Estadísticas de distribución
    """
    if 'RESULTADO DE TIPO ATENCION' not in df.columns:
        return {'error': f"Columna 'RESULTADO DE TIPO ATENCION' no encontrada en {nombre_archivo}"}
    
    resultados = df['RESULTADO DE TIPO ATENCION']
    conteo = Counter(resultados)
    total = len(resultados)
    
    distribucion = {}
    for valor, count in conteo.most_common():
        porcentaje = (count / total) * 100
        distribucion[valor] = {
            'count': count,
            'percentage': round(porcentaje, 2)
        }
    
    return {
        'total_registros': total,
        'distribucion': distribucion,
        'valores_unicos': len(conteo),
        'valor_mas_comun': conteo.most_common(1)[0][0] if conteo else None
    }

def comparar_distribuciones(dist_base, dist_comparar, nombre_archivo, version_base, version_comparar):
    """
    Compara las distribuciones de resultados entre dos versiones.
    
    Args:
        dist_base: Distribución de la versión base
        dist_comparar: Distribución de la versión a comparar
        nombre_archivo: Nombre del archivo
        version_base: Nombre de la versión base
        version_comparar: Nombre de la versión a comparar
        
    Returns:
        dict: Resultados de la comparación
    """
    resultados = {
        'archivo': nombre_archivo,
        'total_base': dist_base.get('total_registros', 0),
        'total_comparar': dist_comparar.get('total_registros', 0),
        'valores_unicos_base': dist_base.get('valores_unicos', 0),
        'valores_unicos_comparar': dist_comparar.get('valores_unicos', 0),
        'valor_mas_comun_base': dist_base.get('valor_mas_comun'),
        'valor_mas_comun_comparar': dist_comparar.get('valor_mas_comun'),
        'distribucion_base': dist_base.get('distribucion', {}),
        'distribucion_comparar': dist_comparar.get('distribucion', {}),
        'diferencias': [],
        'identica': False
    }
    
    # Verificar errores
    if 'error' in dist_base:
        resultados['diferencias'].append(f"Error en {version_base}: {dist_base['error']}")
        return resultados
    
    if 'error' in dist_comparar:
        resultados['diferencias'].append(f"Error en {version_comparar}: {dist_comparar['error']}")
        return resultados
    
    # Comparar totales
    if resultados['total_base'] != resultados['total_comparar']:
        resultados['diferencias'].append(f"Diferencia en total de registros: {version_base}={resultados['total_base']}, {version_comparar}={resultados['total_comparar']}")
    
    # Comparar valores únicos
    if resultados['valores_unicos_base'] != resultados['valores_unicos_comparar']:
        resultados['diferencias'].append(f"Diferencia en valores únicos: {version_base}={resultados['valores_unicos_base']}, {version_comparar}={resultados['valores_unicos_comparar']}")
    
    # Comparar valor más común
    if resultados['valor_mas_comun_base'] != resultados['valor_mas_comun_comparar']:
        resultados['diferencias'].append(f"Diferencia en valor más común: {version_base}='{resultados['valor_mas_comun_base']}', {version_comparar}='{resultados['valor_mas_comun_comparar']}'")
    
    # Comparar distribución detallada
    todos_valores = set(resultados['distribucion_base'].keys()) | set(resultados['distribucion_comparar'].keys())
    
    for valor in sorted(todos_valores):
        count_base = resultados['distribucion_base'].get(valor, {}).get('count', 0)
        count_comparar = resultados['distribucion_comparar'].get(valor, {}).get('count', 0)
        
        if count_base != count_comparar:
            porcentaje_base = resultados['distribucion_base'].get(valor, {}).get('percentage', 0)
            porcentaje_comparar = resultados['distribucion_comparar'].get(valor, {}).get('percentage', 0)
            resultados['diferencias'].append(f"Diferencia en '{valor}': {version_base}={count_base} ({porcentaje_base}%), {version_comparar}={count_comparar} ({porcentaje_comparar}%)")
    
    resultados['identica'] = len(resultados['diferencias']) == 0
    return resultados

def generar_reporte_detallado(resultados_comparacion, version_base, version_comparar):
    """
    Genera un reporte detallado de la comparación.
    
    Args:
        resultados_comparacion: Lista de resultados de comparación
        version_base: Nombre de la versión base
        version_comparar: Nombre de la versión a comparar
        
    Returns:
        str: Reporte formateado
    """
    reporte = []
    reporte.append("=" * 80)
    reporte.append(f"REPORTE DETALLADO DE DISTRIBUCIÓN: {version_base} vs {version_comparar}")
    reporte.append("=" * 80)
    reporte.append("")
    
    total_archivos = len(resultados_comparacion)
    archivos_identicos = sum(1 for r in resultados_comparacion if r['identica'])
    archivos_con_diferencias = total_archivos - archivos_identicos
    
    reporte.append(f"RESUMEN GENERAL:")
    reporte.append(f"  Total de archivos analizados: {total_archivos}")
    reporte.append(f"  Archivos con distribución idéntica: {archivos_identicos}")
    reporte.append(f"  Archivos con diferencias: {archivos_con_diferencias}")
    reporte.append("")
    
    if archivos_con_diferencias > 0:
        reporte.append("ARCHIVOS CON DIFERENCIAS:")
        reporte.append("-" * 40)
        for resultado in resultados_comparacion:
            if not resultado['identica']:
                reporte.append(f"  • {resultado['archivo']}:")
                for diff in resultado['diferencias']:
                    reporte.append(f"      - {diff}")
                reporte.append("")
    
    # Distribución agregada
    reporte.append("DISTRIBUCIÓN AGREGADA:")
    reporte.append("-" * 40)
    
    # Calcular totales agregados
    total_base_agregado = sum(r['total_base'] for r in resultados_comparacion)
    total_comparar_agregado = sum(r['total_comparar'] for r in resultados_comparacion)
    
    reporte.append(f"  Total registros {version_base}: {total_base_agregado:,}")
    reporte.append(f"  Total registros {version_comparar}: {total_comparar_agregado:,}")
    
    if total_base_agregado != total_comparar_agregado:
        reporte.append(f"  ⚠️  Diferencia en total agregado: {abs(total_base_agregado - total_comparar_agregado):,} registros")
    else:
        reporte.append(f"  ✓ Totales agregados idénticos")
    
    reporte.append("")
    
    # Detalles por archivo
    reporte.append("DETALLES POR ARCHIVO:")
    reporte.append("-" * 40)
    
    for resultado in resultados_comparacion:
        estado = "✓ IDÉNTICA" if resultado['identica'] else "✗ DIFERENTE"
        reporte.append(f"  {resultado['archivo']}: {estado}")
        reporte.append(f"    Registros: {version_base}={resultado['total_base']:,}, {version_comparar}={resultado['total_comparar']:,}")
        reporte.append(f"    Valores únicos: {version_base}={resultado['valores_unicos_base']}, {version_comparar}={resultado['valores_unicos_comparar']}")
        reporte.append(f"    Valor más común: {version_base}='{resultado['valor_mas_comun_base']}', {version_comparar}='{resultado['valor_mas_comun_comparar']}'")
        reporte.append("")
    
    reporte.append("=" * 80)
    
    return "\n".join(reporte)

def main():
    """Función principal del verificador detallado."""
    
    # Verificar argumentos
    if len(sys.argv) != 3:
        print("Uso: python verificador_detallado.py <version_base> <version_comparar>")
        print("Ejemplo: python verificador_detallado.py anexo_v2 anexo_v4")
        sys.exit(1)
    
    version_base = sys.argv[1]
    version_comparar = sys.argv[2]
    
    print(f"Iniciando verificación detallada: {version_base} vs {version_comparar}")
    
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
    
    # Analizar cada archivo
    resultados_comparacion = []
    
    for archivo in sorted(archivos_base):
        print(f"  Analizando: {archivo}...")
        
        # Cargar datos
        ruta_base = os.path.join(dir_base, archivo)
        ruta_comparar = os.path.join(dir_comparar, archivo)
        
        if not os.path.exists(ruta_comparar):
            print(f"    ⚠️  Archivo no existe en {version_comparar}")
            continue
        
        try:
            df_base = pd.read_csv(ruta_base, sep='|', low_memory=False)
            df_comparar = pd.read_csv(ruta_comparar, sep='|', low_memory=False)
            
            # Analizar distribuciones
            dist_base = analizar_distribucion_resultados(df_base, archivo)
            dist_comparar = analizar_distribucion_resultados(df_comparar, archivo)
            
            # Comparar distribuciones
            resultado = comparar_distribuciones(dist_base, dist_comparar, archivo, version_base, version_comparar)
            resultados_comparacion.append(resultado)
            
        except Exception as e:
            print(f"    ❌ Error al analizar {archivo}: {e}")
    
    # Generar y mostrar reporte
    reporte = generar_reporte_detallado(resultados_comparacion, version_base, version_comparar)
    print(reporte)
    
    # Guardar reporte en archivo
    with open("reporte_verificacion_detallada.txt", "w") as f:
        f.write(reporte)
    
    print(f"Reporte guardado en: reporte_verificacion_detallada.txt")
    
    # Verificar si todas las distribuciones son idénticas
    todas_identicas = all(r['identica'] for r in resultados_comparacion)
    
    if todas_identicas:
        print(f"\n✅ ¡TODAS LAS DISTRIBUCIONES SON IDÉNTICAS!")
        print(f"   La lógica de asignación en {version_comparar} es consistente con {version_base}.")
    else:
        print(f"\n❌ HAY DIFERENCIAS EN LAS DISTRIBUCIONES")
        print(f"   Revisar el reporte detallado arriba.")
        sys.exit(1)

if __name__ == "__main__":
    main()