# config/production.py
"""
Configurações de Produção - Sistema de Recomendações
Configurações otimizadas para ambiente de produção PostgreSQL

Uso:
    from config.production import get_production_settings
    settings = get_production_settings()
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass

# ==================== LOAD ENVIRONMENT ====================
def load_environment():
    """Carrega variáveis de ambiente do arquivo .env apropriado"""
    try:
        from dotenv import load_dotenv
        
        # Diretório do projeto
        project_root = Path(__file__).parent.parent
        
        # Determinar qual arquivo .env carregar
        environment = os.getenv("ENVIRONMENT", "development")
        
        if environment == "production":
            env_files = [".env.production", ".env"]
        else:
            env_files = [".env.development", ".env"]
        
        # Tentar carregar arquivos na ordem de prioridade
        loaded = False
        for env_file in env_files:
            env_path = project_root / env_file
            if env_path.exists():
                load_dotenv(env_path)
                loaded = True
                print(f"✅ Configurações carregadas de: {env_file}")
                break
        
        if not loaded:
            print("⚠️  Nenhum arquivo .env encontrado - usando variáveis de ambiente do sistema")
        
    except ImportError:
        print("⚠️  python-dotenv não instalado - usando variáveis de ambiente do sistema")
    except Exception as e:
        print(f"⚠️  Erro carregando .env: {e}")

# Carregar ambiente automaticamente ao importar
load_environment()


@dataclass
class ProductionSettings:
    """Configurações de produção otimizadas"""
    
    # ==================== IDENTIFICAÇÃO ====================
    project_name: str = "Sistema de Recomendações de Investimentos"
    version: str = "2.0.0-postgresql"
    environment: str = "production"
    
    # ==================== DATABASE POSTGRESQL ====================
    # Configurações principais
    postgres_host: str = os.getenv("POSTGRES_HOST", "localhost")
    postgres_port: int = int(os.getenv("POSTGRES_PORT", "5432"))
    postgres_db: str = os.getenv("POSTGRES_DB", "investment_system_prod")
    postgres_user: str = os.getenv("POSTGRES_USER", "investment_user")
    postgres_password: str = os.getenv("POSTGRES_PASSWORD", "")
    postgres_sslmode: str = os.getenv("POSTGRES_SSLMODE", "require")  # Produção sempre SSL
    
    # Pool de conexões otimizado para produção
    postgres_pool_size: int = int(os.getenv("POSTGRES_POOL_SIZE", "50"))  # Maior para produção
    postgres_max_overflow: int = int(os.getenv("POSTGRES_MAX_OVERFLOW", "100"))  # Maior capacidade
    postgres_pool_timeout: int = int(os.getenv("POSTGRES_POOL_TIMEOUT", "30"))
    postgres_pool_recycle: int = int(os.getenv("POSTGRES_POOL_RECYCLE", "1800"))  # 30min
    
    # Performance otimizada
    postgres_echo: bool = False  # Sem logs de SQL em produção
    postgres_echo_pool: bool = False
    postgres_connect_timeout: int = int(os.getenv("POSTGRES_CONNECT_TIMEOUT", "10"))
    postgres_command_timeout: int = int(os.getenv("POSTGRES_COMMAND_TIMEOUT", "60"))
    
    # ==================== SECURITY ====================
    secret_key: str = os.getenv("SECRET_KEY", "")
    jwt_secret: str = os.getenv("JWT_SECRET", "")
    encryption_key: str = os.getenv("ENCRYPTION_KEY", "")
    
    # CORS para produção (será definido no __post_init__)
    allowed_origins: list = None
    
    # Rate limiting
    rate_limit_per_minute: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    rate_limit_burst: int = int(os.getenv("RATE_LIMIT_BURST", "120"))
    
    # ==================== LOGGING ====================
    log_level: str = os.getenv("LOG_LEVEL", "INFO")  # INFO em produção, DEBUG em dev
    log_format: str = "json"  # JSON para produção
    log_file: str = "/var/log/investment_system/app.log"
    log_max_size: str = "100MB"
    log_backup_count: int = 10
    
    # Sentry para monitoramento de erros
    sentry_dsn: str = os.getenv("SENTRY_DSN", "")
    sentry_environment: str = "production"
    sentry_sample_rate: float = 0.1  # 10% sampling em produção
    
    # ==================== REDIS CACHE ====================
    redis_enabled: bool = os.getenv("REDIS_ENABLED", "true").lower() == "true"
    redis_host: str = os.getenv("REDIS_HOST", "localhost")
    redis_port: int = int(os.getenv("REDIS_PORT", "6379"))
    redis_password: str = os.getenv("REDIS_PASSWORD", "")
    redis_db: int = int(os.getenv("REDIS_DB", "0"))
    redis_ssl: bool = os.getenv("REDIS_SSL", "false").lower() == "true"
    
    # TTL cache
    cache_ttl_short: int = 300   # 5 minutos
    cache_ttl_medium: int = 1800  # 30 minutos
    cache_ttl_long: int = 3600   # 1 hora
    
    # ==================== APIs EXTERNAS ====================
    # Claude API
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    anthropic_max_tokens: int = int(os.getenv("ANTHROPIC_MAX_TOKENS", "4000"))
    anthropic_timeout: int = int(os.getenv("ANTHROPIC_TIMEOUT", "60"))
    
    # Financial APIs
    alpha_vantage_api_key: str = os.getenv("ALPHA_VANTAGE_API_KEY", "")
    fmp_api_key: str = os.getenv("FMP_API_KEY", "")
    yfinance_timeout: int = int(os.getenv("YFINANCE_TIMEOUT", "15"))
    
    # Rate limiting APIs
    api_rate_limit_per_hour: int = int(os.getenv("API_RATE_LIMIT_PER_HOUR", "1000"))
    
    # ==================== PERFORMANCE ====================
    # Workers e threads
    max_workers: int = int(os.getenv("MAX_WORKERS", "4"))
    max_concurrent_requests: int = int(os.getenv("MAX_CONCURRENT_REQUESTS", "100"))
    request_timeout: int = int(os.getenv("REQUEST_TIMEOUT", "30"))
    
    # Background tasks
    celery_broker: str = os.getenv("CELERY_BROKER", "redis://localhost:6379/1")
    celery_backend: str = os.getenv("CELERY_BACKEND", "redis://localhost:6379/2")
    
    # ==================== MONITORING ====================
    # Health checks
    health_check_interval: int = int(os.getenv("HEALTH_CHECK_INTERVAL", "60"))  # 1 minuto
    health_check_timeout: int = int(os.getenv("HEALTH_CHECK_TIMEOUT", "10"))
    
    # Métricas
    prometheus_enabled: bool = os.getenv("PROMETHEUS_ENABLED", "true").lower() == "true"
    prometheus_port: int = int(os.getenv("PROMETHEUS_PORT", "8001"))
    
    # ==================== BACKUP ====================
    # Backup automático
    backup_enabled: bool = os.getenv("BACKUP_ENABLED", "true").lower() == "true"
    backup_schedule: str = os.getenv("BACKUP_SCHEDULE", "0 2 * * *")  # 2h da manhã
    backup_retention_days: int = int(os.getenv("BACKUP_RETENTION_DAYS", "30"))
    backup_storage: str = os.getenv("BACKUP_STORAGE", "local")  # local, s3, gcs
    
    # ==================== FEATURES ====================
    # Feature flags
    enable_new_features: bool = os.getenv("ENABLE_NEW_FEATURES", "false").lower() == "true"
    enable_experimental: bool = os.getenv("ENABLE_EXPERIMENTAL", "false").lower() == "true"
    enable_debugging: bool = os.getenv("ENABLE_DEBUGGING", "false").lower() == "true"
    
    # Agentes
    collector_enabled: bool = os.getenv("COLLECTOR_ENABLED", "true").lower() == "true"
    analyzer_enabled: bool = os.getenv("ANALYZER_ENABLED", "true").lower() == "true"
    recommender_enabled: bool = os.getenv("RECOMMENDER_ENABLED", "true").lower() == "true"
    
    def __post_init__(self):
        """Validações pós-inicialização"""
        # Definir listas padrão
        if self.allowed_origins is None:
            self.allowed_origins = [
                "https://yourdomain.com",
                "https://api.yourdomain.com"
            ]
        
        # Validar configurações críticas
        self._validate_required_settings()
        
        # Construir URLs
        self.database_url = self._build_database_url()
        self.redis_url = self._build_redis_url()
        
    def _validate_required_settings(self):
        """Valida configurações obrigatórias"""
        required_settings = [
            ("POSTGRES_PASSWORD", self.postgres_password),
            ("SECRET_KEY", self.secret_key),
        ]
        
        missing = []
        for name, value in required_settings:
            if not value or value == "":
                missing.append(name)
        
        if missing:
            raise ValueError(f"Configurações obrigatórias faltando: {', '.join(missing)}")
    
    def _build_database_url(self) -> str:
        """Constrói URL do PostgreSQL"""
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}@"
            f"{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
            f"?sslmode={self.postgres_sslmode}"
            f"&application_name={self.project_name.replace(' ', '_')}"
            f"&connect_timeout={self.postgres_connect_timeout}"
        )
    
    def _build_redis_url(self) -> str:
        """Constrói URL do Redis"""
        if not self.redis_enabled:
            return ""
        
        protocol = "rediss" if self.redis_ssl else "redis"
        auth = f":{self.redis_password}@" if self.redis_password else ""
        
        return f"{protocol}://{auth}{self.redis_host}:{self.redis_port}/{self.redis_db}"
    
    def get_database_config(self) -> Dict[str, Any]:
        """Retorna configurações do banco otimizadas"""
        return {
            "url": self.database_url,
            "echo": self.postgres_echo,
            "echo_pool": self.postgres_echo_pool,
            "pool_size": self.postgres_pool_size,
            "max_overflow": self.postgres_max_overflow,
            "pool_timeout": self.postgres_pool_timeout,
            "pool_recycle": self.postgres_pool_recycle,
            "pool_pre_ping": True,
            "connect_args": {
                "connect_timeout": self.postgres_connect_timeout,
                "command_timeout": self.postgres_command_timeout,
                "server_settings": {
                    "application_name": f"{self.project_name} v{self.version}",
                    "timezone": "UTC"
                }
            }
        }
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Retorna configuração de logging"""
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "json": {
                    "format": '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}'
                },
                "detailed": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "level": self.log_level,
                    "formatter": "json" if self.environment == "production" else "detailed"
                },
                "file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "level": self.log_level,
                    "formatter": "json",
                    "filename": self.log_file,
                    "maxBytes": self._parse_size(self.log_max_size),
                    "backupCount": self.log_backup_count
                }
            },
            "loggers": {
                "": {  # root logger
                    "level": self.log_level,
                    "handlers": ["console", "file"]
                },
                "uvicorn": {
                    "level": "INFO",
                    "handlers": ["console", "file"],
                    "propagate": False
                },
                "sqlalchemy.engine": {
                    "level": "WARNING",  # Reduzir logs SQL em produção
                    "handlers": ["file"],
                    "propagate": False
                }
            }
        }
    
    def _parse_size(self, size_str: str) -> int:
        """Converte string de tamanho para bytes"""
        size_str = size_str.upper()
        if size_str.endswith('MB'):
            return int(size_str[:-2]) * 1024 * 1024
        elif size_str.endswith('GB'):
            return int(size_str[:-2]) * 1024 * 1024 * 1024
        return int(size_str)
    
    def is_production(self) -> bool:
        """Verifica se está em ambiente de produção"""
        return self.environment.lower() == "production"
    
    def is_development(self) -> bool:
        """Verifica se está em ambiente de desenvolvimento"""
        return self.environment.lower() in ["development", "dev"]
    
    def get_summary(self) -> Dict[str, Any]:
        """Retorna resumo das configurações"""
        return {
            "project": self.project_name,
            "version": self.version,
            "environment": self.environment,
            "database": {
                "type": "PostgreSQL",
                "host": self.postgres_host,
                "port": self.postgres_port,
                "database": self.postgres_db,
                "pool_size": self.postgres_pool_size,
                "ssl": self.postgres_sslmode
            },
            "cache": {
                "enabled": self.redis_enabled,
                "host": self.redis_host if self.redis_enabled else None,
                "ssl": self.redis_ssl if self.redis_enabled else None
            },
            "features": {
                "collector": self.collector_enabled,
                "analyzer": self.analyzer_enabled,
                "recommender": self.recommender_enabled,
                "backup": self.backup_enabled,
                "monitoring": self.prometheus_enabled
            },
            "security": {
                "ssl_required": self.postgres_sslmode == "require",
                "rate_limiting": True,
                "cors_configured": len(self.allowed_origins) > 0
            }
        }


# ==================== FACTORY FUNCTIONS ====================

@dataclass
class DevelopmentSettings(ProductionSettings):
    """Configurações de desenvolvimento"""
    environment: str = "development"
    postgres_sslmode: str = "prefer"  # SSL opcional em dev
    postgres_pool_size: int = 10  # Pool menor em dev
    postgres_max_overflow: int = 20
    log_level: str = "DEBUG"
    postgres_echo: bool = True  # Logs SQL em dev
    enable_debugging: bool = True


def get_production_settings() -> ProductionSettings:
    """Retorna configurações de produção"""
    return ProductionSettings()


def get_development_settings() -> DevelopmentSettings:
    """Retorna configurações de desenvolvimento"""
    return DevelopmentSettings()


def get_settings() -> ProductionSettings:
    """Factory que retorna configurações baseadas no ambiente"""
    environment = os.getenv("ENVIRONMENT", "development").lower()
    
    if environment == "production":
        return get_production_settings()
    else:
        return get_development_settings()


# ==================== VALIDATION ====================

def validate_production_environment():
    """Valida se ambiente está pronto para produção"""
    settings = get_production_settings()
    
    issues = []
    warnings = []
    
    # Validações críticas
    if not settings.postgres_password:
        issues.append("POSTGRES_PASSWORD não configurado")
    
    if not settings.secret_key:
        issues.append("SECRET_KEY não configurado")
    
    if settings.postgres_sslmode != "require":
        warnings.append("SSL não obrigatório - considere usar sslmode=require em produção")
    
    if settings.log_level == "DEBUG":
        warnings.append("Log level DEBUG em produção pode impactar performance")
    
    if not settings.sentry_dsn:
        warnings.append("Sentry não configurado - monitoramento de erros limitado")
    
    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "warnings": warnings
    }


# ==================== EXAMPLE USAGE ====================

if __name__ == "__main__":
    """Exemplo de uso e validação"""
    
    # Obter configurações
    settings = get_settings()
    
    print("🔧 CONFIGURAÇÕES CARREGADAS")
    print("=" * 50)
    
    summary = settings.get_summary()
    for section, data in summary.items():
        print(f"\n📋 {section.upper()}:")
        if isinstance(data, dict):
            for key, value in data.items():
                print(f"   {key}: {value}")
        else:
            print(f"   {data}")
    
    # Validar ambiente de produção
    if settings.is_production():
        print("\n🔍 VALIDAÇÃO DE PRODUÇÃO")
        print("=" * 50)
        validation = validate_production_environment()
        
        if validation["valid"]:
            print("✅ Ambiente pronto para produção!")
        else:
            print("❌ Problemas encontrados:")
            for issue in validation["issues"]:
                print(f"   • {issue}")
        
        if validation["warnings"]:
            print("\n⚠️ Avisos:")
            for warning in validation["warnings"]:
                print(f"   • {warning}")
    
    print(f"\n🚀 Configurações para {settings.environment} carregadas com sucesso!")