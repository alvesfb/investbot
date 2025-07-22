#!/usr/bin/env python3
"""
Debug - Verificar quais dados o YFinance realmente retorna para empresas brasileiras
"""

import sys
import asyncio
from pathlib import Path

# Adicionar diretório raiz ao path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

async def debug_yfinance_data():
    """Debug completo dos dados do YFinance"""
    
    print("🔍 DEBUG - DADOS REAIS DO YFINANCE")
    print("=" * 60)
    
    try:
        from agents.collectors.stock_collector import YFinanceClient
        
        # Testar empresa brasileira
        symbol = 'ITUB4'
        print(f"📊 Coletando TODOS os dados para {symbol}...")
        
        client = YFinanceClient()
        raw_data = await client.get_stock_info(symbol)
        
        if not raw_data:
            print("❌ Nenhum dado retornado")
            return
        
        print(f"\n📋 CAMPOS DISPONÍVEIS ({len(raw_data)} total):")
        
        # Categorizar dados
        financial_fields = [
            'totalRevenue', 'netIncomeToCommon', 'totalAssets', 
            'totalStockholderEquity', 'totalDebt', 'totalCurrentAssets',
            'totalCurrentLiabilities', 'grossProfit', 'operatingIncome', 'ebitda'
        ]
        
        market_fields = [
            'regularMarketPrice', 'currentPrice', 'marketCap', 'volume'
        ]
        
        ratio_fields = [
            'trailingPE', 'priceToBook', 'returnOnEquity', 'debtToEquity',
            'currentRatio', 'profitMargins'
        ]
        
        print(f"\n💰 DADOS FINANCEIROS:")
        for field in financial_fields:
            value = raw_data.get(field)
            status = "✅" if value is not None else "❌"
            print(f"   {status} {field}: {value}")
        
        print(f"\n📈 DADOS DE MERCADO:")
        for field in market_fields:
            value = raw_data.get(field)
            status = "✅" if value is not None else "❌"
            print(f"   {status} {field}: {value}")
        
        print(f"\n📊 RATIOS E INDICADORES:")
        for field in ratio_fields:
            value = raw_data.get(field)
            status = "✅" if value is not None else "❌"
            print(f"   {status} {field}: {value}")
        
        # Mostrar TODOS os campos disponíveis
        print(f"\n🗂️ TODOS OS CAMPOS DISPONÍVEIS:")
        available_fields = [k for k, v in raw_data.items() if v is not None]
        missing_fields = [k for k, v in raw_data.items() if v is None]
        
        print(f"   ✅ Disponíveis ({len(available_fields)}): {', '.join(available_fields[:10])}...")
        print(f"   ❌ Vazios ({len(missing_fields)}): {', '.join(missing_fields[:10])}...")
        
        # Verificar dados históricos específicos
        historical_fields = [
            'financialData', 'financials', 'quarterlyFinancials',
            'balanceSheet', 'quarterlyBalanceSheet', 'cashflow'
        ]
        
        print(f"\n📅 DADOS HISTÓRICOS:")
        for field in historical_fields:
            value = raw_data.get(field)
            status = "✅" if value is not None else "❌"
            print(f"   {status} {field}: {type(value) if value else 'None'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no debug: {e}")
        return False

async def test_alternative_symbols():
    """Testar símbolos alternativos"""
    
    print(f"\n🔄 TESTANDO SÍMBOLOS ALTERNATIVOS")
    print("=" * 50)
    
    symbols_to_test = [
        'ITUB4.SA',  # Com .SA
        'ITUB4',     # Sem .SA
        'AAPL',      # Empresa americana para comparação
    ]
    
    try:
        from agents.collectors.stock_collector import YFinanceClient
        client = YFinanceClient()
        
        for symbol in symbols_to_test:
            print(f"\n📊 Testando {symbol}:")
            
            data = await client.get_stock_info(symbol)
            
            if data:
                # Verificar campos essenciais
                essential_fields = ['totalRevenue', 'netIncomeToCommon', 'totalAssets']
                available = sum(1 for field in essential_fields if data.get(field) is not None)
                
                print(f"   Dados essenciais: {available}/{len(essential_fields)}")
                print(f"   Market Cap: {data.get('marketCap', 'N/A')}")
                print(f"   Revenue: {data.get('totalRevenue', 'N/A')}")
                print(f"   Net Income: {data.get('netIncomeToCommon', 'N/A')}")
            else:
                print(f"   ❌ Nenhum dado retornado")
        
    except Exception as e:
        print(f"❌ Erro no teste alternativo: {e}")

def main():
    """Executar debug completo"""
    
    try:
        asyncio.run(debug_yfinance_data())
        asyncio.run(test_alternative_symbols())
        
        print(f"\n💡 CONCLUSÕES E PRÓXIMOS PASSOS:")
        print("1. Verificar quais campos estão realmente disponíveis")
        print("2. Adaptar conversão para usar campos disponíveis")
        print("3. Considerar APIs alternativas para dados fundamentais")
        print("4. Implementar fallbacks mais inteligentes")
        
    except Exception as e:
        print(f"❌ Erro fatal: {e}")

if __name__ == "__main__":
    main()