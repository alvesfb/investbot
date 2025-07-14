# config/settings.py
"""
Configurações Centralizadas do Sistema de Recomendações de Investimentos
Inclui configurações para todas as fases do projeto
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any, List
from functools import lru_cache


class Settings:
    """Configurações principais do sistema"""
    
    def __init__(self):
        # ==================== CONFIGURAÇÕES BÁSICAS ====================
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.debug = os.getenv("DEBUG", "true").lower() == "true"
        self.version = "1.0.0"
        
        # ==================== PATHS E DIRETÓRIOS ====================
        self.project_root = Path(__file__).parent.parent
        self.data_dir = self.project_root / "data"
        self.logs_dir = self.project_root / "logs"
        self.config_dir = self.project_root / "config"
        self.reports_dir = self.project_root / "reports"
        
        # Criar diretórios se não existirem
        for directory in [self.data_dir, self.logs_dir, self.reports_dir]:
            directory.mkdir(exist_ok=True)
        
        # ==================== DATABASE ====================
        self.database_url = os.getenv(
            "DATABASE_URL", 
            f"sqlite:///{self.data_dir}/investment_system.db"
        )
        
        # ==================== APIs EXTERNAS ====================
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "your_claude_api_key_here")
        self.alpha_vantage_api_key = os.getenv("ALPHA_VANTAGE_API_KEY", "")
        self.yfinance_enabled = os.getenv("YFINANCE_ENABLED", "true").lower() == "true"
        
        # ==================== AGNO FRAMEWORK ====================
        self.claude_model = os.getenv("CLAUDE_MODEL", "claude-3-sonnet-20240229")
        self.agno_max_workers = int(os.getenv("AGNO_MAX_WORKERS", "5"))
        self.agno_log_level = os.getenv("AGNO_LOG_LEVEL", "INFO")
        self.agno_timeout = int(os.getenv("AGNO_TIMEOUT", "300"))
        
        # ==================== LOGGING ====================
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        self.log_file = self.logs_dir / "investment_system.log"
        self.log_rotation = "1 day"
        self.log_retention = "30 days"
        self.log_max_size = "50 MB"
        
        # ==================== PERFORMANCE ====================
        self.max_concurrent_requests = int(os.getenv("MAX_CONCURRENT_REQUESTS", "10"))
        self.request_timeout = int(os.getenv("REQUEST_TIMEOUT", "30"))
        self.cache_ttl_hours = int(os.getenv("CACHE_TTL_HOURS", "6"))
        
        # ==================== SEGURANÇA ====================
        self.enable_rate_limiting = os.getenv("ENABLE_RATE_LIMITING", "true").lower() == "true"
        self.rate_limit_per_minute = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
        self.enable_auth = os.getenv("ENABLE_AUTH", "false").lower() == "true"
        
        # ==================== BUSINESS RULES ====================
        self.min_market_cap = float(os.getenv("MIN_MARKET_CAP", "1000000000"))  # 1B
        self.exclude_penny_stocks = os.getenv("EXCLUDE_PENNY_STOCKS", "true").lower() == "true"
        self.penny_stock_threshold = float(os.getenv("PENNY_STOCK_THRESHOLD", "5.0"))
        
        # ==================== NOTIFICAÇÕES ====================
        self.email_enabled = os.getenv("EMAIL_ENABLED", "false").lower() == "true"
        self.smtp_server = os.getenv("SMTP_SERVER", "")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        
        # ==================== DESENVOLVIMENTO ====================
        self.enable_mock_data = os.getenv("ENABLE_MOCK_DATA", "false").lower() == "true"
        self.mock_analysis_delay = float(os.getenv("MOCK_ANALYSIS_DELAY", "1.0"))
        self.enable_debug_endpoints = self.debug
    
    @property
    def database_path(self) -> Optional[Path]:
        """Retorna o caminho do banco SQLite se aplicável"""
        if self.database_url.startswith("sqlite"):
            db_path = self.database_url.replace("sqlite:///", "").replace("sqlite://", "")
            return Path(db_path)
        return None
    
    @property
    def is_production(self) -> bool:
        """Verifica se está em ambiente de produção"""
        return self.environment.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Verifica se está em ambiente de desenvolvimento"""
        return self.environment.lower() == "development"
    
    def validate_configuration(self) -> Dict[str, Any]:
        """Valida configurações críticas"""
        issues = []
        warnings = []
        
        # Validações críticas
        if self.anthropic_api_key == "your_claude_api_key_here":
            issues.append("ANTHROPIC_API_KEY não configurada")
        
        if not self.database_url:
            issues.append("DATABASE_URL não configurada")
        
        # Warnings
        if not self.alpha_vantage_api_key and not self.yfinance_enabled:
            warnings.append("Nenhuma fonte de dados financeiros configurada")
        
        if self.debug and self.is_production:
            warnings.append("Debug ativado em produção")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "environment": self.environment,
            "version": self.version
        }


class Phase2Settings:
    """Configurações específicas da Fase 2 - Análise Fundamentalista"""
    
    def __init__(self):
        # ==================== SISTEMA DE MÉTRICAS ====================
        self.metrics_config_file = "config/metrics_config.json"
        self.enable_sector_benchmarks = True
        self.benchmark_update_frequency = "weekly"
        self.outlier_detection_enabled = True
        
        # ==================== ANÁLISE FUNDAMENTALISTA ====================
        self.min_data_completeness = float(os.getenv("MIN_DATA_COMPLETENESS", "0.6"))
        self.confidence_threshold = float(os.getenv("CONFIDENCE_THRESHOLD", "0.7"))
        self.historical_periods = int(os.getenv("HISTORICAL_PERIODS", "5"))
        self.enable_sector_normalization = True
        
        # ==================== SCORING ====================
        self.scoring_weights = {
            "valuation": 0.20,
            "profitability": 0.25,
            "leverage": 0.15,
            "growth": 0.20,
            "efficiency": 0.10,
            "quality": 0.10
        }
        
        # ==================== PERFORMANCE ====================
        self.enable_parallel_analysis = True
        self.max_concurrent_analyses = int(os.getenv("MAX_CONCURRENT_ANALYSES", "10"))
        self.analysis_timeout_seconds = int(os.getenv("ANALYSIS_TIMEOUT", "300"))
        
        # ==================== CACHE ====================
        self.cache_analysis_results = True
        self.analysis_cache_ttl_hours = 24
        self.benchmark_cache_ttl_hours = 168  # 7 dias
        
        # ==================== RELATÓRIOS ====================
        self.generate_analysis_reports = True
        self.reports_directory = "data/reports"
        self.report_formats = ["json", "excel"]
        
        # ==================== QUALIDADE DE DADOS ====================
        self.data_quality_checks = True
        self.min_pe_ratio = -100
        self.max_pe_ratio = 200
        self.min_pb_ratio = 0
        self.max_pb_ratio = 50
        self.min_roe = -100
        self.max_roe = 200


class Phase3Settings:
    """Configurações específicas da Fase 3 - Recomendações"""
    
    def __init__(self):
        # ==================== RECOMENDAÇÕES ====================
        self.recommendation_weights = {
            "fundamental": float(os.getenv("FUNDAMENTAL_WEIGHT", "0.70")),
            "technical": float(os.getenv("TECHNICAL_WEIGHT", "0.30"))
        }
        
        # ==================== CLASSIFICAÇÕES ====================
        self.classification_thresholds = {
            "compra_forte": 85,
            "compra": 65,
            "neutro_superior": 55,
            "neutro_inferior": 45,
            "venda": 25,
            "venda_forte": 0
        }
        
        # ==================== STOP LOSS ====================
        self.stop_loss_config = {
            "min_percentage": 3.0,
            "max_percentage": 15.0,
            "default_low_risk": 5.0,
            "default_medium_risk": 7.5,
            "default_high_risk": 10.0
        }
        
        # ==================== JUSTIFICATIVAS ====================
        self.enable_justification_refinement = True
        self.max_justification_length = 500
        self.min_justification_length = 100
        
        # ==================== CONFIDENCE ====================
        self.min_confidence_level = 20
        self.max_confidence_level = 95
        self.convergence_bonus = 20  # Bonus por convergência entre análises


class AgentSettings:
    """Configurações específicas dos agentes"""
    
    def __init__(self):
        # ==================== AGENTE COLETOR ====================
        self.collector_config = {
            "batch_size": int(os.getenv("COLLECTOR_BATCH_SIZE", "20")),
            "retry_attempts": 3,
            "retry_delay": 2.0,
            "data_validation": True,
            "enable_cache": True
        }
        
        # ==================== AGENTE ANALISADOR ====================
        self.analyzer_config = {
            "enable_sector_comparison": True,
            "enable_peer_analysis": True,
            "min_peer_count": 3,
            "max_processing_time": 180,
            "enable_outlier_detection": True
        }
        
        # ==================== AGENTE RECOMENDADOR ====================
        self.recommender_config = {
            "enable_market_context": True,
            "enable_sector_rotation": True,
            "risk_assessment": True,
            "generate_reports": True,
            "max_recommendations_per_run": 50
        }


# ==================== INSTÂNCIAS GLOBAIS ====================
@lru_cache()
def get_settings() -> Settings:
    """Factory para obter configurações principais (cached)"""
    return Settings()


@lru_cache()
def get_phase2_settings() -> Phase2Settings:
    """Factory para obter configurações da Fase 2 (cached)"""
    return Phase2Settings()


@lru_cache()
def get_phase3_settings() -> Phase3Settings:
    """Factory para obter configurações da Fase 3 (cached)"""
    return Phase3Settings()


@lru_cache()
def get_agent_settings() -> AgentSettings:
    """Factory para obter configurações dos agentes (cached)"""
    return AgentSettings()


# ==================== FUNÇÕES UTILITÁRIAS ====================
def load_env_file(env_file: str = ".env"):
    """Carrega variáveis de ambiente de um arquivo"""
    env_path = Path(env_file)
    if not env_path.exists():
        return False
    
    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ.setdefault(key.strip(), value.strip())
        return True
    except Exception:
        return False


def validate_all_configurations() -> Dict[str, Any]:
    """Valida todas as configurações do sistema"""
    settings = get_settings()
    validation_result = settings.validate_configuration()
    
    # Adicionar validações específicas das fases
    phase2_settings = get_phase2_settings()
    phase3_settings = get_phase3_settings()
    agent_settings = get_agent_settings()
    
    # Verificar soma dos pesos das recomendações
    weight_sum = sum(phase3_settings.recommendation_weights.values())
    if abs(weight_sum - 1.0) > 0.01:
        validation_result["warnings"].append(f"Soma dos pesos de recomendação != 1.0: {weight_sum}")
    
    # Verificar thresholds de classificação
    thresholds = phase3_settings.classification_thresholds
    if not (thresholds["venda_forte"] < thresholds["venda"] < thresholds["neutro_inferior"] 
            < thresholds["neutro_superior"] < thresholds["compra"] < thresholds["compra_forte"]):
        validation_result["issues"].append("Thresholds de classificação fora de ordem")
    
    validation_result["components"] = {
        "main_settings": "✅",
        "phase2_settings": "✅",
        "phase3_settings": "✅",
        "agent_settings": "✅"
    }
    
    return validation_result


# ==================== CARREGAMENTO AUTOMÁTICO ====================
# Tentar carregar arquivo .env na importação
load_env_file()

# Validar configurações em desenvolvimento
if __name__ == "__main__":
    print("🔧 Validando configurações do sistema...")
    
    validation = validate_all_configurations()
    
    print(f"Ambiente: {validation['environment']}")
    print(f"Versão: {validation['version']}")
    print(f"Válido: {'✅' if validation['valid'] else '❌'}")
    
    if validation['issues']:
        print("\n❌ Problemas encontrados:")
        for issue in validation['issues']:
            print(f"  - {issue}")
    
    if validation['warnings']:
        print("\n⚠️ Avisos:")
        for warning in validation['warnings']:
            print(f"  - {warning}")
    
    print("\n📋 Componentes:")
    for component, status in validation['components'].items():
        print(f"  {component}: {status}")
    
    if validation['valid']:
        print("\n🎉 Configurações válidas!")
    else:
        print("\n🔧 Corrija os problemas antes de continuar.")