#!/usr/bin/env bash
# =============================================================================
# 01-logging.sh
# -----------------------------------------------------------------------------
# Funciones de logging centralizadas. Toda salida a consola pasa por aquí
# para garantizar formato consistente ([timestamp] emoji mensaje) y para que
# WARN/ERROR vayan a stderr sin ensuciar stdout.
# =============================================================================

if [[ -n "${GENIDX_LOGGING_LOADED:-}" ]]; then
    return 0
fi
GENIDX_LOGGING_LOADED=1

# _log_timestamp()
# Devuelve la marca de tiempo estándar usada por todos los niveles.
_log_timestamp() {
    date '+%Y-%m-%d %H:%M:%S'
}

# log_info()
# Mensajes informativos de progreso.
# Arguments:
#   $1 - Mensaje a mostrar
log_info() {
    printf '[%s] ℹ️  %s\n' "$(_log_timestamp)" "$1"
}

# log_success()
# Confirmación de operaciones completadas.
# Arguments:
#   $1 - Mensaje a mostrar
log_success() {
    printf '[%s] ✅ %s\n' "$(_log_timestamp)" "$1"
}

# log_warn()
# Situaciones anómalas que no detienen la ejecución. Va a stderr para
# poder filtrar stdout en pipelines.
# Arguments:
#   $1 - Mensaje a mostrar
log_warn() {
    printf '[%s] ⚠️  %s\n' "$(_log_timestamp)" "$1" >&2
}

# log_error()
# Errores que normalmente preceden a un exit. Va a stderr.
# Arguments:
#   $1 - Mensaje a mostrar
log_error() {
    printf '[%s] ❌ %s\n' "$(_log_timestamp)" "$1" >&2
}
