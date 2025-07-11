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

from config.settings import get_settings

# Configurar logging
logger = logging.getLogger(__name__)

# Configurações globais
settings = get_settings()

# Engine do SQLAlchemy
engine = create_engine(
    settings.database_url,
    echo=settings.database_echo,  # Log de queries SQL se debug
    pool_pre_ping=True,  # Verifica conexão antes de usar
    pool_recycle=3600,  # Recicla conexões a cada hora
    connect_args={"check_same_thread": False} if "sqlite" in
    settings.database_url else {}
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
        logger.info("SQLite pragmas configurados")


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
    from database.models import Base

    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Tabelas criadas com sucesso")
        return True
    except Exception as e:
        logger.error(f"Erro ao criar tabelas: {e}")
        return False


def drop_tables():
    """Remove todas as tabelas (cuidado!)"""
    from database.models import Base

    try:
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
            if "sqlite" in settings.database_url:
                # Informações específicas do SQLite
                result = connection.execute(text("PRAGMA database_list"))
                databases = result.fetchall()

                result = connection.execute(
                    text("SELECT name FROM sqlite_master WHERE type='table'"))
                tables = [row[0] for row in result.fetchall()]

                # Tamanho do arquivo de banco
                db_path = settings.database_path
                file_size = db_path.stat().st_size if (db_path and
                                                       db_path.exists()) else 0

                return {
                    "type": "SQLite",
                    "url": settings.database_url,
                    "file_path": str(db_path) if db_path else None,
                    "file_size_bytes": file_size,
                    "file_size_mb": round(file_size / 1024 / 1024, 2),
                    "tables": tables,
                    "databases": [row._asdict() for row in databases]
                    if databases else []
                }
            else:
                # Para outros bancos (PostgreSQL, etc.)
                result = connection.execute(text("SELECT version()"))
                version = result.fetchone()[0]

                return {
                    "type": "PostgreSQL",
                    "url": settings.database_url,
                    "version": version
                }

    except Exception as e:
        logger.error(f"Erro ao obter informações do banco: {e}")
        return {"error": str(e)}


def vacuum_database():
    """Executa VACUUM no SQLite para otimizar o banco"""
    if "sqlite" not in settings.database_url:
        logger.warning("VACUUM só é suportado no SQLite")
        return False

    try:
        with engine.connect() as connection:
            connection.execute("VACUUM")
        logger.info("VACUUM executado com sucesso")
        return True
    except Exception as e:
        logger.error(f"Erro ao executar VACUUM: {e}")
        return False


def backup_database(backup_path: str = None) -> bool:
    """
    Faz backup do banco SQLite
    """
    if "sqlite" not in settings.database_url:
        logger.warning("Backup automático só é suportado no SQLite")
        return False

    try:
        import shutil
        from datetime import datetime

        db_path = settings.database_path
        if not db_path or not db_path.exists():
            logger.error("Arquivo de banco não encontrado")
            return False

        if not backup_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = db_path.parent / f"bkp_{db_path.stem}_{timestamp}.db"

        shutil.copy2(db_path, backup_path)
        logger.info(f"Backup criado: {backup_path}")
        return True

    except Exception as e:
        logger.error(f"Erro ao criar backup: {e}")
        return False


# Inicialização automática
def init_database():
    """Inicializa o banco de dados"""
    logger.info("Inicializando banco de dados...")

    # Verificar conexão
    if not check_database_connection():
        raise RuntimeError("Não foi possível conectar ao banco de dados")

    # Criar tabelas se não existirem
    create_tables()

    # Log de informações
    db_info = get_database_info()
    logger.info(f"Banco configurado: {db_info.get('type', 'Unknown')}")

    if db_info.get('tables'):
        logger.info(f"Tabelas encontradas: {', '.join(db_info['tables'])}")

    return True


# Executar na importação se for desenvolvimento
if settings.is_development:
    try:
        init_database()
    except Exception as e:
        logger.warning(f"Falha na inicialização automática do banco: {e}")
