# config/settings.py
"""
Configurações básicas do sistema
"""
from pathlib import Path

class Settings:
    def __init__(self):
        self.environment = "development"
        self.debug = True
        self.database_url = "sqlite:///./data/investment_system.db"
        self.project_root = Path(__file__).parent.parent
        self.data_dir = self.project_root / "data"
        self.logs_dir = self.project_root / "logs"
        
        # Criar diretórios se não existirem
        self.data_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)
    
    @property
    def database_path(self):
        """Caminho do banco SQLite"""
        if self.database_url.startswith("sqlite"):
            db_path = self.database_url.replace("sqlite:///", "")
            return Path(db_path)
        return None

# Instância global
settings = Settings()

def get_settings():
    return settings


# ==================== FASE 2 - ANÁLISE FUNDAMENTALISTA ====================
class Phase2Settings:
    """Configurações específicas da Fase 2"""
    
    def __init__(self):
        # Sistema de Métricas
        self.metrics_config_file = "config/metrics_config.json"
        self.enable_sector_benchmarks = True
        self.benchmark_update_frequency = "weekly"
        
        # Análise Fundamentalista
        self.min_data_completeness = 0.6
        self.confidence_threshold = 0.7
        self.historical_periods = 5
        
        # Performance
        self.enable_parallel_analysis = True
        self.max_concurrent_analyses = 10
        self.analysis_timeout_seconds = 300

# Instância global para Fase 2
phase2_settings = Phase2Settings()

def get_phase2_settings():
    """Retorna configurações da Fase 2"""
    return phase2_settings
