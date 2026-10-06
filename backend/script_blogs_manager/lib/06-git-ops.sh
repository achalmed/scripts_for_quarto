#!/usr/bin/env bash
# =============================================================================
#  backend/script_blogs_manager/lib/06-git-ops.sh — Operaciones de Git sobre un blog/proyecto individual: status, commit+push (simula por defecto, puerta R6), inicialización de repositorio
# -----------------------------------------------------------------------------
# =============================================================================

if [[ -n "${QBLOG_GIT_OPS_LOADED:-}" ]]; then
    return 0
fi
QBLOG_GIT_OPS_LOADED=1

# ¿Es la carpeta la raíz de un repositorio git? Un pub es submódulo del hub: su
# `.git` es un archivo, no una carpeta, así que no basta con mirar `.git/`.
# $1 = ruta absoluta del blog
_git_es_raiz() {
    local top
    top="$(git -C "$1" rev-parse --show-toplevel 2>/dev/null)" || return 1
    [[ "$(cd "$top" && pwd -P)" == "$(cd "$1" && pwd -P)" ]]
}

# Rutas con cambios respecto de HEAD (confirmables o ya preparadas, borradas incluidas)
# y sin seguimiento no ignoradas, bajo los pathspecs dados (ninguno = todo el repo).
# Salida separada por NUL y sin repetidos.
# $1 = ruta del sitio; $2… = pathspecs
_git_cambios() {
    local sitio="$1"; shift
    {
        if git -C "$sitio" rev-parse -q --verify HEAD >/dev/null; then
            git -C "$sitio" diff --no-renames --name-only -z HEAD -- "$@"
        else
            git -C "$sitio" ls-files -z --cached -- "$@"
        fi
        git -C "$sitio" ls-files -z --others --exclude-standard -- "$@"
    } | sort -zu
}

# Carpetas de contenido del sitio: las de primer nivel, sin `_` ni `.` delante, que
# contienen algún .qmd (posts/, blog/, talk/…) y no son submódulos. Una por línea.
# $1 = ruta absoluta del sitio
_git_carpetas_contenido() {
    local sitio="$1" d nombre
    local -A submodulos=()
    while IFS= read -r nombre; do submodulos["$nombre"]=1; done \
        < <(git -C "$sitio" -c core.quotePath=false ls-files -s | awk '$1 == "160000" { sub(/^[^\t]*\t/, ""); print }')
    for d in "$sitio"/*/; do
        [[ -d "$d" ]] || continue
        nombre="$(basename "$d")"
        [[ "$nombre" == _* || "$nombre" == .* ]] && continue
        [[ -n "${submodulos[$nombre]:-}" || -e "$d/.git" ]] && continue
        find "$d" -name '*.qmd' -print -quit 2>/dev/null | grep -q . && printf '%s\n' "$nombre"
    done
    return 0
}

# Imprime un título y hasta 15 rutas de un arreglo (por nombre), con el total.
# $1 = título; $2 = nombre del arreglo
_git_listar() {
    local titulo="$1"
    local -n _rutas="$2"
    local i
    print_info "$titulo: ${#_rutas[@]}"
    for (( i = 0; i < ${#_rutas[@]} && i < 15; i++ )); do
        echo "    ${_rutas[$i]}"
    done
    (( ${#_rutas[@]} > 15 )) && echo "    … y $(( ${#_rutas[@]} - 15 )) más"
    return 0
}

# Corre la puerta R6 del hub sobre el sitio (normativa 7.10). Sin la puerta no se
# empuja: falla cerrada.
# $1 = ruta absoluta del sitio
_git_puerta_r6() {
    if [[ ! -f "$QBLOG_PUERTA_R6" ]]; then
        print_error "No encuentro la puerta R6 ($QBLOG_PUERTA_R6): no se empuja"
        return 1
    fi
    GIT_OPTIONAL_LOCKS=0 bash "$QBLOG_PUERTA_R6" "$1"   # sin refrescar el índice: en simulación nada se escribe
}

# Empuja la rama actual a su rama remota de seguimiento, siempre detrás de la
# puerta R6. Netlify despliega con cada push. Sin --aplicar (QBLOG_APLICAR=0)
# corre la puerta (solo lee) y dice cuántos commits empujaría.
# $1 = ruta absoluta del sitio
_git_empujar() {
    local blog_path="$1" upstream pendientes
    if ! upstream="$(git -C "$blog_path" rev-parse --abbrev-ref --symbolic-full-name '@{u}' 2>/dev/null)"; then
        print_error "La rama actual no sigue a ninguna rama remota: no se empuja"
        return 1
    fi
    pendientes="$(git -C "$blog_path" rev-list --count '@{u}..HEAD')"
    if (( pendientes == 0 )); then
        print_info "Nada que empujar: la rama está al día con $upstream"
        return 0
    fi
    if ! _git_puerta_r6 "$blog_path"; then
        print_error "La puerta R6 no pasa: no se empuja (renderiza y confirma _site/ antes)"
        return 1
    fi
    if (( ! QBLOG_APLICAR )); then
        print_info "→ empujaría $pendientes commit(s) a $upstream"
        return 0
    fi
    if git -C "$blog_path" push; then
        print_success "Push exitoso: $pendientes commit(s) a $upstream"
    else
        print_error "git push falló"
        return 1
    fi
}

# Muestra el estado de Git de un blog.
# $1 = ruta absoluta del blog
git_status_blog() {
    local blog_path="$1"
    local blog_name
    blog_name="$(basename "$blog_path")"

    print_header "Git Status: $blog_name"

    if ! _git_es_raiz "$blog_path"; then
        print_error "No es un repositorio Git"
        return 1
    fi

    git -C "$blog_path" status
}

# Confirma el sitio y empuja, detrás de la puerta R6. Simula por defecto (dice qué
# añadiría, qué queda fuera y adónde empujaría); solo con --aplicar
# (QBLOG_APLICAR=1) añade, confirma y empuja. Nunca `git add .`: se añaden las rutas
# cambiadas (respetando .gitignore) bajo QBLOG_FUENTES, las carpetas de contenido
# (con sus imágenes y datos), _freeze/ y _site/; lo demás (sueltos de la raíz,
# punteros de submódulo) se avisa y queda fuera.
# $1 = ruta absoluta del blog
# $2 = mensaje de commit (opcional, default "Update blog")
git_commit_push() {
    local blog_path="$1"
    local message="${2:-Update blog}"
    local blog_name
    blog_name="$(basename "$blog_path")"

    print_header "Git Commit & Push: $blog_name"

    if ! _git_es_raiz "$blog_path"; then
        print_error "No es un repositorio Git: $blog_path"
        return 1
    fi

    local -a fuentes=() contenido=() carpetas=() sitio=() todas=() fuera=()
    local -A dentro=() submodulos=()
    local r
    mapfile -t carpetas < <(_git_carpetas_contenido "$blog_path")
    while IFS= read -r r; do submodulos["$r"]=1; done \
        < <(git -C "$blog_path" -c core.quotePath=false ls-files -s | awk '$1 == "160000" { sub(/^[^\t]*\t/, ""); print }')
    mapfile -d '' -t fuentes < <(_git_cambios "$blog_path" "${QBLOG_FUENTES[@]}")
    if (( ${#carpetas[@]} )); then
        mapfile -d '' -t contenido < <(_git_cambios "$blog_path" "${carpetas[@]/%//}")
    fi
    mapfile -d '' -t sitio < <(_git_cambios "$blog_path" "${QBLOG_GENERADOS[@]}")
    mapfile -d '' -t todas < <(_git_cambios "$blog_path")
    # Un puntero de submódulo nunca entra, aunque caiga bajo un pathspec.
    for r in "${fuentes[@]}" "${contenido[@]}" "${sitio[@]}"; do
        [[ -n "${submodulos[$r]:-}" ]] || dentro["$r"]=1
    done
    for r in "${todas[@]}"; do [[ -n "${dentro[$r]:-}" ]] || fuera+=("$r"); done
    fuentes=()                          # sin repetidos: una ruta puede caer en varios grupos
    if (( ${#dentro[@]} )); then
        mapfile -d '' -t fuentes < <(printf '%s\0' "${!dentro[@]}" | sort -z)
    fi

    print_info "Carpetas de contenido: ${carpetas[*]:-(ninguna)}"
    _git_listar "Rutas que se confirman (fuentes, contenido, _freeze/ y _site/)" fuentes
    if (( ${#fuera[@]} )); then
        print_warning "Quedan fuera ${#fuera[@]} ruta(s): sueltas en la raíz o punteros de submódulo; no se añaden"
        _git_listar "Fuera" fuera
    fi
    if git -C "$blog_path" check-ignore -q "${QBLOG_SITIO_GENERADO}index.html"; then
        print_warning "${QBLOG_SITIO_GENERADO} está ignorado en este repo: la puerta R6 no pasará"
    fi

    local n=${#fuentes[@]}
    if (( ! QBLOG_APLICAR )); then
        if (( n )); then
            print_info "→ añadiría $n ruta(s) y confirmaría: «$message»"
        else
            print_info "→ nada que confirmar en el sitio"
        fi
        print_info "→ después correría la puerta R6 ($QBLOG_PUERTA_R6) y, si pasa, git push"
        print_warning "Simulación: no se añadió, confirmó ni empujó nada. Repite con --aplicar."
        return 0
    fi

    if (( n )); then
        printf '%s\0' "${fuentes[@]}" \
            | git -C "$blog_path" --literal-pathspecs add -A --pathspec-from-file=- --pathspec-file-nul \
            || { print_error "git add falló"; return 1; }
        printf '%s\0' "${fuentes[@]}" \
            | git -C "$blog_path" --literal-pathspecs commit -q -m "$message" --pathspec-from-file=- --pathspec-file-nul \
            || { print_error "git commit falló"; return 1; }
        print_success "Commit realizado ($n ruta(s))"
    else
        print_info "Nada que confirmar en el sitio"
    fi

    _git_empujar "$blog_path"
}

# Inicializa un repositorio Git en un blog, creando .gitignore si no existe.
# $1 = ruta absoluta del blog
git_init() {
    local blog_path="$1"
    local blog_name
    blog_name="$(basename "$blog_path")"

    print_header "Inicializando Git: $blog_name"

    cd "$blog_path" || { print_error "No se pudo acceder a $blog_path"; return 1; }

    if [[ -d ".git" ]]; then
        print_warning "Ya existe un repositorio Git"
        return 0
    fi

    git init

    if [[ ! -f ".gitignore" ]]; then
        cat > .gitignore << 'EOF'
/.quarto/
/_site/
/_freeze/
/.Rproj.user/
.Rhistory
.RData
.DS_Store
EOF
        print_success "Creado .gitignore"
    fi

    print_success "Repositorio Git inicializado"
}
