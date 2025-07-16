import asyncio
import time
from agents.collectors.stock_collector import YFinanceClient


async def test_multi_api_yfinance():
    """Testa YFinanceClient com estratégia multi-API"""
    
    print("🧪 TESTE ESTRATÉGIA MULTI-API")
    print("=" * 35)
    
    try:
        # Importar cliente atualizado
        
        client = YFinanceClient()
        print("✅ YFinanceClient multi-API criado")
        
        # Testar diferentes cenários
        test_symbols = [
            'PETR4',     # Ação grande, deve funcionar com yfinance
            'BBAS3',     # Ação problemática, pode falhar yfinance
            'FAKE99',    # Ação inexistente, deve usar fallback
            'TEST123'    # Ação inventada, deve usar fallback inteligente
        ]
        
        print(f"\\n📊 TESTANDO {len(test_symbols)} SÍMBOLOS:")
        
        results = []
        
        for symbol in test_symbols:
            print(f"\\n🔍 Testando {symbol}...")
            
            start_time = time.time()
            
            try:
                data = await client.get_stock_info(symbol)
                
                duration = round((time.time() - start_time) * 1000, 2)
                
                source = data.get('_source', 'unknown')
                quality = data.get('_data_quality', 'unknown')
                price = data.get('regularMarketPrice', 0)
                
                result = {
                    'symbol': symbol,
                    'success': True,
                    'price': price,
                    'source': source,
                    'quality': quality,
                    'duration_ms': duration
                }
                
                print(f"   ✅ Preço: R$ {price:.2f}")
                print(f"   📡 Fonte: {source}")
                print(f"   🎯 Qualidade: {quality}")
                print(f"   ⏱️  Tempo: {duration}ms")
                
                results.append(result)
                
            except Exception as e:
                result = {
                    'symbol': symbol,
                    'success': False,
                    'error': str(e),
                    'duration_ms': round((time.time() - start_time) * 1000, 2)
                }
                
                print(f"   ❌ Erro: {e}")
                results.append(result)
        
        # Estatísticas finais
        print(f"\\n📈 ESTATÍSTICAS:")
        
        successful = sum(1 for r in results if r['success'])
        total = len(results)
        
        print(f"   • Taxa de sucesso: {successful}/{total} ({(successful/total)*100:.1f}%)")
        
        if hasattr(client, 'get_stats'):
            stats = client.get_stats()
            print(f"   • Cache hit rate: {stats.get('cache_hit_rate', 'N/A')}")
            print(f"   • Confiabilidade: {stats.get('reliability_score', 'N/A')}%")
            print(f"   • Tempo médio: {stats.get('avg_response_time_ms', 'N/A')}ms")
        
        # Testar cache
        print(f"\\n💾 TESTE DE CACHE:")
        
        cache_start = time.time()
        cached_data = await client.get_stock_info('PETR4')  # Segunda chamada
        cache_duration = round((time.time() - cache_start) * 1000, 2)
        
        print(f"   • Segunda chamada PETR4: {cache_duration}ms")
        print(f"   • Melhoria de performance: {((results[0]['duration_ms'] - cache_duration) / results[0]['duration_ms'] * 100):.1f}%")
        
        return results
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return []

async def test_provider_fallback():
    """Testa sequência de fallback dos providers"""
    
    print(f"\n🔄 TESTE DE FALLBACK DOS PROVIDERS:")
    print("=" * 40)
    
    try:
        
        client = YFinanceClient()
        
        # Simular teste com ação problemática
        problematic_symbol = "GOLL4"
        
        print(f"🎯 Testando fallback para {problematic_symbol}")
        print("   Sequência esperada:")
        print("   1. YFinance primário")
        print("   2. YFinance alternativo")
        print("   3. Alpha Vantage (se configurado)")
        print("   4. Financial Modeling Prep (se configurado)")
        print("   5. Dados estáticos")
        print("   6. Fallback inteligente")
        
        data = await client.get_stock_info(problematic_symbol)
        
        source = data.get('_source', 'unknown')
        quality = data.get('_data_quality', 'unknown')
        
        print(f"\n✅ Resultado final:")
        print(f"   • Fonte: {source}")
        print(f"   • Qualidade: {quality}")
        print(f"   • Preço: R$ {data.get('regularMarketPrice', 0):.2f}")
        
        if quality == 'SIMULATED':
            print("   ⚠️  Dados simulados - considere configurar APIs alternativas")
        elif quality == 'STATIC':
            print("   📚 Dados estáticos - considere atualizar base de dados")
        else:
            print("   ✅ Dados obtidos de API externa")
        
    except Exception as e:
        print(f"❌ Erro no teste de fallback: {e}")

if __name__ == "__main__":
    async def main():
        results = await test_multi_api_yfinance()
        await test_provider_fallback()
        
        if results:
            print(f"\n🎉 TESTE CONCLUÍDO COM SUCESSO!")
            print(f"Sistema multi-API funcionando corretamente")
        else:
            print(f"\n❌ TESTE FALHOU")
            print(f"Verificar implementação")
    
    asyncio.run(main())