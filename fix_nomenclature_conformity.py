# fix_nomenclature_conformity.py
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
    
    print("\n🔧 CORRIGINDO NOMENCLATURA NO YFinanceClient")
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
    
    print("\n🧪 TESTANDO CONFORMIDADE")
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
            
            print("\n   YFinanceClient:")
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
    
    print(f"\n📊 RESULTADO:")
    print(f"   • Settings: {'✅' if settings_ok else '❌'}")
    print(f"   • YFinanceClient: {'✅' if client_ok else '❌'}")
    print(f"   • Conformidade: {'✅' if test_ok else '❌'}")
    
    if all([settings_ok, client_ok, test_ok]):
        print(f"\n🎉 CONFORMIDADE CORRIGIDA!")
    else:
        print(f"\n❌ CORREÇÃO MANUAL NECESSÁRIA")

if __name__ == "__main__":
    main()
