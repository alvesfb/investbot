# database/models_english.py
"""
Modelos SQLAlchemy PostgreSQL - NOMENCLATURA 100% INGLÊS
Sistema de Recomendações de Investimentos - Schema Internacional
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
    """Data quality levels"""
    EXCELLENT = "excellent"  # >95% fields filled
    GOOD = "good"           # 85-95% fields filled
    MEDIUM = "medium"       # 70-85% fields filled
    POOR = "poor"          # 50-70% fields filled
    CRITICAL = "critical"   # <50% fields filled


class StockStatusEnum(PyEnum):
    """Stock status"""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DELISTED = "delisted"
    UNDER_REVIEW = "under_review"


class RecommendationEnum(PyEnum):
    """Recommendation types"""
    STRONG_BUY = "strong_buy"    # 90-100
    BUY = "buy"                  # 70-89
    HOLD = "hold"                # 40-69
    SELL = "sell"                # 20-39
    STRONG_SELL = "strong_sell"  # 0-19


# ==================== MAIN STOCK MODEL - 100% ENGLISH ====================
class Stock(Base):
    """
    Stock model - 100% ENGLISH NOMENCLATURE
    Direct mapping from YFinance API fields
    """
    __tablename__ = "stocks"

    # ==================== IDENTIFICATION ====================
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    symbol = Column(String(10), unique=True, nullable=False, index=True)  # PETR4, VALE3 (was: codigo)
    name = Column(String(200), nullable=False, index=True)                # Company name (was: nome)
    long_name = Column(String(500))                                       # Full company name (was: nome_completo)
    
    # ==================== SECTOR CLASSIFICATION ====================
    sector = Column(String(100), nullable=False, index=True)              # Main sector (was: setor)
    industry = Column(String(100))                                        # Industry (was: industria)
    sub_industry = Column(String(100))                                    # Sub-industry (was: subsetor)
    segment = Column(String(100))                                         # Market segment (was: segmento)
    
    # ==================== CORPORATE INFO ====================
    tax_id = Column(String(20), unique=True)                             # CNPJ (was: cnpj)
    website = Column(String(300))                                         # Company website
    description = Column(Text)                                            # Business description (was: descricao)
    ceo = Column(String(150))                                             # Chief Executive Officer
    employees = Column(Integer)                                           # Number of employees (was: funcionarios)
    founded_year = Column(SmallInteger)                                   # Foundation year (was: ano_fundacao)
    headquarters_city = Column(String(100))                              # HQ city (was: sede_cidade)
    headquarters_state = Column(String(50))                              # HQ state (was: sede_estado)
    
    # ==================== STATUS AND LISTING ====================
    status = Column(ENUM(StockStatusEnum), default=StockStatusEnum.ACTIVE, nullable=False, index=True)
    listing_segment = Column(String(50))                                  # B3 listing (was: listagem_b3)
    share_type = Column(String(10))                                       # ON, PN, UNT (was: tipo_acao)
    
    # ==================== MARKET DATA ====================
    # Prices (DECIMAL for financial precision)
    current_price = Column(Numeric(12, 2), nullable=False)               # Current stock price
    previous_close = Column(Numeric(12, 2))                              # Previous close price
    day_high = Column(Numeric(12, 2))                                    # Day high price
    day_low = Column(Numeric(12, 2))                                     # Day low price
    fifty_two_week_high = Column(Numeric(12, 2))                        # 52-week high (was: week_52_high)
    fifty_two_week_low = Column(Numeric(12, 2))                         # 52-week low (was: week_52_low)
    
    # Volume and capitalization
    average_volume_30d = Column(BigInteger)                              # 30-day avg volume (was: volume_medio_30d)
    current_volume = Column(BigInteger)                                  # Current volume (was: volume_atual)
    market_cap = Column(BigInteger, index=True)                         # Market capitalization
    enterprise_value = Column(BigInteger)                               # Enterprise value
    shares_outstanding = Column(BigInteger)                             # Shares outstanding
    free_float_percent = Column(Numeric(5, 2))                         # Free float percentage
    
    # ==================== FUNDAMENTAL METRICS ====================
    # Valuation (international standard names)
    pe_ratio = Column(Numeric(8, 2), index=True)                       # Price/Earnings ratio
    pb_ratio = Column(Numeric(8, 2), index=True)                       # Price/Book ratio
    ps_ratio = Column(Numeric(8, 2))                                   # Price/Sales ratio
    ev_ebitda = Column(Numeric(8, 2))                                  # Enterprise Value/EBITDA
    ev_revenue = Column(Numeric(8, 2))                                 # Enterprise Value/Revenue
    peg_ratio = Column(Numeric(8, 2))                                  # PE/Growth ratio
    
    # Profitability
    roe = Column(Numeric(5, 2), index=True)                            # Return on Equity
    roa = Column(Numeric(5, 2))                                        # Return on Assets
    roic = Column(Numeric(5, 2), index=True)                          # Return on Invested Capital
    gross_margin = Column(Numeric(5, 2))                              # Gross margin
    operating_margin = Column(Numeric(5, 2))                          # Operating margin
    net_margin = Column(Numeric(5, 2))                                # Net margin
    ebitda_margin = Column(Numeric(5, 2))                             # EBITDA margin
    
    # Debt and liquidity
    debt_to_equity = Column(Numeric(8, 2), index=True)                # Debt to equity ratio
    debt_to_ebitda = Column(Numeric(8, 2))                            # Debt to EBITDA ratio
    current_ratio = Column(Numeric(5, 2))                             # Current ratio
    quick_ratio = Column(Numeric(5, 2))                               # Quick ratio
    interest_coverage = Column(Numeric(8, 2))                         # Interest coverage ratio
    
    # Efficiency
    asset_turnover = Column(Numeric(5, 2))                            # Asset turnover
    inventory_turnover = Column(Numeric(5, 2))                        # Inventory turnover
    receivables_turnover = Column(Numeric(5, 2))                      # Receivables turnover
    
    # ==================== FINANCIAL DATA (BigInteger for large values) ====================
    # Revenue and earnings (in cents for precision)
    revenue_ttm = Column(BigInteger)                                   # Revenue trailing twelve months
    revenue_annual = Column(BigInteger)                                # Annual revenue
    gross_profit_ttm = Column(BigInteger)                              # Gross profit TTM
    operating_income_ttm = Column(BigInteger)                          # Operating income TTM
    net_income_ttm = Column(BigInteger)                                # Net income TTM
    ebitda_ttm = Column(BigInteger)                                    # EBITDA TTM
    
    # Balance sheet
    total_assets = Column(BigInteger)                                  # Total assets
    total_equity = Column(BigInteger)                                  # Total equity
    total_debt = Column(BigInteger)                                    # Total debt
    net_debt = Column(BigInteger)                                      # Net debt
    cash_and_equivalents = Column(BigInteger)                          # Cash and cash equivalents
    working_capital = Column(BigInteger)                               # Working capital
    
    # ==================== GROWTH METRICS ====================
    revenue_growth_yoy = Column(Numeric(5, 2))                        # Revenue growth year-over-year
    revenue_growth_3y = Column(Numeric(5, 2))                         # Revenue growth 3-year average
    earnings_growth_yoy = Column(Numeric(5, 2))                       # Earnings growth year-over-year
    earnings_growth_3y = Column(Numeric(5, 2))                        # Earnings growth 3-year average
    book_value_growth_3y = Column(Numeric(5, 2))                      # Book value growth 3-year
    
    # ==================== SCORES AND RANKINGS ====================
    fundamental_score = Column(Numeric(5, 2), index=True)             # Overall fundamental score 0-100
    valuation_score = Column(Numeric(5, 2))                           # Valuation score
    profitability_score = Column(Numeric(5, 2))                       # Profitability score
    growth_score = Column(Numeric(5, 2))                              # Growth score
    financial_health_score = Column(Numeric(5, 2))                    # Financial health score
    
    # Rankings
    overall_rank = Column(Integer, index=True)                        # Overall market rank
    sector_rank = Column(Integer, index=True)                         # Sector rank
    market_cap_rank = Column(Integer)                                 # Market cap rank
    
    # ==================== DATA QUALITY AND METADATA ====================
    data_quality = Column(ENUM(DataQualityEnum), default=DataQualityEnum.MEDIUM, nullable=False)
    data_completeness = Column(Numeric(4, 2))                         # Data completeness percentage 0-100
    confidence_level = Column(Numeric(4, 2))                          # Confidence level 0-100
    last_analysis_date = Column(DateTime(timezone=True))              # Last analysis date
    
    # ==================== TIMESTAMPS ====================
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_price_update = Column(DateTime(timezone=True))               # Last price update
    last_fundamentals_update = Column(DateTime(timezone=True))        # Last fundamentals update
    
    # ==================== ADDITIONAL DATA (JSONB for flexibility) ====================
    yfinance_raw_data = Column(JSONB)                                  # Raw YFinance data
    additional_metrics = Column(JSONB)                                 # Additional metrics
    analyst_estimates = Column(JSONB)                                  # Analyst estimates
    esg_scores = Column(JSONB)                                         # ESG scores
    
    # ==================== RELATIONSHIPS ====================
    recommendations = relationship("Recommendation", back_populates="stock", cascade="all, delete-orphan")
    fundamental_analyses = relationship("FundamentalAnalysis", back_populates="stock", cascade="all, delete-orphan")
    market_data_points = relationship("MarketData", back_populates="stock", cascade="all, delete-orphan")
    
    # ==================== OPTIMIZED POSTGRESQL INDEXES ====================
    __table_args__ = (
        # Composite indexes for frequent queries
        Index('idx_stock_sector_status', 'sector', 'status'),
        Index('idx_stock_market_cap_score', 'market_cap', 'fundamental_score'),
        Index('idx_stock_pe_pb', 'pe_ratio', 'pb_ratio'),
        Index('idx_stock_roe_roic', 'roe', 'roic'),
        Index('idx_stock_sector_rank', 'sector', 'sector_rank'),
        Index('idx_stock_updated', 'updated_at'),
        Index('idx_stock_quality', 'data_quality', 'data_completeness'),
        
        # Text search indexes (PostgreSQL specific)
        Index('idx_stock_name_gin', 'name', postgresql_using='gin', postgresql_ops={'name': 'gin_trgm_ops'}),
        
        # Validation constraints
        CheckConstraint('fundamental_score >= 0 AND fundamental_score <= 100', 
                       name='check_fundamental_score_range'),
        CheckConstraint('data_completeness >= 0 AND data_completeness <= 100', 
                       name='check_data_completeness_range'),
        CheckConstraint('current_price > 0', name='check_positive_price'),
        CheckConstraint('market_cap >= 0', name='check_non_negative_market_cap'),
        
        # Unique constraint
        UniqueConstraint('symbol', name='unique_symbol'),
    )

    def __repr__(self):
        return f"<Stock(symbol='{self.symbol}', name='{self.name}', score={self.fundamental_score})>"

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary with backwards compatibility"""
        return {
            'id': str(self.id),
            'symbol': self.symbol,
            'name': self.name,
            'sector': self.sector,
            'current_price': float(self.current_price) if self.current_price else None,
            'market_cap': self.market_cap,
            'pe_ratio': float(self.pe_ratio) if self.pe_ratio else None,
            'pb_ratio': float(self.pb_ratio) if self.pb_ratio else None,
            'roe': float(self.roe) if self.roe else None,
            'roa': float(self.roa) if self.roa else None,
            'fundamental_score': float(self.fundamental_score) if self.fundamental_score else None,
            'data_quality': self.data_quality.value if self.data_quality else None,
            'status': self.status.value if self.status else None,
            
            # BACKWARDS COMPATIBILITY - Legacy field mapping
            'codigo': self.symbol,           # symbol -> codigo
            'nome': self.name,               # name -> nome
            'setor': self.sector,            # sector -> setor
            'preco_atual': float(self.current_price) if self.current_price else None,  # current_price -> preco_atual
            'p_l': float(self.pe_ratio) if self.pe_ratio else None,                     # pe_ratio -> p_l
            'p_vp': float(self.pb_ratio) if self.pb_ratio else None,                    # pb_ratio -> p_vp
            'margem_liquida': float(self.net_margin) if self.net_margin else None,     # net_margin -> margem_liquida
            
            # Timestamps
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def from_yfinance_data(self, yf_data: Dict[str, Any]) -> 'Stock':
        """Create Stock from YFinance data - DIRECT MAPPING"""
        # Direct field mapping from YFinance
        self.symbol = yf_data.get('symbol', '').upper()
        self.name = yf_data.get('shortName', yf_data.get('longName', ''))
        self.long_name = yf_data.get('longName')
        self.sector = yf_data.get('sector', 'Unknown')
        self.industry = yf_data.get('industry')
        self.website = yf_data.get('website')
        
        # Market data - direct mapping
        self.current_price = yf_data.get('currentPrice', yf_data.get('regularMarketPrice'))
        self.previous_close = yf_data.get('previousClose')
        self.day_high = yf_data.get('dayHigh', yf_data.get('regularMarketDayHigh'))
        self.day_low = yf_data.get('dayLow', yf_data.get('regularMarketDayLow'))
        self.fifty_two_week_high = yf_data.get('fiftyTwoWeekHigh')
        self.fifty_two_week_low = yf_data.get('fiftyTwoWeekLow')
        
        # Volume and cap
        self.current_volume = yf_data.get('volume', yf_data.get('regularMarketVolume'))
        self.average_volume_30d = yf_data.get('averageVolume')
        self.market_cap = yf_data.get('marketCap')
        self.enterprise_value = yf_data.get('enterpriseValue')
        self.shares_outstanding = yf_data.get('sharesOutstanding')
        
        # Fundamental ratios - direct mapping
        self.pe_ratio = yf_data.get('trailingPE', yf_data.get('forwardPE'))
        self.pb_ratio = yf_data.get('priceToBook')
        self.ps_ratio = yf_data.get('priceToSalesTrailing12Months')
        self.ev_ebitda = yf_data.get('enterpriseToEbitda')
        self.ev_revenue = yf_data.get('enterpriseToRevenue')
        self.peg_ratio = yf_data.get('pegRatio')
        
        # Profitability
        self.roe = yf_data.get('returnOnEquity')
        self.roa = yf_data.get('returnOnAssets')
        self.gross_margin = yf_data.get('grossMargins')
        self.operating_margin = yf_data.get('operatingMargins')
        self.net_margin = yf_data.get('profitMargins')
        self.ebitda_margin = yf_data.get('ebitdaMargins')
        
        # Debt ratios
        self.debt_to_equity = yf_data.get('debtToEquity')
        self.current_ratio = yf_data.get('currentRatio')
        self.quick_ratio = yf_data.get('quickRatio')
        
        # Financial data
        self.revenue_ttm = yf_data.get('totalRevenue')
        self.net_income_ttm = yf_data.get('netIncomeToCommon')
        self.ebitda_ttm = yf_data.get('ebitda')
        self.total_assets = yf_data.get('totalAssets')
        self.total_equity = yf_data.get('totalStockholderEquity')
        self.total_debt = yf_data.get('totalDebt')
        self.cash_and_equivalents = yf_data.get('totalCash')
        
        # Growth
        self.revenue_growth_yoy = yf_data.get('revenueGrowth')
        self.earnings_growth_yoy = yf_data.get('earningsGrowth')
        
        # Store raw data
        self.yfinance_raw_data = yf_data
        
        # Set defaults
        self.status = StockStatusEnum.ACTIVE
        self.data_quality = DataQualityEnum.GOOD
        self.last_price_update = datetime.now()
        
        return self


# ==================== OTHER MODELS (Updated field names) ====================
class Recommendation(Base):
    """Recommendation model with English field names"""
    __tablename__ = "recommendations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    stock_id = Column(UUID(as_uuid=True), ForeignKey("stocks.id"), nullable=False, index=True)
    
    # Analysis data
    analysis_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    recommendation_type = Column(ENUM(RecommendationEnum), nullable=False, index=True)
    
    # Detailed scores
    fundamental_score = Column(Numeric(5, 2), nullable=False)
    technical_score = Column(Numeric(5, 2))
    macro_score = Column(Numeric(5, 2))
    composite_score = Column(Numeric(5, 2), nullable=False, index=True)
    
    # Prices and targets
    target_price = Column(Numeric(12, 2))
    entry_price = Column(Numeric(12, 2))
    stop_loss = Column(Numeric(12, 2))
    upside_potential = Column(Numeric(5, 2))  # Percentage upside
    
    # Analysis and context
    rationale = Column(Text, nullable=False)               # was: justificativa
    risk_factors = Column(Text)
    catalysts = Column(Text)
    time_horizon_days = Column(SmallInteger, default=30)
    
    # Status and control
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    confidence_level = Column(Numeric(4, 2))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True))
    reviewed_at = Column(DateTime(timezone=True))
    
    # Metadata
    agent_version = Column(String(20))
    analysis_context = Column(JSONB)
    
    # Relationship
    stock = relationship("Stock", back_populates="recommendations")
    
    __table_args__ = (
        Index('idx_recommendation_stock_date', 'stock_id', 'analysis_date'),
        Index('idx_recommendation_type_score', 'recommendation_type', 'composite_score'),
        Index('idx_recommendation_active', 'is_active', 'analysis_date'),
    )


class FundamentalAnalysis(Base):
    """Fundamental analysis with English field names"""
    __tablename__ = "fundamental_analyses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    stock_id = Column(UUID(as_uuid=True), ForeignKey("stocks.id"), nullable=False, index=True)
    analysis_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Categorized scores (0-100)
    valuation_score = Column(Numeric(5, 2), nullable=False)
    profitability_score = Column(Numeric(5, 2), nullable=False)
    growth_score = Column(Numeric(5, 2), nullable=False)
    financial_health_score = Column(Numeric(5, 2), nullable=False)
    dividend_score = Column(Numeric(5, 2))
    management_score = Column(Numeric(5, 2))
    
    # Consolidated score
    composite_score = Column(Numeric(5, 2), nullable=False, index=True)
    
    # Comparative rankings
    sector_rank = Column(Integer)
    sector_percentile = Column(Numeric(5, 2))
    market_rank = Column(Integer)
    
    # Analysis metadata
    analysis_method = Column(String(50))  # 'automated', 'manual', 'hybrid'
    data_sources = Column(JSONB)          # Data sources used
    calculation_details = Column(JSONB)   # Calculation details
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationship
    stock = relationship("Stock", back_populates="fundamental_analyses")


class MarketData(Base):
    """Market data with English field names"""
    __tablename__ = "market_data"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    stock_id = Column(UUID(as_uuid=True), ForeignKey("stocks.id"), nullable=False, index=True)
    date = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # OHLCV prices
    open_price = Column(Numeric(12, 2), nullable=False)
    high_price = Column(Numeric(12, 2), nullable=False)
    low_price = Column(Numeric(12, 2), nullable=False)
    close_price = Column(Numeric(12, 2), nullable=False)
    adjusted_close = Column(Numeric(12, 2), nullable=False)
    volume = Column(BigInteger, nullable=False)
    
    # Additional data
    dividend_amount = Column(Numeric(8, 4))
    split_ratio = Column(Numeric(8, 4))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationship
    stock = relationship("Stock", back_populates="market_data_points")
    
    __table_args__ = (
        Index('idx_market_data_stock_date', 'stock_id', 'date'),
        UniqueConstraint('stock_id', 'date', name='unique_stock_date'),
    )


class AgentSession(Base):
    """Agent sessions with English field names"""
    __tablename__ = "agent_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    session_id = Column(String(100), unique=True, nullable=False, index=True)
    
    # Agent information
    agent_name = Column(String(100), nullable=False, index=True)
    agent_version = Column(String(20), nullable=False)
    
    # Execution status
    status = Column(String(20), nullable=False, index=True)  # running, completed, failed
    
    # Session data
    input_data = Column(JSONB)
    output_data = Column(JSONB)
    error_message = Column(Text)
    
    # Performance metrics
    execution_time_seconds = Column(Numeric(8, 2))
    stocks_processed = Column(Integer, default=0)
    memory_usage_mb = Column(Numeric(8, 2))
    
    # Configuration used
    config_snapshot = Column(JSONB)
    
    # Timestamps
    started_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    finished_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
