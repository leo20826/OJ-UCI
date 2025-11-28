# Base image: Python 3.11 (recomendado para mejor compatibilidad con paquetes)
FROM python:3.11-slim-bookworm

# Evitar preguntas interactivas de apt
ENV DEBIAN_FRONTEND=noninteractive

# Instalar dependencias del sistema
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git gcc g++ make curl gettext wget \
        libxml2-dev libxslt1-dev zlib1g-dev \
        default-mysql-client default-libmysqlclient-dev \  # CAMBIADO: Mejor compatibilidad
        libjpeg-dev pkg-config && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    apt-get autoremove -y && \
    apt-get clean && \  # AÑADIDO: Limpieza adicional
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar archivos de requerimientos PRIMERO (para cache de Docker)
COPY repo/requirements.txt .
COPY repo/additional_requirements.txt .
COPY repo/package.json .
COPY repo/package-lock.json .

# Instalar Node.js packages
RUN npm ci

# Instalar dependencias de Python
RUN pip install --no-cache-dir --upgrade pip && \  # AÑADIDO: Actualizar pip primero
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r additional_requirements.txt

# Copiar todo el repositorio
COPY repo/ .

# Variables de entorno recomendadas para Django
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DJANGO_SETTINGS_MODULE="dmoj.local_settings"  # AÑADIDO: Para asegurar config

# Crear directorios necesarios para DMOJ
RUN mkdir -p /problems /media /assets/static /assets/resources && \
    chmod -R 755 /problems /media /assets  # AÑADIDO: Permisos para DMOJ

# Puerto por defecto
EXPOSE 8000

# Comando por defecto para desarrollo (mejorado)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]