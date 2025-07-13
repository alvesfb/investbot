# agents/collectors/stock_collector.py
"""
Agente Coletor de Dados de Ações usando Agno Framework + MCP YFinance
"""
import asyncio
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from agno.agent import Agent
from agno.agent.tools import Tool
import httpx

from config.settings import get_settings, get_agent_settings
from database.repositories import (get_stock_repository,
                                   get_agent_session_repository)

# Configurar logging
logger = logging.getLogger(__name__)

settings = get_settings()
agent_settings = get_agent_settings()


@dataclass
class StockData:
    """Estrutura para dados de ação coletados"""
    codigo: str
    nome: str
    preco_atual: float
    volume_medio: float
    market_cap: Optional[float] = None
    p_l: Optional[float] = None
    p_vp: Optional[float] = None
    roe: Optional[float] = None
    roic: Optional[float] = None
    setor: Optional[str] = None
    descricao: Optional[str] = None
    website: Optional[str] = None
    erro: Optional[str] = None


class YFinanceClient:
    """Cliente para comunicação com YFinance via HTTP"""

    def __init__(self):
        self.base_url = "https://query1.finance.yahoo.com/v1"
        self.timeout = settings.yfinance_timeout

    async def get_stock_info(self, symbol: str) -> Dict[str, Any]:
        """Busca informações de uma ação no YFinance"""
        try:
            # Adicionar sufixo .SA para ações brasileiras
            if not symbol.endswith('.SA'):
                symbol = f"{symbol}.SA"

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Quote básico
                quote_url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
                response = await client.get(quote_url)
                response.raise_for_status()

                data = response.json()

                if not data.get('chart', {}).get('result'):
                    raise ValueError(f"Dados não encontrados para {symbol}")

                result = data['chart']['result'][0]
                meta = result.get('meta', {})
                
                # Dados básicos sempre disponíveis
                stock_data = {
                    'symbol': symbol,
                    'regularMarketPrice': meta.get('regularMarketPrice', 0),
                    'regularMarketVolume': meta.get('regularMarketVolume', 0),
                    'marketCap': meta.get('marketCap'),
                    'currency': meta.get('currency', 'BRL'),
                    'exchangeName': meta.get('exchangeName'),
                    'longName': meta.get('longName'),
                    'shortName': meta.get('shortName')
                }
                
                # Tentar buscar dados fundamentalistas adicionais
                try:
                    await self._enrich_fundamental_data(client, symbol, stock_data)
                except Exception as e:
                    logger.warning(f"Não foi possível obter dados fundamentais para {symbol}: {e}")
                
                return stock_data
                
        except Exception as e:
            logger.error(f"Erro ao buscar dados para {symbol}: {e}")
            raise
    
    async def _enrich_fundamental_data(self, client: httpx.AsyncClient, 
                                     symbol: str, stock_data: Dict[str, Any]):
        """Tenta enriquecer com dados fundamentalistas"""
        try:
            # URL para dados de estatísticas
            stats_url = f"https://query1.finance.yahoo.com/v10/finance/quoteSummary/{symbol}"
            params = {
                'modules': 'summaryDetail,financialData,defaultKeyStatistics'
            }
            
            response = await client.get(stats_url, params=params)
            if response.status_code == 200:
                data = response.json()
                result = data.get('quoteSummary', {}).get('result')
                
                if result and len(result) > 0:
                    modules = result[0]
                    
                    # Summary Detail
                    summary = modules.get('summaryDetail', {})
                    if summary:
                        stock_data.update({
                            'trailingPE': self._safe_get_value(summary.get('trailingPE')),
                            'priceToBook': self._safe_get_value(summary.get('priceToBook')),
                            'marketCap': self._safe_get_value(summary.get('marketCap'))
                        })
                    
                    # Financial Data
                    financial = modules.get('financialData', {})
                    if financial:
                        stock_data.update({
                            'returnOnEquity': self._safe_get_value(financial.get('returnOnEquity')),
                            'returnOnAssets': self._safe_get_value(financial.get('returnOnAssets')),
                            'debtToEquity': self._safe_get_value(financial.get('debtToEquity'))
                        })
                    
                    # Key Statistics
                    key_stats = modules.get('defaultKeyStatistics', {})
                    if key_stats:
                        stock_data.update({
                            'enterpriseValue': self._safe_get_value(key_stats.get('enterpriseValue')),
                            'priceToSalesTrailing12Months': self._safe_get_value(key_stats.get('priceToSalesTrailing12Months'))
                        })
                        
        except Exception as e:
            logger.debug(f"Falha ao obter dados fundamentais para {symbol}: {e}")
    
    def _safe_get_value(self, data_obj: Any) -> Optional[float]:
        """Extrai valor de objeto YFinance de forma segura"""
        if data_obj is None:
            return None
        
        if isinstance(data_obj, dict):
            return data_obj.get('raw')
        
        if isinstance(data_obj, (int, float)):
            return float(data_obj)
        
        return None


class StockCollectorAgent(Agent):
    """Agente Coletor de Dados de Ações"""
    
    def __init__(self):
        super().__init__(
            name="StockCollector",
            description="Agente especializado em coletar dados de ações brasileiras via YFinance",
            version="1.0.0"
        )
        
        self.yfinance_client = YFinanceClient()
        self.stock_repo = get_stock_repository()
        self.session_repo = get_agent_session_repository()
        self.session_id = None
        
        # Registrar tools
        self._register_tools()
    
    def _register_tools(self):
        """Registra as ferramentas do agente"""
        
        @Tool(name="collect_stock_data")
        async def collect_stock_data(stock_codes: List[str]) -> Dict[str, Any]:
            """
            Coleta dados de uma lista de códigos de ações
            
            Args:
                stock_codes: Lista de códigos de ações (ex: ['PETR4', 'VALE3'])
            
            Returns:
                Dict com resultados da coleta
            """
            return await self._collect_multiple_stocks(stock_codes)
        
        @Tool(name="update_stock_price")
        async def update_stock_price(codigo: str) -> Dict[str, Any]:
            """
            Atualiza apenas o preço de uma ação específica
            
            Args:
                codigo: Código da ação (ex: 'PETR4')
            
            Returns:
                Dict com resultado da atualização
            """
            return await self._update_single_stock_price(codigo)
        
        @Tool(name="collect_all_active_stocks")
        async def collect_all_active_stocks() -> Dict[str, Any]:
            """
            Coleta dados de todas as ações ativas no banco
            
            Returns:
                Dict com resultados da coleta completa
            """
            active_stocks = self.stock_repo.get_all_stocks(ativo_apenas=True)
            stock_codes = [stock.codigo for stock in active_stocks]
            return await self._collect_multiple_stocks(stock_codes)
        
        self.tools.extend([collect_stock_data, update_stock_price, collect_all_active_stocks])
    
    async def _collect_multiple_stocks(self, stock_codes: List[str]) -> Dict[str, Any]:
        """Coleta dados de múltiplas ações"""
        logger.info(f"Iniciando coleta de {len(stock_codes)} ações")
        
        results = {
            "total_requested": len(stock_codes),
            "successful": 0,
            "failed": 0,
            "updated_stocks": [],
            "failed_stocks": [],
            "processing_time": 0
        }
        
        start_time = datetime.now()
        
        # Processar em lotes para evitar rate limiting
        batch_size = agent_settings.collector_batch_size
        
        for i in range(0, len(stock_codes), batch_size):
            batch = stock_codes[i:i + batch_size]
            logger.info(f"Processando lote {i//batch_size + 1}: {batch}")
            
            # Processar lote
            for codigo in batch:
                try:
                    stock_data = await self._collect_single_stock(codigo)
                    if stock_data and not stock_data.erro:
                        self._update_stock_in_database(stock_data)
                        results["successful"] += 1
                        results["updated_stocks"].append({
                            "codigo": codigo,
                            "preco": stock_data.preco_atual,
                            "volume": stock_data.volume_medio
                        })
                    else:
                        results["failed"] += 1
                        results["failed_stocks"].append({
                            "codigo": codigo,
                            "erro": stock_data.erro if stock_data else "Erro desconhecido"
                        })
                        
                except Exception as e:
                    logger.error(f"Erro ao processar {codigo}: {e}")
                    results["failed"] += 1
                    results["failed_stocks"].append({
                        "codigo": codigo,
                        "erro": str(e)
                    })
            
            # Delay entre lotes para evitar rate limiting
            if i + batch_size < len(stock_codes):
                await asyncio.sleep(1)
        
        results["processing_time"] = (datetime.now() - start_time).total_seconds()
        logger.info(f"Coleta concluída: {results['successful']} sucessos, {results['failed']} falhas")
        
        return results
    
    async def _collect_single_stock(self, codigo: str) -> Optional[StockData]:
        """Coleta dados de uma única ação"""
        try:
            logger.debug(f"Coletando dados para {codigo}")
            
            # Buscar dados no YFinance
            yf_data = await self.yfinance_client.get_stock_info(codigo)
            
            # Converter para StockData
            stock_data = StockData(
                codigo=codigo,
                nome=yf_data.get('longName') or yf_data.get('shortName') or codigo,
                preco_atual=yf_data.get('regularMarketPrice', 0),
                volume_medio=yf_data.get('regularMarketVolume', 0),
                market_cap=yf_data.get('marketCap'),
                p_l=yf_data.get('trailingPE'),
                p_vp=yf_data.get('priceToBook'),
                roe=yf_data.get('returnOnEquity'),
                roic=None,  # YFinance não tem ROIC direto
                setor=None,  # Seria necessário API adicional
                descricao=None,
                website=None
            )
            
            return stock_data
            
        except Exception as e:
            logger.error(f"Erro ao coletar dados para {codigo}: {e}")
            return StockData(
                codigo=codigo,
                nome="",
                preco_atual=0,
                volume_medio=0,
                erro=str(e)
            )
    
    async def _update_single_stock_price(self, codigo: str) -> Dict[str, Any]:
        """Atualiza apenas o preço de uma ação"""
        try:
            stock_data = await self._collect_single_stock(codigo)
            
            if stock_data and not stock_data.erro:
                # Atualizar apenas preço e volume
                success = self.stock_repo.update_stock_price(
                    codigo, 
                    stock_data.preco_atual, 
                    stock_data.volume_medio
                )
                
                return {
                    "codigo": codigo,
                    "success": success,
                    "preco_atual": stock_data.preco_atual,
                    "volume_medio": stock_data.volume_medio,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "codigo": codigo,
                    "success": False,
                    "erro": stock_data.erro if stock_data else "Erro desconhecido"
                }
                
        except Exception as e:
            return {
                "codigo": codigo,
                "success": False,
                "erro": str(e)
            }
    
    def _update_stock_in_database(self, stock_data: StockData):
        """Atualiza ou cria ação no banco de dados"""
        try:
            # Verificar se ação já existe
            existing_stock = self.stock_repo.get_stock_by_code(stock_data.codigo)
            
            if existing_stock:
                # Atualizar dados de mercado
                fundamentals = {}
                if stock_data.p_l is not None:
                    fundamentals['p_l'] = stock_data.p_l
                if stock_data.p_vp is not None:
                    fundamentals['p_vp'] = stock_data.p_vp
                if stock_data.roe is not None:
                    fundamentals['roe'] = stock_data.roe
                if stock_data.market_cap is not None:
                    fundamentals['market_cap'] = stock_data.market_cap
                
                # Atualizar preço
                self.stock_repo.update_stock_price(
                    stock_data.codigo, 
                    stock_data.preco_atual, 
                    stock_data.volume_medio
                )
                
                # Atualizar fundamentals se tiver
                if fundamentals:
                    self.stock_repo.update_stock_fundamentals(
                        stock_data.codigo, fundamentals)
                
                logger.debug(f"Ação atualizada: {stock_data.codigo}")
            else:
                # Criar nova ação
                new_stock_data = {
                    "codigo": stock_data.codigo,
                    "nome": stock_data.nome,
                    "preco_atual": stock_data.preco_atual,
                    "volume_medio": stock_data.volume_medio,
                    "market_cap": stock_data.market_cap,
                    "p_l": stock_data.p_l,
                    "p_vp": stock_data.p_vp,
                    "roe": stock_data.roe,
                    "setor": stock_data.setor or "Não classificado",
                    "descricao": stock_data.descricao,
                    "website": stock_data.website,
                    "ativo": True
                }
                
                self.stock_repo.create_stock(new_stock_data)
                logger.info(f"Nova ação criada: {stock_data.codigo}")
                
        except Exception as e:
            logger.error(f"Erro ao salvar {stock_data.codigo} no banco: {e}")
            raise
    
    async def start_collection_session(self, stock_codes: List[str] = None) -> str:
        """Inicia uma sessão de coleta de dados"""
        session_data = {
            "session_id": f"collect_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "agent_name": self.name,
            "agent_version": self.version,
            "status": "running",
            "input_data": json.dumps({
                "stock_codes": stock_codes or "all_active",
                "timestamp": datetime.now().isoformat()
            }),
            "stocks_processed": 0
        }
        
        session = self.session_repo.create_session(session_data)
        self.session_id = session.session_id
        
        logger.info(f"Sessão de coleta iniciada: {self.session_id}")
        return self.session_id
    
    async def finish_collection_session(self, results: Dict[str, Any]):
        """Finaliza sessão de coleta"""
        if self.session_id:
            output_data = {
                "results": results,
                "timestamp": datetime.now().isoformat()
            }
            
            self.session_repo.update_session(self.session_id, {
                "output_data": json.dumps(output_data),
                "stocks_processed": results.get("successful", 0),
                "execution_time_seconds": results.get("processing_time", 0)
            })
            
            status = "completed" if results.get("failed", 0) == 0 else "partial_failure"
            self.session_repo.finish_session(self.session_id, status)
            
            logger.info(f"Sessão finalizada: {self.session_id} - Status: {status}")


# Função principal para uso standalone
async def main():
    """Função principal para execução standalone"""
    collector = StockCollectorAgent()
    
    # Exemplo de uso
    test_stocks = ["PETR4", "VALE3", "ITUB4"]
    
    session_id = await collector.start_collection_session(test_stocks)
    print(f"Sessão iniciada: {session_id}")
    
    # Executar coleta
    tool = collector.tools[0]  # collect_stock_data
    results = await tool(test_stocks)
    
    await collector.finish_collection_session(results)
    
    print("Resultados:")
    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(main())
