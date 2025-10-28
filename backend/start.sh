#!/bin/bash

# Matar procesos en puerto 8000
lsof -ti:8000 | xargs kill -9 2>/dev/null

# Limpiar entorno virtual
rm -rf venv

# Crear nuevo entorno
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias mínimas
pip3 install --quiet fastapi uvicorn[standard] sqlmodel aiosqlite pydantic pydantic-settings python-jose[cryptography] python-dotenv bcrypt

# Crear admin
python3 -m app.scripts.create_admin

# Iniciar servidor
python3 -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
