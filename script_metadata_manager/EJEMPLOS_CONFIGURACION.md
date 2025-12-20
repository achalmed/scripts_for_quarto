# EJEMPLOS DE CONFIGURACIÓN PARA EXCEL
# Autor: Edison Achalma
# Fecha: Diciembre 2024

Este documento contiene ejemplos de cómo llenar correctamente los campos en el Excel.

## CAMPOS COMUNES (Aplicables a todos los tipos)

### Identificación y Títulos

```
title: Análisis Económico de la Región Ayacucho 2024
shorttitle: Análisis Económico 2024
subtitle: Un Estudio Comprehensivo del Desarrollo Regional
```

### Publicación y Estado

```
date: 12/19/2025
draft: FALSE
```

Para borradores que no quieres publicar aún:
```
draft: TRUE
```

### Descripción y Resumen

```
abstract: Este estudio analiza el comportamiento económico de la región Ayacucho durante el año 2024, enfocándose en los sectores productivos, índices de empleo, y proyecciones de crecimiento. Se utilizó metodología cuantitativa con datos del INEI y entrevistas a 200 empresarios locales. Los resultados muestran un crecimiento del 3.5% en el sector agrícola y 2.1% en servicios.

description: Análisis económico comprehensivo de Ayacucho 2024 con datos del INEI y proyecciones de crecimiento sectorial.
```

### Clasificación

```
keywords: economía regional, Ayacucho, desarrollo económico, sectores productivos, INEI
tags: economía, análisis, Perú, Ayacucho, desarrollo
categories: Economía Regional, Análisis Económico, Estudios de Desarrollo
```

**Importante:** Separar siempre con comas

### Medios

```
image: featured.png
```

Asegurarse que el archivo existe en la carpeta del artículo.

### Código

```
eval: TRUE   # Para evaluar bloques de código R/Python
eval: FALSE  # Para no evaluar código
```

### Citación

```
citation_type: article-journal
citation_author: Edison Achalma
citation_pdf_url: https://achalmaedison.netlify.app/blog/posts/2024-12-19-analisis/index.pdf
```

Otros tipos de citación:
- `article-journal` - Artículo de revista
- `book` - Libro
- `chapter` - Capítulo de libro
- `paper-conference` - Conferencia
- `thesis` - Tesis
- `report` - Reporte técnico

### Enlaces Adicionales

Sin enlaces:
```
links_enabled: FALSE
links_data: (dejar vacío)
```

Con enlaces:
```
links_enabled: TRUE
links_data: [{"icon": "github", "name": "Repositorio", "url": "https://github.com/achalmed/proyecto"}, {"icon": "file-pdf", "name": "Slides", "url": "https://ejemplo.com/slides.pdf"}]
```

### Bibliografía

```
bibliography: referencias.bib
```

Para múltiples archivos:
```
bibliography: referencias.bib, extra.bib
```

---

## AUTOR 1 (Principal - Correspondiente)

```
author_1_name: Edison Achalma
author_1_corresponding: TRUE
author_1_orcid: 0000-0002-1234-5678
author_1_email: achalmaedison@gmail.com
author_1_affiliation_name: Universidad Nacional de San Cristóbal de Huamanga
author_1_affiliation_department: Facultad de Ciencias Económicas, Administrativas y Contables
author_1_affiliation_city: Ayacucho
author_1_affiliation_region: Ayacucho
author_1_affiliation_country: Perú
author_1_roles: conceptualization, methodology, formal analysis, writing, visualization
```

## AUTOR 2 (Coautor)

```
author_2_name: María González Pérez
author_2_corresponding: FALSE
author_2_orcid: 0000-0002-9876-5432
author_2_email: mgonzalez@universidad.edu
author_2_affiliation_name: Universidad Nacional de San Cristóbal de Huamanga
author_2_roles: investigation, data curation, writing
```

## AUTOR 3 (Colaborador)

```
author_3_name: Juan Carlos Rodríguez
author_3_orcid: 0000-0003-1111-2222
author_3_affiliation_name: Universidad Nacional Mayor de San Marcos
author_3_roles: methodology, validation, editing
```

**Roles CRediT comunes:**
- conceptualization
- methodology
- software
- validation
- formal analysis
- investigation
- resources
- data curation
- writing
- visualization
- supervision
- project administration
- funding acquisition

---

## TIPO STU (Estudiante)

### Ejemplo 1: Trabajo de Curso

```
course: Metodología de la Investigación Económica (ECON 5101)
professor: Dr. Edison Achalma Mendoza
duedate: 01/23/2025
note: Código de estudiante: 2020123456
Sección: A
```

### Ejemplo 2: Proyecto Grupal

```
course: Econometría Aplicada II
professor: Dra. María González
duedate: 06/15/2025
note: Trabajo grupal - Estudiantes:
- Edison Achalma (2020123456)
- Juan Pérez (2020123457)
- Ana López (2020123458)
```

---

## TIPO JOU (Revista)

### Ejemplo 1: Artículo Publicado

```
journal: Revista Peruana de Economía
volume: 2025, Vol. 7, No. 1, 1--25
copyrightnotice: © 2025
copyrightext: Universidad Nacional de San Cristóbal de Huamanga. Todos los derechos reservados.
```

### Ejemplo 2: Revista Internacional

```
journal: Journal of Development Economics
volume: 2025, Vol. 156, 102847
copyrightnotice: © 2025
copyrightext: Elsevier Ltd. All rights reserved.
```

---

## TIPO MAN (Manuscrito)

### Ejemplo 1: Manuscrito para Envío

```
floatsintext: FALSE
numbered_lines: TRUE
meta_analysis: FALSE
mask: FALSE
```

**Configuración típica para envío a revista:**
- `floatsintext: FALSE` - Figuras al final
- `numbered_lines: TRUE` - Facilita revisión
- `mask: FALSE` - Información completa de autores

### Ejemplo 2: Manuscrito con Meta-análisis

```
floatsintext: FALSE
numbered_lines: TRUE
meta_analysis: TRUE
mask: FALSE
```

### Ejemplo 3: Revisión Ciega

```
floatsintext: FALSE
numbered_lines: TRUE
meta_analysis: FALSE
mask: TRUE
```

---

## TIPO DOC (Documento)

### Ejemplo 1: Working Paper

```
floatsintext: TRUE
numbered_lines: FALSE
```

### Ejemplo 2: Informe Técnico

```
floatsintext: TRUE
numbered_lines: FALSE
```

### Ejemplo 3: Ensayo Académico

```
floatsintext: TRUE
numbered_lines: FALSE
```

---

## CASOS ESPECIALES

### Artículo Multilingüe

Si el artículo está en español pero quieres metadatos en inglés:

```
title: Economic Analysis of Ayacucho Region 2024
shorttitle: Economic Analysis 2024
keywords: regional economics, Ayacucho, economic development
```

### Artículo con Múltiples Categorías

```
categories: Economía Regional, Análisis Cuantitativo, Políticas Públicas, Desarrollo Sostenible
```

### Artículo con Tags Técnicos

```
tags: econometría, panel data, R, ggplot2, regresión múltiple, análisis longitudinal
```

### Artículo Antiguo (Fecha Retroactiva)

```
date: 03/15/2020
draft: FALSE
```

### Serie de Artículos

Para mantener consistencia en una serie:

**Artículo 1:**
```
title: Series de Tiempo en Economía: Parte I - Fundamentos
categories: Series Temporales, Tutorial
tags: series-de-tiempo, parte-1
```

**Artículo 2:**
```
title: Series de Tiempo en Economía: Parte II - Modelos ARIMA
categories: Series Temporales, Tutorial
tags: series-de-tiempo, parte-2, arima
```

---

## VALIDACIÓN DE DATOS

### ✅ CORRECTO

```
draft: TRUE
eval: FALSE
floatsintext: TRUE
```

### ❌ INCORRECTO

```
draft: true    # Debe ser mayúsculas
eval: false    # Debe ser mayúsculas
floatsintext: Si  # Debe ser TRUE o FALSE
```

### ✅ CORRECTO (Listas)

```
keywords: economía, estadística, análisis
tags: tutorial, python, datos
```

### ❌ INCORRECTO (Listas)

```
keywords: economía; estadística; análisis  # Usar comas, no punto y coma
tags: [tutorial, python, datos]           # No usar corchetes
```

### ✅ CORRECTO (Fechas)

```
date: 12/19/2025
date: 2025-12-19
```

### ❌ INCORRECTO (Fechas)

```
date: 19-12-2025     # Puede causar confusión
date: Dec 19, 2025   # Usar formato numérico
```

---

## TIPS Y MEJORES PRÁCTICAS

### 1. Palabras Clave (Keywords)

**Buenas prácticas:**
- 3-5 keywords principales
- Usar términos específicos de tu campo
- Incluir términos de búsqueda comunes
- Considerar sinónimos importantes

**Ejemplo:**
```
keywords: desarrollo económico regional, indicadores socioeconómicos, Ayacucho Perú, políticas de desarrollo, análisis cuantitativo
```

### 2. Tags

**Buenas prácticas:**
- Mezclar tags generales y específicos
- Incluir tecnologías usadas
- Agregar tags de nivel (básico, intermedio, avanzado)

**Ejemplo:**
```
tags: economía, R, ggplot2, análisis-datos, tutorial, intermedio, visualización
```

### 3. Abstract

**Buenas prácticas:**
- Primera oración: problema/pregunta
- Segunda parte: metodología
- Tercera parte: resultados principales
- Última oración: conclusión/implicación
- Máximo 250 palabras

**Ejemplo:**
```
abstract: La región Ayacucho ha experimentado transformaciones económicas significativas en la última década. Este estudio analiza los factores determinantes del crecimiento económico regional utilizando datos panel de 11 provincias durante 2014-2024. Empleamos modelos de efectos fijos y análisis de series temporales para identificar patrones de desarrollo. Los resultados muestran que la inversión pública en infraestructura y educación tiene efectos positivos significativos (p < 0.01) en el PIB regional. Las implicaciones sugieren que políticas focalizadas en estos sectores pueden acelerar el desarrollo económico sostenible.
```

### 4. Mantener Consistencia

Para un blog, mantener formato consistente:

```
# Blog de Economía
categories: Siempre usar: Macroeconomía, Microeconomía, Econometría, etc.
tags: Estilo camelCase o kebab-case consistente
date: Siempre MM/DD/YYYY
```

### 5. Preparación para Publicación

Antes de cambiar `draft: FALSE`:
- ✅ Revisar ortografía
- ✅ Verificar links
- ✅ Comprobar que imágenes existen
- ✅ Validar referencias bibliográficas
- ✅ Probar código (si eval: TRUE)

---

## TROUBLESHOOTING COMÚN

### Problema: Cambios no se aplican

**Solución:** Verificar:
1. Formato de booleanos (TRUE/FALSE en mayúsculas)
2. Archivo Excel guardado como .xlsx
3. Sin celdas fusionadas en el Excel
4. Rutas de archivo correctas

### Problema: Error en YAML generado

**Solución:** 
1. Ejecutar con `--dry-run` para ver vista previa
2. Verificar caracteres especiales en texto
3. Usar comillas para textos con dos puntos

### Problema: Autores no se actualizan

**Solución:**
1. Verificar que `author_N_name` no esté vacío
2. Solo UN autor puede tener `corresponding: TRUE`
3. ORCID debe tener formato: 0000-0000-0000-0000

---

**Autor:** Edison Achalma  
**Contacto:** achalmaedison@gmail.com  
**Versión:** 1.0.0
