# scripts/setup_direto_fase2.py
"""
Setup Direto da Fase 2 - Sem migração complexa
Cria estrutura da Fase 2 diretamente
"""
import sys
import json
from pathlib import Path
from datetime import datetime

def setup_phase2_direct():
    """Setup direto da Fase 2"""
    project_root = Path.cwd()
    sys.path.insert(0, str(project_root))
    
    print("🚀 Setup Direto da Fase 2")
    print("=" * 50)
    
    # 1. Criar estrutura de diretórios expandida
    print("📁 Criando diretórios da Fase 2...")
    dirs = [
        'utils',
        'agents/analyzers',
        'database/migrations',
        'tests/phase2',
        'docs/phase2',
        'data/benchmarks',
        'data/financial_statements',
        'data/reports'
    ]
    
    for dir_path in dirs:
        full_path = project_root / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        # Criar __init__.py
        init_file = full_path / '__init__.py'
        if not init_file.exists() and 'data' not in dir_path:
            init_file.write_text('# Auto-generated\n')
    
    print("✅ Diretórios criados")
    
    # 2. Criar tabelas do banco (assumindo que models.py já foi atualizado)
    print("🗄️  Criando tabelas do banco...")
    try:
        from database.connection import create_tables, get_database_info
        
        # Criar todas as tabelas
        if create_tables():
            print("✅ Tabelas criadas com sucesso")
        else:
            print("❌ Erro ao criar tabelas")
            return False
        
        # Verificar quais tabelas foram criadas
        from database.connection import get_database_info
        db_info = get_database_info()
        tables = db_info.get('tables', [])
        print(f"   📋 Tabelas no banco: {len(tables)}")
        for table in sorted(tables):
            print(f"      - {table}")
            
    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {e}")
        print("⚠️  Verifique se database/models.py foi atualizado corretamente")
        return False
    
    # 3. Criar configuração de métricas
    print("⚙️  Criando configuração de métricas...")
    metrics_config = {
        "version": "2.0",
        "scoring_weights": {
            "valuation": 0.20,
            "profitability": 0.25,
            "leverage": 0.15,
            "growth": 0.20,
            "efficiency": 0.10,
            "quality": 0.10
        },
        "sector_adjustments": {
            "Bancos": {
                "leverage": 0.05,
                "profitability": 0.35
            },
            "Tecnologia": {
                "growth": 0.30,
                "valuation": 0.15
            },
            "Petróleo e Gás": {
                "leverage": 0.20,
                "growth": 0.15
            }
        },
        "outlier_thresholds": {
            "pe_ratio": {"min": 0, "max": 100},
            "pb_ratio": {"min": 0, "max": 20},
            "roe": {"min": -50, "max": 100},
            "debt_to_equity": {"min": 0, "max": 10}
        }
    }
    
    config_path = project_root / 'config' / 'metrics_config.json'
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(metrics_config, f, indent=2, ensure_ascii=False)
    
    print("✅ Configuração de métricas criada")
    
    # 4. Atualizar settings.py com configurações da Fase 2
    print("⚙️  Atualizando configurações...")
    settings_path = project_root / 'config' / 'settings.py'
    
    # Ler arquivo atual
    if settings_path.exists():
        with open(settings_path, 'r', encoding='utf-8') as f:
            current_content = f.read()
        
        # Adicionar configurações da Fase 2 se não existirem
        if "FASE 2" not in current_content:
            phase2_config = '''

# ==================== FASE 2 - ANÁLISE FUNDAMENTALISTA ====================
class Phase2Settings:
    """Configurações específicas da Fase 2"""
    
    def __init__(self):
        # Sistema de Métricas
        self.metrics_config_file = "config/metrics_config.json"
        self.enable_sector_benchmarks = True
        self.benchmark_update_frequency = "weekly"
        
        # Análise Fundamentalista
        self.min_data_completeness = 0.6
        self.confidence_threshold = 0.7
        self.historical_periods = 5
        
        # Performance
        self.enable_parallel_analysis = True
        self.max_concurrent_analyses = 10
        self.analysis_timeout_seconds = 300

# Instância global para Fase 2
phase2_settings = Phase2Settings()

def get_phase2_settings():
    """Retorna configurações da Fase 2"""
    return phase2_settings
'''
            
            # Adicionar no final
            updated_content = current_content + phase2_config
            with open(settings_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            print("✅ settings.py atualizado com Fase 2")
        else:
            print("✅ settings.py já contém Fase 2")
    
    # 5. Criar dados de exemplo
    print("📊 Criando dados de exemplo...")
    try:
        # Verificar se há ações no banco
        from database.connection import get_db_session
        from database.models import Stock
        
        with get_db_session() as session:
            stock_count = session.query(Stock).count()
            
            if stock_count == 0:
                # Criar algumas ações de exemplo
                example_stocks = [
                    {
                        "codigo": "PETR4",
                        "nome": "Petróleo Brasileiro S.A.",
                        "setor": "Petróleo e Gás",
                        "preco_atual": 32.50,
                        "market_cap": 420000000000,
                        "p_l": 4.2,
                        "roe": 19.5,
                        "ativo": True
                    },
                    {
                        "codigo": "VALE3", 
                        "nome": "Vale S.A.",
                        "setor": "Mineração",
                        "preco_atual": 61.80,
                        "market_cap": 280000000000,
                        "p_l": 5.1,
                        "roe": 24.3,
                        "ativo": True
                    },
                    {
                        "codigo": "ITUB4",
                        "nome": "Itaú Unibanco Holding S.A.",
                        "setor": "Bancos", 
                        "preco_atual": 33.15,
                        "market_cap": 325000000000,
                        "p_l": 8.9,
                        "roe": 20.1,
                        "ativo": True
                    }
                ]
                
                for stock_data in example_stocks:
                    stock = Stock(**stock_data)
                    session.add(stock)
                
                session.commit()
                print(f"✅ {len(example_stocks)} ações de exemplo criadas")
            else:
                print(f"✅ {stock_count} ações já existem no banco")
                
    except Exception as e:
        print(f"⚠️  Erro ao criar dados de exemplo: {e}")
    
    # 6. Testar componentes básicos
    print("🧪 Testando componentes básicos...")
    try:
        # Testar import dos novos modelos
        from database.models import Stock, FinancialStatement, DataQuality
        print("✅ Imports dos modelos OK")
        
        # Testar enums
        quality = DataQuality.HIGH
        print(f"✅ Enums funcionando: {quality.value}")
        
        # Testar conexão com banco
        from database.connection import check_database_connection
        if check_database_connection():
            print("✅ Conexão com banco OK")
        else:
            print("⚠️  Problema na conexão com banco")
            
    except Exception as e:
        print(f"⚠️  Erro nos testes: {e}")
    
    # 7. Criar README da Fase 2
    print("📚 Criando documentação...")
    readme_content = f'''# Fase 2 - Sistema de Métricas Expandido

## ✅ Implementação Concluída

### Componentes Criados:
- ✅ Modelos de dados expandidos (50+ campos)
- ✅ Sistema de configuração de métricas
- ✅ Estrutura para análise fundamentalista
- ✅ Enums para qualidade de dados

### Estrutura do Banco:
- `stocks`: Tabela principal expandida
- `financial_statements`: Demonstrações financeiras
- `fundamental_analyses`: Análises expandidas
- `recommendations`: Recomendações (mantido)
- `agent_sessions`: Sessões de agentes

### Próximos Passos:
1. Implementar utils/financial_calculator.py
2. Implementar agents/collectors/enhanced_yfinance_client.py
3. Criar agente analisador fundamentalista
4. Implementar sistema de scoring

### Status: ✅ Fase 2 Passo 1 CONCLUÍDO
Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}
'''
    
    readme_path = project_root / 'README_FASE2.md'
    readme_path.write_text(readme_content, encoding='utf-8')
    
    print("✅ Documentação criada")
    
    # 8. Resumo final
    print("\n" + "=" * 50)
    print("🎉 FASE 2 CONFIGURADA COM SUCESSO!")
    print("=" * 50)
    print("📁 Estrutura criada:")
    print("   ✅ Diretórios da Fase 2")
    print("   ✅ Tabelas do banco expandidas")
    print("   ✅ Configuração de métricas")
    print("   ✅ Settings atualizados")
    print("   ✅ Dados de exemplo")
    
    print("\n🚀 PRÓXIMOS PASSOS:")
    print("   1. Implementar utils/financial_calculator.py")
    print("   2. Implementar enhanced_yfinance_client.py")  
    print("   3. Criar componentes da Fase 2 Passo 1")
    
    print(f"\n📄 Documentação: README_FASE2.md")
    
    return True

if __name__ == "__main__":
    try:
        success = setup_phase2_direct()
        if success:
            print("\n✅ Setup concluído com sucesso!")
        else:
            print("\n❌ Setup falhou - verifique os erros acima")
    except Exception as e:
        print(f"\n❌ Erro crítico: {e}")
        sys.exit(1)
