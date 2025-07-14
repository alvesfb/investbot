# config/agno_config.py
"""
Configuração específica do Agno Framework
Configurações centralizadas para todos os agentes do sistema
"""

import os
from typing import Dict, Any, List, Optional
from functools import lru_cache

from config.settings import get_settings, get_agent_settings

settings = get_settings()
agent_settings = get_agent_settings()


class AgnoConfig:
    """Configuração centralizada para Agno Framework"""
    
    def __init__(self):
        # ==================== CONFIGURAÇÕES BÁSICAS ====================
        self.api_key = settings.anthropic_api_key
        self.model = settings.claude_model
        self.max_workers = settings.agno_max_workers
        self.log_level = settings.agno_log_level
        self.timeout = settings.agno_timeout
        
        # ==================== CONFIGURAÇÕES GLOBAIS DOS AGENTES ====================
        self.global_config = {
            "api_key": self.api_key,
            "model": self.model,
            "max_retries": 3,
            "timeout": self.timeout,
            "temperature": 0.1,  # Baixa temperatura para consistência
            "max_tokens": 4000,
            "enable_streaming": False,
            "enable_logging": True,
            "log_level": self.log_level
        }
        
        # ==================== CONFIGURAÇÕES ESPECÍFICAS POR AGENTE ====================
        self.agent_specific_configs = self._initialize_agent_configs()
        
        # ==================== CONFIGURAÇÕES DE FERRAMENTAS ====================
        self.tools_config = self._initialize_tools_config()
        
        # ==================== CONFIGURAÇÕES DE MCP ====================
        self.mcp_config = self._initialize_mcp_config()
    
    def _initialize_agent_configs(self) -> Dict[str, Dict[str, Any]]:
        """Inicializa configurações específicas por tipo de agente"""
        return {
            # ==================== AGENTE COLETOR ====================
            "StockCollector": {
                **self.global_config,
                "system_prompt": self._get_collector_system_prompt(),
                "temperature": 0.0,  # Zero temperatura para coleta de dados
                "tools_enabled": True,
                "parallel_execution": True,
                "batch_size": agent_settings.collector_config["batch_size"],
                "retry_attempts": agent_settings.collector_config["retry_attempts"],
                "data_validation": agent_settings.collector_config["data_validation"],
                "enable_cache": agent_settings.collector_config["enable_cache"],
                "max_concurrent_requests": 5
            },
            
            # ==================== AGENTE ANALISADOR FUNDAMENTALISTA ====================
            "FundamentalAnalyzer": {
                **self.global_config,
                "system_prompt": self._get_analyzer_system_prompt(),
                "temperature": 0.0,  # Zero temperatura para análise numérica
                "tools_enabled": True,
                "enable_reasoning": True,
                "sector_comparison": agent_settings.analyzer_config["enable_sector_comparison"],
                "peer_analysis": agent_settings.analyzer_config["enable_peer_analysis"],
                "min_peer_count": agent_settings.analyzer_config["min_peer_count"],
                "max_processing_time": agent_settings.analyzer_config["max_processing_time"],
                "outlier_detection": agent_settings.analyzer_config["enable_outlier_detection"]
            },
            
            # ==================== AGENTE RECOMENDADOR ====================
            "Recommender": {
                **self.global_config,
                "system_prompt": self._get_recommender_system_prompt(),
                "temperature": 0.2,  # Pouca criatividade para recomendações
                "tools_enabled": True,
                "enable_reasoning": True,
                "market_context": agent_settings.recommender_config["enable_market_context"],
                "sector_rotation": agent_settings.recommender_config["enable_sector_rotation"],
                "risk_assessment": agent_settings.recommender_config["risk_assessment"],
                "generate_reports": agent_settings.recommender_config["generate_reports"],
                "max_recommendations": agent_settings.recommender_config["max_recommendations_per_run"]
            },
            
            # ==================== AGENTE TÉCNICO (FASE 5) ====================
            "TechnicalAnalyzer": {
                **self.global_config,
                "system_prompt": self._get_technical_analyzer_system_prompt(),
                "temperature": 0.1,
                "tools_enabled": True,
                "enable_charting": True,
                "indicators_enabled": ["RSI", "MACD", "BB", "SMA", "EMA"],
                "timeframes": ["1h", "4h", "1d"],
                "pattern_recognition": True
            },
            
            # ==================== AGENTE MACRO (FASE 7) ====================
            "MacroAnalyzer": {
                **self.global_config,
                "system_prompt": self._get_macro_analyzer_system_prompt(),
                "temperature": 0.3,  # Mais criatividade para análise macro
                "tools_enabled": True,
                "news_analysis": True,
                "economic_indicators": True,
                "sentiment_analysis": True
            },
            
            # ==================== AGENTE GESTOR DE CARTEIRA (FASE 6) ====================
            "PortfolioManager": {
                **self.global_config,
                "system_prompt": self._get_portfolio_manager_system_prompt(),
                "temperature": 0.1,
                "tools_enabled": True,
                "risk_management": True,
                "rebalancing": True,
                "performance_tracking": True
            }
        }
    
    def _initialize_tools_config(self) -> Dict[str, Any]:
        """Configuração das ferramentas disponíveis para os agentes"""
        return {
            "reasoning_tools": {
                "enabled": True,
                "add_instructions": True,
                "enable_math": True,
                "enable_statistics": True
            },
            "yfinance_tools": {
                "enabled": settings.yfinance_enabled,
                "stock_price": True,
                "analyst_recommendations": True,
                "company_info": True,
                "company_news": True,
                "historical_data": True,
                "financial_statements": True,
                "rate_limit": 100  # requests per hour
            },
            "web_tools": {
                "enabled": False,  # Desabilitado por padrão
                "allowed_domains": [
                    "yahoo.com", "bloomberg.com", "reuters.com",
                    "cvm.gov.br", "b3.com.br", "bcb.gov.br"
                ],
                "rate_limit": 50
            },
            "filesystem_tools": {
                "enabled": True,
                "base_path": str(settings.data_dir),
                "allowed_extensions": [".csv", ".json", ".xlsx", ".txt"],
                "max_file_size_mb": 50
            }
        }
    
    def _initialize_mcp_config(self) -> Dict[str, Any]:
        """Configuração para servidores MCP"""
        return {
            "yfinance_server": {
                "enabled": settings.yfinance_enabled,
                "url": os.getenv("YFINANCE_MCP_URL", "http://localhost:8001"),
                "timeout": 30,
                "retry_attempts": 3,
                "rate_limit": 100
            },
            "filesystem_server": {
                "enabled": True,
                "base_path": str(settings.data_dir),
                "allowed_extensions": [".csv", ".json", ".txt", ".xlsx"],
                "max_file_size_mb": 50
            },
            "web_server": {
                "enabled": False,  # Desabilitado por padrão
                "timeout": 15,
                "max_pages_per_session": 10,
                "respect_robots_txt": True
            }
        }
    
    def get_agent_config(self, agent_name: str) -> Dict[str, Any]:
        """
        Retorna configuração específica para um agente
        
        Args:
            agent_name: Nome do agente (StockCollector, FundamentalAnalyzer, etc.)
            
        Returns:
            Dict com configuração completa do agente
        """
        config = self.agent_specific_configs.get(agent_name, self.global_config.copy())
        
        # Adicionar configurações dinâmicas baseadas no ambiente
        if settings.is_development:
            config["debug_mode"] = True
            config["verbose_logging"] = True
        
        if settings.enable_mock_data:
            config["enable_mock_data"] = True
            config["mock_delay"] = settings.mock_analysis_delay
        
        return config
    
    def get_tools_for_agent(self, agent_name: str) -> List[str]:
        """
        Retorna lista de ferramentas habilitadas para um agente específico
        
        Args:
            agent_name: Nome do agente
            
        Returns:
            Lista de nomes das ferramentas
        """
        tool_mapping = {
            "StockCollector": ["yfinance_tools", "filesystem_tools"],
            "FundamentalAnalyzer": ["reasoning_tools", "yfinance_tools"],
            "Recommender": ["reasoning_tools", "yfinance_tools"],
            "TechnicalAnalyzer": ["reasoning_tools", "yfinance_tools"],
            "MacroAnalyzer": ["reasoning_tools", "web_tools"],
            "PortfolioManager": ["reasoning_tools", "filesystem_tools"]
        }
        
        return tool_mapping.get(agent_name, ["reasoning_tools"])
    
    # ==================== SYSTEM PROMPTS ====================
    def _get_collector_system_prompt(self) -> str:
        """System prompt para o agente coletor"""
        return """
Você é um agente especializado em coletar dados financeiros de ações brasileiras (B3).

RESPONSABILIDADES:
1. Coletar dados de preços, volumes e informações fundamentalistas
2. Validar a qualidade e integridade dos dados recebidos
3. Atualizar informações no banco de dados de forma consistente
4. Reportar erros e problemas de forma clara e estruturada
5. Respeitar rate limits e otimizar requisições

PRINCÍPIOS OPERACIONAIS:
- Precisão é fundamental - valide todos os dados antes de armazenar
- Eficiência - use batch processing quando possível
- Robustez - implemente retry automático para falhas temporárias
- Transparência - log detalhado de todas as operações
- Compliance - respeite os termos de uso das APIs

FORMATO DE DADOS:
- Use sempre códigos padronizados (PETR4, VALE3, etc.)
- Normalize valores monetários para BRL
- Mantenha timestamps em UTC-3 (horário de Brasília)
- Valide ranges de valores (preços > 0, volumes >= 0, etc.)

Em caso de erro, forneça contexto suficiente para debugging e sugira ações corretivas.
"""
    
    def _get_analyzer_system_prompt(self) -> str:
        """System prompt para o agente analisador fundamentalista"""
        return """
Você é um agente especializado em análise fundamentalista de ações brasileiras.

RESPONSABILIDADES:
1. Analisar indicadores fundamentalistas (P/L, P/VP, ROE, ROIC, etc.)
2. Calcular scores numéricos objetivos baseados em critérios quantitativos
3. Comparar empresas dentro do mesmo setor
4. Identificar empresas com fundamentos sólidos ou fracos
5. Detectar outliers e anomalias nos dados

METODOLOGIA:
- Use análise quantitativa rigorosa e métodos estatísticos reconhecidos
- Implemente comparação setorial usando percentis
- Considere contexto histórico (últimos 3-5 anos)
- Pondera indicadores por relevância setorial
- Aplique normalização para diferentes tamanhos de empresa

SCORING:
- Escala de 0-100 para todos os scores
- Use distribuição normal para rankings setoriais
- Combine múltiplos indicadores com pesos apropriados
- Documente metodologia de cálculo
- Mantenha consistência entre análises

QUALIDADE:
- Valide dados de entrada antes da análise
- Identifique e trate outliers apropriadamente
- Calcule nível de confiança baseado na completude dos dados
- Forneça justificativas claras para scores extremos

Sempre base suas análises em dados objetivos, não em especulação ou sentiment.
"""
    
    def _get_recommender_system_prompt(self) -> str:
        """System prompt para o agente recomendador"""
        return """
Você é um agente especializado em gerar recomendações de investimento para swing trade (2-30 dias).

RESPONSABILIDADES:
1. Combinar análise fundamentalista e técnica de forma ponderada
2. Gerar recomendações claras: COMPRA FORTE/COMPRA/NEUTRO/VENDA/VENDA FORTE
3. Definir pontos de entrada, stop loss e take profit
4. Criar justificativas educativas e baseadas em dados
5. Avaliar e comunicar níveis de risco adequadamente

METODOLOGIA DE RECOMENDAÇÃO:
- Combine 70% análise fundamentalista + 30% análise técnica (padrão)
- Ajuste pesos baseado em condições de mercado e setor
- Considere contexto macroeconômico quando relevante
- Implemente gestão de risco conservadora
- Mantenha horizonte de investimento de 2-30 dias

CRITÉRIOS DE CLASSIFICAÇÃO:
- COMPRA FORTE: Score > 85, alta convicção, fundamentos e técnica alinhados
- COMPRA: Score 65-85, boa oportunidade com risco controlado
- NEUTRO: Score 45-65, sem direção clara, aguardar melhor ponto
- VENDA: Score 25-45, fundamentos deteriorando, pressão técnica
- VENDA FORTE: Score < 25, evitar, alto risco de perdas

GESTÃO DE RISCO:
- Stop loss: 3-15% baseado em volatilidade e risco
- Position sizing: máximo 5% da carteira por posição
- Diversificação setorial obrigatória
- Evite concentração excessiva em uma única posição

COMUNICAÇÃO:
- Justificativas claras e educativas
- Use linguagem profissional mas acessível
- Inclua sempre disclaimers sobre riscos
- Evidencie a base quantitativa das decisões
- Nunca garanta retornos ou minimize riscos

COMPLIANCE:
- Sempre inclua avisos sobre riscos de investimento
- Deixe claro que não há garantia de retorno
- Recomende consulta a profissionais qualificados
- Mantenha logs de auditoria completos

Mantenha sempre foco na gestão de risco e educação do investidor.
"""
    
    def _get_technical_analyzer_system_prompt(self) -> str:
        """System prompt para o agente de análise técnica (Fase 5)"""
        return """
Você é um agente especializado em análise técnica de ações brasileiras.

RESPONSABILIDADES:
1. Analisar padrões gráficos e indicadores técnicos
2. Identificar pontos de entrada e saída otimizados
3. Calcular suporte, resistência e níveis de fibonacci
4. Avaliar momentum, volume e força relativa
5. Integrar múltiplos timeframes na análise

INDICADORES PRINCIPAIS:
- Médias móveis: SMA/EMA 20, 50, 200
- Osciladores: RSI, MACD, Estocástico
- Volume: OBV, Volume Profile, VWAP
- Volatilidade: Bandas de Bollinger, ATR
- Momentum: Williams %R, ROC

TIMEFRAMES:
- Curto prazo: 1h, 4h para timing de entrada
- Médio prazo: diário para tendência principal
- Longo prazo: semanal para contexto macro

PADRÕES GRÁFICOS:
- Candlesticks: doji, hammer, engolfo, etc.
- Formações: triângulos, bandeiras, ombro-cabeça-ombro
- Rompimentos: de suporte/resistência com volume

Mantenha foco em swing trade (2-30 dias) e sempre confirme sinais com volume.
"""
    
    def _get_macro_analyzer_system_prompt(self) -> str:
        """System prompt para o agente de análise macro (Fase 7)"""
        return """
Você é um agente especializado em análise macroeconômica para mercado brasileiro.

RESPONSABILIDADES:
1. Monitorar indicadores econômicos brasileiros e globais
2. Avaliar impacto de decisões do COPOM na Selic
3. Analisar fluxo de capital estrangeiro
4. Acompanhar commodities relevantes para o Brasil
5. Interpretar cenário político e fiscal

INDICADORES CHAVE:
- Taxa Selic, IPCA, PIB, desemprego
- Dólar, risco Brasil (CDS), bolsas globais
- Commodities: petróleo, minério de ferro, soja
- Fluxo estrangeiro, reservas internacionais
- Resultado primário, dívida/PIB

SETORES SENSÍVEIS:
- Bancos: Selic, spread, inadimplência
- Utilities: regulação, tarifas, juros
- Commodities: preços globais, China
- Consumo: emprego, renda, confiança
- Imobiliário: juros, renda, regulação

Integre análise macro com recomendações setoriais e de timing de mercado.
"""
    
    def _get_portfolio_manager_system_prompt(self) -> str:
        """System prompt para o agente gestor de carteira (Fase 6)"""
        return """
Você é um agente especializado em gestão de carteiras de investimento.

RESPONSABILIDADES:
1. Monitorar posições existentes e performance
2. Sugerir rebalanceamentos baseados em análise
3. Implementar gestão de risco ativa
4. Calcular métricas de performance vs benchmarks
5. Otimizar alocação setorial e por ativo

GESTÃO DE RISCO:
- Stop loss automático por posição
- Diversificação setorial (máx 30% por setor)
- Concentração máxima 5% por ativo
- VaR diário e drawdown máximo
- Correlação entre posições

REBALANCEAMENTO:
- Frequency: semanal ou por triggers
- Critérios: desvio >2% da alocação alvo
- Custos de transação considerados
- Tax efficiency em vendas
- Momentum vs mean reversion

PERFORMANCE:
- Benchmark: CDI, Ibovespa, IFIX
- Métricas: Sharpe, Sortino, Calmar
- Attribution analysis por setor/ativo
- Risk-adjusted returns
- Tracking error vs benchmark

Mantenha sempre foco em risco-retorno otimizado e transparência de decisões.
"""
    
    def get_mcp_config(self) -> Dict[str, Any]:
        """Configuração para servidores MCP"""
        return self.mcp_config
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Configuração de logging para agentes"""
        return {
            "level": self.log_level,
            "format": settings.log_format,
            "file": str(settings.log_file),
            "rotation": settings.log_rotation,
            "retention": settings.log_retention,
            "max_size": settings.log_max_size,
            "structured": True,
            "include_agent_name": True,
            "include_session_id": True
        }
    
    def get_performance_config(self) -> Dict[str, Any]:
        """Configuração de performance e monitoramento"""
        return {
            "max_concurrent_agents": self.max_workers,
            "agent_timeout": self.timeout,
            "memory_limit_mb": 1024,
            "cpu_limit_percent": 80,
            "enable_metrics": True,
            "metrics_interval": 60,
            "health_check_interval": 30
        }
    
    def validate_agent_config(self, agent_name: str) -> Dict[str, Any]:
        """
        Valida configuração de um agente específico
        
        Args:
            agent_name: Nome do agente a validar
            
        Returns:
            Dict com resultado da validação
        """
        validation_result = {
            "valid": True,
            "warnings": [],
            "errors": [],
            "agent_name": agent_name
        }
        
        # Verificar se agente existe
        if agent_name not in self.agent_specific_configs:
            validation_result["errors"].append(f"Agente '{agent_name}' não configurado")
            validation_result["valid"] = False
            return validation_result
        
        config = self.agent_specific_configs[agent_name]
        
        # Validar configurações críticas
        if not config.get("api_key"):
            validation_result["errors"].append("API key não configurada")
            validation_result["valid"] = False
        
        if config.get("api_key") == "your_claude_api_key_here":
            validation_result["errors"].append("API key não foi atualizada")
            validation_result["valid"] = False
        
        if not config.get("model"):
            validation_result["errors"].append("Modelo Claude não especificado")
            validation_result["valid"] = False
        
        # Validar ranges de valores
        if config.get("temperature", 0) < 0 or config.get("temperature", 0) > 1:
            validation_result["warnings"].append("Temperature fora do range 0-1")
        
        if config.get("max_tokens", 0) <= 0:
            validation_result["warnings"].append("max_tokens deve ser > 0")
        
        if config.get("timeout", 0) <= 0:
            validation_result["warnings"].append("timeout deve ser > 0")
        
        # Validar ferramentas
        tools = self.get_tools_for_agent(agent_name)
        for tool in tools:
            if tool not in self.tools_config:
                validation_result["warnings"].append(f"Ferramenta '{tool}' não configurada")
        
        return validation_result
    
    def get_agent_summary(self) -> Dict[str, Any]:
        """Retorna resumo de todos os agentes configurados"""
        summary = {
            "total_agents": len(self.agent_specific_configs),
            "global_config": {
                "model": self.model,
                "timeout": self.timeout,
                "max_workers": self.max_workers
            },
            "agents": {}
        }
        
        for agent_name, config in self.agent_specific_configs.items():
            summary["agents"][agent_name] = {
                "temperature": config.get("temperature", 0.1),
                "tools_enabled": config.get("tools_enabled", False),
                "max_tokens": config.get("max_tokens", 4000),
                "tools": self.get_tools_for_agent(agent_name)
            }
        
        return summary


# ==================== INSTÂNCIAS GLOBAIS ====================
@lru_cache()
def get_agno_config() -> AgnoConfig:
    """Factory para obter configuração do Agno (cached)"""
    return AgnoConfig()


def validate_all_agent_configs() -> Dict[str, Any]:
    """Valida configurações de todos os agentes"""
    agno_config = get_agno_config()
    
    validation_results = {
        "overall_valid": True,
        "agents_validated": 0,
        "agents_with_errors": 0,
        "agents_with_warnings": 0,
        "details": {}
    }
    
    for agent_name in agno_config.agent_specific_configs.keys():
        result = agno_config.validate_agent_config(agent_name)
        validation_results["details"][agent_name] = result
        validation_results["agents_validated"] += 1
        
        if not result["valid"]:
            validation_results["overall_valid"] = False
            validation_results["agents_with_errors"] += 1
        
        if result["warnings"]:
            validation_results["agents_with_warnings"] += 1
    
    return validation_results


# ==================== FUNCÇÕES UTILITÁRIAS ====================
def create_agent_instance(agent_name: str, **kwargs):
    """
    Cria instância de um agente com configuração apropriada
    
    Args:
        agent_name: Nome do agente
        **kwargs: Configurações adicionais
        
    Returns:
        Instância configurada do agente
    """
    try:
        from agno.agent import Agent
        from agno.models.anthropic import Claude
        from agno.tools.reasoning import ReasoningTools
        from agno.tools.yfinance import YFinanceTools
        
        agno_config = get_agno_config()
        config = agno_config.get_agent_config(agent_name)
        
        # Sobrescrever com kwargs se fornecidos
        config.update(kwargs)
        
        # Criar ferramentas baseadas na configuração
        tools = []
        enabled_tools = agno_config.get_tools_for_agent(agent_name)
        
        if "reasoning_tools" in enabled_tools:
            tools.append(ReasoningTools(add_instructions=True))
        
        if "yfinance_tools" in enabled_tools and settings.yfinance_enabled:
            tools.append(YFinanceTools(
                stock_price=True,
                analyst_recommendations=True,
                company_info=True,
                company_news=True
            ))
        
        # Criar agente
        agent = Agent(
            model=Claude(id=config["model"]),
            tools=tools,
            instructions=config.get("system_prompt", ""),
            markdown=True,
            **{k: v for k, v in config.items() 
               if k not in ["model", "system_prompt", "tools_enabled"]}
        )
        
        return agent
        
    except ImportError as e:
        raise ImportError(f"Agno Framework não disponível: {e}")
    except Exception as e:
        raise RuntimeError(f"Erro ao criar agente {agent_name}: {e}")


# ==================== VALIDAÇÃO NA IMPORTAÇÃO ====================
if __name__ == "__main__":
    print("🤖 Validando configurações do Agno Framework...")
    
    try:
        agno_config = get_agno_config()
        validation = validate_all_agent_configs()
        
        print(f"Total de agentes: {validation['agents_validated']}")
        print(f"Configuração geral válida: {'✅' if validation['overall_valid'] else '❌'}")
        print(f"Agentes com erros: {validation['agents_with_errors']}")
        print(f"Agentes com warnings: {validation['agents_with_warnings']}")
        
        print("\n📋 Detalhes por agente:")
        for agent_name, details in validation["details"].items():
            status = "✅" if details["valid"] else "❌"
            print(f"  {agent_name}: {status}")
            
            if details["errors"]:
                for error in details["errors"]:
                    print(f"    ❌ {error}")
            
            if details["warnings"]:
                for warning in details["warnings"]:
                    print(f"    ⚠️ {warning}")
        
        # Mostrar resumo
        summary = agno_config.get_agent_summary()
        print(f"\n📊 Resumo:")
        print(f"  Modelo: {summary['global_config']['model']}")
        print(f"  Timeout: {summary['global_config']['timeout']}s")
        print(f"  Max Workers: {summary['global_config']['max_workers']}")
        
        if validation['overall_valid']:
            print("\n🎉 Todas as configurações do Agno estão válidas!")
        else:
            print("\n🔧 Corrija os erros antes de usar os agentes.")
            
    except Exception as e:
        print(f"❌ Erro na validação: {e}")
