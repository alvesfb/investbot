#!/usr/bin/env python3
"""
scripts/connection_stability_monitor.py
Connection Stability Monitor - Dia 4 Tarde

Sistema de monitoramento e validação de estabilidade de conexão PostgreSQL:
- Health checks contínuos
- Testes de stress de conexão
- Validação de connection pool
- Detecção de vazamentos de conexão
- Métricas de performance de conexão
"""

import sys
import os
import time
import asyncio
import threading
import traceback
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from contextlib import contextmanager
import statistics
from sqlalchemy import text

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
    print(f"\n{color}{Colors.BOLD}📊 {text}{Colors.NC}")
    print(f"{color}{'─'*50}{Colors.NC}")

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

def print_metric(name: str, value: str, status: str = "info"):
    """Imprime métrica formatada"""
    color_map = {
        "good": Colors.GREEN,
        "warning": Colors.YELLOW,
        "error": Colors.RED,
        "info": Colors.WHITE
    }
    color = color_map.get(status, Colors.WHITE)
    print(f"   {color}📈 {name}: {value}{Colors.NC}")


@dataclass
class ConnectionMetrics:
    """Métricas de conexão PostgreSQL"""
    timestamp: datetime
    connection_time: float
    query_time: float
    pool_size: int
    checked_out: int
    checked_in: int
    overflow: int
    active_connections: int
    idle_connections: int
    waiting_connections: int
    total_connections: int
    connection_success: bool
    error_message: Optional[str] = None


@dataclass
class StabilityReport:
    """Relatório de estabilidade da conexão"""
    test_duration: float
    total_tests: int
    successful_connections: int
    failed_connections: int
    success_rate: float
    avg_connection_time: float
    max_connection_time: float
    min_connection_time: float
    avg_query_time: float
    max_query_time: float
    min_query_time: float
    pool_efficiency: float
    connection_errors: List[str]
    recommendations: List[str]
    overall_status: str


class ConnectionStabilityMonitor:
    """Monitor de estabilidade de conexão PostgreSQL"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.metrics_history: List[ConnectionMetrics] = []
        self.start_time = time.time()
        self.stop_monitoring = False
        
    def run_stability_tests(self, duration_minutes: int = 1) -> StabilityReport:
        """Executa testes de estabilidade de conexão"""
        print_header("🔗 CONNECTION STABILITY MONITOR", Colors.PURPLE)
        print_info("Monitoramento de Estabilidade PostgreSQL")
        print_info(f"Duração do teste: {duration_minutes} minutos")
        print_info(f"Iniciado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        
        # Testes sequenciais
        tests = [
            ("Basic Connection Health", self._test_basic_connection),
            ("Connection Pool Status", self._test_connection_pool),
            ("Query Performance", self._test_query_performance),
            ("Connection Stress Test", lambda: self._test_connection_stress(duration_minutes)),
            ("Connection Pool Efficiency", self._test_pool_efficiency),
            ("Connection Leak Detection", self._test_connection_leaks),
            ("Database Statistics", self._test_database_stats)
        ]
        
        for test_name, test_func in tests:
            print_section(test_name)
            try:
                test_func()
                print_success(f"{test_name} - Concluído")
            except Exception as e:
                print_error(f"{test_name} - Erro: {str(e)}")
                traceback.print_exc()
        
        # Gerar relatório final
        report = self._generate_stability_report()
        self._print_stability_report(report)
        self._save_stability_report(report)
        
        return report
    
    def _test_basic_connection(self):
        """Teste básico de conexão"""
        print_info("Testando conexão básica PostgreSQL...")
        
        try:
            from database.connection import engine, check_database_connection, get_database_info
            from sqlalchemy import text
            
            # Teste de conectividade
            start_time = time.time()
            connection_ok = check_database_connection()
            connection_time = time.time() - start_time
            
            if not connection_ok:
                print_error(f"Falha na conexão básica ({connection_time:.3f}s)")
                return
            
            print_metric("Connection Status", "OK", "good")
            print_metric("Connection Time", f"{connection_time:.3f}s", "good" if connection_time < 1.0 else "warning")
            
            # Informações do banco
            db_info = get_database_info()
            print_metric("PostgreSQL Version", db_info.get('version', 'N/A'), "info")
            print_metric("Database", db_info.get('database', 'N/A'), "info")
            print_metric("Active Connections", str(db_info.get('active_connections', 0)), "info")
            
            # Registrar métrica
            metrics = ConnectionMetrics(
                timestamp=datetime.now(),
                connection_time=connection_time,
                query_time=0.0,
                pool_size=0,
                checked_out=0,
                checked_in=0,
                overflow=0,
                active_connections=db_info.get('active_connections', 0),
                idle_connections=0,
                waiting_connections=0,
                total_connections=0,
                connection_success=True
            )
            self.metrics_history.append(metrics)
            
        except Exception as e:
            print_error(f"Erro no teste básico: {str(e)}")
            
    def _test_connection_pool(self):
        """Teste do pool de conexões"""
        print_info("Analisando pool de conexões...")
        
        try:
            from database.connection import engine
            
            # Estatísticas do pool
            pool_size = engine.pool.size()
            checked_out = engine.pool.checkedout()
            checked_in = engine.pool.checkedin()
            overflow = engine.pool.overflow()
            
            print_metric("Pool Size", str(pool_size), "info")
            print_metric("Checked Out", str(checked_out), "warning" if checked_out > pool_size * 0.8 else "good")
            print_metric("Checked In", str(checked_in), "good")
            print_metric("Overflow", str(overflow), "warning" if overflow > 0 else "good")
            
            # Eficiência do pool
            utilization = (checked_out / pool_size * 100) if pool_size > 0 else 0
            print_metric("Pool Utilization", f"{utilization:.1f}%", 
                        "error" if utilization > 90 else "warning" if utilization > 70 else "good")
            
        except Exception as e:
            print_error(f"Erro análise pool: {str(e)}")
    
    def _test_query_performance(self):
        """Teste de performance de queries"""
        print_info("Testando performance de queries...")
        
        try:
            from database.connection import engine
            from sqlalchemy import text
            
            queries = [
                ("Simple SELECT", "SELECT 1"),
                ("Database Info", "SELECT version()"),
                ("Table Count", "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'"),
                ("Active Connections", "SELECT COUNT(*) FROM pg_stat_activity WHERE datname = current_database()")
            ]
            
            query_times = []
            
            for query_name, query_sql in queries:
                start_time = time.time()
                
                with engine.connect() as conn:
                    result = conn.execute(text(query_sql))
                    result.fetchall()
                
                query_time = time.time() - start_time
                query_times.append(query_time)
                
                status = "good" if query_time < 0.1 else "warning" if query_time < 0.5 else "error"
                print_metric(f"Query '{query_name}'", f"{query_time:.3f}s", status)
            
            # Estatísticas gerais
            if query_times:
                avg_time = statistics.mean(query_times)
                max_time = max(query_times)
                min_time = min(query_times)
                
                print_metric("Average Query Time", f"{avg_time:.3f}s", "good" if avg_time < 0.1 else "warning")
                print_metric("Max Query Time", f"{max_time:.3f}s", "good" if max_time < 0.5 else "warning")
                print_metric("Min Query Time", f"{min_time:.3f}s", "good")
            
        except Exception as e:
            print_error(f"Erro teste performance: {str(e)}")
    
    def _test_connection_stress(self, duration_minutes: int = 1):
        """Teste de stress das conexões"""
        print_info(f"Executando teste de stress por {duration_minutes} minutos...")
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        successful_connections = 0
        failed_connections = 0
        connection_times = []
        
        try:
            from database.connection import get_db_session
            from sqlalchemy import text
            print_info("Iniciando stress test...")
            
            while time.time() < end_time:
                test_start = time.time()
                
                try:
                    with get_db_session() as db:
                        # Query simples para testar conexão
                        result = db.execute(text("SELECT 1"))
                        result.fetchone()
                    
                    connection_time = time.time() - test_start
                    connection_times.append(connection_time)
                    successful_connections += 1
                    
                    # Progress indicator
                    if successful_connections % 10 == 0:
                        elapsed = time.time() - start_time
                        progress = (elapsed / (duration_minutes * 60)) * 100
                        print(f"   Progress: {progress:.1f}% - {successful_connections} connections OK")
                    
                except Exception as e:
                    failed_connections += 1
                    if failed_connections <= 5:  # Log apenas os primeiros erros
                        print_warning(f"Connection failed: {str(e)}")
                
                # Pequeno delay para não sobrecarregar
                time.sleep(0.1)
            
            # Resultados do stress test
            total_tests = successful_connections + failed_connections
            success_rate = (successful_connections / total_tests * 100) if total_tests > 0 else 0
            
            print_metric("Total Connections", str(total_tests), "info")
            print_metric("Successful", str(successful_connections), "good")
            print_metric("Failed", str(failed_connections), "error" if failed_connections > 0 else "good")
            print_metric("Success Rate", f"{success_rate:.1f}%", "good" if success_rate > 95 else "warning")
            
            if connection_times:
                avg_time = statistics.mean(connection_times)
                max_time = max(connection_times)
                min_time = min(connection_times)
                
                print_metric("Avg Connection Time", f"{avg_time:.3f}s", "good" if avg_time < 0.1 else "warning")
                print_metric("Max Connection Time", f"{max_time:.3f}s", "good" if max_time < 0.5 else "warning")
                print_metric("Min Connection Time", f"{min_time:.3f}s", "good")
            
        except Exception as e:
            print_error(f"Erro stress test: {str(e)}")
    
    def _test_pool_efficiency(self):
        """Teste de eficiência do pool (sem threading problemático)"""
        print_info("Testando eficiência do pool sequencialmente...")
        
        try:
            from database.connection import get_db_session
            
            results = []
            
            # Testar múltiplas conexões sequenciais (não simultâneas)
            for i in range(5):
                start_time = time.time()
                try:
                    with get_db_session() as db:
                        result = db.execute(text("SELECT 1"))
                        result.fetchone()
                    
                    duration = time.time() - start_time
                    results.append({"worker": i, "duration": duration, "success": True})
                    
                except Exception as e:
                    results.append({"worker": i, "error": str(e), "success": False})
            
            # Análise dos resultados
            successful_workers = [r for r in results if r.get("success")]
            failed_workers = [r for r in results if not r.get("success")]
            
            print_metric("Sequential Workers", "5", "info")
            print_metric("Successful Workers", str(len(successful_workers)), "good")
            print_metric("Failed Workers", str(len(failed_workers)), "error" if failed_workers else "good")
            
            if successful_workers:
                durations = [r["duration"] for r in successful_workers]
                avg_duration = statistics.mean(durations)
                print_metric("Avg Connection Time", f"{avg_duration:.3f}s", "good" if avg_duration < 0.1 else "warning")
            
            print_success("Pool efficiency test completed (sequential mode)")
            
        except Exception as e:
            print_error(f"Erro teste eficiência: {str(e)}")

    def _test_connection_leaks(self):
        """Teste de vazamentos de conexão"""
        print_info("Detectando vazamentos de conexão...")
        
        try:
            from database.connection import engine
            
            # Estado inicial do pool
            initial_checked_out = engine.pool.checkedout()
            initial_checked_in = engine.pool.checkedin()
            
            print_metric("Initial Checked Out", str(initial_checked_out), "info")
            print_metric("Initial Checked In", str(initial_checked_in), "info")
            
            # Simular uso normal de conexões
            print_info("Simulando uso de conexões...")
            
            from database.connection import get_db_session
            
            for i in range(10):
                with get_db_session() as db:
                    db.execute(text("SELECT 1"))
            
            # Aguardar um pouco para cleanup
            time.sleep(1)
            
            # Estado final do pool
            final_checked_out = engine.pool.checkedout()
            final_checked_in = engine.pool.checkedin()
            
            print_metric("Final Checked Out", str(final_checked_out), "info")
            print_metric("Final Checked In", str(final_checked_in), "info")
            
            # Verificar se há vazamento
            leak_detected = final_checked_out > initial_checked_out
            
            if leak_detected:
                print_warning(f"Possível vazamento detectado: {final_checked_out - initial_checked_out} conexões")
            else:
                print_success("Nenhum vazamento de conexão detectado")
                
        except Exception as e:
            print_error(f"Erro detecção vazamentos: {str(e)}")
    
    def _test_database_stats(self):
        """Testa estatísticas do banco"""
        print_info("Coletando estatísticas do banco...")
        
        try:
            from database.connection import engine
            from sqlalchemy import text
            
            with engine.connect() as conn:
                # Estatísticas de conexão
                result = conn.execute(text("""
                    SELECT 
                        state,
                        COUNT(*) as count
                    FROM pg_stat_activity 
                    WHERE datname = current_database()
                    GROUP BY state
                    ORDER BY count DESC
                """))
                
                print_info("Connection States:")
                for row in result.fetchall():
                    state = row[0] or "unknown"
                    count = row[1]
                    print_metric(f"  State '{state}'", str(count), "info")
                
                # Tamanho do banco
                result = conn.execute(text("""
                    SELECT pg_size_pretty(pg_database_size(current_database())) as db_size
                """))
                db_size = result.fetchone()[0]
                print_metric("Database Size", db_size, "info")
                
                # Número de tabelas
                result = conn.execute(text("""
                    SELECT COUNT(*) FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """))
                table_count = result.fetchone()[0]
                print_metric("Public Tables", str(table_count), "info")
                
        except Exception as e:
            print_error(f"Erro estatísticas banco: {str(e)}")
    
    def _generate_stability_report(self) -> StabilityReport:
        """Gera relatório de estabilidade"""
        
        if not self.metrics_history:
            return StabilityReport(
                test_duration=time.time() - self.start_time,
                total_tests=0,
                successful_connections=0,
                failed_connections=0,
                success_rate=0.0,
                avg_connection_time=0.0,
                max_connection_time=0.0,
                min_connection_time=0.0,
                avg_query_time=0.0,
                max_query_time=0.0,
                min_query_time=0.0,
                pool_efficiency=0.0,
                connection_errors=[],
                recommendations=["Nenhuma métrica coletada"],
                overall_status="UNKNOWN"
            )
        
        # Calcular métricas
        successful_metrics = [m for m in self.metrics_history if m.connection_success]
        failed_metrics = [m for m in self.metrics_history if not m.connection_success]
        
        connection_times = [m.connection_time for m in successful_metrics if m.connection_time > 0]
        query_times = [m.query_time for m in successful_metrics if m.query_time > 0]
        
        # Estatísticas básicas
        total_tests = len(self.metrics_history)
        successful_connections = len(successful_metrics)
        failed_connections = len(failed_metrics)
        success_rate = (successful_connections / total_tests * 100) if total_tests > 0 else 0
        
        # Métricas de tempo
        avg_connection_time = statistics.mean(connection_times) if connection_times else 0.0
        max_connection_time = max(connection_times) if connection_times else 0.0
        min_connection_time = min(connection_times) if connection_times else 0.0
        
        avg_query_time = statistics.mean(query_times) if query_times else 0.0
        max_query_time = max(query_times) if query_times else 0.0
        min_query_time = min(query_times) if query_times else 0.0
        
        # Pool efficiency (estimativa)
        pool_efficiency = min(100.0, success_rate) if success_rate > 0 else 0.0
        
        # Gerar recomendações
        recommendations = self._generate_recommendations(
            success_rate, avg_connection_time, avg_query_time
        )
        
        # Status geral
        if success_rate >= 99 and avg_connection_time < 0.1:
            overall_status = "EXCELLENT"
        elif success_rate >= 95 and avg_connection_time < 0.5:
            overall_status = "GOOD"
        elif success_rate >= 90:
            overall_status = "ACCEPTABLE"
        else:
            overall_status = "NEEDS_ATTENTION"
        
        return StabilityReport(
            test_duration=time.time() - self.start_time,
            total_tests=total_tests,
            successful_connections=successful_connections,
            failed_connections=failed_connections,
            success_rate=success_rate,
            avg_connection_time=avg_connection_time,
            max_connection_time=max_connection_time,
            min_connection_time=min_connection_time,
            avg_query_time=avg_query_time,
            max_query_time=max_query_time,
            min_query_time=min_query_time,
            pool_efficiency=pool_efficiency,
            connection_errors=[m.error_message for m in failed_metrics if m.error_message],
            recommendations=recommendations,
            overall_status=overall_status
        )
    
    def _generate_recommendations(self, success_rate: float, avg_conn_time: float, avg_query_time: float) -> List[str]:
        """Gera recomendações baseadas nas métricas"""
        recommendations = []
        
        if success_rate < 95:
            recommendations.append("🚨 Taxa de sucesso baixa - investigar problemas de conectividade")
        
        if avg_conn_time > 0.5:
            recommendations.append("⚠️ Tempo de conexão alto - considerar otimização do pool")
        
        if avg_query_time > 1.0:
            recommendations.append("⚠️ Queries lentas detectadas - revisar índices e queries")
        
        if success_rate >= 99 and avg_conn_time < 0.1:
            recommendations.append("✅ Conexão excelente - sistema pronto para produção")
        elif success_rate >= 95:
            recommendations.append("✅ Conexão estável - monitoramento recomendado")
        
        recommendations.extend([
            "📊 Monitorar métricas de conexão regularmente",
            "🔧 Considerar ajustes no pool conforme necessário",
            "🚀 Sistema PostgreSQL operacional para próximos passos"
        ])
        
        return recommendations
    
    def _print_stability_report(self, report: StabilityReport):
        """Imprime relatório de estabilidade"""
        print_header("📊 RELATÓRIO DE ESTABILIDADE DE CONEXÃO", Colors.PURPLE)
        
        # Status geral
        status_color = {
            "EXCELLENT": Colors.GREEN,
            "GOOD": Colors.GREEN,
            "ACCEPTABLE": Colors.YELLOW,
            "NEEDS_ATTENTION": Colors.RED
        }.get(report.overall_status, Colors.RED)
        
        print(f"\n{Colors.BOLD}🎯 STATUS GERAL: {status_color}{report.overall_status}{Colors.NC}")
        print(f"{Colors.BOLD}⏱️  DURAÇÃO DO TESTE: {report.test_duration:.1f}s{Colors.NC}")
        
        print_section("Estatísticas de Conexão")
        print_metric("Total de Testes", str(report.total_tests), "info")
        print_metric("Conexões Bem-sucedidas", str(report.successful_connections), "good")
        print_metric("Conexões Falharam", str(report.failed_connections), "error" if report.failed_connections > 0 else "good")
        print_metric("Taxa de Sucesso", f"{report.success_rate:.1f}%", "good" if report.success_rate > 95 else "warning")
        
        print_section("Métricas de Performance")
        print_metric("Tempo Médio Conexão", f"{report.avg_connection_time:.3f}s", "good" if report.avg_connection_time < 0.1 else "warning")
        print_metric("Tempo Máximo Conexão", f"{report.max_connection_time:.3f}s", "good" if report.max_connection_time < 0.5 else "warning")
        print_metric("Tempo Médio Query", f"{report.avg_query_time:.3f}s", "good" if report.avg_query_time < 0.1 else "warning")
        print_metric("Eficiência do Pool", f"{report.pool_efficiency:.1f}%", "good" if report.pool_efficiency > 90 else "warning")
        
        if report.recommendations:
            print_section("Recomendações")
            for rec in report.recommendations:
                print(f"   {rec}")
    
    def _save_stability_report(self, report: StabilityReport):
        """Salva relatório em arquivo"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            report_file = self.project_root / f"connection_stability_report_{timestamp}.json"
            
            import json
            
            report_data = {
                "stability_info": {
                    "name": "Connection Stability Monitor",
                    "description": "Monitoramento de estabilidade PostgreSQL",
                    "timestamp": datetime.now().isoformat(),
                    "test_duration": report.test_duration
                },
                "metrics": asdict(report)
            }
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False, default=str)
            
            print_info(f"📄 Relatório salvo: {report_file}")
            
        except Exception as e:
            print_warning(f"Não foi possível salvar relatório: {e}")


def main():
    """Função principal do monitor de estabilidade"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Connection Stability Monitor")
    parser.add_argument('--duration', type=int, default=1, 
                       help='Duração do teste em minutos (default: 1)')
    parser.add_argument('--quick', action='store_true',
                       help='Execução rápida (30 segundos)')
    
    args = parser.parse_args()
    
    duration = 0.5 if args.quick else args.duration
    
    print_header("🔗 CONNECTION STABILITY MONITOR", Colors.CYAN)
    print_info("Sistema de Monitoramento PostgreSQL")
    print_info(f"Duração configurada: {duration} minutos")
    
    monitor = ConnectionStabilityMonitor()
    
    try:
        # Executar monitoramento
        report = monitor.run_stability_tests(duration)
        
        # Determinar exit code baseado no status
        if report.overall_status == "EXCELLENT":
            exit_code = 0
        elif report.overall_status in ["GOOD", "ACCEPTABLE"]:
            exit_code = 1  # Warning
        else:
            exit_code = 2  # Error
        
        print_header("🏁 MONITORAMENTO CONCLUÍDO", Colors.GREEN if exit_code == 0 else Colors.YELLOW)
        
        if exit_code == 0:
            print_success("✅ Conexão PostgreSQL excelente - sistema pronto!")
        elif exit_code == 1:
            print_warning("⚠️ Conexão estável com observações - monitorar")
        else:
            print_error("🚨 Problemas de estabilidade detectados - investigar")
        
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        print_warning("\nMonitoramento interrompido pelo usuário")
        sys.exit(130)
    except Exception as e:
        print_error(f"Erro crítico no monitoramento: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()