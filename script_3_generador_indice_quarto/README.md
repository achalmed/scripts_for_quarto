# Generador de Índices de Contenido para Blogs Quarto

## 📋 Descripción

Script Bash automatizado que genera archivos de índice (.qmd) para blogs construidos con Quarto. Escanea carpetas organizadas por fecha y crea listas numeradas con enlaces directos a publicaciones y sus versiones PDF.

## 🎯 Características

- ✅ Generación automática de índices en formato Quarto Markdown
- 📅 Detección automática de posts organizados por fecha (YYYY-MM-DD-titulo)
- 🔗 Generación de enlaces a páginas web y archivos PDF
- 📝 Títulos legibles con capitalización automática
- 🎨 Iconos de Font Awesome para enlaces PDF
- 📊 Logging detallado del proceso
- ⚠️ Validaciones de seguridad y manejo de errores

## 📂 Estructura Esperada
```
blog-principal/
├── subblog-1/
│   ├── 2024-01-15-primera-publicacion/
│   │   └── index.qmd
│   ├── 2024-02-20-segunda-publicacion/
│   │   └── index.qmd
│   └── _contenido_subblog-1.qmd  # ← Generado automáticamente
├── subblog-2/
│   ├── 2024-03-10-otra-publicacion/
│   │   └── index.qmd
│   └── _contenido_subblog-2.qmd  # ← Generado automáticamente
└── ...
```

## 🚀 Instalación

### Requisitos Previos

- Bash 4.0 o superior
- Sistema operativo Unix/Linux/macOS o WSL en Windows
- Estructura de directorios compatible con Quarto

### Pasos de Instalación

1. **Clonar o descargar el script:**
```bash
# Crear directorio para el script
mkdir -p ~/scripts/blog-tools
cd ~/scripts/blog-tools

# Descargar el script (sustituir con tu método preferido)
curl -O [URL_del_script]/generar_indices.sh
# O copiar manualmente el script
```

2. **Dar permisos de ejecución:**
```bash
chmod +x generar_indices.sh
```

3. **Configurar variables:**

Editar el archivo y ajustar las variables de configuración:
```bash
nano generar_indices.sh
```

Modificar estas líneas según tu estructura:
```bash
main_blog="../gestion-empresarial"  # Cambiar a tu blog
base_url="https://achalmaedison.netlify.app"  # Tu URL
```

## 💻 Uso

### Uso Básico
```bash
# Ejecutar desde el directorio del script
./generar_indices.sh
```

### Uso desde Cualquier Directorio
```bash
# Agregar alias al .bashrc o .zshrc
echo "alias generar-indices='~/scripts/blog-tools/generar_indices.sh'" >> ~/.bashrc
source ~/.bashrc

# Ahora puedes ejecutar desde cualquier lugar
generar-indices
```

### Procesar Diferentes Blogs
```bash
# Método 1: Editar la variable main_blog antes de ejecutar
main_blog="../finanzas" ./generar_indices.sh

# Método 2: Crear scripts específicos para cada blog
cp generar_indices.sh generar_indices_finanzas.sh
# Editar generar_indices_finanzas.sh y cambiar main_blog
```

## 📖 Ejemplos

### Ejemplo de Salida Generada

**Archivo:** `_contenido_introduccion.qmd`
```markdown
---
title: "Índice de Contenidos - introduccion"
date: "2025-01-19"
format: html
---

# Publicaciones

1. [{{< fa regular file-pdf >}}](https://achalmaedison.netlify.app/gestion-empresarial/introduccion/2024-01-15-conceptos-basicos/index.pdf) [Conceptos Basicos](https://achalmaedison.netlify.app/gestion-empresarial/introduccion/2024-01-15-conceptos-basicos)
2. [{{< fa regular file-pdf >}}](https://achalmaedison.netlify.app/gestion-empresarial/introduccion/2024-02-20-metodologias-agiles/index.pdf) [Metodologias Agiles](https://achalmaedison.netlify.app/gestion-empresarial/introduccion/2024-02-20-metodologias-agiles)
```

### Ejemplo de Log de Ejecución
```
[2025-01-19 10:30:45] ℹ️  Iniciando procesamiento del blog: ../gestion-empresarial
[2025-01-19 10:30:45] ℹ️  URL base configurada: https://achalmaedison.netlify.app
[2025-01-19 10:30:45] ℹ️  Procesando subblog: introduccion
[2025-01-19 10:30:45] ✅ Generado: ../gestion-empresarial/introduccion/_contenido_introduccion.qmd (12 publicaciones)
[2025-01-19 10:30:45] ℹ️  Procesando subblog: avanzado
[2025-01-19 10:30:45] ✅ Generado: ../gestion-empresarial/avanzado/_contenido_avanzado.qmd (8 publicaciones)

════════════════════════════════════════════════════════════════
[2025-01-19 10:30:45] ✅ Proceso completado exitosamente
[2025-01-19 10:30:45] ℹ️  Total de archivos de índice generados: 2
════════════════════════════════════════════════════════════════
```

## 🔧 Personalización

### Modificar el Formato de los Enlaces

Editar la función `convert_to_link`:
```bash
# Para agregar fecha al título
local title="[$(echo "$folder_name" | sed 's/^\([0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}\).*/\1/')] $title"

# Para usar diferentes iconos
echo -e "[📄]($pdf_url) [$title]($url)"  # Emoji directo
echo -e "[PDF]($pdf_url) [$title]($url)" # Texto simple
```

### Agregar Encabezado Personalizado

Modificar la sección del archivo de salida:
```bash
cat > "$output_file" << EOF
---
title: "Índice - $subblog_name"
author: "Edison Achalma"
date: "$(date '+%Y-%m-%d')"
categories: [índice, contenido]
---

:::{.callout-note}
Índice generado automáticamente el $(date '+%d de %B de %Y')
:::

# 📚 Publicaciones

EOF
```

## ❓ Solución de Problemas

### El script no encuentra el directorio
```bash
# Verificar la ruta relativa
ls -la ../gestion-empresarial

# O usar ruta absoluta
main_blog="/home/usuario/proyectos/blog/gestion-empresarial"
```

### Los enlaces no funcionan

- Verificar que `base_url` no tenga barra final
- Confirmar la estructura de URLs de tu sitio Quarto
- Revisar que los archivos PDF se generen correctamente

### Permisos denegados
```bash
chmod +x generar_indices.sh
# O ejecutar con bash explícitamente
bash generar_indices.sh
```

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/mejora`)
3. Commit tus cambios (`git commit -m 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/mejora`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo `LICENSE` para más detalles.

## 👤 Autor

**Edison Achalma**
- Website: [achalmaedison.netlify.app](https://achalmaedison.netlify.app)
- GitHub: [@achalmed](https://github.com/achalmed)
- LinkedIn: [achalmaedison](https://www.linkedin.com/in/achalmaedison)

## 📞 Soporte

Si encuentras algún problema o tienes sugerencias:

- 🐛 [Reportar un bug](https://github.com/achalmed/blog-tools/issues)
- 💡 [Solicitar una feature](https://github.com/achalmed/blog-tools/issues)
- 💬 [Discusiones](https://github.com/achalmed/blog-tools/discussions)

---

⭐ Si este proyecto te resulta útil, considera darle una estrella en GitHub
