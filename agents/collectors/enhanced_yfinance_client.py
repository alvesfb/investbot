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
from config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class EnhancedYFinanceClient:
    """Cliente YFinance expandido com dados fundamentalistas"""
    
    def __init__(self):
        self.timeout = settings.yfinance_timeout
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
            financials = await self._get_financial_statements(ticker)
            balance_sheet = await self._get_balance_sheet(ticker)
            cash_flow = await self._get_cash_flow(ticker)
            
            # Coletar dados históricos de crescimento
            historical_data = await self._get_historical_growth_data(ticker)
            
            # Construir FinancialData
            financial_data = self._build_financial_data(
                info, hist_prices, financials, balance_sheet, 
                cash_flow, historical_data, symbol
            )
            
            # Cachear resultado
            self._cache_data(cache_key, financial_data)
            
            logger.info(f"Dados coletados com sucesso para {symbol}")
            return financial_data
            
        except Exception as e:
            logger.error(f"Erro ao coletar dados para {symbol}: {e}")
            # Retornar estrutura vazia em caso de erro
            return FinancialData()
    
    async def _get_financial_statements(self, ticker: yf.Ticker) -> Optional[pd.DataFrame]:
        """Coleta demonstrações financeiras (DRE)"""
        try:
            financials = ticker.financials
            return financials if not financials.empty else None
        except Exception as e:
            logger.warning(f"Erro ao coletar DRE: {e}")
            return None
    
    async def _get_balance_sheet(self, ticker: yf.Ticker) -> Optional[pd.DataFrame]:
        """Coleta balanço patrimonial"""
        try:
            balance = ticker.balance_sheet
            return balance if not balance.empty else None
        except Exception as e:
            logger.warning(f"Erro ao coletar balanço: {e}")
            return None
    
    async def _get_cash_flow(self, ticker: yf.Ticker) -> Optional[pd.DataFrame]:
        """Coleta demonstração de fluxo de caixa"""
        try:
            cash_flow = ticker.cashflow
            return cash_flow if not cash_flow.empty else None
        except Exception as e:
            logger.warning(f"Erro ao coletar fluxo de caixa: {e}")
            return None
    
    async def _get_historical_growth_data(self, ticker: yf.Ticker) -> Dict[str, List[float]]:
        """Coleta dados históricos para cálculo de crescimento"""
        historical_data = {
            "revenue": [],
            "net_income": [],
            "roe": []
        }
        
        try:
            # Tentar obter dados dos últimos 5 anos
            financials = ticker.financials
            balance = ticker.balance_sheet
            
            if not financials.empty and not balance.empty:
                # Ordenar por data (mais recente primeiro)
                financials = financials.sort_index(axis=1, ascending=False)
                balance = balance.sort_index(axis=1, ascending=False)
                
                # Extrair receita dos últimos anos
                for col in financials.columns:
                    try:
                        # Revenue (Total Revenue ou Total Revenue)
                        revenue = None
                        for revenue_key in ['Total Revenue', 'Total Operating Revenue', 'Revenue']:
                            if revenue_key in financials.index:
                                revenue = financials.loc[revenue_key, col]
                                break
                        
                        if revenue and pd.notna(revenue) and revenue > 0:
                            historical_data["revenue"].append(float(revenue))
                        
                        # Net Income
                        net_income = None
                        for income_key in ['Net Income', 'Net Income Common Stockholders']:
                            if income_key in financials.index:
                                net_income = financials.loc[income_key, col]
                                break
                        
                        if net_income and pd.notna(net_income):
                            historical_data["net_income"].append(float(net_income))
                        
                        # ROE (calcular se tiver net income e equity)
                        if net_income and pd.notna(net_income) and col in balance.columns:
                            equity = None
                            for equity_key in ['Total Stockholder Equity', 'Stockholders Equity', 'Total Equity']:
                                if equity_key in balance.index:
                                    equity = balance.loc[equity_key, col]
                                    break
                            
                            if equity and pd.notna(equity) and equity > 0:
                                roe = (float(net_income) / float(equity)) * 100
                                historical_data["roe"].append(roe)
                                
                    except Exception as e:
                        logger.debug(f"Erro ao processar dados históricos da coluna {col}: {e}")
                        continue
                
                # Limitar a 5 anos e reverter ordem (mais antigo primeiro)
                for key in historical_data:
                    historical_data[key] = list(reversed(historical_data[key][-5:]))
                    
        except Exception as e:
            logger.warning(f"Erro ao coletar dados históricos: {e}")
        
        return historical_data
    
    def _build_financial_data(self, info: Dict[str, Any], hist_prices: pd.DataFrame,
                            financials: Optional[pd.DataFrame], balance: Optional[pd.DataFrame],
                            cash_flow: Optional[pd.DataFrame], historical_data: Dict[str, List[float]],
                            symbol: str) -> FinancialData:
        """Constrói estrutura FinancialData a partir dos dados coletados"""
        
        data = FinancialData()
        
        try:
            # Dados básicos de mercado
            data.market_cap = self._safe_get(info, 'marketCap')
            data.enterprise_value = self._safe_get(info, 'enterpriseValue')
            data.shares_outstanding = self._safe_get(info, 'sharesOutstanding')
            
            # Preço atual
            if not hist_prices.empty:
                data.current_price = float(hist_prices['Close'].iloc[-1])
            else:
                data.current_price = self._safe_get(info, 'regularMarketPrice')
            
            # Dados do balanço patrimonial
            if balance is not None and not balance.empty:
                latest_balance = balance.iloc[:, 0]  # Coluna mais recente
                
                data.total_assets = self._safe_get_from_series(latest_balance, 
                    ['Total Assets', 'Total Asset'])
                
                data.total_equity = self._safe_get_from_series(latest_balance,
                    ['Total Stockholder Equity', 'Stockholders Equity', 'Total Equity'])
                
                data.total_debt = self._safe_get_from_series(latest_balance,
                    ['Total Debt', 'Long Term Debt', 'Short Long Term Debt'])
                
                data.current_assets = self._safe_get_from_series(latest_balance,
                    ['Current Assets', 'Total Current Assets'])
                
                data.current_liabilities = self._safe_get_from_series(latest_balance,
                    ['Current Liabilities', 'Total Current Liabilities'])
                
                data.cash_and_equivalents = self._safe_get_from_series(latest_balance,
                    ['Cash And Cash Equivalents', 'Cash', 'Cash And Short Term Investments'])
            
            # Dados da DRE
            if financials is not None and not financials.empty:
                latest_financials = financials.iloc[:, 0]  # Coluna mais recente
                
                data.revenue = self._safe_get_from_series(latest_financials,
                    ['Total Revenue', 'Total Operating Revenue', 'Revenue'])
                
                data.gross_profit = self._safe_get_from_series(latest_financials,
                    ['Gross Profit', 'Total Gross Profit'])
                
                data.operating_income = self._safe_get_from_series(latest_financials,
                    ['Operating Income', 'Total Operating Income'])
                
                data.ebitda = self._safe_get_from_series(latest_financials,
                    ['EBITDA', 'Normalized EBITDA'])
                
                data.net_income = self._safe_get_from_series(latest_financials,
                    ['Net Income', 'Net Income Common Stockholders'])
            
            # Dados históricos
            data.historical_revenue = historical_data.get("revenue", []) or None
            data.historical_net_income = historical_data.get("net_income", []) or None
            data.historical_roe = historical_data.get("roe", []) or None
            
            # Metadados
            data.currency = self._safe_get(info, 'currency', 'BRL')
            data.last_updated = datetime.now()
            
            # Se não conseguiu dados das demonstrações, tentar do info
            if not data.revenue:
                data.revenue = self._safe_get(info, 'totalRevenue')
            
            if not data.total_debt:
                data.total_debt = self._safe_get(info, 'totalDebt')
            
            if not data.total_assets:
                data.total_assets = self._safe_get(info, 'totalAssets')
            
            logger.debug(f"FinancialData construído para {symbol}")
            
        except Exception as e:
            logger.error(f"Erro ao construir FinancialData: {e}")
        
        return data
    
    def _safe_get(self, data: Dict[str, Any], key: str, default: Any = None) -> Any:
        """Extrai valor de forma segura de um dicionário"""
        try:
            value = data.get(key, default)
            if value is not None and pd.notna(value):
                return float(value) if isinstance(value, (int, float)) else value
        except (ValueError, TypeError):
            pass
        return default
    
    def _safe_get_from_series(self, series: pd.Series, keys: List[str]) -> Optional[float]:
        """Extrai valor de forma segura de uma Series pandas"""
        for key in keys:
            if key in series.index:
                value = series[key]
                if pd.notna(value):
                    try:
                        return float(value)
                    except (ValueError, TypeError):
                        continue
        return None
    
    def _is_cached(self, key: str) -> bool:
        """Verifica se dados estão em cache e são válidos"""
        if key not in self.cache:
            return False
        
        cached_time = self.cache[key]['timestamp']
        return (datetime.now() - cached_time).total_seconds() < self.cache_ttl
    
    def _cache_data(self, key: str, data: Any):
        """Armazena dados no cache"""
        self.cache[key] = {
            'data': data,
            'timestamp': datetime.now()
        }
    
    async def get_batch_stock_data(self, symbols: List[str], 
                                 max_concurrent: int = 5) -> Dict[str, FinancialData]:
        """
        Coleta dados de múltiplas ações em paralelo
        
        Args:
            symbols: Lista de códigos de ações
            max_concurrent: Máximo de requisições simultâneas
            
        Returns:
            Dict com dados de cada ação
        """
        results = {}
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def fetch_single(symbol: str):
            async with semaphore:
                try:
                    data = await self.get_comprehensive_stock_data(symbol)
                    results[symbol] = data
                except Exception as e:
                    logger.error(f"Erro ao coletar {symbol}: {e}")
                    results[symbol] = FinancialData()
        
        # Executar em lotes
        tasks = [fetch_single(symbol) for symbol in symbols]
        await asyncio.gather(*tasks, return_exceptions=True)
        
        return results
    
    async def get_sector_data(self, sector_symbols: Dict[str, List[str]]) -> Dict[str, Dict[str, FinancialData]]:
        """
        Coleta dados organizados por setor
        
        Args:
            sector_symbols: Dict {setor: [códigos]}
            
        Returns:
            Dict {setor: {código: FinancialData}}
        """
        results = {}
        
        for sector, symbols in sector_symbols.items():
            logger.info(f"Coletando dados do setor {sector}: {len(symbols)} ações")
            sector_data = await self.get_batch_stock_data(symbols)
            results[sector] = sector_data
        
        return results
    
    def clear_cache(self):
        """Limpa o cache de dados"""
        self.cache.clear()
        logger.info("Cache limpo")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache"""
        now = datetime.now()
        valid_entries = 0
        expired_entries = 0
        
        for entry in self.cache.values():
            age = (now - entry['timestamp']).total_seconds()
            if age < self.cache_ttl:
                valid_entries += 1
            else:
                expired_entries += 1
        
        return {
            "total_entries": len(self.cache),
            "valid_entries": valid_entries,
            "expired_entries": expired_entries,
            "cache_ttl_seconds": self.cache_ttl
        }


class FallbackDataProvider:
    """Provedor de dados de fallback quando YFinance falha"""
    
    def __init__(self):
        self.alpha_vantage_key = settings.alpha_vantage_api_key
    
    async def get_basic_data(self, symbol: str) -> Optional[FinancialData]:
        """Coleta dados básicos via fonte alternativa"""
        try:
            if not self.alpha_vantage_key:
                logger.warning("Alpha Vantage API key não configurada")
                return None
            
            # Implementar coleta via Alpha Vantage
            # Por enquanto, retorna None
            logger.info(f"Fallback não implementado para {symbol}")
            return None
            
        except Exception as e:
            logger.error(f"Erro no fallback para {symbol}: {e}")
            return None


class DataValidator:
    """Validador de dados financeiros coletados"""
    
    @staticmethod
    def validate_financial_data(data: FinancialData) -> Dict[str, List[str]]:
        """
        Valida dados financeiros coletados
        
        Returns:
            Dict com warnings e errors
        """
        warnings = []
        errors = []
        
        try:
            # Validar dados básicos
            if not data.current_price or data.current_price <= 0:
                errors.append("Preço atual inválido ou ausente")
            
            if data.market_cap and data.market_cap <= 0:
                warnings.append("Market cap inválido")
            
            # Validar consistência
            if (data.total_assets and data.total_equity and 
                data.total_assets < data.total_equity):
                warnings.append("Ativo total menor que patrimônio líquido")
            
            if (data.current_assets and data.current_liabilities and
                data.current_assets < 0):
                errors.append("Ativo circulante negativo")
            
            # Validar dados históricos
            if data.historical_revenue:
                if any(r < 0 for r in data.historical_revenue if r is not None):
                    warnings.append("Receita histórica com valores negativos")
            
            # Validar completude
            required_fields = ['current_price', 'market_cap', 'revenue']
            missing_fields = [f for f in required_fields if not getattr(data, f)]
            
            if missing_fields:
                warnings.append(f"Campos importantes ausentes: {missing_fields}")
            
        except Exception as e:
            errors.append(f"Erro na validação: {e}")
        
        return {"warnings": warnings, "errors": errors}
    
    @staticmethod
    def calculate_data_quality_score(data: FinancialData) -> float:
        """
        Calcula score de qualidade dos dados (0-100)
        
        Returns:
            Score de qualidade
        """
        total_fields = 0
        filled_fields = 0
        important_fields = 0
        important_filled = 0
        
        # Campos importantes (peso maior)
        important_field_names = [
            'current_price', 'market_cap', 'revenue', 'net_income',
            'total_assets', 'total_equity'
        ]
        
        for field_name, field_value in asdict(data).items():
            if field_name not in ['currency', 'reporting_period', 'last_updated']:
                total_fields += 1
                if field_value is not None:
                    filled_fields += 1
                
                if field_name in important_field_names:
                    important_fields += 1
                    if field_value is not None:
                        important_filled += 1
        
        # Score baseado em campos preenchidos (peso 70%) e campos importantes (peso 30%)
        general_score = (filled_fields / total_fields) * 70 if total_fields > 0 else 0
        important_score = (important_filled / important_fields) * 30 if important_fields > 0 else 0
        
        return general_score + important_score


# Exemplo de uso
async def main():
    """Exemplo de uso do cliente expandido"""
    client = EnhancedYFinanceClient()
    
    try:
        # Teste com uma ação
        data = await client.get_comprehensive_stock_data("PETR4")
        
        print(f"Dados coletados para PETR4:")
        print(f"Preço atual: R$ {data.current_price}")
        print(f"Market Cap: R$ {data.market_cap:,.0f}" if data.market_cap else "Market Cap: N/A")
        print(f"Receita: R$ {data.revenue:,.0f}" if data.revenue else "Receita: N/A")
        print(f"Lucro Líquido: R$ {data.net_income:,.0f}" if data.net_income else "Lucro: N/A")
        print(f"Receitas históricas: {len(data.historical_revenue or [])} períodos")
        
        # Validar dados
        validation = DataValidator.validate_financial_data(data)
        if validation["warnings"]:
            print(f"Avisos: {validation['warnings']}")
        if validation["errors"]:
            print(f"Erros: {validation['errors']}")
        
        quality_score = DataValidator.calculate_data_quality_score(data)
        print(f"Qualidade dos dados: {quality_score:.1f}%")
        
    except Exception as e:
        print(f"Erro: {e}")


if __name__ == "__main__":
    asyncio.run(main())
