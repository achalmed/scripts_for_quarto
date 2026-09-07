#!/usr/bin/env bash
# scripts_quarto_studio/backend/script_generador_publicacion_similar/lib/01-logging.sh — envoltorio (FS2, 2026-09-07): el logger vive en core/shell-lib/logger.sh; aquí solo lo propio de esta suite.
_core_d="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; while [ "$_core_d" != / ] && [ ! -f "$_core_d/core/shell-lib/logger.sh" ]; do _core_d="$(dirname "$_core_d")"; done
[ -f "$_core_d/core/shell-lib/logger.sh" ] || { echo "[ERROR] no encuentro core/shell-lib/logger.sh subiendo desde ${BASH_SOURCE[0]}" >&2; exit 1; }
if [[ -n "${GENIDX_LOGGING_LOADED:-}" ]]; then return 0; fi
GENIDX_LOGGING_LOADED=1
source "$_core_d/core/shell-lib/logger.sh"; unset _core_d
