#!/usr/bin/env bash
# tests/run.sh — corre las pruebas de Quarto Studio (tests/studio) con pytest, con la carpeta temporal en disco y sin caché.
# Uso: tests/run.sh [opciones de pytest]   (p. ej. -k operaciones)
# Las de los backends (tests/test_*.py: cada suite en simulación, publish y git-commit con un remoto bare) se corren
# aparte, como dice CLAUDE.md. La carpeta temporal va a ~/.cache (no a /tmp, que es RAM). Nada toca el hub ni los pubs
# reales: cada prueba crea la familia de sitios de muestra (studio/muestra.py) en un temporal, con git y remotos bare
# locales; nada publica. Las pruebas en proceso usan el binding del Python que corre pytest; las de QML y la de humo abren
# un proceso hijo con el Python del sistema (/usr/bin/python3, el del Qt con Kirigami; el .venv del studio si existe) sin
# pantalla y con HOME, XDG_CONFIG_HOME y XDG_CACHE_HOME temporales. Un `quarto render` real solo si quarto está instalado.
set -euo pipefail

DIR_PRUEBAS="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/studio"
BASE_TMP="${XDG_CACHE_HOME:-$HOME/.cache}/pytest/quarto-studio-studio"
mkdir -p "$BASE_TMP"

export PYTHONDONTWRITEBYTECODE=1
export QT_QPA_PLATFORM=offscreen
exec python3 -m pytest "$DIR_PRUEBAS" --basetemp "$BASE_TMP" -p no:cacheprovider -q "$@"
