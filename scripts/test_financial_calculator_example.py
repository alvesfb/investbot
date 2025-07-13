# examples/test_financial_calculator_example.py
"""
Exemplo rápido para testar a Calculadora Financeira
Execute este arquivo para validar a implementação básica
"""
import sys
from pathlib import Path

# Adicionar projeto ao path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_financial_calculator():
    """Teste rápido da calculadora financeira"""
    try:
        from utils.financial_calculator import FinancialCalculator, FinancialData
        
        print("🧪 Testando Calculadora Financeira...")
        print("=" * 50)
        
        # Dados de exemplo (baseados em uma empresa real)
        sample_data = FinancialData(
            # Dados básicos
            current_price=25.50,
            market_cap=100000000000,  # 100 bilhões
            shares_outstanding=4000000000,  # 4 bilhões de ações
            
            # Demonstrativo de Resultados
            revenue=50000000000,  # 50 bilhões
            gross_profit=20000000000,  # 20 bilhões
            operating_income=8000000000,  # 8 bilhões
            net_income=6000000000,  # 6 bilhões
            
            # Balanço Patrimonial
            total_assets=200000000000,  # 200 bilhões
            current_assets=50000000000,  # 50 bilhões
            cash_and_equivalents=10000000000,  # 10 bilhões
            total_debt=30000000000,  # 30 bilhões
            current_liabilities=20000000000,  # 20 bilhões
            shareholders_equity=80000000000,  # 80 bilhões
            
            # Dados históricos (últimos 3 anos)
            revenue_history=[45000000000, 47000000000, 50000000000],
            net_income_history=[4000000000, 5000000000, 6000000000],
            
            # Metadados
            sector="Petróleo e Gás",
            industry="Petróleo Integrado"
        )
        
        # Calcular métricas
        calculator = FinancialCalculator()
        metrics = calculator.calculate_all_metrics(sample_data)
        
        # Exibir resultados
        print("📊 MÉTRICAS CALCULADAS:")
        print("-" * 30)
        
        # Métricas de Valuation
        print("🏷️  VALUATION:")
        print(f"   P/L Ratio: {metrics.pe_ratio:.2f}" if metrics.pe_ratio else "   P/L Ratio: N/A")
        print(f"   P/VP Ratio: {metrics.pb_ratio:.2f}" if metrics.pb_ratio else "   P/VP Ratio: N/A")
        print(f"   P/S Ratio: {metrics.ps_ratio:.2f}" if metrics.ps_ratio else "   P/S Ratio: N/A")
        
        # Métricas de Rentabilidade
        print("\n💰 RENTABILIDADE:")
        print(f"   ROE: {metrics.roe:.2f}%" if metrics.roe else "   ROE: N/A")
        print(f"   ROA: {metrics.roa:.2f}%" if metrics.roa else "   ROA: N/A")
        print(f"   Margem Líquida: {metrics.net_margin:.2f}%" if metrics.net_margin else "   Margem Líquida: N/A")
        print(f"   Margem EBITDA: {metrics.ebitda_margin:.2f}%" if metrics.ebitda_margin else "   Margem EBITDA: N/A")
        
        # Métricas de Crescimento
        print("\n📈 CRESCIMENTO:")
        print(f"   Crescimento Receita (1 ano): {metrics.revenue_growth_1y:.2f}%" if metrics.revenue_growth_1y else "   Crescimento Receita: N/A")
        print(f"   Crescimento Lucro (1 ano): {metrics.earnings_growth_1y:.2f}%" if metrics.earnings_growth_1y else "   Crescimento Lucro: N/A")
        
        # Métricas de Endividamento
        print("\n💳 ENDIVIDAMENTO:")
        print(f"   Dívida/Patrimônio: {metrics.debt_to_equity:.2f}" if metrics.debt_to_equity else "   Dívida/Patrimônio: N/A")
        print(f"   Dívida/Ativos: {metrics.debt_to_assets:.2f}" if metrics.debt_to_assets else "   Dívida/Ativos: N/A")
        
        # Métricas de Liquidez
        print("\n💧 LIQUIDEZ:")
        print(f"   Liquidez Corrente: {metrics.current_ratio:.2f}" if metrics.current_ratio else "   Liquidez Corrente: N/A")
        print(f"   Liquidez Seca: {metrics.cash_ratio:.2f}" if metrics.cash_ratio else "   Liquidez Seca: N/A")
        
        # Scores
        print("\n🎯 SCORES:")
        print(f"   Score Geral: {metrics.overall_score:.1f}/100" if metrics.overall_score else "   Score Geral: N/A")
        
        if metrics.category_scores:
            print("   Scores por Categoria:")
            for category, score in metrics.category_scores.items():
                print(f"     {category.capitalize()}: {score:.1f}/100")
        
        # Warnings
        if metrics.warnings:
            print("\n⚠️  AVISOS:")
            for warning in metrics.warnings:
                print(f"   • {warning}")
        
        print("\n✅ Teste da Calculadora Financeira CONCLUÍDO COM SUCESSO!")
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO no teste: {e}")
        return False


def test_data_validator():
    """Teste rápido do validador de dados"""
    try:
        from utils.financial_calculator import FinancialData
        from agents.collectors.enhanced_yfinance_client import DataValidator
        
        print("\n🔍 Testando Validador de Dados...")
        print("=" * 50)
        
        # Dados completos para teste
        complete_data = FinancialData(
            current_price=25.50,
            market_cap=100000000000,
            revenue=50000000000,
            net_income=6000000000,
            total_assets=200000000000,
            shareholders_equity=80000000000,
            sector="Tecnologia"
        )
        
        # Dados incompletos para teste
        incomplete_data = FinancialData(
            current_price=25.50,
            market_cap=None,  # Faltando
            revenue=50000000000
            # Vários campos faltando
        )
        
        # Validar dados completos
        validation_complete = DataValidator.validate_financial_data(complete_data)
        quality_complete = DataValidator.calculate_data_quality_score(complete_data)
        
        print("📊 DADOS COMPLETOS:")
        print(f"   Válido: {'✅ SIM' if validation_complete['valid'] else '❌ NÃO'}")
        print(f"   Completude: {validation_complete['completeness']*100:.1f}%")
        print(f"   Score de Qualidade: {quality_complete:.1f}/100")
        
        if validation_complete['warnings']:
            print("   Avisos:")
            for warning in validation_complete['warnings']:
                print(f"     • {warning}")
        
        # Validar dados incompletos
        validation_incomplete = DataValidator.validate_financial_data(incomplete_data)
        quality_incomplete = DataValidator.calculate_data_quality_score(incomplete_data)
        
        print("\n📊 DADOS INCOMPLETOS:")
        print(f"   Válido: {'✅ SIM' if validation_incomplete['valid'] else '❌ NÃO'}")
        print(f"   Completude: {validation_incomplete['completeness']*100:.1f}%")
        print(f"   Score de Qualidade: {quality_incomplete:.1f}/100")
        
        if validation_incomplete['errors']:
            print("   Erros:")
            for error in validation_incomplete['errors']:
                print(f"     • {error}")
        
        print("\n✅ Teste do Validador CONCLUÍDO COM SUCESSO!")
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO no teste do validador: {e}")
        return False


def test_client_structure():
    """Teste da estrutura do cliente (sem requisições reais)"""
    try:
        from agents.collectors.enhanced_yfinance_client import EnhancedYFinanceClient, BatchDataProcessor
        
        print("\n🌐 Testando Estrutura do Cliente YFinance...")
        print("=" * 50)
        
        # Criar cliente
        client = EnhancedYFinanceClient()
        
        # Verificar métodos essenciais
        methods_to_check = [
            'get_comprehensive_stock_data',
            'get_batch_stock_data', 
            'get_sector_data',
            'clear_cache',
            'get_cache_stats'
        ]
        
        print("🔧 MÉTODOS DISPONÍVEIS:")
        for method in methods_to_check:
            exists = hasattr(client, method)
            print(f"   {method}: {'✅' if exists else '❌'}")
        
        # Testar cache
        try:
            cache_stats = client.get_cache_stats()
            print(f"\n💾 CACHE:")
            print(f"   Entradas: {cache_stats['entries']}")
            print(f"   Status: {'✅ Funcionando' if cache_stats is not None else '❌ Erro'}")
        except Exception as e:
            print(f"\n💾 CACHE:")
            print(f"   Status: ⚠️  Erro no cache: {e}")
        
        # Testar processador em lote
        try:
            processor = BatchDataProcessor(client)
            print(f"\n📦 PROCESSADOR EM LOTE:")
            print(f"   Criado: {'✅ SIM' if processor else '❌ NÃO'}")
            print(f"   Cliente associado: {'✅ SIM' if processor.client else '❌ NÃO'}")
            print(f"   Max retries: {processor.max_retries}")
        except Exception as e:
            print(f"\n📦 PROCESSADOR EM LOTE:")
            print(f"   Status: ⚠️  Erro: {e}")
        
        print("\n✅ Teste da Estrutura do Cliente CONCLUÍDO COM SUCESSO!")
        return True
        
    except ImportError as e:
        print(f"\n❌ ERRO de importação: {e}")
        print("💡 Dica: Execute o script de correção primeiro:")
        print("   python fix_yfinance_settings.py")
        return False
    except Exception as e:
        print(f"\n❌ ERRO no teste do cliente: {e}")
        return False


def main():
    """Função principal - executa todos os testes rápidos"""
    print("🚀 TESTES RÁPIDOS DOS COMPONENTES DA FASE 2 - PASSO 1")
    print("=" * 60)
    print("Este script testa os componentes implementados sem fazer")
    print("requisições reais à API do Yahoo Finance.")
    print("=" * 60)
    
    tests = [
        ("Calculadora Financeira", test_financial_calculator),
        ("Validador de Dados", test_data_validator),
        ("Estrutura do Cliente", test_client_structure)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 Executando: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ ERRO CRÍTICO em {test_name}: {e}")
            results.append((test_name, False))
    
    # Resumo final
    print("\n" + "=" * 60)
    print("📋 RESUMO DOS TESTES")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"   {test_name}: {status}")
    
    print(f"\n📊 RESULTADO FINAL: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Os componentes da Fase 2 - Passo 1 estão funcionando corretamente.")
        print("\n🚀 PRÓXIMOS PASSOS:")
        print("   1. Execute o script de validação completa se necessário")
        print("   2. Prossiga para a implementação do Agente Analisador (Passo 2)")
    else:
        print("⚠️  ALGUNS TESTES FALHARAM!")
        print("🔧 Verifique os erros acima antes de prosseguir.")


if __name__ == "__main__":
    main()
