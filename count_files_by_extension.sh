#!/bin/bash

# Directorio a analizar (por defecto ~/Documents/biblioteca, pero se puede pasar como argumento)
DIRECTORY=${1:-~/Documents/biblioteca}

# Verificar si el directorio existe
if [ ! -d "$DIRECTORY" ]; then
  echo "Error: El directorio '$DIRECTORY' no existe."
  exit 1
fi

echo "Contando archivos en: $DIRECTORY"
echo "--------------------------------"

# Contar archivos por extensión
find "$DIRECTORY" -type f | while read -r file; do
  # Extraer la extensión del archivo (en minúsculas)
  extension=$(echo "${file##*.}" | tr '[:upper:]' '[:lower:]')
  # Si no tiene extensión, marcar como 'sin_extension'
  [ "$extension" = "$file" ] && extension="sin_extension"
  echo "$extension"
done | sort | uniq -c | awk '{printf "%-15s: %s\n", $2, $1}'

# Contar el total de archivos
total=$(find "$DIRECTORY" -type f | wc -l)
echo "--------------------------------"
echo "Total de archivos: $total"
