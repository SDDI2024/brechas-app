import os
import pandas as pd
import logging
logger = logging.getLogger(__name__)

def cargar_resultados_intermedios(ruta_base, digitos_cie):
    """
    Carga los 10 archivos de resultados intermedios.

    Args:
    ruta_base: Ruta base donde están los archivos (ej: data/intermediate/{carpeta_salida})
    digitos_cie: Dígitos CIE-10 usados (3 o 4)

    Returns:
    dict: Diccionario con DataFrames organizados por grupo y escenario
    """

    grupos = ['A', 'B', 'C', 'D', 'E' ]
    escenarios = ['A', 'C']
    resultados = {}

    for grupo in grupos:
        for escenario in escenarios:
            archivo = f"Resultado_{grupo}_{escenario}_{digitos_cie}D_Nuevo.txt"
            ruta_completa = os.path.join(ruta_base, archivo)

            if os.path.exists(ruta_completa):
                df = pd.read_csv(ruta_completa, sep='|', encoding='utf-8')
                resultados[f"{grupo}_{escenario}"] = df
                logger.info(f"Cargado: {archivo} - {len(df)} registros")
            else:
                logger.warning(f"Archivo no encontrado: {ruta_completa}")
                resultados[f"{grupo}_{escenario}"] = pd.DataFrame()

    return resultados