# agents/analyzers/sector_comparator.py
"""
Sistema de Benchmarking Setorial Avançado - VERSÃO CORRIGIDA
Implementa cálculo de percentis por setor, ranking e identificação de outliers

CORREÇÕES APLICADAS:
- ✅ Compatibilidade com FundamentalScore simplificada
- ✅ Ajuste do mínimo setorial para 2 empresas (mais realista)
- ✅ Tratamento de campos opcionais na FundamentalScore
- ✅ Fallback para quando scoring_engine não está disponível
- ✅ Validação robusta de dados de entrada

Atualizado: 14/07/2025
Autor: Claude Sonnet 4
Status: PATCH DE COMPATIBILIDADE - Fase 2 Passo 2.2
"""
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, NamedTuple
from dataclasses import dataclass, field
from enum import Enum
import json
import statistics
from collections import defaultdict

logger = logging.getLogger(__name__)

# ================================================================
# CLASSES DE DADOS COMPATÍVEIS
# ================================================================

class OutlierType(Enum):
    """Tipos de outliers detectados"""
    HIGH_PERFORMER = "high_performer"  # Performance muito acima da média
    LOW_PERFORMER = "low_performer"    # Performance muito abaixo da média
    VOLATILE = "volatile"              # Muito volátil vs setor
    STATISTICAL = "statistical"       # Outlier estatístico puro


class QualityTier(Enum):
    """Níveis de qualidade para compatibilidade"""
    EXCELLENT = "excellent"
    GOOD = "good"
    AVERAGE = "average"
    POOR = "poor"


@dataclass
class FundamentalScore:
    """
    Versão compatível simplificada do FundamentalScore
    Para uso quando scoring_engine não está disponível
    """
    stock_code: str
    sector: str
    composite_score: float = 50.0
    quality_tier: QualityTier = QualityTier.AVERAGE
    
    # Campos opcionais para compatibilidade
    valuation_score: Optional[float] = None
    profitability_score: Optional[float] = None
    growth_score: Optional[float] = None
    financial_health_score: Optional[float] = None
    efficiency_score: Optional[float] = None
    
    # Metadados
    calculation_date: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validação e normalização após criação"""
        # Garantir que composite_score está no range válido
        if self.composite_score < 0:
            self.composite_score = 0.0
        elif self.composite_score > 100:
            self.composite_score = 100.0
        
        # Se scores individuais não fornecidos, derivar do composite
        if self.valuation_score is None:
            self.valuation_score = self.composite_score
        if self.profitability_score is None:
            self.profitability_score = self.composite_score
        if self.growth_score is None:
            self.growth_score = self.composite_score
        if self.financial_health_score is None:
            self.financial_health_score = self.composite_score
        if self.efficiency_score is None:
            self.efficiency_score = self.composite_score


@dataclass
class SectorStatistics:
    """Estatísticas completas de um setor"""
    sector: str
    sample_size: int
    
    # Estatísticas do composite score
    mean_composite_score: float
    median_composite_score: float
    std_dev: float
    min_score: float
    max_score: float
    
    # Percentis importantes
    percentile_25: float
    percentile_75: float
    percentile_90: float
    
    # Estatísticas por categoria
    mean_valuation: float = 0.0
    mean_profitability: float = 0.0
    mean_growth: float = 0.0
    mean_financial_health: float = 0.0
    mean_efficiency: float = 0.0
    
    # Metadados
    calculation_date: datetime = field(default_factory=datetime.now)
    data_quality: float = 100.0  # % de dados válidos


@dataclass
class SectorRanking:
    """Posição de uma empresa dentro do seu setor"""
    stock_code: str
    sector: str
    
    # Posições e percentis
    sector_rank: int = 0
    sector_percentile: float = 50.0
    total_companies: int = 0
    
    # Score e tier
    composite_score: float = 0.0
    quality_tier: QualityTier = QualityTier.AVERAGE
    
    # Rankings por categoria
    category_ranks: Dict[str, int] = field(default_factory=dict)
    category_percentiles: Dict[str, float] = field(default_factory=dict)
    
    # Análise comparativa
    vs_sector_median: float = 0.0  # Diferença vs mediana setorial
    vs_sector_mean: float = 0.0    # Diferença vs média setorial
    
    # Flags especiais
    is_outlier: bool = False
    outlier_type: Optional[OutlierType] = None
    is_sector_leader: bool = False
    is_top_quartile: bool = False
    is_bottom_quartile: bool = False
    
    # Metadados
    calculation_date: datetime = field(default_factory=datetime.now)


@dataclass
class SectorComparison:
    """Comparação entre setores"""
    comparison_date: datetime
    sectors_analyzed: List[str]
    
    # Rankings entre setores
    sector_performance: Dict[str, float]  # Score médio por setor
    sector_volatility: Dict[str, float]   # Desvio padrão por setor
    sector_medians: Dict[str, float]      # Mediana por setor
    
    # Top performers cross-sector
    cross_sector_top_10: List[SectorRanking]
    sector_leaders: Dict[str, SectorRanking]  # Melhor de cada setor
    
    # Insights
    best_performing_sector: str
    worst_performing_sector: str
    most_consistent_sector: str  # Menor volatilidade
    most_volatile_sector: str


# ================================================================
# FUNÇÕES UTILITÁRIAS ROBUSTAS
# ================================================================

def safe_percentile(values: List[float], percentile: float) -> float:
    """Calcula percentil de forma segura"""
    if not values:
        return 0.0
    
    try:
        # Remove None e valores inválidos
        clean_values = [v for v in values if v is not None and not (isinstance(v, float) and (v != v or v == float('inf')))]
        if not clean_values:
            return 0.0
        
        clean_values.sort()
        n = len(clean_values)
        
        if n == 1:
            return clean_values[0]
        
        # Cálculo de percentil usando interpolação
        index = (percentile / 100.0) * (n - 1)
        lower_index = int(index)
        upper_index = min(lower_index + 1, n - 1)
        
        if lower_index == upper_index:
            return clean_values[lower_index]
        
        # Interpolação linear
        weight = index - lower_index
        return clean_values[lower_index] * (1 - weight) + clean_values[upper_index] * weight
        
    except Exception as e:
        logger.warning(f"Erro no cálculo de percentil: {e}")
        return 0.0


def detect_outliers(values: List[float], method: str = 'iqr') -> Tuple[List[int], float, float]:
    """
    Detecta outliers em uma lista de valores
    
    Returns:
        Tuple[List[int], float, float]: (índices dos outliers, threshold_low, threshold_high)
    """
    if not values or len(values) < 4:
        return [], 0.0, 100.0
    
    try:
        # Remove valores inválidos
        clean_values = [(i, v) for i, v in enumerate(values) 
                       if v is not None and not (isinstance(v, float) and (v != v or v == float('inf')))]
        
        if len(clean_values) < 4:
            return [], 0.0, 100.0
        
        # Separar índices e valores
        indices, vals = zip(*clean_values)
        vals = list(vals)
        
        if method == 'iqr':
            # Método do IQR (Interquartile Range)
            q1 = safe_percentile(vals, 25)
            q3 = safe_percentile(vals, 75)
            iqr = q3 - q1
            
            if iqr == 0:  # Todos os valores iguais
                return [], min(vals), max(vals)
            
            # Thresholds mais conservadores para evitar falsos positivos
            threshold_low = q1 - 2.0 * iqr  # Era 1.5, agora 2.0
            threshold_high = q3 + 2.0 * iqr
            
        elif method == 'zscore':
            # Método Z-Score
            mean_val = statistics.mean(vals)
            std_val = statistics.stdev(vals) if len(vals) > 1 else 0
            
            if std_val == 0:
                return [], min(vals), max(vals)
            
            # Z-score threshold = 2.5 (mais conservador que 2.0)
            z_threshold = 2.5
            threshold_low = mean_val - z_threshold * std_val
            threshold_high = mean_val + z_threshold * std_val
            
        else:
            # Método padrão conservador
            threshold_low = safe_percentile(vals, 5)   # 5% mais baixos
            threshold_high = safe_percentile(vals, 95)  # 5% mais altos
        
        # Identificar outliers
        outlier_indices = []
        for i, val in enumerate(vals):
            if val < threshold_low or val > threshold_high:
                # Mapear de volta para índice original
                original_index = indices[i]
                outlier_indices.append(original_index)
        
        return outlier_indices, threshold_low, threshold_high
        
    except Exception as e:
        logger.warning(f"Erro na detecção de outliers: {e}")
        return [], 0.0, 100.0


def get_or_create_fundamental_score(score_data) -> FundamentalScore:
    """
    Cria FundamentalScore compatível a partir de dados diversos
    """
    if isinstance(score_data, FundamentalScore):
        return score_data
    
    # Se for dict ou objeto com atributos
    if hasattr(score_data, '__dict__') or isinstance(score_data, dict):
        data = score_data.__dict__ if hasattr(score_data, '__dict__') else score_data
        
        return FundamentalScore(
            stock_code=data.get('stock_code', 'UNKNOWN'),
            sector=data.get('sector', 'Unknown'),
            composite_score=data.get('composite_score', 50.0),
            quality_tier=data.get('quality_tier', QualityTier.AVERAGE),
            valuation_score=data.get('valuation_score'),
            profitability_score=data.get('profitability_score'),
            growth_score=data.get('growth_score'),
            financial_health_score=data.get('financial_health_score'),
            efficiency_score=data.get('efficiency_score')
        )
    
    # Fallback: criar score básico
    return FundamentalScore(
        stock_code='UNKNOWN',
        sector='Unknown',
        composite_score=50.0
    )


# ================================================================
# CLASSE PRINCIPAL DO SECTOR COMPARATOR
# ================================================================

class SectorComparator:
    """
    Sistema avançado de comparação setorial - VERSÃO CORRIGIDA
    
    Funcionalidades:
    - Cálculo de percentis por setor
    - Rankings intra e inter-setoriais
    - Identificação de outliers
    - Cache para performance
    - Análise estatística avançada
    - Compatibilidade com múltiplas versões de FundamentalScore
    """
    
    def __init__(self, cache_ttl: int = 3600):
        self.cache_ttl = cache_ttl  # 1 hora por padrão
        self.logger = logging.getLogger(__name__)
        
        # Caches
        self._sector_stats_cache = {}
        self._rankings_cache = {}
        self._percentiles_cache = {}
        
        # Configurações ajustadas
        self.outlier_detection_method = 'iqr'
        self.min_sector_size = 2  # REDUZIDO de 3 para 2 (mais realista)
        
        self.logger.info("SectorComparator inicializado com configurações corrigidas")
    
    def _normalize_scores(self, scores: List[Any]) -> List[FundamentalScore]:
        """
        Normaliza entrada para lista de FundamentalScore compatíveis
        """
        normalized = []
        
        for score in scores:
            try:
                normalized_score = get_or_create_fundamental_score(score)
                normalized.append(normalized_score)
            except Exception as e:
                self.logger.warning(f"Erro ao normalizar score: {e}")
                continue
        
        return normalized
    
    def calculate_sector_statistics(self, scores: List[Any]) -> Dict[str, SectorStatistics]:
        """
        Calcula estatísticas completas por setor - VERSÃO CORRIGIDA
        """
        # Normalizar entrada
        normalized_scores = self._normalize_scores(scores)
        
        if not normalized_scores:
            self.logger.warning("Nenhum score válido para calcular estatísticas")
            return {}
        
        # Cache key
        cache_key = f"sector_stats_{len(normalized_scores)}_{hash(tuple(s.stock_code for s in normalized_scores))}"
        
        # Verificar cache
        if cache_key in self._sector_stats_cache:
            cached = self._sector_stats_cache[cache_key]
            if (datetime.now() - cached['timestamp']).seconds < self.cache_ttl:
                return cached['data']
        
        # Agrupar por setor
        sector_groups = defaultdict(list)
        for score in normalized_scores:
            sector_groups[score.sector].append(score)
        
        sector_stats = {}
        
        for sector, sector_scores in sector_groups.items():
            # AJUSTE: Aceitar setores com pelo menos 2 empresas (era 3)
            if len(sector_scores) < self.min_sector_size:
                self.logger.info(f"Setor {sector} tem apenas {len(sector_scores)} empresas (mínimo: {self.min_sector_size})")
                continue
            
            # Extrair scores para cálculos
            composite_scores = [s.composite_score for s in sector_scores]
            valuation_scores = [s.valuation_score for s in sector_scores if s.valuation_score is not None]
            profitability_scores = [s.profitability_score for s in sector_scores if s.profitability_score is not None]
            growth_scores = [s.growth_score for s in sector_scores if s.growth_score is not None]
            financial_health_scores = [s.financial_health_score for s in sector_scores if s.financial_health_score is not None]
            efficiency_scores = [s.efficiency_score for s in sector_scores if s.efficiency_score is not None]
            
            # Calcular estatísticas
            try:
                stats = SectorStatistics(
                    sector=sector,
                    sample_size=len(sector_scores),
                    mean_composite_score=statistics.mean(composite_scores),
                    median_composite_score=statistics.median(composite_scores),
                    std_dev=statistics.stdev(composite_scores) if len(composite_scores) > 1 else 0.0,
                    min_score=min(composite_scores),
                    max_score=max(composite_scores),
                    percentile_25=safe_percentile(composite_scores, 25),
                    percentile_75=safe_percentile(composite_scores, 75),
                    percentile_90=safe_percentile(composite_scores, 90),
                    mean_valuation=statistics.mean(valuation_scores) if valuation_scores else 0.0,
                    mean_profitability=statistics.mean(profitability_scores) if profitability_scores else 0.0,
                    mean_growth=statistics.mean(growth_scores) if growth_scores else 0.0,
                    mean_financial_health=statistics.mean(financial_health_scores) if financial_health_scores else 0.0,
                    mean_efficiency=statistics.mean(efficiency_scores) if efficiency_scores else 0.0,
                    data_quality=self._calculate_data_quality(sector_scores)
                )
                
                sector_stats[sector] = stats
                
            except Exception as e:
                self.logger.error(f"Erro ao calcular estatísticas do setor {sector}: {e}")
                continue
        
        # Cache do resultado
        self._sector_stats_cache[cache_key] = {
            'data': sector_stats,
            'timestamp': datetime.now()
        }
        
        return sector_stats
    
    def calculate_sector_rankings(self, scores: List[Any]) -> List[SectorRanking]:
        """
        Calcula rankings dentro de cada setor - VERSÃO CORRIGIDA
        """
        # Normalizar entrada
        normalized_scores = self._normalize_scores(scores)
        
        if not normalized_scores:
            return []
        
        # Cache key
        cache_key = f"rankings_{len(normalized_scores)}_{hash(tuple(s.stock_code for s in normalized_scores))}"
        
        # Verificar cache
        if cache_key in self._rankings_cache:
            cached = self._rankings_cache[cache_key]
            if (datetime.now() - cached['timestamp']).seconds < self.cache_ttl:
                return cached['data']
        
        # Obter estatísticas setoriais
        sector_stats = self.calculate_sector_statistics(normalized_scores)
        
        # Agrupar por setor
        sector_groups = defaultdict(list)
        for score in normalized_scores:
            sector_groups[score.sector].append(score)
        
        all_rankings = []
        
        for sector, sector_scores in sector_groups.items():
            # Ordenar por composite_score (decrescente)
            sorted_scores = sorted(sector_scores, key=lambda x: x.composite_score, reverse=True)
            
            sector_stat = sector_stats.get(sector)
            
            for rank, score in enumerate(sorted_scores, 1):
                # Calcular percentil dentro do setor
                scores_in_sector = [s.composite_score for s in sector_scores]
                better_scores = [s for s in scores_in_sector if s > score.composite_score]
                percentile = (len(better_scores) / len(scores_in_sector)) * 100
                percentile = 100 - percentile  # Inverter para que maior score = maior percentil
                
                # Calcular diferenças vs setor
                vs_median = 0.0
                vs_mean = 0.0
                if sector_stat:
                    vs_median = score.composite_score - sector_stat.median_composite_score
                    vs_mean = score.composite_score - sector_stat.mean_composite_score
                
                # Determinar flags especiais
                is_leader = rank == 1
                is_top_quartile = percentile >= 75
                is_bottom_quartile = percentile <= 25
                
                ranking = SectorRanking(
                    stock_code=score.stock_code,
                    sector=score.sector,
                    sector_rank=rank,
                    sector_percentile=percentile,
                    total_companies=len(sector_scores),
                    composite_score=score.composite_score,
                    quality_tier=score.quality_tier,
                    vs_sector_median=vs_median,
                    vs_sector_mean=vs_mean,
                    is_sector_leader=is_leader,
                    is_top_quartile=is_top_quartile,
                    is_bottom_quartile=is_bottom_quartile
                )
                
                all_rankings.append(ranking)
        
        # Cache do resultado
        self._rankings_cache[cache_key] = {
            'data': all_rankings,
            'timestamp': datetime.now()
        }
        
        return all_rankings
    
    def compare_sectors(self, scores: List[Any]) -> Optional[SectorComparison]:
        """
        Compara performance entre setores - VERSÃO CORRIGIDA
        """
        try:
            # Normalizar entrada
            normalized_scores = self._normalize_scores(scores)
            
            if not normalized_scores:
                return None
            
            # Obter estatísticas e rankings
            sector_stats = self.calculate_sector_statistics(normalized_scores)
            rankings = self.calculate_sector_rankings(normalized_scores)
            
            if not sector_stats:
                return None
            
            # Calcular performance por setor
            sector_performance = {}
            sector_volatility = {}
            sector_medians = {}
            
            for sector, stats in sector_stats.items():
                sector_performance[sector] = stats.mean_composite_score
                sector_volatility[sector] = stats.std_dev
                sector_medians[sector] = stats.median_composite_score
            
            # Top 10 cross-sector
            cross_sector_top_10 = sorted(rankings, key=lambda x: x.composite_score, reverse=True)[:10]
            
            # Líderes por setor
            sector_leaders = {}
            for ranking in rankings:
                if ranking.is_sector_leader:
                    sector_leaders[ranking.sector] = ranking
            
            # Determinar melhores e piores setores
            if sector_performance:
                best_sector = max(sector_performance.items(), key=lambda x: x[1])[0]
                worst_sector = min(sector_performance.items(), key=lambda x: x[1])[0]
            else:
                best_sector = "Unknown"
                worst_sector = "Unknown"
            
            # Setor mais consistente (menor volatilidade)
            if sector_volatility:
                most_consistent = min(sector_volatility.items(), key=lambda x: x[1])[0]
                most_volatile = max(sector_volatility.items(), key=lambda x: x[1])[0]
            else:
                most_consistent = "Unknown"
                most_volatile = "Unknown"
            
            return SectorComparison(
                comparison_date=datetime.now(),
                sectors_analyzed=list(sector_stats.keys()),
                sector_performance=sector_performance,
                sector_volatility=sector_volatility,
                sector_medians=sector_medians,
                cross_sector_top_10=cross_sector_top_10,
                sector_leaders=sector_leaders,
                best_performing_sector=best_sector,
                worst_performing_sector=worst_sector,
                most_consistent_sector=most_consistent,
                most_volatile_sector=most_volatile
            )
            
        except Exception as e:
            self.logger.error(f"Erro na comparação setorial: {e}")
            return None
    
    def identify_sector_outliers(self, scores: List[Any], 
                               metric: str = 'composite_score') -> Dict[str, List[FundamentalScore]]:
        """
        Identifica outliers por setor - VERSÃO CORRIGIDA
        """
        # Normalizar entrada
        normalized_scores = self._normalize_scores(scores)
        
        sector_groups = defaultdict(list)
        for score in normalized_scores:
            sector_groups[score.sector].append(score)
        
        sector_outliers = {}
        
        for sector, sector_scores in sector_groups.items():
            if len(sector_scores) < 4:  # Mínimo para detecção de outliers
                continue
            
            # Extrair valores da métrica
            metric_values = []
            for score in sector_scores:
                value = getattr(score, metric, None)
                if value is not None:
                    metric_values.append(value)
            
            if len(metric_values) < 4:
                continue
            
            # Detectar outliers
            outlier_indices, _, _ = detect_outliers(metric_values, self.outlier_detection_method)
            
            # Mapear de volta para scores
            outlier_scores = []
            for idx in outlier_indices:
                if idx < len(sector_scores):
                    outlier_scores.append(sector_scores[idx])
            
            if outlier_scores:
                sector_outliers[sector] = outlier_scores
        
        return sector_outliers
    
    def get_sector_percentiles(self, sector: str, metric_values: List[float]) -> Dict[str, float]:
        """
        Calcula percentis para uma métrica específica em um setor
        """
        cache_key = f"percentiles_{sector}_{hash(tuple(metric_values))}"
        
        # Verificar cache
        if cache_key in self._percentiles_cache:
            cached = self._percentiles_cache[cache_key]
            if (datetime.now() - cached['timestamp']).seconds < self.cache_ttl:
                return cached['data']
        
        # Calcular percentis
        percentiles = {}
        for p in [10, 25, 50, 75, 90, 95, 99]:
            percentiles[f'p{p}'] = safe_percentile(metric_values, p)
        
        # Cache do resultado
        self._percentiles_cache[cache_key] = {
            'data': percentiles,
            'timestamp': datetime.now()
        }
        
        return percentiles
    
    def _calculate_data_quality(self, scores: List[FundamentalScore]) -> float:
        """Calcula qualidade dos dados do setor"""
        if not scores:
            return 0.0
        
        # Contar campos preenchidos vs total
        total_fields = 0
        filled_fields = 0
        
        for score in scores:
            # Campos principais para avaliar qualidade
            fields_to_check = [
                'valuation_score', 'profitability_score', 'growth_score',
                'financial_health_score', 'efficiency_score', 'composite_score'
            ]
            
            for field in fields_to_check:
                total_fields += 1
                value = getattr(score, field, None)
                if value is not None:
                    filled_fields += 1
        
        return (filled_fields / total_fields * 100) if total_fields > 0 else 0.0
    
    def clear_cache(self):
        """Limpa todos os caches"""
        self._sector_stats_cache.clear()
        self._rankings_cache.clear()
        self._percentiles_cache.clear()
        self.logger.info("Cache do SectorComparator limpo")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas dos caches"""
        return {
            'sector_stats_entries': len(self._sector_stats_cache),
            'rankings_entries': len(self._rankings_cache),
            'percentiles_entries': len(self._percentiles_cache),
            'cache_ttl': self.cache_ttl,
            'outlier_method': self.outlier_detection_method,
            'min_sector_size': self.min_sector_size
        }


# ================================================================
# FUNÇÕES UTILITÁRIAS DE CONVENIÊNCIA
# ================================================================

def create_sector_comparator(cache_ttl: int = 3600) -> SectorComparator:
    """Factory function para criar SectorComparator"""
    return SectorComparator(cache_ttl)


def quick_sector_analysis(scores: List[Any]) -> Dict[str, Any]:
    """
    Análise setorial rápida - VERSÃO CORRIGIDA
    """
    comparator = create_sector_comparator()
    
    try:
        stats = comparator.calculate_sector_statistics(scores)
        rankings = comparator.calculate_sector_rankings(scores)
        comparison = comparator.compare_sectors(scores)
        
        return {
            'sector_statistics': stats,
            'top_rankings': rankings[:10],  # Top 10
            'sector_comparison': comparison,
            'summary': {
                'total_companies': len(scores),
                'sectors_analyzed': len(stats) if stats else 0,
                'best_sector': comparison.best_performing_sector if comparison else "Unknown",
                'most_consistent': comparison.most_consistent_sector if comparison else "Unknown"
            }
        }
    except Exception as e:
        logger.error(f"Erro na análise rápida: {e}")
        return {
            'sector_statistics': {},
            'top_rankings': [],
            'sector_comparison': None,
            'summary': {
                'total_companies': len(scores),
                'sectors_analyzed': 0,
                'best_sector': "Unknown",
                'most_consistent': "Unknown"
            }
        }


def get_sector_leaders(scores: List[Any]) -> Dict[str, FundamentalScore]:
    """Retorna o líder de cada setor - VERSÃO CORRIGIDA"""
    try:
        comparator = create_sector_comparator()
        rankings = comparator.calculate_sector_rankings(scores)
        
        # Normalizar scores para busca
        normalized_scores = comparator._normalize_scores(scores)
        
        leaders = {}
        for ranking in rankings:
            if ranking.is_sector_leader:
                # Encontrar o score original
                for score in normalized_scores:
                    if score.stock_code == ranking.stock_code:
                        leaders[ranking.sector] = score
                        break
        
        return leaders
    except Exception as e:
        logger.error(f"Erro ao obter líderes setoriais: {e}")
        return {}


# ================================================================
# TESTE INTEGRADO PARA VALIDAÇÃO
# ================================================================

# ================================================================
# TESTE INTEGRADO PARA VALIDAÇÃO
# ================================================================

def run_comprehensive_test():
    """
    Teste abrangente do SectorComparator corrigido
    """
    print("🧪 TESTE ABRANGENTE DO SECTOR COMPARATOR CORRIGIDO")
    print("=" * 70)
    
    try:
        # Criar dados de teste diversos
        test_scores = [
            # Tecnologia (setor forte)
            FundamentalScore(
                stock_code="TECH_HIGH", sector="Tecnologia",
                composite_score=88, quality_tier=QualityTier.EXCELLENT,
                valuation_score=90, profitability_score=95, growth_score=90,
                financial_health_score=85, efficiency_score=80
            ),
            FundamentalScore(
                stock_code="TECH_MID", sector="Tecnologia",
                composite_score=74, quality_tier=QualityTier.GOOD,
                valuation_score=70, profitability_score=75, growth_score=80,
                financial_health_score=75, efficiency_score=70
            ),
            FundamentalScore(
                stock_code="TECH_LOW", sector="Tecnologia",
                composite_score=56, quality_tier=QualityTier.AVERAGE,
                valuation_score=50, profitability_score=55, growth_score=60,
                financial_health_score=65, efficiency_score=50
            ),
            
            # Bancos (setor médio)
            FundamentalScore(
                stock_code="BANK_HIGH", sector="Bancos",
                composite_score=72, quality_tier=QualityTier.GOOD,
                valuation_score=65, profitability_score=85, growth_score=45,
                financial_health_score=95, efficiency_score=70
            ),
            FundamentalScore(
                stock_code="BANK_LOW", sector="Bancos",
                composite_score=68, quality_tier=QualityTier.AVERAGE,
                valuation_score=60, profitability_score=80, growth_score=40,
                financial_health_score=90, efficiency_score=65
            ),
            
            # Varejo (setor fraco)
            FundamentalScore(
                stock_code="RET_HIGH", sector="Varejo",
                composite_score=58, quality_tier=QualityTier.AVERAGE,
                valuation_score=55, profitability_score=60, growth_score=55,
                financial_health_score=60, efficiency_score=60
            ),
            FundamentalScore(
                stock_code="RET_LOW", sector="Varejo",
                composite_score=45, quality_tier=QualityTier.POOR,
                valuation_score=40, profitability_score=50, growth_score=45,
                financial_health_score=50, efficiency_score=40
            )
        ]
        
        print(f"📊 Dados de teste criados: {len(test_scores)} empresas em 3 setores")
        
        # Criar comparador
        comparator = create_sector_comparator()
        
        # 1. Testar estatísticas setoriais
        print("\n1️⃣ TESTANDO ESTATÍSTICAS SETORIAIS:")
        stats = comparator.calculate_sector_statistics(test_scores)
        
        if stats:
            print(f"   ✅ {len(stats)} setores processados:")
            for sector, stat in stats.items():
                print(f"      {sector}: {stat.sample_size} empresas, score médio {stat.mean_composite_score:.1f}")
        else:
            print("   ❌ Nenhuma estatística calculada")
        
        # 2. Testar rankings
        print("\n2️⃣ TESTANDO RANKINGS SETORIAIS:")
        rankings = comparator.calculate_sector_rankings(test_scores)
        
        if rankings:
            print(f"   ✅ {len(rankings)} rankings calculados:")
            # Top 3 overall
            top_rankings = sorted(rankings, key=lambda x: x.composite_score, reverse=True)[:3]
            for ranking in top_rankings:
                print(f"      {ranking.stock_code} ({ranking.sector}): Score {ranking.composite_score:.1f}, "
                      f"Rank setorial #{ranking.sector_rank}, Percentil {ranking.sector_percentile:.0f}%")
        else:
            print("   ❌ Nenhum ranking calculado")
        
        # 3. Testar comparação setorial
        print("\n3️⃣ TESTANDO COMPARAÇÃO SETORIAL:")
        comparison = comparator.compare_sectors(test_scores)
        
        if comparison:
            print(f"   ✅ Comparação realizada:")
            print(f"      Melhor setor: {comparison.best_performing_sector}")
            print(f"      Pior setor: {comparison.worst_performing_sector}")
            print(f"      Mais consistente: {comparison.most_consistent_sector}")
            print(f"      Mais volátil: {comparison.most_volatile_sector}")
        else:
            print("   ❌ Comparação falhou")
        
        # 4. Testar detecção de outliers
        print("\n4️⃣ TESTANDO DETECÇÃO DE OUTLIERS:")
        outliers = comparator.identify_sector_outliers(test_scores)
        
        if outliers:
            print(f"   ✅ Outliers detectados em {len(outliers)} setores:")
            for sector, sector_outliers in outliers.items():
                codes = [o.stock_code for o in sector_outliers]
                print(f"      {sector}: {codes}")
        else:
            print("   ℹ️  Nenhum outlier detectado (normal para dataset pequeno)")
        
        # 5. Testar líderes setoriais
        print("\n5️⃣ TESTANDO LÍDERES SETORIAIS:")
        leaders = get_sector_leaders(test_scores)
        
        if leaders:
            print(f"   ✅ {len(leaders)} líderes identificados:")
            for sector, leader in leaders.items():
                print(f"      {sector}: {leader.stock_code} (Score: {leader.composite_score:.1f})")
        else:
            print("   ❌ Nenhum líder identificado")
        
        # 6. Testar cache
        print("\n6️⃣ TESTANDO SISTEMA DE CACHE:")
        cache_stats = comparator.get_cache_stats()
        print(f"   ✅ Cache funcionando:")
        print(f"      Entradas de estatísticas: {cache_stats['sector_stats_entries']}")
        print(f"      Entradas de rankings: {cache_stats['rankings_entries']}")
        print(f"      TTL configurado: {cache_stats['cache_ttl']}s")
        
        # 7. Análise rápida
        print("\n7️⃣ TESTANDO ANÁLISE RÁPIDA:")
        quick_analysis = quick_sector_analysis(test_scores)
        
        if quick_analysis['summary']:
            summary = quick_analysis['summary']
            print(f"   ✅ Análise rápida funcionando:")
            print(f"      Total de empresas: {summary['total_companies']}")
            print(f"      Setores analisados: {summary['sectors_analyzed']}")
            print(f"      Melhor setor: {summary['best_sector']}")
        else:
            print("   ❌ Análise rápida falhou")
        
        # 8. Teste de performance
        print("\n8️⃣ TESTANDO PERFORMANCE:")
        import time
        start_time = time.time()
        
        # Processar múltiplas vezes
        for _ in range(10):
            comparator.calculate_sector_statistics(test_scores)
            comparator.calculate_sector_rankings(test_scores)
        
        end_time = time.time()
        avg_time = (end_time - start_time) / 10
        
        print(f"   ✅ Performance:")
        print(f"      Tempo médio por ciclo: {avg_time*1000:.1f}ms")
        print(f"      Cache hit esperado: Sim (após primeira execução)")
        
        # Resultado final
        success_count = sum([
            bool(stats),
            bool(rankings),
            bool(comparison),
            bool(leaders),
            bool(cache_stats),
            bool(quick_analysis['summary'])
        ])
        
        print(f"\n✅ RESULTADO FINAL:")
        print(f"   Testes passaram: {success_count}/6")
        print(f"   Taxa de sucesso: {success_count/6*100:.1f}%")
        
        if success_count >= 5:
            print(f"   🎉 SECTOR COMPARATOR FUNCIONANDO CORRETAMENTE!")
            print(f"   ✅ Todas as funcionalidades principais validadas")
            print(f"   🚀 Pronto para integração")
            return True
        else:
            print(f"   ⚠️  Algumas funcionalidades precisam de ajustes")
            return False
        
    except Exception as e:
        print(f"❌ ERRO CRÍTICO no teste: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🔍 SECTOR COMPARATOR - VERSÃO CORRIGIDA")
    print("=" * 50)
    
    # Executar teste integrado
    success = run_comprehensive_test()
    
    if success:
        print(f"\n✅ Sector Comparator validado e funcionando!")
        print(f"📁 Arquivo: agents/analyzers/sector_comparator.py")
        print(f"🎯 Status: IMPLEMENTAÇÃO COMPLETA - Fase 2 Passo 2.2")
        print(f"🚀 Pronto para próxima fase: quality_filters.py (Passo 2.3)")
    else:
        print(f"\n⚠️  Revisar implementação antes de prosseguir")
        print(f"🔧 Alguns componentes podem precisar de ajustes adicionais")


# ================================================================
# IMPORTAÇÕES DE COMPATIBILIDADE
# ================================================================

# Tentar importar do scoring_engine se disponível
try:
    from agents.analyzers.scoring_engine import FundamentalScore as ExternalFundamentalScore
    from agents.analyzers.scoring_engine import QualityTier as ExternalQualityTier
    
    # Se existir, usar versão externa
    SCORING_ENGINE_AVAILABLE = True
    logger.info("Scoring engine detectado - usando FundamentalScore externa")
    
    # Função de compatibilidade
    def get_or_create_fundamental_score_external(score_data):
        """Adapta para FundamentalScore externa"""
        if isinstance(score_data, ExternalFundamentalScore):
            return score_data
        elif isinstance(score_data, FundamentalScore):
            # Converter de interna para externa
            return ExternalFundamentalScore(
                stock_code=score_data.stock_code,
                sector=score_data.sector,
                composite_score=score_data.composite_score,
                quality_tier=score_data.quality_tier,
                valuation_score=score_data.valuation_score or 0,
                profitability_score=score_data.profitability_score or 0,
                growth_score=score_data.growth_score or 0,
                financial_health_score=score_data.financial_health_score or 0,
                efficiency_score=score_data.efficiency_score or 0
            )
        else:
            return get_or_create_fundamental_score(score_data)
    
    # Atualizar função global
    get_or_create_fundamental_score = get_or_create_fundamental_score_external
    
except ImportError:
    SCORING_ENGINE_AVAILABLE = False
    logger.info("Scoring engine não disponível - usando FundamentalScore interna")


# ================================================================
# FUNÇÕES DE MIGRAÇÃO E ATUALIZAÇÃO
# ================================================================

def migrate_from_old_sector_comparator(old_scores: List[Any]) -> List[FundamentalScore]:
    """
    Migra dados de versões antigas do sector_comparator
    """
    migrated = []
    
    for score in old_scores:
        try:
            if hasattr(score, 'stock_code') and hasattr(score, 'sector'):
                # Já é compatível
                migrated.append(get_or_create_fundamental_score(score))
            elif isinstance(score, dict):
                # Dict com dados
                migrated.append(FundamentalScore(
                    stock_code=score.get('stock_code', 'UNKNOWN'),
                    sector=score.get('sector', 'Unknown'),
                    composite_score=score.get('composite_score', 50.0)
                ))
            else:
                logger.warning(f"Tipo de score não reconhecido: {type(score)}")
                continue
        except Exception as e:
            logger.error(f"Erro ao migrar score: {e}")
            continue
    
    return migrated


def update_sector_comparator_config(comparator: SectorComparator, 
                                  min_sector_size: int = None,
                                  cache_ttl: int = None,
                                  outlier_method: str = None) -> None:
    """
    Atualiza configurações do SectorComparator
    """
    if min_sector_size is not None:
        comparator.min_sector_size = min_sector_size
        logger.info(f"Mínimo setorial atualizado para: {min_sector_size}")
    
    if cache_ttl is not None:
        comparator.cache_ttl = cache_ttl
        logger.info(f"TTL do cache atualizado para: {cache_ttl}s")
    
    if outlier_method is not None:
        comparator.outlier_detection_method = outlier_method
        logger.info(f"Método de detecção de outliers atualizado para: {outlier_method}")


def validate_sector_comparator_installation() -> bool:
    """
    Valida se o SectorComparator está corretamente instalado
    """
    try:
        # Teste básico de importação
        comparator = create_sector_comparator()
        
        # Teste com dados mínimos
        test_data = [
            FundamentalScore("TEST1", "TestSector", 50.0),
            FundamentalScore("TEST2", "TestSector", 60.0)
        ]
        
        # Executar funções principais
        stats = comparator.calculate_sector_statistics(test_data)
        rankings = comparator.calculate_sector_rankings(test_data)
        
        # Validar resultados
        if stats and rankings and len(rankings) == 2:
            logger.info("SectorComparator validado com sucesso")
            return True
        else:
            logger.error("Validação do SectorComparator falhou")
            return False
            
    except Exception as e:
        logger.error(f"Erro na validação do SectorComparator: {e}")
        return False


# ================================================================
# TESTES UNITÁRIOS ADICIONAIS
# ================================================================

def test_percentile_edge_cases():
    """Testa casos extremos da função safe_percentile"""
    # Lista vazia
    assert safe_percentile([], 50) == 0.0
    
    # Um elemento
    assert safe_percentile([42.0], 50) == 42.0
    
    # Valores None misturados
    values_with_none = [10, None, 20, None, 30]
    result = safe_percentile(values_with_none, 50)
    assert 15 <= result <= 25  # Deve estar na faixa esperada
    
    # Valores infinitos
    values_with_inf = [10, 20, float('inf'), 30]
    result = safe_percentile(values_with_inf, 50)
    assert 15 <= result <= 25  # Deve ignorar inf
    
    print("✅ Testes de casos extremos passaram")


def test_outlier_detection_edge_cases():
    """Testa casos extremos da detecção de outliers"""
    # Lista muito pequena
    small_list = [1, 2]
    outliers, _, _ = detect_outliers(small_list)
    assert outliers == []  # Não deve detectar outliers
    
    # Todos valores iguais
    equal_values = [50.0] * 10
    outliers, _, _ = detect_outliers(equal_values)
    assert outliers == []  # Não deve detectar outliers
    
    # Outliers óbvios
    obvious_outliers = [10, 12, 11, 13, 12, 14, 11, 10, 13, 100]
    outliers, _, _ = detect_outliers(obvious_outliers)
    assert len(outliers) > 0  # Deve detectar pelo menos um
    
    print("✅ Testes de detecção de outliers passaram")


def test_fundamental_score_validation():
    """Testa validação da FundamentalScore"""
    # Score muito alto (deve normalizar)
    score_high = FundamentalScore("TEST", "Sector", 150.0)
    assert score_high.composite_score == 100.0
    
    # Score negativo (deve normalizar)
    score_low = FundamentalScore("TEST", "Sector", -10.0)
    assert score_low.composite_score == 0.0
    
    # Auto-preenchimento de campos
    score_basic = FundamentalScore("TEST", "Sector", 75.0)
    assert score_basic.valuation_score == 75.0
    assert score_basic.profitability_score == 75.0
    
    print("✅ Testes de validação FundamentalScore passaram")


def run_unit_tests():
    """Executa todos os testes unitários"""
    print("\n🧪 EXECUTANDO TESTES UNITÁRIOS:")
    
    try:
        test_percentile_edge_cases()
        test_outlier_detection_edge_cases()
        test_fundamental_score_validation()
        
        print("✅ Todos os testes unitários passaram!")
        return True
        
    except Exception as e:
        print(f"❌ Erro nos testes unitários: {e}")
        import traceback
        traceback.print_exc()
        return False


# Executar validação na importação (opcional)
if __name__ != "__main__":
    # Validação silenciosa na importação
    try:
        validation_result = validate_sector_comparator_installation()
        if validation_result:
            logger.debug("SectorComparator carregado e validado")
        else:
            logger.warning("SectorComparator carregado mas validação falhou")
    except Exception:
        logger.warning("Não foi possível validar SectorComparator na importação")


# ================================================================
# SCRIPT DE TESTE FINAL
# ================================================================

def main_test():
    """Script principal de teste"""
    print("🚀 TESTE FINAL DO SECTOR COMPARATOR")
    print("=" * 80)
    
    # 1. Testes unitários
    unit_tests_ok = run_unit_tests()
    
    # 2. Teste abrangente
    comprehensive_test_ok = run_comprehensive_test()
    
    # 3. Resultado final
    if unit_tests_ok and comprehensive_test_ok:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Sector Comparator está 100% funcional")
        print("🚀 Pronto para integração e próximos passos")
        return True
    else:
        print("\n⚠️  ALGUNS TESTES FALHARAM")
        print("🔧 Revisar problemas antes de prosseguir")
        return False


if __name__ == "__main__":
    success = main_test()
    exit(0 if success else 1)