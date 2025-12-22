# 📖 Guía Completa de Fórmulas de Excel para Gestión de Metadatos Quarto

**Versión:** 1.0  
**Autor:** Edison Achalma  
**Fecha:** Diciembre 2024

---

## 📋 Tabla de Contenidos

1. [Eliminar Saltos de Línea](#1-eliminar-saltos-de-l%C3%ADnea-enter)
2. [Generar Títulos desde Rutas](#2-generar-t%C3%ADtulos-desde-rutas)
3. [Crear Enlaces a PDFs](#3-crear-enlaces-a-pdfs)
4. [Extraer Fechas de Rutas](#4-extraer-fechas-de-rutas)
5. [Gestión de Tags](#5-gesti%C3%B3n-de-tags)
6. [Extraer Información de Rutas](#6-extraer-informaci%C3%B3n-de-rutas)
7. [Limpieza y Normalización](#7-limpieza-y-normalizaci%C3%B3n)
8. [Fórmulas Avanzadas](#8-f%C3%B3rmulas-avanzadas)

---

## 1. Eliminar Saltos de Línea (Enter)

### 🎯 Problema

Tienes texto con **saltos de línea (Enter)** dentro de una celda y necesitas eliminarlos.

### Solución 1: Con Fórmula (Recomendado)

Si el texto está en **A1**:

```excel
=SUBSTITUTE(A1,CHAR(10)," ")
```

**Explicación:**

- `CHAR(10)` = Salto de línea (Line Feed)
- Reemplaza cada Enter por un espacio

### Solución 2: Eliminar Múltiples Tipos de Saltos

```excel
=SUBSTITUTE(SUBSTITUTE(A1,CHAR(13)," "),CHAR(10)," ")
```

**Explicación:**

- `CHAR(13)` = Retorno de carro (Carriage Return)
- `CHAR(10)` = Salto de línea (Line Feed)
- Útil en archivos de Windows

### Solución 3: Eliminar Sin Dejar Espacios

```excel
=SUBSTITUTE(A1,CHAR(10),"")
```

### ⚡ Método Rápido: Buscar y Reemplazar

**Pasos:**

1. Selecciona la celda o columna
2. Presiona `Ctrl + H` (Buscar y Reemplazar)
3. En **Buscar**: presiona `Ctrl + J` (no verás nada, pero está capturando el Enter)
4. En **Reemplazar con**: escribe un espacio (o déjalo vacío)
5. Click en **Reemplazar todo**

### 🧹 Limpiar Espacios Múltiples Después

```excel
=TRIM(SUBSTITUTE(A1,CHAR(10)," "))
```

**Explicación:**

- `TRIM()` elimina espacios múltiples dejando solo uno

---

## 2. Generar Títulos desde Rutas

### 🎯 Objetivo

Convertir rutas como:

```
aequilibria/posts/2022-01-17-09-crecimiento-economico/index.qmd
```

En títulos formateados:

```
Crecimiento economico
```

### Fórmula Completa (Excel Español)

Suponiendo ruta en **A1**:

```excel
=MAYUSC(IZQUIERDA(SUSTITUIR(TEXTO.ANTES(TEXTO.DESPUES(A1,"-",4),"/"),"-"," "),1))
 & MINUSC(EXTRAE(SUSTITUIR(TEXTO.ANTES(TEXTO.DESPUES(A1,"-",4),"/"),"-"," "),2,99))
```

### Fórmula Completa (Excel Inglés)

```excel
=UPPER(LEFT(SUBSTITUTE(TEXTBEFORE(TEXTAFTER(A1,"-",4),"/"),"-"," "),1))
 & LOWER(MID(SUBSTITUTE(TEXTBEFORE(TEXTAFTER(A1,"-",4),"/"),"-"," "),2,99))
```

### 🔍 Desglose de la Fórmula

#### Paso 1: Extraer después del cuarto guion

```excel
TEXTO.DESPUES(A1,"-",4)
```

De: `aequilibria/posts/2022-01-17-09-crecimiento-economico/index.qmd`  
Resultado: `crecimiento-economico/index.qmd`

#### Paso 2: Eliminar `/index.qmd`

```excel
TEXTO.ANTES(...,"/")
```

Resultado: `crecimiento-economico`

#### Paso 3: Reemplazar guiones por espacios

```excel
SUSTITUIR(...,"-"," ")
```

Resultado: `crecimiento economico`

#### Paso 4: Primera letra mayúscula

```excel
MAYUSC(IZQUIERDA(...,1))
```

Resultado: `C`

#### Paso 5: Resto en minúsculas

```excel
MINUSC(EXTRAE(...,2,99))
```

Resultado: `recimiento economico`

#### Paso 6: Concatenar

```excel
= "C" & "recimiento economico"
```

Resultado final: `Crecimiento economico`

### 📝 Variantes Útiles

#### Solo primera palabra en mayúscula

```excel
=PROPER(SUBSTITUTE(TEXTBEFORE(TEXTAFTER(A1,"-",4),"/"),"-"," "))
```

#### Todo en mayúsculas

```excel
=UPPER(SUBSTITUTE(TEXTBEFORE(TEXTAFTER(A1,"-",4),"/"),"-"," "))
```

#### Todo en minúsculas

```excel
=LOWER(SUBSTITUTE(TEXTBEFORE(TEXTAFTER(A1,"-",4),"/"),"-"," "))
```

---

## 3. Crear Enlaces a PDFs

### 🎯 Objetivo

Generar URLs de PDFs desde rutas de archivos `.qmd`.

### 📋 Suposiciones

- **A2** → `ruta_archivo`
- **B2** → `blog_nombre`

### Fórmula Completa (Excel Español)

```excel
="https://" &
SI(B2="website-achalma","achalmaedison",
   SI(B2="chaska","chaska-x",B2)
) &
".netlify.app/" &
SUSTITUIR(
   TEXTO.DESPUES(A2,B2&"/"),
   "index.qmd",
   "index.pdf"
)
```

### Fórmula Completa (Excel Inglés)

```excel
="https://" &
IF(B2="website-achalma","achalmaedison",
   IF(B2="chaska","chaska-x",B2)
) &
".netlify.app/" &
SUBSTITUTE(
   TEXTAFTER(A2,B2&"/"),
   "index.qmd",
   "index.pdf"
)
```

### 🔍 Ejemplo Real

**Entrada:**

```
ruta_archivo: actus-mercator/inteligencia-comercial/2025-05-15-herramientas/index.qmd
blog_nombre: actus-mercator
```

**Salida:**

```
https://actus-mercator.netlify.app/inteligencia-comercial/2025-05-15-herramientas/index.pdf
```

### 📝 Variantes

#### Con dominio personalizado

```excel
="https://" & B2 & ".com/" & SUBSTITUTE(TEXTAFTER(A2,B2&"/"),"index.qmd","index.pdf")
```

#### Para múltiples extensiones

```excel
="https://" & B2 & ".netlify.app/" & 
SUBSTITUTE(SUBSTITUTE(TEXTAFTER(A2,B2&"/"),"index.qmd","index.pdf"),".html",".pdf")
```

#### Solo el nombre del archivo PDF

```excel
=SUBSTITUTE(TEXTAFTER(A2,"/",-1),"index.qmd","index.pdf")
```

---

## 4. Extraer Fechas de Rutas

### 🎯 Objetivo

Extraer fechas de rutas como:

```
posts/2022-01-17-titulo/index.qmd
```

### Fecha en Formato MM/DD/YYYY

```excel
=TEXT(DATE(LEFT(TEXTAFTER(A2,"/",2),4),MID(TEXTAFTER(A2,"/",2),6,2),MID(TEXTAFTER(A2,"/",2),9,2)),"mm/dd/yyyy")
```

### 🔍 Desglose

#### Extraer año (primeros 4 caracteres)

```excel
LEFT(TEXTAFTER(A2,"/",2),4)
```

Resultado: `2022`

#### Extraer mes (caracteres 6-7)

```excel
MID(TEXTAFTER(A2,"/",2),6,2)
```

Resultado: `01`

#### Extraer día (caracteres 9-10)

```excel
MID(TEXTAFTER(A2,"/",2),9,2)
```

Resultado: `17`

#### Crear fecha

```excel
DATE(2022,01,17)
```

#### Formatear

```excel
TEXT(...,"mm/dd/yyyy")
```

### 📝 Variantes de Formato

#### Formato DD/MM/YYYY

```excel
=TEXT(DATE(...),"dd/mm/yyyy")
```

#### Formato YYYY-MM-DD

```excel
=TEXT(DATE(...),"yyyy-mm-dd")
```

#### Solo año

```excel
=LEFT(TEXTAFTER(A2,"/",2),4)
```

#### Solo mes

```excel
=MID(TEXTAFTER(A2,"/",2),6,2)
```

### Copyright Notice (Solo Año)

```excel
=LEFT(TEXTAFTER(A2,"/",2),4)
```

### Duedate Condicional (Solo para STU)

Si **C2** contiene el tipo de documento:

```excel
=IF(C2="stu",TEXT(DATE(LEFT(TEXTAFTER(A2,"/",2),4),MID(TEXTAFTER(A2,"/",2),6,2),MID(TEXTAFTER(A2,"/",2),9,2)),"mm/dd/yyyy"),"")
```

**Explicación:**

- Si es tipo `stu` → genera fecha
- Si no → celda vacía

---

## 5. Gestión de Tags

### 🎯 Objetivo

Combinar tags existentes con tags nuevos de otra hoja, evitando duplicados.

### Agregar Tags Sin Reemplazar (LibreOffice Calc)

En **METADATOS → columna L (tags)**, fila **L2**:

```excel
=IFERROR(
 IF(
  VLOOKUP(A2,Sheet3.$A:$E,5,0)="",
  L2,
  IF(
   L2="",
   VLOOKUP(A2,Sheet3.$A:$E,5,0),
   L2 & ", " & VLOOKUP(A2,Sheet3.$A:$E,5,0)
  )
 ),
 L2
)
```

### 🔍 Lógica de la Fórmula

1. Busca tag en **Sheet3** usando la ruta (columna A)
2. Si **Sheet3** no tiene tag → mantiene el original
3. Si **METADATOS** está vacío → copia el tag nuevo
4. Si ambos existen → concatena con `,`
5. Si hay error → mantiene el original

### ⚠️ IMPORTANTE: Cómo Aplicar

**NO escribas la fórmula directamente sobre L2 con datos**

**Método seguro:**

1. Inserta columna temporal **M**
2. En **M2** pega la fórmula
3. Copia hacia abajo
4. Copia columna M
5. **Paste Special → Values only** sobre columna L
6. Elimina columna M

### 📝 Variante: Eliminar Duplicados

```excel
=TRIM(SUBSTITUTE(SUBSTITUTE(SUBSTITUTE(
  L2 & ", " & VLOOKUP(A2,Sheet3.$A:$E,5,0),
  L2 & ", ",","),
  "," & L2,","),
  ",,",","))
```

### 🧹 Normalizar Tags (Minúsculas)

```excel
=LOWER(TRIM(SUBSTITUTE(L2,",",", ")))
```

### 🔤 Ordenar Tags Alfabéticamente

_Requiere macro o Power Query - ver sección avanzada_

---

## 6. Extraer Información de Rutas

### Extraer Nombre del Blog

```excel
=LEFT(A2,FIND("/",A2)-1)
```

**Ejemplo:**

- Entrada: `axiomata/posts/2024-01-01-titulo/index.qmd`
- Salida: `axiomata`

### Extraer Carpeta de Posts

```excel
=TRIM(MID(SUBSTITUTE(A2,"/",REPT(" ",100)),100,100))
```

**Ejemplo:**

- Entrada: `axiomata/posts/2024-01-01-titulo/index.qmd`
- Salida: `posts`

### Extraer Carpeta del Artículo

```excel
=TEXTAFTER(TEXTBEFORE(A2,"/index.qmd"),"/",-1)
```

**Ejemplo:**

- Entrada: `axiomata/posts/2024-01-01-titulo/index.qmd`
- Salida: `2024-01-01-titulo`

### Detectar Tipo de Carpeta

```excel
=IF(ISNUMBER(SEARCH("posts",A2)),"posts",
 IF(ISNUMBER(SEARCH("talk",A2)),"talk",
 IF(ISNUMBER(SEARCH("publication",A2)),"publication","otros")))
```

### Contar Niveles de Carpetas

```excel
=LEN(A2)-LEN(SUBSTITUTE(A2,"/",""))
```

---

## 7. Limpieza y Normalización

### Eliminar Espacios Extras

```excel
=TRIM(A1)
```

### Eliminar Todos los Espacios

```excel
=SUBSTITUTE(A1," ","")
```

### Reemplazar Múltiples Guiones por Uno

```excel
=TRIM(SUBSTITUTE(SUBSTITUTE(SUBSTITUTE(A1,"---","-"),"--","-"),"--","-"))
```

### Limpiar Caracteres Especiales

```excel
=SUBSTITUTE(SUBSTITUTE(SUBSTITUTE(SUBSTITUTE(A1,"á","a"),"é","e"),"í","i"),"ó","o")
```

### Eliminar Números del Inicio

```excel
=TRIM(RIGHT(A1,LEN(A1)-FIND(" ",A1)))
```

### Convertir a Snake_Case

```excel
=LOWER(SUBSTITUTE(TRIM(A1)," ","_"))
```

**Ejemplo:**

- Entrada: `Gestión Empresarial`
- Salida: `gestion_empresarial`

### Convertir a Kebab-Case

```excel
=LOWER(SUBSTITUTE(TRIM(A1)," ","-"))
```

**Ejemplo:**

- Entrada: `Economía Internacional`
- Salida: `economia-internacional`

---

## 8. Fórmulas Avanzadas

### Validación de Rutas

Verificar que la ruta tenga el formato correcto:

```excel
=IF(AND(ISNUMBER(FIND("/",A2)),ISNUMBER(FIND("index.qmd",A2))),"Válido","❌ Inválido")
```

### Detectar Artículos con Fecha

```excel
=IF(ISNUMBER(VALUE(MID(TEXTAFTER(A2,"/",-2),1,4))),"Con fecha","⏭️ Sin fecha")
```

### Generar Shorttitle Automático (50 caracteres)

```excel
=IF(LEN(B2)>50,LEFT(B2,47)&"...",B2)
```

### Contar Palabras en un Campo

```excel
=LEN(TRIM(A1))-LEN(SUBSTITUTE(TRIM(A1)," ",""))+1
```

### Extraer Primera Palabra

```excel
=LEFT(A1,FIND(" ",A1&" ")-1)
```

### Extraer Última Palabra

```excel
=TRIM(RIGHT(SUBSTITUTE(A1," ",REPT(" ",100)),100))
```

### Generar Keywords desde Título

```excel
=LOWER(SUBSTITUTE(SUBSTITUTE(B2," ",", "),"  "," "))
```

**Ejemplo:**

- Entrada (título): `Análisis Económico Regional`
- Salida (keywords): `análisis, económico, regional`

### Validar Email

```excel
=IF(AND(ISNUMBER(FIND("@",A1)),ISNUMBER(FIND(".",A1)),LEN(A1)>5),"✅","❌")
```

### Validar ORCID

```excel
=IF(AND(LEN(A1)=19,ISNUMBER(FIND("0000-",A1))),"Válido","❌ Inválido")
```

**Formato válido:** `0000-0001-2345-6789`

### Concatenar Múltiples Columnas con Separador

```excel
=TEXTJOIN(", ",TRUE,A1,B1,C1,D1,E1)
```

**Ejemplo:**

- A1: `economía`
- B1: `estadística`
- C1: `análisis`
- Resultado: `economía, estadística, análisis`

### Eliminar Duplicados en Lista

_Requiere fórmula array o Power Query_

```excel
=UNIQUE(FILTERXML("<t><s>"&SUBSTITUTE(A1,", ","</s><s>")&"</s></t>","//s"))
```

---

## 9. Macros Útiles (VBA)

### 🔧 Eliminar Enter en Rango Seleccionado

```vba
Sub EliminarEnter()
    Dim celda As Range
    For Each celda In Selection
        celda.Value = Replace(celda.Value, vbLf, " ")
        celda.Value = Replace(celda.Value, vbCr, " ")
    Next celda
End Sub
```

### 🔧 Normalizar Tags

```vba
Sub NormalizarTags()
    Dim celda As Range
    For Each celda In Selection
        ' Minúsculas
        celda.Value = LCase(celda.Value)
        ' Reemplazar espacios por guiones bajos
        celda.Value = Replace(celda.Value, " ", "_")
        ' Eliminar acentos (básico)
        celda.Value = Replace(celda.Value, "á", "a")
        celda.Value = Replace(celda.Value, "é", "e")
        celda.Value = Replace(celda.Value, "í", "i")
        celda.Value = Replace(celda.Value, "ó", "o")
        celda.Value = Replace(celda.Value, "ú", "u")
    Next celda
End Sub
```

---

## 10. Atajos de Teclado Útiles

### Excel en Windows

|Atajo|Acción|
|---|---|
|`Ctrl + H`|Buscar y reemplazar|
|`Ctrl + J`|(en Buscar) Captura Enter|
|`Ctrl + 1`|Formato de celdas|
|`Ctrl + Shift + L`|Activar/desactivar filtros|
|`Alt + Enter`|Insertar Enter en celda|
|`Ctrl + Enter`|Llenar selección con fórmula|
|`Ctrl + D`|Rellenar hacia abajo|
|`Ctrl + R`|Rellenar hacia la derecha|

### LibreOffice Calc

|Atajo|Acción|
|---|---|
|`Ctrl + H`|Buscar y reemplazar|
|`Ctrl + J`|(en Buscar) Captura Enter|
|`Ctrl + Shift + F`|Insertar función|
|`Ctrl + ;`|Insertar fecha actual|
|`Ctrl + Shift + ;`|Insertar hora actual|

---

## 11. Tips y Mejores Prácticas

### Al Trabajar con Fórmulas

1. **Siempre prueba en una celda temporal** antes de aplicar a toda la columna
2. **Usa referencias absolutas** (`$A$1`) cuando sea necesario
3. **Nombra rangos** para fórmulas más legibles
4. **Documenta fórmulas complejas** con comentarios en celdas adyacentes
5. **Copia con "Pegar valores"** cuando ya no necesites las fórmulas

### Al Eliminar Enter

1. **Haz backup** antes de operaciones masivas
2. **Usa fórmulas** en vez de buscar/reemplazar cuando necesites deshacer
3. **Verifica el resultado** en varias celdas antes de aplicar a todo

### Al Generar Enlaces

1. **Valida que las URLs funcionen** en navegador
2. **Considera casos especiales** (blogs con nombres diferentes)
3. **Usa hiperenlaces de Excel** para pruebas rápidas

### Al Trabajar con Tags

1. **Mantén formato consistente** (minúsculas, snake_case)
2. **Separa con coma + espacio** (`,` )
3. **Evita duplicados** con validación
4. **Limita cantidad** (3-5 tags por artículo)

---

## 12. Solución de Problemas Comunes

### ❌ Problema: `#VALUE!`

**Causa:** Dato no válido para la función  
**Solución:** Usa `IFERROR()` o `IFNA()`

```excel
=IFERROR(tu_formula,"")
```

### ❌ Problema: `#REF!`

**Causa:** Referencia a celda eliminada  
**Solución:** Revisa referencias de celdas

### ❌ Problema: `#NAME?`

**Causa:** Nombre de función incorrecto  
**Solución:** Verifica idioma de Excel (español/inglés)

### ❌ Problema: Fórmula no calcula

**Causa:** Modo de cálculo manual  
**Solución:** `Fórmulas → Opciones de cálculo → Automático`

### ❌ Problema: Enter no se elimina

**Causa:** Puede ser `CHAR(13)` en vez de `CHAR(10)`  
**Solución:** Usa ambos:

```excel
=SUBSTITUTE(SUBSTITUTE(A1,CHAR(13),""),CHAR(10),"")
```

---

## 📞 Soporte

**Autor:** Edison Achalma  
**Email:** achalmaedison@outlook.com  
**Versión:** 1.0  
**Fecha:** Diciembre 2024

---

## 📝 Changelog

### v1.0 (Diciembre 2024)

- Guía inicial completa
- 8 secciones principales
- 50+ fórmulas documentadas
- Ejemplos prácticos
- Macros VBA incluidos

---

**¡Disfruta automatizando tu gestión de metadatos!** 🚀📊