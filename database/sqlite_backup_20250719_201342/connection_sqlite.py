# database/connection.py
"""
Configuração de conexão com o banco de dados
"""
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.engine import Engine
from contextlib import contextmanager
from typing import Generator
import sqlite3
import logging
from pathlib import Path

# Configurar logging
logger = logging.getLogger(__name__)

# Configurações globais
DATABASE_URL = "sqlite:///./data/investment_system.db"

# Engine do SQLAlchemy
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Não fazer log de queries por padrão
    pool_pre_ping=True,  # Verifica conexão antes de usar
    pool_recycle=3600,  # Recicla conexões a cada hora
    connect_args={"check_same_thread": False}  # SQLite específico
)

# SessionLocal para criar sessões
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Configurações específicas para SQLite
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Configura pragmas do SQLite para melhor performance e integridade"""
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()

        # Configurações de performance
        cursor.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging
        cursor.execute("PRAGMA synchronous=NORMAL")  # Balance seg. e perfor.
        cursor.execute("PRAGMA cache_size=10000")  # Cache maior
        cursor.execute("PRAGMA temp_store=MEMORY")  # Tabelas temp em memória

        # Configurações de integridade
        cursor.execute("PRAGMA foreign_keys=ON")  # Habilita foreign keys
        cursor.execute("PRAGMA busy_timeout=20000")  # Timeout de 20 segundos

        cursor.close()
        logger.debug("SQLite pragmas configurados")


def get_db() -> Generator[Session, None, None]:
    """
    Dependency para obter sessão do banco de dados
    Usado com FastAPI Depends()
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Erro na sessão do banco: {e}")
        db.rollback()
        raise
    finally:
        db.close()


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """
    Context manager para sessões do banco
    Uso: with get_db_session() as db: ...
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        logger.error(f"Erro na transação: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def create_tables():
    """Cria todas as tabelas definidas nos modelos"""
    try:
        from database.models import Base
        Base.metadata.create_all(bind=engine)
        logger.info("Tabelas criadas com sucesso")
        return True
    except Exception as e:
        logger.error(f"Erro ao criar tabelas: {e}")
        return False


def drop_tables():
    """Remove todas as tabelas (cuidado!)"""
    try:
        from database.models import Base
        Base.metadata.drop_all(bind=engine)
        logger.warning("Todas as tabelas foram removidas")
        return True
    except Exception as e:
        logger.error(f"Erro ao remover tabelas: {e}")
        return False


def check_database_connection() -> bool:
    """Verifica se a conexão com o banco está funcionando"""
    try:
        with engine.connect() as connection:
            # Teste simples de query
            result = connection.execute(text("SELECT 1"))
            result.fetchone()
        logger.info("Conexão com banco de dados OK")
        return True
    except Exception as e:
        logger.error(f"Erro na conexão com banco: {e}")
        return False


def get_database_info() -> dict:
    """Retorna informações sobre o banco de dados"""
    try:
        with engine.connect() as connection:
            # Informações específicas do SQLite
            result = connection.execute(text("PRAGMA database_list"))
            databases = result.fetchall()

            result = connection.execute(
                text("SELECT name FROM sqlite_master WHERE type='table'"))
            tables = [row[0] for row in result.fetchall()]

            # Tamanho do arquivo de banco
            db_path = Path("data/investment_system.db")
            file_size = db_path.stat().st_size if db_path.exists() else 0

            return {
                "type": "SQLite",
                "url": DATABASE_URL,
                "file_path": str(db_path) if db_path.exists() else None,
                "file_size_bytes": file_size,
                "file_size_mb": round(file_size / 1024 / 1024, 2),
                "tables": tables,
                "databases": [row._asdict() for row in databases] if databases else []
            }

    except Exception as e:
        logger.error(f"Erro ao obter informações do banco: {e}")
        return {"error": str(e)}


def vacuum_database():
    """Executa VACUUM no SQLite para otimizar o banco"""
    try:
        with engine.connect() as connection:
            connection.execute(text("VACUUM"))
        logger.info("VACUUM executado com sucesso")
        return True
    except Exception as e:
        logger.error(f"Erro ao executar VACUUM: {e}")
        return False


def backup_database(backup_path: str = None) -> bool:
    """
    Faz backup do banco SQLite
    """
    try:
        import shutil
        from datetime import datetime

        db_path = Path("data/investment_system.db")
        if not db_path.exists():
            logger.error("Arquivo de banco não encontrado")
            return False

        if not backup_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"data/bkp_investment_system_{timestamp}.db"

        shutil.copy2(db_path, backup_path)
        logger.info(f"Backup criado: {backup_path}")
        return True

    except Exception as e:
        logger.error(f"Erro ao criar backup: {e}")
        return False


def init_database():
    """Inicializa o banco de dados"""
    logger.info("Inicializando banco de dados...")

    # Criar diretório data se não existir
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)

    # Verificar conexão
    if not check_database_connection():
        raise RuntimeError("Não foi possível conectar ao banco de dados")

    # Criar tabelas se não existirem
    if not create_tables():
        raise RuntimeError("Falha ao criar tabelas")

    # Log de informações
    db_info = get_database_info()
    logger.info(f"Banco configurado: {db_info.get('type', 'Unknown')}")

    if db_info.get('tables'):
        logger.info(f"Tabelas encontradas: {', '.join(db_info['tables'])}")

    return True


# Funções de compatibilidade e utilitárias
def get_settings():
    """Função de compatibilidade para obter configurações"""
    try:
        from config.settings import get_settings as _get_settings
        return _get_settings()
    except ImportError:
        # Configurações básicas se settings não estiver disponível
        class BasicSettings:
            def __init__(self):
                self.database_url = DATABASE_URL
                self.database_path = Path("data/investment_system.db")
                self.is_development = True
        
        return BasicSettings()


# Executar inicialização básica na importação
try:
    # Verificar se diretório data existe
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # Verificar conexão básica
    check_database_connection()
    
except Exception as e:
    logger.warning(f"Falha na inicialização automática: {e}")


if __name__ == "__main__":
    # Teste básico
    print("Testando conexão com banco de dados...")
    if check_database_connection():
        print("✅ Conexão OK")
        
        db_info = get_database_info()
        print(f"Tipo: {db_info.get('type')}")
        print(f"Tabelas: {len(db_info.get('tables', []))}")
        
        if create_tables():
            print("✅ Tabelas criadas")
        else:
            print("❌ Erro ao criar tabelas")
    else:
        print("❌ Falha na conexão")
