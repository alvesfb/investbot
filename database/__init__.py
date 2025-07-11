# database/__init__.py
"""
Módulo de banco de dados do Sistema de Recomendações de Investimentos

Este módulo contém:
- Modelos SQLAlchemy (models.py)
- Configuração de conexão (connection.py)
- Repositories para acesso aos dados (repositories.py)
- Scripts de inicialização (init_db.py)
"""

# Imports principais
from database.models import (
    Base,
    Stock,
    Recommendation,
    FundamentalAnalysis,
    AgentSession,
    MarketData
)

from database.connection import (
    engine,
    SessionLocal,
    get_db,
    get_db_session,
    create_tables,
    check_database_connection,
    get_database_info,
    init_database
)

from database.repositories import (
    StockRepository,
    RecommendationRepository,
    FundamentalAnalysisRepository,
    AgentSessionRepository,
    MarketDataRepository,
    get_stock_repository,
    get_recommendation_repository,
    get_fundamental_repository,
    get_agent_session_repository,
    get_market_data_repository
)

# Versão do módulo
__version__ = "1.0.0"

# Exports principais
__all__ = [
    # Modelos
    "Base",
    "Stock",
    "Recommendation",
    "FundamentalAnalysis",
    "AgentSession",
    "MarketData",

    # Conexão
    "engine",
    "SessionLocal",
    "get_db",
    "get_db_session",
    "create_tables",
    "check_database_connection",
    "get_database_info",
    "init_database",

    # Repositories
    "StockRepository",
    "RecommendationRepository",
    "FundamentalAnalysisRepository",
    "AgentSessionRepository",
    "MarketDataRepository",
    "get_stock_repository",
    "get_recommendation_repository",
    "get_fundamental_repository",
    "get_agent_session_repository",
    "get_market_data_repository"
]
