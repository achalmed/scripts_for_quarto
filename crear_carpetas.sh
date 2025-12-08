#!/bin/bash

# Lista de nombres de carpetas a crear. Puedes copiar y pegar aquí tu lista.
folders=$(cat <<EOF
2022-07-131-01-02-manipulacion-de-datos
2022-07-132-01-03-visualizacion-de-datos
2022-07-133-01-04-modelo-de-machine-learning-i-analisis-exploratorio
2022-07-134-01-05-modelo-de-machine-learning-ii-modelo-de-clasificacion
2022-07-135-01-06-modelo-de-machine-learning-iii-modelo-de-regresion
2022-07-136-01-07-modelo-de-machine-learning-iv-tex-mining
EOF
)

# Convierte el texto en un array, separando por líneas
IFS=$'\n' read -rd '' -a folders_array <<< "$folders"

# Itera sobre cada elemento en el array 'folders_array'
for folder in "${folders_array[@]}"; do
    # Crea la carpeta si no existe
    if [ ! -d "$folder" ]; then
        mkdir "$folder"
        echo "Carpeta creada: $folder"
    else
        echo "La carpeta '$folder' ya existe."
    fi
done
