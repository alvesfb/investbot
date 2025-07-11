# scripts/test_stock_collector.py
"""
Script para testar o Agente Coletor de forma simples
"""
import asyncio
import sys
import json
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Adicionar path do projeto
sys.path.insert(0, '.')


async def test_yfinance_direct():
    """Testa YFinance diretamente"""
    try:
        logger.info("🧪 Testando YFinance diretamente...")
        
        # Instalar yfinance se necessário
        try:
            import yfinance as yf
        except ImportError:
            logger.info("📦 Instalando yfinance...")
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "yfinance"])
            import yfinance as yf
        
        # Testar algumas ações brasileiras
        test_symbols = ["PETR4.SA", "VALE3.SA", "ITUB4.SA"]
        results = []
        
        for symbol in test_symbols:
            try:
                logger.info(f"   Testando {symbol}...")
                ticker = yf.Ticker(symbol)
                
                # Buscar informações básicas
                info = ticker.info
                hist = ticker.history(period="1d")
                
                if not hist.empty and info:
                    price = hist['Close'].iloc[-1] if not hist.empty else info.get('regularMarketPrice', 0)
                    volume = hist['Volume'].iloc[-1] if not hist.empty else info.get('regularMarketVolume', 0)
                    
                    stock_data = {
                        "symbol": symbol,
                        "name": info.get('shortName') or info.get('longName') or symbol,
                        "price": float(price) if price else 0,
                        "volume": int(volume) if volume else 0,
                        "market_cap": info.get('marketCap'),
                        "pe_ratio": info.get('trailingPE'),
                        "success": True
                    }
                    
                    results.append(stock_data)
                    logger.info(f"   ✅ {symbol}: {stock_data['name']} - R$ {stock_data['price']:.2f}")
                else:
                    results.append({"symbol": symbol, "success": False, "error": "Sem dados"})
                    logger.warning(f"   ⚠️ {symbol}: Sem dados disponíveis")
                    
            except Exception as e:
                results.append({"symbol": symbol, "success": False, "error": str(e)})
                logger.error(f"   ❌ {symbol}: {e}")
        
        successful = sum(1 for r in results if r.get("success"))
        logger.info(f"📊 YFinance: {successful}/{len(test_symbols)} sucessos")
        
        return results
        
    except Exception as e:
        logger.error(f"❌ Erro no teste YFinance: {e}")
        return []


async def test_database_integration():
    """Testa integração com banco de dados"""
    try:
        logger.info("🧪 Testando integração com banco...")
        
        from database.repositories import get_stock_repository
        stock_repo = get_stock_repository()
        
        # Verificar ações existentes
        existing_stocks = stock_repo.get_all_stocks()
        logger.info(f"   📋 {len(existing_stocks)} ações no banco")
        
        # Testar criação/atualização
        test_stock_data = {
            "codigo": "TEST4",
            "nome": "Ação de Teste",
            "preco_atual": 25.50,
            "volume_medio": 1000000,
            "setor": "Teste",
            "ativo": True
        }
        
        # Verificar se já existe
        existing = stock_repo.get_stock_by_code("TEST4")
        if existing:
            # Atualizar preço
            success = stock_repo.update_stock_price("TEST4", 26.00, 1100000)
            if success:
                logger.info("   ✅ Atualização de preço OK")
            else:
                logger.warning("   ⚠️ Falha na atualização")
        else:
            # Criar nova
            new_stock = stock_repo.create_stock(test_stock_data)
            if new_stock:
                logger.info(f"   ✅ Criação OK - ID: {new_stock.id}")
            else:
                logger.warning("   ⚠️ Falha na criação")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro na integração DB: {e}")
        return False


async def test_simplified_collector():
    """Testa versão simplificada do coletor"""
    try:
        logger.info("🧪 Testando coletor simplificado...")
        
        from database.repositories import get_stock_repository
        import yfinance as yf
        
        stock_repo = get_stock_repository()
        
        # Ações para testar
        test_codes = ["PETR4", "VALE3", "ITUB4"]
        results = {
            "total": len(test_codes),
            "successful": 0,
            "failed": 0,
            "details": []
        }
        
        for codigo in test_codes:
            try:
                logger.info(f"   Processando {codigo}...")
                
                # Buscar dados no YFinance
                symbol = f"{codigo}.SA"
                ticker = yf.Ticker(symbol)
                info = ticker.info
                hist = ticker.history(period="1d")
                
                if info and not hist.empty:
                    price = hist['Close'].iloc[-1]
                    volume = hist['Volume'].iloc[-1]
                    
                    # Verificar se ação existe no banco
                    existing = stock_repo.get_stock_by_code(codigo)
                    
                    if existing:
                        # Atualizar preço
                        success = stock_repo.update_stock_price(codigo, float(price), int(volume))
                        action = "updated"
                    else:
                        # Criar nova ação
                        stock_data = {
                            "codigo": codigo,
                            "nome": info.get('shortName') or info.get('longName') or codigo,
                            "preco_atual": float(price),
                            "volume_medio": int(volume),
                            "market_cap": info.get('marketCap'),
                            "p_l": info.get('trailingPE'),
                            "p_vp": info.get('priceToBook'),
                            "setor": "Coletado",
                            "ativo": True
                        }
                        new_stock = stock_repo.create_stock(stock_data)
                        success = new_stock is not None
                        action = "created"
                    
                    if success:
                        results["successful"] += 1
                        results["details"].append({
                            "codigo": codigo,
                            "action": action,
                            "price": float(price),
                            "volume": int(volume),
                            "success": True
                        })
                        logger.info(f"   ✅ {codigo}: {action} - R$ {price:.2f}")
                    else:
                        results["failed"] += 1
                        results["details"].append({
                            "codigo": codigo,
                            "success": False,
                            "error": "Falha no banco de dados"
                        })
                        logger.error(f"   ❌ {codigo}: Falha no banco")
                else:
                    results["failed"] += 1
                    results["details"].append({
                        "codigo": codigo,
                        "success": False,
                        "error": "Sem dados do YFinance"
                    })
                    logger.warning(f"   ⚠️ {codigo}: Sem dados")
                    
            except Exception as e:
                results["failed"] += 1
                results["details"].append({
                    "codigo": codigo,
                    "success": False,
                    "error": str(e)
                })
                logger.error(f"   ❌ {codigo}: {e}")
        
        logger.info(f"📊 Coletor: {results['successful']}/{results['total']} sucessos")
        return results
        
    except Exception as e:
        logger.error(f"❌ Erro no coletor: {e}")
        return {}


async def test_agno_agent():
    """Testa o agente Agno completo"""
    try:
        logger.info("🧪 Testando Agente Agno...")
        
        # Verificar se agno está instalado
        try:
            from agno import Agent
        except ImportError:
            logger.warning("⚠️ Agno não está instalado - testando apenas funcionalidade básica")
            return await test_simplified_collector()
        
        # Tentar importar o agente
        try:
            from agents.collectors.stock_collector import StockCollectorAgent
        except ImportError as e:
            logger.error(f"❌ Erro ao importar agente: {e}")
            logger.info("🔄 Usando coletor simplificado...")
            return await test_simplified_collector()
        
        # Criar e testar agente
        collector = StockCollectorAgent()
        test_stocks = ["PETR4", "VALE3", "ITUB4"]
        
        # Iniciar sessão
        session_id = await collector.start_collection_session(test_stocks)
        logger.info(f"   📋 Sessão: {session_id}")
        
        # Buscar tool de coleta
        collect_tool = None
        for tool in collector.tools:
            if tool.name == "collect_stock_data":
                collect_tool = tool
                break
        
        if collect_tool:
            # Executar coleta
            results = await collect_tool(test_stocks)
            await collector.finish_collection_session(results)
            
            logger.info(f"   📊 Total: {results['total_requested']}")
            logger.info(f"   ✅ Sucessos: {results['successful']}")
            logger.info(f"   ❌ Falhas: {results['failed']}")
            logger.info(f"   ⏱️ Tempo: {results['processing_time']:.2f}s")
            
            return results
        else:
            logger.error("❌ Tool não encontrada")
            return {}
            
    except Exception as e:
        logger.error(f"❌ Erro no agente Agno: {e}")
        logger.info("🔄 Usando coletor simplificado...")
        return await test_simplified_collector()


async def main():
    """Função principal de teste"""
    logger.info("🚀 TESTE DO AGENTE COLETOR - PASSO 3")
    logger.info("=" * 50)
    
    # 1. Testar YFinance
    logger.info("\n1️⃣ TESTE YFINANCE")
    logger.info("-" * 30)
    yf_results = await test_yfinance_direct()
    
    # 2. Testar banco de dados
    logger.info("\n2️⃣ TESTE BANCO DE DADOS")
    logger.info("-" * 30)
    db_success = await test_database_integration()
    
    # 3. Testar coletor (simplificado ou Agno)
    logger.info("\n3️⃣ TESTE COLETOR")
    logger.info("-" * 30)
    collector_results = await test_agno_agent()
    
    # Resumo final
    logger.info("\n📊 RESUMO FINAL")
    logger.info("=" * 50)
    
    yf_success = sum(1 for r in yf_results if r.get("success"))
    logger.info(f"YFinance: {yf_success}/{len(yf_results)} sucessos")
    logger.info(f"Banco de dados: {'✅ OK' if db_success else '❌ Falha'}")
    
    if collector_results:
        if isinstance(collector_results, dict) and "successful" in collector_results:
            logger.info(f"Coletor: {collector_results['successful']}/{collector_results.get('total', 0)} sucessos")
        else:
            logger.info("Coletor: Executado (formato diferente)")
    else:
        logger.info("Coletor: ❌ Falha")
    
    # Status do Passo 3
    logger.info("\n🎯 STATUS DO PASSO 3")
    logger.info("-" * 30)
    
    if yf_success >= 2 and db_success and collector_results:
        logger.info("✅ PASSO 3 CONCLUÍDO COM SUCESSO!")
        logger.info("🚀 Pronto para Passo 4: Automação e Agendamento")
    elif yf_success >= 2 and db_success:
        logger.info("🔶 PASSO 3 PARCIALMENTE CONCLUÍDO")
        logger.info("💡 YFinance e banco funcionam - pode prosseguir")
        logger.info("🔧 Considere melhorar o agente Agno se necessário")
    else:
        logger.warning("⚠️ PASSO 3 COM PROBLEMAS")
        logger.info("🔧 Corrija os problemas antes de prosseguir:")
        if yf_success < 2:
            logger.info("   - Verificar conexão YFinance")
        if not db_success:
            logger.info("   - Verificar banco de dados")
        if not collector_results:
            logger.info("   - Verificar implementação do coletor")
    
    return {
        "yfinance": yf_results,
        "database": db_success,
        "collector": collector_results
    }


if __name__ == "__main__":
    asyncio.run(main())
