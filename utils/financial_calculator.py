# utils/financial_calculator.py
"""
Calculadora de Indicadores Financeiros para Análise Fundamentalista
Implementa cálculo de 25+ métricas fundamentalistas com validação automática
"""
import logging
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class MetricCategory(Enum):
    """Categorias de métricas financeiras"""
    VALUATION = "valuation"
    PROFITABILITY = "profitability"
    GROWTH = "growth"
    EFFICIENCY = "efficiency"
    DEBT = "debt"
    LIQUIDITY = "liquidity"


@dataclass
class FinancialData:
    """Estrutura de dados financeiros para cálculos"""
    # Dados básicos
    symbol: Optional[str] = None
    current_price: Optional[float] = None
    market_cap: Optional[float] = None
    shares_outstanding: Optional[float] = None
    
    # Demonstrativo de Resultados
    revenue: Optional[float] = None
    gross_profit: Optional[float] = None
    operating_income: Optional[float] = None
    ebitda: Optional[float] = None
    net_income: Optional[float] = None
    
    # Balanço Patrimonial
    total_assets: Optional[float] = None
    current_assets: Optional[float] = None
    cash_and_equivalents: Optional[float] = None
    total_debt: Optional[float] = None
    current_liabilities: Optional[float] = None
    shareholders_equity: Optional[float] = None
    
    # Dados históricos para crescimento (últimos 3 anos)
    revenue_history: List[float] = field(default_factory=list)
    net_income_history: List[float] = field(default_factory=list)
    
    # Dados setoriais/mercado
    sector: Optional[str] = None
    industry: Optional[str] = None
    
    # Metadados
    last_updated: Optional[datetime] = None
    data_quality_score: Optional[float] = None


@dataclass
class FinancialMetrics:
    """Resultado dos cálculos de métricas financeiras"""
    # Métricas de Valuation
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    ps_ratio: Optional[float] = None
    ev_ebitda: Optional[float] = None
    price_to_book: Optional[float] = None
    
    # Métricas de Rentabilidade
    roe: Optional[float] = None  # Return on Equity
    roa: Optional[float] = None  # Return on Assets
    roic: Optional[float] = None  # Return on Invested Capital
    gross_margin: Optional[float] = None
    operating_margin: Optional[float] = None
    net_margin: Optional[float] = None
    ebitda_margin: Optional[float] = None
    
    # Métricas de Crescimento
    revenue_growth_1y: Optional[float] = None
    revenue_growth_3y: Optional[float] = None
    earnings_growth_1y: Optional[float] = None
    earnings_growth_3y: Optional[float] = None
    
    # Métricas de Eficiência
    asset_turnover: Optional[float] = None
    inventory_turnover: Optional[float] = None
    
    # Métricas de Endividamento
    debt_to_equity: Optional[float] = None
    debt_to_assets: Optional[float] = None
    debt_to_ebitda: Optional[float] = None
    interest_coverage: Optional[float] = None
    
    # Métricas de Liquidez
    current_ratio: Optional[float] = None
    quick_ratio: Optional[float] = None
    cash_ratio: Optional[float] = None
    
    # Scores e qualidade
    overall_score: Optional[float] = None
    category_scores: Dict[str, float] = field(default_factory=dict)
    
    # Metadados
    calculation_date: datetime = field(default_factory=datetime.now)
    warnings: List[str] = field(default_factory=list)


class FinancialCalculator:
    """Calculadora principal de métricas financeiras"""
    
    def __init__(self):
        self.sector_benchmarks = self._load_sector_benchmarks()
        
    def calculate_all_metrics(self, data: FinancialData, reasoning_agent=None) -> FinancialMetrics:
        """
        Calcula todas as métricas financeiras disponíveis
        
        Args:
            data: Dados financeiros da empresa
            
        Returns:
            FinancialMetrics: Todas as métricas calculadas
        """
        logger.info(f"Calculando métricas para empresa (Market Cap: {data.market_cap})")
        
        metrics = FinancialMetrics()
        
        # Validar dados de entrada
        quality_score = self._validate_data_quality(data)
        
        try:
            # Calcular métricas por categoria
            self._calculate_valuation_metrics(data, metrics)
            self._calculate_profitability_metrics(data, metrics)
            self._calculate_growth_metrics(data, metrics)
            self._calculate_efficiency_metrics(data, metrics)
            self._calculate_debt_metrics(data, metrics)
            self._calculate_liquidity_metrics(data, metrics)
            
            # ESCOLHER ENTRE VERSÕES:
            if reasoning_agent:
                # Versão inteligente com Agno
                self._calculate_category_scores_intelligent(metrics, data.sector, reasoning_agent)
            else:
                # Versão tradicional (fallback)
                self._calculate_category_scores(metrics, data.sector)
            
            # Calcular score geral
            metrics.overall_score = self._calculate_overall_score(metrics)
            
        except Exception as e:
            logger.error(f"Erro no cálculo de métricas: {e}")
            metrics.warnings.append(f"Erro no cálculo: {str(e)}")
        
        return metrics
    
    def _calculate_valuation_metrics(self, data: FinancialData, metrics: FinancialMetrics):
        """Calcula métricas de valuation"""
        try:
            # P/L Ratio
            if data.current_price and data.net_income and data.shares_outstanding:
                eps = data.net_income / data.shares_outstanding
                if eps > 0:
                    metrics.pe_ratio = data.current_price / eps
            
            # P/VP Ratio
            if data.market_cap and data.shareholders_equity and data.shareholders_equity > 0:
                metrics.pb_ratio = data.market_cap / data.shareholders_equity
            
            # P/S Ratio
            if data.market_cap and data.revenue and data.revenue > 0:
                metrics.ps_ratio = data.market_cap / data.revenue
            
            # EV/EBITDA
            if data.market_cap and data.total_debt and data.cash_and_equivalents and data.ebitda:
                enterprise_value = data.market_cap + data.total_debt - data.cash_and_equivalents
                if data.ebitda > 0:
                    metrics.ev_ebitda = enterprise_value / data.ebitda
                    
        except Exception as e:
            logger.warning(f"Erro no cálculo de métricas de valuation: {e}")
            metrics.warnings.append("Erro em métricas de valuation")
    
    def _calculate_profitability_metrics(self, data: FinancialData, metrics: FinancialMetrics):
        """Calcula métricas de rentabilidade"""
        try:
            # ROE (Return on Equity)
            if data.net_income and data.shareholders_equity and data.shareholders_equity > 0:
                metrics.roe = (data.net_income / data.shareholders_equity) * 100
            
            # ROA (Return on Assets)
            if data.net_income and data.total_assets and data.total_assets > 0:
                metrics.roa = (data.net_income / data.total_assets) * 100
            
            # Margens
            if data.revenue and data.revenue > 0:
                if data.gross_profit:
                    metrics.gross_margin = (data.gross_profit / data.revenue) * 100
                if data.operating_income:
                    metrics.operating_margin = (data.operating_income / data.revenue) * 100
                if data.net_income:
                    metrics.net_margin = (data.net_income / data.revenue) * 100
                if data.ebitda:
                    metrics.ebitda_margin = (data.ebitda / data.revenue) * 100
                    
        except Exception as e:
            logger.warning(f"Erro no cálculo de métricas de rentabilidade: {e}")
            metrics.warnings.append("Erro em métricas de rentabilidade")
    
    def _calculate_growth_metrics(self, data: FinancialData, metrics: FinancialMetrics):
        """Calcula métricas de crescimento"""
        try:
            # Crescimento de receita
            if len(data.revenue_history) >= 2:
                # Crescimento 1 ano
                metrics.revenue_growth_1y = self._calculate_growth_rate(
                    data.revenue_history[-1], data.revenue_history[-2]
                )
                
                # Crescimento 3 anos (CAGR)
                if len(data.revenue_history) >= 3:
                    metrics.revenue_growth_3y = self._calculate_cagr(
                        data.revenue_history[-3], data.revenue_history[-1], 3
                    )
            
            # Crescimento de lucro
            if len(data.net_income_history) >= 2:
                metrics.earnings_growth_1y = self._calculate_growth_rate(
                    data.net_income_history[-1], data.net_income_history[-2]
                )
                
                if len(data.net_income_history) >= 3:
                    metrics.earnings_growth_3y = self._calculate_cagr(
                        data.net_income_history[-3], data.net_income_history[-1], 3
                    )
                    
        except Exception as e:
            logger.warning(f"Erro no cálculo de métricas de crescimento: {e}")
            metrics.warnings.append("Erro em métricas de crescimento")
    
    def _calculate_efficiency_metrics(self, data: FinancialData, metrics: FinancialMetrics):
        """Calcula métricas de eficiência"""
        try:
            # Asset Turnover
            if data.revenue and data.total_assets and data.total_assets > 0:
                metrics.asset_turnover = data.revenue / data.total_assets
                
        except Exception as e:
            logger.warning(f"Erro no cálculo de métricas de eficiência: {e}")
            metrics.warnings.append("Erro em métricas de eficiência")
    
    def _calculate_debt_metrics(self, data: FinancialData, metrics: FinancialMetrics):
        """Calcula métricas de endividamento"""
        try:
            # Debt to Equity
            if data.total_debt and data.shareholders_equity and data.shareholders_equity > 0:
                metrics.debt_to_equity = data.total_debt / data.shareholders_equity
            
            # Debt to Assets
            if data.total_debt and data.total_assets and data.total_assets > 0:
                metrics.debt_to_assets = data.total_debt / data.total_assets
            
            # Debt to EBITDA
            if data.total_debt and data.ebitda and data.ebitda > 0:
                metrics.debt_to_ebitda = data.total_debt / data.ebitda
                
        except Exception as e:
            logger.warning(f"Erro no cálculo de métricas de endividamento: {e}")
            metrics.warnings.append("Erro em métricas de endividamento")
    
    def _calculate_liquidity_metrics(self, data: FinancialData, metrics: FinancialMetrics):
        """Calcula métricas de liquidez"""
        try:
            # Current Ratio
            if data.current_assets and data.current_liabilities and data.current_liabilities > 0:
                metrics.current_ratio = data.current_assets / data.current_liabilities
            
            # Cash Ratio
            if data.cash_and_equivalents and data.current_liabilities and data.current_liabilities > 0:
                metrics.cash_ratio = data.cash_and_equivalents / data.current_liabilities
                
        except Exception as e:
            logger.warning(f"Erro no cálculo de métricas de liquidez: {e}")
            metrics.warnings.append("Erro em métricas de liquidez")
    
    def _calculate_growth_rate(self, current: float, previous: float) -> float:
        """Calcula taxa de crescimento simples"""
        if previous == 0:
            return 0.0
        return ((current - previous) / abs(previous)) * 100
    
    def _calculate_cagr(self, initial: float, final: float, years: int) -> float:
        """Calcula Compound Annual Growth Rate (CAGR)"""
        if initial <= 0 or years <= 0:
            return 0.0
        return (((final / initial) ** (1/years)) - 1) * 100
    
    def _validate_data_quality(self, data: FinancialData) -> float:
        """Valida a qualidade dos dados e retorna score 0-100"""
        required_fields = [
            'current_price', 'market_cap', 'revenue', 'net_income',
            'total_assets', 'shareholders_equity'
        ]
        
        available_fields = sum(1 for field in required_fields 
                             if getattr(data, field) is not None)
        
        return (available_fields / len(required_fields)) * 100
    
    def _calculate_category_scores(self, metrics: FinancialMetrics, sector: Optional[str]):
        """Calcula scores por categoria baseado em benchmarks setoriais"""
        benchmarks = self.sector_benchmarks.get(sector, self.sector_benchmarks.get('default', {}))
        
        # Score de Valuation
        valuation_score = self._score_valuation_metrics(metrics, benchmarks)
        metrics.category_scores['valuation'] = valuation_score
        
        # Score de Rentabilidade
        profitability_score = self._score_profitability_metrics(metrics, benchmarks)
        metrics.category_scores['profitability'] = profitability_score
        
        # Score de Crescimento
        growth_score = self._score_growth_metrics(metrics, benchmarks)
        metrics.category_scores['growth'] = growth_score
        
        # Score de Endividamento
        debt_score = self._score_debt_metrics(metrics, benchmarks)
        metrics.category_scores['debt'] = debt_score


    def _calculate_category_scores_intelligent(self, metrics: FinancialMetrics, 
                                         sector: Optional[str],
                                         reasoning_agent: Optional['Agent'] = None):
        """
        Versão inteligente do cálculo de scores por categoria
        Usa ReasoningTools do Agno para benchmarking setorial avançado
        """
        
        # 1. SEMPRE executar cálculo base primeiro (mantém compatibilidade)
        self._calculate_category_scores(metrics, sector)
        
        # 2. Se Agno disponível, fazer análise inteligente
        if reasoning_agent and sector and hasattr(reasoning_agent, 'run'):
            try:
                import asyncio
                
                benchmark_prompt = f"""
                BENCHMARKING SETORIAL INTELIGENTE
                
                EMPRESA: {getattr(metrics, 'stock_code', 'UNKNOWN')}
                SETOR: {sector}
                
                MÉTRICAS CALCULADAS:
                - P/L: {metrics.pe_ratio if metrics.pe_ratio else 'N/A'}
                - P/VP: {metrics.pb_ratio if metrics.pb_ratio else 'N/A'}  
                - ROE: {metrics.roe if metrics.roe else 'N/A'}%
                - ROA: {metrics.roa if metrics.roa else 'N/A'}%
                - Margem Líquida: {metrics.net_margin if metrics.net_margin else 'N/A'}%
                - Crescimento Receita: {metrics.revenue_growth_1y if metrics.revenue_growth_1y else 'N/A'}%
                - Dívida/Patrimônio: {metrics.debt_to_equity if metrics.debt_to_equity else 'N/A'}
                
                SCORES CALCULADOS PELO ALGORITMO BASE:
                - Valuation: {metrics.category_scores.get('valuation', 0):.1f}/100
                - Rentabilidade: {metrics.category_scores.get('profitability', 0):.1f}/100
                - Crescimento: {metrics.category_scores.get('growth', 0):.1f}/100
                - Endividamento: {metrics.category_scores.get('debt', 0):.1f}/100
                
                ANÁLISE SETORIAL REQUERIDA:
                1. Para o setor {sector}, essas métricas estão dentro do esperado?
                2. Algum score parece inconsistente com benchmarks típicos do setor?
                3. Há outliers positivos ou negativos que merecem ajuste?
                4. Considerando ciclos setoriais, os scores refletem bem o momento?
                
                RETORNE EM JSON:
                {{
                    "sector_analysis": "análise textual do setor",
                    "suggested_adjustments": {{
                        "valuation": number ou null,
                        "profitability": number ou null, 
                        "growth": number ou null,
                        "debt": number ou null
                    }},
                    "confidence_level": number de 0 a 100,
                    "key_insights": ["insight1", "insight2", "insight3"],
                    "reasoning": "justificativa dos ajustes"
                }}
                """
                
                # Executar análise inteligente
                intelligent_result = asyncio.run(reasoning_agent.run(benchmark_prompt))
                
                # Aplicar ajustes sugeridos se confidence > 70
                if self._parse_intelligence_result(intelligent_result, metrics):
                    self.logger.info(f"Scores ajustados inteligentemente para {sector}")
                
                # Armazenar análise para auditoria
                metrics.intelligent_analysis = intelligent_result
                
            except Exception as e:
                self.logger.warning(f"Análise inteligente falhou: {e}")
                # Fallback: usar scores base (sem problemas)
        
    def _parse_intelligence_result(self, result: str, metrics: FinancialMetrics) -> bool:
        """Processa resultado da análise inteligente e aplica ajustes"""
        try:
            import json
            import re
            
            # Extrair JSON da resposta
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if not json_match:
                return False
            
            analysis = json.loads(json_match.group())
            confidence = analysis.get('confidence_level', 0)
            
            # Aplicar ajustes apenas se confidence > 70
            if confidence > 70:
                adjustments = analysis.get('suggested_adjustments', {})
                
                for category, new_score in adjustments.items():
                    if new_score is not None and 0 <= new_score <= 100:
                        # Aplicar ajuste ponderado (50% original + 50% sugestão)
                        original_score = metrics.category_scores.get(category, 50)
                        adjusted_score = (original_score + new_score) / 2
                        metrics.category_scores[category] = adjusted_score
                        
                        self.logger.info(f"Score {category} ajustado: {original_score:.1f} → {adjusted_score:.1f}")
                
                return True
            
            return False
            
        except Exception as e:
            self.logger.warning(f"Erro ao processar resultado inteligente: {e}")
            return False

    
    def _score_valuation_metrics(self, metrics: FinancialMetrics, benchmarks: Dict) -> float:
        """Calcula score de valuation (0-100)"""
        score = 0
        count = 0
        
        # P/L Score - menor é melhor
        if metrics.pe_ratio:
            pe_benchmark = benchmarks.get('pe_ratio', 15.0)
            if metrics.pe_ratio <= pe_benchmark:
                score += 100
            else:
                score += max(0, 100 - ((metrics.pe_ratio - pe_benchmark) / pe_benchmark) * 50)
            count += 1
        
        # P/VP Score - menor é melhor
        if metrics.pb_ratio:
            pb_benchmark = benchmarks.get('pb_ratio', 2.0)
            if metrics.pb_ratio <= pb_benchmark:
                score += 100
            else:
                score += max(0, 100 - ((metrics.pb_ratio - pb_benchmark) / pb_benchmark) * 50)
            count += 1
        
        return score / count if count > 0 else 0
    
    def _score_profitability_metrics(self, metrics: FinancialMetrics, benchmarks: Dict) -> float:
        """Calcula score de rentabilidade (0-100)"""
        score = 0
        count = 0
        
        # ROE Score - maior é melhor
        if metrics.roe:
            roe_benchmark = benchmarks.get('roe', 15.0)
            if metrics.roe >= roe_benchmark:
                score += 100
            else:
                score += max(0, (metrics.roe / roe_benchmark) * 100)
            count += 1
        
        # Margem Líquida Score - maior é melhor
        if metrics.net_margin:
            margin_benchmark = benchmarks.get('net_margin', 10.0)
            if metrics.net_margin >= margin_benchmark:
                score += 100
            else:
                score += max(0, (metrics.net_margin / margin_benchmark) * 100)
            count += 1
        
        return score / count if count > 0 else 0
    
    def _score_growth_metrics(self, metrics: FinancialMetrics, benchmarks: Dict) -> float:
        """Calcula score de crescimento (0-100)"""
        score = 0
        count = 0
        
        # Crescimento de receita
        if metrics.revenue_growth_1y:
            growth_benchmark = benchmarks.get('revenue_growth', 10.0)
            if metrics.revenue_growth_1y >= growth_benchmark:
                score += 100
            else:
                score += max(0, (metrics.revenue_growth_1y / growth_benchmark) * 100)
            count += 1
        
        return score / count if count > 0 else 0
    
    def _score_debt_metrics(self, metrics: FinancialMetrics, benchmarks: Dict) -> float:
        """Calcula score de endividamento (0-100) - menor endividamento é melhor"""
        score = 0
        count = 0
        
        # Debt to Equity - menor é melhor
        if metrics.debt_to_equity:
            debt_benchmark = benchmarks.get('debt_to_equity', 0.5)
            if metrics.debt_to_equity <= debt_benchmark:
                score += 100
            else:
                score += max(0, 100 - ((metrics.debt_to_equity - debt_benchmark) / debt_benchmark) * 100)
            count += 1
        
        return score / count if count > 0 else 0
    
    def _calculate_overall_score(self, metrics: FinancialMetrics) -> float:
        """Calcula score geral ponderado"""
        weights = {
            'valuation': 0.25,
            'profitability': 0.30,
            'growth': 0.25,
            'debt': 0.20
        }
        
        total_score = 0
        total_weight = 0
        
        for category, weight in weights.items():
            if category in metrics.category_scores:
                total_score += metrics.category_scores[category] * weight
                total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0
    
    def _load_sector_benchmarks(self) -> Dict[str, Dict[str, float]]:
        """Carrega benchmarks setoriais"""
        return {
            'default': {
                'pe_ratio': 15.0,
                'pb_ratio': 2.0,
                'roe': 15.0,
                'net_margin': 10.0,
                'revenue_growth': 10.0,
                'debt_to_equity': 0.5
            },
            'Bancos': {
                'pe_ratio': 12.0,
                'pb_ratio': 1.5,
                'roe': 18.0,
                'net_margin': 20.0,
                'revenue_growth': 8.0,
                'debt_to_equity': 0.3
            },
            'Tecnologia': {
                'pe_ratio': 25.0,
                'pb_ratio': 3.0,
                'roe': 20.0,
                'net_margin': 15.0,
                'revenue_growth': 25.0,
                'debt_to_equity': 0.2
            },
            'Petróleo e Gás': {
                'pe_ratio': 10.0,
                'pb_ratio': 1.0,
                'roe': 12.0,
                'net_margin': 8.0,
                'revenue_growth': 5.0,
                'debt_to_equity': 0.8
            }
        }


# Utility functions
def create_financial_data_from_dict(data_dict: Dict[str, Any]) -> FinancialData:
    """Cria FinancialData a partir de dicionário"""
    return FinancialData(**{k: v for k, v in data_dict.items() 
                           if k in FinancialData.__dataclass_fields__})


def metrics_to_dict(metrics: FinancialMetrics) -> Dict[str, Any]:
    """Converte FinancialMetrics para dicionário"""
    result = {}
    for field_name, field_def in FinancialMetrics.__dataclass_fields__.items():
        value = getattr(metrics, field_name)
        if isinstance(value, datetime):
            result[field_name] = value.isoformat()
        else:
            result[field_name] = value
    return result


if __name__ == "__main__":
    # Exemplo de uso
    sample_data = FinancialData(
        current_price=25.50,
        market_cap=100000000000,
        shares_outstanding=4000000000,
        revenue=50000000000,
        net_income=6000000000,
        total_assets=200000000000,
        shareholders_equity=80000000000,
        total_debt=30000000000,
        sector="Petróleo e Gás"
    )
    
    calculator = FinancialCalculator()
    metrics = calculator.calculate_all_metrics(sample_data)
    
    print(f"P/L: {metrics.pe_ratio:.2f}" if metrics.pe_ratio else "P/L: N/A")
    print(f"ROE: {metrics.roe:.2f}%" if metrics.roe else "ROE: N/A")
    print(f"Score Geral: {metrics.overall_score:.1f}" if metrics.overall_score else "Score: N/A")
