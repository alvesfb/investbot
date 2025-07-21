#!/usr/bin/env python3
"""
scripts/validation_pipeline_minimal.py
Validation Pipeline Mínimo - Dia 4 Tarde

Pipeline de validação consolidado que:
- Executa validações críticas pós-migração
- Consolida resultados de testes
- Fornece parecer final para prosseguir
- Gera relatório de readiness
"""

import sys
import os
import time
import json
import asyncio
import traceback
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict

# Adicionar diretório raiz ao path
sys.path.append(str(Path(__file__).parent.parent))

# Cores para output
class Colors:
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    RED = '\033[0;31m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    WHITE = '\033[1;37m'
    BOLD = '\033[1m'
    NC = '\033[0m'  # No Color

def print_header(text: str, color: str = Colors.BLUE):
    """Imprime cabeçalho formatado"""
    print(f"\n{color}{Colors.BOLD}{'='*70}{Colors.NC}")
    print(f"{color}{Colors.BOLD}{text.center(70)}{Colors.NC}")
    print(f"{color}{Colors.BOLD}{'='*70}{Colors.NC}")

def print_section(text: str, color: str = Colors.CYAN):
    """Imprime seção"""
    print(f"\n{color}{Colors.BOLD}📋 {text}{Colors.NC}")
    print(f"{color}{'─'*60}{Colors.NC}")

def print_step(text: str):
    """Imprime passo do teste"""
    print(f"\n{Colors.WHITE}🔍 {text}{Colors.NC}")

def print_success(text: str):
    """Imprime sucesso"""
    print(f"{Colors.GREEN}✅ {text}{Colors.NC}")

def print_error(text: str):
    """Imprime erro"""
    print(f"{Colors.RED}❌ {text}{Colors.NC}")

def print_warning(text: str):
    """Imprime aviso"""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.NC}")

def print_info(text: str):
    """Imprime informação"""
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.NC}")

def print_critical(text: str):
    """Imprime crítico"""
    print(f"{Colors.RED}{Colors.BOLD}🚨 {text}{Colors.NC}")


@dataclass
class ValidationResult:
    """Resultado de uma validação individual"""
    name: str
    passed: bool
    critical: bool = True
    duration: float = 0.0
    details: Dict[str, Any] = None
    error: str = None
    recommendations: List[str] = None
    
    def __post_init__(self):
        if self.details is None:
            self.details = {}
        if self.recommendations is None:
            self.recommendations = []


@dataclass
class PipelineResults:
    """Resultados consolidados do pipeline"""
    total_validations: int = 0
    passed_validations: int = 0
    failed_validations: int = 0
    critical_failed: int = 0
    warnings: int = 0
    total_duration: float = 0.0
    overall_status: str = "UNKNOWN"
    readiness_score: float = 0.0
    results: List[ValidationResult] = None
    final_recommendations: List[str] = None
    
    def __post_init__(self):
        if self.results is None:
            self.results = []
        if self.final_recommendations is None:
            self.final_recommendations = []


class ValidationPipeline:
    """Pipeline de validação consolidado para sistema pós-migração"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.start_time = time.time()
        self.results = PipelineResults()
        
    def run_validation_pipeline(self) -> PipelineResults:
        """Executa pipeline completo de validação"""
        print_header("🔍 VALIDATION PIPELINE - DIA 4 TARDE", Colors.PURPLE)
        print_info("Sistema de Recomendações - Validação Pós-Migração PostgreSQL")
        print_info(f"Iniciado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        
        # Pipeline de validações em ordem de prioridade
        validations = [
            # CRÍTICAS - Sistema não funciona se falhar
            ("PostgreSQL Connection", self._validate_postgresql, True),
            ("Database Schema", self._validate_schema, True),
            ("Model Integration", self._validate_models, True),
            ("Repository Layer", self._validate_repositories, True),
            
            # IMPORTANTES - Sistema funciona mas com limitações
            ("Data Population", self._validate_data_population, False),
            ("Stock Collector", self._validate_stock_collector, False),
            ("Configuration", self._validate_configuration, False),
            
            # OPCIONAIS - Nice-to-have
            ("Performance Baseline", self._validate_performance, False),
            ("Environment Setup", self._validate_environment, False)
        ]
        
        print_section("Executando Validações Sequenciais")
        
        for validation_name, validation_func, is_critical in validations:
            result = self._run_single_validation(validation_name, validation_func, is_critical)
            self.results.results.append(result)
            
            # Se crítica falhar, avaliar se deve continuar
            if is_critical and not result.passed:
                print_critical(f"Validação crítica falhou: {validation_name}")
                self._ask_continue_or_abort()
        
        # Calcular métricas finais
        self._calculate_final_metrics()
        
        # Gerar recomendações
        self._generate_recommendations()
        
        # Imprimir relatório final
        self._print_final_report()
        
        # Salvar relatório
        self._save_report()
        
        return self.results
    
    def _run_single_validation(self, name: str, func, is_critical: bool) -> ValidationResult:
        """Executa uma validação individual"""
        print_step(f"Validando: {name}")
        
        start_time = time.time()
        result = ValidationResult(name=name, passed=True, critical=is_critical)
        
        try:
            validation_result = func()
            result.passed = validation_result.get("passed", False)
            result.details = validation_result.get("details", {})
            result.error = validation_result.get("error")
            result.duration = time.time() - start_time
            
            if result.passed:
                print_success(f"{name} - OK ({result.duration:.2f}s)")
            else:
                if is_critical:
                    print_critical(f"{name} - FALHOU ({result.duration:.2f}s)")
                else:
                    print_warning(f"{name} - FALHOU ({result.duration:.2f}s)")
                
                if result.error:
                    print_error(f"   Erro: {result.error}")
            
        except Exception as e:
            result.passed = False
            result.error = str(e)
            result.duration = time.time() - start_time
            
            if is_critical:
                print_critical(f"{name} - EXCEÇÃO ({result.duration:.2f}s): {str(e)}")
            else:
                print_warning(f"{name} - EXCEÇÃO ({result.duration:.2f}s): {str(e)}")
        
        return result
    
    def _validate_postgresql(self) -> Dict[str, Any]:
        """Validação crítica: Conexão PostgreSQL"""
        try:
            from database.connection import engine, check_database_connection, get_database_info
            from sqlalchemy import text
            
            # Teste básico de conexão
            if not check_database_connection():
                return {"passed": False, "error": "Falha na conexão básica com PostgreSQL"}
            
            # Informações do banco
            db_info = get_database_info()
            
            # Teste de query simples
            with engine.connect() as conn:
                result = conn.execute(text("SELECT version()"))
                pg_version = result.fetchone()[0]
            
            return {
                "passed": True,
                "details": {
                    "database": db_info.get("database"),
                    "postgresql_version": pg_version,
                    "connection_status": "OK"
                }
            }
            
        except Exception as e:
            return {"passed": False, "error": f"Erro PostgreSQL: {str(e)}"}
    
    def _validate_schema(self) -> Dict[str, Any]:
        """Validação crítica: Schema do banco"""
        try:
            from database.models import Base, Stock, Recommendation
            from database.connection import engine
            from sqlalchemy import inspect
            
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            
            # Tabelas obrigatórias
            required_tables = ['stocks', 'recommendations']
            missing_tables = [table for table in required_tables if table not in tables]
            
            if missing_tables:
                return {
                    "passed": False,
                    "error": f"Tabelas obrigatórias faltando: {missing_tables}",
                    "details": {"found_tables": tables}
                }
            
            # Verificar estrutura da tabela stocks
            stocks_columns = [col['name'] for col in inspector.get_columns('stocks')]
            
            return {
                "passed": True,
                "details": {
                    "total_tables": len(tables),
                    "tables": tables,
                    "stocks_columns_count": len(stocks_columns),
                    "schema_status": "Valid"
                }
            }
            
        except Exception as e:
            return {"passed": False, "error": f"Erro validação schema: {str(e)}"}
    
    def _validate_models(self) -> Dict[str, Any]:
        """Validação crítica: Modelos SQLAlchemy"""
        try:
            from database.models import Stock, Recommendation, FundamentalAnalysis
            from database.connection import get_db_session
            
            # Teste básico de instanciação
            models_tested = []
            
            # Testar Stock
            stock_fields = Stock.__table__.columns.keys()
            models_tested.append({"model": "Stock", "fields_count": len(stock_fields)})
            
            # Testar Recommendation
            rec_fields = Recommendation.__table__.columns.keys()
            models_tested.append({"model": "Recommendation", "fields_count": len(rec_fields)})
            
            # Testar conexão com sessão
            with get_db_session() as db:
                stock_count = db.query(Stock).count()
                rec_count = db.query(Recommendation).count()
            
            return {
                "passed": True,
                "details": {
                    "models_tested": models_tested,
                    "current_stocks": stock_count,
                    "current_recommendations": rec_count,
                    "models_status": "Functional"
                }
            }
            
        except Exception as e:
            return {"passed": False, "error": f"Erro modelos: {str(e)}"}
    
    def _validate_repositories(self) -> Dict[str, Any]:
        """Validação crítica: Camada de repositories"""
        try:
            from database.repositories import get_stock_repository
            from database.connection import get_db_session
            
            with get_db_session() as db:
                stock_repo = get_stock_repository(db)
                
                # Testar métodos básicos
                repo_methods = [method for method in dir(stock_repo) if not method.startswith('_')]
                
                # Testar operação básica
                stocks = stock_repo.get_all_stocks()
                
                return {
                    "passed": True,
                    "details": {
                        "repository_methods": len(repo_methods),
                        "sample_stocks_retrieved": len(stocks),
                        "repository_status": "Functional"
                    }
                }
                
        except Exception as e:
            return {"passed": False, "error": f"Erro repositories: {str(e)}"}
    
    def _validate_data_population(self) -> Dict[str, Any]:
        """Validação importante: População de dados"""
        try:
            from database.connection import get_db_session
            from database.models import Stock
            
            with get_db_session() as db:
                total_stocks = db.query(Stock).count()
                
                # Verificar se há dados mínimos
                if total_stocks < 5:
                    return {
                        "passed": False,
                        "error": f"Poucos stocks no banco ({total_stocks}). Mínimo: 5",
                        "details": {"current_stocks": total_stocks}
                    }
                
                # Verificar qualidade dos dados
                with_price = db.query(Stock).filter(
                    getattr(Stock, 'current_price', None) is not None or
                    getattr(Stock, 'preco_atual', None) is not None
                ).count()
                
                return {
                    "passed": True,
                    "details": {
                        "total_stocks": total_stocks,
                        "stocks_with_price": with_price,
                        "data_coverage": f"{(with_price/total_stocks)*100:.1f}%" if total_stocks > 0 else "0%"
                    }
                }
                
        except Exception as e:
            return {"passed": False, "error": f"Erro população dados: {str(e)}"}
    
    def _validate_stock_collector(self) -> Dict[str, Any]:
        """Validação importante: Agente coletor"""
        try:
            # Tentar importar componentes do collector
            components_status = {}
            
            try:
                from agents.collectors.stock_collector import YFinanceClient
                components_status["YFinanceClient"] = "Available"
            except ImportError:
                components_status["YFinanceClient"] = "Not Available"
            
            try:
                from agents.collectors.stock_collector import StockCollectorAgent
                components_status["StockCollectorAgent"] = "Available"
            except ImportError:
                components_status["StockCollectorAgent"] = "Not Available"
            
            # Testar yfinance básico
            try:
                import yfinance as yf
                ticker = yf.Ticker("PETR4.SA")
                info = ticker.info
                yfinance_status = "Working" if info.get('regularMarketPrice') else "Limited"
            except:
                yfinance_status = "Error"
            
            # Considerado OK se pelo menos yfinance funciona
            passed = yfinance_status in ["Working", "Limited"]
            
            return {
                "passed": passed,
                "details": {
                    "components": components_status,
                    "yfinance_status": yfinance_status,
                    "collector_ready": passed
                }
            }
            
        except Exception as e:
            return {"passed": False, "error": f"Erro stock collector: {str(e)}"}
    
    def _validate_configuration(self) -> Dict[str, Any]:
        """Validação importante: Configurações"""
        try:
            from config.settings import get_settings
            
            settings = get_settings()
            
            # Verificar configurações essenciais
            config_checks = {
                "database_url": bool(settings.database_url),
                "environment": bool(settings.environment),
                "log_level": bool(settings.log_level)
            }
            
            passed_checks = sum(config_checks.values())
            total_checks = len(config_checks)
            
            return {
                "passed": passed_checks >= total_checks * 0.7,  # 70% das configs OK
                "details": {
                    "configuration_checks": config_checks,
                    "config_coverage": f"{(passed_checks/total_checks)*100:.1f}%",
                    "environment": settings.environment
                }
            }
            
        except Exception as e:
            return {"passed": False, "error": f"Erro configuração: {str(e)}"}
    
    def _validate_performance(self) -> Dict[str, Any]:
        """Validação opcional: Performance básica"""
        try:
            from database.connection import engine
            from sqlalchemy import text
            import time
            
            # Teste de performance de query simples
            start_time = time.time()
            with engine.connect() as conn:
                conn.execute(text("SELECT COUNT(*) FROM stocks"))
            query_time = time.time() - start_time
            
            # Considerado OK se query demora menos que 1s
            performance_ok = query_time < 1.0
            
            return {
                "passed": performance_ok,
                "details": {
                    "simple_query_time": f"{query_time:.3f}s",
                    "performance_status": "Good" if performance_ok else "Slow"
                }
            }
            
        except Exception as e:
            return {"passed": False, "error": f"Erro performance: {str(e)}"}
    
    def _validate_environment(self) -> Dict[str, Any]:
        """Validação opcional: Ambiente e dependências"""
        try:
            import sys
            import platform
            
            # Verificar Python version
            python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
            python_ok = sys.version_info >= (3, 8)
            
            # Verificar virtual env
            venv_active = sys.prefix != sys.base_prefix
            
            # Verificar algumas dependências críticas
            deps_status = {}
            critical_deps = ['sqlalchemy', 'pydantic', 'fastapi']
            
            for dep in critical_deps:
                try:
                    __import__(dep)
                    deps_status[dep] = "OK"
                except ImportError:
                    deps_status[dep] = "Missing"
            
            deps_ok = all(status == "OK" for status in deps_status.values())
            
            return {
                "passed": python_ok and venv_active and deps_ok,
                "details": {
                    "python_version": python_version,
                    "python_compatible": python_ok,
                    "virtual_env_active": venv_active,
                    "dependencies": deps_status,
                    "platform": platform.system()
                }
            }
            
        except Exception as e:
            return {"passed": False, "error": f"Erro ambiente: {str(e)}"}
    
    def _ask_continue_or_abort(self):
        """Pergunta se deve continuar após falha crítica"""
        print_critical("Validação crítica falhou!")
        print_info("Escolha uma ação:")
        print("   1. Continuar validações (não recomendado)")
        print("   2. Abortar e corrigir problema")
        
        try:
            choice = input("\nEscolha (1/2): ").strip()
            if choice == "2":
                print_error("Abortando validação. Corrija os problemas antes de prosseguir.")
                sys.exit(1)
            else:
                print_warning("Continuando validações...")
        except KeyboardInterrupt:
            print_error("\nValidação interrompida pelo usuário.")
            sys.exit(1)
    
    def _calculate_final_metrics(self):
        """Calcula métricas finais do pipeline"""
        self.results.total_validations = len(self.results.results)
        self.results.passed_validations = sum(1 for r in self.results.results if r.passed)
        self.results.failed_validations = self.results.total_validations - self.results.passed_validations
        self.results.critical_failed = sum(1 for r in self.results.results if r.critical and not r.passed)
        self.results.warnings = sum(1 for r in self.results.results if not r.critical and not r.passed)
        self.results.total_duration = time.time() - self.start_time
        
        # Calcular readiness score
        if self.results.total_validations == 0:
            self.results.readiness_score = 0.0
        else:
            # Score baseado em: 70% validações críticas + 30% não-críticas
            critical_results = [r for r in self.results.results if r.critical]
            non_critical_results = [r for r in self.results.results if not r.critical]
            
            critical_score = sum(1 for r in critical_results if r.passed) / len(critical_results) if critical_results else 1.0
            non_critical_score = sum(1 for r in non_critical_results if r.passed) / len(non_critical_results) if non_critical_results else 1.0
            
            self.results.readiness_score = (critical_score * 0.7 + non_critical_score * 0.3) * 100
        
        # Determinar status geral
        if self.results.critical_failed == 0:
            if self.results.readiness_score >= 90:
                self.results.overall_status = "EXCELLENT"
            elif self.results.readiness_score >= 75:
                self.results.overall_status = "GOOD"
            else:
                self.results.overall_status = "ACCEPTABLE"
        else:
            self.results.overall_status = "NEEDS_ATTENTION"
    
    def _generate_recommendations(self):
        """Gera recomendações baseadas nos resultados"""
        recommendations = []
        
        # Recomendações baseadas em falhas críticas
        critical_failures = [r for r in self.results.results if r.critical and not r.passed]
        for failure in critical_failures:
            recommendations.append(f"🚨 CRÍTICO: Corrigir {failure.name} antes de prosseguir")
        
        # Recomendações baseadas em warnings
        warnings = [r for r in self.results.results if not r.critical and not r.passed]
        for warning in warnings:
            recommendations.append(f"⚠️ ATENÇÃO: Resolver {warning.name} quando possível")
        
        # Recomendações gerais baseadas no score
        if self.results.readiness_score >= 90:
            recommendations.append("✅ Sistema pronto para Dia 5 - Production Ready")
        elif self.results.readiness_score >= 75:
            recommendations.append("✅ Sistema funcional - pode prosseguir com cautela")
        elif self.results.readiness_score >= 50:
            recommendations.append("⚠️ Sistema tem problemas - recomenda-se correções antes de prosseguir")
        else:
            recommendations.append("🚨 Sistema não está pronto - correções obrigatórias")
        
        # Próximos passos específicos
        if self.results.overall_status in ["EXCELLENT", "GOOD"]:
            recommendations.extend([
                "🚀 Próximo: Implementar Dia 5 - Performance Tuning",
                "📊 Próximo: Configurar Production Config",
                "📚 Próximo: Atualizar documentação"
            ])
        
        self.results.final_recommendations = recommendations
    
    def _print_final_report(self):
        """Imprime relatório final consolidado"""
        print_header("📊 RELATÓRIO FINAL DE VALIDAÇÃO", Colors.PURPLE)
        
        # Status geral
        status_color = {
            "EXCELLENT": Colors.GREEN,
            "GOOD": Colors.GREEN, 
            "ACCEPTABLE": Colors.YELLOW,
            "NEEDS_ATTENTION": Colors.RED
        }.get(self.results.overall_status, Colors.RED)
        
        print(f"\n{Colors.BOLD}📈 STATUS GERAL: {status_color}{self.results.overall_status}{Colors.NC}")
        print(f"{Colors.BOLD}🎯 READINESS SCORE: {status_color}{self.results.readiness_score:.1f}%{Colors.NC}")
        
        # Estatísticas
        print(f"\n{Colors.WHITE}📊 ESTATÍSTICAS:{Colors.NC}")
        print(f"   Total de validações: {self.results.total_validations}")
        print(f"   Validações aprovadas: {Colors.GREEN}{self.results.passed_validations}{Colors.NC}")
        print(f"   Validações falharam: {Colors.RED}{self.results.failed_validations}{Colors.NC}")
        print(f"   Falhas críticas: {Colors.RED}{self.results.critical_failed}{Colors.NC}")
        print(f"   Warnings: {Colors.YELLOW}{self.results.warnings}{Colors.NC}")
        print(f"   Tempo total: {self.results.total_duration:.2f}s")
        
        # Detalhes por validação
        print(f"\n{Colors.WHITE}📋 DETALHES POR VALIDAÇÃO:{Colors.NC}")
        for result in self.results.results:
            status_icon = "✅" if result.passed else ("🚨" if result.critical else "⚠️")
            critical_mark = " [CRÍTICA]" if result.critical else ""
            print(f"   {status_icon} {result.name}{critical_mark} ({result.duration:.2f}s)")
            if result.error:
                print(f"      {Colors.RED}Error: {result.error}{Colors.NC}")
        
        # Recomendações
        if self.results.final_recommendations:
            print(f"\n{Colors.WHITE}🎯 RECOMENDAÇÕES:{Colors.NC}")
            for recommendation in self.results.final_recommendations:
                print(f"   {recommendation}")
        
        # Parecer final
        print_header("🏁 PARECER FINAL", Colors.BOLD)
        
        if self.results.critical_failed == 0:
            print_success("✅ SISTEMA VALIDADO - Migração PostgreSQL bem-sucedida!")
            print_success("🚀 PRONTO PARA PROSSEGUIR para próximas etapas")
        else:
            print_critical("❌ SISTEMA NÃO VALIDADO - Problemas críticos detectados")
            print_critical("🛠️ CORREÇÕES OBRIGATÓRIAS antes de prosseguir")
    
    def _save_report(self):
        """Salva relatório detalhado em arquivo"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            report_file = self.project_root / f"validation_pipeline_report_{timestamp}.json"
            
            # Converter dataclasses para dict
            report_data = {
                "pipeline_info": {
                    "name": "Validation Pipeline - Dia 4 Tarde",
                    "description": "Pipeline consolidado de validação pós-migração PostgreSQL",
                    "timestamp": datetime.now().isoformat(),
                    "duration": self.results.total_duration
                },
                "results": asdict(self.results)
            }
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False, default=str)
            
            print_info(f"📄 Relatório salvo: {report_file}")
            
        except Exception as e:
            print_warning(f"Não foi possível salvar relatório: {e}")


def main():
    """Função principal do pipeline de validação"""
    print_header("🔍 VALIDATION PIPELINE MÍNIMO", Colors.CYAN)
    print_info("Sistema de Recomendações - Validação Pós-Migração")
    print_info("Execução automatizada de validações críticas")
    
    pipeline = ValidationPipeline()
    
    try:
        # Executar pipeline
        results = pipeline.run_validation_pipeline()
        
        # Determinar exit code
        if results.critical_failed == 0:
            if results.overall_status in ["EXCELLENT", "GOOD"]:
                exit_code = 0  # Sucesso total
            else:
                exit_code = 1  # Sucesso com warnings
        else:
            exit_code = 2  # Falhas críticas
        
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        print_warning("\nPipeline interrompido pelo usuário")
        sys.exit(130)
    except Exception as e:
        print_critical(f"Erro crítico no pipeline: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()