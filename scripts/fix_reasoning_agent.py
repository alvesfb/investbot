# test_reasoning_fix.py
from agents.analyzers.fundamental_scoring_system import FundamentalAnalyzerAgent

print("🧪 Testando correção do reasoning_agent...")

try:
    # Teste básico
    agent = FundamentalAnalyzerAgent()
    result = agent.analyze_single_stock('PETR4')
    
    if "error" in result:
        print(f"❌ Erro: {result['error']}")
    else:
        score = result['fundamental_score']['composite_score']
        print(f"✅ Score: {score:.1f}")
        print(f"✅ Recomendação: {result['recommendation']}")
        print("🎉 CORREÇÃO FUNCIONOU!")
        
except Exception as e:
    print(f"❌ Erro no teste: {e}")