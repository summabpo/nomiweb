#!/bin/bash

# Move to app directory
cd /app

# Clone or pull the repository
if [ -d "tu_repositorio" ]; then
  cd tu_repositorio
  git pull origin master
else
  git clone https://github.com/tu_usuario/tu_repositorio.git
  cd tu_repositorio
fi

# Check if Docker build fails
if ! docker build -t nombre_de_la_imagen . ; then
  echo "Docker build failed, rolling back to previous version"
  docker rmi nombre_de_la_imagen
  exit 1
fi

# Check if Docker service is running
if [ "$(docker service ls -q -f name=nombre_del_servicio)" ]; then
  echo "Updating Docker service"
  docker service update --image nombre_de_la_imagen nombre_del_servicio
fi
