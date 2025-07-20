# database/models_new.py - NOMENCLATURA 100% INGLÊS
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

# ENUMs
class DataQualityEnum(PyEnum):
    EXCELLENT = "excellent"
    GOOD = "good"
    MEDIUM = "medium"
    POOR = "poor"
    CRITICAL = "critical"

class StockStatusEnum(PyEnum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DELISTED = "delisted"
    UNDER_REVIEW = "under_review"

class RecommendationEnum(PyEnum):
    STRONG_BUY = "strong_buy"
    BUY = "buy"
    HOLD = "hold"
    SELL = "sell"
    STRONG_SELL = "strong_sell"

# MODELO PRINCIPAL - 100% INGLÊS
class Stock(Base):
    __tablename__ = "stocks"

    # Identificação
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    symbol = Column(String(10), unique=True, nullable=False, index=True)  # PETR4
    name = Column(String(200), nullable=False, index=True)                # Company name
    long_name = Column(String(500))                                       # Full name
    
    # Setor
    sector = Column(String(100), nullable=False, index=True)              # Energy
    industry = Column(String(100))                                        # Oil & Gas
    sub_industry = Column(String(100))
    segment = Column(String(100))
    
    # Dados corporativos
    tax_id = Column(String(20), unique=True)                             # CNPJ
    website = Column(String(300))
    description = Column(Text)
    ceo = Column(String(150))
    employees = Column(Integer)
    founded_year = Column(SmallInteger)
    headquarters_city = Column(String(100))
    headquarters_state = Column(String(50))
    
    # Status
    status = Column(ENUM(StockStatusEnum), default=StockStatusEnum.ACTIVE, nullable=False, index=True)
    listing_segment = Column(String(50))                                  # Novo Mercado
    share_type = Column(String(10))                                       # ON, PN
    
    # Preços
    current_price = Column(Numeric(12, 2), nullable=False)               # Preço atual
    previous_close = Column(Numeric(12, 2))
    day_high = Column(Numeric(12, 2))
    day_low = Column(Numeric(12, 2))
    fifty_two_week_high = Column(Numeric(12, 2))
    fifty_two_week_low = Column(Numeric(12, 2))
    
    # Volume
    current_volume = Column(BigInteger)
    average_volume_30d = Column(BigInteger)                              # Volume médio
    market_cap = Column(BigInteger, index=True)
    enterprise_value = Column(BigInteger)
    shares_outstanding = Column(BigInteger)
    free_float_percent = Column(Numeric(5, 2))
    
    # Indicadores fundamentalistas
    pe_ratio = Column(Numeric(8, 2), index=True)                        # P/L
    pb_ratio = Column(Numeric(8, 2), index=True)                        # P/VP
    ps_ratio = Column(Numeric(8, 2))                                    # P/S
    ev_ebitda = Column(Numeric(8, 2))
    ev_revenue = Column(Numeric(8, 2))
    peg_ratio = Column(Numeric(8, 2))
    
    # Rentabilidade
    roe = Column(Numeric(5, 2), index=True)                             # ROE
    roa = Column(Numeric(5, 2))                                         # ROA
    roic = Column(Numeric(5, 2), index=True)                            # ROIC
    gross_margin = Column(Numeric(5, 2))                                # Margem bruta
    operating_margin = Column(Numeric(5, 2))                            # Margem operacional
    net_margin = Column(Numeric(5, 2))                                  # Margem líquida
    ebitda_margin = Column(Numeric(5, 2))
    
    # Endividamento
    debt_to_equity = Column(Numeric(8, 2), index=True)
    debt_to_ebitda = Column(Numeric(8, 2))
    current_ratio = Column(Numeric(5, 2))
    quick_ratio = Column(Numeric(5, 2))
    interest_coverage = Column(Numeric(8, 2))
    
    # Eficiência
    asset_turnover = Column(Numeric(5, 2))
    inventory_turnover = Column(Numeric(5, 2))
    receivables_turnover = Column(Numeric(5, 2))
    
    # Dados financeiros
    revenue_ttm = Column(BigInteger)                                     # Receita TTM
    revenue_annual = Column(BigInteger)
    gross_profit_ttm = Column(BigInteger)
    operating_income_ttm = Column(BigInteger)
    net_income_ttm = Column(BigInteger)
    ebitda_ttm = Column(BigInteger)
    
    # Balanço
    total_assets = Column(BigInteger)
    total_equity = Column(BigInteger)
    total_debt = Column(BigInteger)
    net_debt = Column(BigInteger)
    cash_and_equivalents = Column(BigInteger)
    working_capital = Column(BigInteger)
    
    # Crescimento
    revenue_growth_yoy = Column(Numeric(5, 2))
    revenue_growth_3y = Column(Numeric(5, 2))
    earnings_growth_yoy = Column(Numeric(5, 2))
    earnings_growth_3y = Column(Numeric(5, 2))
    book_value_growth_3y = Column(Numeric(5, 2))
    
    # Scores
    fundamental_score = Column(Numeric(5, 2), index=True)
    valuation_score = Column(Numeric(5, 2))
    profitability_score = Column(Numeric(5, 2))
    growth_score = Column(Numeric(5, 2))
    financial_health_score = Column(Numeric(5, 2))
    
    # Rankings
    overall_rank = Column(Integer, index=True)
    sector_rank = Column(Integer, index=True)
    market_cap_rank = Column(Integer)
    
    # Qualidade
    data_quality = Column(ENUM(DataQualityEnum), default=DataQualityEnum.MEDIUM, nullable=False)
    data_completeness = Column(Numeric(4, 2))
    confidence_level = Column(Numeric(4, 2))
    last_analysis_date = Column(DateTime(timezone=True))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_price_update = Column(DateTime(timezone=True))
    last_fundamentals_update = Column(DateTime(timezone=True))
    
    # Dados adicionais
    yfinance_raw_data = Column(JSONB)
    additional_metrics = Column(JSONB)
    analyst_estimates = Column(JSONB)
    esg_scores = Column(JSONB)
    
    # Relacionamentos
    recommendations = relationship("Recommendation", back_populates="stock", cascade="all, delete-orphan")
    fundamental_analyses = relationship("FundamentalAnalysis", back_populates="stock", cascade="all, delete-orphan")
    market_data_points = relationship("MarketData", back_populates="stock", cascade="all, delete-orphan")
    
    # Índices
    __table_args__ = (
        Index('idx_stock_sector_status', 'sector', 'status'),
        Index('idx_stock_market_cap_score', 'market_cap', 'fundamental_score'),
        Index('idx_stock_pe_pb', 'pe_ratio', 'pb_ratio'),
        Index('idx_stock_roe_roic', 'roe', 'roic'),
        Index('idx_stock_updated', 'updated_at'),
        CheckConstraint('fundamental_score >= 0 AND fundamental_score <= 100', name='check_fundamental_score_range'),
        CheckConstraint('current_price > 0', name='check_positive_price'),
        UniqueConstraint('symbol', name='unique_symbol'),
    )

    def __repr__(self):
        return f"<Stock(symbol='{self.symbol}', name='{self.name}')>"

    def to_dict(self) -> Dict[str, Any]:
        """Converte para dict com compatibilidade português"""
        return {
            # Campos inglês (novos)
            'id': str(self.id),
            'symbol': self.symbol,
            'name': self.name,
            'sector': self.sector,
            'industry': self.industry,
            'current_price': float(self.current_price) if self.current_price else None,
            'market_cap': self.market_cap,
            'pe_ratio': float(self.pe_ratio) if self.pe_ratio else None,
            'pb_ratio': float(self.pb_ratio) if self.pb_ratio else None,
            'roe': float(self.roe) if self.roe else None,
            'roa': float(self.roa) if self.roa else None,
            'fundamental_score': float(self.fundamental_score) if self.fundamental_score else None,
            'status': self.status.value if self.status else None,
            'data_quality': self.data_quality.value if self.data_quality else None,
            
            # COMPATIBILIDADE PORTUGUÊS (mapeamento reverso)
            'codigo': self.symbol,                                                    # symbol -> codigo
            'nome': self.name,                                                        # name -> nome
            'setor': self.sector,                                                     # sector -> setor
            'preco_atual': float(self.current_price) if self.current_price else None, # current_price -> preco_atual
            'p_l': float(self.pe_ratio) if self.pe_ratio else None,                   # pe_ratio -> p_l
            'p_vp': float(self.pb_ratio) if self.pb_ratio else None,                  # pb_ratio -> p_vp
            'margem_liquida': float(self.net_margin) if self.net_margin else None,    # net_margin -> margem_liquida
            'ativo': self.status == StockStatusEnum.ACTIVE if self.status else True, # status -> ativo
            
            # Timestamps
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def from_yfinance_data(self, yf_data: Dict[str, Any]) -> 'Stock':
        """Cria Stock diretamente de dados YFinance - SEM CONVERSÃO"""
        self.symbol = yf_data.get('symbol', '').upper()
        self.name = yf_data.get('shortName', yf_data.get('longName', ''))
        self.long_name = yf_data.get('longName')
        self.sector = yf_data.get('sector', 'Unknown')
        self.industry = yf_data.get('industry')
        self.website = yf_data.get('website')
        
        # Preços - mapeamento direto
        self.current_price = yf_data.get('currentPrice', yf_data.get('regularMarketPrice'))
        self.previous_close = yf_data.get('previousClose')
        self.day_high = yf_data.get('dayHigh', yf_data.get('regularMarketDayHigh'))
        self.day_low = yf_data.get('dayLow', yf_data.get('regularMarketDayLow'))
        self.fifty_two_week_high = yf_data.get('fiftyTwoWeekHigh')
        self.fifty_two_week_low = yf_data.get('fiftyTwoWeekLow')
        
        # Volume
        self.current_volume = yf_data.get('volume', yf_data.get('regularMarketVolume'))
        self.average_volume_30d = yf_data.get('averageVolume')
        self.market_cap = yf_data.get('marketCap')
        self.enterprise_value = yf_data.get('enterpriseValue')
        self.shares_outstanding = yf_data.get('sharesOutstanding')
        
        # Indicadores - mapeamento direto
        self.pe_ratio = yf_data.get('trailingPE', yf_data.get('forwardPE'))
        self.pb_ratio = yf_data.get('priceToBook')
        self.ps_ratio = yf_data.get('priceToSalesTrailing12Months')
        self.ev_ebitda = yf_data.get('enterpriseToEbitda')
        self.ev_revenue = yf_data.get('enterpriseToRevenue')
        self.peg_ratio = yf_data.get('pegRatio')
        
        # Rentabilidade
        self.roe = yf_data.get('returnOnEquity')
        self.roa = yf_data.get('returnOnAssets')
        self.gross_margin = yf_data.get('grossMargins')
        self.operating_margin = yf_data.get('operatingMargins')
        self.net_margin = yf_data.get('profitMargins')
        self.ebitda_margin = yf_data.get('ebitdaMargins')
        
        # Endividamento
        self.debt_to_equity = yf_data.get('debtToEquity')
        self.current_ratio = yf_data.get('currentRatio')
        self.quick_ratio = yf_data.get('quickRatio')
        
        # Dados financeiros
        self.revenue_ttm = yf_data.get('totalRevenue')
        self.net_income_ttm = yf_data.get('netIncomeToCommon')
        self.ebitda_ttm = yf_data.get('ebitda')
        self.total_assets = yf_data.get('totalAssets')
        self.total_equity = yf_data.get('totalStockholderEquity')
        self.total_debt = yf_data.get('totalDebt')
        self.cash_and_equivalents = yf_data.get('totalCash')
        
        # Crescimento
        self.revenue_growth_yoy = yf_data.get('revenueGrowth')
        self.earnings_growth_yoy = yf_data.get('earningsGrowth')
        
        # Armazenar dados brutos
        self.yfinance_raw_data = yf_data
        
        # Padrões
        self.status = StockStatusEnum.ACTIVE
        self.data_quality = DataQualityEnum.GOOD
        self.last_price_update = datetime.now()
        
        return self


# OUTROS MODELOS (simplificados para foco na migração)
class Recommendation(Base):
    __tablename__ = "recommendations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    stock_id = Column(UUID(as_uuid=True), ForeignKey("stocks.id"), nullable=False, index=True)
    analysis_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    recommendation_type = Column(ENUM(RecommendationEnum), nullable=False, index=True)
    fundamental_score = Column(Numeric(5, 2), nullable=False)
    composite_score = Column(Numeric(5, 2), nullable=False, index=True)
    target_price = Column(Numeric(12, 2))
    entry_price = Column(Numeric(12, 2))
    stop_loss = Column(Numeric(12, 2))
    rationale = Column(Text, nullable=False)  # era justificativa
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    confidence_level = Column(Numeric(4, 2))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    stock = relationship("Stock", back_populates="recommendations")


class FundamentalAnalysis(Base):
    __tablename__ = "fundamental_analyses"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    stock_id = Column(UUID(as_uuid=True), ForeignKey("stocks.id"), nullable=False, index=True)
    analysis_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    valuation_score = Column(Numeric(5, 2), nullable=False)
    profitability_score = Column(Numeric(5, 2), nullable=False)
    growth_score = Column(Numeric(5, 2), nullable=False)
    financial_health_score = Column(Numeric(5, 2), nullable=False)
    composite_score = Column(Numeric(5, 2), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    stock = relationship("Stock", back_populates="fundamental_analyses")


class MarketData(Base):
    __tablename__ = "market_data"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    stock_id = Column(UUID(as_uuid=True), ForeignKey("stocks.id"), nullable=False, index=True)
    date = Column(DateTime(timezone=True), nullable=False, index=True)
    open_price = Column(Numeric(12, 2), nullable=False)
    high_price = Column(Numeric(12, 2), nullable=False)
    low_price = Column(Numeric(12, 2), nullable=False)
    close_price = Column(Numeric(12, 2), nullable=False)
    adjusted_close = Column(Numeric(12, 2), nullable=False)
    volume = Column(BigInteger, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    stock = relationship("Stock", back_populates="market_data_points")


class AgentSession(Base):
    __tablename__ = "agent_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    session_id = Column(String(100), unique=True, nullable=False, index=True)
    agent_name = Column(String(100), nullable=False, index=True)
    agent_version = Column(String(20), nullable=False)
    status = Column(String(20), nullable=False, index=True)
    input_data = Column(JSONB)
    output_data = Column(JSONB)
    execution_time_seconds = Column(Numeric(8, 2))
    started_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    finished_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
