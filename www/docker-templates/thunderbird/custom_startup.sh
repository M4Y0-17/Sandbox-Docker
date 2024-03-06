#!/bin/bash

# Lee la ruta del archivo .eml desde la variable de entorno
EML_FILE_PATH="/home/ubuntu/eml_file.eml"

# Espera un momento para asegurar que el sistema esté listo
sleep 10
thunderbird "$EML_FILE_PATH"
# Comprueba si la variable no está vacía y el archivo existe, luego abre Thunderbird con el archivo
if [ -n "$EML_FILE_PATH" ] && [ -f "$EML_FILE_PATH" ]; then
    thunderbird "$EML_FILE_PATH"
else
    echo "Archivo .eml no encontrado o ruta no especificada."
fi
