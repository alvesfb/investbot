# scripts/setup_mcp_yfinance.py
"""
Script para configurar e testar o MCP YFinance Server
"""
import asyncio
import json
import logging
from typing import Dict, Any
import subprocess
import sys

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class MCPYFinanceManager:
    """Gerenciador para MCP YFinance Server"""
    
    def __init__(self):
        self.server_process = None
        self.server_url = "http://localhost:8001"  # Porta padrão MCP YFinance
    
    async def install_mcp_yfinance(self) -> bool:
        """Instala o MCP YFinance Server se não estiver instalado"""
        try:
            logger.info("Verificando instalação do MCP YFinance...")
            
            # Verificar se já está instalado
            result = subprocess.run([
                sys.executable, "-c", "import mcp_server_yfinance"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("✅ MCP YFinance já está instalado")
                return True
            
            # Instalar se não estiver
            logger.info("📦 Instalando MCP YFinance Server...")
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", "mcp-server-yfinance"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("✅ MCP YFinance instalado com sucesso")
                return True
            else:
                logger.error(f"❌ Falha na instalação: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro na instalação: {e}")
            return False
    
    async def start_mcp_server(self) -> bool:
        """Inicia o MCP YFinance Server"""
        try:
            logger.info("🚀 Iniciando MCP YFinance Server...")
            
            # Comando para iniciar o servidor
            cmd = [
                sys.executable, "-m", "mcp_server_yfinance",
                "--host", "localhost",
                "--port", "8001"
            ]
            
            self.server_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Aguardar um pouco para o servidor inicializar
            await asyncio.sleep(3)
            
            # Verificar se está rodando
            if self.server_process.poll() is None:
                logger.info("✅ MCP YFinance Server iniciado")
                return True
            else:
                stderr = self.server_process.stderr.read()
                logger.error(f"❌ Servidor falhou ao iniciar: {stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro ao iniciar servidor: {e}")
            return False
    
    def stop_mcp_server(self):
        """Para o MCP YFinance Server"""
        if self.server_process:
            logger.info("⏹️ Parando MCP YFinance Server...")
            self.server_process.terminate()
            self.server_process.wait()
            self.server_process = None
            logger.info("✅ Servidor parado")
    
    async def test_mcp_connection(self) -> bool:
        """Testa conexão com o MCP Server"""
        try:
            import httpx
            
            logger.info("🧪 Testando conexão com MCP Server...")
            
            async with httpx.AsyncClient(timeout=10) as client:
                # Testar endpoint de health check
                response = await client.get(f"{self.server_url}/health")
                
                if response.status_code == 200:
                    logger.info("✅ Conexão com MCP Server OK")
                    return True
                else:
                    logger.error(f"❌ Falha na conexão: Status {response.status_code}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Erro na conexão: {e}")
            return False
    
    async def test_stock_data_retrieval(self) -> Dict[str, Any]:
        """Testa coleta de dados de ações via MCP"""
        try:
            import httpx
            
            logger.info("🧪 Testando coleta de dados via MCP...")
            
            test_symbols = ["PETR4.SA", "VALE3.SA", "ITUB4.SA"]
            results = {}
            
            async with httpx.AsyncClient(timeout=30) as client:
                for symbol in test_symbols:
                    try:
                        # Endpoint para dados de ação
                        response = await client.post(
                            f"{self.server_url}/get_stock_data",
                            json={"symbol": symbol}
                        )
                        
                        if response.status_code == 200:
                            data = response.json()
                            results[symbol] = {
                                "success": True,
                                "price": data.get("regularMarketPrice"),
                                "volume": data.get("regularMarketVolume"),
                                "name": data.get("shortName")
                            }
                            logger.info(f"✅ {symbol}: {data.get('shortName')} - R$ {data.get('regularMarketPrice')}")
                        else:
                            results[symbol] = {
                                "success": False,
                                "error": f"HTTP {response.status_code}"
                            }
                            logger.warning(f"⚠️ {symbol}: Falha HTTP {response.status_code}")
                            
                    except Exception as e:
                        results[symbol] = {
                            "success": False,
                            "error": str(e)
                        }
                        logger.error(f"❌ {symbol}: {e}")
            
            successful = sum(1 for r in results.values() if r.get("success"))
            logger.info(f"📊 Teste concluído: {successful}/{len(test_symbols)} sucessos")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Erro no teste de coleta: {e}")
            return {}


async def test_direct_yfinance():
    """Testa YFinance diretamente (sem MCP)"""
    try:
        logger.info("🧪 Testando YFinance diretamente...")
        
        import yfinance as yf
        
        test_symbols = ["PETR4.SA", "VALE3.SA", "ITUB4.SA"]
        results = {}
        
        for symbol in test_symbols:
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                
                results[symbol] = {
                    "success": True,
                    "name": info.get("shortName") or info.get("longName"),
                    "price": info.get("regularMarketPrice") or info.get("currentPrice"),
                    "volume": info.get("regularMarketVolume") or info.get("volume"),
                    "market_cap": info.get("marketCap"),
                    "pe_ratio": info.get("trailingPE")
                }
                
                logger.info(f"✅ {symbol}: {results[symbol]['name']} - R$ {results[symbol]['price']}")
                
            except Exception as e:
                results[symbol] = {
                    "success": False,
                    "error": str(e)
                }
                logger.error(f"❌ {symbol}: {e}")
        
        successful = sum(1 for r in results.values() if r.get("success"))
        logger.info(f"📊 Teste YFinance direto: {successful}/{len(test_symbols)} sucessos")
        
        return results
        
    except ImportError:
        logger.error("❌ YFinance não está instalado. Instalando...")
        subprocess.run([sys.executable, "-m", "pip", "install", "yfinance"])
        return await test_direct_yfinance()
    except Exception as e:
        logger.error(f"❌ Erro no teste direto: {e}")
        return {}


async def test_agente_coletor():
    """Testa o Agente Coletor implementado"""
    try:
        logger.info("🧪 Testando Agente Coletor...")
        
        # Import do agente
        sys.path.insert(0, '.')
        from agents.collectors.stock_collector import StockCollectorAgent
        
        # Criar instância
        collector = StockCollectorAgent()
        
        # Testar coleta de algumas ações
        test_stocks = ["PETR4", "VALE3", "ITUB4"]
        
        # Iniciar sessão
        session_id = await collector.start_collection_session(test_stocks)
        logger.info(f"📋 Sessão iniciada: {session_id}")
        
        # Executar coleta via tool
        collect_tool = None
        for tool in collector.tools:
            if tool.name == "collect_stock_data":
                collect_tool = tool
                break
        
        if collect_tool:
            results = await collect_tool(test_stocks)
            await collector.finish_collection_session(results)
            
            logger.info(f"📊 Resultados da coleta:")
            logger.info(f"   Total: {results['total_requested']}")
            logger.info(f"   Sucessos: {results['successful']}")
            logger.info(f"   Falhas: {results['failed']}")
            logger.info(f"   Tempo: {results['processing_time']:.2f}s")
            
            return results
        else:
            logger.error("❌ Tool collect_stock_data não encontrada")
            return {}
            
    except Exception as e:
        logger.error(f"❌ Erro no teste do agente: {e}")
        import traceback
        traceback.print_exc()
        return {}


async def main():
    """Função principal de teste"""
    logger.info("🚀 SETUP E TESTE DO MCP YFINANCE")
    logger.info("=" * 50)
    
    # Opção 1: Testar YFinance diretamente (mais simples)
    logger.info("\n1️⃣ TESTE YFINANCE DIRETO")
    logger.info("-" * 30)
    direct_results = await test_direct_yfinance()
    
    # Opção 2: Testar via MCP (mais avançado)
    logger.info("\n2️⃣ TESTE VIA MCP SERVER")
    logger.info("-" * 30)
    
    mcp_manager = MCPYFinanceManager()
    
    # Instalar MCP se necessário
    if await mcp_manager.install_mcp_yfinance():
        # Tentar iniciar servidor MCP
        if await mcp_manager.start_mcp_server():
            # Testar conexão
            if await mcp_manager.test_mcp_connection():
                # Testar coleta de dados
                mcp_results = await mcp_manager.test_stock_data_retrieval()
            else:
                logger.warning("⚠️ Falha na conexão MCP - usando YFinance direto")
                mcp_results = {}
            
            # Parar servidor
            mcp_manager.stop_mcp_server()
        else:
            logger.warning("⚠️ Falha ao iniciar MCP Server - usando YFinance direto")
            mcp_results = {}
    else:
        logger.warning("⚠️ Falha na instalação MCP - usando YFinance direto")
        mcp_results = {}
    
    # Opção 3: Testar Agente Coletor completo
    logger.info("\n3️⃣ TESTE AGENTE COLETOR")
    logger.info("-" * 30)
    agent_results = await test_agente_coletor()
    
    # Resumo final
    logger.info("\n📊 RESUMO DOS TESTES")
    logger.info("=" * 50)
    
    direct_success = sum(1 for r in direct_results.values() if r.get("success", False))
    logger.info(f"YFinance Direto: {direct_success}/3 sucessos")
    
    if mcp_results:
        mcp_success = sum(1 for r in mcp_results.values() if r.get("success", False))
        logger.info(f"MCP Server: {mcp_success}/3 sucessos")
    else:
        logger.info("MCP Server: Não testado")
    
    if agent_results:
        logger.info(f"Agente Coletor: {agent_results.get('successful', 0)}/3 sucessos")
    else:
        logger.info("Agente Coletor: Falha no teste")
    
    # Recomendação
    logger.info("\n💡 RECOMENDAÇÃO")
    logger.info("-" * 30)
    
    if direct_success >= 2:
        logger.info("✅ YFinance funcionando - Agente pode usar conexão direta")
        logger.info("🔧 Configure o agente para usar YFinance diretamente")
    elif mcp_results and sum(1 for r in mcp_results.values() if r.get("success", False)) >= 2:
        logger.info("✅ MCP Server funcionando - Use conexão MCP")
        logger.info("🔧 Configure o agente para usar MCP Server")
    else:
        logger.warning("⚠️ Problemas detectados - Verifique configuração de rede")
        logger.info("🔧 Possíveis soluções:")
        logger.info("   1. Verificar conexão com internet")
        logger.info("   2. Configurar proxy se necessário")
        logger.info("   3. Usar dados simulados para desenvolvimento")
    
    return {
        "direct_yfinance": direct_results,
        "mcp_server": mcp_results,
        "agente_coletor": agent_results
    }


if __name__ == "__main__":
    asyncio.run(main())
