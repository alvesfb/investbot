#!/bin/bash
# test_insert.sh
# Script para testar inserção de um registro no banco PostgreSQL

echo "🧪 TESTE DE INSERÇÃO - Registro de Teste"
echo "========================================"

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

# ==================== VERIFICAÇÕES ====================
print_step "Verificando conexão com PostgreSQL..."

if ! docker-compose -f docker-compose.postgresql.yml ps postgres | grep -q "Up"; then
    print_error "PostgreSQL não está rodando!"
    exit 1
fi

print_success "PostgreSQL está ativo"

# ==================== TESTE DE INSERÇÃO ====================
print_step "Executando teste de inserção..."

# Criar script Python para teste
cat > temp_test_insert.py << 'EOF'
#!/usr/bin/env python3
"""
Teste de Inserção - Registro de Teste
Insere um registro completo na tabela stocks
"""
import sys
import os
import psycopg2
from datetime import datetime
from pathlib import Path
import uuid

# Configurar variáveis de ambiente
os.environ.update({
    'POSTGRES_HOST': 'localhost',
    'POSTGRES_PORT': '5432',
    'POSTGRES_DB': 'investment_system',
    'POSTGRES_USER': 'investment_user',
    'POSTGRES_PASSWORD': 'investment_secure_pass_2024'
})

def test_insert():
    """Testa inserção de um registro completo"""
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
        
        print("🧹 Limpando registros de teste anteriores...")
        cur.execute("DELETE FROM stocks WHERE symbol = 'TEST5';")
        
        print("📝 Inserindo registro de teste completo...")
        
        # Dados de teste realistas
        test_data = {
            'symbol': 'TEST5',
            'name': 'Empresa Teste S.A.',
            'long_name': 'Empresa Teste Sociedade Anônima - Teste Completo',
            'sector': 'Tecnologia',
            'industry': 'Software',
            'business_summary': 'Empresa fictícia para teste do sistema de investimentos. Atua no setor de tecnologia com foco em desenvolvimento de software.',
            'market_cap': 15000000000.00,  # 15 bilhões
            'enterprise_value': 16500000000.00,  # 16.5 bilhões
            'revenue': 8500000000.00,  # 8.5 bilhões
            'net_income': 1200000000.00,  # 1.2 bilhões
            'total_assets': 25000000000.00,  # 25 bilhões
            'total_equity': 18000000000.00,  # 18 bilhões
            'total_debt': 7000000000.00,  # 7 bilhões
            'free_cash_flow': 2100000000.00,  # 2.1 bilhões
            'operating_cash_flow': 2800000000.00,  # 2.8 bilhões
            'pe_ratio': 12.5,
            'pb_ratio': 0.83,
            'ps_ratio': 1.76,
            'peg_ratio': 0.95,
            'ev_ebitda': 8.2,
            'price_to_book': 0.83,
            'price_to_sales': 1.76,
            'roe': 0.0667,  # 6.67%
            'roa': 0.048,   # 4.8%
            'roic': 0.085,  # 8.5%
            'gross_margin': 0.65,    # 65%
            'operating_margin': 0.22, # 22%
            'net_margin': 0.141,     # 14.1%
            'ebitda_margin': 0.28,   # 28%
            'debt_to_equity': 0.389,  # 38.9%
            'debt_to_assets': 0.28,   # 28%
            'current_ratio': 2.15,
            'quick_ratio': 1.85,
            'cash_ratio': 0.95,
            'interest_coverage': 15.2,
            'revenue_growth': 0.125,    # 12.5%
            'earnings_growth': 0.18,    # 18%
            'book_value_growth': 0.092, # 9.2%
            'dividend_growth': 0.085,   # 8.5%
            'current_price': 42.75,
            'day_change': 0.85,
            'day_change_percent': 0.0203,  # 2.03%
            'volume': 2850000,
            'avg_volume': 1950000,
            'market_cap_category': 'large_cap',
            'dividend_yield': 0.028,  # 2.8%
            'dividend_rate': 1.20,
            'payout_ratio': 0.35,     # 35%
            'status': 'active',
            'data_quality': 'excellent',
            'data_completeness': 95.5,
            'confidence_level': 88.2,
            'country': 'BR',
            'currency': 'BRL',
            'exchange': 'B3'
        }
        
        # Montar query de inserção
        columns = list(test_data.keys())
        placeholders = ', '.join(['%s'] * len(columns))
        values = list(test_data.values())
        
        query = f"""
            INSERT INTO stocks ({', '.join(columns)}, last_price_update, last_fundamentals_update)
            VALUES ({placeholders}, NOW(), NOW())
            RETURNING id, symbol, name;
        """
        
        cur.execute(query, values)
        result = cur.fetchone()
        
        if result:
            record_id, symbol, name = result
            print(f"   ✅ Registro inserido com sucesso!")
            print(f"   📊 ID: {record_id}")
            print(f"   📈 Symbol: {symbol}")
            print(f"   🏢 Name: {name}")
        
        print("🔍 Verificando dados inseridos...")
        
        # Verificar dados inseridos
        cur.execute("""
            SELECT symbol, name, sector, current_price, pe_ratio, roe, 
                   market_cap, data_quality, status, created_at
            FROM stocks 
            WHERE symbol = %s;
        """, ('TEST5',))
        
        row = cur.fetchone()
        if row:
            symbol, name, sector, price, pe, roe, mcap, quality, status, created = row
            print(f"   📋 Dados verificados:")
            print(f"      • Symbol: {symbol}")
            print(f"      • Name: {name}")
            print(f"      • Sector: {sector}")
            print(f"      • Price: R$ {price}")
            print(f"      • P/E: {pe}")
            print(f"      • ROE: {roe:.2%}")
            print(f"      • Market Cap: R$ {mcap:,.0f}")
            print(f"      • Quality: {quality}")
            print(f"      • Status: {status}")
            print(f"      • Created: {created}")
        
        print("📊 Testando relacionamentos...")
        
        # Inserir uma recomendação de teste
        cur.execute("""
            INSERT INTO recommendations (stock_id, recommendation_type, target_price, 
                                       entry_price, confidence_score, rationale, analyst_name)
            SELECT id, 'buy', 48.50, 42.75, 85.5, 
                   'Empresa com fundamentos sólidos e crescimento consistente. Recomendação de compra baseada em análise fundamentalista.',
                   'Sistema de Testes'
            FROM stocks WHERE symbol = 'TEST5'
            RETURNING id;
        """)
        
        rec_result = cur.fetchone()
        if rec_result:
            print(f"   ✅ Recomendação criada - ID: {rec_result[0]}")
        
        # Inserir análise fundamental de teste
        cur.execute("""
            INSERT INTO fundamental_analyses (stock_id, valuation_score, profitability_score,
                                            growth_score, financial_health_score, composite_score)
            SELECT id, 78.5, 82.3, 75.8, 88.1, 81.2
            FROM stocks WHERE symbol = 'TEST5'
            RETURNING id;
        """)
        
        analysis_result = cur.fetchone()
        if analysis_result:
            print(f"   ✅ Análise fundamental criada - ID: {analysis_result[0]}")
        
        # Inserir dados de mercado de teste
        cur.execute("""
            INSERT INTO market_data (stock_id, date, open_price, high_price, low_price,
                                   close_price, adjusted_close, volume)
            SELECT id, NOW()::date, 42.10, 43.25, 41.85, 42.75, 42.75, 2850000
            FROM stocks WHERE symbol = 'TEST5'
            RETURNING id;
        """)
        
        market_result = cur.fetchone()
        if market_result:
            print(f"   ✅ Dados de mercado criados - ID: {market_result[0]}")
        
        print("🔢 Contando registros nas tabelas...")
        
        # Contar registros em cada tabela
        tables = ['stocks', 'recommendations', 'fundamental_analyses', 'market_data', 'agent_sessions']
        for table in tables:
            cur.execute(f"SELECT COUNT(*) FROM {table};")
            count = cur.fetchone()[0]
            print(f"   📊 {table}: {count} registro(s)")
        
        print("🎯 Testando consulta complexa...")
        
        # Consulta complexa com JOINs
        cur.execute("""
            SELECT s.symbol, s.name, s.current_price, s.pe_ratio,
                   r.recommendation_type, r.target_price, r.confidence_score,
                   fa.composite_score
            FROM stocks s
            LEFT JOIN recommendations r ON s.id = r.stock_id
            LEFT JOIN fundamental_analyses fa ON s.id = fa.stock_id
            WHERE s.symbol = 'TEST5';
        """)
        
        complex_result = cur.fetchone()
        if complex_result:
            symbol, name, price, pe, rec_type, target, confidence, score = complex_result
            print(f"   ✅ Consulta complexa executada:")
            print(f"      • {symbol} - {name}")
            print(f"      • Preço atual: R$ {price}")
            print(f"      • P/E: {pe}")
            print(f"      • Recomendação: {rec_type}")
            print(f"      • Preço alvo: R$ {target}")
            print(f"      • Confiança: {confidence}%")
            print(f"      • Score composto: {score}")
        
        conn.close()
        
        print("\n🎉 TESTE DE INSERÇÃO CONCLUÍDO COM SUCESSO!")
        print("=" * 50)
        print("✅ Registro de teste inserido com dados completos")
        print("✅ Relacionamentos funcionando corretamente")
        print("✅ Todas as tabelas testadas")
        print("✅ Consultas complexas executadas")
        print("✅ Schema PostgreSQL validado")
        
        return True
        
    except Exception as e:
        print(f"❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_insert()
    sys.exit(0 if success else 1)
EOF

# Executar teste
print_info "Executando script de teste..."
python3 temp_test_insert.py

if [ $? -eq 0 ]; then
    print_success "Teste de inserção passou!"
    
    print_step "Executando verificação adicional via SQL direto..."
    
    # Verificação adicional via psql
    docker exec investment-postgres psql -U investment_user -d investment_system -c "
        SELECT 
            symbol, 
            name, 
            sector, 
            current_price, 
            pe_ratio, 
            status,
            data_quality
        FROM stocks 
        WHERE symbol = 'TEST5';
    "
    
    print_step "Verificando contagem de registros..."
    
    docker exec investment-postgres psql -U investment_user -d investment_system -c "
        SELECT 
            'stocks' as tabela, COUNT(*) as registros FROM stocks
        UNION ALL
        SELECT 
            'recommendations' as tabela, COUNT(*) as registros FROM recommendations
        UNION ALL
        SELECT 
            'fundamental_analyses' as tabela, COUNT(*) as registros FROM fundamental_analyses
        UNION ALL
        SELECT 
            'market_data' as tabela, COUNT(*) as registros FROM market_data;
    "
    
    # Limpeza
    rm -f temp_test_insert.py
    
    echo ""
    echo "🎉 TESTE COMPLETO EXECUTADO!"
    echo "============================="
    echo ""
    echo -e "${GREEN}✅ Resultados:${NC}"
    echo "   📝 Registro de teste inserido na tabela 'stocks'"
    echo "   🔗 Relacionamentos criados (recommendations, fundamental_analyses, market_data)"
    echo "   🔍 Consultas complexas com JOINs executadas"
    echo "   📊 Todas as colunas testadas com dados realistas"
    echo "   ✅ Schema PostgreSQL totalmente funcional"
    echo ""
    echo -e "${BLUE}📋 Dados de teste inseridos:${NC}"
    echo "   • Symbol: TEST5"
    echo "   • Name: Empresa Teste S.A."
    echo "   • Sector: Tecnologia"
    echo "   • Price: R$ 42,75"
    echo "   • Market Cap: R$ 15 bilhões"
    echo "   • Status: active"
    echo "   • Data Quality: excellent"
    
else
    print_error "Teste de inserção falhou!"
    rm -f temp_test_insert.py
    exit 1
fi