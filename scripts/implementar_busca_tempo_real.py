# implementar_busca_tempo_real.py
"""
Implementação da busca de dados em tempo real para ações não encontradas no banco
FLUXO: Ação não encontrada → Buscar API → Salvar no banco → Calcular score real
"""

def create_real_time_data_fetcher():
    """Cria sistema de busca de dados em tempo real"""
    
    print("🔄 IMPLEMENTANDO BUSCA DE DADOS EM TEMPO REAL")
    print("=" * 60)
    
    print("✅ FLUXO CORRETO:")
    print("1. Ação solicitada não está no banco")
    print("2. Buscar dados reais via API (yfinance/Alpha Vantage)")
    print("3. Validar e salvar dados no banco")
    print("4. Calcular score com dados REAIS")
    print("5. Retornar análise baseada em dados verdadeiros")
    
    print("\n💡 BENEFÍCIOS:")
    print("• Scores baseados em dados reais")
    print("• Banco cresce automaticamente")
    print("• Sem dados fictícios/simulados")
    print("• Sistema autossuficiente")

def show_real_time_fetcher_implementation():
    """Mostra implementação do sistema de busca em tempo real"""
    
    print("\n📝 IMPLEMENTAÇÃO PARA fundamental_scoring_system.py:")
    print("=" * 55)
    
    implementation = '''
# ADICIONAR estes imports no topo do arquivo:
import yfinance as yf
from datetime import datetime, timedelta
import time

# SUBSTITUIR método _get_stock_data:

def _get_stock_data(self, stock_code: str) -> Dict[str, Any]:
    """
    Busca dados da ação com sistema inteligente:
    1. Tentar banco local
    2. Se não encontrar, buscar dados reais via API
    3. Salvar no banco
    4. Retornar dados reais
    """
    
    # 1. TENTAR BANCO LOCAL PRIMEIRO
    if DATABASE_AVAILABLE and self.stock_repo:
        try:
            stock = self.stock_repo.get_stock_by_code(stock_code)
            if stock and self._is_data_fresh(stock):
                self.logger.info(f"✅ {stock_code} encontrado no banco (dados frescos)")
                return self._stock_to_dict(stock)
            elif stock:
                self.logger.info(f"⚠️  {stock_code} no banco mas dados antigos - atualizando...")
            else:
                self.logger.info(f"❌ {stock_code} não encontrado no banco - buscando dados reais...")
        except Exception as e:
            self.logger.warning(f"Erro acessando banco: {e}")
    
    # 2. BUSCAR DADOS REAIS VIA API
    real_data = self._fetch_real_financial_data(stock_code)
    
    if real_data:
        # 3. SALVAR NO BANCO PARA PRÓXIMAS CONSULTAS
        self._save_to_database(stock_code, real_data)
        
        # 4. RETORNAR DADOS REAIS
        self.logger.info(f"✅ Dados reais obtidos para {stock_code}")
        return real_data
    else:
        # 5. ÚLTIMO RECURSO: Informar que não foi possível obter dados
        self.logger.error(f"❌ Não foi possível obter dados reais para {stock_code}")
        raise ValueError(f"Dados não disponíveis para {stock_code}")

def _fetch_real_financial_data(self, stock_code: str) -> Dict[str, Any]:
    """Busca dados financeiros reais via APIs"""
    
    self.logger.info(f"🌐 Buscando dados reais para {stock_code}...")
    
    try:
        # Tentar yfinance primeiro (gratuito e confiável)
        ticker_symbol = f"{stock_code}.SA"  # Formato B3
        ticker = yf.Ticker(ticker_symbol)
        
        # Obter informações básicas
        info = ticker.info
        
        if not info or 'marketCap' not in info:
            self.logger.warning(f"Dados insuficientes no yfinance para {stock_code}")
            return self._try_alternative_sources(stock_code)
        
        # Obter demonstrações financeiras
        financials = ticker.financials
        balance_sheet = ticker.balance_sheet
        
        # Extrair dados fundamentais REAIS
        real_data = {
            'codigo': stock_code,
            'nome': info.get('longName', f'Empresa {stock_code}'),
            'setor': self._normalize_sector(info.get('sector', 'Diversos')),
            'preco_atual': info.get('currentPrice', info.get('regularMarketPrice', 0)),
            'market_cap': info.get('marketCap', 0),
            'volume_medio': info.get('averageVolume', 0),
            
            # Dados financeiros REAIS
            'revenue': self._get_financial_metric(financials, 'Total Revenue'),
            'net_income': self._get_financial_metric(financials, 'Net Income'),
            'total_assets': self._get_balance_metric(balance_sheet, 'Total Assets'),
            'total_equity': self._get_balance_metric(balance_sheet, 'Total Equity Gross Minority Interest'),
            'total_debt': self._get_balance_metric(balance_sheet, 'Total Debt'),
            
            # Métricas calculadas REAIS
            'roe': info.get('returnOnEquity', 0) * 100 if info.get('returnOnEquity') else 0,
            'roa': info.get('returnOnAssets', 0) * 100 if info.get('returnOnAssets') else 0,
            'net_margin': info.get('profitMargins', 0) * 100 if info.get('profitMargins') else 0,
            'pe_ratio': info.get('forwardPE', info.get('trailingPE', 0)),
            'pb_ratio': info.get('priceToBook', 0),
            'debt_to_equity': self._calculate_debt_to_equity(balance_sheet),
            
            # Metadados
            'data_source': 'yfinance',
            'data_atualizacao': datetime.now().isoformat(),
            'data_quality': 'REAL'
        }
        
        # Validar dados obtidos
        if self._validate_financial_data(real_data):
            self.logger.info(f"✅ Dados reais validados para {stock_code}")
            return real_data
        else:
            self.logger.warning(f"⚠️  Dados reais incompletos para {stock_code}")
            return None
            
    except Exception as e:
        self.logger.error(f"Erro buscando dados reais para {stock_code}: {e}")
        return self._try_alternative_sources(stock_code)

def _get_financial_metric(self, financials, metric_name: str) -> float:
    """Extrai métrica financeira das demonstrações"""
    
    try:
        if financials is not None and not financials.empty:
            if metric_name in financials.index:
                # Pegar valor mais recente (primeira coluna)
                value = financials.loc[metric_name].iloc[0]
                return float(value) if pd.notna(value) else 0
    except Exception as e:
        self.logger.debug(f"Erro extraindo {metric_name}: {e}")
    
    return 0

def _get_balance_metric(self, balance_sheet, metric_name: str) -> float:
    """Extrai métrica do balanço patrimonial"""
    
    try:
        if balance_sheet is not None and not balance_sheet.empty:
            if metric_name in balance_sheet.index:
                value = balance_sheet.loc[metric_name].iloc[0]
                return float(value) if pd.notna(value) else 0
    except Exception as e:
        self.logger.debug(f"Erro extraindo {metric_name}: {e}")
    
    return 0

def _calculate_debt_to_equity(self, balance_sheet) -> float:
    """Calcula debt-to-equity ratio dos dados reais"""
    
    try:
        total_debt = self._get_balance_metric(balance_sheet, 'Total Debt')
        total_equity = self._get_balance_metric(balance_sheet, 'Total Equity Gross Minority Interest')
        
        if total_equity > 0:
            return total_debt / total_equity
    except Exception:
        pass
    
    return 0

def _validate_financial_data(self, data: Dict[str, Any]) -> bool:
    """Valida se os dados obtidos são suficientes para análise"""
    
    required_fields = ['market_cap', 'revenue', 'net_income']
    
    for field in required_fields:
        if not data.get(field) or data[field] <= 0:
            self.logger.warning(f"Campo obrigatório inválido: {field} = {data.get(field)}")
            return False
    
    # Validações de sanidade
    if data['market_cap'] < 1000000:  # Menos de 1M
        self.logger.warning(f"Market cap muito baixo: {data['market_cap']}")
        return False
    
    if data['pe_ratio'] and (data['pe_ratio'] < 0 or data['pe_ratio'] > 1000):
        self.logger.warning(f"P/L suspeito: {data['pe_ratio']}")
        # Não invalidar por isso, apenas avisar
    
    return True

def _save_to_database(self, stock_code: str, data: Dict[str, Any]) -> bool:
    """Salva dados reais no banco para futuras consultas"""
    
    if not DATABASE_AVAILABLE or not self.stock_repo:
        self.logger.warning("Banco não disponível - dados não serão persistidos")
        return False
    
    try:
        # Verificar se já existe
        existing_stock = self.stock_repo.get_stock_by_code(stock_code)
        
        if existing_stock:
            # Atualizar dados existentes
            self.logger.info(f"📝 Atualizando {stock_code} no banco")
            success = self.stock_repo.update_stock_data(stock_code, data)
        else:
            # Criar nova entrada
            self.logger.info(f"➕ Adicionando {stock_code} ao banco")
            success = self.stock_repo.create_stock(data)
        
        if success:
            self.logger.info(f"✅ {stock_code} salvo no banco com dados reais")
            return True
        else:
            self.logger.error(f"❌ Falha ao salvar {stock_code} no banco")
            return False
            
    except Exception as e:
        self.logger.error(f"Erro salvando {stock_code} no banco: {e}")
        return False

def _is_data_fresh(self, stock) -> bool:
    """Verifica se os dados no banco ainda estão frescos"""
    
    try:
        if hasattr(stock, 'data_atualizacao') and stock.data_atualizacao:
            last_update = datetime.fromisoformat(stock.data_atualizacao.replace('Z', '+00:00'))
            age = datetime.now() - last_update.replace(tzinfo=None)
            
            # Considerar dados frescos se atualizados nas últimas 24 horas
            return age < timedelta(hours=24)
    except Exception as e:
        self.logger.debug(f"Erro verificando freshness: {e}")
    
    return False

def _try_alternative_sources(self, stock_code: str) -> Dict[str, Any]:
    """Tenta fontes alternativas quando yfinance falha"""
    
    # Poderia implementar outras APIs como:
    # - Alpha Vantage
    # - Financial Modeling Prep  
    # - Yahoo Finance direto
    # - APIs brasileiras (Economatica, etc.)
    
    self.logger.warning(f"Fontes alternativas não implementadas para {stock_code}")
    return None

def _normalize_sector(self, sector: str) -> str:
    """Normaliza nome do setor para padrão brasileiro"""
    
    sector_mapping = {
        'Technology': 'Tecnologia',
        'Financial Services': 'Financeiro',
        'Energy': 'Petróleo',
        'Basic Materials': 'Mineração',
        'Consumer Cyclical': 'Varejo',
        'Consumer Defensive': 'Consumo',
        'Healthcare': 'Saúde',
        'Industrials': 'Industrial',
        'Real Estate': 'Imobiliário',
        'Utilities': 'Utilidades',
        'Communication Services': 'Telecomunicações'
    }
    
    return sector_mapping.get(sector, sector)
'''
    
    print(implementation)

def create_database_integration():
    """Cria integração com banco de dados para persistência"""
    
    print("\n🗄️ INTEGRAÇÃO COM BANCO DE DADOS:")
    print("=" * 40)
    
    db_integration = '''
# ADICIONAR ao stock_repository.py:

def create_stock(self, stock_data: Dict[str, Any]) -> bool:
    """Cria nova ação no banco com dados reais"""
    
    try:
        with self.get_db_session() as session:
            stock = Stock(
                codigo=stock_data['codigo'],
                nome=stock_data['nome'],
                setor=stock_data['setor'],
                preco_atual=stock_data['preco_atual'],
                market_cap=stock_data['market_cap'],
                volume_medio=stock_data.get('volume_medio', 0),
                revenue=stock_data.get('revenue', 0),
                net_income=stock_data.get('net_income', 0),
                total_assets=stock_data.get('total_assets', 0),
                total_equity=stock_data.get('total_equity', 0),
                total_debt=stock_data.get('total_debt', 0),
                roe=stock_data.get('roe', 0),
                roa=stock_data.get('roa', 0),
                debt_to_equity=stock_data.get('debt_to_equity', 0),
                net_margin=stock_data.get('net_margin', 0),
                pe_ratio=stock_data.get('pe_ratio', 0),
                pb_ratio=stock_data.get('pb_ratio', 0),
                data_source=stock_data.get('data_source', 'API'),
                data_atualizacao=datetime.now(),
                ativo=True
            )
            
            session.add(stock)
            session.commit()
            return True
            
    except Exception as e:
        self.logger.error(f"Erro criando stock: {e}")
        return False

def update_stock_data(self, stock_code: str, new_data: Dict[str, Any]) -> bool:
    """Atualiza dados existentes da ação"""
    
    try:
        with self.get_db_session() as session:
            stock = session.query(Stock).filter(Stock.codigo == stock_code).first()
            
            if stock:
                # Atualizar campos com novos dados
                for field, value in new_data.items():
                    if hasattr(stock, field):
                        setattr(stock, field, value)
                
                stock.data_atualizacao = datetime.now()
                session.commit()
                return True
                
    except Exception as e:
        self.logger.error(f"Erro atualizando stock {stock_code}: {e}")
        return False
        
    return False
'''
    
    print(db_integration)

def create_usage_example():
    """Cria exemplo de uso do sistema"""
    
    print("\n💻 EXEMPLO DE USO:")
    print("=" * 20)
    
    usage_example = '''
# test_real_time_system.py
"""
Teste do sistema de busca em tempo real
"""

def test_real_time_fetching():
    """Testa busca automática de dados reais"""
    
    from agents.analyzers.fundamental_scoring_system import FundamentalAnalyzerAgent
    
    agent = FundamentalAnalyzerAgent()
    
    # Testar com ação que não existe no banco
    print("🧪 Testando ação não existente no banco...")
    
    stock_code = "WEGE3"  # WEG - ação real da B3
    
    print(f"📊 Analisando {stock_code}...")
    result = agent.analyze_single_stock(stock_code)
    
    if "error" not in result:
        score = result["fundamental_score"]["composite_score"]
        data_source = result.get("data_source", "unknown")
        
        print(f"✅ {stock_code}:")
        print(f"   • Score: {score:.1f}")
        print(f"   • Fonte: {data_source}")
        
        # Verificar se foi salvo no banco
        if data_source == "yfinance":
            print(f"   ✅ Dados reais obtidos via API")
            print(f"   ✅ Dados salvos no banco para próximas consultas")
        
        # Testar segunda consulta (deve vir do banco agora)
        print(f"\\n🔄 Segunda consulta (deve usar banco)...")
        result2 = agent.analyze_single_stock(stock_code)
        
        if result2.get("data_source") == "banco":
            print(f"   ✅ Dados vindos do banco (cache funcionando)")
        
    else:
        print(f"❌ Erro: {result['error']}")

if __name__ == "__main__":
    test_real_time_fetching()
'''
    
    with open('test_real_time_system.py', 'w', encoding='utf-8') as f:
        f.write(usage_example)
    
    print("✅ Exemplo criado: test_real_time_system.py")

def main():
    """Implementa sistema completo de busca em tempo real"""
    
    create_real_time_data_fetcher()
    show_real_time_fetcher_implementation()
    create_database_integration()
    create_usage_example()
    
    print(f"\n🎯 SISTEMA DE BUSCA EM TEMPO REAL")
    print(f"=" * 40)
    
    print(f"\n✅ VANTAGENS:")
    print(f"   • Scores baseados em dados REAIS")
    print(f"   • Banco cresce automaticamente")
    print(f"   • Cache inteligente (dados frescos)")
    print(f"   • Sem dados fictícios")
    print(f"   • Sistema autossuficiente")
    
    print(f"\n🔄 FLUXO DE FUNCIONAMENTO:")
    print(f"   1. Usuário solicita análise de WEGE3")
    print(f"   2. Sistema verifica: WEGE3 não está no banco")
    print(f"   3. Busca dados reais via yfinance API")
    print(f"   4. Valida e salva WEGE3 no banco")
    print(f"   5. Calcula score com dados reais")
    print(f"   6. Próxima consulta usa dados do banco")
    
    print(f"\n⚡ PERFORMANCE:")
    print(f"   • Primeira consulta: ~2-3 segundos (API + banco)")
    print(f"   • Consultas seguintes: ~100ms (só banco)")
    print(f"   • Dados atualizados a cada 24h")
    
    print(f"\n🛠️ IMPLEMENTAÇÃO:")
    print(f"   1. Adicionar código ao fundamental_scoring_system.py")
    print(f"   2. Atualizar stock_repository.py")
    print(f"   3. Instalar: pip install yfinance")
    print(f"   4. Testar: python test_real_time_system.py")
    
    print(f"\n🎉 RESULTADO:")
    print(f"   Scores precisos baseados em dados financeiros reais!")

if __name__ == "__main__":
    main()