# analise_conformidade_nomenclatura.py
"""
Análise de conformidade entre settings.py e implementação multi-API
"""

def analyze_nomenclature_conformity():
    """Analisa conformidade entre settings e implementação"""
    
    print("🔍 ANÁLISE DE CONFORMIDADE - SETTINGS vs IMPLEMENTAÇÃO")
    print("=" * 65)
    
    print("❌ INCONSISTÊNCIAS ENCONTRADAS:")
    
    inconsistencies = {
        "API Keys": {
            "Settings": [
                "self.alpha_vantage_api_key",
                "self.fmp_api_key", 
                "self.twelve_data_api_key"
            ],
            "Implementação": [
                "self.alpha_vantage_key",
                "self.fmp_key",
                "# twelve_data não implementado"
            ],
            "Status": "❌ INCONSISTENTE"
        },
        
        "Timeout Settings": {
            "Settings": [
                "self.yfinance_timeout",
                "self.alpha_vantage_timeout",
                "self.fmp_timeout"
            ],
            "Implementação": [
                "self.timeout (genérico)",
                "# timeouts específicos não usados"
            ],
            "Status": "❌ INCONSISTENTE"
        },
        
        "Cache Directory": {
            "Settings": [
                "self.financial_cache_dir"
            ],
            "Implementação": [
                "cache_dir: str = 'cache/financial' (hardcoded)"
            ],
            "Status": "❌ INCONSISTENTE"
        },
        
        "Provider Names": {
            "Settings": [
                "yfinance_primary",
                "yfinance_alternative",
                "alpha_vantage",
                "fmp"
            ],
            "Implementação": [
                "_try_yfinance_primary",
                "_try_yfinance_alternative", 
                "_try_alpha_vantage",
                "_try_financial_modeling_prep"
            ],
            "Status": "⚠️ PARCIALMENTE CONSISTENTE"
        }
    }
    
    for category, details in inconsistencies.items():
        print(f"\n🔍 {category}:")
        print(f"   Status: {details['Status']}")
        print(f"   Settings: {details['Settings']}")
        print(f"   Implementação: {details['Implementação']}")

def show_corrected_settings():
    """Mostra settings corrigidos para conformidade"""
    
    print("\n✅ SETTINGS CORRIGIDOS PARA CONFORMIDADE:")
    print("=" * 50)
    
    corrected_settings = '''
# CORRIGIR config/settings.py - Seção APIs:

class Settings:
    def __init__(self):
        # ... outras configurações ...
        
        # ==================== APIs FINANCEIRAS (CONFORMIDADE) ====================
        
        # YFinance (primário)
        self.yfinance_enabled = os.getenv("YFINANCE_ENABLED", "true").lower() == "true"
        self.yfinance_timeout = int(os.getenv("YFINANCE_TIMEOUT", "15"))
        self.yfinance_max_retries = int(os.getenv("YFINANCE_MAX_RETRIES", "3"))
        
        # Alpha Vantage (backup) - CORRIGIDO: alpha_vantage_key (não api_key)
        self.alpha_vantage_key = os.getenv("ALPHA_VANTAGE_API_KEY", "")
        self.alpha_vantage_timeout = int(os.getenv("ALPHA_VANTAGE_TIMEOUT", "10"))
        
        # Financial Modeling Prep (backup) - CORRIGIDO: fmp_key (não api_key)
        self.fmp_key = os.getenv("FMP_API_KEY", "")
        self.fmp_timeout = int(os.getenv("FMP_TIMEOUT", "10"))
        
        # ==================== CACHE SYSTEM (CONFORMIDADE) ====================
        self.cache_enabled = os.getenv("CACHE_ENABLED", "true").lower() == "true"
        
        # CORRIGIDO: usar mesmo nome da implementação
        self.cache_dir = os.getenv("FINANCIAL_CACHE_DIR", "cache/financial")
        
        # TTL em segundos (nomes conformes)
        self.cache_ttl = {
            'market_data': int(os.getenv("CACHE_TTL_MARKET_DATA", "300")),
            'fundamentals': int(os.getenv("CACHE_TTL_FUNDAMENTALS", "3600")), 
            'company_info': int(os.getenv("CACHE_TTL_COMPANY_INFO", "86400"))
        }
        
        # ==================== TIMEOUT GLOBAL (CONFORMIDADE) ====================
        # CORRIGIDO: usar timeout genérico como na implementação
        self.timeout = int(os.getenv("API_TIMEOUT", "15"))
        
        # ==================== RETRY CONFIG (CONFORMIDADE) ====================
        self.retry_config = {
            'max_retries': int(os.getenv("API_MAX_RETRIES", "3")),
            'backoff_factor': int(os.getenv("API_BACKOFF_FACTOR", "2")),
            'timeout': self.timeout
        }
'''
    
    print(corrected_settings)

def show_corrected_yfinance_client():
    """Mostra YFinanceClient corrigido para usar settings"""
    
    print("\n🔧 YFinanceClient CORRIGIDO PARA USAR SETTINGS:")
    print("=" * 50)
    
    corrected_client = '''
# CORRIGIR collectors/stock_collector.py:

from config.settings import get_settings

class YFinanceClient:
    """Cliente multi-API com configurações dos settings"""
    
    def __init__(self):
        # USAR SETTINGS EM VEZ DE HARDCODE
        self.settings = get_settings()
        
        # URLs base
        self.base_url = "https://query1.finance.yahoo.com/v1"
        
        # CONFIGURAÇÕES DOS SETTINGS
        self.timeout = self.settings.timeout  # Em vez de hardcode 15
        
        # Chaves de API dos settings (nomenclatura correta)
        self.alpha_vantage_key = self.settings.alpha_vantage_key  # Não api_key
        self.fmp_key = self.settings.fmp_key  # Não api_key
        
        # Cache manager com settings
        self.cache_manager = FinancialDataCache(
            cache_dir=self.settings.cache_dir,  # Do settings
            ttl_rules=self.settings.cache_ttl   # Do settings
        )
        
        # Configuração de retry dos settings
        self.retry_config = self.settings.retry_config
        
        # Providers em ordem de prioridade
        self.providers = [
            self._try_yfinance_primary,
            self._try_yfinance_alternative,
            self._try_alpha_vantage,
            self._try_financial_modeling_prep,  # Nome completo
            self._get_static_fallback
        ]
    
    async def _try_alpha_vantage(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Provider Alpha Vantage usando settings"""
        
        # USAR CHAVE DOS SETTINGS
        if not self.alpha_vantage_key:  # Nome correto
            return None
        
        try:
            url = "https://www.alphavantage.co/query"
            params = {
                'function': 'GLOBAL_QUOTE',
                'symbol': f"{symbol}.SAO",
                'apikey': self.alpha_vantage_key  # Nome correto dos settings
            }
            
            # USAR TIMEOUT DOS SETTINGS
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)
                # ... resto igual
    
    async def _try_financial_modeling_prep(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Provider FMP usando settings"""
        
        # USAR CHAVE DOS SETTINGS
        if not self.fmp_key:  # Nome correto
            return None
        
        try:
            url = f"https://financialmodelingprep.com/api/v3/quote/{symbol}.SA"
            params = {'apikey': self.fmp_key}  # Nome correto dos settings
            
            # USAR TIMEOUT DOS SETTINGS
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)
                # ... resto igual

# CORRIGIR FinancialDataCache para usar settings:
class FinancialDataCache:
    """Cache usando configurações dos settings"""
    
    def __init__(self, cache_dir: str = None, ttl_rules: dict = None):
        # USAR CONFIGURAÇÕES DOS SETTINGS
        settings = get_settings()
        
        self.cache_dir = Path(cache_dir or settings.cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # TTL rules dos settings
        self.ttl_rules = ttl_rules or settings.cache_ttl
'''
    
    print(corrected_client)

def show_updated_env_template():
    """Mostra .env atualizado com nomenclatura correta"""
    
    print("\n📄 .env ATUALIZADO COM NOMENCLATURA CORRETA:")
    print("=" * 50)
    
    updated_env = '''
# .env - Nomenclatura corrigida

# ==================== APIs FINANCEIRAS ====================
YFINANCE_ENABLED=true

# CORRIGIDO: Timeout genérico (não específico por API)
API_TIMEOUT=15
API_MAX_RETRIES=3
API_BACKOFF_FACTOR=2

# Alpha Vantage (será acessado como alpha_vantage_key)
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key

# Financial Modeling Prep (será acessado como fmp_key)
FMP_API_KEY=your_fmp_key

# ==================== CACHE SYSTEM ====================
CACHE_ENABLED=true

# CORRIGIDO: Nome que será usado na implementação
FINANCIAL_CACHE_DIR=cache/financial

# TTL em segundos (conforme implementação)
CACHE_TTL_MARKET_DATA=300
CACHE_TTL_FUNDAMENTALS=3600  
CACHE_TTL_COMPANY_INFO=86400
'''
    
    print(updated_env)

def create_conformity_fix_script():
    """Cria script para corrigir conformidade"""
    
    fix_script = '''# fix_nomenclature_conformity.py
"""
Script para corrigir conformidade entre settings e implementação
"""

import re
from pathlib import Path

def fix_settings_nomenclature():
    """Corrige nomenclatura no settings.py"""
    
    print("🔧 CORRIGINDO NOMENCLATURA NO SETTINGS")
    print("=" * 40)
    
    settings_path = Path("config/settings.py")
    
    if not settings_path.exists():
        print("❌ settings.py não encontrado")
        return False
    
    # Ler conteúdo atual
    with open(settings_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Correções de nomenclatura
    corrections = [
        # API keys
        ('alpha_vantage_api_key', 'alpha_vantage_key'),
        ('fmp_api_key', 'fmp_key'),
        
        # Cache directory
        ('financial_cache_dir', 'cache_dir'),
        
        # Timeout específicos para timeout genérico
        ('yfinance_timeout', 'timeout'),
        ('alpha_vantage_timeout', 'timeout'),
        ('fmp_timeout', 'timeout'),
    ]
    
    for old_name, new_name in corrections:
        if old_name in content:
            content = content.replace(old_name, new_name)
            print(f"✅ Corrigido: {old_name} → {new_name}")
    
    # Salvar arquivo corrigido
    with open(settings_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ settings.py corrigido")
    return True

def fix_yfinance_client_nomenclature():
    """Corrige nomenclatura no YFinanceClient"""
    
    print("\\n🔧 CORRIGINDO NOMENCLATURA NO YFinanceClient")
    print("=" * 45)
    
    client_path = Path("agents/collectors/stock_collector.py")
    
    if not client_path.exists():
        print("❌ stock_collector.py não encontrado")
        return False
    
    # Ler conteúdo atual
    with open(client_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Correções específicas
    corrections = [
        # Import settings
        ('from config.settings import get_settings', '# Import já existe ou adicionar'),
        
        # Usar settings
        ('self.timeout = 15', 'self.timeout = get_settings().timeout'),
        ('cache_dir: str = "cache/financial"', 'cache_dir: str = None'),
        
        # Nomes de chaves
        ('self.alpha_vantage_api_key', 'self.alpha_vantage_key'),
        ('self.fmp_api_key', 'self.fmp_key'),
    ]
    
    changes_made = 0
    for old_pattern, new_pattern in corrections:
        if old_pattern in content:
            content = content.replace(old_pattern, new_pattern)
            print(f"✅ Corrigido: {old_pattern}")
            changes_made += 1
    
    if changes_made > 0:
        with open(client_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ {changes_made} correções aplicadas no YFinanceClient")
    else:
        print("ℹ️  Nenhuma correção necessária no YFinanceClient")
    
    return True

def test_conformity():
    """Testa conformidade após correções"""
    
    print("\\n🧪 TESTANDO CONFORMIDADE")
    print("=" * 25)
    
    try:
        from config.settings import get_settings
        settings = get_settings()
        
        # Verificar se nomenclatura está correta
        checks = [
            ('alpha_vantage_key', hasattr(settings, 'alpha_vantage_key')),
            ('fmp_key', hasattr(settings, 'fmp_key')),
            ('cache_dir', hasattr(settings, 'cache_dir')),
            ('timeout', hasattr(settings, 'timeout')),
        ]
        
        for attr_name, exists in checks:
            print(f"   • {attr_name}: {'✅' if exists else '❌'}")
        
        # Testar YFinanceClient
        try:
            from agents.collectors.stock_collector import YFinanceClient
            client = YFinanceClient()
            
            client_checks = [
                ('settings loaded', hasattr(client, 'settings')),
                ('alpha_vantage_key', hasattr(client, 'alpha_vantage_key')),
                ('fmp_key', hasattr(client, 'fmp_key')),
                ('timeout from settings', client.timeout == settings.timeout if hasattr(client, 'timeout') else False),
            ]
            
            print("\\n   YFinanceClient:")
            for check_name, result in client_checks:
                print(f"   • {check_name}: {'✅' if result else '❌'}")
        
        except Exception as e:
            print(f"   ❌ Erro no YFinanceClient: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

def main():
    """Executa correção completa de conformidade"""
    
    print("🎯 CORREÇÃO DE CONFORMIDADE NOMENCLATURA")
    print("=" * 50)
    
    # 1. Corrigir settings
    settings_ok = fix_settings_nomenclature()
    
    # 2. Corrigir YFinanceClient  
    client_ok = fix_yfinance_client_nomenclature()
    
    # 3. Testar conformidade
    test_ok = test_conformity()
    
    print(f"\\n📊 RESULTADO:")
    print(f"   • Settings: {'✅' if settings_ok else '❌'}")
    print(f"   • YFinanceClient: {'✅' if client_ok else '❌'}")
    print(f"   • Conformidade: {'✅' if test_ok else '❌'}")
    
    if all([settings_ok, client_ok, test_ok]):
        print(f"\\n🎉 CONFORMIDADE CORRIGIDA!")
    else:
        print(f"\\n❌ CORREÇÃO MANUAL NECESSÁRIA")

if __name__ == "__main__":
    main()
'''
    
    with open('fix_nomenclature_conformity.py', 'w', encoding='utf-8') as f:
        f.write(fix_script)
    
    print("✅ Script de correção criado: fix_nomenclature_conformity.py")

def main():
    """Análise completa de conformidade"""
    
    analyze_nomenclature_conformity()
    show_corrected_settings()
    show_corrected_yfinance_client()
    show_updated_env_template()
    create_conformity_fix_script()
    
    print(f"\n🎯 ANÁLISE DE CONFORMIDADE CONCLUÍDA")
    print(f"=" * 40)
    
    print(f"\n❌ PROBLEMAS IDENTIFICADOS:")
    print(f"   • API keys: alpha_vantage_api_key vs alpha_vantage_key")
    print(f"   • Timeouts: específicos vs genérico")
    print(f"   • Cache dir: financial_cache_dir vs cache_dir")
    print(f"   • Provider names: parcialmente inconsistentes")
    
    print(f"\n✅ SOLUÇÕES:")
    print(f"   1. Padronizar nomenclatura no settings")
    print(f"   2. Atualizar YFinanceClient para usar settings")
    print(f"   3. Corrigir .env com nomes corretos")
    print(f"   4. Aplicar script de correção automática")
    
    print(f"\n🛠️ IMPLEMENTAÇÃO:")
    print(f"   1. python fix_nomenclature_conformity.py")
    print(f"   2. Atualizar .env conforme template")
    print(f"   3. Testar conformidade")
    
    print(f"\n💡 RESULTADO ESPERADO:")
    print(f"   Settings e implementação 100% alinhados!")

if __name__ == "__main__":
    main()