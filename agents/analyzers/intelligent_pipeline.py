# agents/analyzers/intelligent_pipeline.py
"""
Pipeline Inteligente de Análise Fundamentalista
Coordena múltiplas análises e gera insights automaticamente
"""
import asyncio
import logging
from typing import List, Dict, Any
from datetime import datetime

from agno.agent import Agent
from agno.models.anthropic import Claude
from agno.tools.reasoning import ReasoningTools

from .fundamental_scoring_system import FundamentalAnalyzerAgent

logger = logging.getLogger(__name__)

class IntelligentAnalysisPipeline(Agent):
    def __init__(self):
        super().__init__(
            model=Claude(id="claude-sonnet-4-20250514"),
            tools=[
                ReasoningTools(add_instructions=True),
            ],
            instructions="""
            Você coordena análises fundamentalistas em lote e gera insights.
            
            FUNÇÕES:
            1. Priorizar ações para análise baseado em critérios
            2. Identificar padrões entre múltiplas análises
            3. Detectar outliers e anomalias setoriais
            4. Gerar insights automáticos sobre tendências
            5. Recomendar ajustes nos algoritmos
            
            Use ReasoningTools para validar conclusões sobre mercado.
            """,
            markdown=True,
        )
        
        self.analyzer = FundamentalAnalyzerAgent()
    
    async def analyze_portfolio(self, stock_codes: List[str]) -> Dict[str, Any]:
        """Analisa portfolio com insights inteligentes"""
        
        # 1. Executar análises individuais
        individual_results = []
        for stock_code in stock_codes:
            try:
                if hasattr(self.analyzer, 'analyze_single_stock_with_reasoning'):
                    result = await self.analyzer.analyze_single_stock_with_reasoning(stock_code)
                else:
                    result = self.analyzer.analyze_single_stock(stock_code)
                individual_results.append(result)
                logger.info(f"✅ {stock_code} analisado")
            except Exception as e:
                individual_results.append({
                    "stock_code": stock_code,
                    "error": str(e)
                })
                logger.error(f"❌ {stock_code}: {e}")
        
        # 2. Análise de portfolio com ReasoningTools
        portfolio_prompt = f"""
        ANÁLISE DE PORTFOLIO INTELIGENTE
        
        AÇÕES ANALISADAS: {len(stock_codes)}
        
        RESULTADOS:
        {self._format_results_for_analysis(individual_results)}
        
        ANÁLISE REQUERIDA:
        1. Identifique os 3 melhores scores e padrões em comum
        2. Identifique os 3 piores scores e problemas recorrentes
        3. Analise distribuição setorial dos scores
        4. Detecte outliers (scores inconsistentes com setor)
        5. Recomende estratégia de portfolio baseada em fundamentos
        
        Use ReasoningTools para validar cada insight gerado.
        """
        
        portfolio_insights = await self.run(portfolio_prompt)
        
        return {
            "individual_analyses": individual_results,
            "portfolio_insights": portfolio_insights,
            "summary_stats": self._calculate_portfolio_stats(individual_results),
            "analysis_timestamp": datetime.now().isoformat(),
            "stocks_analyzed": len([r for r in individual_results if "error" not in r]),
            "stocks_failed": len([r for r in individual_results if "error" in r])
        }
    
    def _format_results_for_analysis(self, results: List[Dict]) -> str:
        """Formata resultados para análise"""
        formatted = []
        for result in results:
            if "error" not in result:
                code = result.get('stock_code', 'UNKNOWN')
                score = result.get('fundamental_score', {}).get('composite_score', 0)
                tier = result.get('fundamental_score', {}).get('quality_tier', 'unknown')
                sector = result.get('sector', 'Desconhecido')
                formatted.append(f"- {code}: Score {score:.1f} ({tier}) - Setor: {sector}")
        return "\n".join(formatted)
    
    def _calculate_portfolio_stats(self, results: List[Dict]) -> Dict[str, Any]:
        """Calcula estatísticas do portfolio"""
        valid_results = [r for r in results if "error" not in r]
        if not valid_results:
            return {"error": "Nenhum resultado válido"}
        
        scores = [r.get('fundamental_score', {}).get('composite_score', 0) for r in valid_results]
        
        return {
            "total_stocks": len(results),
            "successful_analyses": len(valid_results),
            "average_score": sum(scores) / len(scores) if scores else 0,
            "highest_score": max(scores) if scores else 0,
            "lowest_score": min(scores) if scores else 0,
            "scores_above_70": len([s for s in scores if s >= 70]),
            "scores_below_50": len([s for s in scores if s < 50])
        }
