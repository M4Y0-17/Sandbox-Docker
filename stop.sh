#!/bin/bash

# Parar contenedores
docker stop $(docker ps -aq)

# Eliminar contenedores
docker rm $(docker ps -aq)
