# scripts/validate_phase1.py
"""
Script de Validação Completa da Fase 1
Sistema de Recomendações de Investimentos

Este script executa todos os testes necessários para validar:
- Configurações do sistema
- Banco de dados e modelos
- Agente Coletor
- Integrações (YFinance, MCP)
- Performance e integridade
"""
import sys
import json
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

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
    NC = '\033[0m'  # No Color


def print_header(text: str, color: str = Colors.BLUE):
    """Imprime cabeçalho colorido"""
    print(f"\n{color}{'='*60}{Colors.NC}")
    print(f"{color}{text.center(60)}{Colors.NC}")
    print(f"{color}{'='*60}{Colors.NC}")


def print_step(text: str):
    """Imprime passo do teste"""
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


class ValidationResults:
    """Classe para armazenar resultados da validação"""

    def __init__(self):
        self.tests: List[Dict[str, Any]] = []
        self.start_time = datetime.now()
        self.end_time = None

    def add_test(self, test_name: str, passed: bool, 
                 details: Dict[str, Any] = None, error: str = None):
        """Adiciona resultado de um teste"""
        self.tests.append({
            "name": test_name,
            "passed": passed,
            "details": details or {},
            "error": error,
            "timestamp": datetime.now()
        })

    def finish(self):
        """Finaliza a validação"""
        self.end_time = datetime.now()

    def get_summary(self) -> Dict[str, Any]:
        """Retorna resumo dos resultados"""
        passed = sum(1 for t in self.tests if t["passed"])
        failed = len(self.tests) - passed

        return {
            "total_tests": len(self.tests),
            "passed": passed,
            "failed": failed,
            "success_rate": round((passed / len(self.tests)) * 100, 1) if self.tests else 0,
            "duration": (self.end_time - self.start_time).total_seconds() if self.end_time else 0,
            "status": "PASS" if failed == 0 else "FAIL"
        }

    def save_report(self, filepath: str = None):
        """Salva relatório detalhado"""
        if not filepath:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"validation_report_{timestamp}.json"

        report = {
            "summary": self.get_summary(),
            "tests": self.tests,
            "generated_at": datetime.now().isoformat()
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        
        return filepath


class Phase1Validator:
    """Validador principal da Fase 1"""

    def __init__(self):
        self.results = ValidationResults()
        sys.path.insert(0, '.')

    async def run_all_validations(self) -> ValidationResults:
        """Executa todas as validações da Fase 1"""
        print_header("VALIDAÇÃO COMPLETA DA FASE 1", Colors.PURPLE)
        print_info("Sistema de Recomendações de Investimentos")
        print_info(f"Iniciado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

        # Lista de validações a executar
        validations = [
            ("Ambiente e Dependências", self._validate_environment),
            ("Configurações", self._validate_configuration),
            ("Banco de Dados", self._validate_database),
            ("Modelos de Dados", self._validate_models),
            ("Repositories", self._validate_repositories),
            ("Agente Coletor", self._validate_stock_collector),
            ("Integração YFinance", self._validate_yfinance),
            ("Performance", self._validate_performance),
            ("Integridade de Dados", self._validate_data_integrity),
            ("Logs e Monitoramento", self._validate_logging)
        ]

        for test_name, test_func in validations:
            print_step(f"Executando: {test_name}")

            try:
                start_time = time.time()
                result = await test_func()
                duration = time.time() - start_time

                if result.get("passed", False):
                    print_success(f"{test_name} - PASSOU ({duration:.2f}s)")
                    self.results.add_test(test_name, True, result.get("details"), None)
                else:
                    print_error(f"{test_name} - FALHOU ({duration:.2f}s)")
                    print_error(f"   Erro: {result.get('error', 'Erro desconhecido')}")
                    self.results.add_test(test_name, False, result.get("details"), result.get("error"))

            except Exception as e:
                print_error(f"{test_name} - EXCEÇÃO: {str(e)}")
                self.results.add_test(test_name, False, {}, str(e))

        self.results.finish()
        self._print_final_summary()

        return self.results

    async def _validate_environment(self) -> Dict[str, Any]:
        """Valida ambiente Python e dependências"""
        try:
            details = {}

            # Python version
            import sys
            python_version = sys.version_info
            details["python_version"] = f"{python_version.major}.{python_version.minor}.{python_version.micro}"

            if python_version < (3, 11):
                return {"passed": False, "error": "Python 3.11+ é necessário", "details": details}

            # Dependências críticas
            critical_deps = [
                "agno", "fastapi", "sqlalchemy", "pydantic", 
                "yfinance", "pandas", "httpx"
            ]

            missing_deps = []
            for dep in critical_deps:
                try:
                    __import__(dep)
                except ImportError:
                    missing_deps.append(dep)

            details["missing_dependencies"] = missing_deps

            if missing_deps:
                return {
                    "passed": False, 
                    "error": f"Dependências faltando: {', '.join(missing_deps)}", 
                    "details": details
                }

            # Verificar estrutura de diretórios
            required_dirs = ["agents", "database", "config", "api", "data", "logs"]
            missing_dirs = [d for d in required_dirs if not Path(d).exists()]
            details["missing_directories"] = missing_dirs

            if missing_dirs:
                return {
                    "passed": False,
                    "error": f"Diretórios faltando: {', '.join(missing_dirs)}",
                    "details": details
                }

            details["status"] = "Ambiente configurado corretamente"
            return {"passed": True, "details": details}

        except Exception as e:
            return {"passed": False, "error": str(e)}

    async def _validate_configuration(self) -> Dict[str, Any]:
        """Valida configurações do sistema"""
        try:
            from config.settings import get_settings, get_agent_settings

            settings = get_settings()
            agent_settings = get_agent_settings()

            details = {}
            issues = []

            # Verificar configurações críticas
            if settings.anthropic_api_key == "your_claude_api_key_here":
                issues.append("Chave da API do Claude não configurada")

            if not settings.database_url:
                issues.append("URL do banco de dados não configurada")

            # Verificar arquivo .env
            env_file = Path(".env")
            if not env_file.exists():
                issues.append("Arquivo .env não encontrado")

            details.update({
                "environment": settings.environment,
                "database_url": settings.database_url,
                "api_port": settings.api_port,
                "has_claude_key": settings.anthropic_api_key != "your_claude_api_key_here",
                "agent_batch_size": agent_settings.collector_batch_size,
                "issues": issues
            })

            if issues:
                return {
                    "passed": False,
                    "error": f"Problemas de configuração: {'; '.join(issues)}",
                    "details": details
                }

            return {"passed": True, "details": details}

        except Exception as e:
            return {"passed": False, "error": str(e)}

    async def _validate_database(self) -> Dict[str, Any]:
        """Valida banco de dados"""
        try:
            from database.connection import (
                check_database_connection, get_database_info, 
                create_tables
            )

            details = {}

            # Verificar conexão
            if not check_database_connection():
                return {"passed": False, "error": "Falha na conexão com banco de dados"}

            # Informações do banco
            db_info = get_database_info()
            details.update(db_info)

            # Verificar tabelas essenciais
            expected_tables = ["stocks", "recommendations", "fundamental_analyses", 
                             "agent_sessions", "market_data"]
            missing_tables = [t for t in expected_tables if t not in db_info.get("tables", [])]

            if missing_tables:
                # Tentar criar tabelas
                if create_tables():
                    details["created_missing_tables"] = missing_tables
                else:
                    return {
                        "passed": False,
                        "error": f"Tabelas faltando e não foi possível criar: {missing_tables}",
                        "details": details
                    }

            # Verificar se há dados de exemplo
            from database.repositories import get_stock_repository
            stock_repo = get_stock_repository()
            stocks = stock_repo.get_all_stocks()
            details["total_stocks"] = len(stocks)

            if len(stocks) == 0:
                # Tentar popular dados de exemplo
                try:
                    from database.init_db import populate_sample_data
                    created = populate_sample_data()
                    details["created_sample_stocks"] = created
                except Exception as e:
                    details["sample_data_error"] = str(e)

            return {"passed": True, "details": details}

        except Exception as e:
            return {"passed": False, "error": str(e)}

    async def _validate_models(self) -> Dict[str, Any]:
        """Valida modelos de dados"""
        try:
            from database.models import Stock, Recommendation, FundamentalAnalysis, AgentSession, MarketData
            from sqlalchemy import inspect
            from database.connection import engine

            details = {}

            # Verificar se todos os modelos têm tabelas correspondentes
            inspector = inspect(engine)
            table_names = inspector.get_table_names()

            model_tables = {
                "Stock": "stocks",
                "Recommendation": "recommendations", 
                "FundamentalAnalysis": "fundamental_analyses",
                "AgentSession": "agent_sessions",
                "MarketData": "market_data"
            }

            missing_tables = []
            for model, table in model_tables.items():
                if table not in table_names:
                    missing_tables.append(f"{model} -> {table}")

            details["model_tables"] = model_tables
            details["missing_tables"] = missing_tables

            if missing_tables:
                return {
                    "passed": False,
                    "error": f"Tabelas de modelos faltando: {missing_tables}",
                    "details": details
                }

            # Testar criação de instâncias
            test_stock = Stock(
                codigo="TEST", nome="Teste", setor="Teste", 
                preco_atual=10.0, volume_medio=1000, ativo=True
            )
            details["models_instantiable"] = True

            return {"passed": True, "details": details}
            
        except Exception as e:
            return {"passed": False, "error": str(e)}

    async def _validate_repositories(self) -> Dict[str, Any]:
        """Valida repositories de acesso aos dados"""
        try:
            from database.repositories import (
                get_stock_repository, get_recommendation_repository,
                get_agent_session_repository, get_fundamental_repository
            )

            details = {}

            # Testar stock repository
            stock_repo = get_stock_repository()
            stocks = stock_repo.get_all_stocks()
            details["stock_repo_count"] = len(stocks)

            if len(stocks) > 0:
                # Testar busca por código
                first_stock = stocks[0]
                found_stock = stock_repo.get_stock_by_code(first_stock.codigo)
                if not found_stock:
                    return {"passed": False, "error": "Falha na busca por código de ação"}

                # Testar atualização de preço
                original_price = found_stock.preco_atual
                test_price = original_price + 1.0
                if stock_repo.update_stock_price(first_stock.codigo, test_price):
                    # Reverter para preço original
                    stock_repo.update_stock_price(first_stock.codigo, original_price)
                    details["price_update_works"] = True
                else:
                    return {"passed": False, "error": "Falha na atualização de preço"}

            # Testar recommendation repository
            rec_repo = get_recommendation_repository()
            recommendations = rec_repo.get_latest_recommendations(limit=5)
            details["recommendation_repo_count"] = len(recommendations)
            
            # Testar agent session repository
            session_repo = get_agent_session_repository()
            sessions = session_repo.get_recent_sessions(limit=5)
            details["session_repo_count"] = len(sessions)
            
            # Testar estatísticas
            try:
                stats = rec_repo.get_recommendation_statistics()
                details["recommendation_stats"] = stats
            except Exception as e:
                details["stats_error"] = str(e)
            
            return {"passed": True, "details": details}
            
        except Exception as e:
            return {"passed": False, "error": str(e)}
    
    async def _validate_stock_collector(self) -> Dict[str, Any]:
        """Valida o agente coletor de ações"""
        try:
            details = {}
            
            # Verificar se Agno está disponível
            try:
                from agno import Agent
                details["agno_available"] = True
            except ImportError:
                details["agno_available"] = False
                return {
                    "passed": False,
                    "error": "Agno Framework não está instalado",
                    "details": details
                }
            
            # Importar agente coletor
            try:
                from agents.collectors.stock_collector import StockCollectorAgent
                details["collector_importable"] = True
            except ImportError as e:
                return {
                    "passed": False,
                    "error": f"Falha ao importar StockCollectorAgent: {e}",
                    "details": details
                }
            
            # Criar instância do agente
            collector = StockCollectorAgent()
            details["collector_instantiable"] = True
            details["agent_name"] = collector.name
            details["agent_version"] = collector.version
            details["tools_count"] = len(collector.tools)
            
            # Verificar tools
            tool_names = [tool.name for tool in collector.tools]
            expected_tools = ["collect_stock_data", "update_stock_price", "collect_all_active_stocks"]
            missing_tools = [t for t in expected_tools if t not in tool_names]
            
            details["available_tools"] = tool_names
            details["missing_tools"] = missing_tools
            
            if missing_tools:
                return {
                    "passed": False,
                    "error": f"Tools faltando: {missing_tools}",
                    "details": details
                }
            
            # Testar cliente YFinance
            try:
                from agents.collectors.stock_collector import YFinanceClient
                yf_client = YFinanceClient()
                details["yfinance_client_available"] = True
            except Exception as e:
                return {
                    "passed": False,
                    "error": f"Falha no cliente YFinance: {e}",
                    "details": details
                }
            
            return {"passed": True, "details": details}
            
        except Exception as e:
            return {"passed": False, "error": str(e)}
    
    async def _validate_yfinance(self) -> Dict[str, Any]:
        """Valida integração com YFinance"""
        try:
            details = {}
            
            # Testar importação do yfinance
            try:
                import yfinance as yf
                details["yfinance_installed"] = True
            except ImportError:
                return {
                    "passed": False,
                    "error": "YFinance não está instalado",
                    "details": details
                }
            
            # Testar coleta de dados de uma ação
            test_symbols = ["PETR4.SA", "VALE3.SA"]
            successful_tests = 0
            
            for symbol in test_symbols:
                try:
                    ticker = yf.Ticker(symbol)
                    info = ticker.info
                    
                    if info and info.get('regularMarketPrice'):
                        successful_tests += 1
                        details[f"{symbol}_price"] = info.get('regularMarketPrice')
                        details[f"{symbol}_name"] = info.get('shortName')
                    
                except Exception as e:
                    details[f"{symbol}_error"] = str(e)
            
            details["successful_requests"] = successful_tests
            details["total_requests"] = len(test_symbols)
            
            if successful_tests == 0:
                return {
                    "passed": False,
                    "error": "Falha em todas as requisições YFinance",
                    "details": details
                }
            
            # Testar via agente coletor
            try:
                from agents.collectors.stock_collector import YFinanceClient
                yf_client = YFinanceClient()
                
                test_data = await yf_client.get_stock_info("PETR4")
                if test_data and test_data.get('regularMarketPrice'):
                    details["agent_client_works"] = True
                    details["agent_test_price"] = test_data.get('regularMarketPrice')
                else:
                    details["agent_client_works"] = False
                    
            except Exception as e:
                details["agent_client_error"] = str(e)
            
            return {"passed": True, "details": details}
            
        except Exception as e:
            return {"passed": False, "error": str(e)}
    
    async def _validate_performance(self) -> Dict[str, Any]:
        """Valida performance do sistema"""
        try:
            details = {}
            
            # Teste de velocidade do banco
            start_time = time.time()
            from database.repositories import get_stock_repository
            stock_repo = get_stock_repository()
            stocks = stock_repo.get_all_stocks()
            db_time = time.time() - start_time
            
            details["db_query_time"] = round(db_time, 3)
            details["stocks_queried"] = len(stocks)
            
            # Teste de velocidade do agente (se disponível)
            try:
                from agents.collectors.stock_collector import StockCollectorAgent
                
                start_time = time.time()
                collector = StockCollectorAgent()
                agent_init_time = time.time() - start_time
                
                details["agent_init_time"] = round(agent_init_time, 3)
                
                # Testar uma coleta simples
                if len(stocks) > 0:
                    test_codigo = stocks[0].codigo
                    start_time = time.time()
                    
                    # Usar tool de atualização de preço
                    update_tool = None
                    for tool in collector.tools:
                        if tool.name == "update_stock_price":
                            update_tool = tool
                            break
                    
                    if update_tool:
                        result = await update_tool(test_codigo)
                        collection_time = time.time() - start_time
                        
                        details["single_collection_time"] = round(collection_time, 3)
                        details["collection_success"] = result.get("success", False)
                        
            except Exception as e:
                details["agent_performance_error"] = str(e)
            
            # Verificar thresholds de performance
            issues = []
            if details.get("db_query_time", 0) > 1.0:
                issues.append("Query do banco muito lenta (>1s)")
            
            if details.get("agent_init_time", 0) > 5.0:
                issues.append("Inicialização do agente muito lenta (>5s)")
            
            if details.get("single_collection_time", 0) > 10.0:
                issues.append("Coleta individual muito lenta (>10s)")
            
            details["performance_issues"] = issues
            
            if issues:
                return {
                    "passed": False,
                    "error": f"Problemas de performance: {'; '.join(issues)}",
                    "details": details
                }
            
            return {"passed": True, "details": details}
            
        except Exception as e:
            return {"passed": False, "error": str(e)}
    
    async def _validate_data_integrity(self) -> Dict[str, Any]:
        """Valida integridade dos dados"""
        try:
            from database.repositories import get_stock_repository
            from database.connection import get_db_session
            from sqlalchemy import func
            from database.models import Stock
            
            details = {}
            issues = []
            
            stock_repo = get_stock_repository()
            
            # Verificar dados básicos das ações
            stocks = stock_repo.get_all_stocks()
            details["total_stocks"] = len(stocks)
            
            if len(stocks) == 0:
                return {
                    "passed": False,
                    "error": "Nenhuma ação encontrada no banco",
                    "details": details
                }
            
            # Verificar ações com dados inválidos
            invalid_stocks = []
            for stock in stocks:
                stock_issues = []
                
                if not stock.codigo:
                    stock_issues.append("código vazio")
                if not stock.nome:
                    stock_issues.append("nome vazio")
                if stock.preco_atual and stock.preco_atual <= 0:
                    stock_issues.append("preço inválido")
                if stock.volume_medio and stock.volume_medio < 0:
                    stock_issues.append("volume negativo")
                
                if stock_issues:
                    invalid_stocks.append({
                        "codigo": stock.codigo,
                        "issues": stock_issues
                    })
            
            details["invalid_stocks"] = invalid_stocks
            details["invalid_count"] = len(invalid_stocks)
            
            # Verificar duplicatas
            with get_db_session() as db:
                duplicates = db.query(
                    Stock.codigo,
                    func.count(Stock.id).label('count')
                ).group_by(Stock.codigo).having(func.count(Stock.id) > 1).all()
                
                duplicate_codes = [codigo for codigo, count in duplicates]
                details["duplicate_codes"] = duplicate_codes
                details["duplicate_count"] = len(duplicate_codes)
            
            # Verificar consistência de preços
            recent_prices = [s for s in stocks if s.preco_atual and s.preco_atual > 0]
            if recent_prices:
                prices = [s.preco_atual for s in recent_prices]
                details["price_stats"] = {
                    "min": min(prices),
                    "max": max(prices),
                    "avg": sum(prices) / len(prices),
                    "count": len(prices)
                }
                
                # Verificar preços extremos (possíveis erros)
                extreme_prices = [s for s in recent_prices if s.preco_atual > 1000 or s.preco_atual < 0.01]
                details["extreme_prices"] = [{"codigo": s.codigo, "preco": s.preco_atual} for s in extreme_prices]
            
            # Resumir problemas
            if invalid_stocks:
                issues.append(f"{len(invalid_stocks)} ações com dados inválidos")
            if duplicate_codes:
                issues.append(f"{len(duplicate_codes)} códigos duplicados")
            if details.get("extreme_prices"):
                issues.append(f"{len(details['extreme_prices'])} preços extremos")
            
            details["integrity_issues"] = issues
            
            if issues:
                return {
                    "passed": False,
                    "error": f"Problemas de integridade: {'; '.join(issues)}",
                    "details": details
                }
            
            return {"passed": True, "details": details}
            
        except Exception as e:
            return {"passed": False, "error": str(e)}
    
    async def _validate_logging(self) -> Dict[str, Any]:
        """Valida sistema de logs"""
        try:
            from config.settings import get_settings
            
            settings = get_settings()
            details = {}
            
            # Verificar diretório de logs
            logs_dir = settings.logs_dir
            details["logs_dir"] = str(logs_dir)
            details["logs_dir_exists"] = logs_dir.exists()
            
            if not logs_dir.exists():
                logs_dir.mkdir(parents=True, exist_ok=True)
                details["created_logs_dir"] = True
            
            # Verificar arquivo de log principal
            log_file = logs_dir / "investment_system.log"
            details["main_log_file"] = str(log_file)
            details["main_log_exists"] = log_file.exists()
            
            if log_file.exists():
                details["log_file_size"] = log_file.stat().st_size
                
                # Ler últimas linhas para verificar formato
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        details["log_lines_count"] = len(lines)
                        if lines:
                            details["last_log_entry"] = lines[-1].strip()
                except Exception as e:
                    details["log_read_error"] = str(e)
            
            # Testar escrita de log
            test_logger = logging.getLogger("test_validation")
            test_message = f"Teste de validação - {datetime.now().isoformat()}"
            test_logger.info(test_message)
            details["test_log_written"] = True
            
            # Verificar logs de agentes
            agent_log_file = logs_dir / "agents.log"
            details["agent_log_exists"] = agent_log_file.exists()
            
            return {"passed": True, "details": details}
            
        except Exception as e:
            return {"passed": False, "error": str(e)}
    
    def _print_final_summary(self):
        """Imprime resumo final da validação"""
        summary = self.results.get_summary()
        
        print_header("RESUMO DA VALIDAÇÃO", Colors.WHITE)
        
        print(f"\n{Colors.WHITE}📊 ESTATÍSTICAS:{Colors.NC}")
        print(f"   Total de testes: {summary['total_tests']}")
        print(f"   Testes aprovados: {Colors.GREEN}{summary['passed']}{Colors.NC}")
        print(f"   Testes falharam: {Colors.RED}{summary['failed']}{Colors.NC}")
        print(f"   Taxa de sucesso: {summary['success_rate']}%")
        print(f"   Duração total: {summary['duration']:.2f}s")
        
        print(f"\n{Colors.WHITE}📋 STATUS POR CATEGORIA:{Colors.NC}")
        for test in self.results.tests:
            status_color = Colors.GREEN if test["passed"] else Colors.RED
            status_icon = "✅" if test["passed"] else "❌"
            print(f"   {status_icon} {test['name']}: {status_color}{'PASS' if test['passed'] else 'FAIL'}{Colors.NC}")
            
            if not test["passed"] and test["error"]:
                print(f"      {Colors.RED}└─ {test['error']}{Colors.NC}")
        
        # Status final da Fase 1
        print_header
