# test_financial_calculator.py
"""
Teste mínimo do FinancialCalculator
"""

import sys
from pathlib import Path

# Adicionar projeto ao path
current_dir = Path.cwd()
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

def test_financial_calculator():
    """Teste básico do FinancialCalculator"""
    try:
        print("🧪 Testando FinancialCalculator...")
        
        # Import
        from utils.financial_calculator import FinancialCalculator, FinancialData, FinancialMetrics
        print("✅ Import realizado com sucesso")
        
        # Instanciar calculator
        calc = FinancialCalculator()
        print("✅ FinancialCalculator instanciado")
        
        # Criar dados de teste
        data = FinancialData(
            symbol="PETR4",
            revenue=50000000000,
            net_income=6000000000,
            current_price=25.50
        )
        print("✅ FinancialData criado")
        
        # Calcular métricas
        metrics = calc.calculate_all_metrics(data)
        print("✅ Métricas calculadas")
        
        # Verificar resultado
        if hasattr(metrics, 'roe') or hasattr(metrics, 'profit_margin'):
            print("✅ Métricas contêm dados esperados")
            
            # Exibir algumas métricas
            if hasattr(metrics, 'roe') and metrics.roe:
                print(f"   ROE: {metrics.roe:.2f}%")
            if hasattr(metrics, 'profit_margin') and metrics.profit_margin:
                print(f"   Margem: {metrics.profit_margin:.2f}%")
                
            return True
        else:
            print("❌ Métricas não contêm dados esperados")
            return False
            
    except ImportError as e:
        print(f"❌ Erro de import: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

if __name__ == "__main__":
    success = test_financial_calculator()
    print(f"\nResultado: {'✅ SUCESSO' if success else '❌ FALHA'}")
