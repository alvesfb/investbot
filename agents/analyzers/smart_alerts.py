# agents/analyzers/smart_alerts.py
"""
Sistema de Alertas Inteligentes com Agno
"""
from typing import List, Dict
from agno.agent import Agent
from agno.models.anthropic import Claude
from agno.tools.reasoning import ReasoningTools


class SmartAlertAgent(Agent):
    def __init__(self):
        super().__init__(
            model=Claude(id="claude-sonnet-4-20250514"),
            tools=[
                ReasoningTools(add_instructions=True),
            ],
            instructions="""
            Você é um sistema de alertas inteligente para análise \
                fundamentalista.
            
            Detecta automaticamente:
            1. Mudanças significativas em scores fundamentalistas
            2. Discrepâncias entre preço de mercado e valor fundamentalista
            3. Deterioração de métricas de qualidade
            4. Oportunidades de valor (value traps vs value opportunities)
            
            Use ReasoningTools para evitar falsos positivos.
            """,
            markdown=True,
        )
    
    async def detect_opportunities(self, analyses: List[Dict]) -> List[Dict]:
        """Detecta oportunidades usando ReasoningTools"""
        
        opportunities_prompt = f"""
        DETECÇÃO DE OPORTUNIDADES DE INVESTIMENTO
        
        ANÁLISES RECENTES:
        {self._format_analyses(analyses)}
        
        TAREFAS:
        1. Identifique empresas com scores fundamentalistas >70 mas P/L <15
        2. Detecte empresas com ROE >20% e score geral >60
        3. Encontre possíveis value traps (score baixo caindo ainda mais)
        4. Use ReasoningTools para validar cada oportunidade identificada
        
        Para cada oportunidade, explique o racional e calcule potencial upside.
        """
        
        opportunities = await self.run(opportunities_prompt)
        return opportunities
    