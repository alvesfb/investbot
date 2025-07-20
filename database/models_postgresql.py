# database/models_postgresql.py
"""
Modelos SQLAlchemy otimizados para PostgreSQL
Sistema de Recomendações de Investimentos - Migração PostgreSQL
"""
from sqlalchemy import (
    Column, Integer, String, Numeric, Boolean, DateTime, Text, 
    ForeignKey, Index, JSON, UniqueConstraint, CheckConstraint,
    BigInteger, SmallInteger, func
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB, ENUM
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum as PyEnum
import uuid

Base = declarative_base()

# ==================== ENUMS POSTGRESQL ====================
class DataQualityEnum(PyEnum):
    """Níveis de qualidade dos dados"""
    EXCELLENT = "excellent"  # >95% campos preenchidos
    GOOD = "good"           # 85-95% campos preenchidos
    MEDIUM = "medium"       # 70-85% campos preenchidos
    POOR = "poor"          # 50-70% campos preenchidos
    CRITICAL = "critical"   # <50% campos preenchidos


class StockStatusEnum(PyEnum):
    """Status das ações"""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DELISTED = "delisted"
    UNDER_REVIEW = "under_review"


class RecommendationEnum(PyEnum):
    """Tipos de recomendação"""
    STRONG_BUY = "strong_buy"    # 90-100
    BUY = "buy"                  # 70-89
    HOLD = "hold"                # 40-69
    SELL = "sell"                # 20-39
    STRONG_SELL = "strong_sell"  # 0-19


# ==================== MODELO PRINCIPAL OTIMIZADO ====================
class Stock(Base):
    """
    Modelo principal para ações - OTIMIZADO POSTGRESQL
    Schema padronizado com nomenclatura internacional
    """
    __tablename__ = "stocks"

    # ==================== IDENTIFICAÇÃO ====================
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    codigo = Column(String(10), unique=True, nullable=False, index=True)  # PETR4, VALE3
    nome = Column(String(200), nullable=False, index=True)
    nome_completo = Column(String(500))
    
    # ==================== CLASSIFICAÇÃO SETORIAL ====================
    setor = Column(String(100), nullable=False, index=True)
    subsetor = Column(String(100))
    segmento = Column(String(100))
    industria = Column(String(100))  # Padronizado!
    
    # ==================== INFORMAÇÕES CORPORATIVAS ====================
    cnpj = Column(String(20), unique=True)
    website = Column(String(300))
    descricao = Column(Text)
    ceo = Column(String(150))
    funcionarios = Column(Integer)
    ano_fundacao = Column(SmallInteger)
    sede_cidade = Column(String(100))
    sede_estado = Column(String(50))
    
    # ==================== STATUS E LISTAGEM ====================
    status = Column(ENUM(StockStatusEnum), default=StockStatusEnum.ACTIVE, nullable=False, index=True)
    listagem_b3 = Column(String(50))  # Novo Mercado, Nível 1, etc.
    tipo_acao = Column(String(10))    # ON, PN, UNT
    
    # ==================== DADOS DE MERCADO ====================
    # Preços (DECIMAL para precisão financeira)
    current_price = Column(Numeric(12, 2), nullable=False)  # vs preco_atual
    previous_close = Column(Numeric(12, 2))
    day_high = Column(Numeric(12, 2))
    day_low = Column(Numeric(12, 2))
    week_52_high = Column(Numeric(12, 2))
    week_52_low = Column(Numeric(12, 2))
    
    # Volume e capitalização
    volume_medio_30d = Column(BigInteger)  # vs volume_medio
    volume_atual = Column(BigInteger)
    market_cap = Column(BigInteger, index=True)  # Market Cap em centavos
    enterprise_value = Column(BigInteger)
    shares_outstanding = Column(BigInteger)
    free_float_percent = Column(Numeric(5, 2))
    
    # ==================== MÉTRICAS FUNDAMENTALISTAS ====================
    # Valuation (nomes padronizados internacionalmente)
    pe_ratio = Column(Numeric(8, 2), index=True)           # vs p_l
    pb_ratio = Column(Numeric(8, 2), index=True)           # vs p_vp  
    ps_ratio = Column(Numeric(8, 2))                       # Price/Sales
    ev_ebitda = Column(Numeric(8, 2))                      # Enterprise Value/EBITDA
    ev_revenue = Column(Numeric(8, 2))                     # Enterprise Value/Revenue
    peg_ratio = Column(Numeric(8, 2))                      # PE/Growth
    
    # Rentabilidade
    roe = Column(Numeric(5, 2), index=True)                # Return on Equity
    roa = Column(Numeric(5, 2))                            # Return on Assets  
    roic = Column(Numeric(5, 2), index=True)               # Return on Invested Capital
    gross_margin = Column(Numeric(5, 2))                   # Margem Bruta
    operating_margin = Column(Numeric(5, 2))               # Margem Operacional
    net_margin = Column(Numeric(5, 2))                     # vs margem_liquida
    ebitda_margin = Column(Numeric(5, 2))                  # Margem EBITDA
    
    # Endividamento
    debt_to_equity = Column(Numeric(8, 2), index=True)     # vs divida_liquida_ebitda
    debt_to_ebitda = Column(Numeric(8, 2))
    current_ratio = Column(Numeric(5, 2))                  # Liquidez Corrente
    quick_ratio = Column(Numeric(5, 2))                    # Liquidez Seca
    interest_coverage = Column(Numeric(8, 2))              # Cobertura de Juros
    
    # Eficiência
    asset_turnover = Column(Numeric(5, 2))                 # Giro de Ativos
    inventory_turnover = Column(Numeric(5, 2))             # Giro de Estoque
    receivables_turnover = Column(Numeric(5, 2))           # Giro de Recebíveis
    
    # ==================== DADOS FINANCEIROS (BigInteger para valores grandes) ====================
    # Receitas e Lucros (em centavos para precisão)
    revenue_ttm = Column(BigInteger)                        # Receita últimos 12 meses
    revenue_annual = Column(BigInteger)                     # Receita anual
    gross_profit_ttm = Column(BigInteger)                   # Lucro Bruto TTM
    operating_income_ttm = Column(BigInteger)               # Lucro Operacional TTM
    net_income_ttm = Column(BigInteger)                     # Lucro Líquido TTM
    ebitda_ttm = Column(BigInteger)                         # EBITDA TTM
    
    # Balanço Patrimonial
    total_assets = Column(BigInteger)                       # Ativo Total
    total_equity = Column(BigInteger)                       # Patrimônio Líquido
    total_debt = Column(BigInteger)                         # Dívida Total
    net_debt = Column(BigInteger)                           # Dívida Líquida
    cash_and_equivalents = Column(BigInteger)               # Caixa e Equivalentes
    working_capital = Column(BigInteger)                    # Capital de Giro
    
    # ==================== CRESCIMENTO ====================
    revenue_growth_yoy = Column(Numeric(5, 2))             # Crescimento Receita YoY
    revenue_growth_3y = Column(Numeric(5, 2))              # Crescimento Receita 3 anos
    earnings_growth_yoy = Column(Numeric(5, 2))            # Crescimento Lucro YoY
    earnings_growth_3y = Column(Numeric(5, 2))             # Crescimento Lucro 3 anos
    book_value_growth_3y = Column(Numeric(5, 2))           # Crescimento Patrimônio 3 anos
    
    # ==================== SCORES E RANKINGS ====================
    fundamental_score = Column(Numeric(5, 2), index=True)  # Score geral 0-100
    valuation_score = Column(Numeric(5, 2))                # Score de valuation
    profitability_score = Column(Numeric(5, 2))            # Score de rentabilidade  
    growth_score = Column(Numeric(5, 2))                   # Score de crescimento
    financial_health_score = Column(Numeric(5, 2))         # Score de saúde financeira
    
    # Rankings
    overall_rank = Column(Integer, index=True)             # Ranking geral
    sector_rank = Column(Integer, index=True)              # Ranking no setor
    market_cap_rank = Column(Integer)                      # Ranking por tamanho
    
    # ==================== QUALIDADE E METADADOS ====================
    data_quality = Column(ENUM(DataQualityEnum), default=DataQualityEnum.MEDIUM, nullable=False)
    data_completeness = Column(Numeric(4, 2))              # Percentual de completude 0-100
    confidence_level = Column(Numeric(4, 2))               # Nível de confiança 0-100
    last_analysis_date = Column(DateTime(timezone=True))   # Última análise
    
    # ==================== TIMESTAMPS PADRONIZADOS ====================
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_price_update = Column(DateTime(timezone=True))    # vs ultima_atualizacao_preco
    last_fundamentals_update = Column(DateTime(timezone=True))  # vs ultima_atualizacao_fundamentals
    
    # ==================== DADOS ADICIONAIS (JSONB para flexibilidade) ====================
    yfinance_data = Column(JSONB)                          # Dados brutos do YFinance
    additional_metrics = Column(JSONB)                      # Métricas extras
    analyst_estimates = Column(JSONB)                       # Estimativas de analistas
    esg_scores = Column(JSONB)                             # Scores ESG
    
    # ==================== RELACIONAMENTOS ====================
    recommendations = relationship("Recommendation", back_populates="stock", cascade="all, delete-orphan")
    fundamental_analyses = relationship("FundamentalAnalysis", back_populates="stock", cascade="all, delete-orphan")
    market_data_points = relationship("MarketData", back_populates="stock", cascade="all, delete-orphan")
    
    # ==================== ÍNDICES OTIMIZADOS POSTGRESQL ====================
    __table_args__ = (
        # Índices compostos para queries frequentes
        Index('idx_stock_setor_status', 'setor', 'status'),
        Index('idx_stock_market_cap_score', 'market_cap', 'fundamental_score'),
        Index('idx_stock_pe_pb', 'pe_ratio', 'pb_ratio'),
        Index('idx_stock_roe_roic', 'roe', 'roic'),
        Index('idx_stock_sector_rank', 'setor', 'sector_rank'),
        Index('idx_stock_updated', 'updated_at'),
        Index('idx_stock_quality', 'data_quality', 'data_completeness'),
        
        # Índices para texto (PostgreSQL specific)
        Index('idx_stock_nome_gin', 'nome', postgresql_using='gin', postgresql_ops={'nome': 'gin_trgm_ops'}),
        
        # Constraints de validação
        CheckConstraint('fundamental_score >= 0 AND fundamental_score <= 100', 
                       name='check_fundamental_score_range'),
        CheckConstraint('data_completeness >= 0 AND data_completeness <= 100', 
                       name='check_data_completeness_range'),
        CheckConstraint('current_price > 0', name='check_positive_price'),
        CheckConstraint('market_cap >= 0', name='check_non_negative_market_cap'),
        
        # Constraint único para código ativo
        UniqueConstraint('codigo', name='unique_codigo'),
    )

    def __repr__(self):
        return f"<Stock(codigo='{self.codigo}', nome='{self.nome}', score={self.fundamental_score})>"

    def to_dict(self) -> Dict[str, Any]:
        """Converte o modelo para dicionário com compatibilidade"""
        return {
            'id': str(self.id),
            'codigo': self.codigo,
            'nome': self.nome,
            'setor': self.setor,
            'current_price': float(self.current_price) if self.current_price else None,
            'market_cap': self.market_cap,
            
            # Campos de compatibilidade (mapeamento reverso)
            'preco_atual': float(self.current_price) if self.current_price else None,
            'p_l': float(self.pe_ratio) if self.pe_ratio else None,
            'p_vp': float(self.pb_ratio) if self.pb_ratio else None,
            'margem_liquida': float(self.net_margin) if self.net_margin else None,
            
            # Novos campos padronizados
            'pe_ratio': float(self.pe_ratio) if self.pe_ratio else None,
            'pb_ratio': float(self.pb_ratio) if self.pb_ratio else None,
            'roe': float(self.roe) if self.roe else None,
            'roa': float(self.roa) if self.roa else None,
            'fundamental_score': float(self.fundamental_score) if self.fundamental_score else None,
            'data_quality': self.data_quality.value if self.data_quality else None,
            'status': self.status.value if self.status else None,
            
            # Timestamps
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


# ==================== RECOMENDAÇÕES OTIMIZADAS ====================
class Recommendation(Base):
    """Modelo para recomendações - OTIMIZADO POSTGRESQL"""
    __tablename__ = "recommendations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    stock_id = Column(UUID(as_uuid=True), ForeignKey("stocks.id"), nullable=False, index=True)
    
    # Dados da análise
    analysis_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    recommendation_type = Column(ENUM(RecommendationEnum), nullable=False, index=True)
    
    # Scores detalhados
    fundamental_score = Column(Numeric(5, 2), nullable=False)
    technical_score = Column(Numeric(5, 2))
    macro_score = Column(Numeric(5, 2))
    composite_score = Column(Numeric(5, 2), nullable=False, index=True)
    
    # Preços e alvos
    target_price = Column(Numeric(12, 2))
    entry_price = Column(Numeric(12, 2))
    stop_loss = Column(Numeric(12, 2))
    upside_potential = Column(Numeric(5, 2))  # Percentual de upside
    
    # Análise e contexto
    justificativa = Column(Text, nullable=False)
    risk_factors = Column(Text)
    catalysts = Column(Text)
    time_horizon_days = Column(SmallInteger, default=30)
    
    # Status e controle
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    confidence_level = Column(Numeric(4, 2))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True))
    reviewed_at = Column(DateTime(timezone=True))
    
    # Metadados
    agent_version = Column(String(20))
    analysis_context = Column(JSONB)
    
    # Relacionamento
    stock = relationship("Stock", back_populates="recommendations")
    
    __table_args__ = (
        Index('idx_recommendation_stock_date', 'stock_id', 'analysis_date'),
        Index('idx_recommendation_type_score', 'recommendation_type', 'composite_score'),
        Index('idx_recommendation_active', 'is_active', 'analysis_date'),
        CheckConstraint('composite_score >= 0 AND composite_score <= 100', 
                       name='check_composite_score_range'),
        CheckConstraint('confidence_level >= 0 AND confidence_level <= 100', 
                       name='check_confidence_range'),
    )


# ==================== ANÁLISES FUNDAMENTALISTAS ====================
class FundamentalAnalysis(Base):
    """Análises fundamentalistas detalhadas - OTIMIZADO POSTGRESQL"""
    __tablename__ = "fundamental_analyses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    stock_id = Column(UUID(as_uuid=True), ForeignKey("stocks.id"), nullable=False, index=True)
    analysis_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Scores categorizados (0-100)
    valuation_score = Column(Numeric(5, 2), nullable=False)
    profitability_score = Column(Numeric(5, 2), nullable=False)
    growth_score = Column(Numeric(5, 2), nullable=False)
    financial_health_score = Column(Numeric(5, 2), nullable=False)
    dividend_score = Column(Numeric(5, 2))
    management_score = Column(Numeric(5, 2))
    
    # Score consolidado
    composite_score = Column(Numeric(5, 2), nullable=False, index=True)
    
    # Rankings comparativos
    sector_rank = Column(Integer)
    sector_percentile = Column(Numeric(5, 2))
    market_rank = Column(Integer)
    
    # Metadados da análise
    analysis_method = Column(String(50))  # 'automated', 'manual', 'hybrid'
    data_sources = Column(JSONB)          # Fontes dos dados utilizados
    calculation_details = Column(JSONB)   # Detalhes dos cálculos
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relacionamento
    stock = relationship("Stock", back_populates="fundamental_analyses")
    
    __table_args__ = (
        Index('idx_fundamental_stock_date', 'stock_id', 'analysis_date'),
        Index('idx_fundamental_score', 'composite_score'),
        Index('idx_fundamental_sector_rank', 'sector_rank'),
    )


# ==================== DADOS DE MERCADO ====================
class MarketData(Base):
    """Dados de mercado históricos - OTIMIZADO POSTGRESQL"""
    __tablename__ = "market_data"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    stock_id = Column(UUID(as_uuid=True), ForeignKey("stocks.id"), nullable=False, index=True)
    date = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Preços OHLCV
    open_price = Column(Numeric(12, 2), nullable=False)
    high_price = Column(Numeric(12, 2), nullable=False)
    low_price = Column(Numeric(12, 2), nullable=False)
    close_price = Column(Numeric(12, 2), nullable=False)
    adjusted_close = Column(Numeric(12, 2), nullable=False)
    volume = Column(BigInteger, nullable=False)
    
    # Dados adicionais
    dividend_amount = Column(Numeric(8, 4))
    split_ratio = Column(Numeric(8, 4))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relacionamento
    stock = relationship("Stock", back_populates="market_data_points")
    
    __table_args__ = (
        Index('idx_market_data_stock_date', 'stock_id', 'date'),
        Index('idx_market_data_date', 'date'),
        UniqueConstraint('stock_id', 'date', name='unique_stock_date'),
    )


# ==================== SESSÕES DOS AGENTES ====================
class AgentSession(Base):
    """Sessões dos agentes - OTIMIZADO POSTGRESQL"""
    __tablename__ = "agent_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    session_id = Column(String(100), unique=True, nullable=False, index=True)
    
    # Informações do agente
    agent_name = Column(String(100), nullable=False, index=True)
    agent_version = Column(String(20), nullable=False)
    
    # Status da execução
    status = Column(String(20), nullable=False, index=True)  # running, completed, failed
    
    # Dados da sessão
    input_data = Column(JSONB)
    output_data = Column(JSONB)
    error_message = Column(Text)
    
    # Métricas de performance
    execution_time_seconds = Column(Numeric(8, 2))
    stocks_processed = Column(Integer, default=0)
    memory_usage_mb = Column(Numeric(8, 2))
    
    # Configuração utilizada
    config_snapshot = Column(JSONB)
    
    # Timestamps
    started_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    finished_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    __table_args__ = (
        Index('idx_agent_session_name_status', 'agent_name', 'status'),
        Index('idx_agent_session_started', 'started_at'),
        CheckConstraint('execution_time_seconds >= 0', name='check_positive_execution_time'),
    )