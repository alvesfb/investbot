# utils/justification_generator.py
"""
Gerador de Justificativas Automáticas - Fase 3
Sistema para criação de justificativas textuais para recomendações usando Claude

Funcionalidades:
- Templates estruturados por tipo de recomendação
- Contextualização setorial
- Evidências baseadas em indicadores
- Formatação consistente
- Personalização por nível de risco
"""

from typing import Dict, List, Optional
from enum import Enum
import json
import logging

from agno.agent import Agent
from database.repositories import get_stock_repository, get_fundamental_repository

logger = logging.getLogger(__name__)


class JustificationTemplate(Enum):
    """Templates de justificativa por classificação"""
    COMPRA_FORTE = "COMPRA_FORTE"
    COMPRA = "COMPRA"
    NEUTRO = "NEUTRO"
    VENDA = "VENDA"
    VENDA_FORTE = "VENDA_FORTE"


class JustificationGenerator:
    """
    Gerador de justificativas automáticas para recomendações
    
    Utiliza o agente Claude para gerar justificativas consistentes e informativas
    baseadas nos scores e dados fundamentalistas/técnicos disponíveis.
    """
    
    def __init__(self, agent: Agent):
        """
        Inicializa o gerador de justificativas
        
        Args:
            agent: Instância do agente Agno/Claude configurado
        """
        self.agent = agent
        self.logger = logger
        self.stock_repo = get_stock_repository()
        self.fundamental_repo = get_fundamental_repository()
        
        # Templates base para cada tipo de recomendação
        self.templates = self._initialize_templates()
        
        # Contextos setoriais para personalização
        self.sector_contexts = self._initialize_sector_contexts()
        
        self.logger.info("JustificationGenerator inicializado")
    
    def _initialize_templates(self) -> Dict[JustificationTemplate, str]:
        """Inicializa templates base para justificativas"""
        return {
            JustificationTemplate.COMPRA_FORTE: """
Baseado na análise quantitativa, esta ação apresenta características muito atrativas para investimento:

PONTOS FORTES:
{positive_indicators}

ANÁLISE FUNDAMENTALISTA (Score: {fundamental_score}/100):
{fundamental_analysis}

ANÁLISE TÉCNICA (Score: {technical_score}/100):
{technical_analysis}

CONCLUSÃO: Recomendação de COMPRA FORTE com {confidence_level}% de confiança. {sector_context}

RISCOS: {risk_factors}
            """,
            
            JustificationTemplate.COMPRA: """
A análise indica uma oportunidade de investimento com fundamentos positivos:

ASPECTOS POSITIVOS:
{positive_indicators}

FUNDAMENTALISTA (Score: {fundamental_score}/100):
{fundamental_analysis}

TÉCNICA (Score: {technical_score}/100):
{technical_analysis}

RECOMENDAÇÃO: COMPRA com {confidence_level}% de confiança. {sector_context}

CONSIDERAÇÕES: {risk_factors}
            """,
            
            JustificationTemplate.NEUTRO: """
A análise apresenta aspectos mistos, sugerindo posição neutra:

PONTOS EQUILIBRADOS:
{mixed_indicators}

FUNDAMENTALISTA (Score: {fundamental_score}/100):
{fundamental_analysis}

TÉCNICA (Score: {technical_score}/100):
{technical_analysis}

POSICIONAMENTO: NEUTRO com {confidence_level}% de confiança. {sector_context}

MONITORAMENTO: {watch_factors}
            """,
            
            JustificationTemplate.VENDA: """
A análise indica fragilidades que sugerem redução de posição:

PONTOS DE ATENÇÃO:
{negative_indicators}

FUNDAMENTALISTA (Score: {fundamental_score}/100):
{fundamental_analysis}

TÉCNICA (Score: {technical_score}/100):
{technical_analysis}

RECOMENDAÇÃO: VENDA com {confidence_level}% de confiança. {sector_context}

RISCOS IDENTIFICADOS: {risk_factors}
            """,
            
            JustificationTemplate.VENDA_FORTE: """
A análise revela sinais preocupantes que indicam venda imediata:

ALERTAS CRÍTICOS:
{critical_indicators}

FUNDAMENTALISTA (Score: {fundamental_score}/100):
{fundamental_analysis}

TÉCNICA (Score: {technical_score}/100):
{technical_analysis}

AÇÃO RECOMENDADA: VENDA FORTE com {confidence_level}% de confiança. {sector_context}

RISCOS ELEVADOS: {risk_factors}
            """
        }
    
    def _initialize_sector_contexts(self) -> Dict[str, str]:
        """Inicializa contextos específicos por setor"""
        return {
            "Financeiro": "Setor financeiro sensível a mudanças na Selic e spread bancário.",
            "Tecnologia": "Setor de tecnologia com foco em crescimento e inovação.",
            "Utilidades": "Setor de utilidades com perfil defensivo e dividendos atrativos.",
            "Energia": "Setor energético influenciado por preços de commodities.",
            "Saúde": "Setor de saúde com crescimento estável e regulamentação específica.",
            "Materiais": "Setor de materiais cíclico e dependente da economia global.",
            "Industrial": "Setor industrial ligado ao ciclo econômico e infraestrutura.",
            "Consumo Discricionário": "Setor de consumo discricionário sensível à renda disponível.",
            "Consumo Básico": "Setor de consumo básico com características defensivas.",
            "Imobiliário": "Setor imobiliário influenciado por juros e demanda habitacional.",
            "Comunicações": "Setor de comunicações em transformação digital."
        }
    
    async def generate(self, stock_code: str, fundamental_score: float, technical_score: float,
                      combined_score: float, classification) -> str:
        """
        Gera justificativa automática para a recomendação
        
        Args:
            stock_code: Código da ação
            fundamental_score: Score fundamentalista
            technical_score: Score técnico
            combined_score: Score combinado
            classification: Classificação da recomendação
            
        Returns:
            Justificativa textual estruturada
        """
        try:
            # Coletar dados adicionais
            stock_data = await self._collect_stock_data(stock_code)
            fundamental_data = await self._collect_fundamental_data(stock_code)
            
            # Determinar template apropriado
            template = self._get_template_for_classification(classification)
            
            # Gerar componentes da justificativa
            indicators = self._generate_indicators(fundamental_score, technical_score, classification)
            fundamental_analysis = await self._generate_fundamental_analysis(fundamental_data, fundamental_score)
            technical_analysis = self._generate_technical_analysis(technical_score)
            sector_context = self._get_sector_context(stock_data.get('setor'))
            risk_factors = await self._generate_risk_factors(stock_code, combined_score, classification)
            
            # Calcular nível de confiança
            confidence_level = self._calculate_display_confidence(fundamental_score, technical_score)
            
            # Formatar template
            justification = template.format(
                stock_code=stock_code,
                fundamental_score=round(fundamental_score, 1),
                technical_score=round(technical_score, 1),
                combined_score=round(combined_score, 1),
                confidence_level=round(confidence_level, 1),
                positive_indicators=indicators.get('positive', ''),
                negative_indicators=indicators.get('negative', ''),
                mixed_indicators=indicators.get('mixed', ''),
                critical_indicators=indicators.get('critical', ''),
                fundamental_analysis=fundamental_analysis,
                technical_analysis=technical_analysis,
                sector_context=sector_context,
                risk_factors=risk_factors,
                watch_factors=indicators.get('watch', '')
            )
            
            # Refinar com Claude para melhor qualidade
            refined_justification = await self._refine_with_claude(justification, stock_code, classification)
            
            self.logger.info(f"Justificativa gerada para {stock_code}: {len(refined_justification)} caracteres")
            
            return refined_justification
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar justificativa para {stock_code}: {str(e)}")
            # Fallback para justificativa básica
            return self._generate_fallback_justification(stock_code, combined_score, classification)
    
    async def _collect_stock_data(self, stock_code: str) -> Dict:
        """Coleta dados básicos da ação"""
        try:
            stock = self.stock_repo.get_stock_by_code(stock_code)
            if stock:
                return {
                    'nome': stock.nome,
                    'setor': stock.setor,
                    'preco_atual': stock.preco_atual,
                    'market_cap': stock.market_cap
                }
        except Exception as e:
            self.logger.warning(f"Erro ao coletar dados da ação {stock_code}: {str(e)}")
        
        return {'nome': stock_code, 'setor': None}
    
    async def _collect_fundamental_data(self, stock_code: str) -> Optional[Dict]:
        """Coleta dados da análise fundamentalista"""
        try:
            # Buscar na estrutura atual do projeto
            with self.fundamental_repo._get_session() as db:
                stock = self.stock_repo.get_stock_by_code(stock_code)
                if not stock:
                    return None
                    
                # Usar campos disponíveis no modelo atual
                return {
                    'pe_ratio': getattr(stock, 'p_l', None),
                    'pb_ratio': getattr(stock, 'p_vp', None),
                    'roe': getattr(stock, 'roe', None),
                    'roic': getattr(stock, 'roic', None),
                    'market_cap': stock.market_cap,
                    'preco_atual': stock.preco_atual
                }
        except Exception as e:
            self.logger.warning(f"Erro ao coletar dados fundamentalistas para {stock_code}: {str(e)}")
        
        return None
    
    def _get_template_for_classification(self, classification) -> str:
        """Retorna template apropriado para a classificação"""
        template_map = {
            "COMPRA_FORTE": JustificationTemplate.COMPRA_FORTE,
            "COMPRA": JustificationTemplate.COMPRA,
            "NEUTRO": JustificationTemplate.NEUTRO,
            "VENDA": JustificationTemplate.VENDA,
            "VENDA_FORTE": JustificationTemplate.VENDA_FORTE
        }
        
        classification_value = classification.value if hasattr(classification, 'value') else str(classification)
        template_key = template_map.get(classification_value, JustificationTemplate.NEUTRO)
        return self.templates[template_key]
    
    def _generate_indicators(self, fundamental_score: float, technical_score: float, classification) -> Dict[str, str]:
        """Gera indicadores baseados nos scores"""
        indicators = {
            'positive': [],
            'negative': [],
            'mixed': [],
            'critical': [],
            'watch': []
        }
        
        # Indicadores fundamentalistas
        if fundamental_score >= 70:
            indicators['positive'].append("• Fundamentos sólidos e consistentes")
        elif fundamental_score >= 50:
            indicators['mixed'].append("• Fundamentos equilibrados")
        elif fundamental_score >= 30:
            indicators['negative'].append("• Fundamentos fracos")
        else:
            indicators['critical'].append("• Fundamentos muito fracos")
        
        # Indicadores técnicos
        if technical_score >= 70:
            indicators['positive'].append("• Momentum técnico positivo")
        elif technical_score >= 50:
            indicators['mixed'].append("• Indicadores técnicos neutros")
        elif technical_score >= 30:
            indicators['negative'].append("• Pressão vendedora técnica")
        else:
            indicators['critical'].append("• Sinais técnicos muito negativos")
        
        # Convergência/divergência
        score_diff = abs(fundamental_score - technical_score)
        classification_value = classification.value if hasattr(classification, 'value') else str(classification)
        
        if score_diff <= 10:
            indicators['positive'].append("• Convergência entre análises fundamental e técnica")
        elif score_diff >= 30:
            if classification_value in ['COMPRA_FORTE', 'COMPRA']:
                indicators['watch'].append("• Divergência entre análises - monitorar evolução")
            else:
                indicators['negative'].append("• Divergência significativa entre análises")
        
        # Converter listas em strings
        for key in indicators:
            indicators[key] = '\n'.join(indicators[key]) if indicators[key] else "Nenhum identificado."
        
        return indicators
    
    async def _generate_fundamental_analysis(self, fundamental_data: Optional[Dict], score: float) -> str:
        """Gera análise fundamentalista textual"""
        if not fundamental_data:
            return f"Análise limitada por dados indisponíveis. Score calculado: {score:.1f}/100."
        
        analysis_parts = []
        
        # P/L
        if fundamental_data.get('pe_ratio'):
            pe = fundamental_data['pe_ratio']
            if pe < 10:
                analysis_parts.append(f"P/L baixo ({pe:.1f}x) indica potencial subvalorização")
            elif pe > 25:
                analysis_parts.append(f"P/L elevado ({pe:.1f}x) sugere expectativas altas")
            else:
                analysis_parts.append(f"P/L adequado ({pe:.1f}x) dentro de parâmetros normais")
        
        # P/VPA
        if fundamental_data.get('pb_ratio'):
            pb = fundamental_data['pb_ratio']
            if pb < 1.0:
                analysis_parts.append(f"P/VPA ({pb:.1f}x) indica possível subvalorização")
            elif pb > 3.0:
                analysis_parts.append(f"P/VPA elevado ({pb:.1f}x) sugere prêmio de mercado")
            else:
                analysis_parts.append(f"P/VPA ({pb:.1f}x) em nível adequado")
        
        # ROE
        if fundamental_data.get('roe'):
            roe = fundamental_data['roe']
            # Assumir que ROE já está em decimal, converter para %
            if isinstance(roe, float) and roe < 1:
                roe_pct = roe * 100
            else:
                roe_pct = roe
                
            if roe_pct > 15:
                analysis_parts.append(f"ROE forte ({roe_pct:.1f}%) demonstra eficiência na geração de lucro")
            elif roe_pct > 10:
                analysis_parts.append(f"ROE adequado ({roe_pct:.1f}%) dentro de padrões setoriais")
            else:
                analysis_parts.append(f"ROE baixo ({roe_pct:.1f}%) indica ineficiência na geração de retorno")
        
        # Market Cap
        if fundamental_data.get('market_cap'):
            market_cap = fundamental_data['market_cap']
            if market_cap > 100_000_000_000:  # > 100B
                analysis_parts.append("Empresa de grande porte com liquidez elevada")
            elif market_cap > 10_000_000_000:  # > 10B
                analysis_parts.append("Empresa de médio-grande porte")
            else:
                analysis_parts.append("Empresa de menor porte com maior potencial de crescimento")
        
        if not analysis_parts:
            return f"Dados fundamentalistas limitados. Score baseado em indicadores disponíveis: {score:.1f}/100."
        
        return '. '.join(analysis_parts) + '.'
    
    def _generate_technical_analysis(self, score: float) -> str:
        """Gera análise técnica textual"""
        if score >= 70:
            return f"Indicadores técnicos mostram força ({score:.1f}/100), com momentum positivo e sinais de continuidade de alta."
        elif score >= 50:
            return f"Cenário técnico neutro ({score:.1f}/100), sem direção clara definida no curto prazo."
        elif score >= 30:
            return f"Indicadores técnicos fracos ({score:.1f}/100), com pressão vendedora e sinais de cautela."
        else:
            return f"Cenário técnico muito negativo ({score:.1f}/100), com fortes sinais de venda e deterioração do momentum."
    
    def _get_sector_context(self, sector: Optional[str]) -> str:
        """Retorna contexto setorial"""
        if not sector:
            return "Análise setorial limitada por dados indisponíveis."
        
        return self.sector_contexts.get(sector, "Análise dentro do contexto setorial apropriado.")
    
    async def _generate_risk_factors(self, stock_code: str, combined_score: float, classification) -> str:
        """Gera fatores de risco baseados na análise"""
        risk_factors = []
        
        # Riscos baseados no score
        if combined_score < 30:
            risk_factors.append("Alto risco de perdas no curto prazo")
        elif combined_score < 50:
            risk_factors.append("Risco moderado de volatilidade")
        
        # Riscos por classificação
        classification_value = classification.value if hasattr(classification, 'value') else str(classification)
        
        if classification_value in ['VENDA', 'VENDA_FORTE']:
            risk_factors.append("Deterioração dos fundamentos")
            risk_factors.append("Pressão vendedora contínua")
        elif classification_value == 'NEUTRO':
            risk_factors.append("Indefinição de direção no curto prazo")
        elif classification_value in ['COMPRA', 'COMPRA_FORTE']:
            risk_factors.append("Volatilidade inerente ao mercado")
            risk_factors.append("Mudanças no cenário macroeconômico")
        
        # Riscos gerais sempre presentes
        risk_factors.extend([
            "Flutuações do mercado brasileiro",
            "Mudanças na política econômica",
            "Fatores setoriais específicos"
        ])
        
        return '. '.join(risk_factors[:4]) + '.'  # Limitar a 4 fatores principais
    
    def _calculate_display_confidence(self, fundamental_score: float, technical_score: float) -> float:
        """Calcula nível de confiança para exibição"""
        # Confiança baseada na convergência dos scores
        score_diff = abs(fundamental_score - technical_score)
        base_confidence = max(60, 100 - score_diff * 2)
        
        # Ajustar baseado na qualidade dos scores
        if fundamental_score > 70 or fundamental_score < 30:
            base_confidence += 5  # Scores extremos são mais confiáveis
        if technical_score > 70 or technical_score < 30:
            base_confidence += 5
        
        return min(95, max(50, base_confidence))
    
    async def _refine_with_claude(self, justification: str, stock_code: str, classification) -> str:
        """Refina a justificativa usando Claude para melhor qualidade"""
        try:
            classification_value = classification.value if hasattr(classification, 'value') else str(classification)
            
            prompt = f"""
Refine e melhore a justificativa de investimento abaixo, mantendo a estrutura e informações técnicas, mas tornando o texto mais fluido e profissional:

AÇÃO: {stock_code}
RECOMENDAÇÃO: {classification_value}

JUSTIFICATIVA ATUAL:
{justification}

INSTRUÇÕES:
1. Mantenha todos os números e dados técnicos exatos
2. Melhore a fluidez e clareza do texto
3. Use linguagem profissional mas acessível
4. Mantenha a estrutura de tópicos
5. Não adicione informações não presentes no texto original
6. Limite a resposta a 500 palavras

JUSTIFICATIVA REFINADA:
"""
            
            response = await self.agent.run(prompt)
            
            # Extrair apenas a justificativa refinada da resposta
            if "JUSTIFICATIVA REFINADA:" in response:
                refined = response.split("JUSTIFICATIVA REFINADA:")[-1].strip()
            else:
                refined = response.strip()
            
            # Validar se o refinamento mantém informações essenciais
            if len(refined) > 100 and stock_code in refined:
                return refined
            else:
                self.logger.warning(f"Refinamento inadequado para {stock_code}, usando original")
                return justification
                
        except Exception as e:
            self.logger.warning(f"Erro no refinamento para {stock_code}: {str(e)}")
            return justification
    
    def _generate_fallback_justification(self, stock_code: str, combined_score: float, classification) -> str:
        """Gera justificativa básica em caso de falha"""
        classification_value = classification.value if hasattr(classification, 'value') else str(classification)
        
        classification_text = {
            "COMPRA_FORTE": "Recomendação de COMPRA FORTE",
            "COMPRA": "Recomendação de COMPRA",
            "NEUTRO": "Posicionamento NEUTRO",
            "VENDA": "Recomendação de VENDA",
            "VENDA_FORTE": "Recomendação de VENDA FORTE"
        }
        
        text = classification_text.get(classification_value, "Análise")
        
        return f"""
{text} para {stock_code} baseada em análise quantitativa.

SCORE COMBINADO: {combined_score:.1f}/100

A recomendação foi gerada através da combinação ponderada de análises fundamentalista e técnica, 
considerando o contexto setorial e as condições atuais de mercado.

IMPORTANTE: Esta é uma análise automatizada baseada em dados históricos. 
Recomenda-se análise adicional antes de decisões de investimento.

RISCOS: Investimentos em ações estão sujeitos a riscos de mercado, 
incluindo possibilidade de perdas do capital investido.
        """.strip()
    
    async def generate_batch_justifications(self, recommendations_data: List[Dict]) -> Dict[str, str]:
        """
        Gera justificativas para múltiplas recomendações em lote
        
        Args:
            recommendations_data: Lista de dicts com dados das recomendações
            
        Returns:
            Dict mapeando stock_code para justificativa
        """
        results = {}
        
        for rec_data in recommendations_data:
            try:
                justification = await self.generate(
                    rec_data['stock_code'],
                    rec_data['fundamental_score'],
                    rec_data['technical_score'],
                    rec_data['combined_score'],
                    rec_data['classification']
                )
                results[rec_data['stock_code']] = justification
                
            except Exception as e:
                self.logger.error(f"Erro ao gerar justificativa em lote para {rec_data.get('stock_code', 'UNKNOWN')}: {str(e)}")
                results[rec_data['stock_code']] = self._generate_fallback_justification(
                    rec_data['stock_code'],
                    rec_data.get('combined_score', 50.0),
                    rec_data['classification']
                )
        
        self.logger.info(f"Justificativas em lote geradas: {len(results)} de {len(recommendations_data)}")
        return results
    
    def validate_justification_quality(self, justification: str, stock_code: str) -> Dict:
        """
        Valida a qualidade da justificativa gerada
        
        Args:
            justification: Texto da justificativa
            stock_code: Código da ação
            
        Returns:
            Dict com resultado da validação
        """
        validation = {
            "is_valid": True,
            "warnings": [],
            "quality_score": 100,
            "metrics": {}
        }
        
        try:
            # Métricas básicas
            word_count = len(justification.split())
            char_count = len(justification)
            
            validation["metrics"] = {
                "word_count": word_count,
                "character_count": char_count,
                "has_stock_code": stock_code in justification,
                "has_numbers": any(char.isdigit() for char in justification),
                "has_structure": any(marker in justification for marker in ["•", "SCORE", "RECOMENDAÇÃO"])
            }
            
            # Validações de qualidade
            if word_count < 50:
                validation["warnings"].append("Justificativa muito curta")
                validation["quality_score"] -= 20
            elif word_count > 300:
                validation["warnings"].append("Justificativa muito longa")
                validation["quality_score"] -= 10
            
            if not validation["metrics"]["has_stock_code"]:
                validation["warnings"].append("Código da ação não mencionado")
                validation["quality_score"] -= 15
            
            if not validation["metrics"]["has_numbers"]:
                validation["warnings"].append("Ausência de dados quantitativos")
                validation["quality_score"] -= 10
            
            if not validation["metrics"]["has_structure"]:
                validation["warnings"].append("Estrutura não detectada")
                validation["quality_score"] -= 15
            
            # Verificar palavras-chave essenciais
            required_keywords = ["análise", "score", "recomendação"]
            missing_keywords = [kw for kw in required_keywords if kw.lower() not in justification.lower()]
            
            if missing_keywords:
                validation["warnings"].append(f"Palavras-chave ausentes: {missing_keywords}")
                validation["quality_score"] -= len(missing_keywords) * 5
            
            # Determinar validade final
            if validation["quality_score"] < 60:
                validation["is_valid"] = False
            
        except Exception as e:
            validation["warnings"].append(f"Erro na validação: {str(e)}")
            validation["is_valid"] = False
            self.logger.error(f"Erro na validação de justificativa para {stock_code}: {str(e)}")
        
        return validation


# Exemplo de uso
async def main():
    """Exemplo de uso do JustificationGenerator"""
    from agno.agent import Agent
    from agno.models.anthropic import Claude
    
    # Configurar agente (exemplo)
    agent = Agent(
        model=Claude(id="claude-sonnet-4-20250514"),
        instructions="Você é um especialista em análise de investimentos."
    )
    
    generator = JustificationGenerator(agent)
    
    # Simular classificação para teste
    class MockClassification:
        def __init__(self, value):
            self.value = value
    
    # Gerar justificativa individual
    justification = await generator.generate(
        stock_code="PETR4",
        fundamental_score=75.0,
        technical_score=65.0,
        combined_score=71.5,
        classification=MockClassification("COMPRA")
    )
    
    print(f"Justificativa gerada:\n{justification}")
    
    # Validar qualidade
    validation = generator.validate_justification_quality(justification, "PETR4")
    print(f"\nValidação: {validation}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
