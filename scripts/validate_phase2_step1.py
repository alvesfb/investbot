# scripts/validate_phase2_step1.py
"""
Script de Validação Completa da Fase 2 - Passo 1
Valida toda a implementação do sistema de métricas expandido
"""
import asyncio
import sys
import json
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cores para output
class Colors:
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    RED = '\033[0;31m'
    CYAN = '\033[0;36m'
    WHITE = '\033[1;37m'
    NC = '\033[0m'


def print_header(text: str, color: str = Colors.BLUE):
    print(f"\n{color}{'='*60}{Colors.NC}")
    print(f"{color}{text.center(60)}{Colors.NC}")
    print(f"{color}{'='*60}{Colors.NC}")


def print_step(text: str):
    print(f"\n{Colors.CYAN}📋 {text}{Colors.NC}")


def print_success(text: str):
    print(f"{Colors.GREEN}✅ {text}{Colors.NC}")


def print_warning(text: str):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.NC}")


def print_error(text: str):
    print(f"{Colors.RED}❌ {text}{Colors.NC}")


class Phase2Step1Validator:
    """Validador completo do Passo 1 da Fase 2"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        sys.path.insert(0, str(self.project_root))
        self.test_results = []
        
    async def run_complete_validation(self) -> bool:
        """Executa validação completa"""
        print_header("VALIDAÇÃO FASE 2 - PASSO 1", Colors.BLUE)
        print(f"Sistema de Métricas Expandido")
        print(f"Iniciado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        
        validations = [
            ("Estrutura de Arquivos", self._validate_file_structure),
            ("Calculadora Financeira", self._validate_financial_calculator),
            ("Cliente YFinance Expandido", self._validate_enhanced_yfinance),
            ("Modelos de Dados Expandidos", self._validate_expanded_models),
            ("Sistema de Configuração", self._validate_configuration_system),
            ("Migração de Banco", self._validate_database_migration),
            ("Testes de Integração", self._validate_integration_tests),
            ("Performance", self._validate_performance)
        ]
        
        for test_name, test_func in validations:
            print_step(f"Validando: {test_name}")
            
            try:
                start_time = time.time()
                result = await test_func()
                duration = time.time() - start_time
                
                self.test_results.append({
                    "name": test_name,
                    "passed": result.get("passed", False),
                    "details": result.get("details", {}),
                    "error": result.get("error"),
                    "duration": duration
                })
                
                if result.get("passed"):
                    print_success(f"{test_name} - PASSOU ({duration:.2f}s)")
                else:
                    print_error(f"{test_name} - FALHOU ({duration:.2f}s)")
                    if result.get("error"):
                        print_error(f"   {result['error']}")
                        
            except Exception as e:
                print_error(f"{test_name} - EXCEÇÃO: {str(e)}")
                self.test_results.append({
                    "name": test_name,
                    "passed": False,
                    "error": str(e),
                    "duration": 0
                })
        
        return self._generate_final_report()
    
    async def _validate_file_structure(self) -> Dict[str, Any]:
        """Valida estrutura de arquivos criada"""
        try:
            required_files = [
                "utils/financial_calculator.py",
                "agents/collectors/enhanced_yfinance_client.py",
                "database/models.py",
                "config/metrics_config.json"
            ]
            
            required_dirs = [
                "utils",
                "agents/analyzers", 
                "database/migrations",
                "tests/phase2",
                "data/benchmarks"
            ]
            
            missing_files = []
            missing_dirs = []
            
            # Verificar arquivos
            for file_path in required_files:
                if not (self.project_root / file_path).exists():
                    missing_files.append(file_path)
            
            # Verificar diretórios
            for dir_path in required_dirs:
                if not (self.project_root / dir_path).exists():
                    missing_dirs.append(dir_path)
            
            details = {
                "required_files": len(required_files),
                "missing_files": missing_files,
                "required_dirs": len(required_dirs),
                "missing_dirs": missing_dirs
            }
            
            if missing_files or missing_dirs:
                return {
                    "passed": False,
                    "error": f"Arquivos faltando: {missing_files}, Diretórios: {missing_dirs}",
                    "details": details
                }
            
            return {"passed": True, "details": details}
            
        except Exception as e:
            return {"passed": False, "error": str(e)}
    
    async def _validate_financial_calculator(self) -> Dict[str, Any]:
        """Valida calculadora financeira"""
        try:
            from utils.financial_calculator import (
                FinancialCalculator, FinancialData, FinancialMetrics,
                calculate_cagr, normalize_metric
            )
            
            details = {}
            
            # Teste 1: Importações
            details["imports_ok"] = True
            
            # Teste 2: Criar dados de teste
            test_data = FinancialData(
                market_cap=100000000000,  # 100B
                current_price=20.0,
                revenue=50000000000,      # 50B
                net_income=6000000000,    # 6B
                total_assets=80000000000, # 80B
                total_equity=40000000000, # 40B
                total_debt=25000000000,   # 25B
                historical_revenue=[40000000000, 45000000000, 50000000000],
                historical_net_income=[4000000000, 5000000000, 6000000000]
            )
            
            # Teste 3: Calcular métricas
            calculator = FinancialCalculator()
            metrics = calculator.calculate_all_metrics(test_data)
            
            # Validar resultados
            validations = {
                "pe_ratio_calculated": metrics.pe_ratio is not None,
                "pb_ratio_calculated": metrics.pb_ratio is not None,
                "roe_calculated": metrics.roe is not None,
                "growth_calculated": metrics.revenue_growth_1y is not None,
                "data_completeness": metrics.data_completeness > 0.5
            }
            
            details.update(validations)
            details["calculated_metrics"] = {
                "pe_ratio": metrics.pe_ratio,
                "pb_ratio": metrics.pb_ratio,
                "roe": metrics.roe,
                "data_completeness": metrics.data_completeness
            }
            
            # Teste 4: Validação de métricas
            validation_result = calculator.validate_metrics(metrics)
            details["validation_warnings"] = len(validation_result.get("warnings", []))
            details["validation_errors"] = len(validation_result.get("errors", []))
            
            # Teste 5: Funções utilitárias
            cagr_result = calculate_cagr(100, 150, 3)
            normalized = normalize_metric(75, 0, 100)
            
            details["cagr_test"] = abs(cagr_result - 14.47) < 1  # ~14.47% CAGR
            details["normalize_test"] = normalized == 75.0
            
            passed = all(validations.values()) and details["cagr_test"] and details["normalize_test"]
            
            return {"passed": passed, "details": details}
            
        except Exception as e:
            return {"passed": False, "error": str(e)}
    
    async def _validate_enhanced_yfinance(self) -> Dict[str, Any]:
        """Valida cliente YFinance expandido"""
        try:
            from agents.collectors.enhanced_yfinance_client import (
                EnhancedYFinanceClient, DataValidator
            )
            
            details = {}
            
            # Teste 1: Criar cliente
            client = EnhancedYFinanceClient()
            details["client_created"] = True
            
            # Teste 2: Testar coleta de dados (mock/simulação)
            # Não vamos fazer requisições reais para evitar rate limiting
            
            # Teste 3: Validador de dados
            from utils.financial_calculator import FinancialData
            
            test_data = FinancialData(
                current_price=20.0,
                market_cap=1000000000,
                revenue=5000000000
            )
            
            validation = DataValidator.validate_financial_data(test_data)
            quality_score = DataValidator.calculate_data_quality_score(test_data)
            
            details["validator_works"] = isinstance(validation, dict)
            details["quality_score"] = quality_score
            details["cache_stats"] = client.get_cache_stats()
            
            # Teste 4: Métodos do cliente
            methods_exist = [
                hasattr(client, 'get_comprehensive_stock_data'),
                hasattr(client, 'get_batch_stock_data'),
                hasattr(client, 'get_sector_data'),
                hasattr(client, 'clear_cache')
            ]
            
            details["all_methods_exist"] = all(methods_exist)
            details["methods_count"] = sum(methods_exist)
            
            passed = (details["client_created"] and 
                     details["validator_works"] and 
                     details["all_methods_exist"] and
                     quality_score > 0)
            
            return {"passed": passed, "details": details}
            
        except Exception as e:
            return {"passed": False, "error": str(e)}
    
    async def _validate_expanded_models(self) -> Dict[str, Any]:
        """Valida modelos de dados expandidos"""
        try:
            from database.models import (
                Stock, FinancialStatement, FundamentalAnalysis,
                SectorBenchmark, DataQuality, ReportingPeriod
            )
            
            details = {}
            
            # Teste 1: Criar instâncias dos modelos
            test_stock = Stock(
                codigo="TEST4",
                nome="Empresa Teste",
                setor="Tecnologia",
                market_cap=1000000000,
                pe_ratio=15.5,
                roe=20.0,
                data_quality=DataQuality.HIGH
            )
            
            test_statement = FinancialStatement(
                stock_id=1,
                period_end_date=datetime.now(),
                reporting_period=ReportingPeriod.QUARTERLY,
                fiscal_year=2025,
                revenue=1000000000,
                net_income=100000000
            )
            
            test_analysis = FundamentalAnalysis(
                stock_id=1,
                valuation_score=75.0,
                profitability_score=80.0,
                leverage_score=70.0,
                growth_score=85.0,
                efficiency_score=65.0,
                quality_score=90.0,
                final_score=77.5
            )
            
            details["models_instantiated"] = True
            
            # Teste 2: Verificar campos obrigatórios
            required_stock_fields = ['codigo', 'nome', 'setor', 'fundamental_score']
            stock_fields_ok = all(hasattr(test_stock, field) for field in required_stock_fields)
            
            required_analysis_fields = ['valuation_score', 'final_score', 'sector_percentile_overall']
            analysis_fields_ok = all(hasattr(test_analysis, field) for field in required_analysis_fields)
            
            details["stock_fields_ok"] = stock_fields_ok
            details["analysis_fields_ok"] = analysis_fields_ok
            
            # Teste 3: Métodos to_dict
            stock_dict = test_stock.to_dict()
            analysis_dict = test_analysis.to_dict()
            
            details["to_dict_methods"] = {
                "stock_dict_keys": len(stock_dict.keys()) if stock_dict else 0,
                "analysis_dict_keys": len(analysis_dict.keys()) if analysis_dict else 0
            }
            
            # Teste 4: Enums
            details["enums_work"] = {
                "data_quality": DataQuality.HIGH.value == "high",
                "reporting_period": ReportingPeriod.QUARTERLY.value == "quarterly"
            }
            
            passed = (details["models_instantiated"] and 
                     stock_fields_ok and 
                     analysis_fields_ok and 
                     all(details["enums_work"].values()))
            
            return {"passed": passed, "details": details}
            
        except Exception as e:
            return {"passed": False, "error": str(e)}
    
    async def _validate_configuration_system(self) -> Dict[str, Any]:
        """Valida sistema de configuração"""
        try:
            details = {}
            
            # Teste 1: Arquivo de configuração de métricas
            config_path = self.project_root / 'config' / 'metrics_config.json'
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                required_keys = ['version', 'scoring_weights', 'sector_adjustments']
                config_keys_ok = all(key in config for key in required_keys)
                
                details["config_file_exists"] = True
                details["config_keys_ok"] = config_keys_ok
                details["config_version"] = config.get("version")
                details["scoring_weights"] = config.get("scoring_weights", {})
            else:
                details["config_file_exists"] = False
                config_keys_ok = False
            
            # Teste 2: Configurações expandidas em settings.py
            try:
                from config.settings import get_phase2_settings
                phase2_config = get_phase2_settings()
                
                details["phase2_settings_exist"] = True
                details["metrics_config_file"] = hasattr(phase2_config, 'metrics_config_file')
                details["analysis_settings"] = {
                    "min_data_completeness": getattr(phase2_config, 'min_data_completeness', None),
                    "confidence_threshold": getattr(phase2_config, 'confidence_threshold', None)
                }
            except ImportError:
                details["phase2_settings_exist"] = False
                details["metrics_config_file"] = False
            
            # Teste 3: Definições de métricas
            definitions_path = self.project_root / 'data' / 'metric_definitions.json'
            if definitions_path.exists():
                with open(definitions_path, 'r', encoding='utf-8') as f:
                    definitions = json.load(f)
                
                details["metric_definitions_exist"] = True
                details["definitions_count"] = len(definitions)
                
                # Verificar estrutura das definições
                if definitions:
                    first_def = definitions[0]
                    required_def_keys = ['name', 'category', 'description']
                    details["definition_structure_ok"] = all(key in first_def for key in required_def_keys)
                else:
                    details["definition_structure_ok"] = False
            else:
                details["metric_definitions_exist"] = False
                details["definition_structure_ok"] = False
            
            passed = (details["config_file_exists"] and 
                     config_keys_ok and 
                     details.get("phase2_settings_exist", False))
            
            return {"passed": passed, "details": details}
            
        except Exception as e:
            return {"passed": False, "error": str(e)}
    
    async def _validate_database_migration(self) -> Dict[str, Any]:
        """Valida migração do banco de dados"""
        try:
            from database.connection import engine, get_database_info
            
            details = {}
            
            # Teste 1: Verificar se engine funciona
            db_info = get_database_info()
            details["database_connection"] = "error" not in db_info
            details["database_type"] = db_info.get("type", "unknown")
            
            # Teste 2: Verificar se novas tabelas existem
            expected_tables = [
                "stocks",
                "financial_statements", 
                "fundamental_analyses",
                "sector_benchmarks",
                "analysis_audit_log",
                "metric_definitions"
            ]
            
            existing_tables = db_info.get("tables", [])
            new_tables_exist = [table for table in expected_tables if table in existing_tables]
            
            details["expected_tables"] = len(expected_tables)
            details["existing_new_tables"] = len(new_tables_exist)
            details["new_tables_list"] = new_tables_exist
            
            # Teste 3: Verificar script de migração
            migration_path = self.project_root / 'database' / 'migrations' / '001_expand_tables_phase2.py'
            details["migration_script_exists"] = migration_path.exists()
            
            # Teste 4: Testar criação de tabelas expandidas
            try:
                from database.models import create_expanded_tables
                details["create_function_exists"] = True
                
                # Não vamos recriar as tabelas, só verificar se a função existe
                
            except ImportError:
                details["create_function_exists"] = False
            
            passed = (details["database_connection"] and 
                     details["existing_new_tables"] >= 3 and  # Pelo menos 3 tabelas novas
                     details.get("migration_script_exists", False))
            
            return {"passed": passed, "details": details}
            
        except Exception as e:
            return {"passed": False, "error": str(e)}
    
    async def _validate_integration_tests(self) -> Dict[str, Any]:
        """Valida integração entre componentes"""
        try:
            details = {}
            
            # Teste 1: Pipeline completo - dados → cálculo → análise
            from utils.financial_calculator import FinancialCalculator, FinancialData
            
            # Criar dados de teste
            test_data = FinancialData(
                market_cap=50000000000,
                current_price=25.0,
                revenue=20000000000,
                net_income=2000000000,
                total_assets=30000000000,
                total_equity=15000000000,
                total_debt=8000000000,
                historical_revenue=[15000000000, 17000000000, 20000000000],
                historical_net_income=[1200000000, 1600000000, 2000000000]
            )
            
            # Calcular métricas
            calculator = FinancialCalculator()
            metrics = calculator.calculate_all_metrics(test_data)
            
            details["pipeline_data_creation"] = True
            details["pipeline_metrics_calculation"] = metrics.data_completeness > 0
            
            # Teste 2: Validação cruzada
            validation = calculator.validate_metrics(metrics)
            details["pipeline_validation"] = isinstance(validation, dict)
            
            # Teste 3: Configuração aplicada
            try:
                config_path = self.project_root / 'config' / 'metrics_config.json'
                if config_path.exists():
                    with open(config_path, 'r') as f:
                        config = json.load(f)
                    
                    weights = config.get("scoring_weights", {})
                    details["config_integration"] = len(weights) > 0
                else:
                    details["config_integration"] = False
            except:
                details["config_integration"] = False
            
            # Teste 4: Modelo expandido + métricas
            try:
                from database.models import Stock, DataQuality
                
                test_stock = Stock(
                    codigo="INTEG4",
                    nome="Teste Integração",
                    setor="Teste",
                    pe_ratio=metrics.pe_ratio,
                    roe=metrics.roe,
                    fundamental_score=75.0,
                    data_quality=DataQuality.HIGH
                )
                
                details["model_integration"] = test_stock.pe_ratio == metrics.pe_ratio
                
            except Exception as e:
                details["model_integration"] = False
                details["model_integration_error"] = str(e)
            
            # Teste 5: Benchmarks setoriais (função)
            try:
                benchmarks = calculator.get_sector_benchmarks("Tecnologia")
                details["benchmark_integration"] = isinstance(benchmarks, dict) and len(benchmarks) > 0
            except:
                details["benchmark_integration"] = False
            
            passed = (details["pipeline_data_creation"] and 
                     details["pipeline_metrics_calculation"] and 
                     details["pipeline_validation"] and
                     details.get("model_integration", False))
            
            return {"passed": passed, "details": details}
            
        except Exception as e:
            return {"passed": False, "error": str(e)}
    
    async def _validate_performance(self) -> Dict[str, Any]:
        """Valida performance do sistema"""
        try:
            from utils.financial_calculator import FinancialCalculator, FinancialData
            
            details = {}
            
            # Teste 1: Performance de cálculo de métricas
            calculator = FinancialCalculator()
            
            test_data = FinancialData(
                market_cap=100000000000,
                current_price=20.0,
                revenue=50000000000,
                net_income=6000000000,
                total_assets=80000000000,
                total_equity=40000000000
            )
            
            # Medir tempo de cálculo
            start_time = time.time()
            metrics = calculator.calculate_all_metrics(test_data)
            calculation_time = time.time() - start_time
            
            details["single_calculation_time"] = calculation_time
            details["calculation_fast_enough"] = calculation_time < 1.0  # < 1 segundo
            
            # Teste 2: Performance de múltiplos cálculos
            start_time = time.time()
            for i in range(10):
                test_data_batch = FinancialData(
                    market_cap=100000000000 + i * 1000000,
                    current_price=20.0 + i * 0.1,
                    revenue=50000000000 + i * 1000000,
                    net_income=6000000000 + i * 100000
                )
                calculator.calculate_all_metrics(test_data_batch)
            
            batch_time = time.time() - start_time
            avg_time_per_calculation = batch_time / 10
            
            details["batch_calculation_time"] = batch_time
            details["avg_time_per_calculation"] = avg_time_per_calculation
            details["batch_fast_enough"] = avg_time_per_calculation < 0.5  # < 0.5s por cálculo
            
            # Teste 3: Memória e recursos
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()
            
            details["memory_usage_mb"] = memory_info.rss / 1024 / 1024
            details["memory_reasonable"] = details["memory_usage_mb"] < 500  # < 500MB
            
            # Teste 4: Validação de outliers
            outlier_values = [1.0, 2.0, 3.0, 4.0, 5.0, 100.0]  # 100 é outlier
            
            start_time = time.time()
            from utils.financial_calculator import detect_outliers
            outliers = detect_outliers(outlier_values)
            outlier_detection_time = time.time() - start_time
            
            details["outlier_detection_time"] = outlier_detection_time
            details["outlier_detection_correct"] = outliers[-1] == True  # Último valor é outlier
            details["outlier_detection_fast"] = outlier_detection_time < 0.1
            
            passed = (details["calculation_fast_enough"] and 
                     details["batch_fast_enough"] and 
                     details["memory_reasonable"] and 
                     details["outlier_detection_correct"])
            
            return {"passed": passed, "details": details}
            
        except Exception as e:
            return {"passed": False, "error": str(e)}
    
    def _generate_final_report(self) -> bool:
        """Gera relatório final da validação"""
        try:
            print_header("RELATÓRIO FINAL DE VALIDAÇÃO", Colors.WHITE)
            
            # Estatísticas
            total_tests = len(self.test_results)
            passed_tests = sum(1 for t in self.test_results if t["passed"])
            failed_tests = total_tests - passed_tests
            success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
            
            print(f"\n{Colors.WHITE}📊 ESTATÍSTICAS GERAIS:{Colors.NC}")
            print(f"   Total de testes: {total_tests}")
            print(f"   Testes aprovados: {Colors.GREEN}{passed_tests}{Colors.NC}")
            print(f"   Testes falharam: {Colors.RED}{failed_tests}{Colors.NC}")
            print(f"   Taxa de sucesso: {success_rate:.1f}%")
            
            # Resultados por categoria
            print(f"\n{Colors.WHITE}📋 RESULTADOS POR CATEGORIA:{Colors.NC}")
            for test in self.test_results:
                status_color = Colors.GREEN if test["passed"] else Colors.RED
                status_icon = "✅" if test["passed"] else "❌"
                duration = test.get("duration", 0)
                
                print(f"   {status_icon} {test['name']}: {status_color}{'PASS' if test['passed'] else 'FAIL'}{Colors.NC} ({duration:.2f}s)")
                
                if not test["passed"] and test.get("error"):
                    print(f"      {Colors.RED}└─ {test['error']}{Colors.NC}")
            
            # Detalhes importantes
            print(f"\n{Colors.WHITE}🔍 DESTAQUES:{Colors.NC}")
            
            # Performance
            perf_test = next((t for t in self.test_results if t["name"] == "Performance"), None)
            if perf_test and perf_test.get("details"):
                calc_time = perf_test["details"].get("single_calculation_time", 0)
                memory_mb = perf_test["details"].get("memory_usage_mb", 0)
                print(f"   ⚡ Tempo de cálculo: {calc_time:.3f}s")
                print(f"   🧠 Uso de memória: {memory_mb:.1f}MB")
            
            # Estrutura
            struct_test = next((t for t in self.test_results if t["name"] == "Estrutura de Arquivos"), None)
            if struct_test and struct_test.get("details"):
                files_ok = len(struct_test["details"].get("missing_files", []))
                dirs_ok = len(struct_test["details"].get("missing_dirs", []))
                print(f"   📁 Arquivos implementados: {4 - files_ok}/4")
                print(f"   📂 Diretórios criados: {5 - dirs_ok}/5")
            
            # Salvar relatório JSON
            report = {
                "validation_info": {
                    "phase": "Fase 2 - Passo 1",
                    "description": "Validação do Sistema de Métricas Expandido",
                    "date": datetime.now().isoformat(),
                    "total_tests": total_tests,
                    "passed_tests": passed_tests,
                    "failed_tests": failed_tests,
                    "success_rate": success_rate
                },
                "test_results": self.test_results,
                "summary": {
                    "overall_status": "PASS" if failed_tests == 0 else "FAIL",
                    "critical_components": {
                        "financial_calculator": any(t["name"] == "Calculadora Financeira" and t["passed"] for t in self.test_results),
                        "enhanced_yfinance": any(t["name"] == "Cliente YFinance Expandido" and t["passed"] for t in self.test_results),
                        "models": any(t["name"] == "Modelos de Dados Expandidos" and t["passed"] for t in self.test_results),
                        "integration": any(t["name"] == "Testes de Integração" and t["passed"] for t in self.test_results)
                    }
                }
            }
            
            report_path = self.project_root / f"validation_report_phase2_step1_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False, default=str)
            
            # Status final
            if failed_tests == 0:
                print(f"\n{Colors.GREEN}🎉 VALIDAÇÃO COMPLETA - TODOS OS TESTES PASSARAM!{Colors.NC}")
                print(f"{Colors.GREEN}✅ Fase 2 Passo 1 implementado e validado com sucesso{Colors.NC}")
                print(f"\n{Colors.CYAN}🚀 SISTEMA PRONTO PARA O PASSO 2:{Colors.NC}")
                print("   1. Implementar Agente Analisador Fundamentalista")
                print("   2. Configurar Sistema de Scoring Avançado")
                print("   3. Implementar Benchmarks Setoriais Automáticos")
                print("   4. Criar Pipeline de Análise Automatizada")
            else:
                print(f"\n{Colors.YELLOW}⚠️  VALIDAÇÃO CONCLUÍDA COM PROBLEMAS{Colors.NC}")
                print(f"{Colors.YELLOW}🔧 Corrija os problemas antes de prosseguir para o Passo 2{Colors.NC}")
                print(f"\n{Colors.CYAN}📋 AÇÕES RECOMENDADAS:{Colors.NC}")
                print("   1. Verificar componentes que falharam")
                print("   2. Corrigir problemas identificados")
                print("   3. Executar validação novamente")
                print("   4. Verificar logs detalhados no relatório JSON")
            
            print(f"\n{Colors.WHITE}📄 Relatório detalhado salvo: {report_path.name}{Colors.NC}")
            
            return failed_tests == 0
            
        except Exception as e:
            print_error(f"Erro ao gerar relatório final: {e}")
            return False


async def main():
    """Função principal"""
    print_header("INICIANDO VALIDAÇÃO FASE 2 PASSO 1", Colors.BLUE)
    
    try:
        validator = Phase2Step1Validator()
        success = await validator.run_complete_validation()
        
        return success
        
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️  Validação interrompida pelo usuário{Colors.NC}")
        return False
    except Exception as e:
        print(f"\n{Colors.RED}❌ Erro crítico na validação: {e}{Colors.NC}")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
