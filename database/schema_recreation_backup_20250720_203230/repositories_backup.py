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
