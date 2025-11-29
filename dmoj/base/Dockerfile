FROM python:3.11-slim-bookworm  # ACTUALIZADO: bullseye → bookworm

# Evitar preguntas interactivas de apt
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y --no-install-recommends \  # AÑADIDO: --no-install-recommends
        git gcc g++ make curl gettext wget \
        libxml2-dev libxslt1-dev zlib1g-dev \
        default-mysql-client default-libmysqlclient-dev \  # CAMBIADO: mejor compatibilidad
        libjpeg-dev pkg-config && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \  # ACTUALIZADO: 18.x → 20.x
    apt-get install -y nodejs && \
    apt-get autoremove -y && \
    apt-get clean && \  # AÑADIDO: limpieza
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*  # MEJORADO: más limpieza

WORKDIR /
COPY repo/requirements.txt .
COPY repo/additional_requirements.txt .
COPY repo/package.json .
COPY repo/package-lock.json .

RUN npm ci && \  # CAMBIADO: npm install → npm ci (más consistente)
    pip install --no-cache-dir --upgrade pip && \  # AÑADIDO: actualizar pip primero
    pip install --no-cache-dir -r requirements.txt && \  # AÑADIDO: --no-cache-dir
    pip install --no-cache-dir -r additional_requirements.txt