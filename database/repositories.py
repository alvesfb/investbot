# database/repositories.py
"""
Repository pattern para acesso aos dados
Abstrai o acesso ao banco de dados com métodos de alto nível
"""
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_, func
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from database.models import (Stock, Recommendation,
                             FundamentalAnalysis, AgentSession, MarketData)
from database.connection import get_db_session

logger = logging.getLogger(__name__)


class BaseRepository:
    """Classe base para repositories"""

    def __init__(self, db_session: Session = None):
        self.db_session = db_session

    def _get_session(self):
        """Retorna sessão do banco (injetada ou nova)"""
        if self.db_session:
            return self.db_session
        return get_db_session()


class StockRepository(BaseRepository):
    """Repository para operações com ações"""

    def create_stock(self, stock_data: Dict[str, Any]) -> Stock:
        """Cria uma nova ação"""
        with self._get_session() as db:
            stock = Stock(**stock_data)
            db.add(stock)
            db.commit()
            db.refresh(stock)
            logger.info(f"Ação criada: {stock.codigo}")
            return stock

    def get_stock_by_code(self, codigo: str) -> Optional[Stock]:
        """Busca ação por código"""
        with self._get_session() as db:
            return db.query(Stock).filter(Stock.codigo ==
                                          codigo.upper()).first()

    def get_stock_by_id(self, stock_id: int) -> Optional[Stock]:
        """Busca ação por ID"""
        with self._get_session() as db:
            return db.query(Stock).filter(Stock.id == stock_id).first()

    def get_all_stocks(self, ativo_apenas: bool = True) -> List[Stock]:
        """Retorna todas as ações"""
        with self._get_session() as db:
            query = db.query(Stock)
            if ativo_apenas:
                query = query.filter(Stock.ativo is True)
            return query.order_by(Stock.codigo).all()

    def get_stocks_by_sector(self,
                             setor: str,
                             ativo_apenas: bool = True) -> List[Stock]:
        """Retorna ações de um setor específico"""
        with self._get_session() as db:
            query = db.query(Stock).filter(Stock.setor == setor)
            if ativo_apenas:
                query = query.filter(Stock.ativo is True)
            return query.order_by(Stock.codigo).all()

    def get_stocks_for_analysis(self,
                                min_market_cap: float = None,
                                min_volume: float = None,
                                exclude_penny_stocks: bool = True,
                                penny_threshold: float = 5.0) -> List[Stock]:
        """Retorna ações filtradas para análise"""
        with self._get_session() as db:
            query = db.query(Stock).filter(Stock.ativo is True)

            if min_market_cap:
                query = query.filter(Stock.market_cap >= min_market_cap)

            if min_volume:
                query = query.filter(Stock.volume_medio >= min_volume)

            if exclude_penny_stocks:
                query = query.filter(Stock.preco_atual >= penny_threshold)

            return query.order_by(desc(Stock.market_cap)).all()

    def update_stock_price(self,
                           codigo: str,
                           preco: float,
                           volume: float = None) -> bool:
        """Atualiza preço atual da ação"""
        with self._get_session() as db:
            stock = db.query(Stock).filter(Stock.codigo ==
                                           codigo.upper()).first()
            if stock:
                stock.preco_atual = preco
                if volume:
                    stock.volume_medio = volume
                stock.ultima_atualizacao_preco = datetime.now()
                db.commit()
                return True
            return False

    def update_stock_fundamentals(self,
                                  codigo: str,
                                  fundamentals: Dict[str, Any]) -> bool:
        """Atualiza dados fundamentalistas da ação"""
        with self._get_session() as db:
            stock = db.query(Stock).filter(Stock.codigo ==
                                           codigo.upper()).first()
            if stock:
                for key, value in fundamentals.items():
                    if hasattr(stock, key):
                        setattr(stock, key, value)
                stock.ultima_atualizacao_fundamentals = datetime.now()
                db.commit()
                return True
            return False

    def search_stocks(self, query: str) -> List[Stock]:
        """Busca ações por código ou nome"""
        with self._get_session() as db:
            search_term = f"%{query.upper()}%"
            return db.query(Stock).filter(
                or_(
                    Stock.codigo.like(search_term),
                    Stock.nome.like(search_term)
                )
            ).filter(Stock.ativo is True).limit(20).all()

    def get_stock_count_by_sector(self) -> List[Dict[str, Any]]:
        """Retorna contagem de ações por setor"""
        with self._get_session() as db:
            result = db.query(
                Stock.setor,
                func.count(Stock.id).label('count')
            ).filter(
                Stock.ativo is True
            ).group_by(Stock.setor).all()

            return [{"setor": setor,
                     "count": count} for setor, count in result]


class RecommendationRepository(BaseRepository):
    """Repository para operações com recomendações"""

    def create_recommendation(self,
                              recommendation_data:
                              Dict[str, Any]) -> Recommendation:
        """Cria uma nova recomendação"""
        with self._get_session() as db:
            recommendation = Recommendation(**recommendation_data)
            db.add(recommendation)
            db.commit()
            db.refresh(recommendation)
            logger.info(f"Recomendação \
                         criada: \
                        {recommendation.stock.codigo} - \
                            {recommendation.classificacao}")
            return recommendation

    def get_latest_recommendations(self,
                                   limit: int = 20,
                                   ativas_apenas: bool = True) -> List[
                                       Recommendation]:
        """Retorna as recomendações mais recentes"""
        with self._get_session() as db:
            query = db.query(Recommendation).join(Stock)
            if ativas_apenas:
                query = query.filter(Recommendation.ativa is True)
            return query.order_by(
                desc(Recommendation.data_analise)).limit(limit).all()

    def get_recommendations_by_stock(self,
                                     codigo: str,
                                     limit: int = 10) -> List[Recommendation]:
        """Retorna recomendações de uma ação específica"""
        with self._get_session() as db:
            return db.query(Recommendation).join(Stock).filter(
                Stock.codigo == codigo.upper()
            ).order_by(desc(Recommendation.data_analise)).limit(limit).all()

    def get_recommendations_by_classification(self, classificacao: str,
                                              ativas_apenas: bool = True,
                                              limit: int = 50) -> List[
                                                  Recommendation]:
        """Retorna recomendações por classificação (COMPRA, VENDA, etc.)"""
        with self._get_session() as db:
            query = db.query(Recommendation).join(Stock).filter(
                Recommendation.classificacao == classificacao.upper()
            )
            if ativas_apenas:
                query = query.filter(Recommendation.ativa is True)
            return query.order_by(
                desc(Recommendation.score_final)).limit(limit).all()

    def get_recommendations_by_date_range(self, start_date: datetime,
                                          end_date: datetime) -> List[
                                              Recommendation]:
        """Retorna recomendações em um período"""
        with self._get_session() as db:
            return db.query(Recommendation).filter(
                and_(
                    Recommendation.data_analise >= start_date,
                    Recommendation.data_analise <= end_date
                )
            ).order_by(desc(Recommendation.data_analise)).all()

    def get_top_recommendations(self, limit: int = 10,
                                classificacao: str = None) -> List[
                                    Recommendation]:
        """Retorna as melhores recomendações por score"""
        with self._get_session() as db:
            query = db.query(Recommendation).join(Stock).filter(
                Recommendation.ativa is True
            )
            if classificacao:
                query = query.filter(
                    Recommendation.classificacao == classificacao.upper())
            return query.order_by(
                desc(Recommendation.score_final)).limit(limit).all()

    def deactivate_old_recommendations(self, days_old: int = 30) -> int:
        """Desativa recomendações antigas"""
        with self._get_session() as db:
            cutoff_date = datetime.now() - timedelta(days=days_old)
            count = db.query(Recommendation).filter(
                and_(
                    Recommendation.data_analise < cutoff_date,
                    Recommendation.ativa is True
                )
            ).update({"ativa": False})
            db.commit()
            logger.info(f"Desativadas {count} recomendações antigas")
            return count

    def get_recommendation_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas das recomendações"""
        with self._get_session() as db:
            # Contagem por classificação
            class_stats = db.query(
                Recommendation.classificacao,
                func.count(Recommendation.id).label('count')
            ).filter(
                Recommendation.ativa is True
            ).group_by(Recommendation.classificacao).all()

            # Score médio
            avg_score = db.query(func.avg(Recommendation.score_final)).filter(
                Recommendation.ativa is True
            ).scalar()

            # Total de recomendações ativas
            total_ativas = db.query(func.count(Recommendation.id)).filter(
                Recommendation.ativa is True
            ).scalar()

            # Recomendações dos últimos 7 dias
            week_ago = datetime.now() - timedelta(days=7)
            recent_count = db.query(func.count(Recommendation.id)).filter(
                Recommendation.data_analise >= week_ago
            ).scalar()

            return {
                "total_ativas": total_ativas,
                "recentes_7_dias": recent_count,
                "score_medio": round(avg_score, 2) if avg_score else 0,
                "por_classificacao": {classificacao: count for
                                      classificacao, count in class_stats}
            }


class FundamentalAnalysisRepository(BaseRepository):
    """Repository para análises fundamentalistas"""

    def create_analysis(self,
                        analysis_data: Dict[str, Any]) -> FundamentalAnalysis:
        """Cria nova análise fundamentalista"""
        with self._get_session() as db:
            analysis = FundamentalAnalysis(**analysis_data)
            db.add(analysis)
            db.commit()
            db.refresh(analysis)
            return analysis

    def get_latest_analysis_by_stock(self,
                                     codigo: str) -> Optional[
                                         FundamentalAnalysis]:
        """Retorna a análise mais recente de uma ação"""
        with self._get_session() as db:
            return db.query(FundamentalAnalysis).join(Stock).filter(
                Stock.codigo == codigo.upper()
            ).order_by(desc(FundamentalAnalysis.data_analise)).first()

    def get_sector_analysis(self,
                            setor: str,
                            limit: int = 50) -> List[FundamentalAnalysis]:
        """Retorna análises de um setor específico"""
        with self._get_session() as db:
            # Subquery para pegar a análise mais recente de cada ação
            latest_analysis = db.query(
                FundamentalAnalysis.stock_id,
                func.max(FundamentalAnalysis.data_analise).label('max_date')
            ).group_by(FundamentalAnalysis.stock_id).subquery()

            return db.query(FundamentalAnalysis).join(Stock).join(
                latest_analysis,
                and_(
                    FundamentalAnalysis.stock_id == latest_analysis.c.stock_id,
                    FundamentalAnalysis.data_analise == (latest_analysis.c.
                                                         max_date)
                )
            ).filter(
                Stock.setor == setor
            ).order_by(
                desc(FundamentalAnalysis.score_total)).limit(limit).all()

    def get_top_fundamental_scores(self,
                                   limit: int = 20) -> List[
                                       FundamentalAnalysis]:
        """Retorna as melhores análises fundamentalistas"""
        with self._get_session() as db:
            # Análises mais recentes de cada ação
            latest_analysis = db.query(
                FundamentalAnalysis.stock_id,
                func.max(FundamentalAnalysis.data_analise).label('max_date')
            ).group_by(FundamentalAnalysis.stock_id).subquery()

            return db.query(FundamentalAnalysis).join(Stock).join(
                latest_analysis,
                and_(
                    FundamentalAnalysis.stock_id == latest_analysis.c.stock_id,
                    FundamentalAnalysis.data_analise == (latest_analysis.c.
                                                         max_date)
                )
            ).filter(
                Stock.ativo is True
            ).order_by(
                desc(FundamentalAnalysis.score_total)).limit(limit).all()


class AgentSessionRepository(BaseRepository):
    """Repository para sessões dos agentes"""

    def create_session(self, session_data: Dict[str, Any]) -> AgentSession:
        """Cria nova sessão de agente"""
        with self._get_session() as db:
            session = AgentSession(**session_data)
            db.add(session)
            db.commit()
            db.refresh(session)
            return session

    def update_session(self,
                       session_id: str,
                       update_data: Dict[str, Any]) -> bool:
        """Atualiza dados de uma sessão"""
        with self._get_session() as db:
            session = db.query(AgentSession).filter(
                AgentSession.session_id == session_id
            ).first()
            if session:
                for key, value in update_data.items():
                    if hasattr(session, key):
                        setattr(session, key, value)
                db.commit()
                return True
            return False

    def finish_session(self, session_id: str, status: str = "completed",
                       error_message: str = None) -> bool:
        """Finaliza uma sessão"""
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

    def get_recent_sessions(self, agent_name: str = None,
                            limit: int = 20) -> List[AgentSession]:
        """Retorna sessões recentes"""
        with self._get_session() as db:
            query = db.query(AgentSession)
            if agent_name:
                query = query.filter(AgentSession.agent_name == agent_name)
            return query.order_by(
                desc(AgentSession.started_at)).limit(limit).all()

    def get_session_statistics(self, days: int = 7) -> Dict[str, Any]:
        """Retorna estatísticas das sessões"""
        with self._get_session() as db:
            start_date = datetime.now() - timedelta(days=days)

            # Sessões por agente
            agent_stats = db.query(
                AgentSession.agent_name,
                func.count(AgentSession.id).label('count'),
                func.avg(AgentSession.execution_time_seconds).label('avg_time')
            ).filter(
                AgentSession.started_at >= start_date
            ).group_by(AgentSession.agent_name).all()

            # Sessões por status
            status_stats = db.query(
                AgentSession.status,
                func.count(AgentSession.id).label('count')
            ).filter(
                AgentSession.started_at >= start_date
            ).group_by(AgentSession.status).all()

            return {
                "period_days": days,
                "por_agente": {
                    agent: {
                        "count": count,
                        "avg_time_seconds": round(
                            avg_time, 2) if avg_time else 0
                    }
                    for agent, count, avg_time in agent_stats
                },
                "por_status": {status: count for status, count in status_stats}
            }


class MarketDataRepository(BaseRepository):
    """Repository para dados de mercado (preços históricos)"""

    def create_market_data(self, data_list: List[Dict[str, Any]]) -> int:
        """Cria dados de mercado em lote"""
        with self._get_session() as db:
            market_data_objects = [MarketData(**data) for data in data_list]
            db.add_all(market_data_objects)
            db.commit()
            return len(market_data_objects)

    def get_market_data_by_stock(self, codigo: str,
                                 start_date: datetime = None,
                                 end_date: datetime = None,
                                 limit: int = 252) -> List[
                                     MarketData]:  # 252 = ~1 ano útil
        """Retorna dados de mercado de uma ação"""
        with self._get_session() as db:
            query = db.query(MarketData).join(Stock).filter(
                Stock.codigo == codigo.upper()
            )

            if start_date:
                query = query.filter(MarketData.data >= start_date)
            if end_date:
                query = query.filter(MarketData.data <= end_date)

            return query.order_by(desc(MarketData.data)).limit(limit).all()

    def get_latest_prices(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Retorna os preços mais recentes de várias ações"""
        with self._get_session() as db:
            # Subquery para data mais recente de cada ação
            latest_dates = db.query(
                MarketData.stock_id,
                func.max(MarketData.data).label('max_date')
            ).group_by(MarketData.stock_id).subquery()

            result = db.query(
                Stock.codigo,
                Stock.nome,
                MarketData.fechamento,
                MarketData.volume,
                MarketData.data
            ).join(MarketData).join(
                latest_dates,
                and_(
                    MarketData.stock_id == latest_dates.c.stock_id,
                    MarketData.data == latest_dates.c.max_date
                )
            ).filter(
                Stock.ativo is True
            ).order_by(desc(MarketData.data)).limit(limit).all()

            return [
                {
                    "codigo": codigo,
                    "nome": nome,
                    "preco": fechamento,
                    "volume": volume,
                    "data": data
                }
                for codigo, nome, fechamento, volume, data in result
            ]


# Factory functions para facilitar uso
def get_stock_repository(db_session: Session = None) -> StockRepository:
    """Factory para StockRepository"""
    return StockRepository(db_session)


def get_recommendation_repository(
        db_session: Session = None) -> RecommendationRepository:
    """Factory para RecommendationRepository"""
    return RecommendationRepository(db_session)


def get_fundamental_repository(
        db_session: Session = None) -> FundamentalAnalysisRepository:
    """Factory para FundamentalAnalysisRepository"""
    return FundamentalAnalysisRepository(db_session)


def get_agent_session_repository(
        db_session: Session = None) -> AgentSessionRepository:
    """Factory para AgentSessionRepository"""
    return AgentSessionRepository(db_session)


def get_market_data_repository(
        db_session: Session = None) -> MarketDataRepository:
    """Factory para MarketDataRepository"""
    return MarketDataRepository(db_session)
