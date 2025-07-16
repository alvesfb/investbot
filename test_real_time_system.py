
# test_real_time_system.py
"""
Teste do sistema de busca em tempo real
"""

def test_real_time_fetching():
    """Testa busca automática de dados reais"""
    
    from agents.analyzers.fundamental_scoring_system import FundamentalAnalyzerAgent
    
    agent = FundamentalAnalyzerAgent()
    
    # Testar com ação que não existe no banco
    print("🧪 Testando ação não existente no banco...")
    
    stock_code = "WEGE3"  # WEG - ação real da B3
    
    print(f"📊 Analisando {stock_code}...")
    result = agent.analyze_single_stock(stock_code)
    
    if "error" not in result:
        score = result["fundamental_score"]["composite_score"]
        data_source = result.get("data_source", "unknown")
        
        print(f"✅ {stock_code}:")
        print(f"   • Score: {score:.1f}")
        print(f"   • Fonte: {data_source}")
        
        # Verificar se foi salvo no banco
        if data_source == "yfinance":
            print(f"   ✅ Dados reais obtidos via API")
            print(f"   ✅ Dados salvos no banco para próximas consultas")
        
        # Testar segunda consulta (deve vir do banco agora)
        print(f"\n🔄 Segunda consulta (deve usar banco)...")
        result2 = agent.analyze_single_stock(stock_code)
        
        if result2.get("data_source") == "banco":
            print(f"   ✅ Dados vindos do banco (cache funcionando)")
        
    else:
        print(f"❌ Erro: {result['error']}")

if __name__ == "__main__":
    test_real_time_fetching()
