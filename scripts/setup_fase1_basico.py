# scripts/setup_fase1_basico.py
"""
Setup Rápido da Fase 1 para preparar migração para Fase 2
Cria apenas os componentes essenciais
"""
import os
import sys
from pathlib import Path

def create_basic_phase1():
    """Cria estrutura básica da Fase 1"""
    project_root = Path.cwd()
    
    print("🚀 Criando estrutura básica da Fase 1...")
    
    # 1. Criar diretórios
    dirs = [
        'database',
        'config', 
        'agents',
        'agents/collectors',
        'api',
        'tests',
        'data',
        'logs'
    ]
    
    for dir_path in dirs:
        (project_root / dir_path).mkdir(parents=True, exist_ok=True)
        # Criar __init__.py
        init_file = project_root / dir_path / '__init__.py'
        if not init_file.exists():
            init_file.write_text('# Auto-generated\n')
    
    print("✅ Diretórios criados")
    
    # 2. Criar models.py básico da Fase 1
    models_content = '''# database/models.py - Versão Básica Fase 1
"""
Modelos SQLAlchemy básicos para Fase 1
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from typing import Dict, Any

Base = declarative_base()

class Stock(Base):
    """Modelo básico para ações - Fase 1"""
    __tablename__ = "stocks"

    # Identificação
    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(10), unique=True, index=True, nullable=False)
    nome = Column(String(200), nullable=False)
    nome_completo = Column(String(500))

    # Classificação
    setor = Column(String(100), index=True)
    subsetor = Column(String(100))
    segmento = Column(String(100))

    # Informações básicas
    cnpj = Column(String(20))
    website = Column(String(200))
    descricao = Column(Text)

    # Status
    ativo = Column(Boolean, default=True, index=True)
    listagem = Column(String(50))

    # Dados de mercado
    preco_atual = Column(Float)
    volume_medio = Column(Float)
    market_cap = Column(Float)
    free_float = Column(Float)

    # Dados fundamentalistas básicos
    p_l = Column(Float)
    p_vp = Column(Float)
    ev_ebitda = Column(Float)
    roe = Column(Float)
    roic = Column(Float)
    margem_liquida = Column(Float)
    divida_liquida_ebitda = Column(Float)

    # Metadados
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    ultima_atualizacao_preco = Column(DateTime(timezone=True))
    ultima_atualizacao_fundamentals = Column(DateTime(timezone=True))

    # Relacionamentos
    recommendations = relationship("Recommendation", back_populates="stock")

    # Índices
    __table_args__ = (
        Index('idx_stock_setor_ativo', 'setor', 'ativo'),
        Index('idx_stock_market_cap', 'market_cap'),
        Index('idx_stock_volume', 'volume_medio'),
    )

    def __repr__(self):
        return f"<Stock(codigo='{self.codigo}', nome='{self.nome}')>"

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'codigo': self.codigo,
            'nome': self.nome,
            'setor': self.setor,
            'preco_atual': self.preco_atual,
            'market_cap': self.market_cap,
            'p_l': self.p_l,
            'p_vp': self.p_vp,
            'roe': self.roe,
            'ativo': self.ativo,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Recommendation(Base):
    """Modelo básico para recomendações"""
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False)
    data_analise = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    score_fundamentalista = Column(Float, nullable=False)
    score_final = Column(Float, nullable=False)
    classificacao = Column(String(20), nullable=False, index=True)
    justificativa = Column(Text, nullable=False)
    preco_entrada = Column(Float)
    stop_loss = Column(Float)
    ativa = Column(Boolean, default=True, index=True)

    # Relacionamento
    stock = relationship("Stock", back_populates="recommendations")

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'stock_codigo': self.stock.codigo if self.stock else None,
            'classificacao': self.classificacao,
            'score_final': self.score_final,
            'justificativa': self.justificativa
        }
'''
    
    models_path = project_root / 'database' / 'models.py'
    models_path.write_text(models_content, encoding='utf-8')
    print("✅ database/models.py criado")
    
    # 3. Criar connection.py básico
    connection_content = '''# database/connection.py
"""
Configuração básica de conexão com banco de dados
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from typing import Generator
import logging

logger = logging.getLogger(__name__)

# Engine básico com SQLite
DATABASE_URL = "sqlite:///./data/investment_system.db"
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Dependency para FastAPI"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def get_db_session():
    """Context manager para sessões"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

def create_tables():
    """Cria todas as tabelas"""
    try:
        from database.models import Base
        Base.metadata.create_all(bind=engine)
        return True
    except Exception as e:
        logger.error(f"Erro ao criar tabelas: {e}")
        return False

def check_database_connection() -> bool:
    """Verifica conexão com banco"""
    try:
        with engine.connect():
            pass
        return True
    except Exception:
        return False

def get_database_info() -> dict:
    """Retorna informações do banco"""
    try:
        with engine.connect() as conn:
            # SQLite específico
            result = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in result.fetchall()]
            
            return {
                "type": "SQLite",
                "url": DATABASE_URL,
                "tables": tables
            }
    except Exception as e:
        return {"error": str(e)}
'''
    
    connection_path = project_root / 'database' / 'connection.py'
    connection_path.write_text(connection_content, encoding='utf-8')
    print("✅ database/connection.py criado")
    
    # 4. Criar settings.py básico
    settings_content = '''# config/settings.py
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
'''
    
    settings_path = project_root / 'config' / 'settings.py'
    settings_path.write_text(settings_content, encoding='utf-8')
    print("✅ config/settings.py criado")
    
    # 5. Criar arquivo .env básico
    env_content = '''# Configurações básicas
ENVIRONMENT=development
DEBUG=true
DATABASE_URL=sqlite:///./data/investment_system.db
ANTHROPIC_API_KEY=your_claude_api_key_here
'''
    
    env_path = project_root / '.env'
    if not env_path.exists():
        env_path.write_text(env_content, encoding='utf-8')
        print("✅ .env criado")
    
    # 6. Inicializar banco
    print("📋 Inicializando banco de dados...")
    try:
        sys.path.insert(0, str(project_root))
        from database.connection import create_tables
        if create_tables():
            print("✅ Banco de dados inicializado")
        else:
            print("⚠️  Problema na criação das tabelas")
    except Exception as e:
        print(f"⚠️  Erro ao inicializar banco: {e}")
    
    print("\n🎉 Fase 1 básica criada com sucesso!")
    print("📁 Estrutura criada:")
    print("   ✅ database/models.py (versão básica)")
    print("   ✅ database/connection.py")
    print("   ✅ config/settings.py")
    print("   ✅ .env")
    print("   ✅ Banco SQLite inicializado")
    
    return True

if __name__ == "__main__":
    create_basic_phase1()
