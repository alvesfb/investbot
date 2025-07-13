# agents/collectors/enhanced_yfinance_client.py
"""
Cliente YFinance Expandido para Coleta de Dados Fundamentalistas
Extensão do cliente original com capacidades avançadas de coleta
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
import httpx
import yfinance as yf
import pandas as pd
from dataclasses import asdict

from utils.financial_calculator import FinancialData
try:
    from config.settings import get_settings
    settings = get_settings()
    # Fallback para timeout se não existir na configuração
    YFINANCE_TIMEOUT = getattr(settings, 'yfinance_timeout', 30)
except (ImportError, AttributeError):
    # Valores padrão caso não consiga carregar settings
    YFINANCE_TIMEOUT = 30

logger = logging.getLogger(__name__)


class DataValidator:
    """Validador de dados financeiros"""
    
    @staticmethod
    def validate_financial_data(data: FinancialData) -> Dict[str, Any]:
        """Valida dados financeiros e retorna relatório de qualidade"""
        validation_report = {
            "valid": True,
            "warnings": [],
            "errors": [],
            "completeness": 0.0,
            "quality_score": 0.0
        }
        
        # Campos obrigatórios
        required_fields = ['current_price', 'market_cap', 'revenue', 'net_income']
        missing_required = []
        
        for field in required_fields:
            value = getattr(data, field)
            if value is None or (isinstance(value, (int, float)) and value <= 0):
                missing_required.append(field)
        
        if missing_required:
            validation_report["errors"].append(f"Campos obrigatórios ausentes: {missing_required}")
            validation_report["valid"] = False
        
        # Validações de consistência
        if data.market_cap and data.current_price and data.shares_outstanding:
            expected_market_cap = data.current_price * data.shares_outstanding
            difference = abs(data.market_cap - expected_market_cap) / data.market_cap
            if difference > 0.1:  # 10% de diferença
                validation_report["warnings"].append("Market cap inconsistente com preço × ações")
        
        # Calcular completude
        all_fields = len(FinancialData.__dataclass_fields__)
        filled_fields = sum(1 for field_name in FinancialData.__dataclass_fields__
                           if getattr(data, field_name) is not None)
        validation_report["completeness"] = filled_fields / all_fields
        
        # Score de qualidade
        validation_report["quality_score"] = DataValidator.calculate_data_quality_score(data)
        
        return validation_report
    
    @staticmethod
    def calculate_data_quality_score(data: FinancialData) -> float:
        """Calcula score de qualidade dos dados (0-100)"""
        score = 0
        max_score = 0
        
        # Dados básicos (peso 40%)
        basic_fields = ['current_price', 'market_cap', 'revenue', 'net_income']
        basic_score = sum(1 for field in basic_fields 
                         if getattr(data, field) is not None) / len(basic_fields)
        score += basic_score * 40
        max_score += 40
        
        # Dados de balanço (peso 30%)
        balance_fields = ['total_assets', 'shareholders_equity', 'total_debt']
        balance_score = sum(1 for field in balance_fields 
                           if getattr(data, field) is not None) / len(balance_fields)
        score += balance_score * 30
        max_score += 30
        
        # Dados históricos (peso 20%)
        history_score = 0
        if data.revenue_history and len(data.revenue_history) >= 3:
            history_score += 0.5
        if data.net_income_history and len(data.net_income_history) >= 3:
            history_score += 0.5
        score += history_score * 20
        max_score += 20
        
        # Metadados (peso 10%)
        meta_score = 0
        if data.sector:
            meta_score += 0.5
        if data.last_updated and (datetime.now() - data.last_updated).days < 7:
            meta_score += 0.5
        score += meta_score * 10
        max_score += 10
        
        return (score / max_score) * 100 if max_score > 0 else 0


class EnhancedYFinanceClient:
    """Cliente YFinance expandido com dados fundamentalistas"""
    
    def __init__(self):
        self.timeout = YFINANCE_TIMEOUT
        self.session = None
        self.cache = {}
        self.cache_ttl = 3600  # 1 hora
        
    async def __aenter__(self):
        """Context manager entry"""
        self.session = httpx.AsyncClient(timeout=self.timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self.session:
            await self.session.aclose()
    
    async def get_comprehensive_stock_data(self, symbol: str) -> FinancialData:
        """
        Coleta dados abrangentes de uma ação incluindo fundamentals
        
        Args:
            symbol: Código da ação (ex: 'PETR4')
            
        Returns:
            FinancialData: Estrutura completa com todos os dados disponíveis
        """
        try:
            # Normalizar símbolo
            if not symbol.endswith('.SA'):
                symbol = f"{symbol}.SA"
            
            logger.info(f"Coletando dados abrangentes para {symbol}")
            
            # Verificar cache
            cache_key = f"comprehensive_{symbol}"
            if self._is_cached(cache_key):
                logger.debug(f"Usando dados em cache para {symbol}")
                return self.cache[cache_key]['data']
            
            # Criar ticker
            ticker = yf.Ticker(symbol)
            
            # Coletar dados básicos
            info = ticker.info
            if not info:
                raise ValueError(f"Dados não disponíveis para {symbol}")
            
            # Coletar dados históricos
            hist_prices = ticker.history(period="1d")
            
            # Coletar demonstrações financeiras
            financials = self._get_financial_statements(ticker)
            
            # Coletar dados históricos para crescimento
            historical_data = self._get_historical_fundamentals(ticker)
            
            # Construir objeto FinancialData
            financial_data = self._build_financial_data(
                symbol, info, hist_prices, financials, historical_data
            )
            
            # Cache dos dados
            self._cache_data(cache_key, financial_data)
            
            return financial_data
            
        except Exception as e:
            logger.error(f"Erro ao coletar dados para {symbol}: {e}")
            return self._create_empty_financial_data(symbol)
    
    async def get_batch_stock_data(self, symbols: List[str], max_concurrent: int = 5) -> Dict[str, FinancialData]:
        """
        Coleta dados de múltiplas ações em paralelo
        
        Args:
            symbols: Lista de códigos de ações
            max_concurrent: Máximo de requisições simultâneas
            
        Returns:
            Dict com dados de cada ação
        """
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def fetch_single(symbol: str) -> Tuple[str, FinancialData]:
            async with semaphore:
                data = await self.get_comprehensive_stock_data(symbol)
                return symbol, data
        
        tasks = [fetch_single(symbol) for symbol in symbols]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        batch_data = {}
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Erro na coleta em lote: {result}")
                continue
            symbol, data = result
            batch_data[symbol] = data
        
        return batch_data
    
    async def get_sector_data(self, sector_symbols: List[str]) -> Dict[str, Any]:
        """
        Coleta dados setoriais para benchmarking
        
        Args:
            sector_symbols: Lista de símbolos do setor
            
        Returns:
            Estatísticas agregadas do setor
        """
        sector_data = await self.get_batch_stock_data(sector_symbols)
        
        # Calcular métricas agregadas
        sector_metrics = self._calculate_sector_metrics(sector_data)
        
        return sector_metrics
    
    def _get_financial_statements(self, ticker) -> Dict[str, pd.DataFrame]:
        """Coleta demonstrações financeiras"""
        try:
            statements = {
                'income_statement': ticker.financials,
                'balance_sheet': ticker.balance_sheet,
                'cash_flow': ticker.cashflow
            }
            
            # Verificar se dados foram coletados
            for name, df in statements.items():
                if df.empty:
                    logger.warning(f"Demonstração {name} vazia")
            
            return statements
            
        except Exception as e:
            logger.warning(f"Erro ao coletar demonstrações financeiras: {e}")
            return {
                'income_statement': pd.DataFrame(),
                'balance_sheet': pd.DataFrame(),
                'cash_flow': pd.DataFrame()
            }
    
    def _get_historical_fundamentals(self, ticker) -> Dict[str, List[float]]:
        """Coleta dados históricos fundamentais"""
        try:
            historical = {
                'revenue_history': [],
                'net_income_history': []
            }
            
            # Tentar coletar dados dos últimos 5 anos
            financials = ticker.financials
            if not financials.empty:
                # Revenue (Total Revenue ou Operating Revenue)
                revenue_keys = ['Total Revenue', 'Operating Revenue', 'Revenue']
                for key in revenue_keys:
                    if key in financials.index:
                        revenue_data = financials.loc[key].dropna()
                        historical['revenue_history'] = revenue_data.tolist()[:5]
                        break
                
                # Net Income
                income_keys = ['Net Income', 'Net Income Common Stockholders']
                for key in income_keys:
                    if key in financials.index:
                        income_data = financials.loc[key].dropna()
                        historical['net_income_history'] = income_data.tolist()[:5]
                        break
            
            return historical
            
        except Exception as e:
            logger.warning(f"Erro ao coletar dados históricos: {e}")
            return {'revenue_history': [], 'net_income_history': []}
    
    def _build_financial_data(self, symbol: str, info: Dict, hist_prices: pd.DataFrame, 
                             financials: Dict[str, pd.DataFrame], 
                             historical: Dict[str, List[float]]) -> FinancialData:
        """Constrói objeto FinancialData a partir dos dados coletados"""
        
        # Dados básicos do info
        current_price = info.get('currentPrice') or info.get('regularMarketPrice')
        if current_price is None and not hist_prices.empty:
            current_price = hist_prices['Close'].iloc[-1]
        
        # Extrair dados das demonstrações
        balance_sheet = financials.get('balance_sheet', pd.DataFrame())
        income_statement = financials.get('income_statement', pd.DataFrame())
        
        # Construir FinancialData
        financial_data = FinancialData(
            # Dados básicos
            current_price=current_price,
            market_cap=info.get('marketCap'),
            shares_outstanding=info.get('sharesOutstanding'),
            
            # Demonstrativo de Resultados
            revenue=self._extract_financial_value(income_statement, ['Total Revenue', 'Revenue']),
            gross_profit=self._extract_financial_value(income_statement, ['Gross Profit']),
            operating_income=self._extract_financial_value(income_statement, ['Operating Income']),
            ebitda=self._extract_financial_value(income_statement, ['EBITDA']),
            net_income=self._extract_financial_value(income_statement, ['Net Income']),
            
            # Balanço Patrimonial
            total_assets=self._extract_financial_value(balance_sheet, ['Total Assets']),
            current_assets=self._extract_financial_value(balance_sheet, ['Current Assets']),
            cash_and_equivalents=self._extract_financial_value(balance_sheet, ['Cash And Cash Equivalents']),
            total_debt=self._extract_financial_value(balance_sheet, ['Total Debt']),
            current_liabilities=self._extract_financial_value(balance_sheet, ['Current Liabilities']),
            shareholders_equity=self._extract_financial_value(balance_sheet, ['Stockholders Equity']),
            
            # Dados históricos
            revenue_history=historical.get('revenue_history', []),
            net_income_history=historical.get('net_income_history', []),
            
            # Metadados
            sector=info.get('sector'),
            industry=info.get('industry'),
            last_updated=datetime.now()
        )
        
        return financial_data
    
    def _extract_financial_value(self, df: pd.DataFrame, keys: List[str]) -> Optional[float]:
        """Extrai valor financeiro do DataFrame"""
        if df.empty:
            return None
            
        for key in keys:
            if key in df.index:
                values = df.loc[key].dropna()
                if not values.empty:
                    return float(values.iloc[0])  # Valor mais recente
        
        return None
    
    def _calculate_sector_metrics(self, sector_data: Dict[str, FinancialData]) -> Dict[str, Any]:
        """Calcula métricas agregadas do setor"""
        from utils.financial_calculator import FinancialCalculator
        
        calculator = FinancialCalculator()
        all_metrics = []
        
        # Calcular métricas para cada empresa
        for symbol, data in sector_data.items():
            if data.market_cap:  # Só processar se tiver dados válidos
                metrics = calculator.calculate_all_metrics(data)
                all_metrics.append(metrics)
        
        if not all_metrics:
            return {}
        
        # Calcular estatísticas agregadas
        sector_stats = {
            'companies_count': len(all_metrics),
            'median_pe': self._calculate_median([m.pe_ratio for m in all_metrics if m.pe_ratio]),
            'median_pb': self._calculate_median([m.pb_ratio for m in all_metrics if m.pb_ratio]),
            'median_roe': self._calculate_median([m.roe for m in all_metrics if m.roe]),
            'median_debt_to_equity': self._calculate_median([m.debt_to_equity for m in all_metrics if m.debt_to_equity]),
            'avg_revenue_growth': self._calculate_average([m.revenue_growth_1y for m in all_metrics if m.revenue_growth_1y])
        }
        
        return sector_stats
    
    def _calculate_median(self, values: List[float]) -> Optional[float]:
        """Calcula mediana de lista de valores"""
        if not values:
            return None
        values.sort()
        n = len(values)
        if n % 2 == 0:
            return (values[n//2 - 1] + values[n//2]) / 2
        return values[n//2]
    
    def _calculate_average(self, values: List[float]) -> Optional[float]:
        """Calcula média de lista de valores"""
        if not values:
            return None
        return sum(values) / len(values)
    
    def _is_cached(self, key: str) -> bool:
        """Verifica se dados estão em cache e são válidos"""
        if key not in self.cache:
            return False
        
        cached_time = self.cache[key]['timestamp']
        return (datetime.now() - cached_time).seconds < self.cache_ttl
    
    def _cache_data(self, key: str, data: FinancialData):
        """Armazena dados no cache"""
        self.cache[key] = {
            'data': data,
            'timestamp': datetime.now()
        }
    
    def _create_empty_financial_data(self, symbol: str) -> FinancialData:
        """Cria FinancialData vazio em caso de erro"""
        return FinancialData(
            sector="Desconhecido",
            last_updated=datetime.now(),
            data_quality_score=0.0
        )
    
    def clear_cache(self):
        """Limpa cache de dados"""
        self.cache.clear()
        logger.info("Cache limpo")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache"""
        return {
            'entries': len(self.cache),
            'oldest_entry': min([v['timestamp'] for v in self.cache.values()]) if self.cache else None,
            'newest_entry': max([v['timestamp'] for v in self.cache.values()]) if self.cache else None
        }


class BatchDataProcessor:
    """Processador de dados em lote com retry e rate limiting"""
    
    def __init__(self, client: EnhancedYFinanceClient):
        self.client = client
        self.max_retries = 3
        self.retry_delay = 1.0
        
    async def process_symbol_list(self, symbols: List[str], 
                                 batch_size: int = 10) -> Dict[str, FinancialData]:
        """Processa lista de símbolos em lotes"""
        results = {}
        
        # Dividir em lotes
        for i in range(0, len(symbols), batch_size):
            batch = symbols[i:i + batch_size]
            logger.info(f"Processando lote {i//batch_size + 1}: {batch}")
            
            # Processar lote com retry
            batch_results = await self._process_batch_with_retry(batch)
            results.update(batch_results)
            
            # Delay entre lotes para evitar rate limiting
            if i + batch_size < len(symbols):
                await asyncio.sleep(1.0)
        
        return results
    
    async def _process_batch_with_retry(self, symbols: List[str]) -> Dict[str, FinancialData]:
        """Processa lote com retry automático"""
        for attempt in range(self.max_retries):
            try:
                return await self.client.get_batch_stock_data(symbols)
            except Exception as e:
                logger.warning(f"Tentativa {attempt + 1} falhou: {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
                else:
                    logger.error(f"Todas as tentativas falharam para lote: {symbols}")
                    return {}


# Funções utilitárias
async def validate_and_collect_stock_data(symbol: str) -> Tuple[FinancialData, Dict[str, Any]]:
    """Coleta dados de ação com validação automática"""
    async with EnhancedYFinanceClient() as client:
        data = await client.get_comprehensive_stock_data(symbol)
        validation = DataValidator.validate_financial_data(data)
        return data, validation


async def collect_sector_benchmark(sector_symbols: List[str]) -> Dict[str, Any]:
    """Coleta benchmark setorial"""
    async with EnhancedYFinanceClient() as client:
        return await client.get_sector_data(sector_symbols)


if __name__ == "__main__":
    # Exemplo de uso
    async def test_client():
        async with EnhancedYFinanceClient() as client:
            # Teste individual
            data = await client.get_comprehensive_stock_data("PETR4")
            validation = DataValidator.validate_financial_data(data)
            
            print(f"Dados coletados para PETR4:")
            print(f"Market Cap: {data.market_cap}")
            print(f"Qualidade: {validation['quality_score']:.1f}")
            
            # Teste em lote
            batch_data = await client.get_batch_stock_data(["PETR4", "VALE3", "ITUB4"])
            print(f"\nLote processado: {len(batch_data)} ações")
    
    # Executar teste
    asyncio.run(test_client())
