#!/usr/bin/env bash
# =============================================================================
# 01-logging.sh
# -----------------------------------------------------------------------------
# Funciones de salida por consola + registro en archivo de log. Todos los
# demás módulos deben usar estas funciones en vez de "echo" directo, así el
# formato y el log quedan consistentes en todo el script.
# =============================================================================

if [[ -n "${PUBINDEX_LOGGING_LOADED:-}" ]]; then
    return 0
fi
PUBINDEX_LOGGING_LOADED=1

# Escribe una línea al archivo de log (si está configurado) con timestamp
_pubindex_log_to_file() {
    local level="$1"
    local msg="$2"
    if [[ -n "$PUBINDEX_LOG_FILE" ]]; then
        printf '[%s] [%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$level" "$msg" >> "$PUBINDEX_LOG_FILE"
    fi
}

log_info() {
    local msg="$1"
    printf '%s[INFO]%s  %s\n' "$PUBINDEX_C_BLUE" "$PUBINDEX_C_RESET" "$msg" >&2
    _pubindex_log_to_file "INFO" "$msg"
}

log_ok() {
    local msg="$1"
    printf '%s[OK]%s    %s\n' "$PUBINDEX_C_GREEN" "$PUBINDEX_C_RESET" "$msg" >&2
    _pubindex_log_to_file "OK" "$msg"
}

log_warn() {
    local msg="$1"
    printf '%s[WARN]%s  %s\n' "$PUBINDEX_C_YELLOW" "$PUBINDEX_C_RESET" "$msg" >&2
    _pubindex_log_to_file "WARN" "$msg"
}

log_error() {
    local msg="$1"
    printf '%s[ERROR]%s %s\n' "$PUBINDEX_C_RED" "$PUBINDEX_C_RESET" "$msg" >&2
    _pubindex_log_to_file "ERROR" "$msg"
}

log_section() {
    local msg="$1"
    printf '\n%s%s── %s%s\n' "$PUBINDEX_C_BOLD" "$PUBINDEX_C_BLUE" "$msg" "$PUBINDEX_C_RESET" >&2
    _pubindex_log_to_file "SECTION" "$msg"
}
