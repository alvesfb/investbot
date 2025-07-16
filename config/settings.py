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
        self.cache_dir = self.project_root / "cache"
        
        # Criar diretórios se não existirem
        for directory in [self.data_dir, self.logs_dir, self.reports_dir, self.cache_dir]:
            directory.mkdir(exist_ok=True)
        
        # ==================== DATABASE ====================
        self.database_url = os.getenv(
            "DATABASE_URL", 
            f"sqlite:///{self.data_dir}/investment_system.db"
        )
        
        # ==================== APIs FINANCEIRAS (MULTI-API) ====================
        
        # YFinance (primário)
        self.yfinance_enabled = os.getenv("YFINANCE_ENABLED", "true").lower() == "true"
        self.yfinance_timeout = int(os.getenv("YFINANCE_TIMEOUT", "15"))
        self.yfinance_max_retries = int(os.getenv("YFINANCE_MAX_RETRIES", "3"))
        
        # Alpha Vantage (backup)
        self.alpha_vantage_api_key = os.getenv("ALPHA_VANTAGE_API_KEY", "")
        self.alpha_vantage_timeout = int(os.getenv("ALPHA_VANTAGE_TIMEOUT", "10"))
        self.alpha_vantage_daily_limit = int(os.getenv("ALPHA_VANTAGE_DAILY_LIMIT", "500"))
        
        # Financial Modeling Prep (backup)
        self.fmp_api_key = os.getenv("FMP_API_KEY", "")
        self.fmp_timeout = int(os.getenv("FMP_TIMEOUT", "10"))
        self.fmp_daily_limit = int(os.getenv("FMP_DAILY_LIMIT", "250"))
        
        # Twelve Data (backup)
        self.twelve_data_api_key = os.getenv("TWELVE_DATA_API_KEY", "")
        self.twelve_data_timeout = int(os.getenv("TWELVE_DATA_TIMEOUT", "10"))
        
        # ==================== CACHE SYSTEM ====================
        self.cache_enabled = os.getenv("CACHE_ENABLED", "true").lower() == "true"
        self.financial_cache_dir = os.getenv("FINANCIAL_CACHE_DIR", str(self.cache_dir / "financial"))
        
        # TTL por tipo de dado (em segundos)
        self.cache_ttl_market_data = int(os.getenv("CACHE_TTL_MARKET_DATA", "300"))      # 5 min
        self.cache_ttl_fundamentals = int(os.getenv("CACHE_TTL_FUNDAMENTALS", "3600"))  # 1 hora
        self.cache_ttl_company_info = int(os.getenv("CACHE_TTL_COMPANY_INFO", "86400")) # 24 horas
        self.cache_ttl_static_data = int(os.getenv("CACHE_TTL_STATIC_DATA", "604800"))  # 7 dias
        
        # ==================== MULTI-API STRATEGY ====================
        self.api_strategy_enabled = os.getenv("API_STRATEGY_ENABLED", "true").lower() == "true"
        self.api_fallback_enabled = os.getenv("API_FALLBACK_ENABLED", "true").lower() == "true"
        self.static_data_fallback = os.getenv("STATIC_DATA_FALLBACK", "true").lower() == "true"
        self.intelligent_fallback = os.getenv("INTELLIGENT_FALLBACK", "true").lower() == "true"
        
        # Prioridade dos providers (ordem de tentativa)
        self.api_provider_priority = [
            "yfinance_primary",
            "yfinance_alternative", 
            "alpha_vantage",
            "fmp",
            "twelve_data",
            "static_data",
            "intelligent_fallback"
        ]
        
        # ==================== AGNO FRAMEWORK ====================
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "your_claude_api_key_here")
        self.claude_model = os.getenv("CLAUDE_MODEL", "claude-3-sonnet-20240229")
        self.agno_max_workers = int(os.getenv("AGNO_MAX_WORKERS", "5"))
        self.agno_log_level = os.getenv("AGNO_LOG_LEVEL", "INFO")
        self.agno_timeout = int(os.getenv("AGNO_TIMEOUT", "300"))
        
        # ==================== LOGGING ====================
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        self.log_file = self.logs_dir / "investment_system.log"
        self.enable_api_logging = os.getenv("ENABLE_API_LOGGING", "true").lower() == "true"
        
        # ==================== RATE LIMITING ====================
        self.rate_limit_enabled = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
        self.rate_limit_requests_per_minute = int(os.getenv("RATE_LIMIT_RPM", "60"))
        self.rate_limit_burst_size = int(os.getenv("RATE_LIMIT_BURST", "10"))
        
        # ==================== MONITORING ====================
        self.monitoring_enabled = os.getenv("MONITORING_ENABLED", "true").lower() == "true"
        self.stats_collection_enabled = os.getenv("STATS_COLLECTION", "true").lower() == "true"
        self.performance_tracking = os.getenv("PERFORMANCE_TRACKING", "true").lower() == "true"
        
        # ==================== BACKUP E RECOVERY ====================
        self.backup_enabled = os.getenv("BACKUP_ENABLED", "true").lower() == "true"
        self.backup_interval_hours = int(os.getenv("BACKUP_INTERVAL_HOURS", "24"))
        self.max_backup_files = int(os.getenv("MAX_BACKUP_FILES", "7"))
        
        # Criar diretório de cache financeiro
        Path(self.financial_cache_dir).mkdir(parents=True, exist_ok=True)
    
    @property
    def database_path(self) -> Optional[Path]:
        """Caminho do banco SQLite"""
        if self.database_url.startswith("sqlite"):
            db_path = self.database_url.replace("sqlite:///", "")
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
    
    def get_api_config(self, provider: str) -> Dict[str, Any]:
        """Retorna configuração específica de um provider"""
        
        configs = {
            "yfinance": {
                "enabled": self.yfinance_enabled,
                "timeout": self.yfinance_timeout,
                "max_retries": self.yfinance_max_retries,
                "priority": 1
            },
            "alpha_vantage": {
                "enabled": bool(self.alpha_vantage_api_key),
                "api_key": self.alpha_vantage_api_key,
                "timeout": self.alpha_vantage_timeout,
                "daily_limit": self.alpha_vantage_daily_limit,
                "priority": 2
            },
            "fmp": {
                "enabled": bool(self.fmp_api_key),
                "api_key": self.fmp_api_key,
                "timeout": self.fmp_timeout,
                "daily_limit": self.fmp_daily_limit,
                "priority": 3
            },
            "twelve_data": {
                "enabled": bool(self.twelve_data_api_key),
                "api_key": self.twelve_data_api_key,
                "timeout": self.twelve_data_timeout,
                "priority": 4
            }
        }
        
        return configs.get(provider, {})
    
    def get_cache_config(self) -> Dict[str, Any]:
        """Retorna configuração completa do cache"""
        return {
            "enabled": self.cache_enabled,
            "cache_dir": self.financial_cache_dir,
            "ttl": {
                "market_data": self.cache_ttl_market_data,
                "fundamentals": self.cache_ttl_fundamentals,
                "company_info": self.cache_ttl_company_info,
                "static_data": self.cache_ttl_static_data
            }
        }
    
    def validate_configuration(self) -> Dict[str, Any]:
        """Valida configurações críticas"""
        issues = []
        warnings = []
        info = []
        
        # ==================== VALIDAÇÕES CRÍTICAS ====================
        if self.anthropic_api_key == "your_claude_api_key_here":
            issues.append("ANTHROPIC_API_KEY não configurada")
        
        if not self.database_url:
            issues.append("DATABASE_URL não configurada")
        
        # ==================== WARNINGS ====================
        if not any([self.yfinance_enabled, self.alpha_vantage_api_key, self.fmp_api_key]):
            warnings.append("Nenhuma fonte de dados financeiros configurada")
        
        if not self.alpha_vantage_api_key and not self.fmp_api_key:
            warnings.append("Nenhuma API de backup configurada - sistema pode falhar em caso de problemas com YFinance")
        
        if self.debug and self.is_production:
            warnings.append("Debug ativado em produção")
        
        if not self.cache_enabled:
            warnings.append("Cache desabilitado - performance pode ser afetada")
        
        # ==================== INFORMAÇÕES ====================
        enabled_apis = []
        if self.yfinance_enabled:
            enabled_apis.append("YFinance")
        if self.alpha_vantage_api_key:
            enabled_apis.append("Alpha Vantage")
        if self.fmp_api_key:
            enabled_apis.append("Financial Modeling Prep")
        if self.twelve_data_api_key:
            enabled_apis.append("Twelve Data")
        
        info.append(f"APIs habilitadas: {', '.join(enabled_apis) if enabled_apis else 'Nenhuma'}")
        info.append(f"Cache: {'Habilitado' if self.cache_enabled else 'Desabilitado'}")
        info.append(f"Fallback inteligente: {'Habilitado' if self.intelligent_fallback else 'Desabilitado'}")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "info": info,
            "environment": self.environment,
            "version": self.version,
            "api_strategy": self.api_strategy_enabled
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
        self.analysis_cache_ttl_hours = int(os.getenv("ANALYSIS_CACHE_TTL", "24"))
        self.benchmark_cache_ttl_hours = int(os.getenv("BENCHMARK_CACHE_TTL", "168"))  # 7 dias
        
        # ==================== RELATÓRIOS ====================
        self.generate_analysis_reports = True
        self.reports_directory = "data/reports"
        self.report_formats = ["json", "excel"]


class AgentSettings:
    """Configurações específicas dos agentes"""
    
    def __init__(self):
        # ==================== AGENTE COLETOR ====================
        self.collector_batch_size = int(os.getenv("COLLECTOR_BATCH_SIZE", "10"))
        self.collector_delay_between_batches = int(os.getenv("COLLECTOR_DELAY", "2"))
        self.collector_max_retries = int(os.getenv("COLLECTOR_MAX_RETRIES", "3"))
        
        # ==================== AGENTE ANALISADOR ====================
        self.analyzer_parallel_limit = int(os.getenv("ANALYZER_PARALLEL_LIMIT", "5"))
        self.analyzer_timeout = int(os.getenv("ANALYZER_TIMEOUT", "180"))
        self.analyzer_cache_enabled = True
        
        # ==================== REASONING AGENT ====================
        self.reasoning_enabled = os.getenv("REASONING_ENABLED", "true").lower() == "true"
        self.reasoning_timeout = int(os.getenv("REASONING_TIMEOUT", "60"))
        self.reasoning_fallback_enabled = True


# ==================== INSTÂNCIAS GLOBAIS ====================
settings = Settings()
phase2_settings = Phase2Settings()
agent_settings = AgentSettings()


# ==================== FUNÇÕES DE ACESSO ====================
@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Retorna instância singleton das configurações principais"""
    return settings


@lru_cache(maxsize=1)
def get_phase2_settings() -> Phase2Settings:
    """Retorna configurações da Fase 2"""
    return phase2_settings


@lru_cache(maxsize=1)
def get_agent_settings() -> AgentSettings:
    """Retorna configurações dos agentes"""
    return agent_settings


def validate_all_settings() -> Dict[str, Any]:
    """Valida todas as configurações do sistema"""
    
    main_validation = settings.validate_configuration()
    
    # Validações adicionais para multi-API
    additional_checks = []
    
    if settings.api_strategy_enabled:
        if not any([settings.yfinance_enabled, settings.alpha_vantage_api_key]):
            additional_checks.append("Estratégia multi-API habilitada mas nenhuma API configurada")
        
        if settings.cache_enabled:
            cache_dir = Path(settings.financial_cache_dir)
            if not cache_dir.exists():
                additional_checks.append(f"Diretório de cache não existe: {cache_dir}")
    
    # Combinar resultados
    result = main_validation.copy()
    if additional_checks:
        result["warnings"].extend(additional_checks)
    
    return result


def print_configuration_summary():
    """Imprime resumo das configurações"""
    
    validation = validate_all_settings()
    
    print("⚙️ RESUMO DAS CONFIGURAÇÕES")
    print("=" * 40)
    
    print(f"Ambiente: {settings.environment}")
    print(f"Versão: {settings.version}")
    print(f"Debug: {settings.debug}")
    
    print(f"\n📡 APIs FINANCEIRAS:")
    print(f"   • YFinance: {'✅' if settings.yfinance_enabled else '❌'}")
    print(f"   • Alpha Vantage: {'✅' if settings.alpha_vantage_api_key else '❌'}")
    print(f"   • Financial Modeling Prep: {'✅' if settings.fmp_api_key else '❌'}")
    print(f"   • Twelve Data: {'✅' if settings.twelve_data_api_key else '❌'}")
    
    print(f"\n💾 CACHE:")
    print(f"   • Habilitado: {'✅' if settings.cache_enabled else '❌'}")
    print(f"   • Diretório: {settings.financial_cache_dir}")
    
    print(f"\n🤖 AGNO:")
    print(f"   • API Key: {'✅' if settings.anthropic_api_key != 'your_claude_api_key_here' else '❌'}")
    print(f"   • Modelo: {settings.claude_model}")
    
    print(f"\n🎯 VALIDAÇÃO:")
    print(f"   • Status: {'✅ Válido' if validation['valid'] else '❌ Problemas encontrados'}")
    
    if validation['issues']:
        print(f"\n❌ PROBLEMAS CRÍTICOS:")
        for issue in validation['issues']:
            print(f"   • {issue}")
    
    if validation['warnings']:
        print(f"\n⚠️ AVISOS:")
        for warning in validation['warnings']:
            print(f"   • {warning}")
    
    if validation['info']:
        print(f"\nℹ️ INFORMAÇÕES:")
        for info in validation['info']:
            print(f"   • {info}")


if __name__ == "__main__":
    print_configuration_summary()
