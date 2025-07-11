# database/init_db.py
"""
Script para inicialização do banco de dados
"""
import logging
from datetime import datetime
from typing import List, Dict, Any

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


def create_sample_stocks() -> List[Dict[str, Any]]:
    """Cria dados de exemplo de ações brasileiras"""
    return [
        {
            "codigo": "PETR4",
            "nome": "Petróleo Brasileiro S.A. - Petrobras",
            "nome_completo": "Petróleo Brasileiro S.A. - Petrobras",
            "setor": "Petróleo e Gás",
            "subsetor": "Exploração e Refino",
            "segmento": "Petróleo",
            "cnpj": "33.000.167/0001-01",
            "website": "https://petrobras.com.br",
            "descricao": "Sociedade de economia mista que atua de forma " +
            "integrada e especializada nos segmentos de exploração e " +
            "produção, refino, comercialização, transporte, petroquímica" +
            " e distribuição de derivados de petróleo, gás natural " +
            "e energia elétrica.",
            "listagem": "Nível 2",
            "preco_atual": 32.50,
            "volume_medio": 89000000.0,
            "market_cap": 422000000000.0,
            "p_l": 4.2,
            "p_vp": 0.8,
            "roe": 19.5,
            "roic": 12.8
        },
        {
            "codigo": "VALE3",
            "nome": "Vale S.A.",
            "nome_completo": "Vale S.A.",
            "setor": "Mineração",
            "subsetor": "Minerais Metálicos",
            "segmento": "Mineração",
            "cnpj": "33.592.510/0001-54",
            "website": "https://vale.com",
            "descricao": "Mineradora global que transforma recursos " +
            "naturais em prosperidade e desenvolvimento sustentável.",
            "listagem": "Nível 1",
            "preco_atual": 61.80,
            "volume_medio": 67000000.0,
            "market_cap": 280000000000.0,
            "p_l": 5.1,
            "p_vp": 1.2,
            "roe": 24.3,
            "roic": 18.5
        },
        {
            "codigo": "ITUB4",
            "nome": "Itaú Unibanco Holding S.A.",
            "nome_completo": "Itaú Unibanco Holding S.A.",
            "setor": "Bancos",
            "subsetor": "Bancos",
            "segmento": "Bancos",
            "cnpj": "60.872.504/0001-23",
            "website": "https://itau.com.br",
            "descricao": "Holding bancária que controla o Itaú Unibanco, " +
            "um dos maiores bancos privados do Brasil.",
            "listagem": "Nível 1",
            "preco_atual": 33.15,
            "volume_medio": 45000000.0,
            "market_cap": 325000000000.0,
            "p_l": 8.9,
            "p_vp": 1.8,
            "roe": 20.1,
            "roic": 15.2
        },
        {
            "codigo": "BBDC4",
            "nome": "Banco Bradesco S.A.",
            "nome_completo": "Banco Bradesco S.A.",
            "setor": "Bancos",
            "subsetor": "Bancos",
            "segmento": "Bancos",
            "cnpj": "60.746.948/0001-12",
            "website": "https://bradesco.com.br",
            "descricao": "Um dos maiores bancos privados do Brasil, " +
            "oferecendo serviços bancários e financeiros.",
            "listagem": "Nível 1",
            "preco_atual": 13.85,
            "volume_medio": 38000000.0,
            "market_cap": 127000000000.0,
            "p_l": 6.8,
            "p_vp": 1.1,
            "roe": 16.8,
            "roic": 14.5
        },
        {
            "codigo": "ABEV3",
            "nome": "Ambev S.A.",
            "nome_completo": "Ambev S.A.",
            "setor": "Bebidas",
            "subsetor": "Cervejas e Refrigerantes",
            "segmento": "Bebidas",
            "cnpj": "07.526.557/0001-00",
            "website": "https://ambev.com.br",
            "descricao": "Companhia brasileira de bebidas, produzindo " +
            "e distribuindo cervejas, refrigerantes e outras bebidas.",
            "listagem": "Nível 1",
            "preco_atual": 11.25,
            "volume_medio": 28000000.0,
            "market_cap": 177000000000.0,
            "p_l": 15.2,
            "p_vp": 1.9,
            "roe": 12.5,
            "roic": 8.9
        },
        {
            "codigo": "MGLU3",
            "nome": "Magazine Luiza S.A.",
            "nome_completo": "Magazine Luiza S.A.",
            "setor": "Varejo",
            "subsetor": "Eletrodomésticos",
            "segmento": "Varejo",
            "cnpj": "47.960.950/0001-21",
            "website": "https://magazineluiza.com.br",
            "descricao": "Rede varejista brasileira de lojas de " +
            "departamento e e-commerce.",
            "listagem": "Novo Mercado",
            "preco_atual": 4.85,
            "volume_medio": 31000000.0,
            "market_cap": 33000000000.0,
            "p_l": -8.5,  # Prejuízo
            "p_vp": 1.2,
            "roe": -15.2,
            "roic": -5.8
        },
        {
            "codigo": "WEGE3",
            "nome": "WEG S.A.",
            "nome_completo": "WEG S.A.",
            "setor": "Máquinas Industriais",
            "subsetor": "Motores, Compressores e Outros",
            "segmento": "Máquinas e Equipamentos",
            "cnpj": "84.429.695/0001-11",
            "website": "https://weg.net",
            "descricao": "Fabricante de equipamentos elétricos " +
            "industriais, motores elétricos e automação.",
            "listagem": "Novo Mercado",
            "preco_atual": 42.90,
            "volume_medio": 15000000.0,
            "market_cap": 115000000000.0,
            "p_l": 22.8,
            "p_vp": 4.2,
            "roe": 18.5,
            "roic": 16.2
        },
        {
            "codigo": "B3SA3",
            "nome": "B3 S.A. - Brasil, Bolsa, Balcão",
            "nome_completo": "B3 S.A. - Brasil, Bolsa, Balcão",
            "setor": "Serviços Financeiros Diversos",
            "subsetor": "Serviços Financeiros Diversos",
            "segmento": "Serviços Financeiros Diversos",
            "cnpj": "09.346.601/0001-25",
            "website": "https://b3.com.br",
            "descricao": "Bolsa de valores brasileira, oferecendo " +
            "serviços de listagem, negociação, liquidação e depositária.",
            "listagem": "Novo Mercado",
            "preco_atual": 9.85,
            "volume_medio": 22000000.0,
            "market_cap": 52000000000.0,
            "p_l": 12.5,
            "p_vp": 2.1,
            "roe": 16.8,
            "roic": 14.5
        }
    ]


def populate_sample_data():
    """Popula o banco com dados de exemplo"""
    logger.info("Populando banco com dados de exemplo...")

    stock_repo = get_stock_repository()

    # Criar ações de exemplo
    sample_stocks = create_sample_stocks()
    created_count = 0

    for stock_data in sample_stocks:
        # Verificar se já existe
        existing = stock_repo.get_stock_by_code(stock_data["codigo"])
        if not existing:
            try:
                stock_repo.create_stock(stock_data)
                created_count += 1
                logger.info(f"Ação criada: {stock_data['codigo']}")
            except Exception as e:
                logger.error(f"Erro ao criar ação {stock_data['codigo']}: {e}")
        else:
            logger.info(f"Ação já existe: {stock_data['codigo']}")

    logger.info(f"Dados de exemplo populados: {created_count} "
                f"novas ações criadas")
    return created_count


def create_initial_agent_session():
    """Cria sessão inicial do agente"""
    agent_repo = get_agent_session_repository()

    session_data = {
        "session_id": f"init_session_"
        f"{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "agent_name": "database_initializer",
        "agent_version": "1.0.0",
        "status": "completed",
        "input_data": '{"action": "database_initialization"}',
        "output_data": '{"stocks_created": 8, "status": "success"}',
        "execution_time_seconds": 1.5,
        "stocks_processed": 8,
        "config_snapshot": '{"environment": "development"}'
    }

    try:
        session = agent_repo.create_session(session_data)
        agent_repo.finish_session(session.session_id, "completed")
        logger.info(f"Sessão inicial criada: {session.session_id}")
        return session
    except Exception as e:
        logger.error(f"Erro ao criar sessão inicial: {e}")
        return None


def validate_database():
    """Valida se o banco foi inicializado corretamente"""
    logger.info("Validando banco de dados...")

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

    # Verificar se dados de exemplo existem
    stock_repo = get_stock_repository()
    stocks = stock_repo.get_all_stocks()

    if len(stocks) == 0:
        logger.warning("⚠️  Nenhuma ação encontrada no banco")
    else:
        logger.info(f"✅ {len(stocks)} ações encontradas no banco")

    logger.info("✅ Banco de dados validado com sucesso")
    return True


def main():
    """Função principal de inicialização"""
    logger.info("=" * 60)
    logger.info("🚀 INICIALIZANDO BANCO DE DADOS")
    logger.info("=" * 60)

    try:
        # 1. Backup do banco atual (se existir)
        if settings.database_path and settings.database_path.exists():
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

        # 4. Popular com dados de exemplo
        logger.info("📋 Populando dados de exemplo...")
        stocks = populate_sample_data()

        # 5. Criar sessão inicial
        logger.info("📋 Criando sessão inicial...")
        create_initial_agent_session()

        # 6. Validar tudo
        logger.info("📋 Validando banco...")
        if not validate_database():
            logger.error("❌ Falha na validação do banco")
            return False

        # 7. Resumo final
        db_info = get_database_info()
        logger.info("=" * 60)
        logger.info("🎉 BANCO INICIALIZADO COM SUCESSO!")
        logger.info("=" * 60)
        logger.info(f"📊 Tipo: {db_info.get('type', 'Unknown')}")
        logger.info(f"📁 Arquivo: {db_info.get('file_path', 'N/A')}")
        logger.info(f"💾 Tamanho: {db_info.get('file_size_mb', 0)} MB")
        logger.info(f"📋 Tabelas: {len(db_info.get('tables', []))}")
        logger.info(f"🏢 Ações: {len(stocks)}")
        logger.info("=" * 60)

        return True

    except Exception as e:
        logger.error(f"❌ Erro na inicialização: {e}")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
