"""
DataCollectionTools - Implementação para Agno Framework

Esta tool encapsula o Enhanced YFinance Client e Stock Collector para integração
com o framework Agno, fornecendo coleta de dados robusta e em lote.

Autor: Sistema de Recomendações de Investimentos
Data: 22/07/2025
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List, Union
from datetime import datetime, timedelta

try:
    from agents.collectors.stock_collector import YFinanceClient, StockData
    STOCK_COLLECTOR_AVAILABLE = True
except ImportError:
    STOCK_COLLECTOR_AVAILABLE = False
    logging.warning("StockCollector não disponível - Tool funcionará em modo limitado")

# Enhanced YFinance Client aparentemente não existe ainda
ENHANCED_CLIENT_AVAILABLE = False
SECTOR_SYMBOLS_AVAILABLE = False
SECTOR_SYMBOLS = {}

try:
    from utils.financial_calculator import FinancialData, FinancialCalculator
    CALCULATOR_AVAILABLE = True
except ImportError:
    CALCULATOR_AVAILABLE = False
    logging.warning("FinancialCalculator não disponível")


class DataCollectionTools:
    """
    Tool Agno para Coleta de Dados Financeiros
    
    Encapsula Enhanced YFinance Client + Stock Collector para uso em agentes Agno.
    Fornece coleta robusta de dados de mercado com múltiplas estratégias.
    """
    
    def __init__(self):
        """Inicializa a tool com os coletores disponíveis"""
        self.logger = logging.getLogger(__name__)
        
        # Inicializar coletores se disponíveis
        if STOCK_COLLECTOR_AVAILABLE:
            self.stock_collector = YFinanceClient()
            self.logger.info("Stock Collector inicializado")
        else:
            self.stock_collector = None
            self.logger.warning("Stock Collector não disponível")
        
        # Enhanced Client não existe ainda
        self.enhanced_client = None
        self.logger.info("Enhanced YFinance Client não implementado ainda")
        
        # Cache de sessão para evitar requests desnecessários
        self.session_cache = {}
        self.cache_ttl = 300  # 5 minutos
    
    async def collect_single_stock(self, symbol: str, use_enhanced: bool = True) -> Dict[str, Any]:
        """
        Coleta dados de uma única ação
        
        Args:
            symbol: Código da ação (ex: 'PETR4', 'VALE3')
            use_enhanced: Se deve usar Enhanced Client quando disponível
            
        Returns:
            Dict com dados coletados e metadados
        """
        try:
            start_time = datetime.now()
            
            # Verificar cache primeiro
            cache_key = f"single_{symbol}"
            if self._is_cache_valid(cache_key):
                cached_data = self.session_cache[cache_key]['data']
                cached_data['from_cache'] = True
                return cached_data
            
            # Usar apenas Stock Collector (Enhanced não existe)
            if self.stock_collector:
                self.logger.info(f"Coletando {symbol} via Stock Collector")
                raw_data = await self.stock_collector.get_stock_info(symbol)
                collector_used = "stock_collector"
            else:
                return {
                    "success": False,
                    "error": "Stock Collector não disponível",
                    "symbol": symbol
                }
            
            if not raw_data:
                return {
                    "success": False,
                    "error": "Nenhum dado retornado",
                    "symbol": symbol
                }
            
            # Processar dados coletados
            processed_data = self._process_collected_data(raw_data, symbol)
            
            # Calcular tempo de coleta
            collection_time = (datetime.now() - start_time).total_seconds()
            
            result = {
                "success": True,
                "symbol": symbol,
                "data": processed_data,
                "metadata": {
                    "collection_time": collection_time,
                    "collector_used": collector_used,
                    "timestamp": datetime.now().isoformat(),
                    "data_quality": self._assess_data_quality(processed_data),
                    "from_cache": False
                }
            }
            
            # Salvar no cache
            self._cache_result(cache_key, result)
            
            self.logger.info(f"Dados coletados para {symbol} em {collection_time:.2f}s")
            return result
            
        except Exception as e:
            self.logger.error(f"Erro ao coletar dados para {symbol}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "symbol": symbol,
                "timestamp": datetime.now().isoformat()
            }
    
    async def collect_multiple_stocks(self, symbols: List[str], 
                                    batch_size: int = 5, 
                                    use_enhanced: bool = True) -> Dict[str, Any]:
        """
        Coleta dados de múltiplas ações em lote
        
        Args:
            symbols: Lista de códigos de ações
            batch_size: Tamanho do lote para processamento
            use_enhanced: Se deve usar Enhanced Client quando disponível
            
        Returns:
            Dict com resultados de todas as coletas
        """
        try:
            start_time = datetime.now()
            
            self.logger.info(f"Iniciando coleta em lote: {len(symbols)} ações")
            
            # Dividir em lotes
            batches = [symbols[i:i + batch_size] for i in range(0, len(symbols), batch_size)]
            
            all_results = []
            successful_collections = 0
            failed_collections = 0
            
            for i, batch in enumerate(batches, 1):
                self.logger.info(f"Processando lote {i}/{len(batches)}: {batch}")
                
                # Processar lote em paralelo
                batch_tasks = [
                    self.collect_single_stock(symbol, use_enhanced) 
                    for symbol in batch
                ]
                
                batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
                
                # Processar resultados do lote
                for result in batch_results:
                    if isinstance(result, Exception):
                        failed_collections += 1
                        all_results.append({
                            "success": False,
                            "error": str(result),
                            "symbol": "unknown"
                        })
                    else:
                        all_results.append(result)
                        if result.get("success"):
                            successful_collections += 1
                        else:
                            failed_collections += 1
                
                # Delay entre lotes para evitar rate limiting
                if i < len(batches):
                    await asyncio.sleep(1)
            
            total_time = (datetime.now() - start_time).total_seconds()
            
            return {
                "success": True,
                "total_symbols": len(symbols),
                "successful_collections": successful_collections,
                "failed_collections": failed_collections,
                "success_rate": (successful_collections / len(symbols)) * 100,
                "total_time": total_time,
                "results": all_results,
                "metadata": {
                    "batch_size": batch_size,
                    "total_batches": len(batches),
                    "timestamp": datetime.now().isoformat(),
                    "use_enhanced": use_enhanced
                }
            }
            
        except Exception as e:
            self.logger.error(f"Erro na coleta em lote: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "total_symbols": len(symbols),
                "timestamp": datetime.now().isoformat()
            }
    
    async def collect_sector_data(self, sector: str, limit: Optional[int] = None) -> Dict[str, Any]:
        """
        Coleta dados de todas as empresas de um setor
        
        Args:
            sector: Nome do setor (ex: 'Bancos', 'Petróleo e Gás')
            limit: Limite de empresas a coletar (None = todas)
            
        Returns:
            Dict com dados do setor
        """
        try:
            # Usar apenas mapeamento básico (Enhanced Client não existe)
            sector_symbols = self._get_sector_symbols_fallback(sector)
            
            if not sector_symbols:
                return {
                    "success": False,
                    "error": f"Setor '{sector}' não encontrado ou sem empresas mapeadas",
                    "sector": sector
                }
            
            # Aplicar limite se especificado
            if limit:
                sector_symbols = sector_symbols[:limit]
            
            self.logger.info(f"Coletando dados do setor {sector}: {len(sector_symbols)} empresas")
            
            # Coletar dados do setor
            sector_result = await self.collect_multiple_stocks(sector_symbols, batch_size=3)
            
            if sector_result["success"]:
                # Adicionar análise setorial
                sector_analysis = self._analyze_sector_data(sector_result["results"])
                
                return {
                    "success": True,
                    "sector": sector,
                    "companies_analyzed": len(sector_symbols),
                    "data_collection": sector_result,
                    "sector_analysis": sector_analysis,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return sector_result
                
        except Exception as e:
            self.logger.error(f"Erro ao coletar dados do setor {sector}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "sector": sector,
                "timestamp": datetime.now().isoformat()
            }
    
    async def validate_market_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida qualidade dos dados coletados
        
        Args:
            data: Dados a serem validados
            
        Returns:
            Dict com resultado da validação
        """
        try:
            # Implementar validação básica já que DataValidator não existe
            validation_result = self._basic_data_validation(data)
            
            return {
                "success": True,
                "validation": validation_result,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Erro na validação: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_available_sectors(self) -> Dict[str, Any]:
        """
        Retorna setores disponíveis para coleta
        
        Returns:
            Dict com setores e empresas mapeadas
        """
        try:
            # Usar apenas setores básicos (Enhanced Client não existe)
            basic_sectors = {
                "Bancos": ["ITUB4", "BBDC4", "BBAS3", "SANB4"],
                "Petróleo e Gás": ["PETR4", "PETR3", "PRIO3"],
                "Mineração": ["VALE3", "CSNA3"],
                "Varejo": ["MGLU3", "AMER3", "VVAR3"],
                "Tecnologia": ["TOTS3", "LWSA3"],
                "Utilities": ["ELET3", "ELET6"]
            }
            
            sectors_info = {}
            for sector, symbols in basic_sectors.items():
                sectors_info[sector] = {
                    "companies_count": len(symbols),
                    "sample_companies": symbols[:3],
                    "all_companies": symbols
                }
            
            return {
                "success": True,
                "sectors": sectors_info,
                "total_sectors": len(sectors_info),
                "total_companies": sum(len(symbols) for symbols in basic_sectors.values()),
                "source": "built_in",
                "note": "Usando mapeamento básico integrado"
            }
                
        except Exception as e:
            self.logger.error(f"Erro ao obter setores: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_tool_status(self) -> Dict[str, Any]:
        """
        Retorna status dos componentes da tool
        
        Returns:
            Dict com status dos componentes
        """
        return {
            "tool_name": "DataCollectionTools",
            "version": "1.0.0",
            "components": {
                "stock_collector": {
                    "available": STOCK_COLLECTOR_AVAILABLE,
                    "status": "operational" if STOCK_COLLECTOR_AVAILABLE else "unavailable"
                },
                "enhanced_client": {
                    "available": False,
                    "status": "not_implemented",
                    "note": "Enhanced Client será implementado na próxima fase"
                },
                "financial_calculator": {
                    "available": CALCULATOR_AVAILABLE,
                    "status": "operational" if CALCULATOR_AVAILABLE else "unavailable"
                }
            },
            "capabilities": {
                "single_stock_collection": STOCK_COLLECTOR_AVAILABLE,
                "batch_collection": STOCK_COLLECTOR_AVAILABLE,
                "enhanced_validation": False,  # Não implementado ainda
                "sector_analysis": STOCK_COLLECTOR_AVAILABLE,
                "sector_symbols": True,  # Built-in básico
                "data_caching": True
            },
            "cache_info": {
                "cached_items": len(self.session_cache),
                "cache_ttl_seconds": self.cache_ttl
            },
            "timestamp": datetime.now().isoformat()
        }
    
    # Métodos auxiliares
    
    def _basic_data_validation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validação básica de dados (substituindo DataValidator)"""
        essential_fields = ['current_price', 'market_cap', 'symbol']
        optional_fields = ['pe_ratio', 'pb_ratio', 'roe', 'volume']
        
        # Verificar campos essenciais
        missing_essential = [field for field in essential_fields if not data.get(field)]
        available_optional = [field for field in optional_fields if data.get(field)]
        
        total_fields = len(essential_fields) + len(optional_fields)
        available_fields = len(essential_fields) - len(missing_essential) + len(available_optional)
        completeness = available_fields / total_fields
        
        is_valid = len(missing_essential) == 0
        
        return {
            "valid": is_valid,
            "completeness": completeness,
            "missing_essential": missing_essential,
            "available_optional": available_optional,
            "quality_score": completeness * 100,
            "warnings": [f"Campo essencial faltando: {field}" for field in missing_essential]
        }
    
    def _process_collected_data(self, raw_data: Dict[str, Any], symbol: str) -> Dict[str, Any]:
        """Processa dados coletados para formato padronizado"""
        try:
            # Dados básicos sempre presentes
            processed = {
                "symbol": symbol,
                "name": raw_data.get('longName') or raw_data.get('shortName', symbol),
                "current_price": raw_data.get('regularMarketPrice') or raw_data.get('currentPrice'),
                "market_cap": raw_data.get('marketCap'),
                "volume": raw_data.get('regularMarketVolume') or raw_data.get('volume'),
                "sector": raw_data.get('sector'),
                "industry": raw_data.get('industry'),
                
                # Ratios importantes
                "pe_ratio": raw_data.get('trailingPE'),
                "pb_ratio": raw_data.get('priceToBook'),
                "roe": raw_data.get('returnOnEquity'),
                "dividend_yield": raw_data.get('dividendYield'),
                
                # Dados financeiros (se disponíveis)
                "revenue": raw_data.get('totalRevenue'),
                "net_income": raw_data.get('netIncomeToCommon'),
                "total_assets": raw_data.get('totalAssets'),
                "total_debt": raw_data.get('totalDebt'),
                
                # Metadados
                "currency": raw_data.get('currency', 'BRL'),
                "country": raw_data.get('country', 'Brazil')
            }
            
            # Remover campos None para limpar dados
            return {k: v for k, v in processed.items() if v is not None}
            
        except Exception as e:
            self.logger.warning(f"Erro ao processar dados para {symbol}: {e}")
            return {"symbol": symbol, "raw_data": raw_data}
    
    def _assess_data_quality(self, data: Dict[str, Any]) -> str:
        """Avalia qualidade dos dados coletados"""
        essential_fields = ['current_price', 'market_cap', 'pe_ratio', 'pb_ratio']
        available_fields = sum(1 for field in essential_fields if data.get(field) is not None)
        
        quality_ratio = available_fields / len(essential_fields)
        
        if quality_ratio >= 0.9:
            return "excellent"
        elif quality_ratio >= 0.7:
            return "good" 
        elif quality_ratio >= 0.5:
            return "fair"
        else:
            return "poor"
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Verifica se cache é válido"""
        if cache_key not in self.session_cache:
            return False
        
        cache_time = self.session_cache[cache_key]['timestamp']
        return (datetime.now() - cache_time).total_seconds() < self.cache_ttl
    
    def _cache_result(self, cache_key: str, result: Dict[str, Any]):
        """Salva resultado no cache"""
        self.session_cache[cache_key] = {
            'data': result,
            'timestamp': datetime.now()
        }
    
    def _get_sector_symbols_fallback(self, sector: str) -> List[str]:
        """Mapeamento básico integrado de símbolos setoriais"""
        sector_mapping = {
            "Bancos": ["ITUB4", "BBDC4", "BBAS3", "SANB4"],
            "Petróleo e Gás": ["PETR4", "PETR3", "PRIO3"],
            "Mineração": ["VALE3", "CSNA3"],
            "Varejo": ["MGLU3", "AMER3", "VVAR3"],
            "Tecnologia": ["TOTS3", "LWSA3"],
            "Utilities": ["ELET3", "ELET6"]
        }
        
        return sector_mapping.get(sector, [])
    
    def _analyze_sector_data(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Análise básica dos dados setoriais"""
        try:
            successful_results = [r for r in results if r.get("success") and r.get("data")]
            
            if not successful_results:
                return {"error": "Nenhum dado válido para análise"}
            
            # Extrair métricas
            prices = []
            market_caps = []
            pe_ratios = []
            
            for result in successful_results:
                data = result["data"]
                if data.get("current_price"):
                    prices.append(data["current_price"])
                if data.get("market_cap"):
                    market_caps.append(data["market_cap"])
                if data.get("pe_ratio"):
                    pe_ratios.append(data["pe_ratio"])
            
            analysis = {
                "companies_analyzed": len(successful_results),
                "data_quality": {
                    "with_price": len(prices),
                    "with_market_cap": len(market_caps), 
                    "with_pe_ratio": len(pe_ratios)
                }
            }
            
            # Estatísticas básicas
            if prices:
                analysis["price_stats"] = {
                    "avg": sum(prices) / len(prices),
                    "min": min(prices),
                    "max": max(prices)
                }
            
            if market_caps:
                total_market_cap = sum(market_caps)
                analysis["market_cap_stats"] = {
                    "total": total_market_cap,
                    "avg": total_market_cap / len(market_caps),
                    "largest_company": max(market_caps)
                }
            
            if pe_ratios:
                analysis["pe_stats"] = {
                    "avg": sum(pe_ratios) / len(pe_ratios),
                    "median": sorted(pe_ratios)[len(pe_ratios) // 2]
                }
            
            return analysis
            
        except Exception as e:
            return {"error": f"Erro na análise setorial: {str(e)}"}


# Factory function para compatibilidade com Agno
def create_data_collection_tools() -> DataCollectionTools:
    """Factory function para criar instância da tool"""
    return DataCollectionTools()


# Exemplo de uso direto (para testes)
if __name__ == "__main__":
    async def test_data_collection_tools():
        print("📡 Testando DataCollectionTools")
        print("=" * 50)
        
        # Criar instância
        tools = create_data_collection_tools()
        
        # Verificar status
        status = tools.get_tool_status()
        print(f"📊 STATUS DA TOOL:")
        print(f"   Stock Collector disponível: {status['components']['stock_collector']['available']}")
        print(f"   Enhanced Client disponível: {status['components']['enhanced_client']['available']}")
        print(f"   Coleta individual: {status['capabilities']['single_stock_collection']}")
        print(f"   Coleta em lote: {status['capabilities']['batch_collection']}")
        
        # Testar coleta individual
        if status['capabilities']['single_stock_collection']:
            print(f"\n🎯 TESTANDO COLETA INDIVIDUAL:")
            result = await tools.collect_single_stock('PETR4')
            
            if result['success']:
                data = result['data']
                print(f"   ✅ Dados coletados para {data.get('symbol')}")
                print(f"   📈 Preço: R$ {data.get('current_price', 'N/A')}")
                print(f"   💰 Market Cap: R$ {data.get('market_cap', 'N/A'):,.0f}" if data.get('market_cap') else "   💰 Market Cap: N/A")
                print(f"   ⏱️ Tempo: {result['metadata']['collection_time']:.2f}s")
                print(f"   🎯 Qualidade: {result['metadata']['data_quality']}")
            else:
                print(f"   ❌ Falha: {result.get('error')}")
        
        # Testar setores disponíveis
        print(f"\n🏭 SETORES DISPONÍVEIS:")
        sectors = tools.get_available_sectors()
        if sectors['success']:
            for sector, info in sectors['sectors'].items():
                print(f"   • {sector}: {info['companies_count']} empresas")
        
        print(f"\n✅ DataCollectionTools testada com sucesso!")
    
    asyncio.run(test_data_collection_tools())