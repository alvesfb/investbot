#!/usr/bin/env python3
# =================================================================
# TESTE DO SISTEMA DE SCORING FUNDAMENTALISTA CORRIGIDO
# =================================================================
# Script para testar a implementação corrigida do Passo 2
# Compatible com a arquitetura existente do projeto
# Data: 13/07/2025
# =================================================================

"""
Script de Teste - Sistema de Scoring Fundamentalista

Este script testa a implementação corrigida que:
1. É compatível com StockRepository.get_stock_by_code()
2. Usa mocks quando componentes não estão disponíveis
3. Integra corretamente com a arquitetura existente
4. Fornece fallbacks robustos para desenvolvimento
"""

import sys
import os
from pathlib import Path

# Adicionar path do projeto se necessário
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

def test_imports():
    """Testa imports e disponibilidade de componentes"""
    print("🔍 TESTANDO IMPORTS E COMPONENTES")
    print("=" * 50)
    
    components_status = {}
    
    # 1. Teste Financial Calculator
    try:
        from utils.financial_calculator import FinancialCalculator, FinancialMetrics, FinancialData
        components_status['FinancialCalculator'] = True
        print("✅ FinancialCalculator: Disponível")
    except ImportError as e:
        components_status['FinancialCalculator'] = False
        print(f"❌ FinancialCalculator: Não disponível ({e})")
    
    # 2. Teste Database
    try:
        from database.models import Stock, FundamentalAnalysis
        from database.repositories import get_stock_repository, get_fundamental_repository
        components_status['Database'] = True
        print("✅ Database: Disponível")
    except ImportError as e:
        components_status['Database'] = False
        print(f"❌ Database: Não disponível ({e})")
    
    # 3. Teste Agno
    try:
        from agno.agent import Agent
        components_status['Agno'] = True
        print("✅ Agno Framework: Disponível")
    except ImportError as e:
        components_status['Agno'] = False
        print(f"❌ Agno Framework: Não disponível ({e})")
    
    # 4. Teste NumPy
    try:
        import numpy as np
        components_status['NumPy'] = True
        print("✅ NumPy: Disponível")
    except ImportError as e:
        components_status['NumPy'] = False
        print(f"❌ NumPy: Não disponível ({e})")
    
    return components_status

def test_fundamental_analyzer_import():
    """Testa import do sistema de scoring"""
    print("\n📊 TESTANDO IMPORT DO SISTEMA DE SCORING")
    print("=" * 50)
    
    try:
        # Assumindo que o arquivo foi salvo como fundamental_scoring_system.py
        # Ajustar nome conforme necessário
        sys.path.append('agents/analyzers')
        
        from agents.analyzers.fundamental_scoring_system import (
            FundamentalAnalyzerAgent, 
            ScoringEngine, 
            QualityTier,
            FundamentalScore
        )
        
        print("✅ Imports do sistema de scoring: Sucesso")
        return True
        
    except ImportError as e:
        print(f"❌ Erro no import: {e}")
        print("💡 Dica: Salve o código como 'agents/analyzers/fundamental_scoring_system.py'")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def test_agent_creation():
    """Testa criação do agente"""
    print("\n🤖 TESTANDO CRIAÇÃO DO AGENTE")
    print("=" * 50)
    
    try:
        sys.path.append('agents/analyzers')
        from agents.analyzers.fundamental_scoring_system import FundamentalAnalyzerAgent
        
        # Criar agente
        agent = FundamentalAnalyzerAgent()
        print("✅ Agente criado com sucesso")
        
        # Verificar atributos essenciais
        if hasattr(agent, 'scoring_engine'):
            print("✅ ScoringEngine inicializado")
        else:
            print("❌ ScoringEngine não encontrado")
        
        if hasattr(agent, 'calculator'):
            print("✅ Calculator inicializado")
        else:
            print("❌ Calculator não encontrado")
        
        return agent
        
    except Exception as e:
        print(f"❌ Erro na criação do agente: {e}")
        return None

def test_single_stock_analysis(agent):
    """Testa análise de ação individual"""
    print("\n📈 TESTANDO ANÁLISE DE AÇÃO INDIVIDUAL")
    print("=" * 50)
    
    if not agent:
        print("❌ Agente não disponível")
        return False
    
    try:
        # Testar com PETR4
        print("Analisando PETR4...")
        result = agent.analyze_single_stock("PETR4")
        
        if "error" in result:
            print(f"❌ Erro na análise: {result['error']}")
            return False
        
        # Verificar estrutura do resultado
        required_keys = [
            "stock_code", 
            "analysis_date", 
            "fundamental_score", 
            "recommendation"
        ]
        
        missing_keys = [key for key in required_keys if key not in result]
        if missing_keys:
            print(f"❌ Chaves faltando no resultado: {missing_keys}")
            return False
        
        # Exibir resultado
        fs = result["fundamental_score"]
        print(f"✅ Análise PETR4 concluída:")
        print(f"   • Score: {fs['composite_score']:.1f}/100")
        print(f"   • Qualidade: {fs['quality_tier']}")
        print(f"   • Recomendação: {result['recommendation']}")
        print(f"   • Setor: {result.get('stock_info', {}).get('setor', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na análise individual: {e}")
        return False

def test_top_stocks_analysis(agent):
    """Testa análise de top ações"""
    print("\n🏆 TESTANDO ANÁLISE DE TOP AÇÕES")
    print("=" * 50)
    
    if not agent:
        print("❌ Agente não disponível")
        return False
    
    try:
        print("Buscando top 3 ações...")
        result = agent.get_top_stocks(3)
        
        if "error" in result:
            print(f"❌ Erro na análise: {result['error']}")
            return False
        
        # Verificar resultado
        if "top_stocks" not in result:
            print("❌ 'top_stocks' não encontrado no resultado")
            return False
        
        top_stocks = result["top_stocks"]
        print(f"✅ Top ações encontradas: {len(top_stocks)}")
        
        for i, stock in enumerate(top_stocks, 1):
            fs = stock["fundamental_score"]
            print(f"   {i}. {stock['stock_code']} - Score: {fs['composite_score']:.1f} - {stock['recommendation']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na análise de top ações: {e}")
        return False

def test_sector_analysis(agent):
    """Testa análise setorial"""
    print("\n🏭 TESTANDO ANÁLISE SETORIAL")
    print("=" * 50)
    
    if not agent:
        print("❌ Agente não disponível")
        return False
    
    try:
        print("Analisando setor 'Mock'...")
        result = agent.analyze_sector("Mock")
        
        if "error" in result:
            print(f"❌ Erro na análise: {result['error']}")
            return False
        
        # Verificar resultado
        if "companies_analyzed" not in result:
            print("❌ 'companies_analyzed' não encontrado")
            return False
        
        companies_count = result["companies_analyzed"]
        print(f"✅ Análise setorial concluída:")
        print(f"   • Empresas analisadas: {companies_count}")
        
        if "sector_stats" in result:
            stats = result["sector_stats"]
            if "average_score" in stats:
                print(f"   • Score médio: {stats['average_score']:.1f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na análise setorial: {e}")
        return False

def test_repository_integration():
    """Testa integração com repositórios"""
    print("\n🗄️  TESTANDO INTEGRAÇÃO COM REPOSITÓRIOS")
    print("=" * 50)
    
    try:
        from database.repositories import get_stock_repository
        
        stock_repo = get_stock_repository()
        print("✅ StockRepository criado")
        
        # Testar método get_stock_by_code
        if hasattr(stock_repo, 'get_stock_by_code'):
            print("✅ Método get_stock_by_code disponível")
            
            # Tentar buscar uma ação
            try:
                stock = stock_repo.get_stock_by_code("PETR4")
                if stock:
                    print(f"✅ Ação encontrada: {stock.codigo}")
                else:
                    print("⚠️  Ação PETR4 não encontrada (banco vazio?)")
            except Exception as e:
                print(f"⚠️  Erro ao buscar ação: {e}")
        else:
            print("❌ Método get_stock_by_code NÃO disponível")
        
        # Testar outros métodos
        methods_to_check = [
            'get_all_stocks',
            'get_stocks_by_sector',
            'create_stock'
        ]
        
        for method in methods_to_check:
            if hasattr(stock_repo, method):
                print(f"✅ Método {method}: Disponível")
            else:
                print(f"❌ Método {method}: Não disponível")
        
        return True
        
    except ImportError as e:
        print(f"❌ Repositórios não disponíveis: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro na integração: {e}")
        return False

def run_comprehensive_test():
    """Executa teste abrangente"""
    print("🚀 TESTE ABRANGENTE DO SISTEMA DE SCORING FUNDAMENTALISTA")
    print("=" * 80)
    print("Este teste verifica a compatibilidade com a arquitetura existente")
    print("=" * 80)
    
    test_results = {}
    
    # 1. Teste de imports
    test_results['imports'] = test_imports()
    
    # 2. Teste de import do sistema
    test_results['system_import'] = test_fundamental_analyzer_import()
    
    if not test_results['system_import']:
        print("\n❌ TESTE INTERROMPIDO: Não foi possível importar o sistema")
        return False
    
    # 3. Teste de criação do agente
    agent = test_agent_creation()
    test_results['agent_creation'] = agent is not None
    
    if not agent:
        print("\n❌ TESTE INTERROMPIDO: Não foi possível criar o agente")
        return False
    
    # 4. Testes funcionais
    test_results['single_analysis'] = test_single_stock_analysis(agent)
    test_results['top_stocks'] = test_top_stocks_analysis(agent)
    test_results['sector_analysis'] = test_sector_analysis(agent)
    
    # 5. Teste de integração
    test_results['repository_integration'] = test_repository_integration()
    
    # Resumo dos resultados
    print("\n📋 RESUMO DOS TESTES")
    print("=" * 50)
    
    for test_name, result in test_results.items():
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    # Resultado final
    all_passed = all(test_results.values())
    
    if all_passed:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("\n✅ O sistema de scoring está funcionando corretamente")
        print("✅ Compatível com a arquitetura existente")
        print("✅ Mocks funcionando para desenvolvimento")
        
        print("\n📋 PRÓXIMOS PASSOS:")
        print("1. Salvar o código como 'agents/analyzers/fundamental_scoring_system.py'")
        print("2. Integrar com dados reais do YFinance")
        print("3. Implementar Passo 3: Benchmarking Setorial Avançado")
        
    else:
        failed_tests = [name for name, result in test_results.items() if not result]
        print(f"\n❌ ALGUNS TESTES FALHARAM: {', '.join(failed_tests)}")
        print("\n🔧 AÇÕES CORRETIVAS:")
        
        if not test_results['system_import']:
            print("• Salvar o código do sistema de scoring no local correto")
        if not test_results['repository_integration']:
            print("• Verificar implementação dos repositórios")
        if not test_results['agent_creation']:
            print("• Verificar dependências do agente")
    
    return all_passed

def simple_usage_example():
    """Exemplo simples de uso"""
    print("\n💡 EXEMPLO DE USO SIMPLES")
    print("=" * 50)
    
    try:
        sys.path.append('agents/analyzers')
        from agents.analyzers.fundamental_scoring_system import FundamentalAnalyzerAgent
        
        # Criar e usar agente
        agent = FundamentalAnalyzerAgent()
        
        print("Código de exemplo:")
        print("""
# Importar o agente
from agents.analyzers.fundamental_scoring_system import FundamentalAnalyzerAgent

# Criar agente
agent = FundamentalAnalyzerAgent()

# Analisar uma ação
result = agent.analyze_single_stock('PETR4')
score = result['fundamental_score']['composite_score']
recommendation = result['recommendation']

print(f'PETR4: Score {score:.1f} - {recommendation}')

# Buscar top ações
top_result = agent.get_top_stocks(5)
for stock in top_result['top_stocks']:
    code = stock['stock_code']
    score = stock['fundamental_score']['composite_score']
    rec = stock['recommendation']
    print(f'{code}: {score:.1f} - {rec}')
        """)
        
        # Executar exemplo
        result = agent.analyze_single_stock('PETR4')
        if 'error' not in result:
            fs = result['fundamental_score']
            print(f"\nResultado do exemplo:")
            print(f"PETR4: Score {fs['composite_score']:.1f} - {result['recommendation']}")
        
    except Exception as e:
        print(f"❌ Erro no exemplo: {e}")

if __name__ == "__main__":
    # Executar teste abrangente
    success = run_comprehensive_test()
    
    if success:
        # Mostrar exemplo de uso
        simple_usage_example()
    
    print(f"\n{'='*80}")
    print(f"TESTE CONCLUÍDO: {'✅ SUCESSO' if success else '❌ FALHAS DETECTADAS'}")
    print(f"{'='*80}")
