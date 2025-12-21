# 🛠️ Scripts for Quarto

**Colección de herramientas para optimizar y automatizar la gestión de blogs Quarto**

[![GitHub](https://img.shields.io/badge/GitHub-achalmed%2Fscripts__for__quarto-blue?logo=github)](https://github.com/achalmed/scripts_for_quarto)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Quarto](https://img.shields.io/badge/Quarto-Compatible-orange.svg)](https://quarto.org/)

---

## 📋 Descripción General

Este repositorio contiene una **suite de herramientas especializadas** para trabajar con blogs y documentos Quarto. Cada script está diseñado para resolver problemas específicos en la gestión, mantenimiento y publicación de contenido académico y profesional.

**Desarrollado por:** Edison Achalma  
**Ubicación:** Ayacucho, Perú  
**Última actualización:** Diciembre 2024

---

## 🎯 ¿Para quién es este repositorio?

Este conjunto de scripts es ideal para:

- 📝 **Bloggers académicos** que gestionan múltiples blogs Quarto
- 🎓 **Investigadores** que publican contenido técnico
- 📚 **Educadores** que mantienen material educativo online
- 💼 **Profesionales** con múltiples sitios de documentación
- 🔧 **Desarrolladores** que buscan automatizar flujos de trabajo en Quarto

---

## 📦 Scripts Incluidos

### 1. 🔧 **Script Format YAML** (`script_format_yaml/`)

**Problema que resuelve:** Corrige automáticamente el formato del bloque YAML en archivos `.qmd`.

**Características principales:**
- ✅ Normaliza el espaciado después de los delimitadores `---`
- ✅ Elimina líneas en blanco innecesarias
- ✅ Es **idempotente** (puedes ejecutarlo múltiples veces)
- ✅ Modo `--dry-run` para simular cambios

**Uso rápido:**
```bash
cd script_format_yaml
python fix_qmd_files.py --directory ~/Documents/publicaciones --recursive
```

**📖 [README completo](script_format_yaml/README.md)**

---

### 2. 📑 **Generador de Índices de Publicaciones** (`script_generador_publicacion_similar/`)

**Problema que resuelve:** Genera automáticamente archivos de índice para tus publicaciones.

**Características principales:**
- 📁 Soporta **dos estructuras**: página web completa (`blog/posts/`) y blog independiente (`posts/`)
- 🔗 Crea enlaces a PDFs y artículos
- 🎨 Usa iconos de Font Awesome
- 🔄 Procesamiento automático de subdirectorios

**Uso rápido:**
```bash
cd script_generador_publicacion_similar
./generar_indices.sh
```

**Estructuras soportadas:**

**Página Web:**
```
mi-sitio/
└── blog/
    └── posts/
        └── 2023-05-12-titulo/
            └── index.qmd
```

**Blog Independiente:**
```
actus-mercator/
└── posts/
    └── 2022-01-23-titulo/
        └── index.qmd
```

**📖 [README completo](script_generador_publicacion_similar/README.md)**

---

### 3. 📊 **Sistema de Gestión de Metadatos** (`script_metadata_manager/`)

**Problema que resuelve:** Administra metadatos YAML de **cientos de artículos** desde un solo archivo Excel.

**Características principales:**
- 📊 **Excel como base de datos** - Edita metadatos en Excel
- 🎯 Filtra por blog, ruta o criterios personalizados
- 🔄 Solo actualiza cuando hay diferencias
- 📝 Soporta 4 tipos de documentos: STU, MAN, JOU, DOC
- 👥 Gestión de hasta 3 autores con ORCID y afiliaciones
- ⚡ Modo simulación con `--dry-run`

**Flujo de trabajo:**
```bash
cd script_metadata_manager

# 1. Crear configuración
python quarto_metadata_manager.py create-config ~/Documents/publicaciones

# 2. Generar base de datos Excel
python quarto_metadata_manager.py create-template ~/Documents/publicaciones \
    --config metadata_config.yml

# 3. Editar metadatos en Excel
libreoffice excel_databases/quarto_metadata.xlsx

# 4. Actualizar archivos
python quarto_metadata_manager.py update ~/Documents/publicaciones \
    excel_databases/quarto_metadata.xlsx --config metadata_config.yml
```

**Casos de uso comunes:**
- ✅ Publicar 20+ artículos cambiando `draft: FALSE`
- ✅ Actualizar keywords de forma masiva
- ✅ Cambiar tipo de documento (JOU → STU)
- ✅ Agregar/modificar autores en múltiples artículos

**📖 [README completo](script_metadata_manager/README.md)**

---

### 4. 🏷️ **Gestor de Tags** (`script_tag_manager/`)

**Problema que resuelve:** Normaliza, reemplaza y gestiona tags en archivos `.qmd`.

**Características principales:**
- 🔄 **Normalización automática** - Convierte a minúsculas, elimina tildes
- 🔁 **Reemplazo masivo** - Cambia tags obsoletos por nuevos
- 🗑️ **Eliminación selectiva** - Remueve tags no deseados
- ➕ **Adición inteligente** - Solo agrega tags a archivos que ya los tienen
- 🔍 **Detección de duplicados** - Evita tags repetidos

**Ejemplos de normalización:**
```yaml
# Antes
tags:
  - Gestión Empresarial
  - Economía Internacional
  - Cadena de suministros

# Después (con --normalize)
tags:
  - gestion_empresarial
  - economia_internacional
  - cadena_de_suministros
```

**Uso rápido:**
```bash
cd script_tag_manager

# Normalizar todos los tags
python qmd_tag_manager.py --normalize --recursive

# Reemplazar tags específicos
python qmd_tag_manager.py --replace "viejo:nuevo" --recursive

# Agregar tags nuevos
python qmd_tag_manager.py --add "nuevo_tag" --recursive
```

**📖 [README completo](script_tag_manager/README.md)**

---

## 🚀 Instalación General

### Requisitos Previos

- **Python 3.8+**
- **Conda** (recomendado) o pip
- **Quarto** (para renderizar blogs)
- **Git** (para control de versiones)

### Instalación Rápida

```bash
# 1. Clonar el repositorio
git clone https://github.com/achalmed/scripts_for_quarto.git
cd scripts_for_quarto

# 2. Crear entorno conda (recomendado)
conda create -n scripts_quarto python=3.9
conda activate scripts_quarto

# 3. Instalar dependencias generales
pip install pyyaml pandas openpyxl

# 4. Dar permisos de ejecución
chmod +x script_generador_publicacion_similar/generar_indices.sh
chmod +x script_metadata_manager/*.sh
chmod +x script_tag_manager/*.sh
```

### Instalación por Script

Cada script tiene su propio directorio con instrucciones específicas:

```bash
# Script Format YAML
cd script_format_yaml
# Ver README.md

# Generador de Índices
cd script_generador_publicacion_similar
# Ver README.md

# Gestor de Metadatos
cd script_metadata_manager
bash install.sh  # Instalación automática

# Gestor de Tags
cd script_tag_manager
# Ver README.md
```

---

## 📖 Guías de Uso Rápido

### Flujo de Trabajo Típico

```bash
# 1. Activar entorno
conda activate scripts_quarto

# 2. Normalizar formato YAML
cd script_format_yaml
python fix_qmd_files.py --directory ~/Documents/publicaciones --recursive

# 3. Normalizar tags
cd ../script_tag_manager
python qmd_tag_manager.py --normalize --recursive --directory ~/Documents/publicaciones

# 4. Actualizar metadatos desde Excel
cd ../script_metadata_manager
python quarto_metadata_manager.py update ~/Documents/publicaciones \
    excel_databases/quarto_metadata.xlsx

# 5. Generar índices
cd ../script_generador_publicacion_similar
./generar_indices.sh

# 6. Renderizar con Quarto
cd ~/Documents/publicaciones/mi-blog
quarto render
```

---

## 🎯 Casos de Uso por Escenario

### Escenario 1: Iniciar un Nuevo Blog

```bash
# 1. Crear estructura
quarto create project blog mi-blog

# 2. Configurar gestor de metadatos
cd scripts_for_quarto/script_metadata_manager
python quarto_metadata_manager.py create-config ~/Documents/mi-blog

# 3. Generar primera base de datos
python quarto_metadata_manager.py create-template ~/Documents/mi-blog
```

### Escenario 2: Migrar Blog Existente

```bash
# 1. Corregir formato YAML
cd script_format_yaml
python fix_qmd_files.py --directory ~/Documents/blog-viejo --recursive

# 2. Normalizar tags
cd ../script_tag_manager
python qmd_tag_manager.py --normalize --recursive --directory ~/Documents/blog-viejo

# 3. Crear base de datos de metadatos
cd ../script_metadata_manager
python quarto_metadata_manager.py create-template ~/Documents/blog-viejo
```

### Escenario 3: Publicación Masiva

```bash
# 1. Crear Excel con todos los artículos
cd script_metadata_manager
python quarto_metadata_manager.py create-template ~/Documents/publicaciones

# 2. Editar en Excel (cambiar draft: FALSE)
libreoffice excel_databases/quarto_metadata.xlsx

# 3. Aplicar cambios
python quarto_metadata_manager.py update ~/Documents/publicaciones \
    excel_databases/quarto_metadata.xlsx

# 4. Generar índices
cd ../script_generador_publicacion_similar
./generar_indices.sh

# 5. Renderizar
cd ~/Documents/publicaciones
quarto render
```

### Escenario 4: Mantenimiento Periódico

```bash
# 1. Actualizar metadatos
cd script_metadata_manager
python quarto_metadata_manager.py create-template ~/Documents/publicaciones

# 2. Revisar y editar Excel
# (Actualizar keywords, categorías, etc.)

# 3. Aplicar cambios
python quarto_metadata_manager.py update ~/Documents/publicaciones \
    excel_databases/quarto_metadata.xlsx --dry-run  # Simular primero
python quarto_metadata_manager.py update ~/Documents/publicaciones \
    excel_databases/quarto_metadata.xlsx  # Aplicar
```

---

## 📊 Comparación de Scripts

| Script | Propósito | Input | Output | Mejor Para |
|--------|-----------|-------|--------|------------|
| **Format YAML** | Corregir formato | `.qmd` | `.qmd` corregidos | Normalización inicial |
| **Generador Índices** | Crear listas | Carpetas con posts | `_contenido_*.qmd` | Navegación en blogs |
| **Metadata Manager** | Gestión masiva | `.qmd` | Excel → `.qmd` | Edición de metadatos |
| **Tag Manager** | Normalizar tags | `.qmd` | `.qmd` con tags limpios | Taxonomía consistente |

---

## 🤝 Contribuciones

¡Las contribuciones son bienvenidas! Si tienes ideas para mejorar estos scripts:

1. **Fork** el repositorio
2. Crea una **branch** para tu feature: `git checkout -b feature/nueva-caracteristica`
3. **Commit** tus cambios: `git commit -m "Agregar nueva característica"`
4. **Push** a la branch: `git push origin feature/nueva-caracteristica`
5. Abre un **Pull Request**

### Áreas de Mejora Sugeridas

- [ ] Interfaz gráfica (GUI) para los scripts
- [ ] Soporte para más formatos de documentos
- [ ] Integración con GitHub Actions
- [ ] Tests automatizados
- [ ] Documentación en inglés

---

## 🐛 Reportar Problemas

Si encuentras un bug o tienes una sugerencia:

1. Verifica que estás usando la última versión
2. Revisa los [Issues existentes](https://github.com/achalmed/scripts_for_quarto/issues)
3. Crea un nuevo Issue con:
   - Descripción del problema
   - Pasos para reproducir
   - Versión de Python y sistema operativo
   - Logs relevantes

---

## 📄 Licencia

Este proyecto está licenciado bajo la licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

---

## 📞 Contacto y Soporte

**Autor:** Edison Achalma

- 🌐 **Website:** [achalmaedison.netlify.app](https://achalmaedison.netlify.app)
- 💼 **LinkedIn:** [@achalmaedison](https://www.linkedin.com/in/achalmaedison)
- 🐙 **GitHub:** [@achalmed](https://github.com/achalmed)
- 📧 **Email:** achalmaedison@gmail.com
- 📍 **Ubicación:** Ayacucho, Perú

---

## 🎓 Recursos Adicionales

### Documentación de Quarto

- [Quarto Official Docs](https://quarto.org/)
- [Quarto Blogs Guide](https://quarto.org/docs/websites/website-blog.html)
- [YAML Metadata](https://quarto.org/docs/reference/formats/html.html)

### Tutoriales y Guías

Cada script incluye:
- 📖 **README.md** - Documentación completa
- 📝 **EJEMPLOS.md** - Casos de uso detallados
- 🔄 **CHANGELOG.md** - Historial de versiones (donde aplica)
- 🚀 **QUICKSTART.md** - Guía de inicio rápido (donde aplica)

---

## ⭐ Agradecimientos

Gracias a todos los que han contribuido con ideas, reportes de bugs y sugerencias para mejorar estos scripts.

Especial agradecimiento a:
- La comunidad de **Quarto**
- Los usuarios beta que probaron las primeras versiones
- Todos los que reportaron bugs y sugirieron mejoras

---

## 🔄 Actualizaciones Recientes

### Diciembre 2024

- ✅ **Script Metadata Manager v1.2** - Filtros avanzados, Excel unificado
- ✅ **Script Tag Manager v1.1** - Corrección de bugs, mejor normalización
- ✅ **Script Format YAML v2.0** - Idempotente, más robusto
- ✅ **Generador de Índices v2.0** - Soporte para múltiples estructuras

### Próximas Características

- 🔜 Interfaz web para Metadata Manager
- 🔜 Integración con CI/CD
- 🔜 Exportación a otros formatos (JSON, CSV)
- 🔜 Validación automática de metadatos
- 🔜 Dashboard de estadísticas de blogs

---

## 📈 Estadísticas del Proyecto

![GitHub stars](https://img.shields.io/github/stars/achalmed/scripts_for_quarto?style=social)
![GitHub forks](https://img.shields.io/github/forks/achalmed/scripts_for_quarto?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/achalmed/scripts_for_quarto?style=social)

---

## 🎉 ¿Te gustó este proyecto?

Si estos scripts te han sido útiles:

- ⭐ **Dale una estrella** al repositorio
- 🔄 **Comparte** con otros usuarios de Quarto
- 💬 **Comenta** tus casos de uso
- 🤝 **Contribuye** con mejoras

---

**¡Feliz gestión de blogs con Quarto!** 🚀📝

---

<div align="center">

**Hecho con ❤️ en Ayacucho, Perú**

*Last Updated: December 2024*

</div>