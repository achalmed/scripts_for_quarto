#!/usr/bin/env bash
# =============================================================================
# 01-printing.sh
# -----------------------------------------------------------------------------
# Funciones de salida visual (colores, emojis, cajas). Conserva exactamente
# el mismo estilo del script original para que la experiencia de uso no
# cambie, solo la organización del código.
# =============================================================================

if [[ -n "${QBLOG_PRINTING_LOADED:-}" ]]; then
    return 0
fi
QBLOG_PRINTING_LOADED=1

print_header() {
    local width=80
    echo ""
    echo -e "${QBLOG_CYAN}$(printf '═%.0s' $(seq 1 $width))${QBLOG_NC}"
    echo -e "${QBLOG_CYAN}${QBLOG_BOLD}  $QBLOG_E_ROCKET $1${QBLOG_NC}"
    echo -e "${QBLOG_CYAN}$(printf '═%.0s' $(seq 1 $width))${QBLOG_NC}"
    echo ""
}

print_subheader() {
    echo ""
    echo -e "${QBLOG_BLUE}${QBLOG_BOLD}── $1${QBLOG_NC}"
    echo ""
}

print_success() {
    echo -e "${QBLOG_GREEN}  $QBLOG_E_SUCCESS${QBLOG_NC} $1"
}

print_error() {
    echo -e "${QBLOG_RED}  $QBLOG_E_ERROR${QBLOG_NC} $1"
}

print_warning() {
    echo -e "${QBLOG_YELLOW}  $QBLOG_E_WARNING${QBLOG_NC} $1"
}

print_info() {
    echo -e "${QBLOG_BLUE}  $QBLOG_E_INFO${QBLOG_NC} $1"
}

print_step() {
    echo -e "${QBLOG_WHITE}${QBLOG_BOLD}→${QBLOG_NC} $1"
}

print_box() {
    local text="$1"
    local width=76
    local padding=$(((width - ${#text}) / 2))

    echo -e "${QBLOG_CYAN}╔$(printf '═%.0s' $(seq 1 $width))╗${QBLOG_NC}"
    printf "${QBLOG_CYAN}║${QBLOG_NC}%*s%s%*s${QBLOG_CYAN}║${QBLOG_NC}\n" "$padding" "" "$text" "$padding" ""
    echo -e "${QBLOG_CYAN}╚$(printf '═%.0s' $(seq 1 $width))╝${QBLOG_NC}"
}
