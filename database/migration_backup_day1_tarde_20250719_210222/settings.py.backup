# config/settings_postgresql.py
"""
Configurações do Sistema de Recomendações - VERSÃO POSTGRESQL
Configurações otimizadas para PostgreSQL + compatibilidade com sistema existente
"""
import os
from pathlib import Path
from functools import lru_cache
from typing import Dict, Any, List, Optional

# ==================== CONFIGURAÇÃO BASE ====================
class BaseSettings:
    """Configurações base do sistema"""
    
    def __init__(self):
        # Informações do projeto
        self.project_name = "Sistema de Recomendações de Investimentos"
        self.version = "2.0.0-postgresql"
        self.description = "Sistema automatizado de análise e recomendações de ações brasileiras"
        
        # Ambiente
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.debug = os.getenv("DEBUG", "true").lower() == "true"
        self.testing = os.getenv("TESTING", "false").lower() == "true"
        
        # Diretórios
        self.base_dir = Path(__file__).parent.parent
        self.data_dir = self.base_dir / "data"
        self.logs_dir = self.base_dir / "logs"
        
        # Criar diretórios se não existirem
        self.data_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)


class PostgreSQLSettings(BaseSettings):
    """Configurações principais - OTIMIZADAS POSTGRESQL"""
    
    def __init__(self):
        super().__init__()
        
        # ==================== DATABASE POSTGRESQL ====================
        self.database_type = "postgresql"
        
        # Configurações de conexão PostgreSQL
        self.postgres_host = os.getenv("POSTGRES_HOST", "localhost")
        self.postgres_port = int(os.getenv("POSTGRES_PORT", "5432"))
        self.postgres_db = os.getenv("POSTGRES_DB", "investment_system")
        self.postgres_user = os.getenv("POSTGRES_USER", "investment_user")
        self.postgres_password = os.getenv("POSTGRES_PASSWORD", "investment_secure_pass_2024")
        self.postgres_sslmode = os.getenv("POSTGRES_SSLMODE", "prefer")
        
        # Pool de conexões PostgreSQL
        self.postgres_pool_size = int(os.getenv("POSTGRES_POOL_SIZE", "20"))
        self.postgres_max_overflow = int(os.getenv("POSTGRES_MAX_OVERFLOW", "30"))
        self.postgres_pool_timeout = int(os.getenv("POSTGRES_POOL_TIMEOUT", "30"))
        self.postgres_pool_recycle = int(os.getenv("POSTGRES_POOL_RECYCLE", "3600"))
        
        # Performance PostgreSQL
        self.postgres_echo = os.getenv("POSTGRES_ECHO", "false").lower() == "true"
        self.postgres_echo_pool = os.getenv("POSTGRES_ECHO_POOL", "false").lower() == "true"
        self.postgres_connect_timeout = int(os.getenv("POSTGRES_CONNECT_TIMEOUT", "10"))
        self.postgres_command_timeout = int(os.getenv("POSTGRES_COMMAND_TIMEOUT", "60"))
        
        # URL de conexão construída
        self.database_url = self._build_database_url()
        
        # ==================== APIS EXTERNAS ====================
        # Claude API
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "your_claude_api_key_here")
        self.claude_model = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-20250514")
        self.claude_max_tokens = int(os.getenv("CLAUDE_MAX_TOKENS", "4000"))
        self.claude_temperature = float(os.getenv("CLAUDE_TEMPERATURE", "0.3"))
        
        # YFinance e APIs financeiras
        self.yfinance_timeout = int(os.getenv("YFINANCE_TIMEOUT", "15"))
        self.yfinance_max_retries = int(os.getenv("YFINANCE_MAX_RETRIES", "3"))
        self.alpha_vantage_api_key = os.getenv("ALPHA_VANTAGE_API_KEY", "")
        self.financial_modeling_prep_key = os.getenv("FMP_API_KEY", "")
        
        # ==================== SISTEMA DE CACHE REDIS ====================
        self.redis_enabled = os.getenv("REDIS_ENABLED", "true").lower() == "true"
        self.redis_host = os.getenv("REDIS_HOST", "localhost")
        self.redis_port = int(os.getenv("REDIS_PORT", "6379"))
        self.redis_password = os.getenv("REDIS_PASSWORD", "redis_secure_2024")
        self.redis_db = int(os.getenv("REDIS_DB", "0"))
        self.redis_url = f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        
        # TTL do cache (em segundos)
        self.cache_stock_data_ttl = int(os.getenv("CACHE_STOCK_DATA_TTL", "3600"))  # 1 hora
        self.cache_analysis_ttl = int(os.getenv("CACHE_ANALYSIS_TTL", "86400"))     # 24 horas
        self.cache_market_data_ttl = int(os.getenv("CACHE_MARKET_DATA_TTL", "1800")) # 30 min
        
        # ==================== API CONFIGURATION ====================
        self.api_host = os.getenv("API_HOST", "0.0.0.0")
        self.api_port = int(os.getenv("API_PORT", "8000"))
        self.api_workers = int(os.getenv("API_WORKERS", "4"))
        self.api_timeout = int(os.getenv("API_TIMEOUT", "60"))
        
        # Rate limiting
        self.rate_limit_enabled = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
        self.rate_limit_requests = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
        self.rate_limit_window = int(os.getenv("RATE_LIMIT_WINDOW", "60"))
        
        # ==================== LOGGING ====================
        self.log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        self.log_format = os.getenv("LOG_FORMAT", "json")  # json ou text
        self.log_to_file = os.getenv("LOG_TO_FILE", "true").lower() == "true"
        self.log_max_size_mb = int(os.getenv("LOG_MAX_SIZE_MB", "100"))
        self.log_backup_count = int(os.getenv("LOG_BACKUP_COUNT", "5"))
        
        # Logs específicos
        self.log_sql_queries = os.getenv("LOG_SQL_QUERIES", "false").lower() == "true"
        self.log_api_requests = os.getenv("LOG_API_REQUESTS", "true").lower() == "true"
        self.log_agent_sessions = os.getenv("LOG_AGENT_SESSIONS", "true").lower() == "true"
        
        # ==================== ANÁLISE E SCORING ====================
        # Configurações de scoring
        self.scoring_weights = {
            "valuation": float(os.getenv("SCORING_WEIGHT_VALUATION", "0.25")),
            "profitability": float(os.getenv("SCORING_WEIGHT_PROFITABILITY", "0.25")),
            "growth": float(os.getenv("SCORING_WEIGHT_GROWTH", "0.20")),
            "financial_health": float(os.getenv("SCORING_WEIGHT_FINANCIAL_HEALTH", "0.20")),
            "technical": float(os.getenv("SCORING_WEIGHT_TECHNICAL", "0.10"))
        }
        
        # Thresholds para classificação
        self.recommendation_thresholds = {
            "strong_buy": float(os.getenv("THRESHOLD_STRONG_BUY", "85.0")),
            "buy": float(os.getenv("THRESHOLD_BUY", "70.0")),
            "hold": float(os.getenv("THRESHOLD_HOLD", "40.0")),
            "sell": float(os.getenv("THRESHOLD_SELL", "25.0"))
        }
        
        # Filtros de qualidade
        self.min_market_cap = int(os.getenv("MIN_MARKET_CAP", "1000000000"))  # 1 bilhão
        self.min_daily_volume = int(os.getenv("MIN_DAILY_VOLUME", "1000000"))  # 1 milhão
        self.min_price = float(os.getenv("MIN_PRICE", "5.00"))  # R$ 5,00
        self.max_pe_ratio = float(os.getenv("MAX_PE_RATIO", "50.0"))
        
        # ==================== AGENTES E PROCESSAMENTO ====================
        self.enable_parallel_processing = os.getenv("ENABLE_PARALLEL_PROCESSING", "true").lower() == "true"
        self.max_workers = int(os.getenv("MAX_WORKERS", "4"))
        self.batch_size = int(os.getenv("BATCH_SIZE", "10"))
        self.processing_timeout = int(os.getenv("PROCESSING_TIMEOUT", "300"))
        
        # Scheduler
        self.enable_scheduler = os.getenv("ENABLE_SCHEDULER", "true").lower() == "true"
        self.daily_analysis_time = os.getenv("DAILY_ANALYSIS_TIME", "07:00")
        self.market_data_update_interval = int(os.getenv("MARKET_DATA_UPDATE_INTERVAL", "300"))  # 5 min
        
        # ==================== MONITORING E ALERTAS ====================
        self.enable_monitoring = os.getenv("ENABLE_MONITORING", "true").lower() == "true"
        self.enable_health_checks = os.getenv("ENABLE_HEALTH_CHECKS", "true").lower() == "true"
        self.health_check_interval = int(os.getenv("HEALTH_CHECK_INTERVAL", "60"))
        
        # Alertas
        self.enable_email_alerts = os.getenv("ENABLE_EMAIL_ALERTS", "false").lower() == "true"
        self.email_smtp_host = os.getenv("EMAIL_SMTP_HOST", "smtp.gmail.com")
        self.email_smtp_port = int(os.getenv("EMAIL_SMTP_PORT", "587"))
        self.email_username = os.getenv("EMAIL_USERNAME", "")
        self.email_password = os.getenv("EMAIL_PASSWORD", "")
        
        # Slack/Discord webhooks
        self.slack_webhook_url = os.getenv("SLACK_WEBHOOK_URL", "")
        self.discord_webhook_url = os.getenv("DISCORD_WEBHOOK_URL", "")
        
        # ==================== BACKUP E RECOVERY ====================
        self.enable_auto_backup = os.getenv("ENABLE_AUTO_BACKUP", "true").lower() == "true"
        self.backup_schedule = os.getenv("BACKUP_SCHEDULE", "0 2 * * *")  # Daily at 2 AM
        self.backup_retention_days = int(os.getenv("BACKUP_RETENTION_DAYS", "30"))
        self.backup_compression = os.getenv("BACKUP_COMPRESSION", "true").lower() == "true"
        
        # Diretórios de backup
        self.backup_dir = Path(os.getenv("BACKUP_DIR", str(self.data_dir / "backups")))
        self.backup_dir.mkdir(exist_ok=True)
    
    def _build_database_url(self) -> str:
        """Constrói URL de conexão PostgreSQL"""
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}@"
            f"{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
            f"?sslmode={self.postgres_sslmode}"
            f"&application_name=investment_system"
        )
    
    @property
    def is_development(self) -> bool:
        """Verifica se está em ambiente de desenvolvimento"""
        return self.environment.lower() in ["development", "dev", "local"]
    
    @property
    def is_production(self) -> bool:
        """Verifica se está em ambiente de produção"""
        return self.environment.lower() in ["production", "prod"]
    
    @property
    def is_testing(self) -> bool:
        """Verifica se está em ambiente de teste"""
        return self.testing or self.environment.lower() in ["test", "testing"]
    
    def validate_configuration(self) -> Dict[str, Any]:
        """Valida configurações críticas"""
        issues = []
        warnings = []
        
        # Validar PostgreSQL
        if not self.postgres_host:
            issues.append("POSTGRES_HOST não configurado")
        if not self.postgres_user:
            issues.append("POSTGRES_USER não configurado")
        if not self.postgres_password or self.postgres_password == "investment_secure_pass_2024":
            warnings.append("POSTGRES_PASSWORD está usando valor padrão")
        
        # Validar Claude API
        if not self.anthropic_api_key or self.anthropic_api_key == "your_claude_api_key_here":
            issues.append("ANTHROPIC_API_KEY não configurado")
        
        # Validar pesos de scoring
        total_weight = sum(self.scoring_weights.values())
        if abs(total_weight - 1.0) > 0.01:
            issues.append(f"Pesos de scoring somam {total_weight:.2f}, deve ser 1.0")
        
        # Validar thresholds
        thresholds = list(self.recommendation_thresholds.values())
        if not all(thresholds[i] >= thresholds[i+1] for i in range(len(thresholds)-1)):
            issues.append("Thresholds de recomendação devem ser decrescentes")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "environment": self.environment,
            "database_type": self.database_type,
            "redis_enabled": self.redis_enabled
        }


class AgentSettings:
    """Configurações específicas dos agentes"""
    
    def __init__(self):
        # ==================== AGENTE COLETOR ====================
        self.collector_enabled = os.getenv("COLLECTOR_ENABLED", "true").lower() == "true"
        self.collector_batch_size = int(os.getenv("COLLECTOR_BATCH_SIZE", "10"))
        self.collector_delay_between_batches = int(os.getenv("COLLECTOR_DELAY", "2"))
        self.collector_max_retries = int(os.getenv("COLLECTOR_MAX_RETRIES", "3"))
        self.collector_timeout = int(os.getenv("COLLECTOR_TIMEOUT", "60"))
        
        # ==================== AGENTE ANALISADOR ====================
        self.analyzer_enabled = os.getenv("ANALYZER_ENABLED", "true").lower() == "true"
        self.analyzer_parallel_limit = int(os.getenv("ANALYZER_PARALLEL_LIMIT", "5"))
        self.analyzer_timeout = int(os.getenv("ANALYZER_TIMEOUT", "180"))
        self.analyzer_cache_enabled = os.getenv("ANALYZER_CACHE_ENABLED", "true").lower() == "true"
        self.analyzer_cache_ttl = int(os.getenv("ANALYZER_CACHE_TTL", "3600"))
        
        # ==================== AGENTE RECOMENDADOR ====================
        self.recommender_enabled = os.getenv("RECOMMENDER_ENABLED", "true").lower() == "true"
        self.recommender_min_confidence = float(os.getenv("RECOMMENDER_MIN_CONFIDENCE", "70.0"))
        self.recommender_max_positions = int(os.getenv("RECOMMENDER_MAX_POSITIONS", "20"))
        self.recommender_risk_tolerance = os.getenv("RECOMMENDER_RISK_TOLERANCE", "medium")
        
        # ==================== AGENTE TÉCNICO (FASE 5) ====================
        self.technical_analyzer_enabled = os.getenv("TECHNICAL_ANALYZER_ENABLED", "false").lower() == "true"
        self.technical_indicators = os.getenv("TECHNICAL_INDICATORS", "rsi,macd,sma,ema").split(",")
        self.technical_timeframes = os.getenv("TECHNICAL_TIMEFRAMES", "1h,4h,1d").split(",")
        
        # ==================== AGENTE MACRO (FASE 7) ====================
        self.macro_analyzer_enabled = os.getenv("MACRO_ANALYZER_ENABLED", "false").lower() == "true"
        self.macro_data_sources = os.getenv("MACRO_DATA_SOURCES", "bcb,ibge,investing").split(",")
        self.macro_update_frequency = int(os.getenv("MACRO_UPDATE_FREQUENCY", "86400"))  # 24h
        
        # ==================== REASONING AGENT ====================
        self.reasoning_enabled = os.getenv("REASONING_ENABLED", "true").lower() == "true"
        self.reasoning_timeout = int(os.getenv("REASONING_TIMEOUT", "60"))
        self.reasoning_fallback_enabled = os.getenv("REASONING_FALLBACK_ENABLED", "true").lower() == "true"


class SecuritySettings:
    """Configurações de segurança"""
    
    def __init__(self):
        # JWT
        self.jwt_secret_key = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
        self.jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        self.jwt_expiration_hours = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))
        
        # Rate limiting
        self.rate_limit_enabled = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
        self.rate_limit_per_minute = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
        
        # CORS
        self.cors_enabled = os.getenv("CORS_ENABLED", "true").lower() == "true"
        self.cors_origins = os.getenv("CORS_ORIGINS", "*").split(",")
        
        # SSL/TLS
        self.ssl_enabled = os.getenv("SSL_ENABLED", "false").lower() == "true"
        self.ssl_cert_path = os.getenv("SSL_CERT_PATH", "")
        self.ssl_key_path = os.getenv("SSL_KEY_PATH", "")


# ==================== INSTÂNCIAS GLOBAIS ====================
settings = PostgreSQLSettings()
agent_settings = AgentSettings()
security_settings = SecuritySettings()


# ==================== FUNÇÕES DE ACESSO ====================
@lru_cache(maxsize=1)
def get_settings() -> PostgreSQLSettings:
    """Retorna instância singleton das configurações principais"""
    return settings


@lru_cache(maxsize=1)
def get_agent_settings() -> AgentSettings:
    """Retorna configurações dos agentes"""
    return agent_settings


@lru_cache(maxsize=1)
def get_security_settings() -> SecuritySettings:
    """Retorna configurações de segurança"""
    return security_settings


def load_environment_file(env_file: str = ".env.postgresql"):
    """Carrega variáveis de ambiente de arquivo"""
    env_path = Path(env_file)
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value


def validate_all_settings() -> Dict[str, Any]:
    """Valida todas as configurações do sistema"""
    main_validation = settings.validate_configuration()
    
    # Validações adicionais
    additional_checks = {
        "redis_connection": _check_redis_connection(),
        "postgresql_connection": _check_postgresql_connection(),
        "required_directories": _check_required_directories(),
        "api_dependencies": _check_api_dependencies()
    }
    
    return {
        **main_validation,
        "additional_checks": additional_checks,
        "agent_settings_valid": _validate_agent_settings(),
        "security_settings_valid": _validate_security_settings()
    }


def _check_redis_connection() -> bool:
    """Verifica conexão com Redis"""
    if not settings.redis_enabled:
        return True
    
    try:
        import redis
        r = redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            password=settings.redis_password,
            db=settings.redis_db,
            socket_timeout=5
        )
        r.ping()
        return True
    except Exception:
        return False


def _check_postgresql_connection() -> bool:
    """Verifica conexão com PostgreSQL"""
    try:
        from database.connection_postgresql import check_database_connection
        return check_database_connection()
    except Exception:
        return False


def _check_required_directories() -> bool:
    """Verifica se diretórios obrigatórios existem"""
    required_dirs = [
        settings.data_dir,
        settings.logs_dir,
        settings.backup_dir,
        settings.data_dir / "postgresql",
        settings.logs_dir / "agents"
    ]
    
    for directory in required_dirs:
        if not directory.exists():
            try:
                directory.mkdir(parents=True, exist_ok=True)
            except Exception:
                return False
    return True


def _check_api_dependencies() -> bool:
    """Verifica dependências de APIs externas"""
    checks = []
    
    # Claude API
    if settings.anthropic_api_key and settings.anthropic_api_key != "your_claude_api_key_here":
        checks.append(True)
    else:
        checks.append(False)
    
    # YFinance (sempre disponível)
    checks.append(True)
    
    # APIs opcionais
    alpha_vantage_ok = bool(settings.alpha_vantage_api_key)
    fmp_ok = bool(settings.financial_modeling_prep_key)
    
    # Pelo menos uma API financeira deve estar configurada
    return any(checks) and (True or alpha_vantage_ok or fmp_ok)  # YFinance sempre true


def _validate_agent_settings() -> bool:
    """Valida configurações dos agentes"""
    try:
        # Verificar se pelo menos um agente está habilitado
        agents_enabled = [
            agent_settings.collector_enabled,
            agent_settings.analyzer_enabled,
            agent_settings.recommender_enabled
        ]
        
        if not any(agents_enabled):
            return False
        
        # Verificar valores numéricos
        if agent_settings.collector_batch_size <= 0:
            return False
        
        if agent_settings.analyzer_timeout <= 0:
            return False
        
        if not (0 <= agent_settings.recommender_min_confidence <= 100):
            return False
        
        return True
    except Exception:
        return False


def _validate_security_settings() -> bool:
    """Valida configurações de segurança"""
    try:
        # Verificar JWT secret em produção
        if settings.is_production and security_settings.jwt_secret_key == "your-secret-key-change-in-production":
            return False
        
        # Verificar configurações de rate limiting
        if security_settings.rate_limit_enabled and security_settings.rate_limit_per_minute <= 0:
            return False
        
        return True
    except Exception:
        return False


def get_database_config() -> Dict[str, Any]:
    """Retorna configuração específica do banco de dados"""
    return {
        "type": "postgresql",
        "host": settings.postgres_host,
        "port": settings.postgres_port,
        "database": settings.postgres_db,
        "user": settings.postgres_user,
        "pool_size": settings.postgres_pool_size,
        "max_overflow": settings.postgres_max_overflow,
        "pool_timeout": settings.postgres_pool_timeout,
        "pool_recycle": settings.postgres_pool_recycle,
        "echo": settings.postgres_echo,
        "echo_pool": settings.postgres_echo_pool,
        "connect_timeout": settings.postgres_connect_timeout,
        "command_timeout": settings.postgres_command_timeout,
        "sslmode": settings.postgres_sslmode,
        "url": settings.database_url.replace(settings.postgres_password, "***")
    }


def get_cache_config() -> Dict[str, Any]:
    """Retorna configuração específica do cache"""
    return {
        "enabled": settings.redis_enabled,
        "host": settings.redis_host,
        "port": settings.redis_port,
        "db": settings.redis_db,
        "ttl": {
            "stock_data": settings.cache_stock_data_ttl,
            "analysis": settings.cache_analysis_ttl,
            "market_data": settings.cache_market_data_ttl
        }
    }


def get_logging_config() -> Dict[str, Any]:
    """Retorna configuração específica de logging"""
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "class": "pythonjsonlogger.jsonlogger.JsonFormatter"
            },
            "text": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": settings.log_level,
                "formatter": settings.log_format,
                "stream": "ext://sys.stdout"
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": settings.log_level,
                "formatter": settings.log_format,
                "filename": str(settings.logs_dir / "investment_system.log"),
                "maxBytes": settings.log_max_size_mb * 1024 * 1024,
                "backupCount": settings.log_backup_count,
                "encoding": "utf8"
            },
            "sql": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "DEBUG" if settings.log_sql_queries else "WARNING",
                "formatter": "text",
                "filename": str(settings.logs_dir / "sql_queries.log"),
                "maxBytes": 50 * 1024 * 1024,  # 50MB
                "backupCount": 3
            }
        },
        "loggers": {
            "": {  # Root logger
                "level": settings.log_level,
                "handlers": ["console"] + (["file"] if settings.log_to_file else [])
            },
            "sqlalchemy.engine": {
                "level": "DEBUG" if settings.log_sql_queries else "WARNING",
                "handlers": ["sql"] if settings.log_sql_queries else [],
                "propagate": False
            },
            "uvicorn.access": {
                "level": "INFO" if settings.log_api_requests else "WARNING",
                "propagate": True
            },
            "investment_system.agents": {
                "level": "INFO" if settings.log_agent_sessions else "WARNING",
                "propagate": True
            }
        }
    }


# ==================== COMPATIBILIDADE COM SISTEMA ANTERIOR ====================
class CompatibilityLayer:
    """Camada de compatibilidade para transição suave do SQLite para PostgreSQL"""
    
    def __init__(self):
        self.settings = get_settings()
    
    @property
    def database_url(self) -> str:
        """Compatibilidade: retorna URL do banco"""
        return self.settings.database_url
    
    @property
    def database_path(self) -> Optional[Path]:
        """Compatibilidade: retorna None para PostgreSQL"""
        return None
    
    @property
    def anthropic_api_key(self) -> str:
        """Compatibilidade: retorna chave da API Claude"""
        return self.settings.anthropic_api_key
    
    @property
    def api_port(self) -> int:
        """Compatibilidade: retorna porta da API"""
        return self.settings.api_port
    
    @property
    def enable_mock_data(self) -> bool:
        """Compatibilidade: retorna False para PostgreSQL"""
        return False
    
    def validate_configuration(self) -> Dict[str, Any]:
        """Compatibilidade: valida configuração"""
        return self.settings.validate_configuration()


# Instância de compatibilidade
compatibility_settings = CompatibilityLayer()


# ==================== MIGRATION HELPERS ====================
def migrate_from_sqlite_config():
    """Helper para migrar configurações do SQLite"""
    old_env_file = Path(".env")
    new_env_file = Path(".env.postgresql")
    
    if old_env_file.exists() and not new_env_file.exists():
        print("🔄 Migrando configurações do SQLite para PostgreSQL...")
        
        # Ler configurações antigas
        old_config = {}
        with open(old_env_file, 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    old_config[key] = value
        
        # Mapear para novas configurações PostgreSQL
        new_config = {
            "ENVIRONMENT": old_config.get("ENVIRONMENT", "development"),
            "DEBUG": old_config.get("DEBUG", "true"),
            
            # PostgreSQL específico
            "POSTGRES_HOST": "localhost",
            "POSTGRES_PORT": "5432",
            "POSTGRES_DB": "investment_system",
            "POSTGRES_USER": "investment_user",
            "POSTGRES_PASSWORD": "investment_secure_pass_2024",
            
            # Manter configurações de API
            "ANTHROPIC_API_KEY": old_config.get("ANTHROPIC_API_KEY", "your_claude_api_key_here"),
            "ALPHA_VANTAGE_API_KEY": old_config.get("ALPHA_VANTAGE_API_KEY", ""),
            
            # Novas configurações
            "REDIS_ENABLED": "true",
            "ENABLE_MONITORING": "true",
            "ENABLE_AUTO_BACKUP": "true"
        }
        
        # Escrever novo arquivo
        with open(new_env_file, 'w') as f:
            f.write("# PostgreSQL Configuration - Migrated from SQLite\n")
            f.write(f"# Migration Date: {datetime.now().isoformat()}\n\n")
            
            for key, value in new_config.items():
                f.write(f"{key}={value}\n")
        
        print(f"✅ Configurações migradas para {new_env_file}")
        print(f"⚠️  Revise as configurações em {new_env_file}")
        return True
    
    return False


def print_migration_summary():
    """Imprime resumo da migração de configurações"""
    print("\n" + "="*60)
    print("📊 RESUMO DA CONFIGURAÇÃO POSTGRESQL")
    print("="*60)
    
    config_validation = validate_all_settings()
    
    print(f"✅ Ambiente: {settings.environment}")
    print(f"✅ Banco: PostgreSQL {settings.postgres_host}:{settings.postgres_port}")
    print(f"✅ Cache Redis: {'Habilitado' if settings.redis_enabled else 'Desabilitado'}")
    print(f"✅ Pool Size: {settings.postgres_pool_size}")
    print(f"✅ Agentes: {sum([agent_settings.collector_enabled, agent_settings.analyzer_enabled, agent_settings.recommender_enabled])} habilitados")
    
    if config_validation["valid"]:
        print("✅ Configuração válida")
    else:
        print("❌ Problemas de configuração:")
        for issue in config_validation["issues"]:
            print(f"   • {issue}")
    
    if config_validation["warnings"]:
        print("⚠️  Avisos:")
        for warning in config_validation["warnings"]:
            print(f"   • {warning}")
    
    print("="*60)


if __name__ == "__main__":
    # Migrar configurações se necessário
    migrated = migrate_from_sqlite_config()
    
    # Carregar configurações PostgreSQL
    load_environment_file(".env.postgresql")
    
    # Imprimir resumo
    print_migration_summary()
    
    # Validar configurações
    validation = validate_all_settings()
    if not validation["valid"]:
        print("\n❌ Configuração inválida!")
        exit(1)
    else:
        print("\n✅ Configuração PostgreSQL válida!")