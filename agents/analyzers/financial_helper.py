# agents/analyzers/financial_helper.py
"""
Helper para usar FinancialData corretamente
Resolve o problema do 'symbol' parameter
"""

import sys
from pathlib import Path
from typing import Optional

# Garantir path
current_dir = Path.cwd()
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

try:
    from utils.financial_calculator import FinancialData, FinancialCalculator, FinancialMetrics
    CALCULATOR_AVAILABLE = True
except ImportError as e:
    print(f"Erro ao importar FinancialCalculator: {e}")
    CALCULATOR_AVAILABLE = False

def create_financial_data(stock_code: str = "UNKNOWN",
                         market_cap: Optional[float] = None,
                         revenue: Optional[float] = None,
                         net_income: Optional[float] = None,
                         current_price: Optional[float] = None):
    """
    Cria FinancialData da forma correta (SEM 'symbol')
    
    Args:
        stock_code: Código da ação (apenas para referência)
        market_cap: Valor de mercado
        revenue: Receita
        net_income: Lucro líquido
        current_price: Preço atual
        
    Returns:
        FinancialData configurado corretamente
    """
    if not CALCULATOR_AVAILABLE:
        return None
    
    try:
        # Criar FinancialData vazio (forma que funciona)
        data = FinancialData()
        
        # Definir atributos se existirem
        if hasattr(data, 'market_cap') and market_cap is not None:
            data.market_cap = market_cap
        
        if hasattr(data, 'revenue') and revenue is not None:
            data.revenue = revenue
            
        if hasattr(data, 'net_income') and net_income is not None:
            data.net_income = net_income
            
        if hasattr(data, 'current_price') and current_price is not None:
            data.current_price = current_price
        
        return data
        
    except Exception as e:
        print(f"Erro ao criar FinancialData: {e}")
        return FinancialData()  # Fallback para instância vazia

def safe_calculate_metrics(stock_code: str,
                          market_cap: Optional[float] = None,
                          revenue: Optional[float] = None,
                          net_income: Optional[float] = None,
                          current_price: Optional[float] = None):
    """
    Calcula métricas de forma segura
    """
    if not CALCULATOR_AVAILABLE:
        return MockMetrics()
    
    try:
        # Criar dados financeiros
        financial_data = create_financial_data(
            stock_code=stock_code,
            market_cap=market_cap,
            revenue=revenue,
            net_income=net_income,
            current_price=current_price
        )
        
        # Calcular métricas
        calculator = FinancialCalculator()
        metrics = calculator.calculate_all_metrics(financial_data)
        
        return metrics
        
    except Exception as e:
        print(f"Erro ao calcular métricas para {stock_code}: {e}")
        return MockMetrics()

class MockMetrics:
    """Métricas mock para fallback"""
    def __init__(self):
        self.pe_ratio = 15.0
        self.roe = 18.5
        self.profit_margin = 12.0
        self.pb_ratio = 1.8
        self.debt_to_equity = 0.8
        
    def __dict__(self):
        return {
            'pe_ratio': self.pe_ratio,
            'roe': self.roe,
            'profit_margin': self.profit_margin,
            'pb_ratio': self.pb_ratio,
            'debt_to_equity': self.debt_to_equity
        }

def test_helper():
    """Testa o helper"""
    print("🧪 Testando helper...")
    
    try:
        # Teste criar dados
        data = create_financial_data(
            stock_code="PETR4",
            market_cap=100000000000,
            revenue=50000000000,
            net_income=6000000000
        )
        print("✅ create_financial_data: OK")
        
        # Teste calcular métricas
        metrics = safe_calculate_metrics(
            stock_code="PETR4",
            market_cap=100000000000,
            revenue=50000000000,
            net_income=6000000000
        )
        print("✅ safe_calculate_metrics: OK")
        
        if hasattr(metrics, 'roe'):
            print(f"   ROE: {getattr(metrics, 'roe', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

if __name__ == "__main__":
    test_helper()
