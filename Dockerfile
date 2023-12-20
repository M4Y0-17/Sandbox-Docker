FROM python:3.10

# Establece el directorio de trabajo
WORKDIR /var/www

# Primero copia los archivos de requisitos
COPY ./www/requirements.txt /var/www/

# Instala las dependencias
RUN pip install -r requirements.txt

# Instalar Docker CLI
RUN apt-get update && apt-get install -y curl gnupg lsb-release
RUN curl -fsSL https://download.docker.com/linux/debian/gpg | apt-key add -
RUN echo "deb [arch=amd64] https://download.docker.com/linux/debian $(lsb_release -cs) stable" > /etc/apt/sources.list.d/docker.list
RUN apt-get update && apt-get install -y docker-ce-cli

# Instalar Docker-compose
RUN curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
RUN chmod +x /usr/local/bin/docker-compose