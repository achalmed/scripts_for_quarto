# 🚀 Instalación Rápida

## Pasos de Instalación

### 1. Copiar Archivos

```bash
# Crear directorio de scripts si no existe
mkdir -p /home/achalmaedison/Documents/scripts/scripts_for_quarto

# Copiar todos los archivos al directorio
cp *.sh *.md /home/achalmaedison/Documents/scripts/scripts_for_quarto/

# Navegar al directorio
cd /home/achalmaedison/Documents/scripts/scripts_for_quarto
```

### 2. Dar Permisos de Ejecución

```bash
chmod +x *.sh
```

### 3. Configurar PATH (Opcional)

Para ejecutar desde cualquier ubicación:

```bash
# Añadir al ~/.bashrc
echo 'export PATH="$PATH:/home/achalmaedison/Documents/scripts/scripts_for_quarto"' >> ~/.bashrc

# Recargar configuración
source ~/.bashrc
```

### 4. Crear Aliases (Opcional)

```bash
# Añadir al ~/.bashrc
cat >> ~/.bashrc << 'EOF'

# Quarto Blog Management Aliases
alias qbuild="/home/achalmaedison/Documents/scripts/scripts_for_quarto/build.sh"
alias qlist="qbuild list"
alias qcheck="/home/achalmaedison/Documents/scripts/scripts_for_quarto/check-structure.sh"
alias qbackup="/home/achalmaedison/Documents/scripts/scripts_for_quarto/backup-blogs.sh"
alias qinit="/home/achalmaedison/Documents/scripts/scripts_for_quarto/init-blog.sh"

EOF

# Recargar
source ~/.bashrc
```

### 5. Verificar Instalación

```bash
# Verificar que Quarto está instalado
quarto --version

# Probar el script
./build.sh list

# O con alias
qlist
```

## Uso Básico

### Modo Interactivo

```bash
qbuild
# o
qbuild -i
```

### Comandos Rápidos

```bash
# Listar blogs
qlist

# Renderizar un blog
qbuild render website-achalma

# Preview
qbuild preview epsilon-y-beta

# Crear nuevo post
qbuild new-post numerus-scriptum "Mi Nuevo Post"

# Verificar estructura
qcheck

# Backup
qbackup
```

## Estructura Final

Después de la instalación, tu estructura debería verse así:

```
/home/achalmaedison/Documents/
├── publicaciones/          # Tus blogs
│   ├── website-achalma/
│   ├── epsilon-y-beta/
│   └── ...
└── scripts/
    └── scripts_for_quarto/
        ├── build.sh           # Script principal ⭐
        ├── init-blog.sh       # Crear nuevo blog
        ├── check-structure.sh # Verificar estructura
        ├── backup-blogs.sh    # Crear backups
        ├── config.sh          # Configuración
        ├── README.md          # Documentación completa
        └── INSTALL.md         # Esta guía
```

## Próximos Pasos

1. Lee el `README.md` completo para documentación detallada
2. Ejecuta `qcheck` para verificar tus blogs existentes
3. Crea un backup inicial con `qbackup`
4. Prueba el modo interactivo con `qbuild`

## Solución de Problemas

### Quarto no encontrado

```bash
# Verificar instalación
which quarto

# Si no está instalado, descargar de:
# https://quarto.org/docs/get-started/
```

### Permisos denegados

```bash
chmod +x /home/achalmaedison/Documents/scripts/scripts_for_quarto/*.sh
```

### Directorio no encontrado

Verificar que la ruta en los scripts coincide con tu estructura:

```bash
# Editar build.sh y cambiar líneas 15-16 si es necesario
nano /home/achalmaedison/Documents/scripts/scripts_for_quarto/build.sh
```

## Personalización

Para personalizar la configuración:

```bash
# Editar config.sh
nano config.sh

# Cargar configuración personalizada
source config.sh
```

---

¿Problemas? Consulta el `README.md` o ejecuta:
```bash
qbuild help
```
