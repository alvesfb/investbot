# test_reasoning_integration.py
"""
Teste da integração com reasoning_agent
"""

def test_traditional_calculation():
    """Testa cálculo tradicional (sem reasoning)"""
    try:
        from utils.financial_calculator import FinancialCalculator, FinancialData
        
        calculator = FinancialCalculator()
        data = FinancialData(
            market_cap=100000000000,
            revenue=50000000000,
            net_income=6000000000,
            sector="Tecnologia"
        )
        
        metrics = calculator.calculate_all_metrics(data)
        print(f"✅ Score tradicional: {metrics.overall_score:.1f}")
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste tradicional: {e}")
        return False

def test_reasoning_calculation():
    """Testa cálculo com reasoning_agent"""
    try:
        from utils.financial_calculator import FinancialCalculator, FinancialData
        
        # Mock reasoning agent para teste
        class MockReasoningAgent:
            def run(self, prompt):
                return """
                SCORE_AJUSTADO: 82.5
                JUSTIFICATIVA: Score aumentado devido a métricas sólidas para o setor
                CONFIANÇA: 90
                """
        
        calculator = FinancialCalculator()
        data = FinancialData(
            market_cap=100000000000,
            revenue=50000000000,
            net_income=6000000000,
            sector="Tecnologia"
        )
        
        mock_agent = MockReasoningAgent()
        metrics = calculator.calculate_all_metrics(data, reasoning_agent=mock_agent)
        
        print(f"✅ Score com reasoning: {metrics.overall_score:.1f}")
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste com reasoning: {e}")
        return False

def test_fundamental_analyzer():
    """Testa FundamentalAnalyzerAgent com reasoning"""
    try:
        from agents.analyzers.fundamental_scoring_system import FundamentalAnalyzerAgent
        
        agent = FundamentalAnalyzerAgent()
        result = agent.analyze_single_stock('PETR4')
        
        if "error" in result:
            print(f"❌ Erro na análise: {result['error']}")
            return False
        
        score = result["fundamental_score"]["composite_score"]
        print(f"✅ Score FundamentalAnalyzer: {score:.1f}")
        return True
        
    except Exception as e:
        print(f"❌ Erro no FundamentalAnalyzer: {e}")
        return False

if __name__ == "__main__":
    print("🧪 TESTANDO INTEGRAÇÃO REASONING")
    print("=" * 50)
    
    results = []
    results.append(test_traditional_calculation())
    results.append(test_reasoning_calculation())
    results.append(test_fundamental_analyzer())
    
    success_count = sum(results)
    print(f"\n📊 RESULTADOS: {success_count}/3 testes passaram")
    
    if success_count == 3:
        print("🎉 REASONING INTEGRATION FUNCIONANDO!")
    else:
        print("❌ Alguns testes falharam")
