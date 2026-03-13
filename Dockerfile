# ---- Estágio 1: Build do React (Vite) ----
FROM node:22-slim AS react-build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci --silent
COPY frontend/ ./
RUN npm run build

# ---- Estágio 2: App Django ----
FROM python:3.11-slim

LABEL maintainer="gestor_visitas_escolas"
LABEL description="Sistema de Gestao de Visitas a Escolas"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=gestor.settings

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Copia build React do estágio anterior
COPY --from=react-build /app/frontend/dist ./frontend/dist

RUN mkdir -p data static/uploads anexos relatorios staticfiles \
    && chmod -R 777 data static/uploads anexos relatorios

RUN python manage.py collectstatic --noinput 2>/dev/null || true

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/health', timeout=5)" || exit 1

CMD ["sh", "-c", "python manage.py migrate --noinput && python manage.py init_db && gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 gestor.wsgi:application"]
