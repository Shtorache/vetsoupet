FROM python:3.11-slim

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    g++ \
    curl \
    netcat-traditional \
    build-essential \
    libffi-dev \
    libjpeg-dev \
    zlib1g-dev \
    pkg-config \
    libcairo2-dev \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /code

# Copia requirements e atualiza pip
COPY requirements.txt /code/
RUN python -m pip install --upgrade pip
RUN python -m pip install --no-cache-dir -r requirements.txt

# Copia todo o projeto
COPY . /code/

EXPOSE 8000

# Mantemos o entrypoint simples, o comando final vem do docker-compose
