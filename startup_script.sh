#!/bin/bash

limpiar(){
    echo "Parando los contenedores, se paciente...";
    
    sudo docker stop maquina03sqli > /dev/null 2>&1
    sudo docker rm maquina03sqli > /dev/null 2>&1
    sudo docker image rm maquina03:sqli > /dev/null 2>&1
    sudo docker network rm DockerRed > /dev/null 2>&1
    echo "Listo, ya puedes cerrar la terminal ;)"
    exit 0
}

trap limpiar SIGINT

echo "Iniciando el laboratorio"

if [ "$(whoami)" != "root" ]; then
    echo "Tienes que ejecutar el script como root o usando sudo."
    exit 1
fi

echo "Inicando entorno, no cierres el proceso"
echo "Iniciando red..."
sudo docker network create --subnet 172.18.0.0/16 DockerRed > /dev/null 2>&1

echo "Iniciando host..."
sudo docker build -t maquina03:sqli . > /dev/null 2>&1
sudo docker create --name maquina03sqli --net DockerRed --ip 172.18.0.5 maquina03:sqli > /dev/null 2>&1
sudo docker start maquina03sqli > /dev/null 2>&1

echo "Laboratorio deplegado, para cerrarlo presiona CTRL+C y espera a que se cierre  "
echo "-------------------------------------------------- "
echo ""
echo "Desplegados 1 host en red 172.18.0.5 "
echo "Indentifica la vulnerabilidad, atacalo y consigue 2 flags "
echo "Buena suerte "
echo ""
echo "-------------------------------------------------- "
echo ""
echo "Machine made by dpmcyber for H4ckn3t Team :) "
echo "Team contact: https://linktr.ee/h4ckn3t "
echo "dpmcyber contact: https://linktr.ee/dpmcyber"

#Para mantener el script esperando a que pulse en SIGINT
while true; do
    sleep 1
done