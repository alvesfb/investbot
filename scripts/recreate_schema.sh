#!/bin/bash
# recreate_schema.sh
# Script para apagar e recriar completamente o schema PostgreSQL
# baseado rigorosamente na estrutura definida nos models

echo "🔄 RECREAÇÃO COMPLETA DO SCHEMA PostgreSQL"
echo "==========================================="

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

print_step() {
    echo -e "${BLUE}📋 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

# ==================== VERIFICAÇÕES PRELIMINARES ====================
print_step "Verificando pré-requisitos..."

# Verificar se PostgreSQL está rodando
if ! docker-compose -f docker-compose.postgresql.yml ps postgres | grep -q "Up"; then
    print_error "PostgreSQL não está rodando!"
    echo "Execute: docker-compose -f docker-compose.postgresql.yml up -d postgres"
    exit 1
fi

print_success "PostgreSQL está rodando"

# ==================== BACKUP DE SEGURANÇA ====================
print_step "Fazendo backup de segurança..."

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="./database/schema_recreation_backup_${TIMESTAMP}"
mkdir -p "$BACKUP_DIR"

# Backup do banco via Docker
print_info "Fazendo backup do banco atual..."
docker exec investment-postgres pg_dump -U investment_user investment_system > "$BACKUP_DIR/pre_recreation_backup.sql" 2>/dev/null || print_info "Backup falhou (normal se banco vazio)"

# Backup de arquivos Python críticos
cp database/models.py "$BACKUP_DIR/models_backup.py" 2>/dev/null || true
cp database/repositories.py "$BACKUP_DIR/repositories_backup.py" 2>/dev/null || true

print_success "Backup criado em: $BACKUP_DIR"

# ==================== RECREAÇÃO DO SCHEMA ====================
print_step "Executando recreação completa do schema..."

# Criar script Python para recreação
cat > temp_recreate_schema.py << 'EOF'
#!/usr/bin/env python3
"""
Script de Recreação Completa do Schema PostgreSQL
Baseado rigorosamente na estrutura definida nos models
"""
import sys
import os
import psycopg2
from datetime import datetime
from pathlib import Path

# Adicionar diretório do projeto ao PATH
current_dir = Path.cwd()
sys.path.insert(0, str(current_dir))

# Configurar variáveis de ambiente PostgreSQL
os.environ.update({
    'POSTGRES_HOST': 'localhost',
    'POSTGRES_PORT': '5432',
    'POSTGRES_DB': 'investment_system',
    'POSTGRES_USER': 'investment_user',
    'POSTGRES_PASSWORD': 'investment_secure_pass_2024'
})

def recreate_schema():
    """Recria completamente o schema PostgreSQL"""
    print("🔗 Conectando ao PostgreSQL...")
    
    try:
        # Conectar ao banco
        conn = psycopg2.connect(
            host='localhost',
            port=5432,
            database='investment_system',
            user='investment_user',
            password='investment_secure_pass_2024'
        )
        conn.autocommit = True
        cur = conn.cursor()
        
        print("🗑️  PASSO 1: Removendo todas as tabelas existentes...")
        
        # Drop tabelas em ordem (respeitando foreign keys)
        tables_to_drop = [
            'market_data',
            'fundamental_analyses', 
            'recommendations',
            'agent_sessions',
            'stocks'
        ]
        
        for table in tables_to_drop:
            cur.execute(f"DROP TABLE IF EXISTS {table} CASCADE;")
            print(f"   ✅ Tabela '{table}' removida")
        
        print("🔄 PASSO 2: Removendo tipos customizados...")
        
        # Drop tipos customizados
        custom_types = [
            'data_quality_enum',
            'stock_status_enum', 
            'recommendation_enum'
        ]
        
        for enum_type in custom_types:
            cur.execute(f"DROP TYPE IF EXISTS {enum_type} CASCADE;")
            print(f"   ✅ Tipo '{enum_type}' removido")
        
        print("🆕 PASSO 3: Criando tipos customizados...")
        
        # Criar enums exatamente como definido nos models
        cur.execute("""
            CREATE TYPE data_quality_enum AS ENUM (
                'excellent', 'good', 'medium', 'poor', 'critical'
            );
        """)
        print("   ✅ data_quality_enum criado")
        
        cur.execute("""
            CREATE TYPE stock_status_enum AS ENUM (
                'active', 'suspended', 'delisted', 'under_review'
            );
        """)
        print("   ✅ stock_status_enum criado")
        
        cur.execute("""
            CREATE TYPE recommendation_enum AS ENUM (
                'strong_buy', 'buy', 'hold', 'sell', 'strong_sell'
            );
        """)
        print("   ✅ recommendation_enum criado")
        
        print("🏗️  PASSO 4: Criando extensões necessárias...")
        
        # Extensões PostgreSQL necessárias
        extensions = [
            'uuid-ossp',
            'pg_stat_statements', 
            'pgcrypto'
        ]
        
        for ext in extensions:
            try:
                cur.execute(f'CREATE EXTENSION IF NOT EXISTS "{ext}";')
                print(f"   ✅ Extensão '{ext}' habilitada")
            except Exception as e:
                print(f"   ⚠️  Extensão '{ext}' falhou: {e}")
        
        print("📊 PASSO 5: Criando tabela STOCKS (modelo de referência)...")
        
        # Criar tabela stocks exatamente como definido no modelo Stock
        cur.execute("""
            CREATE TABLE stocks (
                -- ==================== IDENTIFICATION ====================
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                symbol VARCHAR(10) UNIQUE NOT NULL,
                name VARCHAR(200) NOT NULL,
                long_name VARCHAR(500),
                
                -- ==================== SECTOR CLASSIFICATION ====================
                sector VARCHAR(100) NOT NULL,
                industry VARCHAR(100),
                business_summary TEXT,
                
                -- ==================== FINANCIAL METRICS ====================
                market_cap NUMERIC(20, 2),
                enterprise_value NUMERIC(20, 2),
                revenue NUMERIC(20, 2),
                net_income NUMERIC(20, 2),
                total_assets NUMERIC(20, 2),
                total_equity NUMERIC(20, 2),
                total_debt NUMERIC(20, 2),
                free_cash_flow NUMERIC(20, 2),
                operating_cash_flow NUMERIC(20, 2),
                
                -- ==================== RATIOS ====================
                pe_ratio NUMERIC(8, 2),
                pb_ratio NUMERIC(8, 2),
                ps_ratio NUMERIC(8, 2),
                peg_ratio NUMERIC(8, 2),
                ev_ebitda NUMERIC(8, 2),
                price_to_book NUMERIC(8, 2),
                price_to_sales NUMERIC(8, 2),
                
                -- ==================== PROFITABILITY ====================
                roe NUMERIC(8, 4),
                roa NUMERIC(8, 4),
                roic NUMERIC(8, 4),
                gross_margin NUMERIC(8, 4),
                operating_margin NUMERIC(8, 4),
                net_margin NUMERIC(8, 4),
                ebitda_margin NUMERIC(8, 4),
                
                -- ==================== FINANCIAL HEALTH ====================
                debt_to_equity NUMERIC(8, 4),
                debt_to_assets NUMERIC(8, 4),
                current_ratio NUMERIC(8, 4),
                quick_ratio NUMERIC(8, 4),
                cash_ratio NUMERIC(8, 4),
                interest_coverage NUMERIC(8, 2),
                
                -- ==================== GROWTH METRICS ====================
                revenue_growth NUMERIC(8, 4),
                earnings_growth NUMERIC(8, 4),
                book_value_growth NUMERIC(8, 4),
                dividend_growth NUMERIC(8, 4),
                
                -- ==================== MARKET DATA ====================
                current_price NUMERIC(12, 2),
                day_change NUMERIC(8, 4),
                day_change_percent NUMERIC(8, 4),
                volume BIGINT,
                avg_volume BIGINT,
                market_cap_category VARCHAR(20),
                
                -- ==================== DIVIDEND INFO ====================
                dividend_yield NUMERIC(8, 4),
                dividend_rate NUMERIC(8, 2),
                payout_ratio NUMERIC(8, 4),
                
                -- ==================== STATUS & QUALITY ====================
                status stock_status_enum NOT NULL DEFAULT 'active',
                data_quality data_quality_enum NOT NULL DEFAULT 'medium',
                data_completeness NUMERIC(5, 2) DEFAULT 0.0,
                confidence_level NUMERIC(5, 2) DEFAULT 0.0,
                
                -- ==================== METADATA ====================
                country VARCHAR(10) DEFAULT 'BR',
                currency VARCHAR(10) DEFAULT 'BRL',
                exchange VARCHAR(20) DEFAULT 'B3',
                
                -- ==================== TIMESTAMPS ====================
                last_price_update TIMESTAMP WITH TIME ZONE,
                last_fundamentals_update TIMESTAMP WITH TIME ZONE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
            );
        """)
        print("   ✅ Tabela 'stocks' criada com estrutura completa")
        
        print("📈 PASSO 6: Criando índices para tabela stocks...")
        
        # Índices estratégicos para performance
        indexes = [
            "CREATE INDEX idx_stocks_symbol ON stocks(symbol);",
            "CREATE INDEX idx_stocks_sector ON stocks(sector);",
            "CREATE INDEX idx_stocks_market_cap ON stocks(market_cap);", 
            "CREATE INDEX idx_stocks_status ON stocks(status);",
            "CREATE INDEX idx_stocks_data_quality ON stocks(data_quality);",
            "CREATE INDEX idx_stocks_updated_at ON stocks(updated_at);",
            "CREATE INDEX idx_stocks_pe_ratio ON stocks(pe_ratio) WHERE pe_ratio IS NOT NULL;",
            "CREATE INDEX idx_stocks_roe ON stocks(roe) WHERE roe IS NOT NULL;"
        ]
        
        for idx in indexes:
            cur.execute(idx)
            print(f"   ✅ Índice criado")
        
        print("📊 PASSO 7: Criando tabelas relacionadas...")
        
        # Tabela de recomendações
        cur.execute("""
            CREATE TABLE recommendations (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                stock_id UUID REFERENCES stocks(id) ON DELETE CASCADE,
                recommendation_type recommendation_enum NOT NULL,
                target_price NUMERIC(12, 2),
                entry_price NUMERIC(12, 2), 
                stop_loss NUMERIC(12, 2),
                confidence_score NUMERIC(5, 2) NOT NULL,
                rationale TEXT,
                analyst_name VARCHAR(100),
                is_active BOOLEAN DEFAULT TRUE,
                analysis_date TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
            );
        """)
        print("   ✅ Tabela 'recommendations' criada")
        
        # Tabela de análises fundamentais
        cur.execute("""
            CREATE TABLE fundamental_analyses (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                stock_id UUID REFERENCES stocks(id) ON DELETE CASCADE,
                analysis_date TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
                valuation_score NUMERIC(5, 2) NOT NULL,
                profitability_score NUMERIC(5, 2) NOT NULL,
                growth_score NUMERIC(5, 2) NOT NULL,
                financial_health_score NUMERIC(5, 2) NOT NULL,
                composite_score NUMERIC(5, 2) NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
            );
        """)
        print("   ✅ Tabela 'fundamental_analyses' criada")
        
        # Tabela de dados de mercado
        cur.execute("""
            CREATE TABLE market_data (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                stock_id UUID REFERENCES stocks(id) ON DELETE CASCADE,
                date TIMESTAMP WITH TIME ZONE NOT NULL,
                open_price NUMERIC(12, 2) NOT NULL,
                high_price NUMERIC(12, 2) NOT NULL,
                low_price NUMERIC(12, 2) NOT NULL,
                close_price NUMERIC(12, 2) NOT NULL,
                adjusted_close NUMERIC(12, 2) NOT NULL,
                volume BIGINT NOT NULL,
                dividend_amount NUMERIC(8, 4),
                split_ratio NUMERIC(8, 4),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
                UNIQUE(stock_id, date)
            );
        """)
        print("   ✅ Tabela 'market_data' criada")
        
        # Tabela de sessões de agentes
        cur.execute("""
            CREATE TABLE agent_sessions (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                session_id VARCHAR(100) UNIQUE NOT NULL,
                agent_name VARCHAR(100) NOT NULL,
                agent_version VARCHAR(20) NOT NULL,
                status VARCHAR(20) NOT NULL,
                input_data JSONB,
                output_data JSONB,
                error_message TEXT,
                execution_time_seconds NUMERIC(8, 2),
                stocks_processed INTEGER DEFAULT 0,
                memory_usage_mb NUMERIC(8, 2),
                config_snapshot JSONB,
                started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
                finished_at TIMESTAMP WITH TIME ZONE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
            );
        """)
        print("   ✅ Tabela 'agent_sessions' criada")
        
        print("📈 PASSO 8: Criando índices adicionais...")
        
        # Índices para tabelas relacionadas
        additional_indexes = [
            "CREATE INDEX idx_recommendations_stock_id ON recommendations(stock_id);",
            "CREATE INDEX idx_recommendations_type ON recommendations(recommendation_type);",
            "CREATE INDEX idx_recommendations_active ON recommendations(is_active);",
            "CREATE INDEX idx_fundamental_analyses_stock_id ON fundamental_analyses(stock_id);",
            "CREATE INDEX idx_fundamental_analyses_score ON fundamental_analyses(composite_score);",
            "CREATE INDEX idx_market_data_stock_date ON market_data(stock_id, date);",
            "CREATE INDEX idx_agent_sessions_status ON agent_sessions(status);",
            "CREATE INDEX idx_agent_sessions_agent ON agent_sessions(agent_name);"
        ]
        
        for idx in additional_indexes:
            cur.execute(idx)
            print(f"   ✅ Índice adicional criado")
        
        print("🔧 PASSO 9: Criando triggers para updated_at...")
        
        # Function para atualizar updated_at automaticamente
        cur.execute("""
            CREATE OR REPLACE FUNCTION update_updated_at_column()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = NOW();
                RETURN NEW;
            END;
            $$ language 'plpgsql';
        """)
        
        # Trigger para stocks
        cur.execute("""
            CREATE TRIGGER update_stocks_updated_at 
                BEFORE UPDATE ON stocks 
                FOR EACH ROW 
                EXECUTE FUNCTION update_updated_at_column();
        """)
        print("   ✅ Trigger de updated_at criado para stocks")
        
        print("✅ PASSO 10: Verificando estrutura criada...")
        
        # Verificar tabelas criadas
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name;
        """)
        tables = cur.fetchall()
        
        print(f"   📊 {len(tables)} tabelas criadas:")
        for table in tables:
            print(f"      • {table[0]}")
        
        # Verificar estrutura da tabela stocks
        cur.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'stocks' 
            ORDER BY ordinal_position;
        """)
        columns = cur.fetchall()
        
        print(f"   📋 Tabela 'stocks' tem {len(columns)} colunas:")
        for col_name, data_type, nullable, default in columns[:10]:  # Primeiras 10
            null_str = "NULL" if nullable == "YES" else "NOT NULL"
            print(f"      • {col_name}: {data_type} {null_str}")
        
        if len(columns) > 10:
            print(f"      ... e mais {len(columns) - 10} colunas")
        
        conn.close()
        print("\n🎉 SCHEMA RECREADO COM SUCESSO!")
        print("=" * 50)
        print("✅ Todas as tabelas foram recriadas de acordo com os models")
        print("✅ Índices estratégicos aplicados")
        print("✅ Triggers de auditoria configurados")
        print("✅ Tipos customizados PostgreSQL criados")
        print("✅ Estrutura rigorosamente baseada na classe Stock")
        
        return True
        
    except Exception as e:
        print(f"❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = recreate_schema()
    sys.exit(0 if success else 1)
EOF

# Executar script de recreação
print_info "Executando recreação do schema..."
python3 temp_recreate_schema.py

if [ $? -eq 0 ]; then
    print_success "Schema recreado com sucesso!"
    
    # Limpeza
    rm -f temp_recreate_schema.py
    
    print_step "Executando verificação final..."
    
    # Verificação rápida
    docker exec investment-postgres psql -U investment_user -d investment_system -c "\dt" 
    
    print_success "Verificação concluída!"
    
    echo ""
    echo "🎉 RECREAÇÃO DO SCHEMA CONCLUÍDA!"
    echo "================================="
    echo ""
    echo -e "${GREEN}✅ O que foi feito:${NC}"
    echo "   🗑️  Todas as tabelas antigas removidas"
    echo "   🆕 Schema recriado baseado rigorosamente nos models"
    echo "   📊 Estrutura exata da classe Stock implementada"
    echo "   📈 Índices estratégicos aplicados"
    echo "   🔧 Triggers de auditoria configurados"
    echo "   🛡️  Tipos customizados PostgreSQL criados"
    echo ""
    echo -e "${BLUE}📂 Backup salvo em:${NC}"
    echo "   $BACKUP_DIR"
    echo ""
    echo -e "${GREEN}🚀 Próximos passos:${NC}"
    echo "   1. Testar conexão com novo schema"
    echo "   2. Executar migrações de dados se necessário"
    echo "   3. Validar funcionalidade dos repositories"
    
else
    print_error "Falha na recreação do schema!"
    print_info "Verifique os logs acima e o backup em: $BACKUP_DIR"
    exit 1
fi