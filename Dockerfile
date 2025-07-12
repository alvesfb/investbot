"""
Dockerfile de produção para o Sistema de Recomendações de Investimentos
"""
FROM python:3.11-slim as base

# Configurar variáveis de ambiente
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Criar usuário não-root
RUN useradd --create-home --shell /bin/bash app
USER app
WORKDIR /home/app

# Copiar requirements
COPY requirements.txt requirements-prod.txt ./

# Instalar dependências Python
RUN pip install --user --no-cache-dir -r requirements-prod.txt

# Copiar código da aplicação
COPY --chown=app:app . .

# Criar diretórios necessários
RUN mkdir -p data logs

# Expor porta
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Comando padrão
CMD ["python", "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]