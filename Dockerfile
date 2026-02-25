# Imagem base Python 3.11 slim
FROM python:3.11-slim

# Metadados
LABEL maintainer="gestor_visitas_escolas"
LABEL description="Sistema de Gestao de Visitas a Escolas"

# Variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=gestor.settings

# Diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Criar diretórios necessários com permissoes abertas
RUN mkdir -p data static/uploads anexos relatorios staticfiles \
    && chmod -R 777 data static/uploads anexos relatorios

# Coletar arquivos estáticos
RUN python manage.py collectstatic --noinput 2>/dev/null || true

# Expor porta
EXPOSE 5000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/health', timeout=5)" || exit 1

# Comando: roda migrations, inicializa DB e inicia Gunicorn
CMD ["sh", "-c", "python manage.py migrate --noinput && python manage.py init_db && gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 gestor.wsgi:application"]
