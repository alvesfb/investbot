# database/connection_postgresql.py
"""
Configuração de conexão PostgreSQL otimizada
Sistema de Recomendações de Investimentos - Migração PostgreSQL
"""
from sqlalchemy import create_engine, event, text, pool
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.engine import Engine
from sqlalchemy.pool import NullPool, QueuePool
from contextlib import contextmanager
from typing import Generator, Dict, Any
import logging
import os
import time
from pathlib import Path

# Configurar logging
logger = logging.getLogger(__name__)

# ==================== CONFIGURAÇÕES POSTGRESQL ====================
class PostgreSQLConfig:
    """Configurações PostgreSQL otimizadas"""
    
    def __init__(self):
        # Configurações de conexão
        self.host = os.getenv('POSTGRES_HOST', 'localhost')
        self.port = int(os.getenv('POSTGRES_PORT', '5432'))
        self.database = os.getenv('POSTGRES_DB', 'investment_system')
        self.username = os.getenv('POSTGRES_USER', 'investment_user')
        self.password = os.getenv('POSTGRES_PASSWORD', 'investment_secure_pass_2024')
        
        # SSL Configuration
        self.sslmode = os.getenv('POSTGRES_SSLMODE', 'prefer')
        
        # Pool de conexões
        self.pool_size = int(os.getenv('POSTGRES_POOL_SIZE', '20'))
        self.max_overflow = int(os.getenv('POSTGRES_MAX_OVERFLOW', '30'))
        self.pool_timeout = int(os.getenv('POSTGRES_POOL_TIMEOUT', '30'))
        self.pool_recycle = int(os.getenv('POSTGRES_POOL_RECYCLE', '3600'))
        
        # Configurações de performance
        self.echo = os.getenv('POSTGRES_ECHO', 'false').lower() == 'true'
        self.echo_pool = os.getenv('POSTGRES_ECHO_POOL', 'false').lower() == 'true'
        
        # Timeout configurations
        self.connect_timeout = int(os.getenv('POSTGRES_CONNECT_TIMEOUT', '10'))
        self.command_timeout = int(os.getenv('POSTGRES_COMMAND_TIMEOUT', '60'))
        
    @property
    def database_url(self) -> str:
        """Constrói a URL de conexão PostgreSQL"""
        return (
            f"postgresql://{self.username}:{self.password}@"
            f"{self.host}:{self.port}/{self.database}"
            f"?sslmode={self.sslmode}"
            f"&connect_timeout={self.connect_timeout}"
            f"&application_name=investment_system"
        )
    
    @property 
    def database_url_async(self) -> str:
        """URL para conexões assíncronas (asyncpg)"""
        return (
            f"postgresql+asyncpg://{self.username}:{self.password}@"
            f"{self.host}:{self.port}/{self.database}"
            f"?sslmode={self.sslmode}"
        )


# ==================== CONFIGURAÇÃO GLOBAL ====================
config = PostgreSQLConfig()

# Engine PostgreSQL otimizado
engine = create_engine(
    config.database_url,
    echo=config.echo,
    echo_pool=config.echo_pool,
    
    # Pool de conexões otimizado
    poolclass=QueuePool,
    pool_size=config.pool_size,
    max_overflow=config.max_overflow,
    pool_timeout=config.pool_timeout,
    pool_recycle=config.pool_recycle,
    pool_pre_ping=True,  # Verifica conexão antes de usar
    
    # Configurações PostgreSQL específicas
    connect_args={
        "connect_timeout": config.connect_timeout,
        "options": "-c timezone=UTC -c application_name=investment_system"
    },
    
    # Configurações de performance
    execution_options={
        "isolation_level": "READ_COMMITTED",
        "postgresql_readonly": False,
        "postgresql_deferrable": False,
    }
)

# SessionLocal para criar sessões
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False  # Para trabalhar com objetos após commit
)


# ==================== EVENT LISTENERS POSTGRESQL ====================
@event.listens_for(Engine, "connect")
def configure_postgresql_connection(dbapi_connection, connection_record):
    """Configura conexões PostgreSQL para performance otimizada"""
    with dbapi_connection.cursor() as cursor:
        # Configurações de performance
        cursor.execute("SET work_mem = '64MB'")
        cursor.execute("SET maintenance_work_mem = '256MB'")
        cursor.execute("SET effective_cache_size = '1GB'")
        cursor.execute("SET random_page_cost = 1.1")
        cursor.execute("SET seq_page_cost = 1.0")
        
        # Configurações de timeout
        cursor.execute("SET statement_timeout = '300s'")
        cursor.execute("SET lock_timeout = '30s'")
        cursor.execute("SET idle_in_transaction_session_timeout = '600s'")
        
        # Configurações de logging
        cursor.execute("SET log_statement = 'none'")
        cursor.execute("SET log_min_duration_statement = 1000")  # Log queries > 1s
        
        # Configurações de locale
        cursor.execute("SET timezone = 'UTC'")
        cursor.execute("SET lc_monetary = 'pt_BR.UTF-8'")
        
        logger.debug("PostgreSQL connection configured for performance")


@event.listens_for(Engine, "first_connect")
def setup_postgresql_extensions(dbapi_connection, connection_record):
    """Configura extensões PostgreSQL necessárias"""
    try:
        with dbapi_connection.cursor() as cursor:
            # Extensão para busca textual (trigram)
            cursor.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
            
            # Extensão para UUID
            cursor.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\"")
            
            # Extensão para estatísticas de queries
            cursor.execute("CREATE EXTENSION IF NOT EXISTS pg_stat_statements")
            
            # Extensão para funções criptográficas
            cursor.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")
            
            logger.info("PostgreSQL extensions configured successfully")
    except Exception as e:
        logger.warning(f"Could not configure some PostgreSQL extensions: {e}")


# ==================== DEPENDENCY INJECTION ====================
def get_db() -> Generator[Session, None, None]:
    """
    Dependency para obter sessão do banco de dados
    Usado com FastAPI Depends()
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
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
        logger.error(f"Database transaction error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


# ==================== OPERAÇÕES DE SCHEMA ====================
def create_tables():
    """Cria todas as tabelas definidas nos modelos"""
    try:
        from database.models_postgresql import Base
        Base.metadata.create_all(bind=engine)
        logger.info("PostgreSQL tables created successfully")
        return True
    except Exception as e:
        logger.error(f"Error creating PostgreSQL tables: {e}")
        return False


def drop_tables():
    """Remove todas as tabelas (cuidado!)"""
    try:
        from database.models_postgresql import Base
        Base.metadata.drop_all(bind=engine)
        logger.warning("All PostgreSQL tables dropped")
        return True
    except Exception as e:
        logger.error(f"Error dropping PostgreSQL tables: {e}")
        return False


def reset_database():
    """Reseta o banco completamente (desenvolvimento apenas)"""
    if os.getenv('ENVIRONMENT') == 'production':
        raise RuntimeError("Cannot reset database in production!")
    
    logger.warning("Resetting PostgreSQL database...")
    drop_tables()
    create_tables()
    logger.info("PostgreSQL database reset completed")


# ==================== HEALTH CHECKS ====================
def check_database_connection() -> bool:
    """Verifica se a conexão com PostgreSQL está funcionando"""
    try:
        with engine.connect() as connection:
            # Teste básico de conectividade
            result = connection.execute(text("SELECT 1 as test_connection"))
            result.fetchone()
            
            # Verificar se é PostgreSQL
            result = connection.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            
            if 'PostgreSQL' not in version:
                logger.error(f"Expected PostgreSQL, got: {version}")
                return False
            
            logger.info(f"PostgreSQL connection OK: {version}")
            return True
            
    except Exception as e:
        logger.error(f"PostgreSQL connection failed: {e}")
        return False


def get_database_info() -> Dict[str, Any]:
    """Retorna informações detalhadas sobre o banco PostgreSQL"""
    try:
        with engine.connect() as connection:
            # Informações básicas
            result = connection.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            
            # Tamanho do banco
            result = connection.execute(text("""
                SELECT pg_size_pretty(pg_database_size(current_database())) as db_size
            """))
            db_size = result.fetchone()[0]
            
            # Lista de tabelas
            result = connection.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name
            """))
            tables = [row[0] for row in result.fetchall()]
            
            # Estatísticas de conexão
            result = connection.execute(text("""
                SELECT count(*) as active_connections
                FROM pg_stat_activity 
                WHERE datname = current_database()
            """))
            active_connections = result.fetchone()[0]
            
            # Configurações do pool
            pool_info = {
                "pool_size": engine.pool.size(),
                "checked_in": engine.pool.checkedin(),
                "checked_out": engine.pool.checkedout(),
                "overflow": engine.pool.overflow()
            }
            
            return {
                "type": "PostgreSQL",
                "version": version,
                "database": config.database,
                "host": config.host,
                "port": config.port,
                "size": db_size,
                "tables": tables,
                "table_count": len(tables),
                "active_connections": active_connections,
                "pool_info": pool_info,
                "url": config.database_url.replace(config.password, "***")
            }
            
    except Exception as e:
        logger.error(f"Error getting PostgreSQL database info: {e}")
        return {"error": str(e)}


def get_table_stats() -> Dict[str, Any]:
    """Retorna estatísticas das tabelas"""
    try:
        with engine.connect() as connection:
            result = connection.execute(text("""
                SELECT 
                    schemaname,
                    tablename,
                    n_tup_ins as inserts,
                    n_tup_upd as updates,
                    n_tup_del as deletes,
                    n_live_tup as live_tuples,
                    n_dead_tup as dead_tuples,
                    last_vacuum,
                    last_autovacuum,
                    last_analyze,
                    last_autoanalyze
                FROM pg_stat_user_tables
                ORDER BY n_live_tup DESC
            """))
            
            tables_stats = []
            for row in result.fetchall():
                tables_stats.append({
                    "schema": row[0],
                    "table": row[1],
                    "inserts": row[2],
                    "updates": row[3],
                    "deletes": row[4],
                    "live_tuples": row[5],
                    "dead_tuples": row[6],
                    "last_vacuum": row[7],
                    "last_autovacuum": row[8],
                    "last_analyze": row[9],
                    "last_autoanalyze": row[10]
                })
            
            return {"tables": tables_stats}
            
    except Exception as e:
        logger.error(f"Error getting table stats: {e}")
        return {"error": str(e)}


# ==================== BACKUP E RECOVERY ====================
def backup_database(backup_path: str = None) -> bool:
    """Cria backup do banco PostgreSQL"""
    try:
        if not backup_path:
            timestamp = int(time.time())
            backup_path = f"./database/postgresql/backups/backup_{timestamp}.sql"
        
        # Criar diretório se não existir
        Path(backup_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Comando pg_dump
        cmd = (
            f"pg_dump -h {config.host} -p {config.port} "
            f"-U {config.username} -d {config.database} "
            f"--no-password --verbose --clean --no-acl --no-owner "
            f"-f {backup_path}"
        )
        
        # Configurar variável de ambiente para senha
        env = os.environ.copy()
        env['PGPASSWORD'] = config.password
        
        import subprocess
        result = subprocess.run(cmd.split(), env=env, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info(f"PostgreSQL backup created: {backup_path}")
            return True
        else:
            logger.error(f"PostgreSQL backup failed: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"Error creating PostgreSQL backup: {e}")
        return False


def restore_database(backup_path: str) -> bool:
    """Restaura backup do banco PostgreSQL"""
    try:
        if not Path(backup_path).exists():
            logger.error(f"Backup file not found: {backup_path}")
            return False
        
        # Comando psql para restore
        cmd = (
            f"psql -h {config.host} -p {config.port} "
            f"-U {config.username} -d {config.database} "
            f"--no-password -f {backup_path}"
        )
        
        # Configurar variável de ambiente para senha
        env = os.environ.copy()
        env['PGPASSWORD'] = config.password
        
        import subprocess
        result = subprocess.run(cmd.split(), env=env, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info(f"PostgreSQL restore completed from: {backup_path}")
            return True
        else:
            logger.error(f"PostgreSQL restore failed: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"Error restoring PostgreSQL backup: {e}")
        return False


# ==================== MAINTENANCE ====================
def vacuum_analyze_tables():
    """Executa VACUUM ANALYZE em todas as tabelas"""
    try:
        with engine.connect() as connection:
            # Obter lista de tabelas
            result = connection.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """))
            
            tables = [row[0] for row in result.fetchall()]
            
            for table in tables:
                logger.info(f"VACUUM ANALYZE {table}...")
                connection.execute(text(f"VACUUM ANALYZE {table}"))
                connection.commit()
            
            logger.info(f"VACUUM ANALYZE completed for {len(tables)} tables")
            return True
            
    except Exception as e:
        logger.error(f"Error in VACUUM ANALYZE: {e}")
        return False


def reindex_tables():
    """Reconstrói índices de todas as tabelas"""
    try:
        with engine.connect() as connection:
            connection.execute(text("REINDEX DATABASE CONCURRENTLY investment_system"))
            connection.commit()
            logger.info("Database reindex completed")
            return True
            
    except Exception as e:
        logger.error(f"Error in reindex: {e}")
        return False


# ==================== CONFIGURAÇÃO INICIAL ====================
def init_database():
    """Inicializa o banco PostgreSQL"""
    try:
        logger.info("Initializing PostgreSQL database...")
        
        # Verificar conexão
        if not check_database_connection():
            logger.error("Cannot connect to PostgreSQL")
            return False
        
        # Criar tabelas
        if not create_tables():
            logger.error("Failed to create tables")
            return False
        
        logger.info("PostgreSQL database initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error initializing PostgreSQL database: {e}")
        return False


# ==================== VERIFICAÇÃO DE ENVIRONMENT ====================
def validate_environment():
    """Valida se o ambiente PostgreSQL está configurado corretamente"""
    issues = []
    
    # Verificar variáveis de ambiente obrigatórias
    required_vars = ['POSTGRES_HOST', 'POSTGRES_DB', 'POSTGRES_USER', 'POSTGRES_PASSWORD']
    for var in required_vars:
        if not os.getenv(var):
            issues.append(f"Missing environment variable: {var}")
    
    # Verificar conectividade
    if not check_database_connection():
        issues.append("Cannot connect to PostgreSQL database")
    
    # Verificar extensões
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT extname FROM pg_extension"))
            extensions = [row[0] for row in result.fetchall()]
            
            required_extensions = ['pg_trgm', 'uuid-ossp']
            for ext in required_extensions:
                if ext not in extensions:
                    issues.append(f"Missing PostgreSQL extension: {ext}")
                    
    except Exception as e:
        issues.append(f"Cannot check PostgreSQL extensions: {e}")
    
    return issues


if __name__ == "__main__":
    # Teste básico de conexão
    print("Testing PostgreSQL connection...")
    if check_database_connection():
        print("✅ PostgreSQL connection successful")
        db_info = get_database_info()
        print(f"📊 Database: {db_info.get('database')}")
        print(f"🏷️ Version: {db_info.get('version', '').split()[0:2]}")
        print(f"📋 Tables: {db_info.get('table_count', 0)}")
    else:
        print("❌ PostgreSQL connection failed")