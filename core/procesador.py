"""
Procesador principal para cálculo de brechas de recursos humanos.

Contiene la lógica exacta de anexo_v4_completo.py organizada en clases y funciones.
"""

import pandas as pd
import warnings
import re
from datetime import timedelta
import os
import numpy as np
import time
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor, as_completed
import psutil
import logging

logger = logging.getLogger(__name__)

class ProcesadorBrechas:
    """Clase principal para procesamiento de brechas de recursos humanos."""
    
    def __init__(self, carpeta_salida, anio_calculo, ruta_datos, digitos_cie):
        """
        Inicializa el procesador.
        
        Args:
            carpeta_salida: Nombre de la carpeta de trabajo
            anio_calculo: Año para el cálculo de brechas
            ruta_datos: Ruta al archivo de datos de atenciones
            digitos_cie: Dígitos CIE-10 a usar (3 o 4)
        """
        self.carpeta_salida = carpeta_salida
        self.anio_calculo = anio_calculo
        self.ruta_datos = ruta_datos
        self.digitos_cie = digitos_cie
        
        # Configurar rutas
        self.dir_intermedio = f"data/intermediate/{carpeta_salida}"
        self.dir_resultados = f"data/results/{carpeta_salida}"
        self.data_config = 'config'
        
        # Configuración de paralelización
        self.num_cores = psutil.cpu_count(logical=False) or mp.cpu_count()
        
        # Datos cargados
        self.atenciones = None
        self.atenciones_por_grupo = {}
        self.votos_por_grupo = {}
        
        # Conteos para progreso
        self.conteos_registros_por_grupo = {}
        self.conteos_diagnosticos_por_grupo_tipo = {}
        
        logger.info(f"Procesador inicializado: {carpeta_salida}, año {anio_calculo}, {digitos_cie} dígitos")
    
    def ejecutar_asignaciones(self):
        """Ejecuta el flujo completo de asignaciones."""
        try:
            logger.info("Iniciando ejecución de asignaciones...")
            
            # 1. Cargar y preprocesar datos
            self._cargar_y_preprocesar_datos()
            
            # 2. Cargar datos de votos
            self._cargar_datos_votos()
            
            # 3. Ejecutar algoritmo en paralelo
            resultados = self._ejecutar_algoritmo_paralelo()
            
            logger.info(f"Asignaciones completadas: {len(resultados)} archivos generados")
            return True
            
        except Exception as e:
            logger.error(f"Error ejecutando asignaciones: {e}")
            return False
    
    def _cargar_y_preprocesar_datos(self):
        """Carga y preprocesa datos de atenciones médicas."""
        logger.info("Cargando y preprocesando datos de atenciones...")
        
        # Cargar datos (manteniendo lógica exacta)
        self.atenciones = pd.read_csv(
            self.ruta_datos, 
            sep='|', 
            encoding='ISO-8859-1', 
            low_memory=False, 
            parse_dates=['FECHA_ATENCION'], 
            dayfirst=True
        )
        logger.info(f"Datos cargados: {len(self.atenciones)} registros")
        
        # Filtros iniciales (igual que anexo_v4_completo.py)
        self.atenciones = self.atenciones[self.atenciones['CENTRO'] != '001']
        logger.info(f"Después de excluir centro 001: {len(self.atenciones)} registros")
        
        actividades_validas = ['ATENCION  MEDICA AMBULATORIA', 'ATENCION EN MEDICINA COMPLEMENTARIA']
        self.atenciones = self.atenciones[self.atenciones['ACTIVIDAD'].isin(actividades_validas)]
        logger.info(f"Después de filtrar actividades: {len(self.atenciones)} registros")
        
        # Agregar año
        self.atenciones['anio'] = self.atenciones['FECHA_ATENCION'].dt.year
        
        # Limpieza
        atenciones_limpias = self.atenciones.dropna(subset=['DIAGNOSTICO', 'FECHA_ATENCION', 'FECNACIMPACIENTE'])
        logger.info(f"Después de eliminar nulos: {len(atenciones_limpias)} registros")
        
        atenciones_limpias['SERVICIO'] = atenciones_limpias['SERVICIO'].str.strip()
        
        # Excluir servicios específicos
        servicios_excluir = [
            'MEDICO DE PERSONAL',
            'MEDICINA OCUPACIONAL Y DEL MEDIO AMBIENTE',
            'MEDICO DE CONTROL (MECO)'
        ]
        patron_excluir = '|'.join(re.escape(s) for s in servicios_excluir)
        atenciones_limpias = atenciones_limpias[~atenciones_limpias['SERVICIO'].str.contains(patron_excluir, case=False, na=False)]
        logger.info(f"Después de excluir servicios específicos: {len(atenciones_limpias)} registros")
        
        # Cálculo de edad (igual que original)
        atenciones_limpias['FECHA_ATENCION'] = pd.to_datetime(atenciones_limpias['FECHA_ATENCION'], format='%d/%m/%Y')
        atenciones_limpias['FECNACIMPACIENTE'] = pd.to_datetime(atenciones_limpias['FECNACIMPACIENTE'], format='%d/%m/%Y')
        
        atenciones_limpias['edad_meses'] = (
            (atenciones_limpias['FECHA_ATENCION'].dt.year - atenciones_limpias['FECNACIMPACIENTE'].dt.year) * 12 +
            (atenciones_limpias['FECHA_ATENCION'].dt.month - atenciones_limpias['FECNACIMPACIENTE'].dt.month) -
            np.where(atenciones_limpias['FECHA_ATENCION'].dt.day < atenciones_limpias['FECNACIMPACIENTE'].dt.day, 1, 0)
        )
        
        # Categorización etaria (igual que original)
        condiciones_edad = [
            (atenciones_limpias['edad_meses'] >= 1) & (atenciones_limpias['edad_meses'] < 60),
            (atenciones_limpias['edad_meses'] >= 60) & (atenciones_limpias['edad_meses'] < 216),
            (atenciones_limpias['edad_meses'] >= 216) & (atenciones_limpias['edad_meses'] < 360),
            (atenciones_limpias['edad_meses'] >= 360) & (atenciones_limpias['edad_meses'] < 720),
            (atenciones_limpias['edad_meses'] >= 720)
        ]
        categorias_edad = ['A', 'B', 'C', 'D', 'E']
        atenciones_limpias['categoria_edad'] = np.select(condiciones_edad, categorias_edad, default='N/A')
        
        # Excluir menores de 1 mes
        atenciones_limpias = atenciones_limpias[atenciones_limpias['edad_meses'] >= 1]
        logger.info(f"Después de excluir menores de 1 mes: {len(atenciones_limpias)} registros")
        
        # Homogeneización de servicios (igual que original)
        mapeo_servicios = {
            'GINECOLOGIA': 'GINECOLOGIA Y OBSTETRICIA',
            'HEMATOLOGIA': 'HEMATOLOGIA CLINICA',
            'REANIMACION Y TERAPIA DEL DOLOR': 'ANESTESIA, ANALGESIA Y REANIMACION',
            'CIRUGIA VASCULAR': 'CIRUGIA DE TORAX Y CARDIOVASCULAR'
        }
        atenciones_limpias['SERVICIO'] = atenciones_limpias['SERVICIO'].replace(mapeo_servicios)
        
        # Categorización de servicios
        atenciones_limpias['categoria_servicio'] = atenciones_limpias['SERVICIO'].apply(self._categorizar_servicio)
        
        # Dataset consolidado
        self.atenciones_consolidadas = atenciones_limpias[['ID', 'SERVICIO', 'DIAGNOSTICO', 'FECHA_ATENCION', 'categoria_edad', 'anio', 'CENTRO']]
        logger.info(f"Dataset consolidado: {len(self.atenciones_consolidadas)} registros")
        
        # División por grupos etarios
        self._dividir_por_grupos_etarios()
    
    def _dividir_por_grupos_etarios(self):
        """Divide los datos por grupos etarios."""
        logger.info("Dividiendo datos por grupos etarios...")
        
        grupos_etarios = ['A', 'B', 'C', 'D', 'E']
        
        for grupo in grupos_etarios:
            self.atenciones_por_grupo[grupo] = self.atenciones_consolidadas[
                self.atenciones_consolidadas['categoria_edad'] == grupo
            ]
            conteo = len(self.atenciones_por_grupo[grupo])
            self.conteos_registros_por_grupo[grupo] = conteo
            logger.info(f"  Grupo {grupo}: {conteo:,} registros")
    
    def _cargar_datos_votos(self):
        """Carga datos de votos por grupo etario."""
        logger.info("Cargando datos de votos...")
        
        grupos_etarios = ['A', 'B', 'C', 'D', 'E']
        tipos_voto = ['C', 'A']
        
        for grupo in grupos_etarios:
            self.votos_por_grupo[grupo] = {}
            for tipo in tipos_voto:
                ruta = f'{self.data_config}/DF_CONSOLIDADO_{grupo}_respuesta_votos_{tipo}.txt'
                votos_df = self._cargar_datos_votos_archivo(ruta)
                self.votos_por_grupo[grupo][tipo] = votos_df
                conteo = len(votos_df)
                self.conteos_diagnosticos_por_grupo_tipo[f"{grupo}_{tipo}"] = conteo
                logger.info(f"  Grupo {grupo}, tipo {tipo}: {conteo:,} diagnósticos")
    
    def _ejecutar_algoritmo_paralelo(self):
        """Ejecuta el algoritmo de asignación en paralelo con detalles de progreso."""
        print("\n" + "=" * 70)
        print("EJECUCIÓN PARALELIZADA DEL ALGORITMO")
        print("=" * 70)
        
        print(f"⚡ Sistema detectado: {self.num_cores} núcleos físicos disponibles")
        
        # Preparar combinaciones
        combinaciones = []
        grupos_etarios = ['E', 'D', 'C', 'B', 'A']  # Los más pesados primero
        tipos_voto = ['C', 'A']
        
        for grupo in grupos_etarios:
            for tipo in tipos_voto:
                combinaciones.append((
                    grupo, 
                    tipo, 
                    self.digitos_cie, 
                    self.atenciones_por_grupo[grupo], 
                    self.votos_por_grupo[grupo][tipo]
                ))
        
        print(f"📊 Total de combinaciones a procesar: {len(combinaciones)}")
        print(f"   • Grupos etarios: {', '.join(grupos_etarios)}")
        print(f"   • Tipos de votación: {', '.join(tipos_voto)} (C=favorece MF, A=favorece MG)")
        print(f"   • Dígitos CIE-10: {self.digitos_cie}")
        print(f"⚡ Procesando en paralelo usando {self.num_cores} núcleos...")
        
        # Procesar en paralelo
        resultados = []
        archivos_generados = []
        tiempos_procesamiento = []
        tiempo_total_inicio = time.time()
        
        # Mostrar resumen de volúmenes
        print("\n📊 RESUMEN DE VOLÚMENES:")
        print("-" * 50)
        
        total_registros = sum(self.conteos_registros_por_grupo.values())
        print(f"📈 Total registros a procesar: {total_registros:,}")
        print(f"📋 Distribución por grupos etarios:")
        
        for grupo in grupos_etarios:
            registros = self.conteos_registros_por_grupo.get(grupo, 0)
            porcentaje = (registros / total_registros * 100) if total_registros > 0 else 0
            diagnosticos_c = self.conteos_diagnosticos_por_grupo_tipo.get(f"{grupo}_C", 0)
            diagnosticos_a = self.conteos_diagnosticos_por_grupo_tipo.get(f"{grupo}_A", 0)
            print(f"  • Grupo {grupo}: {registros:,} registros ({porcentaje:.1f}%) - {diagnosticos_c}/{diagnosticos_a} diagnósticos (C/A)")
        
        print("\n📈 PROGRESO DE PROCESAMIENTO:")
        print("-" * 50)
        
        with ProcessPoolExecutor(max_workers=self.num_cores) as executor:
            futures = {}
            for combo in combinaciones:
                grupo, tipo, digitos, atenciones_grupo, votos_grupo_tipo = combo
                future = executor.submit(self._procesar_combinacion, combo)
                futures[future] = (grupo, tipo, digitos)
            
            # Mostrar progreso a medida que se completan (solo texto)
            completados = 0
            total = len(combinaciones)
            
            print(f"\n📈 Progreso del procesamiento:")
            print(f"   Total de combinaciones: {total}")
            print(f"   Núcleos utilizados: {self.num_cores}")
            print()
            
            # Definir hitos de progreso
            hitos = {25: False, 50: False, 75: False, 100: False}
            
            for future in as_completed(futures):
                grupo, tipo, digitos = futures[future]
                completados += 1
                
                try:
                    nombre_archivo, tiempo = future.result()
                    resultados.append((nombre_archivo, tiempo))
                    archivos_generados.append(nombre_archivo)
                    tiempos_procesamiento.append(tiempo)
                    
                    # Mostrar progreso con texto simple
                    porcentaje = (completados / total) * 100
                    print(f"   [{completados:2d}/{total}] {porcentaje:5.1f}% - {nombre_archivo} ({tiempo:.1f}s)")
                    
                    # Mostrar hitos de progreso
                    for hito_porcentaje, mostrado in hitos.items():
                        if not mostrado and porcentaje >= hito_porcentaje:
                            hitos[hito_porcentaje] = True
                            if hito_porcentaje == 100:
                                print(f"\n   🎉 {hito_porcentaje}% COMPLETADO - ¡Procesamiento terminado!")
                            else:
                                print(f"\n   ✅ {hito_porcentaje}% completado ({completados}/{total} combinaciones)")
                    
                except Exception as e:
                    print(f"   ❌ Error procesando {grupo}_{tipo}_{digitos}D: {e}")
        
        print()
        
        tiempo_total = time.time() - tiempo_total_inicio
        
        print("\n" + "=" * 70)
        print("RESUMEN DEL PROCESAMIENTO")
        print("=" * 70)
        print(f"⚡ Sistema: {self.num_cores} núcleos utilizados")
        print(f"📁 Directorio de salida: {self.dir_intermedio}/")
        print(f"📄 Total de archivos generados: {len(archivos_generados)}")
        print(f"👥 Grupos etarios procesados: {', '.join(grupos_etarios)}")
        print(f"🗳️  Tipos de votación: C (favorece Medicina Familiar), A (favorece Medicina General)")
        print(f"🔢 Dígitos CIE-10 procesados: {self.digitos_cie}")
        print(f"⏱️  Tiempo total de ejecución: {tiempo_total:.2f} segundos")
        
        if tiempos_procesamiento:
            print(f"📊 Tiempo promedio por combinación: {np.mean(tiempos_procesamiento):.2f} segundos")
            print(f"📈 Tiempo más rápido: {np.min(tiempos_procesamiento):.2f} segundos")
            print(f"📉 Tiempo más lento: {np.max(tiempos_procesamiento):.2f} segundos")
        
        print("\n📋 Archivos generados:")
        for archivo in sorted(archivos_generados):
            print(f"  • {archivo}")
        
        # Guardar tiempo de ejecución de asignaciones
        self._guardar_tiempo_asignaciones(tiempo_total)
        
        return resultados
    
    def _guardar_tiempo_asignaciones(self, tiempo_total):
        """Guarda el tiempo de ejecución de las asignaciones en un archivo markdown."""
        try:
            # Calcular número de combinaciones (5 grupos × 2 tipos = 10)
            num_combinaciones = 10  # 5 grupos etarios × 2 tipos de votación
            
            contenido = f"""# Tiempo de Ejecución - Asignaciones
## (Paso 5 - Lo que más demora)

## Parámetros
- Carpeta de trabajo: {self.carpeta_salida}
- Año de cálculo: {self.anio_calculo}
- Dígitos CIE-10: {self.digitos_cie}
- Fecha de ejecución: {time.strftime('%Y-%m-%d %H:%M:%S')}

## Tiempo de Asignaciones
**Tiempo total:** {tiempo_total:.2f} segundos
**Equivalente:** {tiempo_total/60:.2f} minutos

## Sistema
- Núcleos utilizados: {self.num_cores}
- Combinaciones procesadas: {num_combinaciones}
- Directorio intermedio: {self.dir_intermedio}

## Archivos Generados
- Resultado_[Grupo]_[Tipo]_[Dígitos]D_Nuevo.txt (10 archivos)

## Notas
Procesamiento de asignaciones completado exitosamente.
"""
            
            nombre_archivo = f'tiempo_asignaciones_{self.carpeta_salida}.md'
            ruta_salida = f'{self.dir_resultados}/{nombre_archivo}'
            
            with open(ruta_salida, 'w', encoding='utf-8') as f:
                f.write(contenido)
            
            logger.info(f"Tiempo de asignaciones guardado: {nombre_archivo}")
            print(f"📝 Tiempo de asignaciones guardado: {nombre_archivo}")
            
        except Exception as e:
            logger.error(f"Error guardando tiempo de asignaciones: {e}")
            print(f"⚠️  Error guardando tiempo de asignaciones: {e}")
    
    def _procesar_combinacion(self, args):
        """Procesa una combinación específica de grupo, tipo y dígitos."""
        grupo, tipo, digitos, atenciones_grupo, votos_grupo_tipo = args
        
        # Determinar nombre del archivo según convención original
        nombre_tipo_archivo = 'C' if tipo == 'C' else 'A'
        nombre_archivo = f'Resultado_{grupo}_{nombre_tipo_archivo}_{digitos}D_Nuevo.txt'
        
        # Obtener conteos para mostrar información detallada
        registros = len(atenciones_grupo)
        diagnosticos = len(votos_grupo_tipo)
        
        logger.info(f"  🚀 Iniciando: Grupo {grupo}, Tipo {tipo}, {digitos} dígitos")
        logger.info(f"     📊 Volumen: {registros:,} registros, {diagnosticos:,} diagnósticos")
        
        # Medir tiempo
        tiempo_inicio = time.time()
        
        # Ejecutar algoritmo optimizado
        resultado = self._algoritmo_asignacion_atenciones_optimizado(
            atenciones_grupo.copy(),
            votos_grupo_tipo,
            digitos,
            grupo=grupo,
            tipo=tipo
        )
        
        tiempo_procesamiento = time.time() - tiempo_inicio
        
        # Ordenar y guardar
        resultado = resultado.sort_index()
        ruta_salida = f'{self.dir_intermedio}/{nombre_archivo}'
        resultado.to_csv(ruta_salida, index=False, sep='|')
        
        return nombre_archivo, tiempo_procesamiento
    
    # ===== FUNCIONES AUXILIARES (manteniendo lógica exacta) =====
    
    def _cargar_datos_votos_archivo(self, ruta_archivo):
        """Carga y limpia datos de votos desde archivo CSV."""
        datos = pd.read_csv(ruta_archivo, sep='|', encoding='ISO-8859-1')
        datos = datos.map(lambda x: x.strip() if isinstance(x, str) else x)
        datos['_k'] = datos['_k'].astype(int)
        return datos
    
    def _categorizar_servicio(self, servicio):
        """Categoriza un servicio médico como MG, MF o ESPECIALISTA."""
        if servicio == 'MEDICINA GENERAL':
            return 'MG'
        elif servicio == 'MEDICINA FAMILIAR Y COMUNITARIA':
            return 'MF'
        else:
            return 'ESPECIALISTA'
    
    def _algoritmo_asignacion_atenciones_optimizado(self, atenciones_df, resultados_votos, numero_digitos_cie10, grupo="Desconocido", tipo="Desconocido"):
        """
        Versión optimizada del algoritmo de asignación.
        Mantiene lógica idéntica a anexo_v3_final.py pero optimizada para rendimiento.
        
        Args:
            atenciones_df: DataFrame de atenciones médicas
            resultados_votos: DataFrame de votos por diagnóstico
            numero_digitos_cie10: Número de dígitos CIE-10 a usar (3 o 4)
            grupo: Grupo etario (A, B, C, D, E)
            tipo: Tipo de votación (C o A)
        """
        warnings.simplefilter(action='ignore', category=FutureWarning)
        
        # Inicializar columnas (MISMA LÓGICA QUE V3)
        atenciones_df = atenciones_df.copy()
        atenciones_df['RESULTADO DE TIPO ATENCION'] = 'SIN ASIGNACION'
        atenciones_df['REVISADO'] = 'N'
        atenciones_df['FECHA_ATENCION'] = pd.to_datetime(atenciones_df['FECHA_ATENCION'], format='%d/%m/%Y')
        
        total_iteraciones = len(resultados_votos)
        
        # Definir hitos internos de progreso
        hitos_internos = {10: False, 25: False, 50: False, 75: False, 90: False}
        
        for indice, fila_voto in resultados_votos.iterrows():
            codigo_cie10 = fila_voto['CIE-10']
            resultado_voto = fila_voto['_resultado']
            k_valor = fila_voto['_k']
            
            # Mostrar progreso interno cada 100 iteraciones
            if indice % 100 == 0:
                logger.debug(f"Procesando Grupo {grupo}, Tipo {tipo}: iteración {indice} de {total_iteraciones}, diagnóstico: {codigo_cie10}")
            
            # Mostrar hitos de progreso interno
            porcentaje_interno = (indice / total_iteraciones) * 100
            for hito_porcentaje, mostrado in hitos_internos.items():
                if not mostrado and porcentaje_interno >= hito_porcentaje:
                    hitos_internos[hito_porcentaje] = True
                    logger.info(f"  📊 Progreso interno Grupo {grupo}, Tipo {tipo}: {hito_porcentaje}% ({indice:,}/{total_iteraciones:,} diagnósticos procesados)")
            
            # Filtrar según dígitos CIE-10 (MISMA LÓGICA QUE V3)
            if numero_digitos_cie10 == 3:
                # Usar primeros 3 dígitos para matching (igual que v3)
                codigo_prefix = str(codigo_cie10)[:3]
                # Convertir a string y manejar NaN para matching consistente
                atenciones_filtradas = atenciones_df.loc[
                    atenciones_df['DIAGNOSTICO'].fillna('').astype(str).str.startswith(codigo_prefix) & 
                    (atenciones_df['REVISADO'] == 'N')
                ]
            else:
                # Usar código completo para matching exacto
                atenciones_filtradas = atenciones_df[
                    (atenciones_df['DIAGNOSTICO'] == codigo_cie10) & 
                    (atenciones_df['REVISADO'] == 'N')
                ]
            
            # Filtrar atenciones de 2023 (MISMA LÓGICA)
            atenciones_2023 = atenciones_filtradas.loc[atenciones_filtradas['anio'] == 2023]
            
            # CASO 1: Voto es MF o MG - asignar TODAS las atenciones (MISMA LÓGICA)
            if resultado_voto == 'MF' or resultado_voto == 'MG':
                indices = atenciones_filtradas.index
                atenciones_df.loc[indices, 'RESULTADO DE TIPO ATENCION'] = resultado_voto
                atenciones_df.loc[indices, 'REVISADO'] = 'S'
                # NO usar continue aquí para mantener lógica idéntica a v3
            
            # CASO 2: Voto es otra especialidad - aplicar lógica de k (MISMA LÓGICA)
            if resultado_voto != 'MF' and resultado_voto != 'MG':
                if not atenciones_2023.empty:
                    # Ordenar por fecha para encontrar primera atención de 2023
                    atenciones_ordenadas = atenciones_2023.sort_values(by='FECHA_ATENCION', ascending=True)
                    
                    # Iterar sobre cada fila de atenciones_ordenadas (MISMA LÓGICA QUE V3)
                    for _, fila_atencion in atenciones_ordenadas.iterrows():
                        id_paciente = fila_atencion['ID']
                        primera_fecha_2023 = fila_atencion['FECHA_ATENCION']
                        fecha_limite = primera_fecha_2023 - timedelta(days=365)
                        
                        # Encontrar atenciones del paciente en el último año
                        indices_paciente = atenciones_filtradas[
                            (atenciones_filtradas['ID'] == id_paciente) &
                            (atenciones_filtradas['FECHA_ATENCION'] >= fecha_limite) &
                            (atenciones_filtradas['REVISADO'] == 'N')
                        ].index
                        
                        # APLICAR REGLAS SEGÚN k_valor (LÓGICA IDÉNTICA A V3)
                        if k_valor == 1:
                            atenciones_df.loc[indices_paciente, ['RESULTADO DE TIPO ATENCION', 'REVISADO']] = [resultado_voto, 'S']
                        
                        if k_valor == 2:
                            atenciones_df.loc[indices_paciente[:1], ['RESULTADO DE TIPO ATENCION', 'REVISADO']] = ['MF', 'S']
                            atenciones_df.loc[indices_paciente[1:], ['RESULTADO DE TIPO ATENCION', 'REVISADO']] = [resultado_voto, 'S']
                        
                        if k_valor == 3:
                            atenciones_df.loc[indices_paciente[:2], ['RESULTADO DE TIPO ATENCION', 'REVISADO']] = ['MF', 'S']
                            atenciones_df.loc[indices_paciente[2:], ['RESULTADO DE TIPO ATENCION', 'REVISADO']] = [resultado_voto, 'S']
                        
                        if k_valor == 4:
                            atenciones_df.loc[indices_paciente[:3], ['RESULTADO DE TIPO ATENCION', 'REVISADO']] = ['MF', 'S']
                            atenciones_df.loc[indices_paciente[3:], ['RESULTADO DE TIPO ATENCION', 'REVISADO']] = [resultado_voto, 'S']
                        
                        if k_valor == 5:
                            atenciones_df.loc[indices_paciente[:4], ['RESULTADO DE TIPO ATENCION', 'REVISADO']] = ['MF', 'S']
                            atenciones_df.loc[indices_paciente[4:], ['RESULTADO DE TIPO ATENCION', 'REVISADO']] = [resultado_voto, 'S']
        
        warnings.simplefilter("default", FutureWarning)
        return atenciones_df