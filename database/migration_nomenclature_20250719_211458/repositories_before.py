# database/repositories_postgresql.py
"""
Repository pattern para PostgreSQL - OTIMIZADO
Sistema de Recomendações de Investimentos
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


class BaseRepository:
    """Classe base para repositories PostgreSQL"""

    def __init__(self, db_session: Session = None):
        self.db_session = db_session

    def _get_session(self):
        """Retorna sessão do banco (injetada ou nova)"""
        if self.db_session:
            return self.db_session
        return get_db_session()


class StockRepository(BaseRepository):
    """Repository PostgreSQL para operações com ações - OTIMIZADO"""

    def create_stock(self, stock_data: Dict[str, Any]) -> Stock:
        """Cria uma nova ação com dados PostgreSQL otimizados"""
        with self._get_session() as db:
            # Verificar se já existe
            existing = db.query(Stock).filter(
                Stock.codigo == stock_data.get('codigo', '').upper()
            ).first()
            
            if existing:
                logger.info(f"Ação {stock_data.get('codigo')} já existe")
                return existing
            
            # Mapear campos com compatibilidade SQLite → PostgreSQL
            mapped_data = self._map_stock_data(stock_data)
            
            stock = Stock(**mapped_data)
            db.add(stock)
            db.commit()
            db.refresh(stock)
            
            logger.info(f"Ação criada: {stock.codigo}")
            return stock

    def _map_stock_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Mapeia dados SQLite para PostgreSQL com compatibilidade"""
        mapped = {}
        
        # Campos obrigatórios
        mapped['codigo'] = data.get('codigo', '').upper()
        mapped['nome'] = data.get('nome', f"Empresa {mapped['codigo']}")
        mapped['setor'] = data.get('setor', 'Diversos')
        
        # Mapeamento de nomenclatura: SQLite → PostgreSQL
        field_mapping = {
            'preco_atual': 'current_price',
            'p_l': 'pe_ratio',
            'p_vp': 'pb_ratio',
            'margem_liquida': 'net_margin',
            'divida_liquida_ebitda': 'debt_to_ebitda',
            'ultima_atualizacao_preco': 'last_price_update',
            'ultima_atualizacao_fundamentals': 'last_fundamentals_update'
        }
        
        # Aplicar mapeamento
        for old_field, new_field in field_mapping.items():
            if old_field in data:
                mapped[new_field] = data[old_field]
        
        # Campos diretos (mesmo nome)
        direct_fields = [
            'nome_completo', 'cnpj', 'website', 'descricao', 'ceo',
            'subsetor', 'segmento', 'industria', 'market_cap', 'volume_medio',
            'roe', 'roa', 'roic', 'revenue', 'net_income', 'total_assets',
            'total_equity', 'total_debt', 'cash_and_equivalents',
            'ev_ebitda', 'gross_margin', 'operating_margin'
        ]
        
        for field in direct_fields:
            if field in data:
                mapped[field] = data[field]
        
        # Campos com valores padrão
        mapped.setdefault('status', StockStatusEnum.ACTIVE)
        mapped.setdefault('data_quality', DataQualityEnum.MEDIUM)
        mapped.setdefault('ativo', True)  # Compatibilidade
        
        # Campos calculados
        if 'volume_medio' in data:
            mapped['volume_medio_30d'] = data['volume_medio']
        
        return mapped

    def get_stock_by_code(self, codigo: str) -> Optional[Stock]:
        """Busca ação por código - OTIMIZADO PostgreSQL"""
        with self._get_session() as db:
            return db.query(Stock).filter(
                Stock.codigo == codigo.upper()
            ).first()

    def get_all_stocks(self, active_only: bool = True) -> List[Stock]:
        """Lista todas as ações - OTIMIZADO PostgreSQL"""
        with self._get_session() as db:
            query = db.query(Stock)
            
            if active_only:
                query = query.filter(Stock.status == StockStatusEnum.ACTIVE)
            
            return query.order_by(Stock.nome).all()

    def get_stocks_by_sector(self, setor: str, limit: int = None) -> List[Stock]:
        """Busca ações por setor - OTIMIZADO PostgreSQL"""
        with self._get_session() as db:
            query = db.query(Stock).filter(
                Stock.setor.ilike(f"%{setor}%"),
                Stock.status == StockStatusEnum.ACTIVE
            ).order_by(desc(Stock.market_cap))
            
            if limit:
                query = query.limit(limit)
            
            return query.all()

    def get_top_stocks_by_score(self, limit: int = 20) -> List[Stock]:
        """Top ações por score fundamentalista - OTIMIZADO PostgreSQL"""
        with self._get_session() as db:
            return db.query(Stock).filter(
                Stock.fundamental_score.isnot(None),
                Stock.status == StockStatusEnum.ACTIVE
            ).order_by(
                desc(Stock.fundamental_score)
            ).limit(limit).all()

    def update_stock_prices(self, updates: List[Dict[str, Any]]) -> int:
        """Atualização em lote de preços - BULK UPDATE PostgreSQL"""
        with self._get_session() as db:
            updated_count = 0
            
            for update in updates:
                codigo = update.get('codigo')
                if not codigo:
                    continue
                
                result = db.query(Stock).filter(
                    Stock.codigo == codigo.upper()
                ).update({
                    Stock.current_price: update.get('current_price'),
                    Stock.volume_atual: update.get('volume_atual'),
                    Stock.last_price_update: datetime.now()
                })
                
                updated_count += result
            
            db.commit()
            logger.info(f"Preços atualizados: {updated_count} ações")
            return updated_count

    def search_stocks(self, query: str, limit: int = 10) -> List[Stock]:
        """Busca textual PostgreSQL com trigram"""
        with self._get_session() as db:
            # Busca usando similaridade de trigram (PostgreSQL)
            results = db.query(Stock).filter(
                or_(
                    Stock.codigo.ilike(f"%{query.upper()}%"),
                    Stock.nome.ilike(f"%{query}%"),
                    func.similarity(Stock.nome, query) > 0.3
                ),
                Stock.status == StockStatusEnum.ACTIVE
            ).order_by(
                desc(func.similarity(Stock.nome, query))
            ).limit(limit).all()
            
            return results


class RecommendationRepository(BaseRepository):
    """Repository PostgreSQL para recomendações - OTIMIZADO"""

    def create_recommendation(self, rec_data: Dict[str, Any]) -> Recommendation:
        """Cria nova recomendação PostgreSQL"""
        with self._get_session() as db:
            # Mapear campos SQLite → PostgreSQL
            mapped_data = {
                'stock_id': rec_data.get('stock_id'),
                'recommendation_type': self._map_classification(rec_data.get('classificacao')),
                'fundamental_score': rec_data.get('score_fundamentalista', 0),
                'composite_score': rec_data.get('score_final', 0),
                'entry_price': rec_data.get('preco_entrada'),
                'stop_loss': rec_data.get('stop_loss'),
                'justificativa': rec_data.get('justificativa', ''),
                'is_active': rec_data.get('ativa', True),
                'confidence_level': rec_data.get('confidence_level', 70.0)
            }
            
            recommendation = Recommendation(**mapped_data)
            db.add(recommendation)
            db.commit()
            db.refresh(recommendation)
            
            return recommendation

    def _map_classification(self, classificacao: str) -> RecommendationEnum:
        """Mapeia classificação SQLite para enum PostgreSQL"""
        mapping = {
            'COMPRA FORTE': RecommendationEnum.STRONG_BUY,
            'COMPRA': RecommendationEnum.BUY,
            'NEUTRO': RecommendationEnum.HOLD,
            'VENDA': RecommendationEnum.SELL,
            'VENDA FORTE': RecommendationEnum.STRONG_SELL
        }
        return mapping.get(classificacao, RecommendationEnum.HOLD)

    def get_active_recommendations(self, limit: int = 50) -> List[Recommendation]:
        """Lista recomendações ativas - OTIMIZADO PostgreSQL"""
        with self._get_session() as db:
            return db.query(Recommendation).filter(
                Recommendation.is_active == True
            ).order_by(
                desc(Recommendation.analysis_date)
            ).limit(limit).all()

    def get_recommendations_by_stock(self, stock_id: uuid.UUID) -> List[Recommendation]:
        """Recomendações por ação - OTIMIZADO PostgreSQL"""
        with self._get_session() as db:
            return db.query(Recommendation).filter(
                Recommendation.stock_id == stock_id
            ).order_by(
                desc(Recommendation.analysis_date)
            ).all()


class FundamentalAnalysisRepository(BaseRepository):
    """Repository PostgreSQL para análises fundamentalistas - OTIMIZADO"""

    def create_analysis(self, analysis_data: Dict[str, Any]) -> FundamentalAnalysis:
        """Cria nova análise fundamentalista PostgreSQL"""
        with self._get_session() as db:
            analysis = FundamentalAnalysis(**analysis_data)
            db.add(analysis)
            db.commit()
            db.refresh(analysis)
            return analysis

    def get_latest_analysis_by_stock(self, stock_id: uuid.UUID) -> Optional[FundamentalAnalysis]:
        """Última análise por ação - OTIMIZADO PostgreSQL"""
        with self._get_session() as db:
            return db.query(FundamentalAnalysis).filter(
                FundamentalAnalysis.stock_id == stock_id
            ).order_by(
                desc(FundamentalAnalysis.analysis_date)
            ).first()


class AgentSessionRepository(BaseRepository):
    """Repository PostgreSQL para sessões de agentes - OTIMIZADO"""

    def create_session(self, session_data: Dict[str, Any]) -> AgentSession:
        """Cria nova sessão de agente PostgreSQL"""
        with self._get_session() as db:
            session = AgentSession(**session_data)
            db.add(session)
            db.commit()
            db.refresh(session)
            return session

    def finish_session(self, session_id: str, status: str = "completed", 
                      error_message: str = None) -> bool:
        """Finaliza sessão - OTIMIZADO PostgreSQL"""
        with self._get_session() as db:
            session = db.query(AgentSession).filter(
                AgentSession.session_id == session_id
            ).first()
            
            if session:
                session.finished_at = datetime.now()
                session.status = status
                if error_message:
                    session.error_message = error_message
                
                # Calcular tempo de execução
                if session.started_at:
                    delta = session.finished_at - session.started_at
                    session.execution_time_seconds = delta.total_seconds()
                
                db.commit()
                return True
            return False

    def get_recent_sessions(self, agent_name: str = None, limit: int = 10) -> List[AgentSession]:
        """Sessões recentes - OTIMIZADO PostgreSQL"""
        with self._get_session() as db:
            query = db.query(AgentSession)
            
            if agent_name:
                query = query.filter(AgentSession.agent_name == agent_name)
            
            return query.order_by(
                desc(AgentSession.started_at)
            ).limit(limit).all()


class MarketDataRepository(BaseRepository):
    """Repository PostgreSQL para dados de mercado - OTIMIZADO"""

    def bulk_insert_market_data(self, market_data: List[Dict[str, Any]]) -> int:
        """Inserção em lote de dados de mercado - BULK INSERT PostgreSQL"""
        with self._get_session() as db:
            market_objects = [MarketData(**data) for data in market_data]
            db.bulk_save_objects(market_objects)
            db.commit()
            return len(market_objects)

    def get_latest_market_data(self, stock_id: uuid.UUID, days: int = 30) -> List[MarketData]:
        """Dados de mercado recentes - OTIMIZADO PostgreSQL"""
        with self._get_session() as db:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            return db.query(MarketData).filter(
                MarketData.stock_id == stock_id,
                MarketData.date >= cutoff_date
            ).order_by(desc(MarketData.date)).all()


# ==================== FACTORY FUNCTIONS ====================
def get_stock_repository(db_session: Session = None) -> StockRepository:
    """Factory para StockRepository PostgreSQL"""
    return StockRepository(db_session)


def get_recommendation_repository(db_session: Session = None) -> RecommendationRepository:
    """Factory para RecommendationRepository PostgreSQL"""
    return RecommendationRepository(db_session)


def get_fundamental_repository(db_session: Session = None) -> FundamentalAnalysisRepository:
    """Factory para FundamentalAnalysisRepository PostgreSQL"""
    return FundamentalAnalysisRepository(db_session)


def get_agent_session_repository(db_session: Session = None) -> AgentSessionRepository:
    """Factory para AgentSessionRepository PostgreSQL"""
    return AgentSessionRepository(db_session)


def get_market_data_repository(db_session: Session = None) -> MarketDataRepository:
    """Factory para MarketDataRepository PostgreSQL"""
    return MarketDataRepository(db_session)
