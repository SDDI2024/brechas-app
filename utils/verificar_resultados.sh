#!/usr/bin/env bash
# Script para verificar resultados entre versiones del código

echo "================================================"
echo "VERIFICADOR DE RESULTADOS - Brechas App"
echo "================================================"
echo ""

# Colores para data/intermediate
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Variables globales
VERSION_BASE=""
VERSION_COMPARAR=""

# Función para mostrar mensajes
info() {
    echo -e "${YELLOW}[INFO]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Seleccionar versiones a comparar
seleccionar_versiones() {
    echo "Versiones disponibles en directorio 'data/intermediate/':"
    echo ""
    
    # Listar directorios que comienzan con 'anexo_'
    versiones=()
    i=1
    for dir in data/intermediate/a*; do
        if [ -d "$dir" ]; then
            version=$(basename "$dir")
            versiones+=("$version")
            echo "  $i) $version"
            i=$((i + 1))
        fi
    done
    
    if [ ${#versiones[@]} -eq 0 ]; then
        error "No se encontraron versiones en el directorio 'data/intermediate/'"
        exit 1
    fi
    
    echo ""
    read -p "Seleccione versión BASE (número): " opcion_base
    
    if ! [[ "$opcion_base" =~ ^[0-9]+$ ]] || [ "$opcion_base" -lt 1 ] || [ "$opcion_base" -gt ${#versiones[@]} ]; then
        error "Opción no válida"
        exit 1
    fi
    
    VERSION_BASE="${versiones[$((opcion_base - 1))]}"
    
    echo ""
    read -p "Seleccione versión a COMPARAR (número): " opcion_comparar
    
    if ! [[ "$opcion_comparar" =~ ^[0-9]+$ ]] || [ "$opcion_comparar" -lt 1 ] || [ "$opcion_comparar" -gt ${#versiones[@]} ]; then
        error "Opción no válida"
        exit 1
    fi
    
    VERSION_COMPARAR="${versiones[$((opcion_comparar - 1))]}"
    
    if [ "$VERSION_BASE" = "$VERSION_COMPARAR" ]; then
        error "No puede comparar la misma versión consigo misma"
        exit 1
    fi
    
    echo ""
    info "Comparando: $VERSION_BASE (base) vs $VERSION_COMPARAR (comparar)"
    echo ""
}

# Verificar que existen los directorios
check_directories() {
    info "Verificando directorios de resultados..."
    
    if [ ! -d "data/intermediate/$VERSION_BASE" ]; then
        error "Directorio data/intermediate/$VERSION_BASE no existe"
        return 1
    fi
    
    if [ ! -d "data/intermediate/$VERSION_COMPARAR" ]; then
        error "Directorio data/intermediate/$VERSION_COMPARAR no existe"
        return 1
    fi
    
    success "Directorios verificados"
    return 0
}

# Contar archivos en cada directorio
count_files() {
    info "Contando archivos..."
    
    count_base=$(ls -1 "data/intermediate/$VERSION_BASE"/*.txt 2>/dev/null | wc -l)
    count_compare=$(ls -1 "data/intermediate/$VERSION_COMPARAR"/*.txt 2>/dev/null | wc -l)
    
    echo "  $VERSION_BASE: $count_base archivos"
    echo "  $VERSION_COMPARAR: $count_compare archivos"
    
    if [ "$count_base" -eq "$count_compare" ]; then
        success "Mismo número de archivos en ambos directorios"
        return 0
    else
        error "Diferente número de archivos: $VERSION_BASE=$count_base, $VERSION_COMPARAR=$count_compare"
        return 1
    fi
}

# Verificar tamaños de archivos
check_file_sizes() {
    info "Verificando tamaños de archivos..."
    
    differences=0
    for file in "data/intermediate/$VERSION_BASE"/*.txt; do
        filename=$(basename "$file")
        file_base="data/intermediate/$VERSION_BASE/$filename"
        file_compare="data/intermediate/$VERSION_COMPARAR/$filename"
        
        if [ -f "$file_compare" ]; then
            size_base=$(stat -c%s "$file_base")
            size_compare=$(stat -c%s "$file_compare")
            
            if [ "$size_base" -eq "$size_compare" ]; then
                echo "  ✓ $filename: $size_base bytes"
            else
                echo "  ✗ $filename: $VERSION_BASE=$size_base, $VERSION_COMPARAR=$size_compare"
                differences=$((differences + 1))
            fi
        else
            echo "  ✗ $filename: No existe en $VERSION_COMPARAR"
            differences=$((differences + 1))
        fi
    done
    
    if [ "$differences" -eq 0 ]; then
        success "Todos los archivos tienen el mismo tamaño"
        return 0
    else
        error "Se encontraron $differences archivos con diferencias de tamaño"
        return 1
    fi
}

# Ejecutar verificador Python
run_python_verifier() {
    info "Ejecutando verificador Python..."
    
    if [ -f "utils/verificador_resultados.py" ]; then
        # Pasar las versiones como argumentos al script Python
        python utils/verificador_resultados.py "$VERSION_BASE" "$VERSION_COMPARAR"
        return $?
    else
        error "Archivo utils/verificador_resultados.py no encontrado"
        return 1
    fi
}

# Ejecutar verificador detallado
run_detailed_verifier() {
    info "Ejecutando verificador detallado..."
    
    if [ -f "utils/verificador_detallado.py" ]; then
        # Pasar las versiones como argumentos al script Python
        python utils/verificador_detallado.py "$VERSION_BASE" "$VERSION_COMPARAR"
        return $?
    else
        error "Archivo utils/verificador_detallado.py no encontrado"
        return 1
    fi
}

# Mostrar resumen
show_summary() {
    echo ""
    echo "================================================"
    echo "RESUMEN DE VERIFICACIÓN"
    echo "================================================"
    echo "Comparación: $VERSION_BASE vs $VERSION_COMPARAR"
    echo ""
    
    if [ -f "comparacion_resultados.txt" ]; then
        echo "Resumen guardado en: comparacion_resultados.txt"
        tail -20 comparacion_resultados.txt
    fi
    
    if [ -f "reporte_verificacion_detallada.txt" ]; then
        echo ""
        echo "Reporte detallado en: reporte_verificacion_detallada.txt"
        echo "Distribución agregada:"
        grep -A5 "DISTRIBUCIÓN AGREGADA:" reporte_verificacion_detallada.txt | tail -6
    fi
}

# Menú principal
main() {
    # Primero seleccionar versiones
    seleccionar_versiones
    
    echo ""
    echo "Seleccione tipo de verificación:"
    echo "  1) Verificación básica (directorios y tamaños)"
    echo "  2) Verificación completa (Python)"
    echo "  3) Verificación detallada (distribuciones)"
    echo "  4) Todas las verificaciones"
    echo "  5) Salir"
    echo ""
    read -p "Opción: " option
    
    case $option in
        1)
            check_directories && count_files && check_file_sizes
            ;;
        2)
            check_directories && run_python_verifier
            ;;
        3)
            check_directories && run_detailed_verifier
            ;;
        4)
            check_directories && count_files && check_file_sizes && run_python_verifier && run_detailed_verifier
            ;;
        5)
            echo "Saliendo..."
            exit 0
            ;;
        *)
            error "Opción no válida"
            exit 1
            ;;
    esac
    
    show_summary
}

# Ejecutar menú
main "$@"