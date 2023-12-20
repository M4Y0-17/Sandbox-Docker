#!/bin/bash

# Ejecutar el script para obtener la IP del host
source ./get_host_ip.sh

# Iniciar los contenedores
docker-compose up -d
