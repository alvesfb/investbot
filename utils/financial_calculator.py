# utils/financial_calculator.py
"""
Calculadora de Indicadores Financeiros
Sistema avançado para cálculo de métricas fundamentalistas
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


@dataclass
class FinancialData:
    """Estrutura para dados financeiros de uma empresa"""
    # Dados básicos de mercado
    market_cap: Optional[float] = None
    enterprise_value: Optional[float] = None
    shares_outstanding: Optional[float] = None
    current_price: Optional[float] = None
    
    # Dados do Balanço Patrimonial
    total_assets: Optional[float] = None
    total_equity: Optional[float] = None
    total_debt: Optional[float] = None
    current_assets: Optional[float] = None
    current_liabilities: Optional[float] = None
    cash_and_equivalents: Optional[float] = None
    
    # Dados da DRE
    revenue: Optional[float] = None
    gross_profit: Optional[float] = None
    operating_income: Optional[float] = None
    ebitda: Optional[float] = None
    net_income: Optional[float] = None
    
    # Dados históricos (listas com 3-5 anos)
    historical_revenue: Optional[List[float]] = None
    historical_net_income: Optional[List[float]] = None
    historical_roe: Optional[List[float]] = None
    
    # Metadados
    currency: str = "BRL"
    reporting_period: Optional[str] = None
    last_updated: Optional[datetime] = None


@dataclass
class FinancialMetrics:
    """Estrutura para métricas calculadas"""
    # Métricas de Valuation
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    ps_ratio: Optional[float] = None
    ev_ebitda: Optional[float] = None
    ev_sales: Optional[float] = None
    
    # Métricas de Rentabilidade
    roe: Optional[float] = None  # Return on Equity
    roic: Optional[float] = None  # Return on Invested Capital
    roa: Optional[float] = None  # Return on Assets
    gross_margin: Optional[float] = None
    operating_margin: Optional[float] = None
    net_margin: Optional[float] = None
    ebitda_margin: Optional[float] = None
    
    # Métricas de Endividamento
    debt_to_equity: Optional[float] = None
    debt_to_ebitda: Optional[float] = None
    current_ratio: Optional[float] = None
    quick_ratio: Optional[float] = None
    
    # Métricas de Crescimento
    revenue_growth_1y: Optional[float] = None
    revenue_growth_3y_cagr: Optional[float] = None
    earnings_growth_1y: Optional[float] = None
    earnings_growth_3y_cagr: Optional[float] = None
    
    # Métricas de Eficiência
    asset_turnover: Optional[float] = None
    inventory_turnover: Optional[float] = None
    receivables_turnover: Optional[float] = None
    
    # Métricas de Qualidade
    roe_consistency: Optional[float] = None  # Desvio padrão do ROE
    earnings_quality: Optional[float] = None  # Relação FCF/Lucro
    
    # Metadados
    calculation_date: Optional[datetime] = None
    data_completeness: Optional[float] = None  # % de dados disponíveis


class FinancialCalculator:
    """Calculadora principal de indicadores financeiros"""
    
    def __init__(self):
        self.min_data_threshold = 0.5  # 50% dos dados necessários
        
    def calculate_all_metrics(self, financial_data: FinancialData) -> FinancialMetrics:
        """
        Calcula todas as métricas financeiras disponíveis
        
        Args:
            financial_data: Dados financeiros da empresa
            
        Returns:
            FinancialMetrics: Todas as métricas calculadas
        """
        metrics = FinancialMetrics()
        
        try:
            # Calcular métricas de valuation
            self._calculate_valuation_metrics(financial_data, metrics)
            
            # Calcular métricas de rentabilidade
            self._calculate_profitability_metrics(financial_data, metrics)
            
            # Calcular métricas de endividamento
            self._calculate_leverage_metrics(financial_data, metrics)
            
            # Calcular métricas de crescimento
            self._calculate_growth_metrics(financial_data, metrics)
            
            # Calcular métricas de eficiência
            self._calculate_efficiency_metrics(financial_data, metrics)
            
            # Calcular métricas de qualidade
            self._calculate_quality_metrics(financial_data, metrics)
            
            # Calcular completude dos dados
            metrics.data_completeness = self._calculate_data_completeness(metrics)
            metrics.calculation_date = datetime.now()
            
            logger.info(f"Métricas calculadas com {metrics.data_completeness:.1%} de completude")
            
        except Exception as e:
            logger.error(f"Erro no cálculo de métricas: {e}")
            
        return metrics
    
    def _calculate_valuation_metrics(self, data: FinancialData, metrics: FinancialMetrics):
        """Calcula métricas de valuation"""
        try:
            # P/L (Price/Earnings)
            if data.market_cap and data.net_income and data.net_income > 0:
                metrics.pe_ratio = data.market_cap / data.net_income
            
            # P/VP (Price/Book)
            if data.market_cap and data.total_equity and data.total_equity > 0:
                metrics.pb_ratio = data.market_cap / data.total_equity
            
            # P/S (Price/Sales)
            if data.market_cap and data.revenue and data.revenue > 0:
                metrics.ps_ratio = data.market_cap / data.revenue
            
            # EV/EBITDA
            if data.enterprise_value and data.ebitda and data.ebitda > 0:
                metrics.ev_ebitda = data.enterprise_value / data.ebitda
            
            # EV/Sales
            if data.enterprise_value and data.revenue and data.revenue > 0:
                metrics.ev_sales = data.enterprise_value / data.revenue
                
        except Exception as e:
            logger.error(f"Erro no cálculo de métricas de valuation: {e}")
    
    def _calculate_profitability_metrics(self, data: FinancialData, metrics: FinancialMetrics):
        """Calcula métricas de rentabilidade"""
        try:
            # ROE (Return on Equity)
            if data.net_income and data.total_equity and data.total_equity > 0:
                metrics.roe = (data.net_income / data.total_equity) * 100
            
            # ROA (Return on Assets)
            if data.net_income and data.total_assets and data.total_assets > 0:
                metrics.roa = (data.net_income / data.total_assets) * 100
            
            # ROIC (Return on Invested Capital)
            if data.operating_income and data.total_equity and data.total_debt:
                invested_capital = data.total_equity + data.total_debt
                if invested_capital > 0:
                    # Aproximação: NOPAT ≈ Operating Income * (1 - tax_rate)
                    # Assumindo tax rate de 34% (média brasileira)
                    nopat = data.operating_income * 0.66
                    metrics.roic = (nopat / invested_capital) * 100
            
            # Margens
            if data.revenue and data.revenue > 0:
                # Margem Bruta
                if data.gross_profit:
                    metrics.gross_margin = (data.gross_profit / data.revenue) * 100
                
                # Margem Operacional
                if data.operating_income:
                    metrics.operating_margin = (data.operating_income / data.revenue) * 100
                
                # Margem Líquida
                if data.net_income:
                    metrics.net_margin = (data.net_income / data.revenue) * 100
                
                # Margem EBITDA
                if data.ebitda:
                    metrics.ebitda_margin = (data.ebitda / data.revenue) * 100
                    
        except Exception as e:
            logger.error(f"Erro no cálculo de métricas de rentabilidade: {e}")
    
    def _calculate_leverage_metrics(self, data: FinancialData, metrics: FinancialMetrics):
        """Calcula métricas de endividamento"""
        try:
            # Debt to Equity
            if data.total_debt and data.total_equity and data.total_equity > 0:
                metrics.debt_to_equity = data.total_debt / data.total_equity
            
            # Debt to EBITDA
            if data.total_debt and data.ebitda and data.ebitda > 0:
                metrics.debt_to_ebitda = data.total_debt / data.ebitda
            
            # Current Ratio (Liquidez Corrente)
            if data.current_assets and data.current_liabilities and data.current_liabilities > 0:
                metrics.current_ratio = data.current_assets / data.current_liabilities
            
            # Quick Ratio (Liquidez Seca)
            if (data.current_assets and data.current_liabilities and 
                data.current_liabilities > 0 and data.cash_and_equivalents):
                # Aproximação: Quick Assets ≈ Current Assets - Inventory
                # Como não temos inventory, usamos 70% dos current assets
                quick_assets = data.current_assets * 0.7
                metrics.quick_ratio = quick_assets / data.current_liabilities
                
        except Exception as e:
            logger.error(f"Erro no cálculo de métricas de endividamento: {e}")
    
    def _calculate_growth_metrics(self, data: FinancialData, metrics: FinancialMetrics):
        """Calcula métricas de crescimento"""
        try:
            # Crescimento de Receita
            if data.historical_revenue and len(data.historical_revenue) >= 2:
                revenues = data.historical_revenue
                
                # Crescimento 1 ano (último vs penúltimo)
                if len(revenues) >= 2 and revenues[-2] > 0:
                    metrics.revenue_growth_1y = ((revenues[-1] / revenues[-2]) - 1) * 100
                
                # CAGR 3 anos
                if len(revenues) >= 4 and revenues[-4] > 0:  # 4 pontos = 3 anos
                    years = 3
                    metrics.revenue_growth_3y_cagr = (
                        ((revenues[-1] / revenues[-4]) ** (1/years)) - 1
                    ) * 100
            
            # Crescimento de Lucro
            if data.historical_net_income and len(data.historical_net_income) >= 2:
                earnings = data.historical_net_income
                
                # Crescimento 1 ano
                if len(earnings) >= 2 and earnings[-2] != 0:
                    if earnings[-2] > 0:
                        metrics.earnings_growth_1y = ((earnings[-1] / earnings[-2]) - 1) * 100
                    elif earnings[-1] > 0 and earnings[-2] < 0:
                        metrics.earnings_growth_1y = 100  # Saiu do prejuízo
                
                # CAGR 3 anos (só se todos os valores forem positivos)
                if (len(earnings) >= 4 and 
                    all(e > 0 for e in earnings[-4:]) and earnings[-4] > 0):
                    years = 3
                    metrics.earnings_growth_3y_cagr = (
                        ((earnings[-1] / earnings[-4]) ** (1/years)) - 1
                    ) * 100
                    
        except Exception as e:
            logger.error(f"Erro no cálculo de métricas de crescimento: {e}")
    
    def _calculate_efficiency_metrics(self, data: FinancialData, metrics: FinancialMetrics):
        """Calcula métricas de eficiência"""
        try:
            # Asset Turnover (Giro do Ativo)
            if data.revenue and data.total_assets and data.total_assets > 0:
                metrics.asset_turnover = data.revenue / data.total_assets
                
        except Exception as e:
            logger.error(f"Erro no cálculo de métricas de eficiência: {e}")
    
    def _calculate_quality_metrics(self, data: FinancialData, metrics: FinancialMetrics):
        """Calcula métricas de qualidade"""
        try:
            # Consistência do ROE (desvio padrão)
            if data.historical_roe and len(data.historical_roe) >= 3:
                roe_values = [r for r in data.historical_roe if r is not None]
                if len(roe_values) >= 3:
                    metrics.roe_consistency = np.std(roe_values)
                    
        except Exception as e:
            logger.error(f"Erro no cálculo de métricas de qualidade: {e}")
    
    def _calculate_data_completeness(self, metrics: FinancialMetrics) -> float:
        """Calcula o percentual de completude dos dados"""
        total_fields = 0
        completed_fields = 0
        
        for field_name, field_value in metrics.__dict__.items():
            if field_name not in ['calculation_date', 'data_completeness']:
                total_fields += 1
                if field_value is not None:
                    completed_fields += 1
        
        return completed_fields / total_fields if total_fields > 0 else 0.0
    
    def validate_metrics(self, metrics: FinancialMetrics) -> Dict[str, List[str]]:
        """
        Valida as métricas calculadas e retorna alertas
        
        Returns:
            Dict com warnings e errors encontrados
        """
        warnings = []
        errors = []
        
        try:
            # Validar P/L
            if metrics.pe_ratio is not None:
                if metrics.pe_ratio < 0:
                    warnings.append("P/L negativo - empresa com prejuízo")
                elif metrics.pe_ratio > 100:
                    warnings.append("P/L muito alto (>100) - possível sobrevalorização")
            
            # Validar P/VP
            if metrics.pb_ratio is not None:
                if metrics.pb_ratio < 0:
                    errors.append("P/VP negativo - patrimônio líquido negativo")
                elif metrics.pb_ratio > 10:
                    warnings.append("P/VP muito alto (>10) - possível sobrevalorização")
            
            # Validar ROE
            if metrics.roe is not None:
                if metrics.roe < 0:
                    warnings.append("ROE negativo - empresa não rentável")
                elif metrics.roe > 50:
                    warnings.append("ROE muito alto (>50%) - verificar sustentabilidade")
            
            # Validar endividamento
            if metrics.debt_to_equity is not None:
                if metrics.debt_to_equity > 2:
                    warnings.append("Endividamento alto (D/E > 2)")
            
            # Validar liquidez
            if metrics.current_ratio is not None:
                if metrics.current_ratio < 1:
                    warnings.append("Liquidez baixa (< 1) - possível dificuldade de pagamento")
            
            # Verificar completude mínima
            if metrics.data_completeness and metrics.data_completeness < self.min_data_threshold:
                errors.append(f"Dados insuficientes ({metrics.data_completeness:.1%} < {self.min_data_threshold:.1%})")
                
        except Exception as e:
            errors.append(f"Erro na validação: {e}")
        
        return {"warnings": warnings, "errors": errors}
    
    def get_sector_benchmarks(self, sector: str) -> Dict[str, Tuple[float, float]]:
        """
        Retorna benchmarks típicos por setor (min, max para cada métrica)
        
        Args:
            sector: Nome do setor
            
        Returns:
            Dict com ranges típicos para cada métrica
        """
        # Benchmarks baseados no mercado brasileiro
        sector_benchmarks = {
            "Bancos": {
                "pe_ratio": (5, 15),
                "pb_ratio": (0.8, 2.5),
                "roe": (12, 25),
                "debt_to_equity": (3, 8),  # Bancos têm endividamento diferente
            },
            "Petróleo e Gás": {
                "pe_ratio": (3, 12),
                "pb_ratio": (0.5, 2.0),
                "roe": (8, 20),
                "debt_to_equity": (0.2, 1.0),
            },
            "Mineração": {
                "pe_ratio": (4, 15),
                "pb_ratio": (0.8, 3.0),
                "roe": (10, 25),
                "debt_to_equity": (0.1, 0.8),
            },
            "Varejo": {
                "pe_ratio": (8, 25),
                "pb_ratio": (1.0, 4.0),
                "roe": (15, 30),
                "debt_to_equity": (0.3, 1.5),
            },
            "Tecnologia": {
                "pe_ratio": (15, 40),
                "pb_ratio": (2.0, 8.0),
                "roe": (20, 35),
                "debt_to_equity": (0.0, 0.5),
            }
        }
        
        return sector_benchmarks.get(sector, {
            "pe_ratio": (5, 25),
            "pb_ratio": (0.5, 5.0),
            "roe": (10, 25),
            "debt_to_equity": (0.1, 2.0),
        })


# Funções utilitárias
def calculate_cagr(start_value: float, end_value: float, years: float) -> float:
    """Calcula Compound Annual Growth Rate"""
    if start_value <= 0 or end_value <= 0 or years <= 0:
        return 0.0
    
    return ((end_value / start_value) ** (1/years) - 1) * 100


def calculate_percentile_rank(value: float, value_list: List[float]) -> float:
    """Calcula o percentil de um valor em relação a uma lista"""
    if not value_list or value is None:
        return 0.0
    
    sorted_values = sorted([v for v in value_list if v is not None])
    if not sorted_values:
        return 0.0
    
    # Encontrar posição do valor
    position = sum(1 for v in sorted_values if v < value)
    return (position / len(sorted_values)) * 100


def normalize_metric(value: Optional[float], min_val: float, max_val: float) -> Optional[float]:
    """Normaliza uma métrica para escala 0-100"""
    if value is None:
        return None
    
    if max_val == min_val:
        return 50.0  # Valor médio se não há variação
    
    normalized = ((value - min_val) / (max_val - min_val)) * 100
    return max(0, min(100, normalized))


def detect_outliers(values: List[float], method: str = "iqr") -> List[bool]:
    """Detecta outliers em uma lista de valores"""
    if not values or len(values) < 4:
        return [False] * len(values)
    
    values_array = np.array(values)
    
    if method == "iqr":
        q1 = np.percentile(values_array, 25)
        q3 = np.percentile(values_array, 75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        return [(v < lower_bound or v > upper_bound) for v in values]
    
    elif method == "zscore":
        mean = np.mean(values_array)
        std = np.std(values_array)
        z_scores = np.abs((values_array - mean) / std) if std > 0 else np.zeros_like(values_array)
        
        return [z > 3 for z in z_scores]  # |z-score| > 3 são outliers
    
    return [False] * len(values)


# Exemplo de uso
if __name__ == "__main__":
    # Dados de exemplo
    sample_data = FinancialData(
        market_cap=100000000000,  # 100B
        enterprise_value=120000000000,  # 120B
        shares_outstanding=5000000000,  # 5B ações
        current_price=20.0,
        
        total_assets=80000000000,  # 80B
        total_equity=40000000000,  # 40B
        total_debt=25000000000,    # 25B
        current_assets=15000000000,  # 15B
        current_liabilities=10000000000,  # 10B
        cash_and_equivalents=5000000000,  # 5B
        
        revenue=50000000000,      # 50B
        gross_profit=20000000000,  # 20B
        operating_income=8000000000,  # 8B
        ebitda=12000000000,       # 12B
        net_income=6000000000,    # 6B
        
        historical_revenue=[40000000000, 42000000000, 45000000000, 50000000000],
        historical_net_income=[4000000000, 4500000000, 5500000000, 6000000000],
        historical_roe=[10.0, 11.25, 13.75, 15.0]
    )
    
    # Calcular métricas
    calculator = FinancialCalculator()
    metrics = calculator.calculate_all_metrics(sample_data)
    
    print("Métricas Calculadas:")
    print(f"P/L: {metrics.pe_ratio:.2f}" if metrics.pe_ratio else "P/L: N/A")
    print(f"P/VP: {metrics.pb_ratio:.2f}" if metrics.pb_ratio else "P/VP: N/A")
    print(f"ROE: {metrics.roe:.2f}%" if metrics.roe else "ROE: N/A")
    print(f"ROIC: {metrics.roic:.2f}%" if metrics.roic else "ROIC: N/A")
    print(f"Margem Líquida: {metrics.net_margin:.2f}%" if metrics.net_margin else "Margem Líquida: N/A")
    print(f"Crescimento Receita 3Y CAGR: {metrics.revenue_growth_3y_cagr:.2f}%" if metrics.revenue_growth_3y_cagr else "Crescimento: N/A")
    print(f"Completude dos dados: {metrics.data_completeness:.1%}")
    
    # Validar métricas
    validation = calculator.validate_metrics(metrics)
    if validation["warnings"]:
        print("\nAvisos:", validation["warnings"])
    if validation["errors"]:
        print("Erros:", validation["errors"])
