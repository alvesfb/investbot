# analyze_required_fields.py
"""
Análise detalhada dos campos obrigatórios e sua influência no teste
"""
import sys
from pathlib import Path
from datetime import datetime

# Adicionar projeto ao path
project_root = Path.cwd()
sys.path.insert(0, str(project_root))

def analyze_required_fields_impact():
    """Analisa o impacto dos campos obrigatórios ausentes"""
    print("🔍 ANÁLISE DETALHADA DOS CAMPOS OBRIGATÓRIOS")
    print("=" * 60)
    
    try:
        from utils.financial_calculator import FinancialData
        from agents.collectors.enhanced_yfinance_client import DataValidator
        
        # Recriar exatamente os dados do teste que falha
        print("📋 DADOS DO TESTE:")
        print("-" * 30)
        
        # Dados "completos" do teste
        complete_data = FinancialData(
            current_price=25.50,
            market_cap=100000000000,
            revenue=50000000000,
            net_income=6000000000,
            total_assets=200000000000,
            shareholders_equity=80000000000,
            sector="Tecnologia",
            last_updated=datetime.now()
        )
        
        print("✅ DADOS 'COMPLETOS':")
        required_fields = ['current_price', 'market_cap', 'revenue', 'net_income']
        for field in required_fields:
            value = getattr(complete_data, field)
            status = "✅" if value is not None else "❌"
            print(f"   {field}: {status} {value}")
        
        # Dados incompletos
        incomplete_data = FinancialData(
            current_price=25.50,
            market_cap=None,  # AUSENTE!
            revenue=50000000000
            # net_income também está ausente!
        )
        
        print(f"\n❌ DADOS INCOMPLETOS:")
        for field in required_fields:
            value = getattr(incomplete_data, field)
            status = "✅" if value is not None else "❌"
            print(f"   {field}: {status} {value}")
        
        # Executar validações
        print(f"\n🧪 RESULTADOS DA VALIDAÇÃO:")
        print("-" * 30)
        
        validation_complete = DataValidator.validate_financial_data(complete_data)
        validation_incomplete = DataValidator.validate_financial_data(incomplete_data)
        
        print(f"DADOS COMPLETOS:")
        print(f"   Válido: {validation_complete['valid']}")
        print(f"   Erros: {validation_complete['errors']}")
        print(f"   Warnings: {validation_complete['warnings']}")
        print(f"   Score: {validation_complete['quality_score']}")
        
        print(f"\nDADOS INCOMPLETOS:")
        print(f"   Válido: {validation_incomplete['valid']}")
        print(f"   Erros: {validation_incomplete['errors']}")
        print(f"   Warnings: {validation_incomplete['warnings']}")
        print(f"   Score: {validation_incomplete['quality_score']}")
        
        # Analisar o impacto específico
        print(f"\n🎯 ANÁLISE DO IMPACTO:")
        print("-" * 30)
        
        # Teste 1: Dados completos devem ser válidos
        complete_should_be_valid = validation_complete['valid']
        print(f"1. Dados completos válidos: {'✅' if complete_should_be_valid else '❌'}")
        if not complete_should_be_valid:
            print(f"   ⚠️  PROBLEMA: Dados 'completos' considerados inválidos!")
            print(f"   Erros: {validation_complete['errors']}")
        
        # Teste 2: Dados incompletos devem ser inválidos
        incomplete_should_be_invalid = not validation_incomplete['valid']
        print(f"2. Dados incompletos inválidos: {'✅' if incomplete_should_be_invalid else '❌'}")
        
        # Teste 3: Score de qualidade
        quality_complete = validation_complete['quality_score']
        quality_incomplete = validation_incomplete['quality_score']
        
        print(f"3. Score completos ({quality_complete}) > incompletos ({quality_incomplete}): {'✅' if quality_complete > quality_incomplete else '❌'}")
        print(f"4. Score completos ≥ 60: {'✅' if quality_complete >= 60 else '❌'}")
        print(f"5. Score incompletos ≤ 30: {'✅' if quality_incomplete <= 30 else '❌'}")
        
        # Identificar qual teste está falhando
        failing_tests = []
        if not complete_should_be_valid:
            failing_tests.append("Dados completos considerados inválidos")
        if not incomplete_should_be_invalid:
            failing_tests.append("Dados incompletos considerados válidos")
        if quality_complete < 60:
            failing_tests.append(f"Score completos muito baixo: {quality_complete}")
        if quality_incomplete > 30:
            failing_tests.append(f"Score incompletos muito alto: {quality_incomplete}")
        
        if failing_tests:
            print(f"\n❌ TESTES QUE PODEM ESTAR FALHANDO:")
            for test in failing_tests:
                print(f"   • {test}")
        else:
            print(f"\n✅ TODOS OS CRITÉRIOS ATENDIDOS!")
        
        return failing_tests
        
    except Exception as e:
        print(f"❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return []

def test_different_complete_data():
    """Testa com dados realmente completos"""
    print(f"\n🧪 TESTE COM DADOS REALMENTE COMPLETOS")
    print("=" * 50)
    
    try:
        from utils.financial_calculator import FinancialData
        from agents.collectors.enhanced_yfinance_client import DataValidator
        
        # Dados REALMENTE completos
        really_complete_data = FinancialData(
            # Dados básicos obrigatórios
            current_price=25.50,
            market_cap=100000000000,
            revenue=50000000000,
            net_income=6000000000,
            
            # Dados adicionais importantes
            shares_outstanding=4000000000,
            total_assets=200000000000,
            shareholders_equity=80000000000,
            total_debt=30000000000,
            current_assets=50000000000,
            current_liabilities=20000000000,
            cash_and_equivalents=10000000000,
            gross_profit=20000000000,
            operating_income=8000000000,
            ebitda=10000000000,
            
            # Dados históricos
            revenue_history=[45000000000, 47000000000, 50000000000],
            net_income_history=[4000000000, 5000000000, 6000000000],
            
            # Metadados
            sector="Tecnologia",
            industry="Software",
            last_updated=datetime.now()
        )
        
        validation = DataValidator.validate_financial_data(really_complete_data)
        quality = DataValidator.calculate_data_quality_score(really_complete_data)
        
        print(f"📊 RESULTADOS COM DADOS REALMENTE COMPLETOS:")
        print(f"   Válido: {validation['valid']}")
        print(f"   Score: {quality}")
        print(f"   Completude: {validation['completeness']:.1%}")
        print(f"   Erros: {validation['errors']}")
        print(f"   Warnings: {validation['warnings']}")
        
        # Verificar se isso resolve o problema
        tests_pass = (
            validation['valid'] and 
            quality >= 60 and 
            len(validation['errors']) == 0
        )
        
        print(f"\n🎯 TESTE COM DADOS COMPLETOS: {'✅ PASSA' if tests_pass else '❌ FALHA'}")
        
        return quality
        
    except Exception as e:
        print(f"❌ ERRO: {e}")
        return 0

def recommend_solution():
    """Recomenda solução baseada na análise"""
    print(f"\n💡 RECOMENDAÇÕES:")
    print("=" * 30)
    
    print("1. 🔧 CORREÇÃO IMEDIATA:")
    print("   • Usar dados realmente completos no teste")
    print("   • Ou ajustar thresholds para valores reais")
    
    print(f"\n2. 🎯 DADOS COMPLETOS IDEAIS:")
    print("   • Incluir shares_outstanding")
    print("   • Incluir dados históricos")
    print("   • Incluir mais campos do balanço")
    
    print(f"\n3. 📊 THRESHOLDS REALISTAS:")
    print("   • Score alto: ≥ 60 (em vez de > 70)")
    print("   • Score baixo: ≤ 30 (em vez de < 50)")
    print("   • Foco na comparação relativa")

def main():
    """Função principal"""
    print("🚀 ANÁLISE DO IMPACTO DOS CAMPOS OBRIGATÓRIOS")
    print("=" * 60)
    
    # Analisar problema atual
    failing_tests = analyze_required_fields_impact()
    
    # Testar com dados realmente completos
    better_quality = test_different_complete_data()
    
    # Recomendações
    recommend_solution()
    
    print(f"\n📋 CONCLUSÃO:")
    if failing_tests:
        print("❌ O problema É influenciado pelos campos obrigatórios")
        print("🔧 Solução: Usar dados mais completos OU ajustar thresholds")
    else:
        print("✅ O problema NÃO é dos campos obrigatórios")
        print("🔧 Solução: Apenas ajustar thresholds do teste")

if __name__ == "__main__":
    main()
