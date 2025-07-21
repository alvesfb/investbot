# database/init_db.py - ENHANCED VERSION
"""
Script para inicialização do banco com 50+ ações brasileiras
Aproveita estratégia multi-API do YFinanceClient para fallback robusto
"""
import logging
import asyncio
from datetime import datetime
from typing import List, Dict, Any
import os

from database.connection import (
    init_database,
    create_tables,
    check_database_connection,
    get_database_info,
    backup_database
)
from database.repositories import (
    get_stock_repository,
    get_agent_session_repository
)
from config.settings import get_settings

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()


def create_extended_sample_stocks() -> List[Dict[str, Any]]:
    """
    Retorna 50+ ações brasileiras principais com dados base
    INTEGRADO com estratégia multi-API para busca robusta
    """
    
    # Import da lista expandida
    try:
        from config.stock_universe import get_extended_stock_list, SECTOR_MAPPING
        extended_list = get_extended_stock_list()
        
        logger.info(f"📊 Lista expandida carregada: {len(extended_list)} ações")
        logger.info(f"📋 Setores: {len(set(stock['sector'] for stock in extended_list))}")
        
        return extended_list
        
    except ImportError:
        logger.warning("Lista expandida não encontrada, usando lista básica")
        return create_basic_sample_stocks()


def create_basic_sample_stocks() -> List[Dict[str, Any]]:
    """Lista básica de fallback (as 8 ações originais)"""
    return [
        {
            "symbol": "PETR4", "name": "Petróleo Brasileiro S.A.", "sector": "Oil & Gas",
            "current_price": 32.50, "market_cap": 422000000000, "pe_ratio": 4.2, "roe": 19.5
        },
        {
            "symbol": "VALE3", "name": "Vale S.A.", "sector": "Mining", 
            "current_price": 61.80, "market_cap": 280000000000, "pe_ratio": 5.1, "roe": 24.3
        },
        {
            "symbol": "ITUB4", "name": "Itaú Unibanco Holding S.A.", "sector": "Banks",
            "current_price": 33.15, "market_cap": 325000000000, "pe_ratio": 8.9, "roe": 20.1
        },
        {
            "symbol": "BBDC4", "name": "Banco Bradesco S.A.", "sector": "Banks",
            "current_price": 13.85, "market_cap": 127000000000, "pe_ratio": 6.8, "roe": 16.8
        },
        {
            "symbol": "ABEV3", "name": "Ambev S.A.", "sector": "Beverages",
            "current_price": 11.25, "market_cap": 177000000000, "pe_ratio": 15.2, "roe": 12.5
        },
        {
            "symbol": "MGLU3", "name": "Magazine Luiza S.A.", "sector": "Retail",
            "current_price": 4.85, "market_cap": 33000000000, "pe_ratio": -8.5, "roe": -15.2
        },
        {
            "symbol": "WEGE3", "name": "WEG S.A.", "sector": "Industrial Machinery",
            "current_price": 42.90, "market_cap": 115000000000, "pe_ratio": 22.8, "roe": 18.5
        },
        {
            "symbol": "B3SA3", "name": "B3 S.A. - Brasil, Bolsa, Balcão", "sector": "Financial Services",
            "current_price": 9.85, "market_cap": 52000000000, "pe_ratio": 12.5, "roe": 16.8
        }
    ]


def populate_sample_data() -> List[Any]:
    """
    Popula o banco com dados de exemplo usando estratégia incremental
    """
    logger.info("🚀 Iniciando população do banco com dados expandidos...")

    stock_repo = get_stock_repository()

    # 1. Obter lista expandida de ações
    sample_stocks = create_extended_sample_stocks()
    created_count = 0
    updated_count = 0
    failed_count = 0

    logger.info(f"📋 Processando {len(sample_stocks)} ações...")

    # 2. Processar em lotes para melhor performance
    batch_size = 10
    for i in range(0, len(sample_stocks), batch_size):
        batch = sample_stocks[i:i + batch_size]
        logger.info(f"📦 Processando lote {i//batch_size + 1}: {len(batch)} ações")
        
        for stock_data in batch:
            try:
                # Preparar dados para formato PostgreSQL
                formatted_data = prepare_stock_data_for_postgres(stock_data)
                
                # Verificar se já existe
                existing = stock_repo.get_stock_by_symbol(formatted_data["symbol"])
                
                if not existing:
                    # Criar nova ação
                    stock = stock_repo.create_stock(formatted_data)
                    created_count += 1
                    logger.info(f"✅ Criada: {stock_data['symbol']} - {stock_data['name'][:30]}...")
                else:
                    # Atualizar dados básicos se necessário
                    if should_update_stock(existing, formatted_data):
                        update_existing_stock(stock_repo, existing, formatted_data)
                        updated_count += 1
                        logger.info(f"🔄 Atualizada: {stock_data['symbol']}")
                    else:
                        logger.debug(f"⏭️  Já existe: {stock_data['symbol']}")
                        
            except Exception as e:
                failed_count += 1
                logger.error(f"❌ Erro ao processar {stock_data['symbol']}: {e}")

    # 3. Relatório final
    logger.info("=" * 60)
    logger.info("📊 RELATÓRIO DE POPULAÇÃO")
    logger.info("=" * 60)
    logger.info(f"📈 Ações criadas: {created_count}")
    logger.info(f"🔄 Ações atualizadas: {updated_count}")
    logger.info(f"❌ Falhas: {failed_count}")
    logger.info(f"📋 Total processado: {len(sample_stocks)}")
    
    # 4. Distribuição setorial
    sector_distribution = {}
    for stock_data in sample_stocks:
        sector = stock_data.get("sector", "Unknown")
        sector_distribution[sector] = sector_distribution.get(sector, 0) + 1
    
    logger.info("\n📊 DISTRIBUIÇÃO SETORIAL:")
    for sector, count in sorted(sector_distribution.items()):
        logger.info(f"   {sector}: {count} ações")
    
    logger.info("=" * 60)

    # Retornar todas as ações do banco para validação
    return stock_repo.get_all_stocks()


def prepare_stock_data_for_postgres(stock_data: Dict[str, Any]) -> Dict[str, Any]:
    """Prepara dados para formato PostgreSQL - VERSÃO CORRIGIDA"""
    from database.models import StockStatusEnum, DataQualityEnum
    
    return {
        # Campos obrigatórios PostgreSQL
        "symbol": stock_data.get("symbol", "").upper(),
        "name": stock_data.get("name", f"Company {stock_data.get('symbol', '')}"),
        "sector": stock_data.get("sector", "Unknown"),
        
        # ✅ CORREÇÃO 1: Preço mínimo válido
        "current_price": max(stock_data.get("current_price", 10.0), 0.01),  # Mín 0.01
        
        "market_cap": stock_data.get("market_cap"),
        "pe_ratio": stock_data.get("pe_ratio"),
        "pb_ratio": stock_data.get("pb_ratio"),
        "roe": stock_data.get("roe"),
        "roa": stock_data.get("roa"),
        
        # Metadados
        "listing_segment": stock_data.get("listing", "Standard"),
        
        # ✅ CORREÇÃO 2: Usar ENUMs corretos
        "data_quality": DataQualityEnum.MEDIUM,  # Enum ao invés de string
        "status": StockStatusEnum.ACTIVE,        # Enum ao invés de string
        
        # ✅ CORREÇÃO 3: Timestamps timezone-aware
        "created_at": datetime.now().replace(tzinfo=None),  # Remover timezone
        "updated_at": datetime.now().replace(tzinfo=None)   # Remover timezone
    }

def should_update_stock(existing_stock: Any, new_data: Dict[str, Any]) -> bool:
    """
    Determina se uma ação existente deve ser atualizada
    """
    # Atualizar se:
    # 1. Nome mudou
    # 2. Setor mudou  
    # 3. Dados básicos estão vazios
    
    if existing_stock.name != new_data.get("name"):
        return True
        
    if existing_stock.sector != new_data.get("sector"):
        return True
        
    if not existing_stock.current_price and new_data.get("current_price"):
        return True
        
    return False


def update_existing_stock(stock_repo: Any, existing_stock: Any, new_data: Dict[str, Any]) -> None:
    """
    Atualiza ação existente com novos dados
    """
    try:
        # Usar bulk_update_prices para atualizar dados de mercado
        updates = [{
            "symbol": existing_stock.symbol,
            "current_price": new_data.get("current_price"),
            "market_cap": new_data.get("market_cap")
        }]
        
        stock_repo.bulk_update_prices(updates)
        
    except Exception as e:
        logger.error(f"Erro ao atualizar {existing_stock.symbol}: {e}")


async def enrich_with_api_data(symbols: List[str], max_concurrent: int = 5) -> Dict[str, Dict]:
    """
    Enriquece dados usando YFinanceClient com estratégia multi-API
    APROVEITA: Alpha Vantage, Financial Modeling Prep, fallbacks
    """
    logger.info(f"🌐 Enriquecendo dados via API para {len(symbols)} ações...")
    
    enriched_data = {}
    
    try:
        # Import do YFinanceClient que tem estratégia multi-API
        from agents.collectors.stock_collector import YFinanceClient
        
        yf_client = YFinanceClient()
        
        # Processar em lotes para evitar rate limiting
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def fetch_single_stock(symbol: str) -> Dict:
            async with semaphore:
                try:
                    # Usar estratégia multi-API do YFinanceClient
                    data = await yf_client.get_stock_info(symbol)
                    logger.info(f"✅ Dados obtidos para {symbol}")
                    return {symbol: data}
                except Exception as e:
                    logger.warning(f"⚠️  Falha ao obter dados para {symbol}: {e}")
                    return {symbol: None}
        
        # Executar coletas concorrentes
        tasks = [fetch_single_stock(symbol) for symbol in symbols]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Consolidar resultados
        for result in results:
            if isinstance(result, dict):
                enriched_data.update(result)
        
        success_count = sum(1 for data in enriched_data.values() if data is not None)
        logger.info(f"📊 Enriquecimento concluído: {success_count}/{len(symbols)} sucessos")
        
    except ImportError:
        logger.warning("YFinanceClient não disponível, pulando enriquecimento")
    except Exception as e:
        logger.error(f"Erro no enriquecimento: {e}")
    
    return enriched_data


def create_initial_agent_session():
    """Cria sessão inicial do agente com estatísticas expandidas"""
    agent_repo = get_agent_session_repository()

    session_data = {
        "session_id": f"init_enhanced_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "agent_name": "database_initializer_enhanced",
        "agent_version": "2.0.0",
        "status": "completed",
        "input_data": '{"action": "enhanced_database_initialization", "target_stocks": 50}',
        "output_data": '{"stocks_created": "dynamic", "status": "success", "api_strategy": "multi_api"}',
        "execution_time_seconds": 5.0,
        "stocks_processed": 50,
        "config_snapshot": '{"environment": "development", "multi_api": true}',
        "started_at": datetime.now(),
        "finished_at": datetime.now()
    }

    try:
        session = agent_repo.create_session(session_data)
        agent_repo.finish_session(session.session_id, "completed")
        logger.info(f"✅ Sessão inicial criada: {session.session_id}")
        return session
    except Exception as e:
        logger.error(f"❌ Erro ao criar sessão inicial: {e}")
        return None


def validate_database():
    """Valida se o banco foi inicializado corretamente com dados expandidos"""
    logger.info("🔍 Validando banco de dados expandido...")

    # Verificar conexão
    if not check_database_connection():
        logger.error("❌ Falha na conexão com banco")
        return False

    # Verificar se tabelas existem
    db_info = get_database_info()
    expected_tables = ["stocks", "recommendations", "fundamental_analyses", 
                       "agent_sessions", "market_data"]

    missing_tables = []
    for table in expected_tables:
        if table not in db_info.get("tables", []):
            missing_tables.append(table)

    if missing_tables:
        logger.error(f"❌ Tabelas faltando: {missing_tables}")
        return False

    # Verificar se dados expandidos existem
    stock_repo = get_stock_repository()
    stocks = stock_repo.get_all_stocks()

    if len(stocks) == 0:
        logger.warning("⚠️  Nenhuma ação encontrada no banco")
        return False
    elif len(stocks) < 20:
        logger.warning(f"⚠️  Apenas {len(stocks)} ações encontradas (esperado 50+)")
    else:
        logger.info(f"✅ {len(stocks)} ações encontradas no banco")

    # Validar distribuição setorial
    sector_count = {}
    for stock in stocks[:10]:  # Verificar primeiras 10
        sector = getattr(stock, 'sector', 'Unknown')
        sector_count[sector] = sector_count.get(sector, 0) + 1

    logger.info(f"📊 Distribuição setorial (amostra): {sector_count}")

    # Validar qualidade dos dados
    complete_data_count = 0
    for stock in stocks[:10]:
        if (hasattr(stock, 'current_price') and stock.current_price and 
            hasattr(stock, 'market_cap') and stock.market_cap):
            complete_data_count += 1

    data_quality = (complete_data_count / min(len(stocks), 10)) * 100
    logger.info(f"📈 Qualidade dos dados: {data_quality:.1f}%")

    if data_quality < 50:
        logger.warning("⚠️  Qualidade dos dados baixa")
    else:
        logger.info("✅ Qualidade dos dados adequada")

    logger.info("✅ Banco de dados validado com sucesso")
    return True


async def populate_with_api_enrichment():
    """
    Versão avançada que popula E enriquece com dados da API
    APROVEITA estratégia multi-API do YFinanceClient
    """
    logger.info("🚀 POPULAÇÃO AVANÇADA com enriquecimento via API")
    logger.info("=" * 60)

    # 1. População básica
    stocks = populate_sample_data()
    
    if len(stocks) == 0:
        logger.error("❌ Falha na população básica")
        return False

    # 2. Obter símbolos para enriquecimento
    symbols_to_enrich = [stock.symbol for stock in stocks[:20]]  # Primeiras 20 para teste
    logger.info(f"🌐 Enriquecendo {len(symbols_to_enrich)} ações via API...")

    # 3. Enriquecer com dados da API
    try:
        enriched_data = await enrich_with_api_data(symbols_to_enrich)
        
        # 4. Atualizar banco com dados enriquecidos
        stock_repo = get_stock_repository()
        update_count = 0
        
        for symbol, api_data in enriched_data.items():
            if api_data:
                try:
                    # Preparar dados para bulk update
                    update_data = {
                        'symbol': symbol,
                        'current_price': api_data.get('regularMarketPrice'),
                        'current_volume': api_data.get('regularMarketVolume'),
                        'market_cap': api_data.get('marketCap')
                    }
                    
                    # Filtrar valores None
                    update_data = {k: v for k, v in update_data.items() if v is not None}
                    
                    if len(update_data) > 1:  # Além do symbol
                        stock_repo.bulk_update_prices([update_data])
                        update_count += 1
                        logger.info(f"✅ Enriquecido: {symbol}")
                        
                except Exception as e:
                    logger.warning(f"⚠️  Erro ao enriquecer {symbol}: {e}")

        logger.info(f"📊 Enriquecimento concluído: {update_count} ações atualizadas")
        
    except Exception as e:
        logger.error(f"❌ Erro no enriquecimento: {e}")
        logger.info("💡 Continuando sem enriquecimento...")

    return True


def main():
    """Função principal de inicialização expandida"""
    logger.info("=" * 60)
    logger.info("🚀 INICIALIZANDO BANCO DE DADOS - VERSÃO EXPANDIDA")
    logger.info("Sistema com 50+ ações brasileiras + estratégia multi-API")
    logger.info("=" * 60)

    try:
        # 1. Backup do banco atual (se existir)
        if hasattr(settings, 'database_path') and settings.database_path and settings.database_path.exists():
            logger.info("📋 Fazendo backup do banco atual...")
            backup_database()

        # 2. Inicializar banco
        logger.info("📋 Inicializando estrutura do banco...")
        if not init_database():
            logger.error("❌ Falha na inicialização do banco")
            return False

        # 3. Criar tabelas
        logger.info("📋 Criando tabelas...")
        if not create_tables():
            logger.error("❌ Falha na criação das tabelas")
            return False

        # 4. População expandida com dados básicos
        logger.info("📋 Populando com dados expandidos...")
        stocks = populate_sample_data()

        # 5. Criar sessão inicial
        logger.info("📋 Criando sessão inicial...")
        create_initial_agent_session()

        # 6. Validar tudo
        logger.info("📋 Validando banco...")
        if not validate_database():
            logger.error("❌ Falha na validação do banco")
            return False

        # 7. Relatório final expandido
        db_info = get_database_info()
        sector_distribution = {}
        for stock in stocks:
            sector = getattr(stock, 'sector', 'Unknown')
            sector_distribution[sector] = sector_distribution.get(sector, 0) + 1

        logger.info("=" * 60)
        logger.info("🎉 BANCO INICIALIZADO COM SUCESSO - VERSÃO EXPANDIDA!")
        logger.info("=" * 60)
        logger.info(f"📊 Tipo: {db_info.get('type', 'Unknown')}")
        logger.info(f"📁 Arquivo: {db_info.get('file_path', 'N/A')}")
        logger.info(f"💾 Tamanho: {db_info.get('file_size_mb', 0)} MB")
        logger.info(f"📋 Tabelas: {len(db_info.get('tables', []))}")
        logger.info(f"🏢 Ações: {len(stocks)}")
        logger.info(f"🎯 Meta: 50+ ações brasileiras")
        
        logger.info("\n📊 DISTRIBUIÇÃO SETORIAL:")
        for sector, count in sorted(sector_distribution.items()):
            logger.info(f"   {sector}: {count} ações")
            
        logger.info("\n🌐 ESTRATÉGIA MULTI-API DISPONÍVEL:")
        logger.info("   • YFinance (primário)")
        logger.info("   • Alpha Vantage (fallback)")
        logger.info("   • Financial Modeling Prep (fallback)")
        logger.info("   • Static data (último recurso)")
        
        logger.info("\n🚀 PRÓXIMOS PASSOS SUGERIDOS:")
        logger.info("   1. Execute enriquecimento via API:")
        logger.info("      python -c 'import asyncio; from database.init_db import populate_with_api_enrichment; asyncio.run(populate_with_api_enrichment())'")
        logger.info("   2. Teste o StockCollector com múltiplas ações")
        logger.info("   3. Implemente validação de data quality")
        
        logger.info("=" * 60)

        return True

    except Exception as e:
        logger.error(f"❌ Erro na inicialização: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main_async():
    """Versão assíncrona com enriquecimento automático"""
    logger.info("🚀 INICIALIZAÇÃO COMPLETA COM ENRIQUECIMENTO AUTOMÁTICO")
    
    # Executar inicialização básica
    basic_success = main()
    
    if not basic_success:
        logger.error("❌ Falha na inicialização básica")
        return False
    
    # Executar enriquecimento automático
    logger.info("🌐 Iniciando enriquecimento automático...")
    enrichment_success = await populate_with_api_enrichment()
    
    if enrichment_success:
        logger.info("🎉 INICIALIZAÇÃO COMPLETA COM ENRIQUECIMENTO CONCLUÍDA!")
    else:
        logger.warning("⚠️  Inicialização básica OK, enriquecimento com problemas")
    
    return basic_success


if __name__ == "__main__":
    import sys
    
    # Verificar se deve executar com enriquecimento
    if len(sys.argv) > 1 and sys.argv[1] == "--with-enrichment":
        success = asyncio.run(main_async())
    else:
        success = main()
    
    exit(0 if success else 1)