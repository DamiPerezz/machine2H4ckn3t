FROM ubuntu:20.04

ENV TZ="Europe/Madrid"

RUN apt update -y 

RUN apt-get install -yq tzdata && \
ln -fs /usr/share/zoneinfo/Europe/Madrid /etc/localtime && \
dpkg-reconfigure -f noninteractive tzdata

RUN mkdir -p /maquina

COPY . /maquina

RUN apt update 

RUN apt install python3 -y

RUN apt install python3-pip -y 

RUN pip3 install --upgrade pip  

RUN pip3 install -r /maquina/requirements.txt


EXPOSE 80

CMD ["python3","/maquina/app.py"]