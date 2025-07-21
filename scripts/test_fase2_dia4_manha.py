#!/usr/bin/env python3
"""
Teste rápido da Fase 2 - Dia 4 Manhã
Valida se população automática funcionou
"""
import asyncio
from database.repositories import get_stock_repository

async def test_enhanced_population():
    """Testa se população automática funcionou"""
    print("🧪 TESTANDO POPULAÇÃO AUTOMÁTICA")
    print("=" * 40)
    
    try:
        repo = get_stock_repository()
        
        # 1. Contar total
        total = repo.count_all_stocks()
        print(f"📊 Total de ações: {total}")
        
        # 2. Verificar qualidade
        high_quality = repo.count_stocks_by_quality('good')
        print(f"✅ Qualidade boa: {high_quality}")
        
        # 3. Verificar preços válidos
        with_prices = repo.count_stocks_with_prices()
        print(f"💰 Com preços válidos: {with_prices}")
        
        # 4. Teste de uma ação específica
        petr4 = repo.get_stock_by_symbol("PETR4")
        if petr4:
            print(f"🧪 PETR4: R$ {petr4.current_price} - {petr4.data_quality.value}")
        
        # 5. Avaliação final
        if total >= 30 and with_prices >= 25:
            print("🎉 TESTE PASSOU - População bem-sucedida!")
            return True
        else:
            print("⚠️  TESTE PARCIAL - População parcial")
            return False
            
    except Exception as e:
        print(f"❌ ERRO NO TESTE: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_enhanced_population())
    exit(0 if success else 1)
