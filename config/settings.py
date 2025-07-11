# config/settings.py - Versão robusta e organizada
"""
Configurações centralizadas do Sistema de Recomendações de Investimentos
"""
from pydantic_settings import BaseSettings
from pydantic import Field, validator
from pathlib import Path
from typing import Optional, List
import os


class Settings(BaseSettings):
    """Configurações principais do sistema"""

    # ==================== AMBIENTE ====================
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=True, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")

    # ==================== APIs EXTERNAS ====================
    # Claude API (obrigatório)
    anthropic_api_key: str = Field(
        default="your_claude_api_key_here", env="ANTHROPIC_API_KEY")
    claude_model: str = Field(
        default="claude-3-sonnet-20240229", env="CLAUDE_MODEL")

    # YFinance
    yfinance_timeout: int = Field(default=30, env="YFINANCE_TIMEOUT")

    # Alpha Vantage (backup opcional)
    alpha_vantage_api_key: Optional[str] = Field(
        default=None, env="ALPHA_VANTAGE_API_KEY")

    # ==================== DATABASE ====================
    database_url: str = Field(
        default="sqlite:///./data/investment_system.db", env="DATABASE_URL")
    database_echo: bool = Field(default=False, env="DATABASE_ECHO")

    # ==================== FASTAPI ====================
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")
    api_reload: bool = Field(default=True, env="API_RELOAD")

    # ==================== AGNO FRAMEWORK ====================
    agno_log_level: str = Field(default="INFO", env="AGNO_LOG_LEVEL")
    agno_max_workers: int = Field(default=4, env="AGNO_MAX_WORKERS")

    # ==================== LOGGING ====================
    log_file: str = Field(default="logs/investment_system.log", env="LOG_FILE")
    log_rotation: str = Field(default="1 week", env="LOG_ROTATION")
    log_retention: str = Field(default="1 month", env="LOG_RETENTION")

    # ==================== RATE LIMITING ====================
    requests_per_minute: int = Field(default=100, env="REQUESTS_PER_MINUTE")
    requests_per_hour: int = Field(default=2000, env="REQUESTS_PER_HOUR")

    # ==================== CACHE ====================
    cache_ttl_seconds: int = Field(default=3600, env="CACHE_TTL_SECONDS")
    cache_max_size: int = Field(default=1000, env="CACHE_MAX_SIZE")

    # ==================== SECURITY ====================
    secret_key: str = Field(
        default="dev-secret-key-change-in-production", env="SECRET_KEY")
    allowed_hosts: str = Field(
        default="localhost,127.0.0.1,0.0.0.0", env="ALLOWED_HOSTS")

    # ==================== EMAIL (Opcional) ====================
    smtp_host: Optional[str] = Field(default=None, env="SMTP_HOST")
    smtp_port: int = Field(default=587, env="SMTP_PORT")
    smtp_user: Optional[str] = Field(default=None, env="SMTP_USER")
    smtp_password: Optional[str] = Field(default=None, env="SMTP_PASSWORD")
    smtp_tls: bool = Field(default=True, env="SMTP_TLS")

    # ==================== MONITORING ====================
    enable_metrics: bool = Field(default=True, env="ENABLE_METRICS")
    health_check_interval: int = Field(default=60, env="HEALTH_CHECK_INTERVAL")

    # ==================== VALIDADORES ====================
    @validator("anthropic_api_key")
    def validate_anthropic_key(cls, v):
        if v == "your_claude_api_key_here":
            print("⚠️  ATENÇÃO: Configure sua chave da API do Claude no .env")
        return v

    @validator("secret_key")
    def validate_secret_key(cls, v):
        if v == "dev-secret-key-change-in-production":
            print(" Usando chave secreta padrão - altere em produção")
        if len(v) < 32:
            print("Chave secreta muito curta (recomendado: 64+ caracteres)")
        return v

    @validator("environment")
    def validate_environment(cls, v):
        valid_envs = ["development", "testing", "staging", "production"]
        if v.lower() not in valid_envs:
            raise ValueError(f"Ambiente deve ser um de: {valid_envs}")
        return v.lower()

    # ==================== PROPERTIES ====================
    @property
    def is_development(self) -> bool:
        return self.environment == "development"

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def is_testing(self) -> bool:
        return self.environment == "testing"

    @property
    def allowed_hosts_list(self) -> List[str]:
        """Retorna allowed_hosts como lista"""
        return [
            host.strip() for host in
            self.allowed_hosts.split(",") if host.strip()]

    @property
    def project_root(self) -> Path:
        """Diretório raiz do projeto"""
        return Path(__file__).parent.parent

    @property
    def data_dir(self) -> Path:
        """Diretório de dados - cria se não existir"""
        path = self.project_root / "data"
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def logs_dir(self) -> Path:
        """Diretório de logs - cria se não existir"""
        path = self.project_root / "logs"
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def database_path(self) -> Optional[Path]:
        """Caminho do banco SQLite se aplicável"""
        if self.database_url.startswith("sqlite"):
            db_path = self.database_url.replace("sqlite:///", "")
            return Path(db_path)
        return None

    @property
    def has_email_config(self) -> bool:
        """Verifica se email está configurado"""
        return all([self.smtp_host, self.smtp_user, self.smtp_password])

    @property
    def api_base_url(self) -> str:
        """URL base da API"""
        return f"http://{self.api_host}:{self.api_port}"

    # ==================== CONFIGURATION ====================
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        # Permite campos extras (para compatibilidade)
        extra = "ignore"


class AgentSettings:
    """
    Configurações específicas dos agentes
    Classe simples para evitar conflitos com Pydantic
    """

    def __init__(self):
        # ==================== AGENTE COLETOR ====================
        self.collector_schedule = os.getenv(
            "COLLECTOR_SCHEDULE", "0 7 * * 1-5")  # 7h, seg-sex
        self.collector_batch_size = int(os.getenv(
            "COLLECTOR_BATCH_SIZE", "50"))
        self.collector_retry_attempts = int(os.getenv(
            "COLLECTOR_RETRY_ATTEMPTS", "3"))
        self.collector_timeout = int(os.getenv(
            "COLLECTOR_TIMEOUT", "30"))

        # ==================== AGENTE ANALISADOR ====================
        self.analyzer_min_market_cap = float(
            os.getenv("ANALYZER_MIN_MARKET_CAP", "1000000000"))  # 1B
        self.analyzer_min_volume = float(
            os.getenv("ANALYZER_MIN_VOLUME", "10000000"))  # 10M
        self.analyzer_exclude_penny_stocks = os.getenv(
            "ANALYZER_EXCLUDE_PENNY_STOCKS", "true").lower() == "true"
        self.analyzer_penny_stock_threshold = float(
            os.getenv("ANALYZER_PENNY_STOCK_THRESHOLD", "5.0"))

        # ==================== AGENTE RECOMENDADOR ====================
        self.recommender_fundamental_weight = float(
            os.getenv("RECOMMENDER_FUNDAMENTAL_WEIGHT", "0.7"))
        self.recommender_technical_weight = float(
            os.getenv("RECOMMENDER_TECHNICAL_WEIGHT", "0.3"))
        self.recommender_max_recommendations = int(
            os.getenv("RECOMMENDER_MAX_RECOMMENDATIONS", "20"))

        # ==================== THRESHOLDS DE CLASSIFICAÇÃO ====================
        self.strong_buy_threshold = float(
            os.getenv("STRONG_BUY_THRESHOLD", "90.0"))
        self.buy_threshold = float(
            os.getenv("BUY_THRESHOLD", "70.0"))
        self.neutral_threshold_high = float(
            os.getenv("NEUTRAL_THRESHOLD_HIGH", "69.0"))
        self.neutral_threshold_low = float(
            os.getenv("NEUTRAL_THRESHOLD_LOW", "30.0"))
        self.sell_threshold = float(
            os.getenv("SELL_THRESHOLD", "10.0"))
        self.strong_sell_threshold = float(
            os.getenv("STRONG_SELL_THRESHOLD", "0.0"))

        # ==================== VALIDAÇÕES ====================
        self._validate_weights()
        self._validate_thresholds()

    def _validate_weights(self):
        """Valida se os pesos somam 1.0"""
        total = self.recommender_fundamental_weight + \
            self.recommender_technical_weight
        if abs(total - 1.0) > 0.01:
            print(f"⚠️  ATENÇÃO: Pesos não somam 1.0 (atual: {total:.2f})")

    def _validate_thresholds(self):
        """Valida se os thresholds estão em ordem"""
        thresholds = [
            self.strong_sell_threshold,
            self.sell_threshold,
            self.neutral_threshold_low,
            self.neutral_threshold_high,
            self.buy_threshold,
            self.strong_buy_threshold
        ]

        if thresholds != sorted(thresholds):
            print("⚠️  ATENÇÃO: Thresholds não estão em ordem crescente")

    def get_classification(self, score: float) -> str:
        """Classifica um score em categoria"""
        if score >= self.strong_buy_threshold:
            return "COMPRA FORTE"
        elif score >= self.buy_threshold:
            return "COMPRA"
        elif score >= self.neutral_threshold_low:
            return "NEUTRO"
        elif score >= self.sell_threshold:
            return "VENDA"
        else:
            return "VENDA FORTE"

    def to_dict(self) -> dict:
        """Retorna todas as configurações como dict"""
        return {
            attr: getattr(self, attr)
            for attr in dir(self)
            if not attr.startswith('_') and not callable(getattr(self, attr))
        }


# ==================== INSTÂNCIAS GLOBAIS ====================
def create_settings() -> Settings:
    """Factory para criar settings com tratamento de erro"""
    try:
        return Settings()
    except Exception as e:
        print(f"❌ Erro ao carregar configurações: {e}")
        print("💡 Verifique o arquivo .env")
        raise


def create_agent_settings() -> AgentSettings:
    """Factory para criar agent settings"""
    try:
        return AgentSettings()
    except Exception as e:
        print(f"❌ Erro ao carregar configurações dos agentes: {e}")
        print("💡 Usando valores padrão")
        # Retorna instância com defaults em caso de erro
        agent_settings = AgentSettings()
        return agent_settings


# Criar instâncias globais
settings = create_settings()
agent_settings = create_agent_settings()


# ==================== FUNÇÕES UTILITÁRIAS ====================
def get_settings() -> Settings:
    """Retorna instância das configurações principais"""
    return settings


def get_agent_settings() -> AgentSettings:
    """Retorna instância das configurações dos agentes"""
    return agent_settings


def print_config_summary():
    """Imprime resumo das configurações carregadas"""
    print("=" * 60)
    print("📋 RESUMO DAS CONFIGURAÇÕES")
    print("=" * 60)
    print(f"🌍 Ambiente: {settings.environment}")
    print(f"🐛 Debug: {settings.debug}")
    print(f"🔗 API: {settings.api_base_url}")
    print(f"💾 Database: {settings.database_url}")
    print(f"🤖 Claude Model: {settings.claude_model}")
    print(f"👥 Agno Workers: {settings.agno_max_workers}")
    print(f"📊 Max Recomendações: \
          {agent_settings.recommender_max_recommendations}")
    print(f"📁 Data Dir: {settings.data_dir}")
    print(f"📋 Logs Dir: {settings.logs_dir}")
    print("=" * 60)


def init_directories():
    """Inicializa diretórios necessários"""
    settings.data_dir  # Property que cria o diretório
    settings.logs_dir  # Property que cria o diretório
    print(f"📁 Diretórios inicializados: \
          {settings.data_dir}, {settings.logs_dir}")


# ==================== INICIALIZAÇÃO ====================
# Executar na importação
init_directories()

# Imprimir resumo se não estiver em modo de teste
if settings.environment != "testing":
    print_config_summary()
