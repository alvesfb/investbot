# Setup do Ambiente de Desenvolvimento - Fase 1
# Sistema de Recomendações de Investimentos

# 1. CRIAR E ATIVAR VIRTUAL ENVIRONMENT
echo "🚀 Criando virtual environment..."
python3.11 -m venv venv

# Ativar o venv (Linux/macOS)
source venv/bin/activate

# Ativar o venv (Windows)
# venv\Scripts\activate

# Verificar se está ativo
which python
python --version

# 2. UPGRADE PIP E INSTALAR FERRAMENTAS BÁSICAS
echo "📦 Atualizando pip e instalando ferramentas básicas..."
python -m pip install --upgrade pip
pip install wheel setuptools

# 3. INSTALAR DEPENDÊNCIAS CORE DA FASE 1
echo "🔧 Instalando dependências principais..."

# Agno Framework (Multi-agent system)
pip install agno

# FastAPI para APIs REST
pip install fastapi uvicorn[standard]

# Database
pip install sqlalchemy sqlite3 alembic

# Validação de dados
pip install pydantic pydantic-settings

# Cliente HTTP e APIs
pip install httpx requests

# Processamento de dados
pip install pandas numpy

# Logging e configuração
pip install python-multipart python-dotenv loguru

# Desenvolvimento e testes
pip install pytest pytest-asyncio pytest-cov black isort flake8 mypy

# 4. INSTALAR MCP SERVERS NECESSÁRIOS
echo "🌐 Instalando MCP servers..."

# MCP YFinance para dados de mercado
pip install mcp-server-yfinance

# MCP Filesystem para manipulação de arquivos
pip install mcp-server-filesystem

# 5. CONFIGURAR CLAUDE API
echo "🤖 Configurando Claude API..."
# Criar arquivo .env (será feito separadamente)

# 6. SALVAR DEPENDÊNCIAS
echo "💾 Salvando dependências..."
pip freeze > requirements.txt

echo "✅ Setup básico concluído!"
echo "Próximos passos:"
echo "1. Configurar arquivo .env com chaves da API"
echo "2. Criar estrutura de pastas"
echo "3. Configurar Docker Compose"