# scripts/setup_phase2_step1.py
"""
Script de Setup da Fase 2 - Passo 1: Expansão do Sistema de Métricas
Automatiza a implementação dos novos componentes
"""
import sys
import os
import logging
import subprocess
from pathlib import Path
from datetime import datetime
import json

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Cores para output
class Colors:
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    RED = '\033[0;31m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    WHITE = '\033[1;37m'
    NC = '\033[0m'


def print_header(text: str, color: str = Colors.BLUE):
    """Imprime cabeçalho colorido"""
    print(f"\n{color}{'='*60}{Colors.NC}")
    print(f"{color}{text.center(60)}{Colors.NC}")
    print(f"{color}{'='*60}{Colors.NC}")


def print_step(text: str):
    """Imprime passo atual"""
    print(f"\n{Colors.CYAN}📋 {text}{Colors.NC}")


def print_success(text: str):
    """Imprime sucesso"""
    print(f"{Colors.GREEN}✅ {text}{Colors.NC}")


def print_warning(text: str):
    """Imprime aviso"""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.NC}")


def print_error(text: str):
    """Imprime erro"""
    print(f"{Colors.RED}❌ {text}{Colors.NC}")


def print_info(text: str):
    """Imprime informação"""
    print(f"{Colors.WHITE}ℹ️  {text}{Colors.NC}")


class Phase2Step1Setup:
    """Configurador da Fase 2 Passo 1"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.success_count = 0
        self.error_count = 0
        self.setup_log = []
    
    def run_full_setup(self) -> bool:
        """Executa setup completo do Passo 1"""
        print_header("SETUP FASE 2 - PASSO 1", Colors.PURPLE)
        print_info("Expansão do Sistema de Métricas")
        print_info(f"Iniciado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        
        try:
            # Lista de tarefas
            tasks = [
                ("Verificar Pré-requisitos", self._check_prerequisites),
                ("Criar Estrutura de Diretórios", self._create_directory_structure),
                ("Instalar Dependências", self._install_dependencies),
                ("Configurar Novos Módulos", self._setup_new_modules),
                ("Migrar Banco de Dados", self._migrate_database),
                ("Configurar Sistema de Métricas", self._setup_metrics_system),
                ("Executar Testes Básicos", self._run_basic_tests),
                ("Gerar Relatório de Setup", self._generate_setup_report)
            ]
            
            for task_name, task_func in tasks:
                print_step(f"Executando: {task_name}")
                
                try:
                    success = task_func()
                    if success:
                        print_success(f"{task_name} - CONCLUÍDO")
                        self.success_count += 1
                        self._log_task(task_name, True)
                    else:
                        print_error(f"{task_name} - FALHOU")
                        self.error_count += 1
                        self._log_task(task_name, False)
                        
                except Exception as e:
                    print_error(f"{task_name} - EXCEÇÃO: {str(e)}")
                    self.error_count += 1
                    self._log_task(task_name, False, str(e))
            
            # Resumo final
            self._print_final_summary()
            
            return self.error_count == 0
            
        except Exception as e:
            print_error(f"Erro crítico no setup: {e}")
            return False
    
    def _check_prerequisites(self) -> bool:
        """Verifica pré-requisitos"""
        try:
            print_info("Verificando pré-requisitos...")
            
            # Verificar Python
            python_version = sys.version_info
            if python_version < (3, 11):
                print_error(f"Python 3.11+ necessário. Versão atual: {python_version.major}.{python_version.minor}")
                return False
            
            # Verificar ambiente virtual
            if not os.environ.get('VIRTUAL_ENV'):
                print_warning("Ambiente virtual não detectado")
            
            # Verificar dependências críticas da Fase 1
            critical_modules = ['agno', 'sqlalchemy', 'fastapi', 'pandas', 'numpy']
            missing_modules = []
            
            for module in critical_modules:
                try:
                    __import__(module)
                except ImportError:
                    missing_modules.append(module)
            
            if missing_modules:
                print_error(f"Módulos faltando: {missing_modules}")
                return False
            
            # Verificar estrutura da Fase 1
            required_dirs = ['agents', 'database', 'config', 'utils']
            missing_dirs = [d for d in required_dirs if not (self.project_root / d).exists()]
            
            if missing_dirs:
                print_error(f"Diretórios da Fase 1 faltando: {missing_dirs}")
                return False
            
            print_success("Pré-requisitos verificados")
            return True
            
        except Exception as e:
            print_error(f"Erro na verificação de pré-requisitos: {e}")
            return False
    
    def _create_directory_structure(self) -> bool:
        """Cria estrutura de diretórios para Fase 2"""
        try:
            print_info("Criando estrutura de diretórios...")
            
            # Novos diretórios para Fase 2
            new_dirs = [
                'utils',
                'agents/analyzers',
                'database/migrations',
                'tests/phase2',
                'docs/phase2',
                'data/benchmarks',
                'data/financial_statements'
            ]
            
            created_dirs = []
            for dir_path in new_dirs:
                full_path = self.project_root / dir_path
                if not full_path.exists():
                    full_path.mkdir(parents=True, exist_ok=True)
                    created_dirs.append(dir_path)
            
            if created_dirs:
                print_info(f"Diretórios criados: {', '.join(created_dirs)}")
            else:
                print_info("Estrutura de diretórios já existe")
            
            # Criar arquivos __init__.py necessários
            init_files = [
                'utils/__init__.py',
                'agents/analyzers/__init__.py'
            ]
            
            for init_file in init_files:
                init_path = self.project_root / init_file
                if not init_path.exists():
                    init_path.write_text('# Auto-generated __init__.py\n')
            
            return True
            
        except Exception as e:
            print_error(f"Erro ao criar estrutura: {e}")
            return False
    
    def _install_dependencies(self) -> bool:
        """Instala dependências adicionais da Fase 2"""
        try:
            print_info("Instalando dependências da Fase 2...")
            
            # Dependências adicionais necessárias
            additional_deps = [
                'scipy>=1.10.0',
                'scikit-learn>=1.3.0',
                'matplotlib>=3.6.0',
                'seaborn>=0.12.0',
                'plotly>=5.15.0',
                'openpyxl>=3.1.0',
                'xlsxwriter>=3.1.0'
            ]
            
            # Verificar quais já estão instaladas
            missing_deps = []
            for dep in additional_deps:
                module_name = dep.split('>=')[0].split('==')[0]
                try:
                    __import__(module_name)
                except ImportError:
                    missing_deps.append(dep)
            
            if missing_deps:
                print_info(f"Instalando: {', '.join(missing_deps)}")
                
                # Instalar via pip
                cmd = [sys.executable, '-m', 'pip', 'install'] + missing_deps
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode != 0:
                    print_error(f"Falha na instalação: {result.stderr}")
                    return False
                
                print_success("Dependências instaladas")
            else:
                print_info("Todas as dependências já estão instaladas")
            
            return True
            
        except Exception as e:
            print_error(f"Erro na instalação de dependências: {e}")
            return False
    
    def _setup_new_modules(self) -> bool:
        """Configura novos módulos da Fase 2"""
        try:
            print_info("Configurando novos módulos...")
            
            # Criar arquivo de configuração das métricas
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
                        "leverage": 0.05,  # Menor peso para bancos
                        "profitability": 0.35  # Maior peso
                    },
                    "Tecnologia": {
                        "growth": 0.30,  # Maior peso para crescimento
                        "valuation": 0.15  # Menor peso para valuation
                    }
                },
                "outlier_thresholds": {
                    "pe_ratio": {"min": 0, "max": 100},
                    "pb_ratio": {"min": 0, "max": 20},
                    "roe": {"min": -50, "max": 100},
                    "debt_to_equity": {"min": 0, "max": 10}
                }
            }
            
            config_path = self.project_root / 'config' / 'metrics_config.json'
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(metrics_config, f, indent=2, ensure_ascii=False)
            
            print_success("Configuração de métricas criada")
            
            # Atualizar configurações principais
            settings_path = self.project_root / 'config' / 'settings.py'
            if settings_path.exists():
                # Adicionar configurações da Fase 2 ao arquivo de configuração
                phase2_config = '''

# ==================== FASE 2 - ANÁLISE FUNDAMENTALISTA ====================
# Configurações para análise fundamentalista expandida

class Phase2Settings:
    """Configurações específicas da Fase 2"""
    
    def __init__(self):
        # Sistema de Métricas
        self.metrics_config_file = "config/metrics_config.json"
        self.enable_sector_benchmarks = True
        self.benchmark_update_frequency = "weekly"  # daily, weekly, monthly
        
        # Análise Fundamentalista
        self.min_data_completeness = 0.6  # 60% dos dados necessários
        self.confidence_threshold = 0.7   # Confiança mínima para análise
        self.historical_periods = 5       # Número de períodos históricos
        
        # Performance
        self.enable_parallel_analysis = True
        self.max_concurrent_analyses = 10
        self.analysis_timeout_seconds = 300
        
        # Cache
        self.cache_analysis_results = True
        self.analysis_cache_ttl_hours = 24
        self.benchmark_cache_ttl_hours = 168  # 7 dias
        
        # Relatórios
        self.generate_analysis_reports = True
        self.reports_directory = "data/reports"
        self.report_formats = ["json", "excel"]

# Instância global para Fase 2
phase2_settings = Phase2Settings()

def get_phase2_settings() -> Phase2Settings:
    """Retorna configurações da Fase 2"""
    return phase2_settings
'''
                
                # Ler arquivo atual
                current_content = settings_path.read_text(encoding='utf-8')
                
                # Verificar se já tem configurações da Fase 2
                if "FASE 2" not in current_content:
                    # Adicionar no final do arquivo
                    updated_content = current_content + phase2_config
                    settings_path.write_text(updated_content, encoding='utf-8')
                    print_success("Configurações da Fase 2 adicionadas")
                else:
                    print_info("Configurações da Fase 2 já existem")
            
            return True
            
        except Exception as e:
            print_error(f"Erro na configuração de módulos: {e}")
            return False
    
    def _migrate_database(self) -> bool:
        """Executa migração do banco de dados"""
        try:
            print_info("Executando migração do banco de dados...")
            
            # Verificar se banco existe
            from config.settings import get_settings
            settings = get_settings()
            
            if settings.database_path and not settings.database_path.exists():
                print_error("Banco da Fase 1 não encontrado. Execute setup da Fase 1 primeiro.")
                return False
            
            # Importar modelos expandidos
            sys.path.insert(0, str(self.project_root))
            
            try:
                from database.models import create_expanded_tables
                from database.connection import engine
                
                # Criar novas tabelas
                success = create_expanded_tables(engine)
                if success:
                    print_success("Tabelas expandidas criadas")
                else:
                    print_error("Falha ao criar tabelas expandidas")
                    return False
                
            except ImportError as e:
                print_error(f"Erro ao importar modelos expandidos: {e}")
                return False
            
            # Criar script de migração
            migration_script = '''
# database/migrations/001_expand_tables_phase2.py
"""
Migração 001: Expansão de tabelas para Fase 2
"""
from sqlalchemy import text
from database.connection import engine, get_db_session
from database.models import create_expanded_tables
import logging

logger = logging.getLogger(__name__)

def upgrade():
    """Executa upgrade da migração"""
    try:
        # Criar novas tabelas
        create_expanded_tables(engine)
        
        # Executar comandos SQL específicos se necessário
        with get_db_session() as session:
            # Exemplo: índices adicionais, triggers, etc.
            pass
        
        logger.info("Migração 001 executada com sucesso")
        return True
        
    except Exception as e:
        logger.error(f"Erro na migração 001: {e}")
        return False

def downgrade():
    """Executa downgrade da migração"""
    try:
        # Remover tabelas criadas (se necessário)
        with engine.connect() as conn:
            conn.execute(text("DROP TABLE IF EXISTS financial_statements"))
            conn.execute(text("DROP TABLE IF EXISTS fundamental_analyses_expanded"))
            conn.execute(text("DROP TABLE IF EXISTS sector_benchmarks"))
            conn.execute(text("DROP TABLE IF EXISTS analysis_audit_log"))
            conn.execute(text("DROP TABLE IF EXISTS metric_definitions"))
            conn.execute(text("DROP TABLE IF EXISTS stocks_expanded"))
            conn.commit()
        
        logger.info("Downgrade 001 executado com sucesso")
        return True
        
    except Exception as e:
        logger.error(f"Erro no downgrade 001: {e}")
        return False
'''
            
            migration_path = self.project_root / 'database' / 'migrations' / '001_expand_tables_phase2.py'
            migration_path.write_text(migration_script, encoding='utf-8')
            
            print_success("Script de migração criado")
            return True
            
        except Exception as e:
            print_error(f"Erro na migração: {e}")
            return False
    
    def _setup_metrics_system(self) -> bool:
        """Configura sistema de métricas"""
        try:
            print_info("Configurando sistema de métricas...")
            
            # Criar dados de exemplo para métricas
            from utils.financial_calculator import FinancialCalculator, FinancialData
            
            # Testar calculadora
            sample_data = FinancialData(
                market_cap=100000000000,
                current_price=20.0,
                revenue=50000000000,
                net_income=6000000000,
                total_assets=80000000000,
                total_equity=40000000000
            )
            
            calculator = FinancialCalculator()
            metrics = calculator.calculate_all_metrics(sample_data)
            
            if metrics.data_completeness > 0:
                print_success("Calculadora de métricas funcionando")
            else:
                print_warning("Calculadora com problemas")
            
            # Criar definições de métricas básicas
            metrics_definitions = [
                {
                    "name": "pe_ratio",
                    "category": "valuation",
                    "description": "Price to Earnings Ratio",
                    "formula": "Market Cap / Net Income",
                    "better_when_higher": False,
                    "weight": 1.0
                },
                {
                    "name": "roe",
                    "category": "profitability", 
                    "description": "Return on Equity",
                    "formula": "(Net Income / Total Equity) * 100",
                    "better_when_higher": True,
                    "weight": 1.5
                },
                {
                    "name": "debt_to_equity",
                    "category": "leverage",
                    "description": "Debt to Equity Ratio",
                    "formula": "Total Debt / Total Equity",
                    "better_when_higher": False,
                    "weight": 1.0
                }
            ]
            
            # Salvar definições
            definitions_path = self.project_root / 'data' / 'metric_definitions.json'
            with open(definitions_path, 'w', encoding='utf-8') as f:
                json.dump(metrics_definitions, f, indent=2, ensure_ascii=False)
            
            print_success("Sistema de métricas configurado")
            return True
            
        except Exception as e:
            print_error(f"Erro na configuração de métricas: {e}")
            return False
    
    def _run_basic_tests(self) -> bool:
        """Executa testes básicos dos novos componentes"""
        try:
            print_info("Executando testes básicos...")
            
            test_results = []
            
            # Teste 1: Importação de módulos
            try:
                from utils.financial_calculator import FinancialCalculator
                from agents.collectors.enhanced_yfinance_client import EnhancedYFinanceClient
                test_results.append(("Importação de módulos", True, None))
            except ImportError as e:
                test_results.append(("Importação de módulos", False, str(e)))
            
            # Teste 2: Calculadora de métricas
            try:
                from utils.financial_calculator import FinancialData, FinancialCalculator
                
                test_data = FinancialData(
                    market_cap=1000000000,
                    current_price=10.0,
                    revenue=5000000000,
                    net_income=500000000
                )
                
                calc = FinancialCalculator()
                metrics = calc.calculate_all_metrics(test_data)
                
                success = metrics.pe_ratio is not None and metrics.pe_ratio > 0
                test_results.append(("Calculadora de métricas", success, None))
                
            except Exception as e:
                test_results.append(("Calculadora de métricas", False, str(e)))
            
            # Teste 3: Modelos expandidos
            try:
                from database.models import StockExpanded, DataQuality
                
                # Criar instância de teste
                test_stock = StockExpanded(
                    codigo="TEST",
                    nome="Teste",
                    setor="Teste",
                    data_quality=DataQuality.HIGH
                )
                
                success = test_stock.codigo == "TEST"
                test_results.append(("Modelos expandidos", success, None))
                
            except Exception as e:
                test_results.append(("Modelos expandidos", False, str(e)))
            
            # Teste 4: Configurações
            try:
                config_path = self.project_root / 'config' / 'metrics_config.json'
                if config_path.exists():
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                    
                    success = "scoring_weights" in config
                    test_results.append(("Configurações", success, None))
                else:
                    test_results.append(("Configurações", False, "Arquivo não encontrado"))
                    
            except Exception as e:
                test_results.append(("Configurações", False, str(e)))
            
            # Resumo dos testes
            passed = sum(1 for _, success, _ in test_results if success)
            total = len(test_results)
            
            print_info(f"Resultados dos testes: {passed}/{total}")
            
            for test_name, success, error in test_results:
                if success:
                    print_success(f"  ✅ {test_name}")
                else:
                    print_error(f"  ❌ {test_name}: {error}")
            
            return passed == total
            
        except Exception as e:
            print_error(f"Erro nos testes: {e}")
            return False
    
    def _generate_setup_report(self) -> bool:
        """Gera relatório final do setup"""
        try:
            print_info("Gerando relatório de setup...")
            
            report = {
                "setup_info": {
                    "phase": "Fase 2 - Passo 1",
                    "description": "Expansão do Sistema de Métricas",
                    "date": datetime.now().isoformat(),
                    "success_count": self.success_count,
                    "error_count": self.error_count,
                    "total_tasks": self.success_count + self.error_count
                },
                "components_installed": [
                    "utils/financial_calculator.py",
                    "agents/collectors/enhanced_yfinance_client.py", 
                    "database/models_expanded.py",
                    "config/metrics_config.json"
                ],
                "new_dependencies": [
                    "scipy", "scikit-learn", "matplotlib", 
                    "seaborn", "plotly", "openpyxl"
                ],
                "database_changes": [
                    "Tabelas expandidas criadas",
                    "Novos índices adicionados",
                    "Script de migração gerado"
                ],
                "next_steps": [
                    "Implementar Agente Analisador Fundamentalista",
                    "Configurar sistema de scoring",
                    "Executar primeira análise fundamentalista completa",
                    "Configurar benchmarks setoriais"
                ],
                "task_log": self.setup_log
            }
            
            # Salvar relatório
            report_path = self.project_root / f"setup_report_phase2_step1_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            print_success(f"Relatório salvo: {report_path.name}")
            
            # Gerar README da Fase 2
            readme_content = f'''# Fase 2 - Passo 1: Sistema de Métricas Expandido

## ✅ Componentes Implementados

### 1. Calculadora Financeira (`utils/financial_calculator.py`)
- Cálculo de 25+ métricas fundamentalistas
- Suporte a dados históricos para crescimento
- Validação automática de dados
- Benchmarks setoriais

### 2. Cliente YFinance Expandido (`agents/collectors/enhanced_yfinance_client.py`)
- Coleta de demonstrações financeiras
- Dados históricos de 5 anos
- Cache inteligente
- Processamento em lote

### 3. Modelos de Dados Expandidos (`database/models_expanded.py`)
- Tabela `stocks_expanded` com 50+ campos
- Tabela `financial_statements` para dados históricos
- Tabela `fundamental_analyses_expanded` para análises
- Sistema de auditoria e benchmarks

### 4. Sistema de Configuração
- Arquivo `metrics_config.json` com pesos das métricas
- Configurações por setor
- Thresholds para outliers

## 🚀 Próximos Passos

1. **Implementar Agente Analisador** (Passo 2)
2. **Sistema de Scoring** (Passo 2) 
3. **Benchmarks Setoriais** (Passo 3)
4. **APIs de Análise** (Passo 4)

## 📊 Status do Setup

- ✅ Sucesso: {self.success_count} tarefas
- ❌ Falhas: {self.error_count} tarefas
- 📅 Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}

## 🔧 Como Usar

```python
# Exemplo de uso da calculadora
from utils.financial_calculator import FinancialCalculator, FinancialData

# Criar dados financeiros
data = FinancialData(
    market_cap=100000000000,
    revenue=50000000000,
    net_income=6000000000
)

# Calcular métricas
calc = FinancialCalculator()
metrics = calc.calculate_all_metrics(data)

print(f"P/L: {{metrics.pe_ratio:.2f}}")
print(f"ROE: {{metrics.roe:.2f}}%")
```

## 📚 Documentação

- [Calculadora Financeira](docs/phase2/financial_calculator.md)
- [Cliente YFinance](docs/phase2/yfinance_client.md) 
- [Modelos de Dados](docs/phase2/data_models.md)
'''
            
            readme_path = self.project_root / 'README_PHASE2_STEP1.md'
            readme_path.write_text(readme_content, encoding='utf-8')
            
            return True
            
        except Exception as e:
            print_error(f"Erro ao gerar relatório: {e}")
            return False
    
    def _log_task(self, task_name: str, success: bool, error: str = None):
        """Registra resultado de uma tarefa"""
        self.setup_log.append({
            "task": task_name,
            "success": success,
            "error": error,
            "timestamp": datetime.now().isoformat()
        })
    
    def _print_final_summary(self):
        """Imprime resumo final"""
        print_header("RESUMO DO SETUP", Colors.WHITE)
        
        total_tasks = self.success_count + self.error_count
        success_rate = (self.success_count / total_tasks * 100) if total_tasks > 0 else 0
        
        print(f"\n{Colors.WHITE}📊 ESTATÍSTICAS:{Colors.NC}")
        print(f"   Total de tarefas: {total_tasks}")
        print(f"   Tarefas concluídas: {Colors.GREEN}{self.success_count}{Colors.NC}")
        print(f"   Tarefas falharam: {Colors.RED}{self.error_count}{Colors.NC}")
        print(f"   Taxa de sucesso: {success_rate:.1f}%")
        
        if self.error_count == 0:
            print(f"\n{Colors.GREEN}🎉 SETUP CONCLUÍDO COM SUCESSO!{Colors.NC}")
            print(f"{Colors.GREEN}✅ Fase 2 - Passo 1 implementado corretamente{Colors.NC}")
            print(f"\n{Colors.CYAN}🚀 PRÓXIMOS PASSOS:{Colors.NC}")
            print("   1. Implementar Agente Analisador Fundamentalista")
            print("   2. Configurar Sistema de Scoring")
            print("   3. Executar primeira análise completa")
            print("   4. Validar métricas calculadas")
        else:
            print(f"\n{Colors.YELLOW}⚠️  SETUP CONCLUÍDO COM PROBLEMAS{Colors.NC}")
            print(f"{Colors.YELLOW}🔧 Corrija os problemas antes de prosseguir{Colors.NC}")
            print(f"\n{Colors.CYAN}📋 AÇÕES RECOMENDADAS:{Colors.NC}")
            print("   1. Verificar logs de erro detalhados")
            print("   2. Corrigir problemas identificados")
            print("   3. Executar setup novamente")
            print("   4. Consultar documentação se necessário")


def main():
    """Função principal"""
    try:
        setup = Phase2Step1Setup()
        success = setup.run_full_setup()
        
        if success:
            print(f"\n{Colors.GREEN}✅ Setup da Fase 2 Passo 1 concluído com sucesso!{Colors.NC}")
            return True
        else:
            print(f"\n{Colors.RED}❌ Setup falhou. Verifique os erros acima.{Colors.NC}")
            return False
            
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️  Setup interrompido pelo usuário{Colors.NC}")
        return False
    except Exception as e:
        print(f"\n{Colors.RED}❌ Erro crítico no setup: {e}{Colors.NC}")
        return False


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
