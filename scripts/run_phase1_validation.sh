#!/bin/bash
# scripts/run_phase1_validation.sh
# Script principal para executar a validação completa da Fase 1

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Funções auxiliares
print_header() {
    echo -e "\n${BLUE}============================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}============================================================${NC}"
}

print_step() {
    echo -e "\n${CYAN}📋 $1${NC}"
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
    echo -e "${WHITE}ℹ️  $1${NC}"
}

# Verificar se estamos no ambiente virtual
check_virtual_env() {
    if [[ "$VIRTUAL_ENV" == "" ]]; then
        print_error "Ambiente virtual não ativado!"
        echo -e "${YELLOW}Execute: source venv/bin/activate${NC}"
        exit 1
    fi
    print_success "Ambiente virtual ativo: $VIRTUAL_ENV"
}

# Verificar dependências
check_dependencies() {
    print_step "Verificando dependências..."
    
    # Python version
    python_version=$(python --version 2>&1)
    echo "   Python: $python_version"
    
    # Dependências críticas
    local deps=("agno" "fastapi" "sqlalchemy" "pydantic" "yfinance" "pytest")
    local missing=()
    
    for dep in "${deps[@]}"; do
        if python -c "import $dep" 2>/dev/null; then
            echo -e "   ${GREEN}✓${NC} $dep"
        else
            echo -e "   ${RED}✗${NC} $dep"
            missing+=("$dep")
        fi
    done
    
    if [ ${#missing[@]} -ne 0 ]; then
        print_error "Dependências faltando: ${missing[*]}"
        print_info "Execute: pip install -r requirements.txt"
        exit 1
    fi
    
    print_success "Todas as dependências OK"
}

# Verificar estrutura do projeto
check_project_structure() {
    print_step "Verificando estrutura do projeto..."
    
    local dirs=("agents" "database" "config" "api" "data" "logs" "tests")
    local missing=()
    
    for dir in "${dirs[@]}"; do
        if [ -d "$dir" ]; then
            echo -e "   ${GREEN}✓${NC} $dir/"
        else
            echo -e "   ${RED}✗${NC} $dir/"
            missing+=("$dir")
        fi
    done
    
    if [ ${#missing[@]} -ne 0 ]; then
        print_warning "Diretórios faltando: ${missing[*]}"
        print_info "Criando diretórios faltando..."
        for dir in "${missing[@]}"; do
            mkdir -p "$dir"
            echo -e "   ${GREEN}✓${NC} Criado: $dir/"
        done
    fi
    
    print_success "Estrutura do projeto OK"
}

# Verificar arquivo .env
check_env_file() {
    print_step "Verificando arquivo .env..."
    
    if [ ! -f ".env" ]; then
        print_warning "Arquivo .env não encontrado"
        print_info "Criando .env básico..."
        
        cat > .env << 'EOF'
# Configurações básicas
ENVIRONMENT=development
DEBUG=true

# Claude API (CONFIGURAR!)
ANTHROPIC_API_KEY=your_claude_api_key_here

# Database
DATABASE_URL=sqlite:///./data/investment_system.db

# API
API_HOST=0.0.0.0
API_PORT=8000

# YFinance
YFINANCE_TIMEOUT=30

# Logging
LOG_LEVEL=INFO
EOF
        
        print_warning "Arquivo .env criado - CONFIGURE sua chave da API do Claude!"
    else
        print_success "Arquivo .env encontrado"
    fi
    
    # Verificar configurações críticas
    if grep -q "your_claude_api_key_here" .env; then
        print_warning "Chave da API do Claude não configurada"
        print_info "Edite o arquivo .env e configure ANTHROPIC_API_KEY"
    fi
}

# Executar validação rápida
run_quick_validation() {
    print_step "Executando validação rápida..."
    
    if python scripts/validate_phase1.py --mode quick; then
        print_success "Validação rápida passou"
        return 0
    else
        print_error "Validação rápida falhou"
        return 1
    fi
}

# Executar testes unitários
run_unit_tests() {
    print_step "Executando testes unitários..."
    
    if python -m pytest tests/test_phase1.py -v --tb=short; then
        print_success "Testes unitários passaram"
        return 0
    else
        print_error "Testes unitários falharam"
        return 1
    fi
}

# Executar validação completa
run_complete_validation() {
    print_step "Executando validação completa..."
    
    if python scripts/validate_phase1.py --mode full --save-report; then
        print_success "Validação completa passou"
        return 0
    else
        print_error "Validação completa falhou"
        return 1
    fi
}

# Executar teste do coletor
run_collector_test() {
    print_step "Executando teste do agente coletor..."
    
    if python scripts/validate_phase1.py --mode collector; then
        print_success "Teste do coletor passou"
        return 0
    else
        print_error "Teste do coletor falhou"
        return 1
    fi
}

# Executar teste completo da Fase 1
run_phase1_complete_test() {
    print_step "Executando teste completo da Fase 1..."
    
    if python scripts/phase1_complete_test.py; then
        print_success "Teste completo da Fase 1 passou"
        return 0
    else
        print_error "Teste completo da Fase 1 falhou"
        return 1
    fi
}

# Função principal
main() {
    local test_type="${1:-complete}"
    
    print_header "VALIDAÇÃO DA FASE 1 - SISTEMA DE RECOMENDAÇÕES"
    print_info "Sistema de Recomendações de Investimentos"
    print_info "Iniciado em: $(date '+%d/%m/%Y %H:%M:%S')"
    
    # Verificações preliminares
    check_virtual_env
    check_dependencies
    check_project_structure
    check_env_file
    
    local exit_code=0
    
    case "$test_type" in
        "quick")
            print_header "VALIDAÇÃO RÁPIDA"
            run_quick_validation || exit_code=1
            ;;
        "unit")
            print_header "TESTES UNITÁRIOS"
            run_unit_tests || exit_code=1
            ;;
        "collector")
            print_header "TESTE DO COLETOR"
            run_collector_test || exit_code=1
            ;;
        "complete")
            print_header "VALIDAÇÃO COMPLETA"
            run_complete_validation || exit_code=1
            ;;
        "full")
            print_header "TESTE COMPLETO DA FASE 1"
            run_phase1_complete_test || exit_code=1
            ;;
        "all")
            print_header "TODOS OS TESTES"
            echo -e "${YELLOW}Executando sequência completa de testes...${NC}"
            
            run_quick_validation || exit_code=1
            run_unit_tests || exit_code=1
            run_collector_test || exit_code=1
            run_complete_validation || exit_code=1
            ;;
        *)
            echo "Uso: $0 [quick|unit|collector|complete|full|all]"
            echo ""
            echo "Tipos de teste:"
            echo "  quick     - Validação rápida (essencial)"
            echo "  unit      - Testes unitários"
            echo "  collector - Teste específico do agente coletor"
            echo "  complete  - Validação estrutural completa"
            echo "  full      - Teste completo da Fase 1 (recomendado)"
            echo "  all       - Todos os testes em sequência"
            echo ""
            echo "Padrão: complete"
            exit 1
            ;;
    esac
    
    # Resumo final
    print_header "RESUMO DA VALIDAÇÃO"
    
    if [ $exit_code -eq 0 ]; then
        print_success "🎉 VALIDAÇÃO CONCLUÍDA COM SUCESSO!"
        print_info "✅ Fase 1 está funcionando corretamente"
        print_info "🚀 Sistema pronto para a Fase 2"
        echo ""
        print_info "Próximos passos:"
        echo "   1. ✅ Fase 1 completa"
        echo "   2. 🚀 Implementar Fase 2: Agente Analisador Fundamentalista"
        echo "   3. 📊 Adicionar cálculo de métricas financeiras"
        echo "   4. 🎯 Implementar sistema de scoring"
        echo "   5. 🔄 Configurar pipeline automático"
    else
        print_error "💥 VALIDAÇÃO FALHOU!"
        print_info "❌ Problemas detectados na Fase 1"
        print_info "🔧 Corrija os problemas antes de prosseguir"
        echo ""
        print_info "Ações recomendadas:"
        echo "   1. 📋 Verificar logs de erro detalhados"
        echo "   2. 🔧 Corrigir problemas identificados"
        echo "   3. 🧪 Executar validação novamente"
        echo "   4. 📚 Consultar documentação se necessário"
    fi
    
    echo ""
    print_info "Para mais detalhes, consulte os arquivos de log em: logs/"
    print_info "Relatórios salvos na raiz do projeto"
    
    exit $exit_code
}

# Executar função principal com argumentos
main "$@"
