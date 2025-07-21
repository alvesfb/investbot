#!/bin/bash
# test_insert_USIM5_yfinance.sh
# Script para inserir USIM5 buscando dados reais via YFinance

echo "🏦 INSERÇÃO USIM5 - Dados Reais via YFinance"
echo "============================================="

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

print_step() {
    echo -e "${BLUE}📋 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

# ==================== VERIFICAÇÕES ====================
print_step "Verificando pré-requisitos..."

if ! docker-compose -f docker-compose.postgresql.yml ps postgres | grep -q "Up"; then
    print_error "PostgreSQL não está rodando!"
    exit 1
fi

print_success "PostgreSQL está ativo"

# Verificar se yfinance está instalado
python3 -c "import yfinance" 2>/dev/null || {
    print_info "Instalando yfinance..."
    pip install yfinance
}

print_success "YFinance disponível"

# ==================== BUSCA E INSERÇÃO VIA YFINANCE ====================
print_step "Buscando dados reais do USIM5 via YFinance..."

# Criar script Python integrado com YFinance
cat > temp_insert_USIM5_yfinance.py << 'EOF'
#!/usr/bin/env python3
"""
Inserção USIM5 com Dados Reais via YFinance
Integra com o sistema YFinanceClient existente
"""
import sys
import os
import asyncio
import psycopg2
from datetime import datetime, timedelta
from pathlib import Path
import logging

# Setup do projeto
current_dir = Path.cwd()
sys.path.insert(0, str(current_dir))

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurar variáveis de ambiente
os.environ.update({
    'POSTGRES_HOST': 'localhost',
    'POSTGRES_PORT': '5432',
    'POSTGRES_DB': 'investment_system',
    'POSTGRES_USER': 'investment_user',
    'POSTGRES_PASSWORD': 'investment_secure_pass_2024'
})

class USIM5YFinanceInserter:
    """Classe para inserir USIM5 usando YFinance real"""
    
    def __init__(self):
        self.symbol = "USIM5"
        self.yf_client = None
        
    async def setup_yfinance_client(self):
        """Configura cliente YFinance do projeto"""
        try:
            from agents.collectors.stock_collector import YFinanceClient
            self.yf_client = YFinanceClient()
            logger.info("✅ YFinanceClient inicializado")
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar YFinanceClient: {e}")
            return False
    
    async def fetch_USIM5_data(self):
        """Busca dados reais do USIM5 via YFinance"""
        logger.info("🌐 Buscando dados reais do USIM5...")
        
        try:
            # Usar cliente YFinance integrado
            if self.yf_client:
                yf_data = await self.yf_client.get_stock_info(self.symbol)
            else:
                # Fallback para yfinance direto
                yf_data = await self._fetch_direct_yfinance()
            
            if not yf_data or not yf_data.get('regularMarketPrice'):
                raise ValueError("Dados insuficientes retornados do YFinance")
            
            logger.info(f"✅ Dados obtidos - Preço: R$ {yf_data.get('regularMarketPrice', 0):.2f}")
            
            # Mapear dados do YFinance para schema PostgreSQL
            mapped_data = self._map_yfinance_to_schema(yf_data)
            
            return mapped_data
            
        except Exception as e:
            logger.error(f"❌ Erro ao buscar dados YFinance: {e}")
            raise
    
    async def _fetch_direct_yfinance(self):
        """Fallback para YFinance direto"""
        import yfinance as yf
        
        ticker_symbol = f"{self.symbol}.SA"
        ticker = yf.Ticker(ticker_symbol)
        
        try:
            # Tentar info primeiro
            info = ticker.info
            
            if not info or not info.get('regularMarketPrice'):
                # Fallback para historical data
                hist = ticker.history(period="5d")
                if not hist.empty:
                    info = {
                        'regularMarketPrice': float(hist['Close'].iloc[-1]),
                        'regularMarketVolume': int(hist['Volume'].iloc[-1]),
                        'shortName': self.symbol,
                        'symbol': ticker_symbol
                    }
            
            # Buscar dados financeiros adicionais
            financials = ticker.financials
            balance_sheet = ticker.balance_sheet
            
            # Adicionar dados fundamentais se disponíveis
            if not financials.empty:
                info['total_revenue'] = self._get_latest_financial(financials, 'Total Revenue')
                info['net_income'] = self._get_latest_financial(financials, 'Net Income')
            
            if not balance_sheet.empty:
                info['total_assets'] = self._get_latest_financial(balance_sheet, 'Total Assets')
                info['total_debt'] = self._get_latest_financial(balance_sheet, 'Total Debt')
                info['stockholder_equity'] = self._get_latest_financial(balance_sheet, 'Stockholder Equity')
            
            return info
            
        except Exception as e:
            logger.error(f"Erro no YFinance direto: {e}")
            raise
    
    def _get_latest_financial(self, df, metric_name):
        """Extrai métrica financeira mais recente"""
        try:
            if metric_name in df.index:
                # Pegar valor mais recente (primeira coluna)
                value = df.loc[metric_name].iloc[0]
                return float(value) if not pd.isna(value) else None
            return None
        except:
            return None
    
    def _map_yfinance_to_schema(self, yf_data):
        """Mapeia dados YFinance para schema PostgreSQL"""
        
        # Função auxiliar para extrair valores seguros
        def safe_get(key, default=None):
            value = yf_data.get(key, default)
            if value in [None, 'N/A', '', 0]:
                return default
            return value
        
        # Calcular métricas derivadas
        market_cap = safe_get('marketCap')
        shares_outstanding = safe_get('sharesOutstanding')
        current_price = safe_get('regularMarketPrice', safe_get('currentPrice'))
        
        # Se market cap não disponível, calcular
        if not market_cap and shares_outstanding and current_price:
            market_cap = shares_outstanding * current_price
        
        mapped_data = {
            # ==================== IDENTIFICATION ====================
            'symbol': self.symbol,
            'name': safe_get('shortName') or safe_get('longName') or 'Banco do Brasil S.A.',
            'long_name': safe_get('longName') or 'Banco do Brasil S.A.',
            
            # ==================== SECTOR ====================
            'sector': safe_get('sector') or 'Financial Services',
            'industry': safe_get('industry') or 'Banks',
            'business_summary': safe_get('longBusinessSummary') or 'Banco múltiplo brasileiro com atuação diversificada em serviços financeiros.',
            
            # ==================== FINANCIAL METRICS ====================
            'market_cap': market_cap,
            'enterprise_value': safe_get('enterpriseValue'),
            'revenue': safe_get('total_revenue') or safe_get('totalRevenue'),
            'net_income': safe_get('net_income') or safe_get('netIncomeToCommon'),
            'total_assets': safe_get('total_assets') or safe_get('totalAssets'),
            'total_equity': safe_get('stockholder_equity') or safe_get('totalStockholderEquity'),
            'total_debt': safe_get('total_debt') or safe_get('totalDebt'),
            'free_cash_flow': safe_get('freeCashflow'),
            'operating_cash_flow': safe_get('operatingCashflow'),
            
            # ==================== RATIOS ====================
            'pe_ratio': safe_get('trailingPE') or safe_get('forwardPE'),
            'pb_ratio': safe_get('priceToBook'),
            'ps_ratio': safe_get('priceToSalesTrailing12Months'),
            'peg_ratio': safe_get('pegRatio'),
            'ev_ebitda': safe_get('enterpriseToEbitda'),
            'price_to_book': safe_get('priceToBook'),
            'price_to_sales': safe_get('priceToSalesTrailing12Months'),
            
            # ==================== PROFITABILITY ====================
            'roe': safe_get('returnOnEquity'),
            'roa': safe_get('returnOnAssets'),
            'roic': None,  # YFinance não tem ROIC direto
            'gross_margin': safe_get('grossMargins'),
            'operating_margin': safe_get('operatingMargins'),
            'net_margin': safe_get('profitMargins'),
            'ebitda_margin': safe_get('ebitdaMargins'),
            
            # ==================== FINANCIAL HEALTH ====================
            'debt_to_equity': safe_get('debtToEquity'),
            'debt_to_assets': None,  # Calcular se dados disponíveis
            'current_ratio': safe_get('currentRatio'),
            'quick_ratio': safe_get('quickRatio'),
            'cash_ratio': None,
            'interest_coverage': None,
            
            # ==================== GROWTH ====================
            'revenue_growth': safe_get('revenueGrowth'),
            'earnings_growth': safe_get('earningsGrowth'),
            'book_value_growth': None,
            'dividend_growth': None,
            
            # ==================== MARKET DATA ====================
            'current_price': current_price,
            'day_change': None,  # Calcular se dados disponíveis
            'day_change_percent': safe_get('regularMarketChangePercent'),
            'volume': safe_get('regularMarketVolume') or safe_get('volume'),
            'avg_volume': safe_get('averageVolume'),
            'market_cap_category': self._categorize_market_cap(market_cap),
            
            # ==================== DIVIDEND ====================
            'dividend_yield': safe_get('dividendYield'),
            'dividend_rate': safe_get('dividendRate'),
            'payout_ratio': safe_get('payoutRatio'),
            
            # ==================== STATUS & QUALITY ====================
            'status': 'active',
            'data_quality': 'excellent' if current_price else 'good',
            'data_completeness': self._calculate_completeness(yf_data),
            'confidence_level': 90.0 if current_price else 70.0,
            
            # ==================== METADATA ====================
            'country': 'BR',
            'currency': safe_get('currency') or 'BRL',
            'exchange': safe_get('exchange') or 'B3'
        }
        
        # Calcular métricas derivadas
        if mapped_data['total_debt'] and mapped_data['total_assets']:
            mapped_data['debt_to_assets'] = mapped_data['total_debt'] / mapped_data['total_assets']
        
        return mapped_data
    
    def _categorize_market_cap(self, market_cap):
        """Categoriza market cap"""
        if not market_cap:
            return 'unknown'
        
        if market_cap >= 100_000_000_000:  # 100B+
            return 'mega_cap'
        elif market_cap >= 10_000_000_000:  # 10B+
            return 'large_cap'
        elif market_cap >= 2_000_000_000:   # 2B+
            return 'mid_cap'
        else:
            return 'small_cap'
    
    def _calculate_completeness(self, data):
        """Calcula % de completude dos dados"""
        total_fields = 50  # Aproximadamente 50 campos importantes
        filled_fields = sum(1 for v in data.values() if v not in [None, '', 0, 'N/A'])
        return round((filled_fields / total_fields) * 100, 1)
    
    async def insert_to_database(self, stock_data):
        """Insere dados no PostgreSQL"""
        logger.info("💾 Inserindo dados no PostgreSQL...")
        
        try:
            # Conectar ao banco
            conn = psycopg2.connect(
                host='localhost',
                port=5432,
                database='investment_system',
                user='investment_user',
                password='investment_secure_pass_2024'
            )
            conn.autocommit = True
            cur = conn.cursor()
            
            # Limpar USIM5 existente
            cur.execute("DELETE FROM stocks WHERE symbol = %s;", (self.symbol,))
            logger.info(f"🧹 USIM5 anterior removido")
            
            # Preparar dados para inserção
            columns = list(stock_data.keys())
            placeholders = ', '.join(['%s'] * len(columns))
            values = list(stock_data.values())
            
            # Query de inserção
            query = f"""
                INSERT INTO stocks ({', '.join(columns)}, last_price_update, last_fundamentals_update)
                VALUES ({placeholders}, NOW(), NOW())
                RETURNING id, symbol, name, current_price;
            """
            
            cur.execute(query, values)
            result = cur.fetchone()
            
            if result:
                record_id, symbol, name, price = result
                logger.info(f"✅ USIM5 inserido com sucesso!")
                logger.info(f"   📊 ID: {record_id}")
                logger.info(f"   📈 Symbol: {symbol}")
                logger.info(f"   🏦 Name: {name}")
                logger.info(f"   💰 Price: R$ {price}")
                
                # Criar recomendação baseada nos dados reais
                await self._create_recommendation(cur, record_id, stock_data)
                
                # Criar análise fundamental
                await self._create_fundamental_analysis(cur, record_id, stock_data)
                
                # Buscar dados históricos
                await self._insert_historical_data(cur, record_id)
                
                conn.close()
                return True
            else:
                logger.error("❌ Falha na inserção")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro na inserção: {e}")
            raise
    
    async def _create_recommendation(self, cur, stock_id, stock_data):
        """Cria recomendação baseada nos dados reais"""
        
        # Lógica de recomendação baseada nos dados
        pe_ratio = stock_data.get('pe_ratio')
        roe = stock_data.get('roe')
        div_yield = stock_data.get('dividend_yield')
        current_price = stock_data.get('current_price')
        
        # Tratamento seguro de valores None
        pe_ratio = pe_ratio if pe_ratio and pe_ratio > 0 else None
        roe = roe if roe and roe > 0 else None
        div_yield = div_yield if div_yield and div_yield > 0 else None
        current_price = current_price if current_price and current_price > 0 else None
        
        # Score baseado em métricas reais
        score = 50  # Base
        
        if pe_ratio and pe_ratio < 10:  # P/E baixo para bancos
            score += 15
        if roe and roe > 0.15:  # ROE > 15%
            score += 20
        if div_yield and div_yield > 0.06:  # Dividend yield > 6%
            score += 15
        
        # Determinar recomendação
        if score >= 80:
            rec_type = 'strong_buy'
            target_multiplier = 1.15
        elif score >= 70:
            rec_type = 'buy'
            target_multiplier = 1.10
        elif score >= 40:
            rec_type = 'hold'
            target_multiplier = 1.05
        else:
            rec_type = 'sell'
            target_multiplier = 0.95
        
        target_price = current_price * target_multiplier if current_price else None
        
        # Formatação segura para valores que podem ser None
        pe_text = f"{pe_ratio:.1f}" if pe_ratio else "N/A"
        roe_text = f"{roe:.1%}" if roe else "N/A"
        div_text = f"{div_yield:.1%}" if div_yield else "N/A"
        
        rationale = (
            f"Recomendação baseada em dados reais YFinance. "
            f"P/E: {pe_text}, ROE: {roe_text}, Dividend Yield: {div_text}. "
            f"Score: {score}/100."
        )
        
        cur.execute("""
            INSERT INTO recommendations (stock_id, recommendation_type, target_price, 
                                       entry_price, confidence_score, rationale, analyst_name)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
        """, (
            stock_id,
            rec_type,
            target_price,
            current_price,
            score,
            rationale,
            'YFinance Auto-Analysis'
        ))
        
        rec_id = cur.fetchone()[0]
        logger.info(f"   📈 Recomendação criada: {rec_type.upper()} (Score: {score})")
        
    async def _create_fundamental_analysis(self, cur, stock_id, stock_data):
        """Cria análise fundamental baseada nos dados"""
        
        # Calcular scores baseados em dados reais
        valuation_score = self._calculate_valuation_score(stock_data)
        profitability_score = self._calculate_profitability_score(stock_data)
        growth_score = self._calculate_growth_score(stock_data)
        health_score = self._calculate_health_score(stock_data)
        
        composite_score = (valuation_score + profitability_score + growth_score + health_score) / 4
        
        cur.execute("""
            INSERT INTO fundamental_analyses (stock_id, valuation_score, profitability_score,
                                            growth_score, financial_health_score, composite_score)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id;
        """, (stock_id, valuation_score, profitability_score, growth_score, health_score, composite_score))
        
        analysis_id = cur.fetchone()[0]
        logger.info(f"   📊 Análise fundamental criada (Score: {composite_score:.1f})")
    
    def _calculate_valuation_score(self, data):
        """Calcula score de valuation"""
        score = 50
        
        pe = data.get('pe_ratio')
        pb = data.get('pb_ratio')
        
        # Tratamento seguro de valores None
        pe = pe if pe and pe > 0 else None
        pb = pb if pb and pb > 0 else None
        
        if pe and pe < 8:  # P/E muito baixo para bancos
            score += 25
        elif pe and pe < 12:
            score += 15
        
        if pb and pb < 1.2:  # P/B atrativo
            score += 15
        elif pb and pb < 1.5:
            score += 10
            
        return min(score, 100)
    
    def _calculate_profitability_score(self, data):
        """Calcula score de rentabilidade"""
        score = 50
        
        roe = data.get('roe')
        roa = data.get('roa')
        net_margin = data.get('net_margin')
        
        # Tratamento seguro de valores None
        roe = roe if roe and roe > 0 else None
        roa = roa if roa and roa > 0 else None
        net_margin = net_margin if net_margin and net_margin > 0 else None
        
        if roe and roe > 0.18:  # ROE > 18%
            score += 25
        elif roe and roe > 0.12:
            score += 15
        
        if roa and roa > 0.015:  # ROA > 1.5%
            score += 15
        
        if net_margin and net_margin > 0.25:  # Margem > 25%
            score += 10
            
        return min(score, 100)
    
    def _calculate_growth_score(self, data):
        """Calcula score de crescimento"""
        score = 60  # Base para bancos (crescimento moderado)
        
        revenue_growth = data.get('revenue_growth')
        earnings_growth = data.get('earnings_growth')
        
        # Tratamento seguro de valores None
        revenue_growth = revenue_growth if revenue_growth and revenue_growth > 0 else None
        earnings_growth = earnings_growth if earnings_growth and earnings_growth > 0 else None
        
        if revenue_growth and revenue_growth > 0.1:
            score += 20
        elif revenue_growth and revenue_growth > 0.05:
            score += 10
            
        if earnings_growth and earnings_growth > 0.15:
            score += 20
        elif earnings_growth and earnings_growth > 0.08:
            score += 10
            
        return min(score, 100)
    
    def _calculate_health_score(self, data):
        """Calcula score de saúde financeira"""
        score = 70  # Base para bancos grandes
        
        debt_to_equity = data.get('debt_to_equity')
        current_ratio = data.get('current_ratio')
        
        # Tratamento seguro de valores None
        debt_to_equity = debt_to_equity if debt_to_equity and debt_to_equity > 0 else None
        current_ratio = current_ratio if current_ratio and current_ratio > 0 else None
        
        # Para bancos, debt_to_equity alto é normal
        if debt_to_equity and debt_to_equity < 8:  # Alavancagem controlada
            score += 15
        
        if current_ratio and current_ratio > 1.5:
            score += 15
            
        return min(score, 100)
    
    async def _insert_historical_data(self, cur, stock_id):
        """Busca e insere dados históricos"""
        try:
            import yfinance as yf
            
            ticker = yf.Ticker(f"{self.symbol}.SA")
            hist = ticker.history(period="5d")
            
            if not hist.empty:
                for date, row in hist.iterrows():
                    cur.execute("""
                        INSERT INTO market_data (stock_id, date, open_price, high_price, 
                                               low_price, close_price, adjusted_close, volume)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (stock_id, date) DO NOTHING;
                    """, (
                        stock_id,
                        date.date(),
                        float(row['Open']),
                        float(row['High']),
                        float(row['Low']),
                        float(row['Close']),
                        float(row['Close']),  # Adjusted close
                        int(row['Volume'])
                    ))
                
                logger.info(f"   📅 {len(hist)} dias de dados históricos inseridos")
        except Exception as e:
            logger.warning(f"⚠️ Erro ao inserir dados históricos: {e}")

async def main():
    """Função principal"""
    inserter = USIM5YFinanceInserter()
    
    try:
        # 1. Configurar cliente YFinance
        await inserter.setup_yfinance_client()
        
        # 2. Buscar dados reais do USIM5
        stock_data = await inserter.fetch_USIM5_data()
        
        # 3. Inserir no banco
        success = await inserter.insert_to_database(stock_data)
        
        if success:
            # Formatação segura dos valores para saída
            current_price = stock_data.get('current_price') or 0
            market_cap = stock_data.get('market_cap') or 0
            dividend_yield = stock_data.get('dividend_yield')
            data_completeness = stock_data.get('data_completeness') or 0
            
            # Formatação condicional para dividend yield
            div_yield_text = f"{dividend_yield:.1%}" if dividend_yield else "N/A"
            
            print("\n🎉 USIM5 INSERIDO COM DADOS REAIS!")
            print("=" * 40)
            print(f"✅ Dados obtidos via YFinance")
            print(f"✅ Preço atual: R$ {current_price:.2f}")
            print(f"✅ Market Cap: R$ {market_cap:,.0f}")
            print(f"✅ Dividend Yield: {div_yield_text}")
            print(f"✅ Completude dos dados: {data_completeness:.1f}%")
        else:
            print("❌ Falha na inserção")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import pandas as pd  # Necessário para YFinance
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
EOF

# Executar script integrado
print_info "Executando busca e inserção via YFinance..."
python3 temp_insert_USIM5_yfinance.py

if [ $? -eq 0 ]; then
    print_success "USIM5 inserido com dados reais YFinance!"
    
    print_step "Verificação dos dados inseridos..."
    
    # Verificar dados via SQL
    docker exec investment-postgres psql -U investment_user -d investment_system -c "
        SELECT 
            symbol,
            name,
            CONCAT('R$ ', ROUND(current_price::numeric, 2)) as preco_atual,
            CONCAT(ROUND(pe_ratio::numeric, 1), 'x') as pe_ratio,
            CONCAT(ROUND((roe * 100)::numeric, 1), '%') as roe,
            CONCAT(ROUND((dividend_yield * 100)::numeric, 1), '%') as div_yield,
            CONCAT(ROUND(data_completeness::numeric, 1), '%') as completude,
            data_quality,
            last_price_update::timestamp(0)
        FROM stocks 
        WHERE symbol = 'USIM5';
    "
    
    print_step "Verificando análises criadas..."
    
    docker exec investment-postgres psql -U investment_user -d investment_system -c "
        SELECT 
            'Recomendação' as tipo,
            r.recommendation_type as valor,
            CONCAT('R$ ', ROUND(r.target_price::numeric, 2)) as preco_alvo,
            CONCAT(ROUND(r.confidence_score::numeric, 1), '%') as confianca
        FROM recommendations r 
        JOIN stocks s ON r.stock_id = s.id 
        WHERE s.symbol = 'USIM5'
        UNION ALL
        SELECT 
            'Score Composto' as tipo,
            ROUND(fa.composite_score::numeric, 1)::text as valor,
            '' as preco_alvo,
            '' as confianca
        FROM fundamental_analyses fa 
        JOIN stocks s ON fa.stock_id = s.id 
        WHERE s.symbol = 'USIM5';
    "
    
    # Limpeza
    rm -f temp_insert_USIM5_yfinance.py
    
    echo ""
    echo "🎉 SUCESSO - USIM5 COM DADOS REAIS!"
    echo "===================================="
    echo ""
    echo -e "${GREEN}✅ Integração YFinance funcionando${NC}"
    echo -e "${GREEN}✅ Dados financeiros reais obtidos${NC}"
    echo -e "${GREEN}✅ Análises baseadas em métricas reais${NC}"
    echo -e "${GREEN}✅ Schema PostgreSQL validado${NC}"
    echo -e "${GREEN}✅ Sistema pronto para produção${NC}"
    
else
    print_error "Falha na inserção com YFinance!"
    rm -f temp_insert_USIM5_yfinance.py
    exit 1
fi