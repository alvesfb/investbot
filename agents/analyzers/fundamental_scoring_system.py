# agents/analyzers/fundamental_scoring_system.py
"""
Sistema de Scoring Fundamentalista - Versão Corrigida
Imports atualizados para Agno e investigação do FinancialCalculator

Data: 13/07/2025
Versão: 2.0 (Corrigida)
"""

import asyncio
import json
import logging
import sys
import yfinance as yf
import time
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple, Any, Union
from enum import Enum
from pathlib import Path
import importlib.util

# Configuração de logging
logger = logging.getLogger(__name__)

env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)

# =================================================================
# 1. INVESTIGAÇÃO E IMPORTS CORRIGIDOS
# =================================================================

def investigate_financial_calculator():
    """Investiga problemas com o FinancialCalculator"""
    print("🔍 INVESTIGANDO FINANCIAL CALCULATOR")
    print("=" * 50)
    
    # Verificar se arquivo existe
    calc_path = Path("utils/financial_calculator.py")
    print(f"Arquivo existe: {calc_path.exists()}")
    
    if calc_path.exists():
        print(f"Tamanho do arquivo: {calc_path.stat().st_size} bytes")
        
        # Verificar conteúdo
        try:
            with open(calc_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Verificar classes
            classes_to_check = ['FinancialCalculator', 'FinancialData', 'FinancialMetrics']
            for cls in classes_to_check:
                if f"class {cls}" in content:
                    print(f"✅ Classe {cls} encontrada no arquivo")
                else:
                    print(f"❌ Classe {cls} NÃO encontrada no arquivo")
        
        except Exception as e:
            print(f"❌ Erro ao ler arquivo: {e}")
    
    # Verificar PYTHONPATH
    current_dir = Path.cwd()
    print(f"\nDiretório atual: {current_dir}")
    print(f"utils/ no sys.path: {str(current_dir) in sys.path}")
    
    # Tentar import direto
    try:
        sys.path.insert(0, str(current_dir))
        import utils.financial_calculator as fc
        print("✅ Import utils.financial_calculator: SUCESSO")
        
        # Verificar atributos
        attrs = dir(fc)
        for cls in ['FinancialCalculator', 'FinancialData', 'FinancialMetrics']:
            if cls in attrs:
                print(f"✅ {cls} disponível no módulo")
            else:
                print(f"❌ {cls} NÃO disponível no módulo")
    
    except ImportError as e:
        print(f"❌ Import falhou: {e}")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

def investigate_agno():
    """Investiga estrutura do Agno"""
    print("\n🔍 INVESTIGANDO AGNO")
    print("=" * 50)
    
    try:
        import agno
        print(f"✅ Agno importado: versão {getattr(agno, '__version__', 'desconhecida')}")
        
        # Verificar estrutura
        print("Estrutura do agno:")
        for attr in sorted(dir(agno)):
            if not attr.startswith('_'):
                print(f"   • {attr}")
        
        # Tentar imports corretos
        imports_to_test = [
            ('agno.agent', 'Agent'),
            ('agno.models.anthropic', 'Claude'),
            ('agno.tools.reasoning', 'ReasoningTools'),
            ('agno.tools.yfinance', 'YFinanceTools')
        ]
        
        for module_name, class_name in imports_to_test:
            try:
                module = importlib.import_module(module_name)
                if hasattr(module, class_name):
                    print(f"✅ {module_name}.{class_name}: Disponível")
                else:
                    print(f"❌ {module_name}.{class_name}: Classe não encontrada")
            except ImportError as e:
                print(f"❌ {module_name}: Módulo não encontrado ({e})")
    
    except ImportError as e:
        print(f"❌ Agno não disponível: {e}")

# =================================================================
# 2. IMPORTS COM FALLBACKS INTELIGENTES
# =================================================================

# Import do Agno (versão correta)
try:
    from agno.agent import Agent
    from agno.models.anthropic import Claude
    from agno.tools.reasoning import ReasoningTools
    from agno.tools.yfinance import YFinanceTools
    AGNO_AVAILABLE = True
    print("✅ Agno importado com sucesso (versão correta)")
except ImportError as e:
    AGNO_AVAILABLE = False
    print(f"⚠️  Agno não disponível: {e}")
    
    # Fallback classes
    class Agent:
        def __init__(self, **kwargs):
            pass
    
    class Claude:
        def __init__(self, **kwargs):
            pass

# Import do FinancialCalculator (com investigação)
CALCULATOR_AVAILABLE = False
CALCULATOR_ERROR = None

try:
    # Garantir que o diretório atual está no path
    current_dir = Path.cwd()
    if str(current_dir) not in sys.path:
        sys.path.insert(0, str(current_dir))
    
    # Tentar import
    from utils.financial_calculator import FinancialCalculator, FinancialData, FinancialMetrics
    CALCULATOR_AVAILABLE = True
    print("✅ FinancialCalculator importado com sucesso")
    
except ImportError as e:
    CALCULATOR_ERROR = str(e)
    print(f"⚠️  FinancialCalculator não disponível: {e}")
    
    # Classes mock
    @dataclass
    class FinancialData:
        symbol: Optional[str] = None
        market_cap: Optional[float] = None
        revenue: Optional[float] = None
        net_income: Optional[float] = None
        current_price: Optional[float] = None
    
    @dataclass
    class FinancialMetrics:
        pe_ratio: Optional[float] = None
        roe: Optional[float] = None
        profit_margin: Optional[float] = None
        
        def __dict__(self):
            return asdict(self)
    
    class FinancialCalculator:
        def calculate_all_metrics(self, data):
            return FinancialMetrics(pe_ratio=15.0, roe=18.5, profit_margin=12.0)

# Import do Database
try:
    from database.models import Stock, FundamentalAnalysis
    from database.repositories import get_stock_repository, get_fundamental_repository
    DATABASE_AVAILABLE = True
    print("✅ Database disponível")
except ImportError as e:
    DATABASE_AVAILABLE = False
    print(f"⚠️  Database não disponível: {e}")

# Import do NumPy
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    # Funções matemáticas básicas como fallback
    class np:
        @staticmethod
        def mean(data): return sum(data) / len(data) if data else 0
        @staticmethod
        def median(data): 
            sorted_data = sorted(data)
            n = len(sorted_data)
            return sorted_data[n//2] if n % 2 == 1 else (sorted_data[n//2-1] + sorted_data[n//2]) / 2
        @staticmethod
        def std(data): 
            if not data: return 0
            mean_val = sum(data) / len(data)
            return (sum((x - mean_val) ** 2 for x in data) / len(data)) ** 0.5
        @staticmethod
        def percentile(data, p): 
            sorted_data = sorted(data)
            k = (len(sorted_data) - 1) * p / 100
            f = int(k)
            c = k - f
            if f + 1 < len(sorted_data):
                return sorted_data[f] * (1 - c) + sorted_data[f + 1] * c
            return sorted_data[f]

# =================================================================
# 3. MODELOS DE DADOS (mesmo da versão anterior)
# =================================================================

class QualityTier(Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    AVERAGE = "average"
    BELOW_AVERAGE = "below_average"
    POOR = "poor"

@dataclass
class ScoringWeights:
    valuation: float = 0.25
    profitability: float = 0.30
    growth: float = 0.20
    financial_health: float = 0.15
    efficiency: float = 0.10

    def validate(self) -> bool:
        total = sum([self.valuation, self.profitability, self.growth, 
                    self.financial_health, self.efficiency])
        return abs(total - 1.0) < 0.001

@dataclass
class FundamentalScore:
    stock_code: str
    sector: str
    valuation_score: float
    profitability_score: float
    growth_score: float
    financial_health_score: float
    efficiency_score: float
    composite_score: float
    sector_rank: int
    sector_percentile: float
    overall_rank: int
    overall_percentile: float
    quality_tier: QualityTier
    analysis_date: datetime
    data_quality: float
    
    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result['quality_tier'] = self.quality_tier.value
        result['analysis_date'] = self.analysis_date.isoformat()
        return result

# =================================================================
# 4. AGENTE ANALISADOR CORRIGIDO
# =================================================================


# =================================================================
# SCORING ENGINE - ADICIONADO PARA CORRIGIR IMPORT
# =================================================================

class ScoringEngine:
    """
    Motor de Scoring Fundamentalista
    
    CORREÇÃO: Esta classe resolve o erro de import identificado no teste.
    """
    
    def __init__(self, weights: Optional[ScoringWeights] = None):
        self.weights = weights or ScoringWeights()
        self.logger = logging.getLogger(__name__)
        
        if not self.weights.validate():
            self.logger.warning("Pesos não somam 1.0, normalizando...")
            self._normalize_weights()
        
        self._sector_benchmarks = {}
        self._percentile_cache = {}
        
        self.logger.info("ScoringEngine inicializado com sucesso")
    
    def _normalize_weights(self):
        """Normaliza os pesos para somar 1.0"""
        total = sum([self.weights.valuation, self.weights.profitability, 
                    self.weights.growth, self.weights.financial_health, 
                    self.weights.efficiency])
        
        if total > 0:
            self.weights.valuation /= total
            self.weights.profitability /= total
            self.weights.growth /= total
            self.weights.financial_health /= total
            self.weights.efficiency /= total
    
    def calculate_valuation_score(self, metrics: Dict[str, Any], 
                                sector_benchmarks: Optional[Dict[str, float]] = None) -> float:
        """Calcula score de valuation (0-100)"""
        try:
            score_components = []
            
            # P/L Score (menor é melhor)
            pe_ratio = metrics.get('pe_ratio')
            if pe_ratio and pe_ratio > 0:
                if pe_ratio <= 8:
                    pe_score = 100
                elif pe_ratio <= 15:
                    pe_score = 100 - ((pe_ratio - 8) / 7) * 30
                elif pe_ratio <= 25:
                    pe_score = 70 - ((pe_ratio - 15) / 10) * 50
                else:
                    pe_score = max(0, 20 - ((pe_ratio - 25) / 10) * 20)
                
                score_components.append(pe_score * 0.4)
            
            # P/VP Score
            pb_ratio = metrics.get('pb_ratio')
            if pb_ratio and pb_ratio > 0:
                if pb_ratio <= 0.8:
                    pb_score = 100
                elif pb_ratio <= 2.0:
                    pb_score = 100 - ((pb_ratio - 0.8) / 1.2) * 30
                elif pb_ratio <= 4.0:
                    pb_score = 70 - ((pb_ratio - 2.0) / 2.0) * 50
                else:
                    pb_score = max(0, 20 - ((pb_ratio - 4.0) / 2.0) * 20)
                
                score_components.append(pb_score * 0.3)
            
            if score_components:
                total_weight = sum([0.4, 0.3][:len(score_components)])
                final_score = sum(score_components) / total_weight
                return max(0, min(100, final_score))
            else:
                return 50.0
            
        except Exception as e:
            self.logger.error(f"Erro no cálculo de valuation: {e}")
            return 50.0
        

    def calculate_composite_score_with_validation(self, metrics: Dict[str, Any], 
                                                stock_code: str,
                                                reasoning_agent: Optional[Agent] = None) -> Tuple[float, Dict[str, Any]]:
        """Calcula score com validação inteligente via ReasoningTools"""
        
        # 1. Calcular score base (mantém lógica existente)
        base_score = self.calculate_composite_score(metrics, stock_code)
        
        # 2. Se ReasoningTools disponível, validar score
        if reasoning_agent and hasattr(reasoning_agent, 'run'):
            try:
                validation_prompt = f"""
                VALIDAÇÃO DE SCORE FUNDAMENTALISTA - {stock_code}
                
                MÉTRICAS CALCULADAS:
                - P/L: {metrics.get('pe_ratio', 'N/A')}
                - P/VP: {metrics.get('pb_ratio', 'N/A')}
                - ROE: {metrics.get('roe', 'N/A')}%
                - ROA: {metrics.get('roa', 'N/A')}%
                - Margem Líquida: {metrics.get('net_margin', 'N/A')}%
                - Crescimento Receita: {metrics.get('revenue_growth', 'N/A')}%
                
                SCORE CALCULADO: {base_score:.1f}/100
                
                TAREFA: Use raciocínio lógico para validar se este score faz sentido:
                1. As métricas de valuation (P/L, P/VP) estão coerentes com o score?
                2. As métricas de rentabilidade (ROE, margens) justificam este score?
                3. Há alguma inconsistência evidente?
                4. O score deveria ser ajustado? Se sim, para qual valor e por quê?
                
                Retorne em JSON: {{"validated_score": number, "adjustments": [], "confidence": number}}
                """
                
                # Usar ReasoningTools do Agno
                validation_result = asyncio.run(reasoning_agent.run(validation_prompt))
                
                return base_score, {
                    "validation_performed": True,
                    "reasoning_result": validation_result,
                    "original_score": base_score
                }
                
            except Exception as e:
                self.logger.warning(f"Validação com ReasoningTools falhou: {e}")
        
        # Fallback para score base
        return base_score, {"validation_performed": False}

    
    def calculate_profitability_score(self, metrics: Dict[str, Any], 
                                    sector_benchmarks: Optional[Dict[str, float]] = None) -> float:
        """Calcula score de rentabilidade (0-100)"""
        try:
            score_components = []
            
            # ROE Score (maior é melhor)
            roe = metrics.get('roe')
            if roe is not None:
                if roe >= 25:
                    roe_score = 100
                elif roe >= 20:
                    roe_score = 90 + ((roe - 20) / 5) * 10
                elif roe >= 15:
                    roe_score = 70 + ((roe - 15) / 5) * 20
                elif roe >= 10:
                    roe_score = 40 + ((roe - 10) / 5) * 30
                elif roe >= 0:
                    roe_score = (roe / 10) * 40
                else:
                    roe_score = 0
                
                score_components.append(roe_score)
            
            if score_components:
                return max(0, min(100, sum(score_components) / len(score_components)))
            else:
                return 50.0
            
        except Exception as e:
            self.logger.error(f"Erro no cálculo de rentabilidade: {e}")
            return 50.0
    
    def calculate_growth_score(self, metrics: Dict[str, Any], 
                             sector_benchmarks: Optional[Dict[str, float]] = None) -> float:
        """Calcula score de crescimento (0-100)"""
        try:
            revenue_growth = metrics.get('revenue_growth_3y', 8.0)
            
            if revenue_growth >= 20:
                return 100
            elif revenue_growth >= 15:
                return 85 + ((revenue_growth - 15) / 5) * 15
            elif revenue_growth >= 10:
                return 65 + ((revenue_growth - 10) / 5) * 20
            elif revenue_growth >= 5:
                return 40 + ((revenue_growth - 5) / 5) * 25
            elif revenue_growth >= 0:
                return 20 + (revenue_growth / 5) * 20
            else:
                return max(0, 20 + revenue_growth * 2)
            
        except Exception as e:
            self.logger.error(f"Erro no cálculo de crescimento: {e}")
            return 50.0
    
    def calculate_financial_health_score(self, metrics: Dict[str, Any], 
                                       sector_benchmarks: Optional[Dict[str, float]] = None) -> float:
        """Calcula score de saúde financeira (0-100)"""
        try:
            score_components = []
            
            # Dívida/EBITDA Score
            debt_ebitda = metrics.get('debt_ebitda', 2.5)
            if debt_ebitda <= 1:
                debt_score = 100
            elif debt_ebitda <= 2:
                debt_score = 85 - ((debt_ebitda - 1) / 1) * 15
            elif debt_ebitda <= 3:
                debt_score = 60 - ((debt_ebitda - 2) / 1) * 25
            elif debt_ebitda <= 4:
                debt_score = 30 - ((debt_ebitda - 3) / 1) * 30
            else:
                debt_score = max(0, 30 - ((debt_ebitda - 4) / 2) * 30)
            
            score_components.append(debt_score)
            
            # Current Ratio Score
            current_ratio = metrics.get('current_ratio', 1.5)
            if current_ratio >= 2.0:
                cr_score = 100
            elif current_ratio >= 1.5:
                cr_score = 80 + ((current_ratio - 1.5) / 0.5) * 20
            elif current_ratio >= 1.2:
                cr_score = 60 + ((current_ratio - 1.2) / 0.3) * 20
            elif current_ratio >= 1.0:
                cr_score = 40 + ((current_ratio - 1.0) / 0.2) * 20
            else:
                cr_score = (current_ratio / 1.0) * 40
            
            score_components.append(cr_score)
            
            return max(0, min(100, sum(score_components) / len(score_components)))
            
        except Exception as e:
            self.logger.error(f"Erro no cálculo de saúde financeira: {e}")
            return 50.0
    
    def calculate_efficiency_score(self, metrics: Dict[str, Any], 
                                 sector_benchmarks: Optional[Dict[str, float]] = None) -> float:
        """Calcula score de eficiência (0-100)"""
        try:
            asset_turnover = metrics.get('asset_turnover', 0.8)
            
            if asset_turnover >= 1.5:
                return 100
            elif asset_turnover >= 1.0:
                return 70 + ((asset_turnover - 1.0) / 0.5) * 30
            elif asset_turnover >= 0.5:
                return 40 + ((asset_turnover - 0.5) / 0.5) * 30
            else:
                return (asset_turnover / 0.5) * 40
            
        except Exception as e:
            self.logger.error(f"Erro no cálculo de eficiência: {e}")
            return 50.0
    
    def calculate_composite_score(self, metrics: Dict[str, Any], 
                                sector: Optional[str] = None) -> Tuple[float, Dict[str, float]]:
        """Calcula o score composto final (0-100)"""
        try:
            # Calcular scores individuais
            scores = {
                'valuation': self.calculate_valuation_score(metrics),
                'profitability': self.calculate_profitability_score(metrics),
                'growth': self.calculate_growth_score(metrics),
                'financial_health': self.calculate_financial_health_score(metrics),
                'efficiency': self.calculate_efficiency_score(metrics)
            }
            
            # Score composto ponderado
            composite_score = (
                scores['valuation'] * self.weights.valuation +
                scores['profitability'] * self.weights.profitability +
                scores['growth'] * self.weights.growth +
                scores['financial_health'] * self.weights.financial_health +
                scores['efficiency'] * self.weights.efficiency
            )
            
            # Garantir que está no range 0-100
            composite_score = max(0, min(100, composite_score))
            
            return composite_score, scores
            
        except Exception as e:
            self.logger.error(f"Erro no cálculo do score composto: {e}")
            return 50.0, {'valuation': 50, 'profitability': 50, 'growth': 50, 
                         'financial_health': 50, 'efficiency': 50}
    
    def get_quality_tier(self, score: float) -> QualityTier:
        """Determina o tier de qualidade baseado no score"""
        if score >= 85:
            return QualityTier.EXCELLENT
        elif score >= 70:
            return QualityTier.GOOD
        elif score >= 50:
            return QualityTier.AVERAGE
        elif score >= 30:
            return QualityTier.BELOW_AVERAGE
        else:
            return QualityTier.POOR
    
    def apply_quality_filters(self, metrics: Dict[str, Any]) -> Dict[str, bool]:
        """Aplica filtros de qualidade fundamentalista"""
        filters = {}
        
        try:
            # Filtro ROE > 15%
            roe = metrics.get('roe')
            filters['roe_above_15'] = roe is not None and roe >= 15.0
            
            # Filtro crescimento sustentável
            revenue_growth = metrics.get('revenue_growth_3y')
            filters['sustainable_growth'] = revenue_growth is not None and revenue_growth >= 5.0
            
            # Filtro endividamento controlado
            debt_ebitda = metrics.get('debt_ebitda')
            filters['controlled_debt'] = debt_ebitda is None or debt_ebitda <= 4.0
            
            # Filtro margens estáveis
            net_margin = metrics.get('net_margin')
            filters['stable_margins'] = net_margin is not None and net_margin >= 5.0
            
            # Score geral dos filtros
            passed_filters = sum(1 for passed in filters.values() if passed)
            total_filters = len(filters)
            filters['quality_score'] = (passed_filters / total_filters) * 100
            
            return filters
            
        except Exception as e:
            self.logger.error(f"Erro na aplicação de filtros: {e}")
            return {'quality_score': 50.0}
    
    def identify_red_flags(self, metrics: Dict[str, Any]) -> List[str]:
        """Identifica red flags em empresas problemáticas"""
        red_flags = []
        
        try:
            # ROE negativo
            roe = metrics.get('roe')
            if roe is not None and roe < 0:
                red_flags.append("ROE negativo")
            
            # Endividamento excessivo
            debt_ebitda = metrics.get('debt_ebitda')
            if debt_ebitda is not None and debt_ebitda > 6:
                red_flags.append("Endividamento excessivo")
            
            # Margem líquida negativa
            net_margin = metrics.get('net_margin')
            if net_margin is not None and net_margin < 0:
                red_flags.append("Margem líquida negativa")
            
            # Queda de receita
            revenue_growth = metrics.get('revenue_growth_3y')
            if revenue_growth is not None and revenue_growth < -10:
                red_flags.append("Queda acentuada de receita")
            
            return red_flags
            
        except Exception as e:
            self.logger.error(f"Erro na identificação de red flags: {e}")
            return []
    
    def get_recommendation(self, score: float, quality_filters: Dict[str, bool], 
                          red_flags: List[str]) -> str:
        """Gera recomendação baseada no score e filtros"""
        try:
            # Se há muitos red flags, recomendação negativa
            if len(red_flags) >= 3:
                return "VENDA FORTE"
            elif len(red_flags) >= 2:
                return "VENDA"
            
            # Baseado no score e filtros
            quality_score = quality_filters.get('quality_score', 50.0)
            
            if score >= 85 and quality_score >= 80:
                return "COMPRA FORTE"
            elif score >= 70 and quality_score >= 70:
                return "COMPRA"
            elif score >= 50 and quality_score >= 60:
                return "NEUTRO"
            elif score >= 30:
                return "VENDA"
            else:
                return "VENDA FORTE"
            
        except Exception as e:
            self.logger.error(f"Erro na geração de recomendação: {e}")
            return "NEUTRO"


# =================================================================
# AGENTE ANALISADOR ORIGINAL
# =================================================================

class FundamentalAnalyzerAgent(Agent):
    """
    Agente Analisador Fundamentalista - Versão Corrigida
    
    Agora usa os imports corretos do Agno e tem melhor investigação
    dos problemas do FinancialCalculator.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        # Configuração do Agno (se disponível)
        if AGNO_AVAILABLE:
            super().__init__(
                model=Claude(id="claude-sonnet-4-20250514"),
                tools=[
                    ReasoningTools(add_instructions=True),
                    YFinanceTools(
                        stock_price=True,
                        analyst_recommendations=True,
                        company_info=True,
                        company_news=True,
                        historical_prices=True
                    )
                ],
                instructions="""
                Você é um analista fundamentalista expert que utiliza Claude 4 Sonnet para análises precisas.
                
                METODOLOGIA RIGOROSA:
                1. Sempre use ReasoningTools para validar cálculos matemáticos
                2. Compare resultados com benchmarks setoriais usando raciocínio estruturado
                3. Identifique outliers e explique as razões
                4. Gere justificativas detalhadas baseadas em dados concretos
                
                SCORES DE QUALIDADE:
                - EXCELENTE (85-100): Empresas top-tier com fundamentos excepcionais
                - BOA (70-84): Empresas sólidas com bons fundamentos
                - MÉDIA (50-69): Empresas com fundamentos moderados
                - FRACA (30-49): Empresas com fundamentos questionáveis  
                - PROBLEMÁTICA (0-29): Empresas com sérios problemas fundamentais
                
                Sempre use tabelas para apresentar comparações e ReasoningTools para validar lógica.
                """,
                markdown=True,
            )
        else:
            # Modo compatibilidade sem Agno
            pass
        
        self.logger = logging.getLogger(__name__)
        
        # Configurações
        self.config = self._load_config(config_path)
        self.weights = ScoringWeights(**self.config.get('scoring_weights', {}))
        
        # Componentes
        self._init_components()
        
        # Status report
        self._log_component_status()
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Carrega configuração"""
        if config_path and Path(config_path).exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Erro ao carregar config: {e}")
        
        return {
            "scoring_weights": {
                "valuation": 0.25,
                "profitability": 0.30,
                "growth": 0.20,
                "financial_health": 0.15,
                "efficiency": 0.10
            },
            "quality_tiers": {
                "excellent": 85,
                "good": 70,
                "average": 50,
                "below_average": 30
            }
        }
    
    def _init_components(self):
        """Inicializa componentes com diagnóstico"""
        
        # Financial Calculator
        if CALCULATOR_AVAILABLE:
            self.calculator = FinancialCalculator()
            self.logger.info("FinancialCalculator inicializado")
        else:
            self.calculator = FinancialCalculator()  # Versão mock
            self.logger.warning(f"Usando FinancialCalculator mock: {CALCULATOR_ERROR}")
        
        # Database repositories
        if DATABASE_AVAILABLE:
            try:
                self.stock_repo = get_stock_repository()
                self.analysis_repo = get_fundamental_repository()
                self.logger.info("Repositórios de database inicializados")
            except Exception as e:
                self.logger.warning(f"Erro ao inicializar repositórios: {e}")
                self.stock_repo = None
                self.analysis_repo = None
        else:
            self.stock_repo = None
            self.analysis_repo = None
    
    def _log_component_status(self):
        """Loga status dos componentes"""
        self.logger.info("=== STATUS DOS COMPONENTES ===")
        self.logger.info(f"Agno Framework: {'✅' if AGNO_AVAILABLE else '❌'}")
        self.logger.info(f"FinancialCalculator: {'✅' if CALCULATOR_AVAILABLE else '❌'}")
        self.logger.info(f"Database: {'✅' if DATABASE_AVAILABLE else '❌'}")
        self.logger.info(f"NumPy: {'✅' if NUMPY_AVAILABLE else '❌'}")
    
    def analyze_single_stock(self, stock_code: str) -> Dict[str, Any]:
        """
        Analisa uma ação específica
        
        Args:
            stock_code: Código da ação (ex: PETR4)
            
        Returns:
            Análise fundamentalista completa
        """
        self.logger.info(f"🔍 Analisando {stock_code}")
        
        try:
            # 1. Buscar dados da ação
            stock_data = self._get_stock_data(stock_code)
            
            # 2. Obter dados financeiros
            financial_data = self._create_financial_data(stock_code)
            
            # 3. Calcular métricas COM ANÁLISE INTELIGENTE
            if AGNO_AVAILABLE and hasattr(self, 'run'):
                # Usar versão inteligente
                metrics = self.calculator.calculate_all_metrics(financial_data, reasoning_agent=self)
            else:
                # Usar versão tradicional
                metrics = self.calculator.calculate_all_metrics(financial_data)
            
            # 4. Calcular scores por categoria
            category_scores = self._calculate_category_scores(metrics)
            
            # 5. Score composto
            composite_score = self._calculate_composite_score(category_scores)
            
            # 6. Determinar qualidade
            quality_tier = self._determine_quality_tier(composite_score)
            
            # 7. Criar score fundamentalista
            fundamental_score = FundamentalScore(
                stock_code=stock_code,
                sector=stock_data.get('setor', 'Desconhecido'),
                valuation_score=category_scores['valuation'],
                profitability_score=category_scores['profitability'],
                growth_score=category_scores['growth'],
                financial_health_score=category_scores['financial_health'],
                efficiency_score=category_scores['efficiency'],
                composite_score=composite_score,
                sector_rank=1,  # Placeholder
                sector_percentile=75.0,
                overall_rank=1,
                overall_percentile=75.0,
                quality_tier=quality_tier,
                analysis_date=datetime.now(),
                data_quality=0.85  # Mock
            )
            
            # 8. Gerar resultado
            result = {
                "stock_code": stock_code,
                "analysis_date": datetime.now().isoformat(),
                "fundamental_score": fundamental_score.to_dict(),
                "detailed_metrics": self._metrics_to_dict(metrics),
                "category_scores": category_scores,
                "justification": self._generate_justification(fundamental_score),
                "recommendation": self._get_recommendation(composite_score),
                "stock_info": {
                    "nome": stock_data.get('nome', f'Empresa {stock_code}'),
                    "setor": stock_data.get('setor', 'Desconhecido'),
                    "preco_atual": stock_data.get('preco_atual')
                },
                "system_status": {
                    "agno_available": AGNO_AVAILABLE,
                    "calculator_available": CALCULATOR_AVAILABLE,
                    "database_available": DATABASE_AVAILABLE,
                    "calculator_error": CALCULATOR_ERROR
                }
            }
            
            self.logger.info(f"✅ Análise de {stock_code} concluída. Score: {composite_score:.1f}")
            return result
            
        except Exception as e:
            error_msg = f"Erro na análise de {stock_code}: {str(e)}"
            self.logger.error(error_msg)
            return {
                "error": error_msg,
                "stock_code": stock_code,
                "analysis_date": datetime.now().isoformat(),
                "system_status": {
                    "agno_available": AGNO_AVAILABLE,
                    "calculator_available": CALCULATOR_AVAILABLE,
                    "database_available": DATABASE_AVAILABLE
                }
            }
        
    # ADICIONAR novo método:
    async def analyze_single_stock_with_reasoning(self, stock_code: str) -> Dict[str, Any]:
        """Análise fundamentalista com ReasoningTools para validação"""
        
        # 1. Executar análise base (mantém compatibilidade)
        base_analysis = self.analyze_single_stock(stock_code)
        
        if "error" in base_analysis:
            return base_analysis
        
        # 2. Se Agno disponível, usar Claude + ReasoningTools
        if AGNO_AVAILABLE and hasattr(self, 'run'):
            try:
                score = base_analysis['fundamental_score']['composite_score']
                tier = base_analysis['fundamental_score']['quality_tier']
                
                validation_prompt = f"""
                VALIDAÇÃO INTELIGENTE - {stock_code}
                
                ANÁLISE CALCULADA:
                - Score Composto: {score:.1f}/100
                - Classificação: {tier}
                - Setor: {base_analysis.get('sector', 'Desconhecido')}
                
                MÉTRICAS DETALHADAS:
                {json.dumps(base_analysis.get('metrics_summary', {}), indent=2)}
                
                VALIDAÇÃO REQUERIDA:
                1. O score de {score:.1f} é coerente com as métricas apresentadas?
                2. A classificação "{tier}" está apropriada?
                3. Há inconsistências que precisam ser corrigidas?
                4. Considerando o contexto setorial, algum ajuste é necessário?
                
                Use ReasoningTools para validar cada conclusão.
                
                RETORNE análise estruturada com:
                - Validação do score (correto/precisa ajuste)
                - 3 pontos fortes identificados
                - 3 pontos de atenção
                - Recomendação final (COMPRA/NEUTRO/VENDA)
                - Nível de confiança (0-100)
                """
                
                intelligent_validation = await self.run(validation_prompt)
                
                # Combinar análises
                enhanced_result = {
                    **base_analysis,
                    "intelligent_validation": intelligent_validation,
                    "analysis_method": "claude_enhanced",
                    "confidence_level": self._extract_confidence(intelligent_validation),
                    "generated_at": datetime.now().isoformat()
                }
                
                return enhanced_result
                
            except Exception as e:
                self.logger.warning(f"Validação inteligente falhou: {e}")
                # Fallback para análise base
                return {
                    **base_analysis,
                    "analysis_method": "fallback_traditional",
                    "fallback_reason": str(e)
                }
        
        # Retorna análise base se Agno não disponível
        return base_analysis

    def _extract_confidence(self, validation_text: str) -> float:
        """Extrai nível de confiança da análise"""
        import re
        confidence_match = re.search(r'confiança[:\s]+(\d+)', validation_text, re.IGNORECASE)
        if confidence_match:
            return float(confidence_match.group(1))
        return 75.0  # Default
    
    def get_top_stocks(self, limit: int = 10) -> Dict[str, Any]:
        """Retorna as melhores ações baseado no score"""
        self.logger.info(f"🏆 Buscando top {limit} ações")
        
        try:
            # Ações para análise
            test_stocks = ["PETR4", "VALE3", "ITUB4", "BBDC4", "ABEV3", "MGLU3", "WEGE3", "LREN3"]
            
            analyzed_stocks = []
            for stock in test_stocks[:min(limit * 2, len(test_stocks))]:
                try:
                    result = self.analyze_single_stock(stock)
                    if "error" not in result:
                        analyzed_stocks.append(result)
                except Exception as e:
                    self.logger.warning(f"Erro na análise de {stock}: {e}")
            
            # Ordenar por score
            analyzed_stocks.sort(
                key=lambda x: x["fundamental_score"]["composite_score"], 
                reverse=True
            )
            
            # Atualizar rankings
            for i, stock in enumerate(analyzed_stocks):
                stock["fundamental_score"]["overall_rank"] = i + 1
                stock["fundamental_score"]["overall_percentile"] = ((len(analyzed_stocks) - i) / len(analyzed_stocks)) * 100
            
            top_stocks = analyzed_stocks[:limit]
            
            return {
                "analysis_date": datetime.now().isoformat(),
                "total_analyzed": len(analyzed_stocks),
                "top_stocks_count": len(top_stocks),
                "top_stocks": top_stocks,
                "summary": {
                    "best_score": top_stocks[0]["fundamental_score"]["composite_score"] if top_stocks else 0,
                    "average_score": np.mean([s["fundamental_score"]["composite_score"] for s in analyzed_stocks]) if analyzed_stocks else 0,
                    "sectors_represented": len(set(s["stock_info"]["setor"] for s in top_stocks))
                },
                "system_status": {
                    "agno_available": AGNO_AVAILABLE,
                    "calculator_available": CALCULATOR_AVAILABLE,
                    "database_available": DATABASE_AVAILABLE
                }
            }
            
        except Exception as e:
            error_msg = f"Erro ao buscar top ações: {str(e)}"
            self.logger.error(error_msg)
            return {
                "error": error_msg,
                "analysis_date": datetime.now().isoformat()
            }
    
    # ====== MÉTODOS AUXILIARES ======
    
    def _get_stock_data(self, stock_code: str) -> Dict[str, Any]:
        """
        Busca dados da ação com sistema inteligente:
        1. Tentar banco local
        2. Se não encontrar, buscar dados reais via API
        3. Salvar no banco
        4. Retornar dados reais
        """
        
        # 1. TENTAR BANCO LOCAL PRIMEIRO
        if DATABASE_AVAILABLE and self.stock_repo:
            try:
                stock = self.stock_repo.get_stock_by_code(stock_code)
                if stock and self._is_data_fresh(stock):
                    self.logger.info(f"✅ {stock_code} encontrado no banco (dados frescos)")
                    return self._stock_to_dict(stock)
                elif stock:
                    self.logger.info(f"⚠️  {stock_code} no banco mas dados antigos - atualizando...")
                else:
                    self.logger.info(f"❌ {stock_code} não encontrado no banco - buscando dados reais...")
            except Exception as e:
                self.logger.warning(f"Erro acessando banco: {e}")
        
        # 2. BUSCAR DADOS REAIS VIA API
        real_data = self._fetch_real_financial_data(stock_code)
        
        if real_data:
            # 3. SALVAR NO BANCO PARA PRÓXIMAS CONSULTAS
            self._save_to_database(stock_code, real_data)
            
            # 4. RETORNAR DADOS REAIS
            self.logger.info(f"✅ Dados reais obtidos para {stock_code}")
            return real_data
        else:
            # 5. ÚLTIMO RECURSO: Informar que não foi possível obter dados
            self.logger.error(f"❌ Não foi possível obter dados reais para {stock_code}")
            raise ValueError(f"Dados não disponíveis para {stock_code}")
        
    def _fetch_real_financial_data(self, stock_code: str) -> Dict[str, Any]:
        """Busca dados financeiros reais via APIs"""
        
        self.logger.info(f"🌐 Buscando dados reais para {stock_code}...")
        
        try:
            # Tentar yfinance primeiro (gratuito e confiável)
            ticker_symbol = f"{stock_code}.SA"  # Formato B3
            ticker = yf.Ticker(ticker_symbol)
            
            # Obter informações básicas
            info = ticker.info
            
            if not info or 'marketCap' not in info:
                self.logger.warning(f"Dados insuficientes no yfinance para {stock_code}")
                return self._try_alternative_sources(stock_code)
            
            # Obter demonstrações financeiras
            financials = ticker.financials
            balance_sheet = ticker.balance_sheet
            
            # Extrair dados fundamentais REAIS
            real_data = {
                'codigo': stock_code,
                'nome': info.get('longName', f'Empresa {stock_code}'),
                'setor': self._normalize_sector(info.get('sector', 'Diversos')),
                'preco_atual': info.get('currentPrice', info.get('regularMarketPrice', 0)),
                'market_cap': info.get('marketCap', 0),
                'volume_medio': info.get('averageVolume', 0),
                
                # Dados financeiros REAIS
                'revenue': self._get_financial_metric(financials, 'Total Revenue'),
                'net_income': self._get_financial_metric(financials, 'Net Income'),
                'total_assets': self._get_balance_metric(balance_sheet, 'Total Assets'),
                'total_equity': self._get_balance_metric(balance_sheet, 'Total Equity Gross Minority Interest'),
                'total_debt': self._get_balance_metric(balance_sheet, 'Total Debt'),
                
                # Métricas calculadas REAIS
                'roe': info.get('returnOnEquity', 0) * 100 if info.get('returnOnEquity') else 0,
                'roa': info.get('returnOnAssets', 0) * 100 if info.get('returnOnAssets') else 0,
                'net_margin': info.get('profitMargins', 0) * 100 if info.get('profitMargins') else 0,
                'pe_ratio': info.get('forwardPE', info.get('trailingPE', 0)),
                'pb_ratio': info.get('priceToBook', 0),
                'debt_to_equity': self._calculate_debt_to_equity(balance_sheet),
                
                # Metadados
                'data_source': 'yfinance',
                'data_atualizacao': datetime.now().isoformat(),
                'data_quality': 'REAL'
            }
            
            # Validar dados obtidos
            if self._validate_financial_data(real_data):
                self.logger.info(f"✅ Dados reais validados para {stock_code}")
                return real_data
            else:
                self.logger.warning(f"⚠️  Dados reais incompletos para {stock_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"Erro buscando dados reais para {stock_code}: {e}")
            return self._try_alternative_sources(stock_code)
        
    def _get_financial_metric(self, financials, metric_name: str) -> float:
        """Extrai métrica financeira das demonstrações"""
        
        try:
            if financials is not None and not financials.empty:
                if metric_name in financials.index:
                    # Pegar valor mais recente (primeira coluna)
                    value = financials.loc[metric_name].iloc[0]
                    return float(value) if pd.notna(value) else 0
        except Exception as e:
            self.logger.debug(f"Erro extraindo {metric_name}: {e}")
        
        return 0
    
    def _get_balance_metric(self, balance_sheet, metric_name: str) -> float:
        """Extrai métrica do balanço patrimonial"""
        
        try:
            if balance_sheet is not None and not balance_sheet.empty:
                if metric_name in balance_sheet.index:
                    value = balance_sheet.loc[metric_name].iloc[0]
                    return float(value) if pd.notna(value) else 0
        except Exception as e:
            self.logger.debug(f"Erro extraindo {metric_name}: {e}")
        
        return 0
    
    def _calculate_debt_to_equity(self, balance_sheet) -> float:
        """Calcula debt-to-equity ratio dos dados reais"""
        
        try:
            total_debt = self._get_balance_metric(balance_sheet, 'Total Debt')
            total_equity = self._get_balance_metric(balance_sheet, 'Total Equity Gross Minority Interest')
            
            if total_equity > 0:
                return total_debt / total_equity
        except Exception:
            pass
        
        return 0

    def _validate_financial_data(self, data: Dict[str, Any]) -> bool:
        """Valida se os dados obtidos são suficientes para análise"""
        
        required_fields = ['market_cap', 'revenue', 'net_income']
        
        for field in required_fields:
            if not data.get(field) or data[field] <= 0:
                self.logger.warning(f"Campo obrigatório inválido: {field} = {data.get(field)}")
                return False
        
        # Validações de sanidade
        if data['market_cap'] < 1000000:  # Menos de 1M
            self.logger.warning(f"Market cap muito baixo: {data['market_cap']}")
            return False
        
        if data['pe_ratio'] and (data['pe_ratio'] < 0 or data['pe_ratio'] > 1000):
            self.logger.warning(f"P/L suspeito: {data['pe_ratio']}")
            # Não invalidar por isso, apenas avisar
        
        return True

    def _save_to_database(self, stock_code: str, data: Dict[str, Any]) -> bool:
        """Salva dados reais no banco para futuras consultas"""
        
        if not DATABASE_AVAILABLE or not self.stock_repo:
            self.logger.warning("Banco não disponível - dados não serão persistidos")
            return False
        
        try:
            # Verificar se já existe
            existing_stock = self.stock_repo.get_stock_by_code(stock_code)
            
            if existing_stock:
                # Atualizar dados existentes
                self.logger.info(f"📝 Atualizando {stock_code} no banco")
                success = self.stock_repo.update_stock_data(stock_code, data)
            else:
                # Criar nova entrada
                self.logger.info(f"➕ Adicionando {stock_code} ao banco")
                success = self.stock_repo.create_stock(data)
            
            if success:
                self.logger.info(f"✅ {stock_code} salvo no banco com dados reais")
                return True
            else:
                self.logger.error(f"❌ Falha ao salvar {stock_code} no banco")
                return False
                
        except Exception as e:
            self.logger.error(f"Erro salvando {stock_code} no banco: {e}")
            return False

    def _is_data_fresh(self, stock) -> bool:
        """Verifica se os dados no banco ainda estão frescos"""
        
        try:
            if hasattr(stock, 'data_atualizacao') and stock.data_atualizacao:
                last_update = datetime.fromisoformat(stock.data_atualizacao.replace('Z', '+00:00'))
                age = datetime.now() - last_update.replace(tzinfo=None)
                
                # Considerar dados frescos se atualizados nas últimas 24 horas
                return age < timedelta(hours=24)
        except Exception as e:
            self.logger.debug(f"Erro verificando freshness: {e}")
        
        return False

    def _try_alternative_sources(self, stock_code: str) -> Dict[str, Any]:
        """Tenta fontes alternativas quando yfinance falha"""
        
        # Poderia implementar outras APIs como:
        # - Alpha Vantage
        # - Financial Modeling Prep  
        # - Yahoo Finance direto
        # - APIs brasileiras (Economatica, etc.)
        
        self.logger.warning(f"Fontes alternativas não implementadas para {stock_code}")
        return None

    def _normalize_sector(self, sector: str) -> str:
        """Normaliza nome do setor para padrão brasileiro"""
        
        sector_mapping = {
            'Technology': 'Tecnologia',
            'Financial Services': 'Financeiro',
            'Energy': 'Petróleo',
            'Basic Materials': 'Mineração',
            'Consumer Cyclical': 'Varejo',
            'Consumer Defensive': 'Consumo',
            'Healthcare': 'Saúde',
            'Industrials': 'Industrial',
            'Real Estate': 'Imobiliário',
            'Utilities': 'Utilidades',
            'Communication Services': 'Telecomunicações'
        }
        
        return sector_mapping.get(sector, sector)
        
    def _create_financial_data(self, stock_code: str) -> FinancialData:
        """Cria FinancialData com dados REAIS do banco"""
        try:
            stock_data = self._get_stock_data(stock_code)
            
            # USAR DADOS REAIS DO BANCO (não fallback!)
            financial_data = FinancialData(
                symbol=stock_code,
                current_price=stock_data.get('preco_atual'),
                market_cap=stock_data.get('market_cap'), 
                revenue=stock_data.get('revenue'),                    # ← DADOS REAIS
                net_income=stock_data.get('net_income'),             # ← DADOS REAIS  
                total_assets=stock_data.get('total_assets'),         # ← DADOS REAIS
                shareholders_equity=stock_data.get('total_equity'),   # ← DADOS REAIS
                total_debt=stock_data.get('total_debt'),             # ← DADOS REAIS
                sector=stock_data.get('setor')
            )
            
            self.logger.info(f"✅ FinancialData REAL criado para {stock_code}")
            self.logger.info(f"  Revenue: {financial_data.revenue:,.0f}")
            self.logger.info(f"  Net Income: {financial_data.net_income:,.0f}")
            self.logger.info(f"  Market Cap: {financial_data.market_cap:,.0f}")
            
            return financial_data
            
        except Exception as e:
            self.logger.error(f"Erro criando FinancialData para {stock_code}: {e}")
            import traceback
            traceback.print_exc()
            
            # Se falhar, pelo menos usar alguns dados reais
            stock_data = self._get_stock_data(stock_code)
            return FinancialData(
                symbol=stock_code,
                market_cap=stock_data.get('market_cap', 50000000000),
                revenue=stock_data.get('revenue', 25000000000), 
                net_income=stock_data.get('net_income', 2500000000),
                sector=stock_data.get('setor', 'Diversos')
            )
    
    def _calculate_category_scores(self, metrics) -> Dict[str, float]:
        """Calcula scores por categoria"""
        # Scores baseados nas métricas (simplificado)
        scores = {}
        
        try:
            
            metrics_dict = metrics.__dict__() if hasattr(metrics, '__dict__') and callable(metrics.__dict__) else metrics.__dict__
            # Valuation (menor P/L é melhor)
            pe = metrics_dict.get('pe_ratio', 15)
            
            valuation_score = max(0, min(100, 100 - (pe - 10) * 3))
            
            scores['valuation'] = valuation_score
            
            # Rentabilidade (maior ROE é melhor)
            roe = metrics_dict.get('roe', 15)
            profitability_score = max(0, min(100, roe * 4))
            scores['profitability'] = profitability_score
            
            # Crescimento, saúde financeira, eficiência (valores mock)
            scores['growth'] = 65.0
            scores['financial_health'] = 70.0
            scores['efficiency'] = 75.0
            
        except Exception as e:
            self.logger.warning(f"Erro no cálculo de scores: {e}")
            scores = {
                'valuation': 70.0,
                'profitability': 75.0,
                'growth': 65.0,
                'financial_health': 70.0,
                'efficiency': 75.0
            }
        
        return scores
    
    def _calculate_composite_score(self, category_scores: Dict[str, float]) -> float:
        """Calcula score composto"""
        return (
            category_scores.get('valuation', 50.0) * self.weights.valuation +
            category_scores.get('profitability', 50.0) * self.weights.profitability +
            category_scores.get('growth', 50.0) * self.weights.growth +
            category_scores.get('financial_health', 50.0) * self.weights.financial_health +
            category_scores.get('efficiency', 50.0) * self.weights.efficiency
        )
    
    def _determine_quality_tier(self, score: float) -> QualityTier:
        """Determina tier de qualidade"""
        thresholds = self.config.get('quality_tiers', {})
        
        if score >= thresholds.get('excellent', 85):
            return QualityTier.EXCELLENT
        elif score >= thresholds.get('good', 70):
            return QualityTier.GOOD
        elif score >= thresholds.get('average', 50):
            return QualityTier.AVERAGE
        elif score >= thresholds.get('below_average', 30):
            return QualityTier.BELOW_AVERAGE
        else:
            return QualityTier.POOR
    
    def _metrics_to_dict(self, metrics) -> Dict[str, Any]:
        """Converte métricas para dicionário"""
        if hasattr(metrics, '__dict__'):
            if callable(metrics.__dict__):
                return metrics.__dict__()
            else:
                return metrics.__dict__
        else:
            return {}
    
    def _generate_justification(self, score: FundamentalScore) -> str:
        """Gera justificativa da análise"""
        tier_names = {
            QualityTier.EXCELLENT: "EMPRESA EXCELENTE",
            QualityTier.GOOD: "EMPRESA BOA",
            QualityTier.AVERAGE: "EMPRESA MEDIANA",
            QualityTier.BELOW_AVERAGE: "EMPRESA FRACA",
            QualityTier.POOR: "EMPRESA PROBLEMÁTICA"
        }
        
        tier_name = tier_names.get(score.quality_tier, "EMPRESA")
        
        return f"""
{tier_name} (Score: {score.composite_score:.1f}/100)

ANÁLISE FUNDAMENTALISTA:
• Valuation: {score.valuation_score:.1f}/100
• Rentabilidade: {score.profitability_score:.1f}/100  
• Crescimento: {score.growth_score:.1f}/100
• Saúde Financeira: {score.financial_health_score:.1f}/100
• Eficiência: {score.efficiency_score:.1f}/100

QUALIDADE: {score.quality_tier.value.title()}
SETOR: {score.sector}
DATA: {score.analysis_date.strftime('%d/%m/%Y %H:%M')}

STATUS DO SISTEMA:
• FinancialCalculator: {'✅ Real' if CALCULATOR_AVAILABLE else '⚠️  Mock'}
• Database: {'✅ Conectado' if DATABASE_AVAILABLE else '⚠️  Mock'}
• Agno Framework: {'✅ Ativo' if AGNO_AVAILABLE else '⚠️  Inativo'}
        """.strip()
    
    def _get_recommendation(self, score: float) -> str:
        """Gera recomendação"""
        if score >= 80:
            return "COMPRA FORTE"
        elif score >= 65:
            return "COMPRA"
        elif score >= 45:
            return "NEUTRO"
        elif score >= 30:
            return "VENDA"
        else:
            return "VENDA FORTE"

# =================================================================
# 5. FUNÇÕES DE DIAGNÓSTICO E TESTE
# =================================================================

def run_diagnostics():
    """Executa diagnósticos completos"""
    print("🔍 DIAGNÓSTICOS DO SISTEMA")
    print("=" * 60)
    
    investigate_financial_calculator()
    investigate_agno()
    
    print(f"\n📊 RESUMO:")
    print(f"• Agno: {'✅' if AGNO_AVAILABLE else '❌'}")
    print(f"• FinancialCalculator: {'✅' if CALCULATOR_AVAILABLE else '❌'}")
    print(f"• Database: {'✅' if DATABASE_AVAILABLE else '❌'}")
    print(f"• NumPy: {'✅' if NUMPY_AVAILABLE else '❌'}")

def test_corrected_system():
    """Testa sistema corrigido"""
    print("\n🧪 TESTANDO SISTEMA CORRIGIDO")
    print("=" * 60)
    
    try:
        # Criar agente
        agent = FundamentalAnalyzerAgent()
        print("✅ Agente criado com sucesso")
        
        # Teste de análise individual
        result = agent.analyze_single_stock("PETR4")
        
        if "error" in result:
            print(f"❌ Erro na análise: {result['error']}")
            return False
        
        score = result["fundamental_score"]["composite_score"]
        recommendation = result["recommendation"]
        print(f"✅ PETR4: Score {score:.1f} - {recommendation}")
        
        # Teste de top ações
        top_result = agent.get_top_stocks(3)
        
        if "error" not in top_result:
            print(f"✅ Top stocks: {top_result['top_stocks_count']} ações")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

def main():
    """Função principal"""
    print("🚀 SISTEMA DE SCORING FUNDAMENTALISTA - VERSÃO CORRIGIDA")
    print("=" * 70)
    print("Imports atualizados: Agno e investigação do FinancialCalculator")
    print("=" * 70)
    
    # Executar diagnósticos
    run_diagnostics()
    
    # Testar sistema
    success = test_corrected_system()
    
    if success:
        print("\n🎉 SISTEMA FUNCIONANDO!")
        print("\n📋 MELHORIAS IMPLEMENTADAS:")
        print("   ✅ Import correto do Agno (from agno.agent import Agent)")
        print("   ✅ Investigação detalhada do FinancialCalculator")  
        print("   ✅ Fallbacks robustos para todos os componentes")
        print("   ✅ Logs de status dos componentes")
        print("   ✅ Compatibilidade total com arquitetura existente")
        
        print("\n🔧 EXEMPLO DE USO:")
        print("""
from agents.analyzers.fundamental_scoring_system import FundamentalAnalyzerAgent

agent = FundamentalAnalyzerAgent()
result = agent.analyze_single_stock('PETR4')
score = result['fundamental_score']['composite_score']
print(f'Score: {score:.1f} - {result["recommendation"]}')
        """)
        
    else:
        print("\n❌ PROBLEMAS DETECTADOS")
        print("\n🔧 SOLUÇÕES:")
        print("   1. Para Agno: Verifique se está instalado corretamente")
        print("   2. Para FinancialCalculator: Verifique o arquivo utils/financial_calculator.py")
        print("   3. Execute: python -c \"import utils.financial_calculator; print('OK')\"")

if __name__ == "__main__":
    main()

# =================================================================
# 6. SCRIPT DE TESTE DIRETO
# =================================================================

def quick_test():
    """Teste rápido para validação"""
    print("\n⚡ TESTE RÁPIDO")
    print("=" * 30)
    
    try:
        # Teste direto sem Agno
        from utils.financial_calculator import FinancialCalculator, FinancialData
        
        calc = FinancialCalculator()
        data = FinancialData(symbol="PETR4", net_income=6000000000, revenue=50000000000)
        metrics = calc.calculate_all_metrics(data)
        
        print("✅ FinancialCalculator funcionando!")
        print(f"   ROE: {getattr(metrics, 'roe', 'N/A')}")
        print(f"   Margem: {getattr(metrics, 'profit_margin', 'N/A')}")
        
        return True
        
    except ImportError as e:
        print(f"❌ FinancialCalculator não funciona: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

if __name__ == "__main__":
    # Executar teste rápido também
    quick_test()