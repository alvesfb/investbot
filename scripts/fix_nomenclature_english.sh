# scripts/fix_nomenclature_english.sh
# Correção de Nomenclatura - Schema 100% Inglês

echo "🌍 CORREÇÃO DE NOMENCLATURA - SCHEMA 100% INGLÊS"
echo "================================================"
echo "📋 Objetivo: Padronizar TODOS os campos em inglês para APIs"

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
PURPLE='\033[0;35m'
NC='\033[0m'

print_step() {
    echo -e "${BLUE}📋 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${PURPLE}ℹ️  $1${NC}"
}

# ==================== PRÉ-REQUISITOS ====================
print_step "Verificando pré-requisitos..."

# Verificar se PostgreSQL está rodando
if ! docker-compose -f docker-compose.postgresql.yml ps postgres | grep -q "Up"; then
    print_error "PostgreSQL não está rodando!"
    exit 1
fi

print_success "PostgreSQL está rodando"

# ==================== BACKUP ANTES DA CORREÇÃO ====================
print_step "Fazendo backup antes da correção de nomenclatura..."

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="./database/nomenclature_backup_${TIMESTAMP}"
mkdir -p "$BACKUP_DIR"

# Backup do banco PostgreSQL
docker exec investment-postgres pg_dump -U investment_user investment_system > "$BACKUP_DIR/pre_nomenclature_fix.sql"

# Backup dos modelos atuais
cp database/models.py "$BACKUP_DIR/models_pre_fix.py"
cp database/repositories.py "$BACKUP_DIR/repositories_pre_fix.py"

print_success "Backup criado: $BACKUP_DIR"

# ==================== CRIAR MODELO CORRIGIDO ====================
print_step "Criando modelo PostgreSQL com nomenclatura 100% inglês..."

cat > database/models_english.py << 'EOF'
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
EOF

print_success "Modelo 100% inglês criado"

# ==================== CRIAR REPOSITORIES CORRIGIDO ====================
print_step "Criando repositories com mapeamento inglês ↔ português..."

cat > database/repositories_english.py << 'EOF'
# database/repositories_english.py
"""
Repository pattern para PostgreSQL - NOMENCLATURA 100% INGLÊS
Com mapeamento automático português ↔ inglês para compatibilidade
"""
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_, func, text
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timedelta
import logging
import uuid

from database.models import (Stock, Recommendation, FundamentalAnalysis, 
                           AgentSession, MarketData, DataQualityEnum, 
                           StockStatusEnum, RecommendationEnum)
from database.connection import get_db_session

logger = logging.getLogger(__name__)


class FieldMapper:
    """Mapeamento automático entre campos português ↔ inglês"""
    
    # Mapeamento português → inglês
    PT_TO_EN = {
        'codigo': 'symbol',
        'nome': 'name',
        'nome_completo': 'long_name',
        'setor': 'sector',
        'industria': 'industry',
        'subsetor': 'sub_industry',
        'segmento': 'segment',
        'cnpj': 'tax_id',
        'descricao': 'description',
        'funcionarios': 'employees',
        'ano_fundacao': 'founded_year',
        'sede_cidade': 'headquarters_city',
        'sede_estado': 'headquarters_state',
        'listagem_b3': 'listing_segment',
        'tipo_acao': 'share_type',
        'preco_atual': 'current_price',
        'volume_medio': 'average_volume_30d',
        'volume_atual': 'current_volume',
        'p_l': 'pe_ratio',
        'p_vp': 'pb_ratio',
        'margem_liquida': 'net_margin',
        'margem_bruta': 'gross_margin',
        'margem_operacional': 'operating_margin',
        'margem_ebitda': 'ebitda_margin',
        'divida_liquida_ebitda': 'debt_to_ebitda',
        'divida_patrimonio': 'debt_to_equity',
        'liquidez_corrente': 'current_ratio',
        'liquidez_seca': 'quick_ratio',
        'giro_ativo': 'asset_turnover',
        'receita_ttm': 'revenue_ttm',
        'lucro_liquido_ttm': 'net_income_ttm',
        'ativo_total': 'total_assets',
        'patrimonio_liquido': 'total_equity',
        'divida_total': 'total_debt',
        'caixa_equivalentes': 'cash_and_equivalents',
        'crescimento_receita': 'revenue_growth_yoy',
        'crescimento_lucro': 'earnings_growth_yoy',
        'score_fundamentalista': 'fundamental_score',
        'score_valuation': 'valuation_score',
        'score_rentabilidade': 'profitability_score',
        'score_crescimento': 'growth_score',
        'score_saude_financeira': 'financial_health_score',
        'ranking_geral': 'overall_rank',
        'ranking_setor': 'sector_rank',
        'qualidade_dados': 'data_quality',
        'completude_dados': 'data_completeness',
        'nivel_confianca': 'confidence_level',
        'data_criacao': 'created_at',
        'data_atualizacao': 'updated_at',
        'ultima_atualizacao_preco': 'last_price_update',
        'ultima_atualizacao_fundamentals': 'last_fundamentals_update',
        'ativo': 'status',  # boolean → enum mapping
        'justificativa': 'rationale',
        'classificacao': 'recommendation_type',
        'data_analise': 'analysis_date',
        'data_recomendacao': 'analysis_date',
        'preco_entrada': 'entry_price',
        'ativa': 'is_active'
    }
    
    # Mapeamento inglês → português (reverso)
    EN_TO_PT = {v: k for k, v in PT_TO_EN.items()}
    
    @classmethod
    def map_to_english(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Converte campos português → inglês"""
        mapped = {}
        for key, value in data.items():
            english_key = cls.PT_TO_EN.get(key, key)
            
            # Tratamento especial para campos boolean → enum
            if key == 'ativo' and isinstance(value, bool):
                mapped['status'] = StockStatusEnum.ACTIVE if value else StockStatusEnum.SUSPENDED
            else:
                mapped[english_key] = value
                
        return mapped
    
    @classmethod
    def map_to_portuguese(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Converte campos inglês → português para compatibilidade"""
        mapped = {}
        for key, value in data.items():
            portuguese_key = cls.EN_TO_PT.get(key, key)
            
            # Tratamento especial para enum → boolean
            if key == 'status' and hasattr(value, 'value'):
                mapped['ativo'] = value == StockStatusEnum.ACTIVE
            else:
                mapped[portuguese_key] = value
                
        return mapped


class BaseRepository:
    """Classe base para repositories PostgreSQL"""

    def __init__(self, db_session: Session = None):
        self.db_session = db_session
        self.mapper = FieldMapper()

    def _get_session(self):
        """Retorna sessão do banco (injetada ou nova)"""
        if self.db_session:
            return self.db_session
        return get_db_session()


class StockRepository(BaseRepository):
    """Repository PostgreSQL para ações - 100% INGLÊS + Compatibilidade"""

    def create_stock(self, stock_data: Dict[str, Any]) -> Stock:
        """Cria ação com mapeamento automático português → inglês"""
        with self._get_session() as db:
            # Mapear campos português → inglês
            english_data = self.mapper.map_to_english(stock_data)
            
            # Verificar se já existe
            symbol = english_data.get('symbol', '').upper()
            existing = db.query(Stock).filter(Stock.symbol == symbol).first()
            
            if existing:
                logger.info(f"Stock {symbol} already exists")
                return existing
            
            # Validar e limpar dados
            cleaned_data = self._validate_and_clean_data(english_data)
            
            stock = Stock(**cleaned_data)
            db.add(stock)
            db.commit()
            db.refresh(stock)
            
            logger.info(f"Stock created: {stock.symbol}")
            return stock

    def create_stock_from_yfinance(self, yf_data: Dict[str, Any]) -> Stock:
        """Cria ação diretamente de dados YFinance (sem mapeamento)"""
        with self._get_session() as db:
            symbol = yf_data.get('symbol', '').upper()
            
            # Verificar se já existe
            existing = db.query(Stock).filter(Stock.symbol == symbol).first()
            if existing:
                return existing
            
            # Usar método direto do modelo
            stock = Stock()
            stock.from_yfinance_data(yf_data)
            
            db.add(stock)
            db.commit()
            db.refresh(stock)
            
            logger.info(f"Stock created from YFinance: {stock.symbol}")
            return stock

    def _validate_and_clean_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Valida e limpa dados antes de inserir"""
        cleaned = {}
        
        # Campos obrigatórios
        cleaned['symbol'] = data.get('symbol', '').upper()
        cleaned['name'] = data.get('name', f"Company {cleaned['symbol']}")
        cleaned['sector'] = data.get('sector', 'Unknown')
        
        # Campos opcionais com validação
        optional_fields = [
            'long_name', 'industry', 'sub_industry', 'segment', 'tax_id',
            'website', 'description', 'ceo', 'employees', 'founded_year',
            'headquarters_city', 'headquarters_state', 'listing_segment', 'share_type'
        ]
        
        for field in optional_fields:
            if field in data and data[field] is not None:
                cleaned[field] = data[field]
        
        # Campos numéricos com validação
        numeric_fields = [
            'current_price', 'previous_close', 'day_high', 'day_low',
            'fifty_two_week_high', 'fifty_two_week_low', 'current_volume',
            'average_volume_30d', 'market_cap', 'enterprise_value',
            'shares_outstanding', 'free_float_percent', 'pe_ratio', 'pb_ratio',
            'ps_ratio', 'ev_ebitda', 'ev_revenue', 'peg_ratio', 'roe', 'roa',
            'roic', 'gross_margin', 'operating_margin', 'net_margin',
            'ebitda_margin', 'debt_to_equity', 'debt_to_ebitda', 'current_ratio',
            'quick_ratio', 'interest_coverage', 'asset_turnover',
            'inventory_turnover', 'receivables_turnover', 'revenue_ttm',
            'revenue_annual', 'gross_profit_ttm', 'operating_income_ttm',
            'net_income_ttm', 'ebitda_ttm', 'total_assets', 'total_equity',
            'total_debt', 'net_debt', 'cash_and_equivalents', 'working_capital',
            'revenue_growth_yoy', 'revenue_growth_3y', 'earnings_growth_yoy',
            'earnings_growth_3y', 'book_value_growth_3y', 'fundamental_score',
            'valuation_score', 'profitability_score', 'growth_score',
            'financial_health_score', 'overall_rank', 'sector_rank',
            'market_cap_rank', 'data_completeness', 'confidence_level'
        ]
        
        for field in numeric_fields:
            if field in data and data[field] is not None:
                try:
                    cleaned[field] = float(data[field]) if data[field] != '' else None
                except (ValueError, TypeError):
                    logger.warning(f"Invalid numeric value for {field}: {data[field]}")
        
        # Enums com valores padrão
        cleaned['status'] = data.get('status', StockStatusEnum.ACTIVE)
        cleaned['data_quality'] = data.get('data_quality', DataQualityEnum.MEDIUM)
        
        # Timestamps
        if 'last_price_update' in data:
            cleaned['last_price_update'] = data['last_price_update']
        if 'last_fundamentals_update' in data:
            cleaned['last_fundamentals_update'] = data['last_fundamentals_update']
        
        return cleaned

    def get_stock_by_code(self, codigo: str) -> Optional[Stock]:
        """Busca por código (compatibilidade) - mapeia para symbol"""
        return self.get_stock_by_symbol(codigo)

    def get_stock_by_symbol(self, symbol: str) -> Optional[Stock]:
        """Busca ação por symbol"""
        with self._get_session() as db:
            return db.query(Stock).filter(
                Stock.symbol == symbol.upper()
            ).first()

    def get_all_stocks(self, active_only: bool = True) -> List[Stock]:
        """Lista todas as ações ativas"""
        with self._get_session() as db:
            query = db.query(Stock)
            
            if active_only:
                query = query.filter(Stock.status == StockStatusEnum.ACTIVE)
            
            return query.order_by(Stock.name).all()

    def get_stocks_by_sector(self, sector: str, limit: int = None) -> List[Stock]:
        """Busca ações por setor"""
        with self._get_session() as db:
            query = db.query(Stock).filter(
                Stock.sector.ilike(f"%{sector}%"),
                Stock.status == StockStatusEnum.ACTIVE
            ).order_by(desc(Stock.market_cap))
            
            if limit:
                query = query.limit(limit)
            
            return query.all()

    def get_top_stocks_by_score(self, limit: int = 20) -> List[Stock]:
        """Top ações por score fundamentalista"""
        with self._get_session() as db:
            return db.query(Stock).filter(
                Stock.fundamental_score.isnot(None),
                Stock.status == StockStatusEnum.ACTIVE
            ).order_by(
                desc(Stock.fundamental_score)
            ).limit(limit).all()

    def search_stocks(self, query: str, limit: int = 10) -> List[Stock]:
        """Busca textual com trigram similarity"""
        with self._get_session() as db:
            results = db.query(Stock).filter(
                or_(
                    Stock.symbol.ilike(f"%{query.upper()}%"),
                    Stock.name.ilike(f"%{query}%"),
                    func.similarity(Stock.name, query) > 0.3
                ),
                Stock.status == StockStatusEnum.ACTIVE
            ).order_by(
                desc(func.similarity(Stock.name, query))
            ).limit(limit).all()
            
            return results

    def bulk_update_prices(self, updates: List[Dict[str, Any]]) -> int:
        """Atualização em lote de preços - otimizada PostgreSQL"""
        with self._get_session() as db:
            updated_count = 0
            
            for update in updates:
                # Aceitar tanto 'codigo' quanto 'symbol'
                symbol = update.get('symbol') or update.get('codigo')
                if not symbol:
                    continue
                
                # Mapear campos se necessário
                price_data = self.mapper.map_to_english(update)
                
                result = db.query(Stock).filter(
                    Stock.symbol == symbol.upper()
                ).update({
                    Stock.current_price: price_data.get('current_price'),
                    Stock.current_volume: price_data.get('current_volume'),
                    Stock.last_price_update: datetime.now()
                })
                
                updated_count += result
            
            db.commit()
            logger.info(f"Prices updated: {updated_count} stocks")
            return updated_count

    def get_stocks_needing_update(self, hours_threshold: int = 6) -> List[Stock]:
        """Ações que precisam de atualização de dados"""
        with self._get_session() as db:
            cutoff_time = datetime.now() - timedelta(hours=hours_threshold)
            
            return db.query(Stock).filter(
                Stock.status == StockStatusEnum.ACTIVE,
                or_(
                    Stock.last_price_update < cutoff_time,
                    Stock.last_price_update.is_(None)
                )
            ).order_by(Stock.market_cap.desc()).all()


class RecommendationRepository(BaseRepository):
    """Repository para recomendações com mapeamento automático"""

    def create_recommendation(self, rec_data: Dict[str, Any]) -> Recommendation:
        """Cria recomendação com mapeamento português → inglês"""
        with self._get_session() as db:
            # Mapear campos
            english_data = self.mapper.map_to_english(rec_data)
            
            # Mapear classificação se necessário
            if 'classificacao' in rec_data:
                english_data['recommendation_type'] = self._map_classification(rec_data['classificacao'])
            
            recommendation = Recommendation(**english_data)
            db.add(recommendation)
            db.commit()
            db.refresh(recommendation)
            
            return recommendation

    def _map_classification(self, classificacao: str) -> RecommendationEnum:
        """Mapeia classificação português → enum"""
        mapping = {
            'COMPRA FORTE': RecommendationEnum.STRONG_BUY,
            'COMPRA': RecommendationEnum.BUY,
            'NEUTRO': RecommendationEnum.HOLD,
            'VENDA': RecommendationEnum.SELL,
            'VENDA FORTE': RecommendationEnum.STRONG_SELL
        }
        return mapping.get(classificacao, RecommendationEnum.HOLD)

    def get_active_recommendations(self, limit: int = 50) -> List[Recommendation]:
        """Recomendações ativas"""
        with self._get_session() as db:
            return db.query(Recommendation).filter(
                Recommendation.is_active == True
            ).order_by(
                desc(Recommendation.analysis_date)
            ).limit(limit).all()


class FundamentalAnalysisRepository(BaseRepository):
    """Repository para análises fundamentalistas"""

    def create_analysis(self, analysis_data: Dict[str, Any]) -> FundamentalAnalysis:
        """Cria análise com mapeamento automático"""
        with self._get_session() as db:
            english_data = self.mapper.map_to_english(analysis_data)
            analysis = FundamentalAnalysis(**english_data)
            db.add(analysis)
            db.commit()
            db.refresh(analysis)
            return analysis


class AgentSessionRepository(BaseRepository):
    """Repository para sessões de agentes"""

    def create_session(self, session_data: Dict[str, Any]) -> AgentSession:
        """Cria sessão de agente"""
        with self._get_session() as db:
            session = AgentSession(**session_data)
            db.add(session)
            db.commit()
            db.refresh(session)
            return session

    def finish_session(self, session_id: str, status: str = "completed", 
                      error_message: str = None) -> bool:
        """Finaliza sessão"""
        with self._get_session() as db:
            session = db.query(AgentSession).filter(
                AgentSession.session_id == session_id
            ).first()
            
            if session:
                session.finished_at = datetime.now()
                session.status = status
                if error_message:
                    session.error_message = error_message
                
                if session.started_at:
                    delta = session.finished_at - session.started_at
                    session.execution_time_seconds = delta.total_seconds()
                
                db.commit()
                return True
            return False


class MarketDataRepository(BaseRepository):
    """Repository para dados de mercado"""

    def bulk_insert_market_data(self, market_data: List[Dict[str, Any]]) -> int:
        """Inserção em lote de dados de mercado"""
        with self._get_session() as db:
            market_objects = [MarketData(**data) for data in market_data]
            db.bulk_save_objects(market_objects)
            db.commit()
            return len(market_objects)


# ==================== FACTORY FUNCTIONS ====================
def get_stock_repository(db_session: Session = None) -> StockRepository:
    """Factory para StockRepository"""
    return StockRepository(db_session)


def get_recommendation_repository(db_session: Session = None) -> RecommendationRepository:
    """Factory para RecommendationRepository"""
    return RecommendationRepository(db_session)


def get_fundamental_repository(db_session: Session = None) -> FundamentalAnalysisRepository:
    """Factory para FundamentalAnalysisRepository"""
    return FundamentalAnalysisRepository(db_session)


def get_agent_session_repository(db_session: Session = None) -> AgentSessionRepository:
    """Factory para AgentSessionRepository"""
    return AgentSessionRepository(db_session)


def get_market_data_repository(db_session: Session = None) -> MarketDataRepository:
    """Factory para MarketDataRepository"""
    return MarketDataRepository(db_session)
EOF

print_success "Repositories com mapeamento automático criado"

# ==================== EXECUTAR MIGRAÇÃO DE SCHEMA ====================
print_step "Executando migração de schema no PostgreSQL..."

# Drop e recriar tabelas com nova nomenclatura
python3 << 'EOF'
import sys
import os
sys.path.insert(0, os.getcwd())

try:
    # Configurar ambiente
    os.environ.update({
        'POSTGRES_HOST': 'localhost',
        'POSTGRES_PORT': '5432',
        'POSTGRES_DB': 'investment_system',
        'POSTGRES_USER': 'investment_user',
        'POSTGRES_PASSWORD': 'investment_secure_pass_2024'
    })
    
    print("1️⃣ Fazendo backup do schema atual...")
    from database.connection import backup_database
    backup_database()
    
    print("2️⃣ Dropping tabelas antigas...")
    from database.connection import drop_tables
    drop_tables()
    
    print("3️⃣ Atualizando para modelos inglês...")
    # Substituir models.py pelo inglês
    import shutil
    shutil.copy('database/models_english.py', 'database/models.py')
    
    # Reimportar módulos
    import importlib
    import database.models
    importlib.reload(database.models)
    
    print("4️⃣ Criando tabelas com nomenclatura inglês...")
    from database.connection import create_tables
    if create_tables():
        print("   ✅ Tabelas criadas com nomenclatura inglês")
    else:
        print("   ❌ Erro criando tabelas")
        sys.exit(1)
    
    print("5️⃣ Verificando schema...")
    from database.connection import get_database_info
    db_info = get_database_info()
    if 'error' not in db_info:
        print(f"   ✅ Schema OK - {len(db_info.get('tables', []))} tabelas")
        print(f"   📋 Tabelas: {', '.join(db_info.get('tables', []))}")
    else:
        print(f"   ❌ Erro no schema: {db_info.get('error')}")
        sys.exit(1)
    
    print("🎉 MIGRAÇÃO DE SCHEMA CONCLUÍDA!")
    
except Exception as e:
    print(f"❌ Erro na migração: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
EOF

if [ $? -eq 0 ]; then
    print_success "Schema migrado para nomenclatura 100% inglês"
else
    print_error "Falha na migração de schema"
    exit 1
fi

# ==================== ATUALIZAR REPOSITORIES ====================
print_step "Atualizando repositories.py com mapeamento automático..."

cp database/repositories_english.py database/repositories.py
print_success "Repositories atualizado com mapeamento português ↔ inglês"

# ==================== POPULAR DADOS COM NOMENCLATURA INGLÊS ====================
print_step "Populando dados iniciais com nomenclatura inglês..."

python3 << 'EOF'
import sys
import os
sys.path.insert(0, os.getcwd())

try:
    from database.repositories import get_stock_repository
    from database.models import StockStatusEnum, DataQualityEnum
    
    stock_repo = get_stock_repository()
    
    # Dados com nomenclatura 100% inglês
    sample_stocks = [
        {
            "symbol": "PETR4",
            "name": "Petróleo Brasileiro S.A. - Petrobras",
            "long_name": "Petróleo Brasileiro S.A. - Petrobras",
            "sector": "Energy",
            "industry": "Oil & Gas Integrated",
            "current_price": 32.50,
            "market_cap": 422000000000,
            "pe_ratio": 4.2,
            "pb_ratio": 0.8,
            "roe": 19.5,
            "roic": 12.8,
            "status": StockStatusEnum.ACTIVE,
            "data_quality": DataQualityEnum.GOOD
        },
        {
            "symbol": "VALE3",
            "name": "Vale S.A.",
            "long_name": "Vale S.A.",
            "sector": "Basic Materials",
            "industry": "Steel",
            "current_price": 61.80,
            "market_cap": 280000000000,
            "pe_ratio": 5.1,
            "pb_ratio": 1.2,
            "roe": 24.3,
            "roic": 18.5,
            "status": StockStatusEnum.ACTIVE,
            "data_quality": DataQualityEnum.GOOD
        },
        {
            "symbol": "ITUB4",
            "name": "Itaú Unibanco Holding S.A.",
            "long_name": "Itaú Unibanco Holding S.A.",
            "sector": "Financial Services",
            "industry": "Banks - Regional",
            "current_price": 33.15,
            "market_cap": 325000000000,
            "pe_ratio": 8.9,
            "pb_ratio": 1.8,
            "roe": 20.1,
            "roic": 15.2,
            "status": StockStatusEnum.ACTIVE,
            "data_quality": DataQualityEnum.GOOD
        },
        {
            "symbol": "BBDC4",
            "name": "Banco Bradesco S.A.",
            "long_name": "Banco Bradesco S.A.",
            "sector": "Financial Services",
            "industry": "Banks - Regional",
            "current_price": 13.85,
            "market_cap": 127000000000,
            "pe_ratio": 6.8,
            "pb_ratio": 1.1,
            "roe": 16.8,
            "roic": 14.5,
            "status": StockStatusEnum.ACTIVE,
            "data_quality": DataQualityEnum.GOOD
        },
        {
            "symbol": "ABEV3",
            "name": "Ambev S.A.",
            "long_name": "Ambev S.A.",
            "sector": "Consumer Defensive",
            "industry": "Beverages - Alcoholic",
            "current_price": 11.25,
            "market_cap": 177000000000,
            "pe_ratio": 15.2,
            "pb_ratio": 1.9,
            "roe": 12.5,
            "roic": 8.9,
            "status": StockStatusEnum.ACTIVE,
            "data_quality": DataQualityEnum.GOOD
        }
    ]
    
    created_count = 0
    for stock_data in sample_stocks:
        try:
            stock = stock_repo.create_stock(stock_data)
            created_count += 1
            print(f"✅ Created: {stock.symbol} - {stock.name}")
        except Exception as e:
            print(f"❌ Error creating {stock_data['symbol']}: {e}")
    
    print(f"📊 {created_count} stocks created successfully")
    
    # Testar compatibilidade português
    print("\n🔄 Testing Portuguese compatibility...")
    test_data = {
        "codigo": "TEST3",
        "nome": "Empresa Teste",
        "setor": "Tecnologia",
        "preco_atual": 25.50,
        "p_l": 12.5,
        "p_vp": 2.0
    }
    
    try:
        test_stock = stock_repo.create_stock(test_data)
        print(f"✅ Portuguese compatibility: {test_stock.symbol} created")
        
        # Verificar se campos foram mapeados corretamente
        print(f"   📊 Mapped fields:")
        print(f"      codigo → symbol: {test_stock.symbol}")
        print(f"      nome → name: {test_stock.name}")
        print(f"      setor → sector: {test_stock.sector}")
        print(f"      preco_atual → current_price: {test_stock.current_price}")
        print(f"      p_l → pe_ratio: {test_stock.pe_ratio}")
        print(f"      p_vp → pb_ratio: {test_stock.pb_ratio}")
        
    except Exception as e:
        print(f"❌ Portuguese compatibility failed: {e}")
    
except Exception as e:
    print(f"❌ Error in data population: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
EOF

if [ $? -eq 0 ]; then
    print_success "Dados populados com nomenclatura inglês + compatibilidade português"
else
    print_warning "Problema na população (pode ser normal)"
fi

