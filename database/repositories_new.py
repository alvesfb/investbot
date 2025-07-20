# database/repositories_new.py - COM MAPEAMENTO AUTOMÁTICO
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
    
    PT_TO_EN = {
        'codigo': 'symbol',
        'nome': 'name',
        'nome_completo': 'long_name',
        'setor': 'sector',
        'industria': 'industry',
        'preco_atual': 'current_price',
        'volume_medio': 'average_volume_30d',
        'p_l': 'pe_ratio',
        'p_vp': 'pb_ratio',
        'margem_liquida': 'net_margin',
        'ativo': 'status',
        'justificativa': 'rationale',
        'classificacao': 'recommendation_type',
        'data_analise': 'analysis_date',
        'preco_entrada': 'entry_price',
        'ativa': 'is_active'
    }
    
    EN_TO_PT = {v: k for k, v in PT_TO_EN.items()}
    
    @classmethod
    def map_to_english(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Converte campos português → inglês"""
        mapped = {}
        for key, value in data.items():
            english_key = cls.PT_TO_EN.get(key, key)
            
            # Conversões especiais
            if key == 'ativo' and isinstance(value, bool):
                mapped['status'] = StockStatusEnum.ACTIVE if value else StockStatusEnum.SUSPENDED
            elif key == 'classificacao' and isinstance(value, str):
                mapping = {
                    'COMPRA FORTE': RecommendationEnum.STRONG_BUY,
                    'COMPRA': RecommendationEnum.BUY,
                    'NEUTRO': RecommendationEnum.HOLD,
                    'VENDA': RecommendationEnum.SELL,
                    'VENDA FORTE': RecommendationEnum.STRONG_SELL
                }
                mapped['recommendation_type'] = mapping.get(value, RecommendationEnum.HOLD)
            else:
                mapped[english_key] = value
                
        return mapped
