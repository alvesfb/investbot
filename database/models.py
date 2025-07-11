# database/models.py
"""
Modelos SQLAlchemy para o Sistema de Recomendações de Investimentos
"""
from sqlalchemy import (Column, Integer, String, Float, Boolean,
                        DateTime, Text, ForeignKey, Index)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from typing import Dict, Any

Base = declarative_base()


class Stock(Base):
    """Modelo para ações/ativos"""
    __tablename__ = "stocks"

    # Identificação
    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(
        String(10), unique=True, index=True,
        nullable=False)  # Ex: PETR4, VALE3
    nome = Column(String(200), nullable=False)  # Ex: Petróleo Brasileiro S.A.
    nome_completo = Column(String(500))  # Razão social completa

    # Classificação
    setor = Column(String(100), index=True)  # Ex: Petróleo e Gás
    subsetor = Column(String(100))  # Ex: Exploração e Refino
    segmento = Column(String(100))  # Ex: Petróleo

    # Informações básicas
    cnpj = Column(String(20))
    website = Column(String(200))
    descricao = Column(Text)

    # Status
    ativo = Column(Boolean, default=True, index=True)  # Se ainda é negociada
    listagem = Column(String(50))  # Novo Mercado, Nível 1, etc.

    # Dados de mercado (atualizados frequentemente)
    preco_atual = Column(Float)
    volume_medio = Column(Float)  # Volume médio dos últimos 30 dias
    market_cap = Column(Float)  # Valor de mercado
    free_float = Column(Float)  # Percentual em circulação

    # Dados fundamentalistas básicos (atualizados trimestralmente)
    p_l = Column(Float)  # Preço/Lucro
    p_vp = Column(Float)  # Preço/Valor Patrimonial
    ev_ebitda = Column(Float)  # EV/EBITDA
    roe = Column(Float)  # Return on Equity
    roic = Column(Float)  # Return on Invested Capital
    margem_liquida = Column(Float)  # Margem líquida
    divida_liquida_ebitda = Column(Float)  # Dívida líquida/EBITDA

    # Metadados
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    ultima_atualizacao_preco = Column(DateTime(timezone=True))
    ultima_atualizacao_fundamentals = Column(DateTime(timezone=True))

    # Relacionamentos
    recommendations = relationship("Recommendation", back_populates="stock")
    fundamental_analyses = relationship("FundamentalAnalysis",
                                        back_populates="stock")

    # Índices compostos
    __table_args__ = (
        Index('idx_stock_setor_ativo', 'setor', 'ativo'),
        Index('idx_stock_market_cap', 'market_cap'),
        Index('idx_stock_volume', 'volume_medio'),
    )

    def __repr__(self):
        return f"<Stock(codigo='{self.codigo}', nome='{self.nome}')>"

    def to_dict(self) -> Dict[str, Any]:
        """Converte o modelo para dicionário"""
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
            'updated_at': self.updated_at.isoformat() if
            self.updated_at else None
        }


class Recommendation(Base):
    """Modelo para recomendações geradas pelos agentes"""
    __tablename__ = "recommendations"

    # Identificação
    id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False)

    # Data da análise
    data_analise = Column(DateTime(timezone=True),
                          server_default=func.now(), index=True)

    # Scores e classificação
    score_fundamentalista = Column(Float, nullable=False)  # 0-100
    score_tecnico = Column(Float, default=0.0)  # 0-100 (Fase 5)
    score_macro = Column(Float, default=0.0)  # 0-100 (Fase 7)
    score_final = Column(Float, nullable=False)  # 0-100 (ponderado)

    # Classificação final
    classificacao = Column(String(20),
                           nullable=False, index=True)  # COMPRA, VENDA, etc.
    confianca = Column(Float, default=1.0)  # 0-1 (confiança do modelo)

    # Targets e stops
    preco_entrada = Column(Float)  # Preço no momento da análise
    preco_alvo = Column(Float)  # Target price
    stop_loss = Column(Float)  # Stop loss sugerido
    take_profit = Column(Float)  # Take profit sugerido

    # Justificativa e contexto
    justificativa = Column(Text, nullable=False)  # Explicação da recomendação
    fatores_positivos = Column(Text)  # JSON com fatores positivos
    fatores_negativos = Column(Text)  # JSON com fatores negativos
    riscos = Column(Text)  # Principais riscos identificados

    # Metadados
    agente_versao = Column(String(50))  # Versão do agente que gerou
    tempo_processamento = Column(Float)  # Tempo em segundos

    # Status da recomendação
    ativa = Column(Boolean, default=True, index=True)
    revisada_em = Column(DateTime(timezone=True))

    # Relacionamentos
    stock = relationship("Stock", back_populates="recommendations")

    # Índices
    __table_args__ = (
        Index('idx_recommendation_data_classificacao',
              'data_analise', 'classificacao'),
        Index('idx_recommendation_score', 'score_final'),
        Index('idx_recommendation_ativa', 'ativa'),
    )

    def __repr__(self):
        return f"<Recommendation" \
            f"(stock={self.stock.codigo if self.stock else self.stock_id}, " \
            f"classificacao='{self.classificacao}', score={self.score_final})>"

    def to_dict(self) -> Dict[str, Any]:
        """Converte o modelo para dicionário"""
        return {
            'id': self.id,
            'stock_codigo': self.stock.codigo if self.stock else None,
            'data_analise': self.data_analise.isoformat() if
            self.data_analise else None,
            'score_final': self.score_final,
            'classificacao': self.classificacao,
            'preco_entrada': self.preco_entrada,
            'stop_loss': self.stop_loss,
            'justificativa': self.justificativa,
            'ativa': self.ativa
        }


class FundamentalAnalysis(Base):
    """Modelo para análises fundamentalistas detalhadas"""
    __tablename__ = "fundamental_analyses"

    # Identificação
    id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False)
    data_analise = Column(
        DateTime(timezone=True), server_default=func.now(), index=True)

    # Métricas de valuation
    p_l_score = Column(Float)  # Score individual do P/L
    p_vp_score = Column(Float)  # Score individual do P/VP
    ev_ebitda_score = Column(Float)  # Score individual do EV/EBITDA

    # Métricas de rentabilidade
    roe_score = Column(Float)  # Score individual do ROE
    roic_score = Column(Float)  # Score individual do ROIC
    margem_liquida_score = Column(Float)  # Score da margem líquida

    # Métricas de endividamento
    divida_ebitda_score = Column(Float)  # Score da dívida/EBITDA

    # Métricas de crescimento
    crescimento_receita_score = Column(Float)  # Score do cresc. de receita
    crescimento_lucro_score = Column(Float)  # Score do crescimento de lucro

    # Score consolidado
    score_valuation = Column(Float)  # Score de valuation (0-100)
    score_rentabilidade = Column(Float)  # Score de rentabilidade (0-100)
    score_endividamento = Column(Float)  # Score de endividamento (0-100)
    score_crescimento = Column(Float)  # Score de crescimento (0-100)
    score_total = Column(Float, nullable=False)  # Score fundament. tot (0-100)

    # Comparação setorial
    percentil_setor = Column(Float)  # Posição no setor (0-100)
    ranking_setor = Column(Integer)  # Ranking absoluto no setor
    total_empresas_setor = Column(Integer)  # Total de empresas no setor

    # Metadados
    dados_origem = Column(String(100))  # YFinance, B3, etc.
    agente_versao = Column(String(50))

    # Relacionamentos
    stock = relationship("Stock", back_populates="fundamental_analyses")

    # Índices
    __table_args__ = (
        Index('idx_fundamental_data_score', 'data_analise', 'score_total'),
        Index('idx_fundamental_stock_data', 'stock_id', 'data_analise'),
    )

    def __repr__(self):
        return f"<FundamentalAnalysis" \
            f"(stock={self.stock.codigo if self.stock else self.stock_id}, " \
            f"score={self.score_total})>"


class AgentSession(Base):
    """Modelo para sessões e logs dos agentes Agno"""
    __tablename__ = "agent_sessions"

    # Identificação
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), unique=True, index=True, nullable=False)

    # Agente
    agent_name = Column(
        String(100), nullable=False,
        index=True)  # collector, analyzer, recommender
    agent_version = Column(String(50))

    # Execução
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    finished_at = Column(DateTime(timezone=True))
    status = Column(
        String(20), default="running",
        index=True)  # running, completed, failed

    # Input/Output
    input_data = Column(Text)  # JSON com dados de entrada
    output_data = Column(Text)  # JSON com dados de saída
    error_message = Column(Text)  # Mensagem de erro se falhou

    # Métricas
    execution_time_seconds = Column(Float)
    stocks_processed = Column(Integer, default=0)
    recommendations_generated = Column(Integer, default=0)

    # Metadados
    config_snapshot = Column(Text)  # JSON com configurações usadas

    # Índices
    __table_args__ = (
        Index('idx_agent_session_name_status', 'agent_name', 'status'),
        Index('idx_agent_session_started', 'started_at'),
    )

    def __repr__(self):
        return f"<AgentSession(agent='{self.agent_name}', " \
            f"status='{self.status}')>"

    def to_dict(self) -> Dict[str, Any]:
        """Converte o modelo para dicionário"""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'agent_name': self.agent_name,
            'status': self.status,
            'started_at': self.started_at.isoformat() if
            self.started_at else None,
            'finished_at': self.finished_at.isoformat() if
            self.finished_at else None,
            'execution_time_seconds': self.execution_time_seconds,
            'stocks_processed': self.stocks_processed,
            'recommendations_generated': self.recommendations_generated
        }


class MarketData(Base):
    """Modelo para dados históricos de mercado (preços, volumes)"""
    __tablename__ = "market_data"

    # Identificação
    id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False)
    data = Column(DateTime(timezone=True), nullable=False, index=True)

    # OHLCV
    abertura = Column(Float, nullable=False)
    maximo = Column(Float, nullable=False)
    minimo = Column(Float, nullable=False)
    fechamento = Column(Float, nullable=False)
    volume = Column(Integer, nullable=False)

    # Dados ajustados
    fechamento_ajustado = Column(Float)

    # Metadados
    fonte = Column(
        String(50), default="yfinance")  # yfinance, b3, alphavantage
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relacionamentos
    stock = relationship("Stock")

    # Índices
    __table_args__ = (
        Index('idx_market_data_stock_data', 'stock_id', 'data'),
        Index('idx_market_data_data', 'data'),
    )

    def __repr__(self):
        return f"<MarketData" \
            f"(stock_id={self.stock_id}, data={self.data}, " \
            f"fechamento={self.fechamento})>"
