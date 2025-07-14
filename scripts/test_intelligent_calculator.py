# Criar arquivo test_intelligent_calculator.py
from utils.financial_calculator import FinancialCalculator, FinancialData

# Teste rápido
data = FinancialData(market_cap=100000000000, revenue=50000000000, sector="Tecnologia")
calc = FinancialCalculator()

# Teste tradicional
metrics_traditional = calc.calculate_all_metrics(data)
print(f"Score tradicional: {metrics_traditional.overall_score:.1f}")

# Teste inteligente (quando Agno disponível)
# metrics_intelligent = calc.calculate_all_metrics(data, reasoning_agent=agente)
# print(f"Score inteligente: {metrics_intelligent.overall_score:.1f}")