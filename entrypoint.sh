#!/bin/bash

# Corrige permissoes dos volumes montados
chown -R appuser:appuser /app/data /app/static/uploads /app/anexos /app/relatorios

# Inicia gunicorn como appuser
exec gosu appuser gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 app:app
