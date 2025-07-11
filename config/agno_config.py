# config/agno_config.py
"""
Configuração específica do Agno Framework
"""
import os
from typing import Dict, Any, List
from config.settings import get_settings

settings = get_settings()


class AgnoConfig:
    """Configuração centralizada para Agno Framework"""
    
    def __init__(self):
        self.api_key = settings.anthropic_api_key
        self.model = settings.claude_model
        self.max_workers = settings.agno_max_workers
        self.log_level = settings.agno_log_level
        
    def get_agent_config(self, agent_name: str) -> Dict[str, Any]:
        """Retorna configuração específica para um agente"""
        base_config = {
            "api_key": self.api_key,
            "model": self.model,
            "max_retries": 3,
            "timeout": 30,
            "temperature": 0.1,  # Baixa temperatura para consistência
            "max_tokens": 4000
        }
        
        # Configurações específicas por agente
        agent_configs = {
            "StockCollector": {
                **base_config,
                "system_prompt": self._get_collector_system_prompt(),
                "tools_enabled": True,
                "parallel_execution": True
            },
            "FundamentalAnalyzer": {
                **base_config,
                "system_prompt": self._get_analyzer_system_prompt(),
                "temperature": 0.0,  # Zero temperatura para análise numérica
                "tools_enabled": True
            },
            "Recommender": {
                **base_config,
                "system_prompt": self._get_recommender_system_prompt(),
                "temperature": 0.2,  # Pouca criatividade para recomendações
                "tools_enabled": True
            }
        }
        
        return agent_configs.get(agent_name, base_config)
    
    def _get_collector_system_prompt(self) -> str:
        """System prompt para o agente coletor"""
        return """
Você é um agente especializado em coletar dados financeiros de ações brasileiras.

Seu objetivo é:
1. Coletar dados de preços, volumes e informações fundamentalistas
2. Validar a qualidade dos dados recebidos
3. Atualizar informações no banco de dados de forma consistente
4. Reportar erros e problemas de forma clara

Sempre mantenha foco em:
- Precisão dos dados coletados
- Tratamento adequado de erros
- Logging detalhado das operações
- Respeito aos rate limits das APIs

Use as ferramentas disponíveis de forma eficiente e sempre valide os dados antes de armazenar.
"""
    
    def _get_analyzer_system_prompt(self) -> str:
        """System prompt para o agente analisador"""
        return """
Você é um agente especializado em análise fundamentalista de ações brasileiras.

Seu objetivo é:
1. Analisar indicadores fundamentalistas (P/L, P/VP, ROE, ROIC, etc.)
2. Calcular scores numéricos baseados em critérios objetivos
3. Comparar empresas dentro do mesmo setor
4. Identificar empresas com fundamentos sólidos

Sempre mantenha foco em:
- Análise quantitativa rigorosa
- Comparação setorial adequada
- Scores consistentes e reproduzíveis
- Justificativas baseadas em dados

Use métodos estatísticos e financeiros reconhecidos para suas análises.
"""
    
    def _get_recommender_system_prompt(self) -> str:
        """System prompt para o agente recomendador"""
        return """
Você é um agente especializado em gerar recomendações de investimento para swing trade.

Seu objetivo é:
1. Combinar análise fundamentalista e técnica
2. Gerar recomendações claras (COMPRA/VENDA/NEUTRO)
3. Definir pontos de entrada, stop loss e take profit
4. Justificar recomendações de forma didática

Sempre mantenha foco em:
- Gestão de risco adequada
- Horizonte de 2-30 dias (swing trade)
- Justificativas claras e educativas
- Disclaimers sobre riscos

Nunca garanta retornos e sempre enfatize a gestão de risco.
"""
    
    def get_mcp_config(self) -> Dict[str, Any]:
        """Configuração para servidores MCP"""
        return {
            "yfinance_server": {
                "enabled": True,
                "url": "http://localhost:8001",
                "timeout": 30,
                "retry_attempts": 3
            },
            "filesystem_server": {
                "enabled": True,
                "base_path": str(settings.data_dir),
                "allowed_extensions": [".csv", ".json", ".txt"]
            }
        }
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Configuração de logging para agentes"""
        return {
            "level": self.log_level,
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "file": str(settings.logs_dir / "agents.log"),
            "rotation": "1 day",
            "retention": "30 days",
            "max_size": "10 MB"
        }


# Instância global
agno_config = AgnoConfig()


def get_agno_config() -> AgnoConfig:
    """Factory para obter configuração do Agno"""
    return agno_config
