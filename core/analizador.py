"""
Analizador de resultados para cálculo de brechas de recursos humanos.

Genera análisis estadístico y gráficos basados en los resultados
de las asignaciones, exactamente como en anexo_v4_completo.py.
"""

import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
import logging
from .io_operations import cargar_resultados_intermedios
from .tablas_cruzadas import (
    generar_tablas_cruzadas_para_digitos,
    cargar_datos_codigos,
    calcular_rrhh_completo,
    guardar_rrhh_excel,
    generar_graficos_dumbbell_para_escenario
)
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill
from openpyxl.utils import get_column_letter


logger = logging.getLogger(__name__)

class AnalizadorResultados:
    """Clase para análisis de resultados y generación de gráficos."""
    
    def __init__(self, carpeta_salida, digitos_cie, anio_calculo):
        """
        Inicializa el analizador.
        
        Args:
            carpeta_salida: Nombre de la carpeta de trabajo
            digitos_cie: Dígitos CIE-10 usados (3 o 4)
            anio_calculo: Año del cálculo de brecha. Como el cálculo se hace en base al año anterior año queda en año menos 1
        """
        self.carpeta_salida = carpeta_salida
        self.digitos_cie = digitos_cie
        self.anio_anterior = anio_calculo - 1
        # Configurar rutas
        self.dir_intermedio = f"data/intermediate/{carpeta_salida}"
        self.dir_resultados = f"data/results/{carpeta_salida}"
        self.data_config = 'config'
        
        logger.info(f"Analizador inicializado: {carpeta_salida}, {digitos_cie} dígitos")
    
    def ejecutar_analisis(self):
        """Ejecuta el análisis completo de resultados."""
        try:
            print(f"\n{'='*60}")
            print("ANÁLISIS DE RESULTADOS")
            print(f"{'='*60}")
            print(f"📂 Carpeta de trabajo: {self.carpeta_salida}")
            print(f"🔢 Dígitos CIE-10: {self.digitos_cie}")
            print(f"📅 Año anterior (para filtrar): {self.anio_anterior}")
            
            # 1. Cargar resultados intermedios
            print(f"\n📥 Cargando resultados intermedios...")
            resultados = self._cargar_resultados_intermedios()
            
            if not resultados:
                print("❌ No se pudieron cargar resultados intermedios")
                return False
            
            # Contar archivos cargados exitosamente
            archivos_cargados = sum(1 for df in resultados.values() if not df.empty)
            print(f"✅ Archivos cargados: {archivos_cargados}/10")
            
            # 2. Generar tablas cruzadas para ambos escenarios (A y C)
            print(f"\n📊 Generando tablas cruzadas para {self.digitos_cie} dígitos...")
            tablas_cruzadas = generar_tablas_cruzadas_para_digitos(
                resultados_dict=resultados,
                año_anterior=self.anio_anterior,
                digitos=self.digitos_cie,
                carpeta_salida=self.carpeta_salida
            )
            
            if not tablas_cruzadas:
                print("❌ No se pudieron generar tablas cruzadas")
                return False
            
            print(f"\n✅ Tablas cruzadas generadas: {len(tablas_cruzadas)}")
            
            # 3. Calcular RRHH para cada escenario
            print(f"\n{'='*60}")
            print("CÁLCULO DE RRHH")
            print(f"{'='*60}")
            
            resultados_rrhh = self._calcular_brechas_rrhh(tablas_cruzadas)
            
            if not resultados_rrhh:
                print("❌ No se pudieron calcular RRHH")
                return False
            
            print(f"\n✅ RRHH calculados para: {len(resultados_rrhh)} escenarios")
            
            # 4. Generar gráficos dumbbell
            graficos_dumbbell = self._generar_graficos_dumbbell(resultados_rrhh)
            
            print(f"\n✅ Análisis completado exitosamente")
            print(f"📊 Resultados generados:")
            print(f"   • Tablas cruzadas: {len(tablas_cruzadas)}")
            print(f"   • RRHH calculados: {len(resultados_rrhh)}")
            print(f"   • Gráficos dumbbell: {len(graficos_dumbbell)}")
            
            # Mostrar resumen de archivos generados
            print(f"\n📄 ARCHIVOS GENERADOS:")
            print(f"   Tablas cruzadas:")
            for escenario, datos in tablas_cruzadas.items():
                if 'ruta_archivo' in datos:
                    print(f"     • {escenario}_{self.digitos_cie}D: {datos['ruta_archivo']}")
            
            print(f"   RRHH calculados:")
            for escenario, datos in resultados_rrhh.items():
                if 'ruta_archivo' in datos:
                    print(f"     • {escenario}_{self.digitos_cie}D: {datos['ruta_archivo']}")
            
            print(f"   Gráficos dumbbell:")
            for escenario, ruta in graficos_dumbbell.items():
                print(f"     • {escenario}_{self.digitos_cie}D: {ruta}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error ejecutando análisis: {e}")
            logger.error(f"Error ejecutando análisis: {e}")
            return False

    def _cargar_resultados_intermedios(self):
        """Carga todos los resultados intermedios generados."""
        return cargar_resultados_intermedios(self.dir_intermedio, self.digitos_cie)
    
    def _generar_tablas_cruzadas(self, resultados):
        """
        Genera tablas cruzadas de resultados.
        
        Args:
            resultados: Diccionario con DataFrames por grupo_escenario
            
        Returns:
            dict: Diccionario con tablas cruzadas por escenario
        """
        return generar_tablas_cruzadas_para_digitos(
            resultados_dict=resultados,
            año_anterior=self.anio_anterior,
            digitos=self.digitos_cie,
            carpeta_salida=self.carpeta_salida
        )
    
    def _calcular_brechas_rrhh(self, tablas_cruzadas):
        """
        Calcula brechas de recursos humanos como en anexo_v4_completo.py.
        
        Args:
            tablas_cruzadas: Diccionario con tablas cruzadas por escenario
            
        Returns:
            dict: Diccionario con resultados de RRHH por escenario
        """
        resultados_rrhh = {}
        
        if not tablas_cruzadas:
            logger.warning("No hay tablas cruzadas para calcular RRHH")
            return resultados_rrhh
        
        # Cargar datos de códigos
        print(f"\n📋 Cargando datos de códigos...")
        centro_df, servicio_df = cargar_datos_codigos(self.data_config)
        
        if centro_df is None or servicio_df is None:
            print("❌ No se pudieron cargar datos de códigos")
            return resultados_rrhh
        
        # Calcular RRHH para cada escenario
        for escenario, datos_tablas in tablas_cruzadas.items():
            print(f"\n🧮 Calculando RRHH para escenario {escenario}...")
            
            try:
                resultados = calcular_rrhh_completo(
                    tabla_original=datos_tablas['original'],
                    tabla_sin=datos_tablas['sin_sin_asignacion'],
                    tabla_solo=datos_tablas['solo_sin_asignacion'],
                    tabla_completa=datos_tablas['completa'],
                    centro_df=centro_df,
                    servicio_df=servicio_df
                )
                
                if resultados:
                    # Guardar en Excel
                    ruta_archivo = guardar_rrhh_excel(
                        resultados_rrhh=resultados,
                        escenario=escenario,
                        digitos=self.digitos_cie,
                        carpeta_salida=self.carpeta_salida,
                        año_anterior=self.anio_anterior
                    )
                    
                    if ruta_archivo:
                        resultados['ruta_archivo'] = ruta_archivo
                        resultados_rrhh[escenario] = resultados
                        print(f"✅ RRHH para {escenario} calculado y guardado")
                    else:
                        print(f"⚠️  RRHH calculado pero no guardado para {escenario}")
                else:
                    print(f"❌ No se pudieron calcular RRHH para {escenario}")
                    
            except Exception as e:
                logger.error(f"Error calculando RRHH para {escenario}: {e}")
                print(f"❌ Error calculando RRHH para {escenario}: {e}")
        
        return resultados_rrhh
    
    def _calcular_rrhh_completo(self, tabla_cruzada, centro_df, servicio_df):
        """
        Calcula RRHH como en anexo_v4_completo.py.
        
        Para cada valor: dividir entre 11, luego dividir entre CE de servicio si es > 0 
        o CE de centro si CE de servicio es == 0, luego entre rendimiento del servicio.
        
        Args:
            tabla_cruzada: DataFrame con tabla cruzada
            centro_df: DataFrame con códigos de centros
            servicio_df: DataFrame con servicios
            
        Returns:
            DataFrame con RRHH calculado
        """
        from .tablas_cruzadas import calcular_rrhh
        return calcular_rrhh(tabla_cruzada, centro_df, servicio_df)
    
    def _generar_graficos_dumbbell(self, resultados_rrhh):
        """
        Genera gráficos dumbbell desde los resultados de RRHH.
        
        Args:
            resultados_rrhh: Diccionario con resultados de RRHH por escenario
            
        Returns:
            dict: Diccionario con rutas de gráficos generados por escenario
        """
        graficos_generados = {}
        
        if not resultados_rrhh:
            logger.warning("No hay resultados de RRHH para generar gráficos dumbbell")
            return graficos_generados
        
        print(f"\n{'='*60}")
        print("GENERACIÓN DE GRÁFICOS DUMBBELL")
        print(f"{'='*60}")
        
        for escenario, datos_rrhh in resultados_rrhh.items():
            print(f"\n🎨 Generando gráfico dumbbell para escenario {escenario}...")
            
            try:
                ruta_grafico = generar_graficos_dumbbell_para_escenario(
                    resultados_rrhh=datos_rrhh,
                    escenario=escenario,
                    digitos=self.digitos_cie,
                    carpeta_salida=self.carpeta_salida,
                    año_anterior=self.anio_anterior
                )
                
                if ruta_grafico:
                    graficos_generados[escenario] = ruta_grafico
                    print(f"✅ Gráfico dumbbell generado: {os.path.basename(ruta_grafico)}")
                else:
                    print(f"⚠️  No se pudo generar gráfico dumbbell para {escenario}")
                    
            except Exception as e:
                logger.error(f"Error generando gráfico dumbbell para {escenario}: {e}")
                print(f"❌ Error generando gráfico dumbbell para {escenario}: {e}")
        
        return graficos_generados
    
    def _guardar_tiempo_total(self, tiempo_total, tiempo_asignaciones=None):
        """
        Guarda el tiempo total de ejecución del análisis.
        
        Args:
            tiempo_total: Tiempo total del análisis completo (segundos)
            tiempo_asignaciones: Tiempo de ejecución de asignaciones (segundos, opcional)
        """
        try:
            contenido = f"""# Tiempo de Ejecución - Análisis Completo

## Parámetros
- Carpeta de trabajo: {self.carpeta_salida}
- Dígitos CIE-10: {self.digitos_cie}
- Año de cálculo: {self.anio_calculo + 1}  # Nota: anio_calculo es el año anterior usado para filtrar
- Año para filtrar: {self.anio_anterior}
- Fecha de ejecución: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}

## Tiempos de Ejecución
**Tiempo total del análisis:** {tiempo_total:.2f} segundos
**Equivalente:** {tiempo_total/60:.2f} minutos
**Equivalente:** {tiempo_total/3600:.2f} horas"""

            if tiempo_asignaciones:
                contenido += f"""

**Tiempo de asignaciones (Paso 5):** {tiempo_asignaciones:.2f} segundos
**Porcentaje del total:** {(tiempo_asignaciones/tiempo_total)*100:.1f}%
**Tiempo de análisis (sin asignaciones):** {tiempo_total - tiempo_asignaciones:.2f} segundos"""

            contenido += f"""

## Componentes Procesados
- Resultados intermedios cargados: 10 archivos (5 grupos × 2 escenarios)
- Tablas cruzadas generadas: 2 escenarios (A y C)
- RRHH calculados: 2 escenarios × 4 tablas = 8 cálculos
- Gráficos dumbbell generados: 2

## Archivos Generados
- Tablas cruzadas: tabla_cruzada_[A,C]_{self.digitos_cie}D_{self.carpeta_salida}.xlsx
- RRHH calculados: rrhh_[A,C]_{self.digitos_cie}D_{self.anio_anterior}_{self.carpeta_salida}.xlsx
- Gráficos dumbbell: grafico_dumbbell_[A,C]_{self.digitos_cie}D_rrhh_comparacion_{self.anio_anterior}_{self.carpeta_salida}.png

## Directorios
- Intermedio: {self.dir_intermedio}
- Resultados: {self.dir_resultados}

## Notas
Análisis completado exitosamente. Los tiempos pueden variar según:
1. Volumen de datos procesados
2. Capacidad del sistema (CPU, RAM)
3. Carga del sistema durante la ejecución
"""
            
            nombre_archivo = f'tiempo_total_{self.carpeta_salida}.md'
            ruta_completa = os.path.join(self.dir_resultados, nombre_archivo)
            
            with open(ruta_completa, 'w', encoding='utf-8') as f:
                f.write(contenido)
            
            logger.info(f"Tiempo total guardado: {nombre_archivo}")
            print(f"📝 Tiempo total guardado: {ruta_completa}")
            
            return ruta_completa
            
        except Exception as e:
            logger.error(f"Error guardando tiempo total: {e}")
            print(f"⚠️  Error guardando tiempo total: {e}")
            return None
    
    def _obtener_tiempo_asignaciones(self):
        """
        Intenta obtener el tiempo de ejecución de asignaciones desde archivo.
        
        Returns:
            float: Tiempo en segundos o None si no se encuentra
        """
        # Buscar archivo de tiempo de asignaciones
        patron = f'tiempo_asignaciones_{self.carpeta_salida}.md'
        ruta_posible = os.path.join(self.dir_resultados, patron)
        
        if os.path.exists(ruta_posible):
            try:
                with open(ruta_posible, 'r', encoding='utf-8') as f:
                    contenido = f.read()
                
                # Buscar línea con "Tiempo total:"
                for linea in contenido.split('\n'):
                    if '**Tiempo total:**' in linea:
                        # Extraer número: "**Tiempo total:** 123.45 segundos"
                        partes = linea.split('**Tiempo total:**')
                        if len(partes) > 1:
                            valor = partes[1].strip().split()[0]  # "123.45"
                            return float(valor)
            except Exception as e:
                logger.warning(f"Error leyendo tiempo de asignaciones: {e}")
        
        # También buscar en el directorio intermedio (por si el procesador lo guardó allí)
        dir_intermedio_resultados = f"data/results/{self.carpeta_salida}"
        if os.path.exists(dir_intermedio_resultados):
            for archivo in os.listdir(dir_intermedio_resultados):
                if archivo.startswith('tiempo_asignaciones_'):
                    ruta_completa = os.path.join(dir_intermedio_resultados, archivo)
                    try:
                        with open(ruta_completa, 'r', encoding='utf-8') as f:
                            contenido = f.read()
                        
                        for linea in contenido.split('\n'):
                            if '**Tiempo total:**' in linea:
                                partes = linea.split('**Tiempo total:**')
                                if len(partes) > 1:
                                    valor = partes[1].strip().split()[0]
                                    return float(valor)
                    except Exception as e:
                        logger.warning(f"Error leyendo {archivo}: {e}")
        
        return None
    
    def _generar_metricas_tiempo(self, tiempo_total, tiempo_asignaciones=None):
        """
        Genera métricas de tiempo de ejecución del análisis.
        
        Args:
            tiempo_total: Tiempo total del análisis (segundos)
            tiempo_asignaciones: Tiempo de asignaciones (segundos, opcional)
        """
        print(f"\n{'='*60}")
        print("MÉTRICAS DE TIEMPO DE EJECUCIÓN")
        print(f"{'='*60}")
        
        print(f"⏱️  Tiempo total del análisis: {tiempo_total:.2f} segundos")
        print(f"   • Equivalente: {tiempo_total/60:.2f} minutos")
        print(f"   • Equivalente: {tiempo_total/3600:.2f} horas")
        
        if tiempo_asignaciones:
            print(f"\n📊 Desglose de tiempos:")
            print(f"   • Asignaciones (Paso 5): {tiempo_asignaciones:.2f} segundos ({tiempo_asignaciones/60:.2f} min)")
            print(f"   • Análisis (sin asignaciones): {tiempo_total - tiempo_asignaciones:.2f} segundos ({(tiempo_total - tiempo_asignaciones)/60:.2f} min)")
            print(f"   • Porcentaje asignaciones/total: {(tiempo_asignaciones/tiempo_total)*100:.1f}%")
        
        print(f"\n⚡ Rendimiento:")
        print(f"   • Tiempo por archivo intermedio: {tiempo_total/10:.2f} segundos")
        print(f"   • Tiempo por escenario procesado: {tiempo_total/2:.2f} segundos")
        
        if tiempo_asignaciones:
            print(f"   • Tiempo por combinación de asignación: {tiempo_asignaciones/10:.2f} segundos")