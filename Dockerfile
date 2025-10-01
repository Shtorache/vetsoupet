FROM python:3.11-slim

# Instala dependências do Postgres e utilitários
RUN apt-get update && apt-get install -y \
    libpq-dev gcc curl netcat-traditional && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /code

# Copia requirements e instala dependências
COPY requirements.txt /code/
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o projeto
COPY . /code/

EXPOSE 8000

# Mantemos o entrypoint simples, o comando final vem do docker-compose
