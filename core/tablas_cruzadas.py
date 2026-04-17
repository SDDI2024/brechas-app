"""
Módulo para generación de tablas cruzadas y cálculo de RRHH.
Adaptado de crear_tabla_cruzada y calcular_rrhh en anexo_v4_completo.py.
"""

import pandas as pd
import os
import logging

logger = logging.getLogger(__name__)

def generar_tabla_cruzada(df, año_anterior, escenario, digitos, carpeta_salida):
    """
    Genera tabla cruzada adaptada del anexo_v4_completo.py.
    
    Args:
        df: DataFrame combinado de resultados
        año_anterior: Año para filtrar datos (ej: 2023 si cálculo es 2024)
        escenario: 'A' o 'C' (favorece MF o MG)
        digitos: 3 o 4 (dígitos CIE-10)
        carpeta_salida: Nombre de carpeta de trabajo
        
    Returns:
        tuple: (tabla_original, tabla_sin, tabla_solo, tabla_completa, ruta_archivo)
    """
    # Construir tipo_archivo como en el original
    tipo_archivo = f"{escenario}_{digitos}D"
    
    # Directorio de resultados: data/results/{carpeta_salida}
    dir_resultados = f"data/results/{carpeta_salida}"
    os.makedirs(dir_resultados, exist_ok=True)
    
    # Filtrar por año (igual que original)
    df_año = df[df['anio'] == año_anterior]
    logger.info(f"Datos para año {año_anterior}: {len(df_año)} filas")
    
    # 1. Tabla cruzada original (SERVICIO × CENTRO)
    tabla_cruzada_original = pd.crosstab(
        df_año['SERVICIO'],
        df_año['CENTRO'],
        margins=False
    )
    
    # 2. Tabla cruzada sin 'SIN ASIGNACION' (RESULTADO × CENTRO)
    df_sin_sin_asignacion = df_año[df_año['RESULTADO DE TIPO ATENCION'] != 'SIN ASIGNACION']
    tabla_cruzada_sin_sin_asignacion = pd.crosstab(
        df_sin_sin_asignacion['RESULTADO DE TIPO ATENCION'],
        df_sin_sin_asignacion['CENTRO'],
        margins=False
    )
    tabla_cruzada_sin_sin_asignacion.index.name = 'SERVICIO'
    
    # 3. Tabla cruzada solo 'SIN ASIGNACION' (SERVICIO × CENTRO)
    df_solo_sin_asignacion = df_año[df_año['RESULTADO DE TIPO ATENCION'] == 'SIN ASIGNACION']
    tabla_cruzada_solo_sin_asignacion = pd.crosstab(
        df_solo_sin_asignacion['SERVICIO'],
        df_solo_sin_asignacion['CENTRO'],
        margins=False
    )
    
    # 4. Tabla cruzada completa (suma de 2 y 3)
    tabla_cruzada_completa = tabla_cruzada_sin_sin_asignacion.add(
        tabla_cruzada_solo_sin_asignacion, fill_value=0
    )
    
    # Log de dimensiones (igual que original)
    logger.info(f"Tabla cruzada original: {tabla_cruzada_original.shape[0]} filas x {tabla_cruzada_original.shape[1]} columnas")
    logger.info(f"Tabla cruzada sin 'SIN ASIGNACION': {tabla_cruzada_sin_sin_asignacion.shape[0]} filas x {tabla_cruzada_sin_sin_asignacion.shape[1]} columnas")
    logger.info(f"Tabla cruzada sólo 'SIN ASIGNACION': {tabla_cruzada_solo_sin_asignacion.shape[0]} filas x {tabla_cruzada_solo_sin_asignacion.shape[1]} columnas")
    logger.info(f"Tabla cruzada completa: {tabla_cruzada_completa.shape[0]} filas x {tabla_cruzada_completa.shape[1]} columnas")
    
    # Guardar en Excel (igual que original)
    nombre_archivo = f'tabla_cruzada_{tipo_archivo}_{carpeta_salida}.xlsx'
    ruta_completa = os.path.join(dir_resultados, nombre_archivo)
    
    with pd.ExcelWriter(ruta_completa, engine='openpyxl') as writer:
        tabla_cruzada_original.to_excel(writer, sheet_name='original')
        tabla_cruzada_sin_sin_asignacion.to_excel(writer, sheet_name='solo asignadas')
        tabla_cruzada_solo_sin_asignacion.to_excel(writer, sheet_name='solo NO asignadas')
        tabla_cruzada_completa.to_excel(writer, sheet_name='completa')
    
    logger.info(f"Tabla cruzada guardada: {nombre_archivo}")
    print(f"✅ Tabla cruzada guardada: {ruta_completa}")
    
    return tabla_cruzada_original, tabla_cruzada_sin_sin_asignacion, \
           tabla_cruzada_solo_sin_asignacion, tabla_cruzada_completa, ruta_completa

def combinar_resultados_por_escenario(resultados_dict, escenario):
    """
    Combina resultados de los 5 grupos para un escenario específico.
    
    Args:
        resultados_dict: Diccionario con DataFrames por grupo_escenario
        escenario: 'A' o 'C'
        
    Returns:
        DataFrame combinado
    """
    grupos = ['A', 'B', 'C', 'D', 'E']
    dataframes = []
    
    for grupo in grupos:
        clave = f"{grupo}_{escenario}"
        if clave in resultados_dict and not resultados_dict[clave].empty:
            dataframes.append(resultados_dict[clave])
    
    if dataframes:
        df_combinado = pd.concat(dataframes, ignore_index=True)
        logger.info(f"Resultados combinados para escenario {escenario}: {len(df_combinado)} filas")
        
        # Alinear valores de MG y MF (igual que original)
        df_combinado['RESULTADO DE TIPO ATENCION'] = df_combinado['RESULTADO DE TIPO ATENCION'].replace('MG', 'MEDICINA GENERAL')
        df_combinado['RESULTADO DE TIPO ATENCION'] = df_combinado['RESULTADO DE TIPO ATENCION'].replace('MF', 'MEDICINA FAMILIAR Y COMUNITARIA')
        df_combinado['RESULTADO DE TIPO ATENCION'] = df_combinado['RESULTADO DE TIPO ATENCION'].replace('CIRUGIA VASCULAR', 'CIRUGIA DE TORAX Y CARDIOVASCULAR')
        
        return df_combinado
    else:
        logger.warning(f"No se encontraron resultados para el escenario {escenario}")
        return pd.DataFrame()

def generar_tablas_cruzadas_para_digitos(resultados_dict, año_anterior, digitos, carpeta_salida):
    """
    Genera tablas cruzadas para ambos escenarios (A y C) de un número de dígitos.
    
    Args:
        resultados_dict: Diccionario con DataFrames por grupo_escenario
        año_anterior: Año para filtrar datos
        digitos: 3 o 4 (dígitos CIE-10)
        carpeta_salida: Nombre de carpeta de trabajo
        
    Returns:
        dict: Diccionario con resultados por escenario
    """
    resultados_tablas = {}
    escenarios = ['A', 'C']
    
    for escenario in escenarios:
        print(f"\n📊 Generando tabla cruzada para escenario {escenario} con {digitos} dígitos...")
        
        # Combinar resultados para este escenario
        df_combinado = combinar_resultados_por_escenario(resultados_dict, escenario)
        
        if df_combinado.empty:
            print(f"⚠️  No hay datos para escenario {escenario}")
            continue
        
        # Generar tabla cruzada
        try:
            tabla_original, tabla_sin, tabla_solo, tabla_completa, ruta_archivo = generar_tabla_cruzada(
                df=df_combinado,
                año_anterior=año_anterior,
                escenario=escenario,
                digitos=digitos,
                carpeta_salida=carpeta_salida
            )
            
            resultados_tablas[escenario] = {
                'original': tabla_original,
                'sin_sin_asignacion': tabla_sin,
                'solo_sin_asignacion': tabla_solo,
                'completa': tabla_completa,
                'ruta_archivo': ruta_archivo
            }
            
            print(f"✅ Tabla cruzada {escenario}_{digitos}D generada exitosamente")
            
        except Exception as e:
            print(f"❌ Error generando tabla cruzada para {escenario}_{digitos}D: {e}")
            logger.error(f"Error generando tabla cruzada para {escenario}_{digitos}D: {e}")
    
    return resultados_tablas

def cargar_datos_codigos(data_config='config'):
    """
    Carga los datos de códigos de centros y servicios.
    
    Args:
        data_config: Directorio de configuración (default: 'config')
        
    Returns:
        Tuple con (centro_df, servicio_df)
    """
    try:
        centro_df = pd.read_excel(f'{data_config}/codigos.xlsx', sheet_name=0)
        servicio_df = pd.read_excel(f'{data_config}/codigos.xlsx', sheet_name=1)
        logger.info(f"Datos de códigos cargados: {len(centro_df)} centros, {len(servicio_df)} servicios")
        print(f"✅ Datos de códigos cargados:")
        print(f"   • Centros: {len(centro_df)} registros")
        print(f"   • Servicios: {len(servicio_df)} registros")
        return centro_df, servicio_df
    except Exception as e:
        logger.error(f"Error al cargar datos de códigos: {e}")
        print(f"❌ Error al cargar datos de códigos: {e}")
        return None, None

def calcular_rrhh(tabla_cruzada, centro_df, servicio_df, verbose=False):
    """
    Calcula requerimientos de RRHH basados en tabla cruzada.
    
    Para cada valor: dividir entre 11, luego dividir entre CE de servicio si es > 0 
    o CE de centro si CE de servicio es == 0, luego entre rendimiento del servicio.
    
    Finalmente reemplazar los índices de centro por los valores que NOM_CENTRO según COD_CENTRO.
    
    Args:
        tabla_cruzada: DataFrame con tabla cruzada original
        centro_df: DataFrame con códigos de centros y valores CE
        servicio_df: DataFrame con servicios, rendimiento y valores CE
        verbose: Si True, muestra detalles de cálculo para algunos ejemplos
        
    Returns:
        DataFrame con valores de RRHH calculados
    """
    resultado = tabla_cruzada.astype(float)
    
    for servicio in resultado.index:
        for centro in resultado.columns:
            valor = resultado.loc[servicio, centro]
            if valor > 0:
                valor_rrhh = valor / 11
                
                # Buscar CE de servicio
                ce_servicio = servicio_df.loc[servicio_df['SERVICIO'] == servicio, 'CE'].values
                ce_servicio_val = ce_servicio[0] if len(ce_servicio) > 0 else 0
                
                if ce_servicio_val > 0:
                    valor_rrhh = valor_rrhh / ce_servicio_val
                else:
                    # Si CE de servicio es 0, usar CE de centro
                    ce_centro = centro_df.loc[centro_df['COD_CENTRO'] == centro, 'CE'].values
                    ce_centro_val = ce_centro[0] if len(ce_centro) > 0 else 0
                    if ce_centro_val > 0:
                        valor_rrhh = valor_rrhh / ce_centro_val
                
                # Dividir entre rendimiento del servicio
                rendimiento = servicio_df.loc[servicio_df['SERVICIO'] == servicio, 'RENDIMIENTO'].values
                rendimiento_val = rendimiento[0] if len(rendimiento) > 0 else 1
                if rendimiento_val > 0:
                    valor_rrhh = valor_rrhh / rendimiento_val
                
                resultado.loc[servicio, centro] = round(valor_rrhh)
                
                if verbose and servicio == resultado.index[0] and centro == resultado.columns[0]:
                    print(f"Ejemplo cálculo para {servicio} - {centro}:")
                    print(f"  Valor original: {valor}")
                    print(f"  /11: {valor/11}")
                    print(f"  CE servicio: {ce_servicio_val}")
                    print(f"  Rendimiento: {rendimiento_val}")
                    print(f"  Resultado: {round(valor_rrhh)}")
    
    # Reemplazar códigos de centro por nombres
    mapeo_centros = dict(zip(centro_df['COD_CENTRO'], centro_df['NOM_CENTRO']))
    resultado.columns = [mapeo_centros.get(col, col) for col in resultado.columns]
    
    # Agregar totales
    resultado['Total'] = resultado.sum(axis=1)
    resultado.loc['Total'] = resultado.sum(axis=0)
    
    return resultado.astype(int)

def calcular_rrhh_completo(tabla_original, tabla_sin, tabla_solo, tabla_completa, centro_df, servicio_df):
    """
    Calcula RRHH para las 4 tablas cruzadas.
    
    Args:
        tabla_original: Tabla cruzada original
        tabla_sin: Tabla sin 'SIN ASIGNACION'
        tabla_solo: Tabla solo 'SIN ASIGNACION'
        tabla_completa: Tabla completa
        centro_df: DataFrame con códigos de centros
        servicio_df: DataFrame con servicios
        
    Returns:
        dict: Diccionario con DataFrames de RRHH calculados
    """
    resultados = {}
    
    print(f"\n🧮 Calculando RRHH para 4 tablas...")
    
    # Calcular RRHH para cada tabla
    try:
        resultados['rrhh_original'] = calcular_rrhh(tabla_original, centro_df, servicio_df)
        print(f"✅ RRHH original calculado: {resultados['rrhh_original'].shape}")
        
        resultados['rrhh_con_asignacion'] = calcular_rrhh(tabla_sin, centro_df, servicio_df)
        print(f"✅ RRHH con asignación calculado: {resultados['rrhh_con_asignacion'].shape}")
        
        resultados['rrhh_solo_sin_asignacion'] = calcular_rrhh(tabla_solo, centro_df, servicio_df)
        print(f"✅ RRHH solo sin asignación calculado: {resultados['rrhh_solo_sin_asignacion'].shape}")
        
        resultados['rrhh_completa'] = calcular_rrhh(tabla_completa, centro_df, servicio_df)
        print(f"✅ RRHH completa calculado: {resultados['rrhh_completa'].shape}")
        
    except Exception as e:
        logger.error(f"Error calculando RRHH: {e}")
        print(f"❌ Error calculando RRHH: {e}")
        return {}
    
    return resultados

def guardar_rrhh_excel(resultados_rrhh, escenario, digitos, carpeta_salida, año_anterior):
    """
    Guarda los resultados de RRHH en un archivo Excel.
    
    Args:
        resultados_rrhh: Diccionario con DataFrames de RRHH
        escenario: 'A' o 'C'
        digitos: 3 o 4
        carpeta_salida: Nombre de carpeta de trabajo
        año_anterior: Año para el nombre del archivo
        
    Returns:
        str: Ruta del archivo guardado
    """
    if not resultados_rrhh:
        logger.warning("No hay resultados de RRHH para guardar")
        return None
    
    # Directorio de resultados
    dir_resultados = f"data/results/{carpeta_salida}"
    os.makedirs(dir_resultados, exist_ok=True)
    
    # Nombre del archivo
    nombre_archivo = f'rrhh_{escenario}_{digitos}D_{año_anterior}_{carpeta_salida}.xlsx'
    ruta_completa = os.path.join(dir_resultados, nombre_archivo)
    
    try:
        with pd.ExcelWriter(ruta_completa, engine='openpyxl') as writer:
            for nombre, df in resultados_rrhh.items():
                df.to_excel(writer, sheet_name=nombre)
        
        logger.info(f"RRHH guardado: {nombre_archivo}")
        print(f"✅ RRHH guardado: {ruta_completa}")
        return ruta_completa
        
    except Exception as e:
        logger.error(f"Error guardando RRHH: {e}")
        print(f"❌ Error guardando RRHH: {e}")
        return None

def crear_grafico_dumbbell(rrhh_original, rrhh_completa, escenario, digitos, carpeta_salida, año_anterior):
    """
    Crea un gráfico dumbbell simplificado para comparar RRHH original vs completo.
    Muestra TODOS los servicios con solo la diferencia.
    
    Args:
        rrhh_original: DataFrame con RRHH calculado de tabla original
        rrhh_completa: DataFrame con RRHH calculado completo
        escenario: 'A' o 'C'
        digitos: 3 o 4
        carpeta_salida: Nombre de carpeta de trabajo
        año_anterior: Año para el título del gráfico
        
    Returns:
        str: Ruta del archivo de gráfico guardado
    """
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    
    # Extraer valores totales de TODOS los servicios (excluyendo fila 'Total')
    servicios = []
    valores_original = []
    valores_completa = []
    
    for servicio in rrhh_original.index:
        if servicio != 'Total' and servicio in rrhh_completa.index:
            servicios.append(servicio)
            valores_original.append(rrhh_original.loc[servicio, 'Total'])
            valores_completa.append(rrhh_completa.loc[servicio, 'Total'])
    
    # Calcular diferencias
    diferencias = [c - o for o, c in zip(valores_original, valores_completa)]
    
    # Ordenar servicios por diferencia absoluta (de mayor a menor)
    datos = list(zip(servicios, valores_original, valores_completa, diferencias))
    datos.sort(key=lambda x: abs(x[3]), reverse=True)
    
    # Crear gráfico dumbbell simplificado
    fig, ax = plt.subplots(figsize=(12, max(8, len(datos) * 0.4)))  # Altura dinámica
    
    y_pos = range(len(datos))
    
    for i, (servicio, orig, comp, diff) in enumerate(datos):
        # Determinar color basado en la diferencia
        if diff > 0:
            line_color = 'green'  # Verde para aumento
        elif diff < 0:
            line_color = 'red'    # Rojo para disminución
        else:
            line_color = 'gray'   # Gris para sin cambio
        
        # Puntos original y completa (más pequeños y simples)
        ax.scatter(orig, i, color='blue', s=40, zorder=3, alpha=0.7)
        ax.scatter(comp, i, color='orange', s=40, zorder=3, alpha=0.7)
        
        # Línea conectada
        ax.hlines(i, orig, comp, colors=line_color, linewidth=1.5, zorder=2, alpha=0.8)
        
        # Anotar solo la diferencia (centrada)
        mid_point = (orig + comp) / 2
        diff_text = f'{int(diff):+d}'
        ax.text(mid_point, i, diff_text, ha='center', va='center', fontsize=8,
                fontweight='bold', color=line_color)
    
    ax.set_yticks(y_pos)
    ax.set_yticklabels([d[0] for d in datos], fontsize=9)
    ax.set_xlabel('RRHH', fontsize=10)

    subtitle = f'Escenario: Favorece a {escenario == "C" and "Medicina Familiar" or "Medicina General"} - Tipo análisis: {digitos} dígitos de CIE-10'
    
    ax.set_title(f'Comparación RRHH: Productividad vs Mixta (perfil epidemiológico - productividad) - {año_anterior+1}\n{subtitle}', 
                 fontsize=12, fontweight='bold')

    # Leyenda simple
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', markerfacecolor='blue', markersize=8, label='Productividad'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='orange', markersize=8, label='Mixta (perfil epidemiológico - productividad)'),
        Line2D([0], [0], color='green', linewidth=2, label='Aumento'),
        Line2D([0], [0], color='red', linewidth=2, label='Disminución')
    ]
    
    ax.legend(handles=legend_elements, loc='upper right', fontsize=8)
    ax.grid(True, alpha=0.1, linestyle='-')
    ax.set_axisbelow(True)
    
    # Ajustar márgenes
    plt.tight_layout()
    
    # Directorio de resultados
    dir_resultados = f"data/results/{carpeta_salida}"
    os.makedirs(dir_resultados, exist_ok=True)
    
    # Guardar gráfico
    nombre_archivo = f'grafico_dumbbell_{escenario}_{digitos}D_rrhh_comparacion_{año_anterior}_{carpeta_salida}.png'
    ruta_completa = os.path.join(dir_resultados, nombre_archivo)
    plt.savefig(ruta_completa, dpi=300, bbox_inches='tight')
    plt.close(fig)  # Cerrar figura para liberar memoria
    
    logger.info(f"Gráfico dumbbell guardado: {nombre_archivo}")
    print(f"📊 Gráfico dumbbell guardado: {ruta_completa}")
    
    return ruta_completa

def generar_graficos_dumbbell_para_escenario(resultados_rrhh, escenario, digitos, carpeta_salida, año_anterior):
    """
    Genera gráficos dumbbell para un escenario específico.
    
    Args:
        resultados_rrhh: Diccionario con DataFrames de RRHH
        escenario: 'A' o 'C'
        digitos: 3 o 4
        carpeta_salida: Nombre de carpeta de trabajo
        año_anterior: Año para el título del gráfico
        
    Returns:
        str: Ruta del archivo de gráfico guardado
    """
    if not resultados_rrhh:
        logger.warning(f"No hay resultados de RRHH para generar gráfico dumbbell ({escenario})")
        return None
    
    print(f"\n🎨 Generando gráfico dumbbell para escenario {escenario}...")
    
    try:
        # Obtener DataFrames de RRHH original y completa
        rrhh_original = resultados_rrhh.get('rrhh_original')
        rrhh_completa = resultados_rrhh.get('rrhh_completa')
        
        if rrhh_original is None or rrhh_completa is None:
            logger.warning(f"Faltan DataFrames de RRHH para gráfico dumbbell ({escenario})")
            print(f"⚠️  Faltan DataFrames de RRHH para gráfico dumbbell ({escenario})")
            return None
        
        # Crear gráfico dumbbell
        ruta_grafico = crear_grafico_dumbbell(
            rrhh_original=rrhh_original,
            rrhh_completa=rrhh_completa,
            escenario=escenario,
            digitos=digitos,
            carpeta_salida=carpeta_salida,
            año_anterior=año_anterior
        )
        
        if ruta_grafico:
            print(f"✅ Gráfico dumbbell generado para {escenario}_{digitos}D")
            return ruta_grafico
        else:
            print(f"❌ No se pudo generar gráfico dumbbell para {escenario}_{digitos}D")
            return None
            
    except Exception as e:
        logger.error(f"Error generando gráfico dumbbell para {escenario}: {e}")
        print(f"❌ Error generando gráfico dumbbell para {escenario}: {e}")
        return None