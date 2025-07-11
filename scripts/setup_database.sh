#!/bin/bash
# scripts/setup_database.sh

echo "🚀 Configurando banco de dados - Passo 2 da Fase 1"

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

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Verificar se estamos no ambiente virtual
if [[ "$VIRTUAL_ENV" == "" ]]; then
    print_error "Ambiente virtual não ativado!"
    echo "Execute: source venv/bin/activate"
    exit 1
fi

print_step "Verificando configurações..."

# Testar se as configurações estão OK
python -c "
try:
    from config.settings import settings
    print(f'✅ Configurações OK - Database: {settings.database_url}')
except Exception as e:
    print(f'❌ Erro nas configurações: {e}')
    exit(1)
" || exit 1


print_step "Testando imports dos módulos..."

# Testar se os imports funcionam
python -c "
try:
    from database.models import Stock, Recommendation, FundamentalAnalysis
    print('✅ Models importados com sucesso')
    
    from database.connection import engine, get_db_session, check_database_connection
    print('✅ Connection importado com sucesso')
    
    from database.repositories import get_stock_repository, get_recommendation_repository
    print('✅ Repositories importados com sucesso')
    
    print('✅ Todos os módulos do banco OK!')
    
except Exception as e:
    print(f'❌ Erro nos imports: {e}')
    exit(1)
" || exit 1

print_step "Inicializando banco de dados..."

# Executar inicialização do banco
python -c "
try:
    from database.init_db import main
    success = main()
    if not success:
        exit(1)
except Exception as e:
    print(f'❌ Erro na inicialização: {e}')
    exit(1)
" || exit 1

print_step "Testando operações básicas do banco..."

# Testar operações básicas
python -c "
try:
    from database.repositories import get_stock_repository, get_recommendation_repository
    from database.connection import check_database_connection
    
    # Testar conexão
    if not check_database_connection():
        print('❌ Falha na conexão')
        exit(1)
    print('✅ Conexão com banco OK')
    
    # Testar repository de ações
    stock_repo = get_stock_repository()
    stocks = stock_repo.get_all_stocks()
    print(f'✅ Encontradas {len(stocks)} ações no banco')
    
    if len(stocks) > 0:
        # Testar busca por código
        petr4 = stock_repo.get_stock_by_code('PETR4')
        if petr4:
            print(f'✅ Ação PETR4 encontrada: {petr4.nome}')
        
        # Testar filtros
        filtered_stocks = stock_repo.get_stocks_for_analysis(
            min_market_cap=50000000000,  # 50B
            exclude_penny_stocks=True
        )
        print(f'✅ {len(filtered_stocks)} ações passaram nos filtros de análise')
    
    # Testar repository de recomendações
    rec_repo = get_recommendation_repository()
    recommendations = rec_repo.get_latest_recommendations(limit=5)
    print(f'✅ {len(recommendations)} recomendações encontradas')
    
    print('✅ Todas as operações básicas funcionando!')
    
except Exception as e:
    print(f'❌ Erro nos testes: {e}')
    import traceback
    traceback.print_exc()
    exit(1)
" || exit 1

print_step "Verificando informações do banco..."

# Mostrar informações do banco
python -c "
from database.connection import get_database_info
from database.repositories import get_stock_repository

try:
    db_info = get_database_info()
    stock_repo = get_stock_repository()
    stocks = stock_repo.get_all_stocks()
    
    print('=' * 50)
    print('📊 INFORMAÇÕES DO BANCO DE DADOS')
    print('=' * 50)
    print(f'Tipo: {db_info.get(\"type\", \"Unknown\")}')
    print(f'Arquivo: {db_info.get(\"file_path\", \"N/A\")}')
    print(f'Tamanho: {db_info.get(\"file_size_mb\", 0)} MB')
    print(f'Tabelas: {len(db_info.get(\"tables\", []))}')
    if db_info.get('tables'):
        print(f'Lista: {\", \".join(db_info[\"tables\"])}')
    print(f'Ações cadastradas: {len(stocks)}')
    print('=' * 50)
    
    if len(stocks) > 0:
        print('🏢 AÇÕES CADASTRADAS:')
        for stock in stocks[:5]:  # Mostrar apenas as primeiras 5
            print(f'  {stock.codigo} - {stock.nome} (Setor: {stock.setor})')
        if len(stocks) > 5:
            print(f'  ... e mais {len(stocks) - 5} ações')
        print('=' * 50)
    
except Exception as e:
    print(f'❌ Erro ao obter informações: {e}')
"

echo ""
echo -e "${GREEN}🎉 Banco de dados configurado com sucesso!${NC}"
echo ""
echo -e "${YELLOW}📋 O que foi criado:${NC}"
echo "   ✅ Modelos SQLAlchemy (database/models.py)"
echo "   ✅ Configuração de conexão (database/connection.py)" 
echo "   ✅ Repositories para acesso aos dados (database/repositories.py)"
echo "   ✅ Script de inicialização (database/init_db.py)"
echo "   ✅ Banco SQLite inicializado com dados de exemplo"
echo "   ✅ 8+ ações brasileiras cadastradas (PETR4, VALE3, ITUB4, etc.)"
echo ""
echo -e "${BLUE}📂 Localização do banco:${NC}"
echo "   data/investment_system.db"
echo ""
echo -e "${BLUE}🚀 Próximos passos:${NC}"
echo "   1. Implementar o Agente Coletor (Passo 3 da Fase 1)"
echo "   2. Testar coleta de dados via YFinance"
echo "   3. Atualizar preços das ações no banco"
echo ""
echo -e "${GREEN}✅ Passo 2 da Fase 1 CONCLUÍDO!${NC}"
