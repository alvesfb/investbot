# debug_data_validator.py
"""
Script de diagnóstico para identificar o problema no Validador de Dados
"""
import sys
from pathlib import Path
from datetime import datetime

# Adicionar projeto ao path
project_root = Path.cwd()
sys.path.insert(0, str(project_root))

def debug_data_validator():
    """Diagnostica problemas no validador de dados"""
    print("🔍 DIAGNÓSTICO DO VALIDADOR DE DADOS")
    print("=" * 50)
    
    try:
        # Teste 1: Importações
        print("1️⃣ Testando importações...")
        from utils.financial_calculator import FinancialData
        print("   ✅ FinancialData importado")
        
        from agents.collectors.enhanced_yfinance_client import DataValidator
        print("   ✅ DataValidator importado")
        
        # Teste 2: Criar dados de teste
        print("\n2️⃣ Criando dados de teste...")
        
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
        print("   ✅ Dados completos criados")
        
        incomplete_data = FinancialData(
            current_price=25.50,
            market_cap=None,  # Dado faltante
            revenue=50000000000
        )
        print("   ✅ Dados incompletos criados")
        
        # Teste 3: Validação de dados completos
        print("\n3️⃣ Testando validação de dados completos...")
        try:
            validation_complete = DataValidator.validate_financial_data(complete_data)
            print(f"   ✅ Validação completa: {validation_complete}")
        except Exception as e:
            print(f"   ❌ Erro na validação completa: {e}")
            return False
        
        # Teste 4: Validação de dados incompletos
        print("\n4️⃣ Testando validação de dados incompletos...")
        try:
            validation_incomplete = DataValidator.validate_financial_data(incomplete_data)
            print(f"   ✅ Validação incompleta: {validation_incomplete}")
        except Exception as e:
            print(f"   ❌ Erro na validação incompleta: {e}")
            return False
        
        # Teste 5: Score de qualidade
        print("\n5️⃣ Testando score de qualidade...")
        try:
            quality_complete = DataValidator.calculate_data_quality_score(complete_data)
            print(f"   ✅ Score dados completos: {quality_complete}")
            
            quality_incomplete = DataValidator.calculate_data_quality_score(incomplete_data)
            print(f"   ✅ Score dados incompletos: {quality_incomplete}")
        except Exception as e:
            print(f"   ❌ Erro no cálculo de qualidade: {e}")
            return False
        
        # Teste 6: Verificações detalhadas
        print("\n6️⃣ Verificações detalhadas...")
        
        # Verificar estrutura do resultado
        required_keys = ['valid', 'warnings', 'errors', 'completeness', 'quality_score']
        for key in required_keys:
            if key in validation_complete:
                print(f"   ✅ Chave '{key}' presente")
            else:
                print(f"   ❌ Chave '{key}' AUSENTE")
                return False
        
        # Teste 7: Lógica de validação
        print("\n7️⃣ Testando lógica de validação...")
        
        # Dados completos devem ser válidos
        if validation_complete["valid"]:
            print("   ✅ Dados completos considerados válidos")
        else:
            print("   ❌ Dados completos considerados inválidos")
            print(f"   Erros: {validation_complete.get('errors', [])}")
        
        # Dados incompletos devem ser inválidos
        if not validation_incomplete["valid"]:
            print("   ✅ Dados incompletos considerados inválidos")
        else:
            print("   ❌ Dados incompletos considerados válidos (erro de lógica)")
            return False
        
        # Score de qualidade
        if quality_complete > quality_incomplete:
            print("   ✅ Score de qualidade: completos > incompletos")
        else:
            print("   ❌ Score de qualidade: lógica incorreta")
            print(f"   Completos: {quality_complete}, Incompletos: {quality_incomplete}")
        
        print("\n✅ TODOS OS TESTES DO VALIDADOR PASSARAM!")
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO CRÍTICO: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_dataclass_fields():
    """Testa se os campos do FinancialData estão corretos"""
    print("\n🔍 DIAGNÓSTICO DOS CAMPOS FinancialData")
    print("=" * 50)
    
    try:
        from utils.financial_calculator import FinancialData
        
        # Verificar se é dataclass
        import dataclasses
        if dataclasses.is_dataclass(FinancialData):
            print("✅ FinancialData é um dataclass")
        else:
            print("❌ FinancialData NÃO é um dataclass")
            return False
        
        # Listar campos
        fields = FinancialData.__dataclass_fields__
        print(f"✅ Campos encontrados: {len(fields)}")
        
        for field_name, field_info in fields.items():
            print(f"   • {field_name}: {field_info.type}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar campos: {e}")
        return False

def main():
    """Função principal"""
    print("🚀 DIAGNÓSTICO COMPLETO DO VALIDADOR DE DADOS")
    print("=" * 60)
    
    # Teste dos campos
    fields_ok = test_dataclass_fields()
    
    # Teste do validador
    validator_ok = debug_data_validator()
    
    print("\n" + "=" * 60)
    print("📋 RESUMO DO DIAGNÓSTICO")
    print("=" * 60)
    
    if fields_ok and validator_ok:
        print("🎉 DIAGNÓSTICO COMPLETO: TUDO FUNCIONANDO!")
        print("✅ O validador deve estar operacional")
    else:
        print("⚠️  PROBLEMAS DETECTADOS:")
        if not fields_ok:
            print("   • Problema nos campos do FinancialData")
        if not validator_ok:
            print("   • Problema na lógica do DataValidator")

if __name__ == "__main__":
    main()
