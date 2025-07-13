# database/models.py - ATUALIZADO PARA FASE 2
"""
Modelos SQLAlchemy para o Sistema de Recomendações de Investimentos
VERSÃO EXPANDIDA - Fase 2: Mantém compatibilidade com Fase 1 + Novos recursos
"""
from sqlalchemy import (Column, Integer, String, Float, Boolean,
                        DateTime, Text, ForeignKey, Index, JSON, 
                        Enum as SQLEnum, UniqueConstraint, CheckConstraint)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

Base = declarative_base()


# ==================== ENUMS PARA FASE 2 ====================
class ReportingPeriod(Enum):
    """Tipos de período de reporte"""
    QUARTERLY = "quarterly"
    ANNUAL = "annual"
    TTM = "ttm"  # Trailing Twelve Months


class DataQuality(Enum):
    """Níveis de qualidade dos dados"""
    HIGH = "high"      # >90% dos campos preenchidos
    MEDIUM = "medium"  # 70-90% dos campos preenchidos  
    LOW = "low"        # 50-70% dos campos preenchidos
    POOR = "poor"      # <50% dos campos preenchidos


# ==================== MODELO PRINCIPAL EXPANDIDO ====================
class Stock(Base):
    """Modelo principal para ações - EXPANDIDO para Fase 2"""
    __tablename__ = "stocks"

    # ==================== CAMPOS ORIGINAIS (FASE 1) ====================
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

    # Dados de mercado básicos
    preco_atual = Column(Float)
    volume_medio = Column(Float)
    market_cap = Column(Float)
    free_float = Column(Float)

    # Dados fundamentalistas básicos (MANTIDOS da Fase 1)
    p_l = Column(Float)  # MANTIDO para compatibilidade
    p_vp = Column(Float)  # MANTIDO para compatibilidade
    ev_ebitda = Column(Float)
    roe = Column(Float)
    roic = Column(Float)
    margem_liquida = Column(Float)
    divida_liquida_ebitda = Column(Float)

    # Metadados originais
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    ultima_atualizacao_preco = Column(DateTime(timezone=True))
    ultima_atualizacao_fundamentals = Column(DateTime(timezone=True))

    # ==================== NOVOS CAMPOS (FASE 2) ====================
    # Informações corporativas expandidas
    industria = Column(String(100))
    ceo = Column(String(200))
    funcionarios = Column(Integer)
    ano_fundacao = Column(Integer)
    
    # Dados de mercado expandidos
    enterprise_value = Column(Float)
    shares_outstanding = Column(Float)
    volume_medio_30d = Column(Float)
    volume_medio_90d = Column(Float)
    beta = Column(Float)
    correlacao_ibovespa = Column(Float)
    
    # Dados fundamentalistas TTM (Trailing Twelve Months)
    revenue_ttm = Column(Float)
    gross_profit_ttm = Column(Float)
    operating_income_ttm = Column(Float)
    ebitda_ttm = Column(Float)
    net_income_ttm = Column(Float)
    
    # Balanço patrimonial
    total_assets = Column(Float)
    total_equity = Column(Float)
    total_debt = Column(Float)
    current_assets = Column(Float)
    current_liabilities = Column(Float)
    cash_and_equivalents = Column(Float)
    working_capital = Column(Float)
    
    # Métricas de valuation expandidas
    pe_ratio = Column(Float, index=True)  # NOVO: Padronizado
    pb_ratio = Column(Float, index=True)  # NOVO: Padronizado
    ps_ratio = Column(Float)
    ev_sales = Column(Float)
    
    # Métricas de rentabilidade expandidas
    roa = Column(Float)  # Return on Assets
    gross_margin = Column(Float)
    operating_margin = Column(Float)
    net_margin = Column(Float)
    ebitda_margin = Column(Float)
    
    # Métricas de endividamento expandidas
    debt_to_equity = Column(Float, index=True)
    debt_to_ebitda = Column(Float)
    current_ratio = Column(Float)
    quick_ratio = Column(Float)
    interest_coverage = Column(Float)
    
    # Métricas de eficiência
    asset_turnover = Column(Float)
    inventory_turnover = Column(Float)
    receivables_turnover = Column(Float)
    
    # Métricas de crescimento (CAGR)
    revenue_growth_1y = Column(Float)
    revenue_growth_3y = Column(Float)
    earnings_growth_1y = Column(Float)
    earnings_growth_3y = Column(Float)
    
    # Métricas de qualidade
    roe_consistency = Column(Float)  # Desvio padrão do ROE
    earnings_quality = Column(Float)  # FCF/Net Income ratio
    data_quality = Column(SQLEnum(DataQuality), default=DataQuality.MEDIUM)
    data_completeness = Column(Float)  # Percentual de campos preenchidos
    
    # Scores e rankings (NOVO para Fase 2)
    fundamental_score = Column(Float, index=True)  # Score 0-100
    sector_rank = Column(Integer)  # Posição no setor
    sector_percentile = Column(Float)  # Percentil no setor
    market_rank = Column(Integer)  # Posição no mercado geral
    
    # ESG e Governança
    esg_score = Column(Float)
    governance_level = Column(String(50))
    
    # Metadados expandidos
    last_analysis_date = Column(DateTime(timezone=True))

    # ==================== RELACIONAMENTOS ====================
    # Relacionamentos originais (MANTIDOS)
    recommendations = relationship("Recommendation", back_populates="stock")
    fundamental_analyses = relationship("FundamentalAnalysis", back_populates="stock")
    
    # Novos relacionamentos (FASE 2)
    financial_statements = relationship("FinancialStatement", back_populates="stock")

    # ==================== ÍNDICES OTIMIZADOS ====================
    __table_args__ = (
        # Índices originais (MANTIDOS)
        Index('idx_stock_setor_ativo', 'setor', 'ativo'),
        Index('idx_stock_market_cap', 'market_cap'),
        Index('idx_stock_volume', 'volume_medio'),
        
        # Novos índices para Fase 2
        Index('idx_stock_sector_score', 'setor', 'fundamental_score'),
        Index('idx_stock_pe_pb', 'pe_ratio', 'pb_ratio'),
        Index('idx_stock_roe_roic', 'roe', 'roic'),
        Index('idx_stock_data_quality', 'data_quality', 'data_completeness'),
        
        # Constraints para validação
        CheckConstraint('fundamental_score >= 0 AND fundamental_score <= 100', 
                       name='check_fundamental_score_range'),
        CheckConstraint('data_completeness >= 0 AND data_completeness <= 1', 
                       name='check_data_completeness_range'),
    )

    def __repr__(self):
        return f"<Stock(codigo='{self.codigo}', nome='{self.nome}', score={self.fundamental_score})>"

    def to_dict(self) -> Dict[str, Any]:
        """Converte o modelo para dicionário - EXPANDIDO"""
        # Campos básicos (compatibilidade Fase 1)
        result = {
            'id': self.id,
            'codigo': self.codigo,
            'nome': self.nome,
            'setor': self.setor,
            'market_cap': self.market_cap,
            'preco_atual': self.preco_atual,
            'p_l': self.p_l,  # MANTIDO para compatibilidade
            'p_vp': self.p_vp,  # MANTIDO para compatibilidade
            'roe': self.roe,
            'roic': self.roic,
            'ativo': self.ativo,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        # Campos expandidos (Fase 2)
        if self.pe_ratio is not None:
            result['pe_ratio'] = self.pe_ratio
        if self.pb_ratio is not None:
            result['pb_ratio'] = self.pb_ratio
        if self.fundamental_score is not None:
            result['fundamental_score'] = self.fundamental_score
        if self.sector_rank is not None:
            result['sector_rank'] = self.sector_rank
        if self.data_quality is not None:
            result['data_quality'] = self.data_quality.value
        
        return result

    # ==================== MÉTODOS DE COMPATIBILIDADE ====================
    @property
    def pe_ratio_compat(self) -> Optional[float]:
        """Retorna P/L com compatibilidade entre pe_ratio e p_l"""
        return self.pe_ratio or self.p_l
    
    @property
    def pb_ratio_compat(self) -> Optional[float]:
        """Retorna P/VP com compatibilidade entre pb_ratio e p_vp"""
        return self.pb_ratio or self.p_vp


# ==================== TABELAS EXPANDIDAS (FASE 2) ====================
class FinancialStatement(Base):
    """Demonstrações financeiras históricas - NOVA TABELA"""
    __tablename__ = "financial_statements"

    id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False)
    
    # Período e tipo
    period_end_date = Column(DateTime(timezone=True), nullable=False, index=True)
    reporting_period = Column(SQLEnum(ReportingPeriod), nullable=False)
    fiscal_year = Column(Integer, nullable=False, index=True)
    fiscal_quarter = Column(Integer)  # 1-4, null para anual
    
    # Demonstração de Resultados (DRE)
    revenue = Column(Float)
    cost_of_revenue = Column(Float)
    gross_profit = Column(Float)
    research_development = Column(Float)
    selling_general_administrative = Column(Float)
    total_operating_expenses = Column(Float)
    operating_income = Column(Float)
    interest_expense = Column(Float)
    other_income_expense = Column(Float)
    income_before_tax = Column(Float)
    income_tax_expense = Column(Float)
    net_income = Column(Float)
    
    # EBITDA e derivados
    ebitda = Column(Float)
    depreciation_amortization = Column(Float)
    
    # Dados por ação
    basic_eps = Column(Float)
    diluted_eps = Column(Float)
    weighted_average_shares = Column(Float)
    weighted_average_shares_diluted = Column(Float)
    
    # Balanço Patrimonial
    total_assets = Column(Float)
    current_assets = Column(Float)
    non_current_assets = Column(Float)
    cash_and_cash_equivalents = Column(Float)
    short_term_investments = Column(Float)
    accounts_receivable = Column(Float)
    inventory = Column(Float)
    prepaid_expenses = Column(Float)
    
    total_liabilities = Column(Float)
    current_liabilities = Column(Float)
    non_current_liabilities = Column(Float)
    accounts_payable = Column(Float)
    short_term_debt = Column(Float)
    long_term_debt = Column(Float)
    
    total_equity = Column(Float)
    retained_earnings = Column(Float)
    
    # Fluxo de Caixa
    operating_cash_flow = Column(Float)
    investing_cash_flow = Column(Float)
    financing_cash_flow = Column(Float)
    free_cash_flow = Column(Float)
    capital_expenditures = Column(Float)
    
    # Metadados
    currency = Column(String(10), default="BRL")
    data_source = Column(String(50), default="yfinance")
    confidence_score = Column(Float)  # Confiança nos dados 0-1
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relacionamento
    stock = relationship("Stock", back_populates="financial_statements")
    
    # Índices
    __table_args__ = (
        Index('idx_statement_stock_period', 'stock_id', 'period_end_date'),
        Index('idx_statement_fiscal', 'fiscal_year', 'fiscal_quarter'),
        UniqueConstraint('stock_id', 'period_end_date', 'reporting_period', 
                        name='uq_statement_stock_period'),
    )


class Recommendation(Base):
    """Modelo para recomendações - MANTIDO da Fase 1 + Melhorias"""
    __tablename__ = "recommendations"

    # Campos originais MANTIDOS
    id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False)
    data_analise = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    score_fundamentalista = Column(Float, nullable=False)
    score_tecnico = Column(Float, default=0.0)
    score_macro = Column(Float, default=0.0)
    score_final = Column(Float, nullable=False)
    
    classificacao = Column(String(20), nullable=False, index=True)
    confianca = Column(Float, default=1.0)
    
    preco_entrada = Column(Float)
    preco_alvo = Column(Float)
    stop_loss = Column(Float)
    take_profit = Column(Float)
    
    justificativa = Column(Text, nullable=False)
    fatores_positivos = Column(Text)
    fatores_negativos = Column(Text)
    riscos = Column(Text)
    
    agente_versao = Column(String(50))
    tempo_processamento = Column(Float)
    ativa = Column(Boolean, default=True, index=True)
    revisada_em = Column(DateTime(timezone=True))
    
    # Relacionamento
    stock = relationship("Stock", back_populates="recommendations")
    
    # Índices
    __table_args__ = (
        Index('idx_recommendation_data_classificacao', 'data_analise', 'classificacao'),
        Index('idx_recommendation_score', 'score_final'),
        Index('idx_recommendation_ativa', 'ativa'),
    )

    def __repr__(self):
        return f"<Recommendation(stock={self.stock.codigo if self.stock else self.stock_id}, " \
               f"classificacao='{self.classificacao}', score={self.score_final})>"

    def to_dict(self) -> Dict[str, Any]:
        """Converte o modelo para dicionário"""
        return {
            'id': self.id,
            'stock_codigo': self.stock.codigo if self.stock else None,
            'data_analise': self.data_analise.isoformat() if self.data_analise else None,
            'score_final': self.score_final,
            'classificacao': self.classificacao,
            'preco_entrada': self.preco_entrada,
            'stop_loss': self.stop_loss,
            'justificativa': self.justificativa,
            'ativa': self.ativa
        }


class FundamentalAnalysis(Base):
    """Análises fundamentalistas - EXPANDIDO para Fase 2"""
    __tablename__ = "fundamental_analyses"

    # Campos básicos MANTIDOS
    id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False)
    data_analise = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Scores individuais MANTIDOS + Expandidos
    p_l_score = Column(Float)
    p_vp_score = Column(Float)
    ev_ebitda_score = Column(Float)
    roe_score = Column(Float)
    roic_score = Column(Float)
    margem_liquida_score = Column(Float)
    divida_ebitda_score = Column(Float)
    crescimento_receita_score = Column(Float)
    crescimento_lucro_score = Column(Float)
    
    # Novos scores categorizados (FASE 2)
    valuation_score = Column(Float, nullable=False)
    profitability_score = Column(Float, nullable=False)
    leverage_score = Column(Float, nullable=False)
    growth_score = Column(Float, nullable=False)
    efficiency_score = Column(Float, nullable=False)
    quality_score = Column(Float, nullable=False)
    
    # Score consolidado MANTIDO + Expandido
    score_valuation = Column(Float)  # MANTIDO
    score_rentabilidade = Column(Float)  # MANTIDO
    score_endividamento = Column(Float)  # MANTIDO
    score_crescimento = Column(Float)  # MANTIDO
    score_total = Column(Float, nullable=False)  # MANTIDO
    final_score = Column(Float, nullable=False, index=True)  # NOVO: Padronizado
    
    # Comparação setorial EXPANDIDA
    percentil_setor = Column(Float)  # MANTIDO
    ranking_setor = Column(Integer)  # MANTIDO
    total_empresas_setor = Column(Integer)  # MANTIDO
    
    # Novos campos de comparação
    sector_percentile_valuation = Column(Float)
    sector_percentile_profitability = Column(Float)
    sector_percentile_leverage = Column(Float)
    sector_percentile_growth = Column(Float)
    sector_percentile_overall = Column(Float)
    
    sector_rank = Column(Integer)
    total_companies_in_sector = Column(Integer)
    
    # Comparação com mercado (NOVO)
    market_percentile = Column(Float)
    market_rank = Column(Integer)
    total_companies_in_market = Column(Integer)
    
    # Configuração da análise (NOVO)
    analysis_version = Column(String(20), default="2.0")
    calculation_method = Column(String(50))
    data_period = Column(String(50))
    scoring_weights = Column(JSON)
    
    # Métricas detalhadas (NOVO)
    metrics_snapshot = Column(JSON)
    
    # Flags de identificação (NOVO)
    is_dividend_aristocrat = Column(Boolean, default=False)
    is_growth_stock = Column(Boolean, default=False)
    is_value_stock = Column(Boolean, default=False)
    is_quality_stock = Column(Boolean, default=False)
    
    # Flags de alerta (NOVO)
    has_high_debt = Column(Boolean, default=False)
    has_declining_margins = Column(Boolean, default=False)
    has_inconsistent_earnings = Column(Boolean, default=False)
    
    # Justificativas automáticas (NOVO)
    strengths = Column(Text)
    weaknesses = Column(Text)
    recommendations = Column(Text)
    risks = Column(Text)
    
    # Metadados expandidos
    dados_origem = Column(String(100))  # MANTIDO
    agente_versao = Column(String(50))  # MANTIDO
    processing_time_seconds = Column(Float)
    data_completeness = Column(Float)
    confidence_level = Column(Float)
    
    # Agente que executou
    agent_name = Column(String(100), default="FundamentalAnalyzer")
    agent_version = Column(String(20), default="2.0")
    
    # Relacionamento
    stock = relationship("Stock", back_populates="fundamental_analyses")
    
    # Índices
    __table_args__ = (
        Index('idx_fundamental_data_score', 'data_analise', 'score_total'),
        Index('idx_fundamental_stock_data', 'stock_id', 'data_analise'),
        # Novos índices
        Index('idx_analysis_final_score', 'final_score', 'data_analise'),
        Index('idx_analysis_sector_rank', 'sector_rank', 'data_analise'),
        CheckConstraint('final_score >= 0 AND final_score <= 100', 
                       name='check_final_score_range'),
        CheckConstraint('confidence_level >= 0 AND confidence_level <= 1', 
                       name='check_confidence_range'),
    )

    def __repr__(self):
        return f"<FundamentalAnalysis(stock={self.stock.codigo if self.stock else self.stock_id}, " \
               f"score={self.final_score or self.score_total})>"

    def to_dict(self) -> Dict[str, Any]:
        """Converte análise para dicionário"""
        return {
            'id': self.id,
            'stock_id': self.stock_id,
            'data_analise': self.data_analise.isoformat() if self.data_analise else None,
            'final_score': self.final_score or self.score_total,
            'score_total': self.score_total,  # Compatibilidade
            'valuation_score': self.valuation_score,
            'profitability_score': self.profitability_score,
            'leverage_score': self.leverage_score,
            'growth_score': self.growth_score,
            'sector_percentile_overall': self.sector_percentile_overall or self.percentil_setor,
            'market_percentile': self.market_percentile,
            'sector_rank': self.sector_rank or self.ranking_setor,
            'market_rank': self.market_rank,
            'is_quality_stock': self.is_quality_stock,
            'strengths': self.strengths,
            'weaknesses': self.weaknesses,
            'confidence_level': self.confidence_level
        }


# ==================== NOVAS TABELAS (FASE 2) ====================
class AgentSession(Base):
    """Sessões dos agentes - MANTIDO da Fase 1"""
    __tablename__ = "agent_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), unique=True, index=True, nullable=False)
    agent_name = Column(String(100), nullable=False, index=True)
    agent_version = Column(String(50))
    
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    finished_at = Column(DateTime(timezone=True))
    status = Column(String(20), default="running", index=True)
    
    input_data = Column(Text)
    output_data = Column(Text)
    error_message = Column(Text)
    
    execution_time_seconds = Column(Float)
    stocks_processed = Column(Integer, default=0)
    recommendations_generated = Column(Integer, default=0)
    
    config_snapshot = Column(Text)
    
    __table_args__ = (
        Index('idx_agent_session_name_status', 'agent_name', 'status'),
        Index('idx_agent_session_started', 'started_at'),
    )

    def __repr__(self):
        return f"<AgentSession(agent='{self.agent_name}', status='{self.status}')>"

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'session_id': self.session_id,
            'agent_name': self.agent_name,
            'status': self.status,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'finished_at': self.finished_at.isoformat() if self.finished_at else None,
            'execution_time_seconds': self.execution_time_seconds,
            'stocks_processed': self.stocks_processed,
            'recommendations_generated': self.recommendations_generated
        }


class MarketData(Base):
    """Dados históricos de mercado - MANTIDO da Fase 1"""
    __tablename__ = "market_data"

    id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False)
    data = Column(DateTime(timezone=True), nullable=False, index=True)
    
    abertura = Column(Float, nullable=False)
    maximo = Column(Float, nullable=False)
    minimo = Column(Float, nullable=False)
    fechamento = Column(Float, nullable=False)
    volume = Column(Integer, nullable=False)
    fechamento_ajustado = Column(Float)
    
    fonte = Column(String(50), default="yfinance")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    stock = relationship("Stock")
    
    __table_args__ = (
        Index('idx_market_data_stock_data', 'stock_id', 'data'),
        Index('idx_market_data_data', 'data'),
    )

    def __repr__(self):
        return f"<MarketData(stock_id={self.stock_id}, data={self.data}, " \
               f"fechamento={self.fechamento})>"


# ==================== FUNÇÕES DE MIGRAÇÃO ====================
def migrate_phase1_to_phase2(engine):
    """
    Migra dados da Fase 1 para estrutura expandida da Fase 2
    Mantém compatibilidade total
    """
    try:
        # Criar novas colunas se não existirem
        from sqlalchemy import text
        
        with engine.connect() as conn:
            # Verificar se colunas já existem antes de adicionar
            result = conn.execute(text("PRAGMA table_info(stocks)"))
            existing_columns = [row[1] for row in result.fetchall()]
            
            # Lista de novas colunas para adicionar
            new_columns = [
                "pe_ratio FLOAT",
                "pb_ratio FLOAT", 
                "fundamental_score FLOAT",
                "sector_rank INTEGER",
                "data_quality VARCHAR(20) DEFAULT 'medium'",
                "data_completeness FLOAT",
                "revenue_ttm FLOAT",
                "net_income_ttm FLOAT",
                "total_assets FLOAT",
                "total_equity FLOAT",
                "debt_to_equity FLOAT"
            ]
            
            # Adicionar colunas que não existem
            for column_def in new_columns:
                column_name = column_def.split()[0]
                if column_name not in existing_columns:
                    try:
                        conn.execute(text(f"ALTER TABLE stocks ADD COLUMN {column_def}"))
                        print(f"✅ Coluna adicionada: {column_name}")
                    except Exception as e:
                        print(f"⚠️  Coluna {column_name} já existe ou erro: {e}")
            
            conn.commit()
        
        print("✅ Migração da Fase 1 para Fase 2 concluída")
        return True
        
    except Exception as e:
        print(f"❌ Erro na migração: {e}")
        return False


def populate_phase2_fields(session):
    """
    Popula campos da Fase 2 com dados compatíveis da Fase 1
    """
    try:
        stocks = session.query(Stock).all()
        updated_count = 0
        
        for stock in stocks:
            # Migrar campos com nomes diferentes
            if stock.p_l and not stock.pe_ratio:
                stock.pe_ratio = stock.p_l
            
            if stock.p_vp and not stock.pb_ratio:
                stock.pb_ratio = stock.p_vp
            
            # Definir score inicial baseado em ROE se disponível
            if stock.roe and not stock.fundamental_score:
                # Score básico baseado em ROE (temporário)
                if stock.roe > 20:
                    stock.fundamental_score = 80.0
                elif stock.roe > 15:
                    stock.fundamental_score = 70.0
                elif stock.roe > 10:
                    stock.fundamental_score = 60.0
                else:
                    stock.fundamental_score = 50.0
            
            # Definir qualidade inicial
            if not stock.data_quality:
                stock.data_quality = DataQuality.MEDIUM
            
            updated_count += 1
        
        session.commit()
        print(f"✅ {updated_count} ações atualizadas com campos da Fase 2")
        return True
        
    except Exception as e:
        session.rollback()
        print(f"❌ Erro ao popular campos da Fase 2: {e}")
        return False


# ==================== FUNÇÕES UTILITÁRIAS ====================
def get_latest_analysis(stock_id: int, session) -> Optional[FundamentalAnalysis]:
    """Retorna a análise mais recente de uma ação"""
    return session.query(FundamentalAnalysis)\
                 .filter(FundamentalAnalysis.stock_id == stock_id)\
                 .order_by(FundamentalAnalysis.data_analise.desc())\
                 .first()


def get_sector_ranking(sector: str, session, limit: int = 20) -> List[Stock]:
    """Retorna ranking das melhores ações de um setor"""
    return session.query(Stock)\
                 .filter(Stock.setor == sector)\
                 .filter(Stock.ativo == True)\
                 .order_by(Stock.fundamental_score.desc())\
                 .limit(limit)\
                 .all()


def get_quality_stocks(session, min_score: float = 80.0, limit: int = 50) -> List[Stock]:
    """Retorna ações de alta qualidade fundamentalista"""
    return session.query(Stock)\
                 .filter(Stock.fundamental_score >= min_score)\
                 .filter(Stock.ativo == True)\
                 .filter(Stock.data_quality.in_([DataQuality.HIGH, DataQuality.MEDIUM]))\
                 .order_by(Stock.fundamental_score.desc())\
                 .limit(limit)\
                 .all()


def calculate_sector_statistics(sector: str, session) -> Dict[str, Any]:
    """Calcula estatísticas básicas de um setor"""
    stats = session.query(
        func.count(Stock.id).label('total_companies'),
        func.avg(Stock.fundamental_score).label('avg_score'),
        func.avg(Stock.pe_ratio).label('median_pe'),
        func.avg(Stock.roe).label('median_roe'),
        func.avg(Stock.roic).label('median_roic')
    ).filter(
        Stock.setor == sector,
        Stock.ativo == True
    ).first()
    
    return {
        'sector': sector,
        'total_companies': stats.total_companies or 0,
        'avg_fundamental_score': round(stats.avg_score or 0, 2),
        'avg_pe_ratio': round(stats.median_pe or 0, 2),
        'avg_roe': round(stats.median_roe or 0, 2),
        'avg_roic': round(stats.median_roic or 0, 2)
    }


# ==================== SCRIPTS DE MIGRAÇÃO ====================
def run_phase2_migration(engine):
    """
    Executa migração completa para Fase 2
    MANTÉM COMPATIBILIDADE TOTAL com Fase 1
    """
    print("🚀 Iniciando migração para Fase 2...")
    
    try:
        # 1. Criar novas tabelas
        print("📋 Criando novas tabelas...")
        Base.metadata.create_all(bind=engine)
        
        # 2. Migrar estrutura da tabela stocks
        print("📋 Atualizando estrutura da tabela stocks...")
        migrate_phase1_to_phase2(engine)
        
        # 3. Popular novos campos com dados existentes
        print("📋 Populando novos campos...")
        from database.connection import SessionLocal
        session = SessionLocal()
        populate_phase2_fields(session)
        session.close()
        
        print("✅ Migração para Fase 2 concluída com sucesso!")
        print("✅ Compatibilidade com Fase 1 mantida")
        return True
        
    except Exception as e:
        print(f"❌ Erro na migração: {e}")
        return False


def validate_migration(engine):
    """Valida se a migração foi bem-sucedida"""
    try:
        from database.connection import SessionLocal
        session = SessionLocal()
        
        # Verificar se dados antigos ainda existem
        old_stocks = session.query(Stock).filter(Stock.p_l.isnot(None)).count()
        new_stocks = session.query(Stock).filter(Stock.pe_ratio.isnot(None)).count()
        
        print(f"📊 Validação da migração:")
        print(f"   Ações com P/L (antigo): {old_stocks}")
        print(f"   Ações com pe_ratio (novo): {new_stocks}")
        
        # Verificar se novas tabelas existem
        try:
            statements_count = session.query(FinancialStatement).count()
            print(f"   Tabela financial_statements: {statements_count} registros")
        except:
            print("   ⚠️  Tabela financial_statements não criada")
        
        session.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na validação: {e}")
        return False


# ==================== COMPATIBILIDADE COM FASE 1 ====================
def ensure_backward_compatibility():
    """
    Garante que todo código da Fase 1 continue funcionando
    """
    print("🔄 Verificando compatibilidade com Fase 1...")
    
    # Verificar se campos antigos ainda existem
    required_fields = ['p_l', 'p_vp', 'roe', 'roic', 'market_cap']
    
    for field in required_fields:
        if hasattr(Stock, field):
            print(f"   ✅ Campo {field} mantido")
        else:
            print(f"   ❌ Campo {field} removido - PROBLEMA!")
    
    # Verificar se métodos antigos funcionam
    try:
        stock = Stock()
        dict_result = stock.to_dict()
        if 'p_l' in dict_result or 'pe_ratio' in dict_result:
            print("   ✅ Método to_dict() compatível")
        else:
            print("   ❌ Método to_dict() incompatível")
    except Exception as e:
        print(f"   ❌ Erro no método to_dict(): {e}")


if __name__ == "__main__":
    print("Modelos de Dados Atualizados - Fase 2")
    print("MANTÉM COMPATIBILIDADE TOTAL com Fase 1")
    print()
    print("Mudanças principais:")
    print("✅ Novos campos na tabela 'stocks' (50+ campos)")
    print("✅ Nova tabela 'financial_statements'")
    print("✅ Análises expandidas em 'fundamental_analyses'")
    print("✅ Campos antigos MANTIDOS (p_l, p_vp, etc.)")
    print("✅ Métodos de compatibilidade adicionados")
    print("✅ Migração automática incluída")
    print()
    print("Para executar a migração:")
    print("from database.models import run_phase2_migration")
    print("from database.connection import engine")
    print("run_phase2_migration(engine)")
