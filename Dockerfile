FROM python:3.11-slim

# Evita cache e problemas de encoding
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instala dependências do sistema (PostgreSQL + Cairo + Pango + GDK + Fonts)
RUN apt-get update && apt-get install -y --no-install-recommends \
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
    libcairo2 \
    libcairo2-dev \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    shared-mime-info \
    fonts-liberation \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# Define o diretório de trabalho
WORKDIR /code

# Copia e instala dependências Python
COPY requirements.txt /code/
RUN python -m pip install --upgrade pip
RUN python -m pip install --no-cache-dir -r requirements.txt

# Copia o restante do projeto
COPY . /code/

# Exponha a porta do Django
EXPOSE 8000

# Comando padrão (sobrescrito pelo docker-compose)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
