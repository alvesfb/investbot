#!/usr/bin/env python3
# =================================================================
# TESTE SIMPLES - VALIDAÇÃO RÁPIDA
# =================================================================
# Teste rápido para validar se a correção funcionou
# Execute: python test_quick.py
# =================================================================

import sys
from pathlib import Path

def setup_path():
    """Configurar path do projeto"""
    current_dir = Path.cwd()
    if str(current_dir) not in sys.path:
        sys.path.insert(0, str(current_dir))

def test_financial_data_direct():
    """Teste direto do FinancialData SEM symbol"""
    print("🧪 TESTE DIRETO - SEM SYMBOL")
    print("=" * 40)
    
    setup_path()
    
    try:
        from utils.financial_calculator import FinancialData, FinancialCalculator
        
        # ✅ CORRETO: Criar sem 'symbol'
        data = FinancialData()
        print("✅ FinancialData() criado (sem symbol)")
        
        # ✅ CORRETO: Definir atributos se existirem
        if hasattr(data, 'market_cap'):
            data.market_cap = 100000000000
            print("✅ market_cap definido")
        
        if hasattr(data, 'revenue'):
            data.revenue = 50000000000
            print("✅ revenue definido")
        
        if hasattr(data, 'net_income'):
            data.net_income = 6000000000
            print("✅ net_income definido")
        
        # ✅ CORRETO: Usar calculator
        calc = FinancialCalculator()
        metrics = calc.calculate_all_metrics(data)
        print("✅ Métricas calculadas SEM symbol!")
        
        # Verificar métricas
        if hasattr(metrics, 'roe'):
            print(f"   ROE: {getattr(metrics, 'roe', 'N/A')}")
        if hasattr(metrics, 'profit_margin'):
            print(f"   Margem: {getattr(metrics, 'profit_margin', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def test_helper_if_exists():
    """Testa helper se foi criado"""
    print("\n🛠️  TESTE DO HELPER")
    print("=" * 30)
    
    setup_path()
    
    try:
        from agents.analyzers.financial_helper import create_financial_data, safe_calculate_metrics
        
        # Teste criar dados
        data = create_financial_data(
            stock_code="PETR4",
            market_cap=100000000000,
            revenue=50000000000,
            net_income=6000000000
        )
        print("✅ Helper create_financial_data: OK")
        
        # Teste calcular métricas
        metrics = safe_calculate_metrics(
            stock_code="PETR4",
            market_cap=100000000000,
            revenue=50000000000,
            net_income=6000000000
        )
        print("✅ Helper safe_calculate_metrics: OK")
        
        return True
        
    except ImportError:
        print("⚠️  Helper não encontrado (execute fix primeiro)")
        return False
    except Exception as e:
        print(f"❌ Erro no helper: {e}")
        return False

def test_scoring_system_if_exists():
    """Testa sistema de scoring se foi criado"""
    print("\n🎯 TESTE DO SISTEMA DE SCORING")
    print("=" * 40)
    
    setup_path()
    
    try:
        from agents.analyzers.fundamental_scoring_corrected import quick_analysis
        
        result = quick_analysis("PETR4")
        
        if "error" in result:
            print(f"❌ Erro no sistema: {result['error']}")
            return False
        
        score = result["fundamental_score"]["composite_score"]
        recommendation = result["recommendation"]
        method = result["system_status"]["calculation_method"]
        
        print(f"✅ PETR4: Score {score:.1f} - {recommendation}")
        print(f"✅ Método: {method}")
        
        return True
        
    except ImportError:
        print("⚠️  Sistema de scoring não encontrado (execute fix primeiro)")
        return False
    except Exception as e:
        print(f"❌ Erro no sistema: {e}")
        return False

def main():
    """Função principal de teste"""
    print("🚀 TESTE RÁPIDO - VALIDAÇÃO DA CORREÇÃO")
    print("=" * 50)
    
    # Teste 1: FinancialData direto
    direct_ok = test_financial_data_direct()
    
    # Teste 2: Helper (se existir)
    helper_ok = test_helper_if_exists()
    
    # Teste 3: Sistema completo (se existir)
    system_ok = test_scoring_system_if_exists()
    
    # Resultado
    print("\n📊 RESULTADO DOS TESTES")
    print("=" * 30)
    print(f"FinancialData direto: {'✅' if direct_ok else '❌'}")
    print(f"Helper: {'✅' if helper_ok else '⚠️ '}")
    print(f"Sistema completo: {'✅' if system_ok else '⚠️ '}")
    
    if direct_ok:
        print("\n🎉 PROBLEMA DO 'SYMBOL' RESOLVIDO!")
        print("✅ FinancialData funciona sem o parâmetro 'symbol'")
        
        if not helper_ok or not system_ok:
            print("\n💡 PRÓXIMO PASSO:")
            print("Execute o script de correção para criar os componentes:")
            print("python fix_financial_data.py")
    else:
        print("\n❌ PROBLEMA AINDA EXISTE")
        print("FinancialData ainda tem problemas")
    
    print(f"\n{'='*50}")
    print(f"TESTE CONCLUÍDO: {'✅ SUCESSO' if direct_ok else '❌ FALHA'}")
    print(f"{'='*50}")

if __name__ == "__main__":
    main()
