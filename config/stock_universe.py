# config/stock_universe.py
"""
Universo de ações brasileiras para população do banco
Lista expandida com 50+ empresas principais do mercado brasileiro
"""
from typing import List, Dict, Any

# Lista principal do Ibovespa + ações relevantes
EXTENDED_BRAZILIAN_STOCKS = [
    # === PETRÓLEO E GÁS ===
    {
        "symbol": "PETR4", "name": "Petróleo Brasileiro S.A.", "sector": "Oil & Gas",
        "market_cap": 422000000000, "listing": "Level 2"
    },
    {
        "symbol": "PETR3", "name": "Petróleo Brasileiro S.A.", "sector": "Oil & Gas", 
        "market_cap": 422000000000, "listing": "Level 2"
    },
    {
        "symbol": "PRIO3", "name": "PetroRio S.A.", "sector": "Oil & Gas",
        "market_cap": 45000000000, "listing": "Novo Mercado"
    },
    
    # === MINERAÇÃO ===
    {
        "symbol": "VALE3", "name": "Vale S.A.", "sector": "Mining",
        "market_cap": 280000000000, "listing": "Level 1"
    },
    {
        "symbol": "CSNA3", "name": "Companhia Siderúrgica Nacional", "sector": "Steel",
        "market_cap": 35000000000, "listing": "Level 1"
    },
    {
        "symbol": "USIM5", "name": "Usinas Siderúrgicas de Minas Gerais", "sector": "Steel",
        "market_cap": 25000000000, "listing": "Level 1"
    },
    
    # === BANCOS ===
    {
        "symbol": "ITUB4", "name": "Itaú Unibanco Holding S.A.", "sector": "Banks",
        "market_cap": 325000000000, "listing": "Level 1"
    },
    {
        "symbol": "BBDC4", "name": "Banco Bradesco S.A.", "sector": "Banks",
        "market_cap": 127000000000, "listing": "Level 1"
    },
    {
        "symbol": "BBAS3", "name": "Banco do Brasil S.A.", "sector": "Banks",
        "market_cap": 180000000000, "listing": "Novo Mercado"
    },
    {
        "symbol": "SANB11", "name": "Banco Santander Brasil S.A.", "sector": "Banks",
        "market_cap": 95000000000, "listing": "Level 2"
    },
    {
        "symbol": "ITSA4", "name": "Itaúsa S.A.", "sector": "Financial Holdings",
        "market_cap": 85000000000, "listing": "Level 1"
    },
    
    # === VAREJO ===
    {
        "symbol": "MGLU3", "name": "Magazine Luiza S.A.", "sector": "Retail",
        "market_cap": 33000000000, "listing": "Novo Mercado"
    },
    {
        "symbol": "LREN3", "name": "Lojas Renner S.A.", "sector": "Retail",
        "market_cap": 25000000000, "listing": "Novo Mercado"
    },
    {
        "symbol": "PCAR3", "name": "Companhia Brasileira de Distribuição", "sector": "Retail",
        "market_cap": 18000000000, "listing": "Novo Mercado"
    },
    {
        "symbol": "VVAR3", "name": "Via S.A.", "sector": "Retail",
        "market_cap": 8000000000, "listing": "Novo Mercado"
    },
    {
        "symbol": "AMER3", "name": "Americanas S.A.", "sector": "Retail",
        "market_cap": 2000000000, "listing": "Novo Mercado"
    },
    
    # === BEBIDAS E ALIMENTAÇÃO ===
    {
        "symbol": "ABEV3", "name": "Ambev S.A.", "sector": "Beverages",
        "market_cap": 177000000000, "listing": "Level 1"
    },
    {
        "symbol": "JBSS3", "name": "JBS S.A.", "sector": "Food Processing",
        "market_cap": 95000000000, "listing": "Novo Mercado"
    },
    {
        "symbol": "BRFS3", "name": "BRF S.A.", "sector": "Food Processing",
        "market_cap": 28000000000, "listing": "Novo Mercado"
    },
    
    # === MÁQUINAS E EQUIPAMENTOS ===
    {
        "symbol": "WEGE3", "name": "WEG S.A.", "sector": "Industrial Machinery",
        "market_cap": 115000000000, "listing": "Novo Mercado"
    },
    {
        "symbol": "RAIZ4", "name": "Raízen S.A.", "sector": "Energy",
        "market_cap": 45000000000, "listing": "Level 2"
    },
    
    # === TELECOMUNICAÇÕES ===
    {
        "symbol": "VIVT3", "name": "Telefônica Brasil S.A.", "sector": "Telecommunications",
        "market_cap": 85000000000, "listing": "Novo Mercado"
    },
    {
        "symbol": "TIMS3", "name": "TIM S.A.", "sector": "Telecommunications",
        "market_cap": 28000000000, "listing": "Novo Mercado"
    },
    
    # === ENERGIA ELÉTRICA ===
    {
        "symbol": "ELET3", "name": "Centrais Elétricas Brasileiras S.A.", "sector": "Electric Utilities",
        "market_cap": 95000000000, "listing": "Novo Mercado"
    },
    {
        "symbol": "ELET6", "name": "Centrais Elétricas Brasileiras S.A.", "sector": "Electric Utilities",
        "market_cap": 95000000000, "listing": "Novo Mercado"
    },
    {
        "symbol": "CPFE3", "name": "CPFL Energia S.A.", "sector": "Electric Utilities",
        "market_cap": 35000000000, "listing": "Novo Mercado"
    },
    {
        "symbol": "CPLE6", "name": "Companhia Paranaense de Energia", "sector": "Electric Utilities",
        "market_cap": 28000000000, "listing": "Level 1"
    },
    {
        "symbol": "EQTL3", "name": "Equatorial Energia S.A.", "sector": "Electric Utilities",
        "market_cap": 42000000000, "listing": "Level 2"
    },
    
    # === CONSTRUÇÃO E IMOBILIÁRIO ===
    {
        "symbol": "CYRE3", "name": "Cyrela Brazil Realty S.A.", "sector": "Real Estate",
        "market_cap": 8000000000, "listing": "Novo Mercado"
    },
    {
        "symbol": "MRFG3", "name": "Marfrig Global Foods S.A.", "sector": "Food Processing",
        "market_cap": 18000000000, "listing": "Novo Mercado"
    },
    {
        "symbol": "EZTC3", "name": "EZTEC S.A.", "sector": "Real Estate",
        "market_cap": 5000000000, "listing": "Novo Mercado"
    },
    
    # === LOGÍSTICA E TRANSPORTE ===
    {
        "symbol": "RAIL3", "name": "Rumo S.A.", "sector": "Transportation",
        "market_cap": 35000000000, "listing": "Novo Mercado"
    },
    {
        "symbol": "CCRO3", "name": "CCR S.A.", "sector": "Transportation",
        "market_cap": 32000000000, "listing": "Novo Mercado"
    },
    
    # === QUÍMICOS E PETROQUÍMICOS ===
    {
        "symbol": "BRASKEM", "name": "Braskem S.A.", "sector": "Chemicals", 
        "market_cap": 15000000000, "listing": "Level 1"
    },
    {
        "symbol": "UNIP6", "name": "Unipar Carbocloro S.A.", "sector": "Chemicals",
        "market_cap": 12000000000, "listing": "Level 1"
    },
    
    # === TECNOLOGIA E SERVIÇOS ===
    {
        "symbol": "B3SA3", "name": "B3 S.A. - Brasil, Bolsa, Balcão", "sector": "Financial Services",
        "market_cap": 52000000000, "listing": "Novo Mercado"
    },
    {
        "symbol": "TOTS3", "name": "TOTVS S.A.", "sector": "Technology",
        "market_cap": 18000000000, "listing": "Novo Mercado"
    },
    {
        "symbol": "POSI3", "name": "Positivo Tecnologia S.A.", "sector": "Technology",
        "market_cap": 3000000000, "listing": "Level 2"
    },
    
    # === PAPEL E CELULOSE ===
    {
        "symbol": "SUZB3", "name": "Suzano S.A.", "sector": "Paper & Pulp",
        "market_cap": 85000000000, "listing": "Novo Mercado"
    },
    {
        "symbol": "KLBN11", "name": "Klabin S.A.", "sector": "Paper & Pulp",
        "market_cap": 35000000000, "listing": "Level 2"
    },
    
    # === SEGUROS ===
    {
        "symbol": "BBSE3", "name": "BB Seguridade Participações S.A.", "sector": "Insurance",
        "market_cap": 48000000000, "listing": "Novo Mercado"
    },
    {
        "symbol": "PSSA3", "name": "Porto Seguro S.A.", "sector": "Insurance", 
        "market_cap": 22000000000, "listing": "Novo Mercado"
    },
    
    # === SANEAMENTO ===
    {
        "symbol": "SAPR11", "name": "Sanepar S.A.", "sector": "Water Utilities",
        "market_cap": 18000000000, "listing": "Level 2"
    },
    {
        "symbol": "SBSP3", "name": "Companhia de Saneamento Básico do Estado de São Paulo", "sector": "Water Utilities",
        "market_cap": 42000000000, "listing": "Novo Mercado"
    },
    
    # === SAÚDE ===
    {
        "symbol": "RADL3", "name": "Raia Drogasil S.A.", "sector": "Healthcare",
        "market_cap": 32000000000, "listing": "Novo Mercado"
    },
    {
        "symbol": "HAPV3", "name": "Hapvida Participações e Investimentos S.A.", "sector": "Healthcare",
        "market_cap": 28000000000, "listing": "Novo Mercado"
    },
    {
        "symbol": "QUAL3", "name": "Qualicorp S.A.", "sector": "Healthcare",
        "market_cap": 8000000000, "listing": "Novo Mercado"
    },
    
    # === EDUCAÇÃO ===
    {
        "symbol": "COGN3", "name": "Cogna Educação S.A.", "sector": "Education",
        "market_cap": 3500000000, "listing": "Novo Mercado"
    },
    {
        "symbol": "YDUQ3", "name": "YDUQS Participações S.A.", "sector": "Education",
        "market_cap": 4500000000, "listing": "Novo Mercado"
    },
    
    # === AGRONEGÓCIO ===
    {
        "symbol": "SLCE3", "name": "SLC Agrícola S.A.", "sector": "Agriculture",
        "market_cap": 8500000000, "listing": "Novo Mercado"
    },
    {
        "symbol": "ARZZ3", "name": "Arezzo Indústria e Comércio S.A.", "sector": "Consumer Goods",
        "market_cap": 5500000000, "listing": "Novo Mercado"
    }
]

# Mapeamento setorial para validação
SECTOR_MAPPING = {
    "Oil & Gas": "Petróleo e Gás",
    "Mining": "Mineração", 
    "Steel": "Siderurgia",
    "Banks": "Bancos",
    "Financial Holdings": "Holdings Financeiras",
    "Financial Services": "Serviços Financeiros",
    "Retail": "Varejo",
    "Beverages": "Bebidas",
    "Food Processing": "Alimentos",
    "Industrial Machinery": "Máquinas Industriais",
    "Telecommunications": "Telecomunicações",
    "Electric Utilities": "Energia Elétrica",
    "Real Estate": "Imobiliário",
    "Transportation": "Transporte",
    "Chemicals": "Químicos",
    "Technology": "Tecnologia",
    "Paper & Pulp": "Papel e Celulose",
    "Insurance": "Seguros",
    "Water Utilities": "Saneamento",
    "Healthcare": "Saúde",
    "Education": "Educação",
    "Agriculture": "Agronegócio",
    "Consumer Goods": "Bens de Consumo",
    "Energy": "Energia"
}

# APIs disponíveis para fallback (baseado no YFinanceClient)
API_PRIORITY = [
    "yfinance_primary",
    "yfinance_alternative", 
    "alpha_vantage",
    "financial_modeling_prep",
    "static_fallback"
]

def get_extended_stock_list() -> List[Dict[str, Any]]:
    """Retorna lista completa de 50+ ações brasileiras"""
    return EXTENDED_BRAZILIAN_STOCKS

def get_stocks_by_sector(sector: str) -> List[Dict[str, Any]]:
    """Filtra ações por setor"""
    return [stock for stock in EXTENDED_BRAZILIAN_STOCKS if stock["sector"] == sector]

def get_sector_distribution() -> Dict[str, int]:
    """Retorna distribuição de ações por setor"""
    distribution = {}
    for stock in EXTENDED_BRAZILIAN_STOCKS:
        sector = stock["sector"]
        distribution[sector] = distribution.get(sector, 0) + 1
    return distribution

def validate_stock_symbol(symbol: str) -> bool:
    """Valida se símbolo está na lista"""
    symbols = [stock["symbol"] for stock in EXTENDED_BRAZILIAN_STOCKS]
    return symbol.upper() in symbols

def get_stock_info(symbol: str) -> Dict[str, Any]:
    """Retorna informações básicas de uma ação"""
    for stock in EXTENDED_BRAZILIAN_STOCKS:
        if stock["symbol"] == symbol.upper():
            return stock
    return {}

# Total de ações: 52 empresas
print(f"📊 Total de ações: {len(EXTENDED_BRAZILIAN_STOCKS)}")
print(f"📋 Setores cobertos: {len(set(stock['sector'] for stock in EXTENDED_BRAZILIAN_STOCKS))}")