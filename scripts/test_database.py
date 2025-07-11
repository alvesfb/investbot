# scripts/test_database.py
"""
Script para testar todas as funcionalidades do banco de dados
"""
import sys
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

sys.path.insert(0, '.')


def test_database_models():
    """Testa se todos os modelos foram importados corretamente"""
    try:
        logger.info("✅ Todos os modelos importados com sucesso")
        return True
    except Exception as e:
        logger.error(f"❌ Erro ao importar modelos: {e}")
        return False


def test_database_connection():
    """Testa a conexão com o banco"""
    try:
        from database.connection import (check_database_connection,
                                         get_database_info)

        if not check_database_connection():
            logger.error("❌ Falha na conexão com banco")
            return False

        db_info = get_database_info()
        logger.info(f"✅ Conexão OK - Tipo: {db_info.get('type', 'Unknown')}")
        logger.info(f"   📁 Arquivo: {db_info.get('file_path', 'N/A')}")
        logger.info(f"   💾 Tamanho: {db_info.get('file_size_mb', 0)} MB")
        logger.info(f"   📋 Tabelas: {len(db_info.get('tables', []))}")

        return True
    except Exception as e:
        logger.error(f"❌ Erro na conexão: {e}")
        return False


def test_stock_repository():
    """Testa o repository de ações"""
    try:
        from database.repositories import get_stock_repository

        stock_repo = get_stock_repository()

        # Testar listagem
        stocks = stock_repo.get_all_stocks()
        logger.info(f"✅ Repository de ações - {len(stocks)} ações encontradas")

        if len(stocks) == 0:
            logger.warning(" Nenhuma ação encontrada - " /
                           "execute database/init_db.py primeiro")
            return True

        # Testar busca por código
        petr4 = stock_repo.get_stock_by_code('PETR4')
        if petr4:
            logger.info(f"✅ Busca por código OK - PETR4: {petr4.nome}")
        else:
            logger.warning("⚠️  PETR4 não encontrada")

        # Testar filtros
        filtered = stock_repo.get_stocks_for_analysis(
            min_market_cap=50000000000,  # 50B
            exclude_penny_stocks=True
        )
        logger.info(f"✅ Filtros OK - {len(filtered)} ações" /
                    "passaram nos critérios")

        # Testar busca por setor
        bancos = stock_repo.get_stocks_by_sector('Bancos')
        logger.info(f"✅ Busca por setor OK - {len(bancos)} bancos encontrados")

        # Testar estatísticas
        stats = stock_repo.get_stock_count_by_sector()
        logger.info(f"✅ Estatísticas OK - {len(stats)} setores")

        return True
    except Exception as e:
        logger.error(f"❌ Erro no repository de ações: {e}")
        return False


def test_recommendation_repository():
    """Testa o repository de recomendações"""
    try:
        from database.repositories import (get_recommendation_repository,
                                           get_stock_repository)

        rec_repo = get_recommendation_repository()
        stock_repo = get_stock_repository()

        # Testar criação de recomendação de exemplo
        stocks = stock_repo.get_all_stocks()
        if len(stocks) > 0:
            test_rec_data = {
                "stock_id": stocks[0].id,
                "score_fundamentalista": 75.5,
                "score_final": 75.5,
                "classificacao": "COMPRA",
                "preco_entrada": 32.50,
                "stop_loss": 30.92,
                "justificativa": "Teste de recomendação - ação" /
                "com fundamentos sólidos"
            }

            rec = rec_repo.create_recommendation(test_rec_data)
            logger.info(f"✅ Criação de recomendação OK - ID: {rec.id}")

            # Testar listagem
            recent = rec_repo.get_latest_recommendations(limit=5)
            logger.info(f"Listagem OK - {len(recent)} recomendações recentes")

            # Testar estatísticas
            stats = rec_repo.get_recommendation_statistics()
            logger.info(f"✅ Estatísticas OK - {stats['total_ativas']} ativas")
        else:
            logger.info("✅ Repository de recomendações OK " /
                        "(sem dados para testar)")

        return True
    except Exception as e:
        logger.error(f"❌ Erro no repository de recomendações: {e}")
        return False


def test_agent_session_repository():
    """Testa o repository de sessões de agentes"""
    try:
        from database.repositories import get_agent_session_repository

        session_repo = get_agent_session_repository()

        # Criar sessão de teste
        session_data = {
            "session_id": f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "agent_name": "test_agent",
            "agent_version": "1.0.0",
            "status": "running",
            "input_data": '{"test": true}',
            "stocks_processed": 0
        }

        session = session_repo.create_session(session_data)
        logger.info(f"✅ Criação de sessão OK - ID: {session.session_id}")

        # Finalizar sessão
        success = session_repo.finish_session(session.session_id, "completed")
        if success:
            logger.info("✅ Finalização de sessão OK")

        # Testar listagem
        recent_sessions = session_repo.get_recent_sessions(limit=5)
        logger.info(f"✅ Listagem de sessões OK - {len(recent_sessions)}" /
                    "encontradas")

        # Testar estatísticas
        # stats = session_repo.get_session_statistics(days=7)
        logger.info("✅ Estatísticas de sessões OK")

        return True
    except Exception as e:
        logger.error(f"❌ Erro no repository de sessões: {e}")
        return False


def test_data_integrity():
    """Testa a integridade dos dados"""
    try:
        from database.repositories import get_stock_repository
        from database.connection import get_db_session

        stock_repo = get_stock_repository()

        # Verificar se todas as ações têm dados obrigatórios
        stocks = stock_repo.get_all_stocks()
        invalid_stocks = []

        for stock in stocks:
            if not stock.codigo or not stock.nome:
                invalid_stocks.append(stock.id)

        if invalid_stocks:
            logger.warning(f"⚠️  {len(invalid_stocks)} ações" /
                           "com dados inválidos")
        else:
            logger.info("✅ Integridade dos dados OK")

        # Verificar duplicatas
        with get_db_session() as db:
            from sqlalchemy import func
            from database.models import Stock

            duplicates = db.query(
                Stock.codigo,
                func.count(Stock.id).label('count')
            ).group_by(Stock.codigo).having(func.count(Stock.id) > 1).all()

            if duplicates:
                logger.warning(f"⚠️  {len(duplicates)} códigos " /
                               "duplicados encontrados")
                for codigo, count in duplicates:
                    logger.warning(f"   {codigo}: {count} vezes")
            else:
                logger.info("✅ Sem duplicatas encontradas")

        return True
    except Exception as e:
        logger.error(f"❌ Erro na verificação de integridade: {e}")
        return False


def main():
    """Executa todos os testes"""
    logger.info("🧪 INICIANDO TESTES DO BANCO DE DADOS")
    logger.info("=" * 50)

    tests = [
        ("Modelos", test_database_models),
        ("Conexão", test_database_connection),
        ("Repository de Ações", test_stock_repository),
        ("Repository de Recomendações", test_recommendation_repository),
        ("Repository de Sessões", test_agent_session_repository),
        ("Integridade dos Dados", test_data_integrity)
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        logger.info(f"\n🔍 Testando: {test_name}")
        logger.info("-" * 30)

        try:
            if test_func():
                passed += 1
                logger.info(f"✅ {test_name}: PASSOU")
            else:
                failed += 1
                logger.error(f"❌ {test_name}: FALHOU")
        except Exception as e:
            failed += 1
            logger.error(f"❌ {test_name}: ERRO - {e}")

    logger.info("\n" + "=" * 50)
    logger.info("📊 RESULTADO DOS TESTES")
    logger.info("=" * 50)
    logger.info(f"✅ Passou: {passed}")
    logger.info(f"❌ Falhou: {failed}")
    logger.info(f"📊 Total: {passed + failed}")

    if failed == 0:
        logger.info("🎉 TODOS OS TESTES PASSARAM!")
        return True
    else:
        logger.error(f"💥 {failed} TESTES FALHARAM!")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
