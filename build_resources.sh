#!/usr/bin/env bash
# =============================================================================
# build_resources.sh — Compila resources.qrc a un módulo Python (opcional).
#
# La aplicación funciona sin este paso (carga los recursos desde disco como
# fallback), pero compilarlos permite empaquetar todo en un solo binario.
# =============================================================================
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if ! command -v pyside6-rcc >/dev/null 2>&1; then
    echo "❌ pyside6-rcc no encontrado. Instala PySide6: pip install PySide6" >&2
    exit 1
fi

pyside6-rcc "$DIR/app/resources/resources.qrc" -o "$DIR/app/resources/resources_rc.py"
echo "✅ Recursos compilados en app/resources/resources_rc.py"
