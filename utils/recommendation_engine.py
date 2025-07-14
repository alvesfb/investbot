# utils/recommendation_engine.py
"""
Engine de Recomendações - Fase 3
Sistema de combinação de scores e lógica de decisão para recomendações

Funcionalidades:
- Combinação ponderada de scores fundamentalista e técnico
- Matriz de pesos configurável por setor
- Normalização e validação de scores
- Sistema de confidence level
- Ajustes baseados em contexto de mercado
"""

from typing import Dict, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass
import json
import logging

logger = logging.getLogger(__name__)


class Sector(Enum):
    """Setores compatíveis com a estrutura atual"""
    FINANCIALS = "Financeiro"
    TECHNOLOGY = "Tecnologia"
    UTILITIES = "Utilidades"
    ENERGY = "Energia"
    HEALTHCARE = "Saúde"
    MATERIALS = "Materiais"
    INDUSTRIALS = "Industrial"
    CONSUMER_DISCRETIONARY = "Consumo Discricionário"
    CONSUMER_STAPLES = "Consumo Básico"
    REAL_ESTATE = "Imobiliário"
    COMMUNICATION_SERVICES = "Comunicações"


class MarketCondition(Enum):
    """Condições de mercado que afetam as recomendações"""
    BULL_MARKET = "BULL_MARKET"          # Mercado em alta
    BEAR_MARKET = "BEAR_MARKET"          # Mercado em baixa
    SIDEWAYS = "SIDEWAYS"                # Mercado lateral
    HIGH_VOLATILITY = "HIGH_VOLATILITY"   # Alta volatilidade
    NORMAL = "NORMAL"                    # Condições normais


@dataclass
class ScoreWeights:
    """Pesos para combinação de scores"""
    fundamental: float
    technical: float
    sector_adjustment: float = 0.0
    market_adjustment: float = 0.0


@dataclass
class RecommendationContext:
    """Contexto para geração de recomendações"""
    sector: Optional[Sector] = None
    market_condition: MarketCondition = MarketCondition.NORMAL
    volatility_factor: float = 1.0
    sector_performance: Optional[float] = None


class RecommendationEngine:
    """
    Engine principal para combinação de scores e geração de recomendações
    
    Responsabilidades:
    1. Combinar scores fundamentalista e técnico com pesos apropriados
    2. Aplicar ajustes setoriais e de mercado
    3. Calcular níveis de confiança
    4. Validar qualidade dos dados de entrada
    5. Normalizar scores finais
    """
    
    def __init__(self):
        """Inicializa o engine de recomendações"""
        self.logger = logger
        
        # Pesos padrão (Fase 3: 70% fundamentalista, 30% técnico)
        self.default_weights = ScoreWeights(
            fundamental=0.70,
            technical=0.30
        )
        
        # Pesos específicos por setor
        self.sector_weights = self._initialize_sector_weights()
        
        # Ajustes por condição de mercado
        self.market_adjustments = self._initialize_market_adjustments()
        
        # Thresholds para validação de qualidade
        self.quality_thresholds = {
            "min_data_points": 2,       # Mínimo de pontos de dados
            "max_score_deviation": 50,  # Máximo desvio entre scores
            "min_confidence": 20,       # Confiança mínima aceitável
            "max_volatility": 5.0       # Máxima volatilidade para ajustes
        }
        
        self.logger.info("RecommendationEngine inicializado")
    
    def _initialize_sector_weights(self) -> Dict[Sector, ScoreWeights]:
        """Inicializa pesos específicos por setor"""
        return {
            # Setores cíclicos - maior peso técnico
            Sector.MATERIALS: ScoreWeights(fundamental=0.60, technical=0.40),
            Sector.INDUSTRIALS: ScoreWeights(fundamental=0.65, technical=0.35),
            Sector.ENERGY: ScoreWeights(fundamental=0.60, technical=0.40),
            
            # Setores defensivos - maior peso fundamentalista
            Sector.UTILITIES: ScoreWeights(fundamental=0.80, technical=0.20),
            Sector.HEALTHCARE: ScoreWeights(fundamental=0.75, technical=0.25),
            Sector.CONSUMER_STAPLES: ScoreWeights(fundamental=0.75, technical=0.25),
            
            # Setores de crescimento - balanceado
            Sector.TECHNOLOGY: ScoreWeights(fundamental=0.70, technical=0.30),
            Sector.COMMUNICATION_SERVICES: ScoreWeights(fundamental=0.70, technical=0.30),
            
            # Setores financeiros - maior peso fundamentalista
            Sector.FINANCIALS: ScoreWeights(fundamental=0.80, technical=0.20),
            Sector.REAL_ESTATE: ScoreWeights(fundamental=0.75, technical=0.25),
            
            # Setores sensíveis ao consumo - balanceado com viés técnico
            Sector.CONSUMER_DISCRETIONARY: ScoreWeights(fundamental=0.65, technical=0.35),
        }
    
    def _initialize_market_adjustments(self) -> Dict[MarketCondition, Dict[str, float]]:
        """Inicializa ajustes baseados em condições de mercado"""
        return {
            MarketCondition.BULL_MARKET: {
                "fundamental_boost": 0.05,    # Aumentar peso fundamentalista
                "technical_boost": -0.05,     # Diminuir peso técnico
                "confidence_bonus": 0.10      # Bonus de confiança
            },
            MarketCondition.BEAR_MARKET: {
                "fundamental_boost": -0.10,   # Diminuir peso fundamentalista
                "technical_boost": 0.10,      # Aumentar peso técnico
                "confidence_penalty": -0.15   # Penalidade de confiança
            },
            MarketCondition.HIGH_VOLATILITY: {
                "fundamental_boost": 0.10,    # Preferir fundamentos
                "technical_boost": -0.10,     # Reduzir peso técnico
                "confidence_penalty": -0.20   # Maior penalidade
            },
            MarketCondition.SIDEWAYS: {
                "fundamental_boost": -0.05,   # Leve redução
                "technical_boost": 0.05,      # Leve aumento técnico
                "confidence_bonus": 0.05      # Pequeno bonus
            },
            MarketCondition.NORMAL: {
                "fundamental_boost": 0.0,     # Sem ajustes
                "technical_boost": 0.0,
                "confidence_bonus": 0.0
            }
        }
    
    def calculate_combined_score(self, 
                                fundamental_score: float,
                                technical_score: float,
                                context: Optional[RecommendationContext] = None) -> Tuple[float, float]:
        """
        Calcula score combinado com pesos apropriados
        
        Args:
            fundamental_score: Score fundamentalista (0-100)
            technical_score: Score técnico (0-100)
            context: Contexto adicional para ajustes
            
        Returns:
            Tuple com (score_combinado, nivel_confianca)
        """
        try:
            # Validar inputs
            if not self._validate_scores(fundamental_score, technical_score):
                self.logger.warning("Scores inválidos detectados")
                return 50.0, 20.0  # Score neutro com baixa confiança
            
            # Determinar pesos apropriados
            weights = self._get_weights_for_context(context)
            
            # Aplicar ajustes de mercado se disponível
            if context and context.market_condition != MarketCondition.NORMAL:
                weights = self._apply_market_adjustments(weights, context.market_condition)
            
            # Calcular score combinado
            combined_score = (
                fundamental_score * weights.fundamental +
                technical_score * weights.technical
            )
            
            # Aplicar ajustes setoriais
            if context and context.sector_performance is not None:
                combined_score = self._apply_sector_adjustment(combined_score, context)
            
            # Calcular nível de confiança
            confidence_level = self._calculate_confidence(
                fundamental_score, technical_score, weights, context
            )
            
            # Normalizar resultados
            combined_score = max(0, min(100, combined_score))
            confidence_level = max(0, min(100, confidence_level))
            
            self.logger.debug(
                f"Score combinado: {combined_score:.1f} "
                f"(Fund: {fundamental_score:.1f}, Tech: {technical_score:.1f}, "
                f"Conf: {confidence_level:.1f})"
            )
            
            return round(combined_score, 1), round(confidence_level, 1)
            
        except Exception as e:
            self.logger.error(f"Erro no cálculo do score combinado: {str(e)}")
            return 50.0, 20.0
    
    def _validate_scores(self, fundamental_score: float, technical_score: float) -> bool:
        """Valida se os scores estão em ranges aceitáveis"""
        try:
            # Verificar se são números válidos
            if not all(isinstance(score, (int, float)) for score in [fundamental_score, technical_score]):
                return False
            
            # Verificar range 0-100
            if not all(0 <= score <= 100 for score in [fundamental_score, technical_score]):
                return False
            
            # Verificar se não são NaN
            import math
            if any(math.isnan(score) for score in [fundamental_score, technical_score]):
                return False
            
            return True
            
        except Exception:
            return False
    
    def _get_weights_for_context(self, context: Optional[RecommendationContext]) -> ScoreWeights:
        """Determina pesos apropriados baseados no contexto"""
        # Usar pesos padrão se não houver contexto
        if not context or not context.sector:
            return self.default_weights
        
        # Usar pesos específicos do setor se disponível
        sector_weights = self.sector_weights.get(context.sector, self.default_weights)
        
        return ScoreWeights(
            fundamental=sector_weights.fundamental,
            technical=sector_weights.technical
        )
    
    def _apply_market_adjustments(self, weights: ScoreWeights, 
                                 market_condition: MarketCondition) -> ScoreWeights:
        """Aplica ajustes baseados na condição de mercado"""
        adjustments = self.market_adjustments.get(market_condition, {})
        
        fundamental_adjustment = adjustments.get("fundamental_boost", 0.0)
        technical_adjustment = adjustments.get("technical_boost", 0.0)
        
        # Aplicar ajustes mantendo soma = 1.0
        new_fundamental = weights.fundamental + fundamental_adjustment
        new_technical = weights.technical + technical_adjustment
        
        # Normalizar para manter soma = 1.0
        total = new_fundamental + new_technical
        if total > 0:
            new_fundamental /= total
            new_technical /= total
        
        return ScoreWeights(
            fundamental=new_fundamental,
            technical=new_technical
        )
    
    def _apply_sector_adjustment(self, score: float, 
                               context: RecommendationContext) -> float:
        """Aplica ajuste baseado na performance setorial"""
        if not context.sector_performance:
            return score
        
        # Ajuste baseado na performance do setor
        # Performance positiva do setor = leve boost
        # Performance negativa do setor = leve penalidade
        sector_factor = context.sector_performance / 100.0  # Converter para decimal
        adjustment = sector_factor * 5  # Máximo ajuste de ±5 pontos
        
        return score + adjustment
    
    def _calculate_confidence(self, fundamental_score: float, technical_score: float,
                            weights: ScoreWeights, context: Optional[RecommendationContext]) -> float:
        """Calcula nível de confiança da recomendação"""
        try:
            base_confidence = 70.0  # Confiança base
            
            # Fator 1: Convergência entre scores
            score_difference = abs(fundamental_score - technical_score)
            convergence_factor = max(0, 30 - score_difference) / 30 * 20  # Máximo 20 pontos
            
            # Fator 2: Qualidade dos scores individuais
            quality_factor = 0
            if fundamental_score > 70 or fundamental_score < 30:
                quality_factor += 5  # Scores extremos são mais confiáveis
            if technical_score > 70 or technical_score < 30:
                quality_factor += 5
            
            # Fator 3: Ajustes por contexto de mercado
            market_factor = 0
            if context and context.market_condition in self.market_adjustments:
                market_adjustments = self.market_adjustments[context.market_condition]
                market_factor = market_adjustments.get("confidence_bonus", 0) * 100
                market_factor += market_adjustments.get("confidence_penalty", 0) * 100
            
            # Fator 4: Volatilidade
            volatility_factor = 0
            if context and context.volatility_factor:
                # Alta volatilidade reduz confiança
                if context.volatility_factor > 2.0:
                    volatility_factor = -10
                elif context.volatility_factor > 1.5:
                    volatility_factor = -5
                elif context.volatility_factor < 0.5:
                    volatility_factor = 5
            
            # Combinar fatores
            confidence = (
                base_confidence +
                convergence_factor +
                quality_factor +
                market_factor +
                volatility_factor
            )
            
            return max(20, min(95, confidence))
            
        except Exception as e:
            self.logger.warning(f"Erro no cálculo de confiança: {str(e)}")
            return 50.0
    
    def get_recommendation_weights_summary(self, context: Optional[RecommendationContext] = None) -> Dict:
        """Retorna resumo dos pesos utilizados"""
        weights = self._get_weights_for_context(context)
        
        if context and context.market_condition != MarketCondition.NORMAL:
            adjusted_weights = self._apply_market_adjustments(weights, context.market_condition)
        else:
            adjusted_weights = weights
        
        return {
            "base_weights": {
                "fundamental": weights.fundamental,
                "technical": weights.technical
            },
            "adjusted_weights": {
                "fundamental": adjusted_weights.fundamental,
                "technical": adjusted_weights.technical
            },
            "context": {
                "sector": context.sector.value if context and context.sector else None,
                "market_condition": context.market_condition.value if context else "NORMAL",
                "volatility_factor": context.volatility_factor if context else 1.0,
                "sector_performance": context.sector_performance if context else None
            },
            "quality_checks": {
                "weights_sum": round(adjusted_weights.fundamental + adjusted_weights.technical, 3),
                "valid_context": context is not None
            }
        }
    
    def validate_recommendation_quality(self, fundamental_score: float, technical_score: float,
                                      combined_score: float, confidence_level: float) -> Dict:
        """
        Valida a qualidade da recomendação gerada
        
        Args:
            fundamental_score: Score fundamentalista
            technical_score: Score técnico
            combined_score: Score combinado
            confidence_level: Nível de confiança
            
        Returns:
            Dict com resultado da validação
        """
        validation_result = {
            "is_valid": True,
            "warnings": [],
            "errors": [],
            "quality_score": 100.0
        }
        
        try:
            # Validação 1: Scores em range válido
            for score_name, score_value in [
                ("fundamental", fundamental_score),
                ("technical", technical_score),
                ("combined", combined_score),
                ("confidence", confidence_level)
            ]:
                if not 0 <= score_value <= 100:
                    validation_result["errors"].append(f"Score {score_name} fora do range (0-100): {score_value}")
                    validation_result["is_valid"] = False
            
            # Validação 2: Divergência extrema entre scores
            score_diff = abs(fundamental_score - technical_score)
            if score_diff > self.quality_thresholds["max_score_deviation"]:
                validation_result["warnings"].append(
                    f"Divergência alta entre scores fundamental e técnico: {score_diff:.1f}"
                )
                validation_result["quality_score"] -= 20
            
            # Validação 3: Confiança muito baixa
            if confidence_level < self.quality_thresholds["min_confidence"]:
                validation_result["warnings"].append(
                    f"Nível de confiança baixo: {confidence_level:.1f}%"
                )
                validation_result["quality_score"] -= 15
            
            # Validação 4: Score combinado vs componentes
            expected_range_min = min(fundamental_score, technical_score) - 10
            expected_range_max = max(fundamental_score, technical_score) + 10
            
            if not (expected_range_min <= combined_score <= expected_range_max):
                validation_result["warnings"].append(
                    f"Score combinado fora do range esperado: {combined_score:.1f}"
                )
                validation_result["quality_score"] -= 10
            
            # Validação 5: Consistência lógica
            if (fundamental_score > 80 and technical_score > 80 and combined_score < 70):
                validation_result["warnings"].append("Inconsistência: scores altos mas resultado baixo")
                validation_result["quality_score"] -= 15
            
            if (fundamental_score < 20 and technical_score < 20 and combined_score > 30):
                validation_result["warnings"].append("Inconsistência: scores baixos mas resultado alto")
                validation_result["quality_score"] -= 15
            
            # Determinar qualidade final
            if validation_result["quality_score"] >= 80:
                validation_result["quality_level"] = "HIGH"
            elif validation_result["quality_score"] >= 60:
                validation_result["quality_level"] = "MEDIUM"
            else:
                validation_result["quality_level"] = "LOW"
            
            # Log de warnings/errors
            if validation_result["warnings"]:
                self.logger.warning(f"Warnings na validação: {validation_result['warnings']}")
            if validation_result["errors"]:
                self.logger.error(f"Errors na validação: {validation_result['errors']}")
            
        except Exception as e:
            validation_result["errors"].append(f"Erro na validação: {str(e)}")
            validation_result["is_valid"] = False
            self.logger.error(f"Erro na validação de qualidade: {str(e)}")
        
        return validation_result
    
    def create_recommendation_context(self, sector: Optional[Sector] = None,
                                    market_condition: MarketCondition = MarketCondition.NORMAL,
                                    volatility_factor: float = 1.0,
                                    sector_performance: Optional[float] = None) -> RecommendationContext:
        """
        Cria contexto para recomendação com validação
        
        Args:
            sector: Setor da empresa
            market_condition: Condição atual do mercado
            volatility_factor: Fator de volatilidade (1.0 = normal)
            sector_performance: Performance do setor em %
            
        Returns:
            RecommendationContext validado
        """
        # Validar inputs
        volatility_factor = max(0.1, min(5.0, volatility_factor))  # Limitar entre 0.1 e 5.0
        
        if sector_performance is not None:
            sector_performance = max(-50, min(50, sector_performance))  # Limitar entre ±50%
        
        context = RecommendationContext(
            sector=sector,
            market_condition=market_condition,
            volatility_factor=volatility_factor,
            sector_performance=sector_performance
        )
        
        self.logger.debug(f"Contexto criado: {context}")
        return context


# Exemplo de uso
if __name__ == "__main__":
    engine = RecommendationEngine()
    
    # Teste básico
    combined_score, confidence = engine.calculate_combined_score(75.0, 65.0)
    print(f"Score combinado: {combined_score}, Confiança: {confidence}")
    
    # Teste com contexto
    context = engine.create_recommendation_context(
        sector=Sector.FINANCIALS,
        market_condition=MarketCondition.BULL_MARKET
    )
    
    combined_score, confidence = engine.calculate_combined_score(75.0, 65.0, context)
    print(f"Com contexto - Score: {combined_score}, Confiança: {confidence}")
    
    # Resumo de pesos
    weights_summary = engine.get_recommendation_weights_summary(context)
    print(f"Resumo de pesos: {weights_summary}")
    
    # Validação de qualidade
    validation = engine.validate_recommendation_quality(75.0, 65.0, combined_score, confidence)
    print(f"Validação: {validation}")
