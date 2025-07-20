#!/bin/bash
# scripts/setup_postgresql_day1.sh
# Setup PostgreSQL - DIA 1 MANHÃ da Migração

echo "🚀 MIGRAÇÃO POSTGRESQL - DIA 1 MANHÃ"
echo "================================================"

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
PURPLE='\033[0;35m'
NC='\033[0m'

print_step() {
    echo -e "${BLUE}📋 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${PURPLE}ℹ️  $1${NC}"
}

# ==================== PRÉ-REQUISITOS ====================
print_step "Verificando pré-requisitos..."

# Verificar se Docker está instalado
if ! command -v docker &> /dev/null; then
    print_error "Docker não está instalado!"
    echo "Instale Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

# Verificar se Docker Compose está instalado
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose não está instalado!"
    echo "Instale Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

# Verificar se ambiente virtual está ativo
if [[ "$VIRTUAL_ENV" == "" ]]; then
    print_error "Ambiente virtual não ativado!"
    echo "Execute: source venv/bin/activate"
    exit 1
fi

print_success "Pré-requisitos OK"

# ==================== BACKUP DO SISTEMA ATUAL ====================
print_step "Fazendo backup do sistema SQLite atual..."

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="./database/sqlite_backup_${TIMESTAMP}"

mkdir -p "$BACKUP_DIR"

# Backup do banco SQLite
if [ -f "./data/investment_system.db" ]; then
    cp "./data/investment_system.db" "$BACKUP_DIR/"
    print_success "Backup SQLite criado: $BACKUP_DIR"
else
    print_warning "Banco SQLite não encontrado (tudo bem, continuando)"
fi

# Backup dos modelos atuais
cp "./database/models.py" "$BACKUP_DIR/models_sqlite.py"
cp "./database/connection.py" "$BACKUP_DIR/connection_sqlite.py"

print_success "Backup dos arquivos de configuração criado"

# ==================== CRIAR ESTRUTURA POSTGRESQL ====================
print_step "Criando estrutura de diretórios PostgreSQL..."

# Criar diretórios necessários
mkdir -p ./database/postgresql/{init,backups,config}
mkdir -p ./data/postgresql
mkdir -p ./data/pgadmin
mkdir -p ./logs/postgresql
mkdir -p ./nginx

print_success "Estrutura de diretórios criada"

# ==================== CONFIGURAR VARIABLES DE AMBIENTE ====================
print_step "Configurando variáveis de ambiente PostgreSQL..."

# Criar arquivo .env.postgresql se não existir
if [ ! -f ".env.postgresql" ]; then
    cat > .env.postgresql << 'EOF'
# PostgreSQL Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=investment_system
POSTGRES_USER=investment_user
POSTGRES_PASSWORD=investment_secure_pass_2024

# Connection Pool
POSTGRES_POOL_SIZE=20
POSTGRES_MAX_OVERFLOW=30
POSTGRES_POOL_TIMEOUT=30
POSTGRES_POOL_RECYCLE=3600

# SSL
POSTGRES_SSLMODE=prefer

# Performance
POSTGRES_ECHO=false
POSTGRES_ECHO_POOL=false
POSTGRES_CONNECT_TIMEOUT=10
POSTGRES_COMMAND_TIMEOUT=60

# Environment
ENVIRONMENT=development
DATABASE_TYPE=postgresql
EOF
    print_success "Arquivo .env.postgresql criado"
else
    print_info "Arquivo .env.postgresql já existe"
fi

# ==================== CONFIGURAÇÃO POSTGRESQL ====================
print_step "Criando configuração PostgreSQL personalizada..."

cat > ./database/postgresql/postgresql.conf << 'EOF'
# PostgreSQL configuration for Investment System
# Performance optimizations

# Memory settings
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
work_mem = 16MB

# Checkpoint settings
checkpoint_completion_target = 0.9
wal_buffers = 16MB
max_wal_size = 2GB
min_wal_size = 1GB

# Connection settings
max_connections = 200
superuser_reserved_connections = 3

# Query planner
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200

# Logging
log_min_duration_statement = 1000
log_statement = 'none'
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '

# Autovacuum
autovacuum = on
autovacuum_max_workers = 3
autovacuum_naptime = 20s

# Time zone
timezone = 'UTC'
log_timezone = 'UTC'
EOF

print_success "Configuração PostgreSQL criada"

# ==================== SCRIPT DE INICIALIZAÇÃO ====================
print_step "Criando scripts de inicialização..."

cat > ./database/postgresql/init/01_init_extensions.sql << 'EOF'
-- Investment System PostgreSQL Initialization
-- Extensions and Basic Setup

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create schemas if needed
CREATE SCHEMA IF NOT EXISTS analytics;
CREATE SCHEMA IF NOT EXISTS audit;

-- Set default permissions
GRANT USAGE ON SCHEMA public TO investment_user;
GRANT CREATE ON SCHEMA public TO investment_user;

-- Create custom types
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'data_quality_enum') THEN
        CREATE TYPE data_quality_enum AS ENUM ('excellent', 'good', 'medium', 'poor', 'critical');
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'stock_status_enum') THEN
        CREATE TYPE stock_status_enum AS ENUM ('active', 'suspended', 'delisted', 'under_review');
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'recommendation_enum') THEN
        CREATE TYPE recommendation_enum AS ENUM ('strong_buy', 'buy', 'hold', 'sell', 'strong_sell');
    END IF;
END$$;

-- Configure settings for investment system
ALTER DATABASE investment_system SET timezone TO 'UTC';
ALTER DATABASE investment_system SET lc_monetary TO 'pt_BR.UTF-8';
ALTER DATABASE investment_system SET default_text_search_config TO 'portuguese';

-- Create audit function for tracking changes
CREATE OR REPLACE FUNCTION audit_trigger_function()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        NEW.created_at = COALESCE(NEW.created_at, NOW());
        NEW.updated_at = NOW();
        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' THEN
        NEW.updated_at = NOW();
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Create helper functions
CREATE OR REPLACE FUNCTION calculate_percentile_rank(
    score NUMERIC,
    table_name TEXT,
    score_column TEXT,
    filter_condition TEXT DEFAULT ''
)
RETURNS NUMERIC AS $$
DECLARE
    rank_result NUMERIC;
    query_text TEXT;
BEGIN
    query_text := format(
        'SELECT percent_rank() OVER (ORDER BY %I) FROM %I WHERE %I = $1',
        score_column, table_name, score_column
    );
    
    IF filter_condition != '' THEN
        query_text := query_text || ' AND ' || filter_condition;
    END IF;
    
    EXECUTE query_text USING score INTO rank_result;
    RETURN COALESCE(rank_result * 100, 0);
END;
$$ LANGUAGE plpgsql;

-- Log initialization
INSERT INTO pg_stat_statements_reset();
SELECT 'PostgreSQL initialization completed for Investment System' as status;
EOF

print_success "Script de inicialização criado"

# ==================== CONFIGURAÇÃO PGADMIN ====================
cat > ./database/postgresql/pgadmin/servers.json << 'EOF'
{
    "Servers": {
        "1": {
            "Name": "Investment System",
            "Group": "Servers",
            "Host": "postgres",
            "Port": 5432,
            "MaintenanceDB": "investment_system",
            "Username": "investment_user",
            "SSLMode": "prefer",
            "SSLCert": "<STORAGE_DIR>/.postgresql/postgresql.crt",
            "SSLKey": "<STORAGE_DIR>/.postgresql/postgresql.key",
            "SSLCompression": 0,
            "Timeout": 10,
            "UseSSHTunnel": 0,
            "TunnelPort": "22",
            "TunnelAuthentication": 0
        }
    }
}
EOF

print_success "Configuração pgAdmin criada"

# ==================== NGINX CONFIGURAÇÃO ====================
cat > ./nginx/dev.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    upstream postgres_pool {
        server postgres:5432;
    }
    
    upstream pgadmin_upstream {
        server pgadmin:80;
    }
    
    server {
        listen 80;
        server_name localhost;
        
        location /pgadmin/ {
            proxy_pass http://pgadmin_upstream/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        location /health {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }
    }
}
EOF

print_success "Configuração Nginx criada"

# ==================== INSTALAR DEPENDÊNCIAS PYTHON ====================
print_step "Instalando dependências Python para PostgreSQL..."

# Instalar psycopg2 e outras dependências PostgreSQL
pip install psycopg2-binary
pip install asyncpg  # Para suporte assíncrono futuro
pip install sqlalchemy --no-deps  # Sem dependências automáticas
pip install sqlalchemy[postgresql] --upgrade --no-deps

print_success "Dependências Python instaladas"

# ==================== ATUALIZAR REQUIREMENTS.TXT ====================
print_step "Atualizando requirements.txt..."

# Adicionar dependências PostgreSQL ao requirements.txt
cat >> requirements.txt << 'EOF'

# PostgreSQL Support
psycopg2-binary==2.9.9
asyncpg==0.29.0
sqlalchemy==2.0.23
EOF

print_success "requirements.txt atualizado"

# ==================== CRIAR DOCKER COMPOSE ====================
print_step "Copiando docker-compose.postgresql.yml..."
print_info "Arquivo docker-compose.postgresql.yml deve ter sido criado previamente"

# ==================== INICIAR POSTGRESQL ====================
print_step "Iniciando PostgreSQL via Docker..."

# Parar containers existentes
docker-compose -f docker-compose.postgresql.yml down 2>/dev/null || true

# Iniciar PostgreSQL
docker-compose -f docker-compose.postgresql.yml up -d postgres

print_info "Aguardando PostgreSQL inicializar..."
sleep 10

# Verificar se PostgreSQL está rodando
if docker-compose -f docker-compose.postgresql.yml ps postgres | grep -q "Up"; then
    print_success "PostgreSQL está rodando"
else
    print_error "PostgreSQL falhou ao inicializar"
    docker-compose -f docker-compose.postgresql.yml logs postgres
    exit 1
fi

# ==================== VERIFICAR CONEXÃO ====================
print_step "Verificando conexão PostgreSQL..."

# Teste básico de conexão
if docker exec investment-postgres pg_isready -U investment_user -d investment_system >/dev/null 2>&1; then
    print_success "Conexão PostgreSQL OK"
else
    print_error "Falha na conexão PostgreSQL"
    exit 1
fi

# ==================== CRIAR SCHEMA INICIAL ====================
print_step "Aplicando schema inicial..."

# Importar e testar novos modelos
python3 << 'EOF'
import sys
import os
sys.path.insert(0, os.getcwd())

try:
    # Configurar variáveis de ambiente
    os.environ.update({
        'POSTGRES_HOST': 'localhost',
        'POSTGRES_PORT': '5432',
        'POSTGRES_DB': 'investment_system',
        'POSTGRES_USER': 'investment_user',
        'POSTGRES_PASSWORD': 'investment_secure_pass_2024'
    })
    
    # Testar conexão
    from database.connection_postgresql import check_database_connection
    if check_database_connection():
        print("✅ Conexão PostgreSQL testada com sucesso")
    else:
        print("❌ Falha no teste de conexão PostgreSQL")
        sys.exit(1)
    
    # Criar tabelas
    from database.connection_postgresql import create_tables
    if create_tables():
        print("✅ Tabelas PostgreSQL criadas com sucesso")
    else:
        print("❌ Falha na criação das tabelas PostgreSQL")
        sys.exit(1)
        
except Exception as e:
    print(f"❌ Erro no setup PostgreSQL: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
EOF

if [ $? -eq 0 ]; then
    print_success "Schema PostgreSQL aplicado com sucesso"
else
    print_error "Falha na aplicação do schema"
    exit 1
fi

# ==================== INICIAR PGADMIN ====================
print_step "Iniciando pgAdmin..."

docker-compose -f docker-compose.postgresql.yml up -d pgadmin

sleep 5

if docker-compose -f docker-compose.postgresql.yml ps pgadmin | grep -q "Up"; then
    print_success "pgAdmin está rodando"
    print_info "Acesse pgAdmin em: http://localhost:5050"
    print_info "Email: admin@investment.local"
    print_info "Senha: pgadmin_secure_2024"
else
    print_warning "pgAdmin pode ter problemas - verifique logs"
fi

# ==================== INICIAR REDIS (PREPARAÇÃO FUTURO) ====================
print_step "Iniciando Redis (preparação para fases futuras)..."

docker-compose -f docker-compose.postgresql.yml up -d redis

sleep 3

if docker-compose -f docker-compose.postgresql.yml ps redis | grep -q "Up"; then
    print_success "Redis está rodando"
else
    print_warning "Redis pode ter problemas - verifique logs"
fi

# ==================== VERIFICAÇÕES FINAIS ====================
print_step "Executando verificações finais..."

# Verificar se todos os serviços estão rodando
echo ""
echo "📊 STATUS DOS SERVIÇOS:"
docker-compose -f docker-compose.postgresql.yml ps

# Testar conexão Python final
print_step "Teste final de conexão Python → PostgreSQL..."

python3 << 'EOF'
import sys
import os
sys.path.insert(0, os.getcwd())

try:
    from database.connection_postgresql import get_database_info
    
    db_info = get_database_info()
    
    if 'error' not in db_info:
        print(f"✅ Banco: {db_info.get('database')}")
        print(f"✅ Tipo: {db_info.get('type')}")
        print(f"✅ Host: {db_info.get('host')}:{db_info.get('port')}")
        print(f"✅ Tabelas: {db_info.get('table_count', 0)}")
        print(f"✅ Tamanho: {db_info.get('size', 'N/A')}")
        print(f"✅ Conexões ativas: {db_info.get('active_connections', 0)}")
        
        # Verificar tabelas específicas
        expected_tables = ['stocks', 'recommendations', 'fundamental_analyses', 'agent_sessions', 'market_data']
        existing_tables = db_info.get('tables', [])
        
        print("\n📋 VERIFICAÇÃO DE TABELAS:")
        for table in expected_tables:
            if table in existing_tables:
                print(f"   ✅ {table}")
            else:
                print(f"   ❌ {table} (faltando)")
        
        print("\n🎉 PostgreSQL configurado com sucesso!")
        
    else:
        print(f"❌ Erro na verificação: {db_info.get('error')}")
        sys.exit(1)
        
except Exception as e:
    print(f"❌ Erro na verificação final: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
EOF

if [ $? -eq 0 ]; then
    print_success "Verificação final passou"
else
    print_error "Falha na verificação final"
    exit 1
fi

# ==================== CRIAR SCRIPT DE AMBIENTE ====================
print_step "Criando script para carregar ambiente PostgreSQL..."

cat > ./scripts/load_postgresql_env.sh << 'EOF'
#!/bin/bash
# Script para carregar ambiente PostgreSQL

echo "🔄 Carregando ambiente PostgreSQL..."

# Carregar variáveis do .env.postgresql
if [ -f ".env.postgresql" ]; then
    export $(cat .env.postgresql | grep -v '^#' | xargs)
    echo "✅ Variáveis PostgreSQL carregadas"
else
    echo "❌ Arquivo .env.postgresql não encontrado"
    exit 1
fi

# Verificar se PostgreSQL está rodando
if docker-compose -f docker-compose.postgresql.yml ps postgres | grep -q "Up"; then
    echo "✅ PostgreSQL está rodando"
else
    echo "⚠️  PostgreSQL não está rodando - iniciando..."
    docker-compose -f docker-compose.postgresql.yml up -d postgres
    sleep 5
fi

echo "🎯 Ambiente PostgreSQL pronto!"
echo ""
echo "📊 URLs de acesso:"
echo "   PostgreSQL: localhost:5432"
echo "   pgAdmin: http://localhost:5050"
echo "   Redis: localhost:6379"
echo ""
echo "🔐 Credenciais:"
echo "   DB User: $POSTGRES_USER"
echo "   DB Name: $POSTGRES_DB"
echo "   pgAdmin: admin@investment.local / pgadmin_secure_2024"
EOF

chmod +x ./scripts/load_postgresql_env.sh

print_success "Script de ambiente criado: ./scripts/load_postgresql_env.sh"

# ==================== RESUMO FINAL ====================
echo ""
echo "🎉 DIA 1 MANHÃ - SETUP POSTGRESQL CONCLUÍDO!"
echo "=================================================="
echo ""
echo -e "${GREEN}✅ O que foi criado:${NC}"
echo "   🐳 Docker Compose PostgreSQL + pgAdmin + Redis"
echo "   📊 Schema PostgreSQL otimizado (50+ campos padronizados)"
echo "   🔧 Configurações de performance aplicadas"
echo "   🛡️  Extensões PostgreSQL habilitadas"
echo "   📝 Scripts de inicialização e backup"
echo "   🌐 pgAdmin configurado"
echo ""
echo -e "${BLUE}📂 Arquivos criados:${NC}"
echo "   • docker-compose.postgresql.yml"
echo "   • database/models_postgresql.py"
echo "   • database/connection_postgresql.py"
echo "   • database/postgresql/init/01_init_extensions.sql"
echo "   • .env.postgresql"
echo "   • scripts/load_postgresql_env.sh"
echo ""
echo -e "${PURPLE}🔗 URLs de acesso:${NC}"
echo "   • PostgreSQL: localhost:5432"
echo "   • pgAdmin: http://localhost:5050"
echo "   • Redis: localhost:6379"
echo ""
echo -e "${YELLOW}🔑 Credenciais:${NC}"
echo "   • DB: investment_user / investment_secure_pass_2024"
echo "   • pgAdmin: admin@investment.local / pgadmin_secure_2024"
echo ""
echo -e "${GREEN}🚀 Próximos passos (DIA 1 TARDE):${NC}"
echo "   1. Atualizar database/models.py → models_postgresql.py"
echo "   2. Atualizar database/connection.py → connection_postgresql.py"
echo "   3. Atualizar config/settings.py com PostgreSQL"
echo "   4. Testar migração dos repositories"
echo ""
echo -e "${BLUE}💡 Comandos úteis:${NC}"
echo "   • Carregar ambiente: source ./scripts/load_postgresql_env.sh"
echo "   • Ver logs: docker-compose -f docker-compose.postgresql.yml logs"
echo "   • Parar serviços: docker-compose -f docker-compose.postgresql.yml down"
echo "   • Backup: ./scripts/backup_postgresql.sh"
echo ""
echo -e "${GREEN}✅ DIA 1 MANHÃ COMPLETO - PostgreSQL rodando!${NC}"
EOF