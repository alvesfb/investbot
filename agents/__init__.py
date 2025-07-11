# agents/__init__.py
"""
Módulo de Agentes do Sistema de Recomendações de Investimentos

Este módulo contém agentes especializados usando Agno Framework:
- Agente Coletor: Coleta dados de ações via YFinance
- Agente Analisador: Análise fundamentalista (Fase 2)
- Agente Recomendador: Gera recomendações (Fase 3)
"""

# Imports condicionais para evitar erros se Agno não estiver instalado
try:
    from agno import Agent
    AGNO_AVAILABLE = True
except ImportError:
    AGNO_AVAILABLE = False

# Imports dos agentes
if AGNO_AVAILABLE:
    try:
        from agents.collectors.stock_collector import StockCollectorAgent
        STOCK_COLLECTOR_AVAILABLE = True
    except ImportError:
        STOCK_COLLECTOR_AVAILABLE = False
else:
    STOCK_COLLECTOR_AVAILABLE = False

# Versão do módulo
__version__ = "1.0.0"

# Exports
__all__ = []

if STOCK_COLLECTOR_AVAILABLE:
    __all__.append("StockCollectorAgent")

# Funções utilitárias
def get_available_agents():
    """Retorna lista de agentes disponíveis"""
    agents = []
    
    if STOCK_COLLECTOR_AVAILABLE:
        agents.append({
            "name": "StockCollectorAgent",
            "description": "Agente para coleta de dados de ações",
            "version": "1.0.0",
            "status": "available"
        })
    
    return agents

def check_agno_installation():
    """Verifica se Agno está instalado e disponível"""
    return {
        "agno_available": AGNO_AVAILABLE,
        "stock_collector_available": STOCK_COLLECTOR_AVAILABLE,
        "total_agents": len(get_available_agents())
    }
