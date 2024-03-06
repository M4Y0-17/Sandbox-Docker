#!/bin/bash

# Obtener la dirección IP del host
HOST_IP=$(hostname -I | awk '{print $1}')

# Imprimir la dirección IP para verificación
echo "Host IP: $HOST_IP"

# Exportar la dirección IP como variable de entorno
export HOST_IP
