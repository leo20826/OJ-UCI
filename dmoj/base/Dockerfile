# Base image: Python 3.12 slim (Bookworm)
FROM python:3.12-slim-bookworm

# Evitar preguntas interactivas de apt
ENV DEBIAN_FRONTEND=noninteractive

# Instalar dependencias del sistema
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git gcc g++ make curl gettext wget \
        libxml2-dev libxslt1-dev zlib1g-dev \
        mariadb-client libmariadb-dev \
        libjpeg-dev pkg-config && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar archivos de requerimientos
COPY repo/requirements.txt .
COPY repo/additional_requirements.txt .
COPY repo/package.json .
COPY repo/package-lock.json .

# Instalar Node.js packages
RUN npm ci

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r additional_requirements.txt

# Copiar todo el repositorio
COPY repo/ .

# Variables de entorno recomendadas para Django
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Puerto por defecto
EXPOSE 8000

# Comando por defecto para desarrollo (puedes cambiar a gunicorn en producción)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
