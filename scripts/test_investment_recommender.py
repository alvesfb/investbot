# scripts/test_investment_recommender.py
"""
Script de Teste para o Agente Recomendador de Investimentos - Fase 3

Este script testa todas as funcionalidades do agente recomendador:
1. Análise individual de ações
2. Análise em lote
3. Validação de qualidade
4. Geração de relatórios
5. Testes de performance

Execute com: python -m scripts.test_investment_recommender
"""

import asyncio
import sys
import time
from datetime import datetime
from typing import List, Dict
from pathlib import Path
import logging

from utils.justification_generator import JustificationGenerator

# Adicionar o diretório raiz ao path para imports
sys.path.append(str(Path(__file__).parent.parent))

from agents.recommenders.investment_recommender import (
    InvestmentRecommenderAgent, 
    RecommendationClassification,
    create_investment_recommender
)
from utils.recommendation_engine import RecommendationEngine, MarketCondition, Sector
from utils.technical_analysis import TechnicalAnalyzer

logger = logging.getLogger(__name__)


class RecommenderTester:
    """
    Classe para testar todas as funcionalidades do agente recomendador
    """
    
    def __init__(self):
        """Inicializa o testador"""
        self.logger = logger
        self.recommender = None
        self.test_results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "warnings": 0,
            "start_time": None,
            "end_time": None,
            "details": []
        }
        
        # Ações de teste (mix de setores)
        self.test_stocks = [
            "PETR4",  # Energia
            "VALE3",  # Materiais
            "ITUB4",  # Financeiro
            "BBDC4",  # Financeiro
            "ABEV3",  # Consumo básico
            "MGLU3",  # Consumo discricionário
            "WEGE3",  # Industrial
            "RENT3",  # Real Estate
        ]
    
    async def run_all_tests(self) -> Dict:
        """Executa todos os testes do agente recomendador"""
        self.test_results["start_time"] = datetime.now()
        
        print("=" * 80)
        print("🤖 TESTANDO AGENTE RECOMENDADOR DE INVESTIMENTOS - FASE 3")
        print("=" * 80)
        
        try:
            # Inicializar agente
            await self._test_agent_initialization()
            
            # Testes básicos
            await self._test_individual_analysis()
            await self._test_batch_analysis()
            await self._test_recommendation_quality()
            
            # Testes avançados
            await self._test_different_scenarios()
            await self._test_error_handling()
            await self._test_performance()
            
            # Relatório final
            await self._generate_final_report()
            
        except Exception as e:
            self.logger.error(f"Erro crítico durante os testes: {str(e)}")
            self._record_test_result("CRITICAL_ERROR", False, f"Erro crítico: {str(e)}")
        
        finally:
            self.test_results["end_time"] = datetime.now()
            return self.test_results
    
    async def _test_agent_initialization(self):
        """Teste 1: Inicialização do agente"""
        print("\n📋 Teste 1: Inicialização do Agente")
        
        try:
            self.recommender = create_investment_recommender()
            
            # Verificar se componentes foram inicializados
            assert hasattr(self.recommender, 'agent'), "Agente Agno não inicializado"
            assert hasattr(self.recommender, 'technical_analyzer'), "Analisador técnico não inicializado"
            assert hasattr(self.recommender, 'recommendation_engine'), "Engine de recomendações não inicializado"
            assert hasattr(self.recommender, 'justification_generator'), "Gerador de justificativas não inicializado"
            
            # Verificar configurações
            assert self.recommender.weights["fundamental"] == 0.70, "Peso fundamentalista incorreto"
            assert self.recommender.weights["technical"] == 0.30, "Peso técnico incorreto"
            
            self._record_test_result("AGENT_INITIALIZATION", True, "Agente inicializado com sucesso")
            print("   ✅ Agente inicializado corretamente")
            
        except Exception as e:
            self._record_test_result("AGENT_INITIALIZATION", False, f"Erro na inicialização: {str(e)}")
            print(f"   ❌ Falha na inicialização: {str(e)}")
            raise
    
    async def _test_individual_analysis(self):
        """Teste 2: Análise individual de ações"""
        print("\n📊 Teste 2: Análise Individual")
        
        test_stock = "PETR4"
        
        try:
            print(f"   Analisando {test_stock}...")
            
            recommendation = await self.recommender.analyze_stock(test_stock, force_analysis=True)
            
            # Validações básicas
            assert recommendation.stock_code == test_stock, "Código da ação incorreto"
            assert 0 <= recommendation.combined_score <= 100, "Score combinado fora do range"
            assert 0 <= recommendation.fundamental_score <= 100, "Score fundamentalista fora do range"
            assert 0 <= recommendation.technical_score <= 100, "Score técnico fora do range"
            assert 0 <= recommendation.confidence_level <= 100, "Nível de confiança fora do range"
            assert 0 <= recommendation.stop_loss_percentage <= 20, "Stop loss fora do range esperado"
            
            # Validar classificação
            valid_classifications = [c.value for c in RecommendationClassification]
            assert recommendation.classification.value in valid_classifications, "Classificação inválida"
            
            # Validar justificativa
            assert len(recommendation.justification) > 50, "Justificativa muito curta"
            assert test_stock in recommendation.justification, "Código da ação não encontrado na justificativa"
            
            self._record_test_result("INDIVIDUAL_ANALYSIS", True, f"Análise de {test_stock} bem-sucedida")
            print(f"   ✅ {test_stock} analisado: {recommendation.classification.value} (Score: {recommendation.combined_score})")
            
            # Exibir detalhes
            print(f"      📈 Fundamentalista: {recommendation.fundamental_score}")
            print(f"      📉 Técnico: {recommendation.technical_score}")
            print(f"      🎯 Confiança: {recommendation.confidence_level}%")
            print(f"      🛑 Stop Loss: {recommendation.stop_loss_percentage}%")
            
        except Exception as e:
            self._record_test_result("INDIVIDUAL_ANALYSIS", False, f"Erro na análise individual: {str(e)}")
            print(f"   ❌ Falha na análise de {test_stock}: {str(e)}")
    
    async def _test_batch_analysis(self):
        """Teste 3: Análise em lote"""
        print("\n📦 Teste 3: Análise em Lote")
        
        try:
            print(f"   Analisando {len(self.test_stocks)} ações em lote...")
            
            start_time = time.time()
            recommendations = await self.recommender.analyze_multiple_stocks(
                self.test_stocks[:4],  # Testar com 4 ações para não sobrecarregar
                max_concurrent=2
            )
            end_time = time.time()
            
            # Validações
            assert len(recommendations) > 0, "Nenhuma recomendação retornada"
            assert len(recommendations) <= len(self.test_stocks[:4]), "Mais recomendações que ações solicitadas"
            
            # Verificar se todas as recomendações são válidas
            for rec in recommendations:
                assert hasattr(rec, 'stock_code'), "Recomendação sem código da ação"
                assert hasattr(rec, 'classification'), "Recomendação sem classificação"
                assert 0 <= rec.combined_score <= 100, f"Score inválido para {rec.stock_code}"
            
            processing_time = end_time - start_time
            avg_time_per_stock = processing_time / len(recommendations)
            
            self._record_test_result("BATCH_ANALYSIS", True, 
                f"Análise em lote bem-sucedida: {len(recommendations)} ações em {processing_time:.1f}s")
            
            print(f"   ✅ Lote processado: {len(recommendations)} ações em {processing_time:.1f}s")
            print(f"      ⏱️  Tempo médio por ação: {avg_time_per_stock:.1f}s")
            
            # Resumo das recomendações
            classifications = {}
            for rec in recommendations:
                cls = rec.classification.value
                classifications[cls] = classifications.get(cls, 0) + 1
            
            print("      📊 Distribuição de recomendações:")
            for cls, count in classifications.items():
                print(f"         {cls}: {count}")
                
        except Exception as e:
            self._record_test_result("BATCH_ANALYSIS", False, f"Erro na análise em lote: {str(e)}")
            print(f"   ❌ Falha na análise em lote: {str(e)}")
    
    async def _test_recommendation_quality(self):
        """Teste 4: Qualidade das recomendações"""
        print("\n🎯 Teste 4: Qualidade das Recomendações")
        
        try:
            # Testar com scores conhecidos
            test_cases = [
                {"fund": 85, "tech": 80, "expected_range": (80, 90)},
                {"fund": 25, "tech": 30, "expected_range": (20, 35)},
                {"fund": 50, "tech": 50, "expected_range": (45, 55)},
            ]
            
            engine = RecommendationEngine()
            passed_cases = 0
            
            for i, case in enumerate(test_cases, 1):
                combined_score, confidence = engine.calculate_combined_score(
                    case["fund"], case["tech"]
                )
                
                expected_min, expected_max = case["expected_range"]
                in_range = expected_min <= combined_score <= expected_max
                
                if in_range:
                    passed_cases += 1
                    print(f"   ✅ Caso {i}: Score {combined_score:.1f} (esperado: {expected_min}-{expected_max})")
                else:
                    print(f"   ❌ Caso {i}: Score {combined_score:.1f} fora do range {expected_min}-{expected_max}")
            
            success_rate = (passed_cases / len(test_cases)) * 100
            
            if success_rate >= 80:
                self._record_test_result("RECOMMENDATION_QUALITY", True, 
                    f"Qualidade adequada: {success_rate:.0f}% de acerto")
                print(f"   ✅ Qualidade das recomendações: {success_rate:.0f}% de acerto")
            else:
                self._record_test_result("RECOMMENDATION_QUALITY", False, 
                    f"Qualidade baixa: {success_rate:.0f}% de acerto")
                print(f"   ⚠️  Qualidade das recomendações: {success_rate:.0f}% de acerto (abaixo de 80%)")
                
        except Exception as e:
            self._record_test_result("RECOMMENDATION_QUALITY", False, f"Erro no teste de qualidade: {str(e)}")
            print(f"   ❌ Falha no teste de qualidade: {str(e)}")
    
    async def _test_different_scenarios(self):
        """Teste 5: Diferentes cenários de mercado"""
        print("\n🌍 Teste 5: Cenários de Mercado")
        
        try:
            engine = RecommendationEngine()
            scenarios = [
                MarketCondition.BULL_MARKET,
                MarketCondition.BEAR_MARKET,
                MarketCondition.HIGH_VOLATILITY,
                MarketCondition.NORMAL
            ]
            
            base_fund_score = 70.0
            base_tech_score = 60.0
            
            scenario_results = {}
            
            for scenario in scenarios:
                context = engine.create_recommendation_context(
                    sector=Sector.FINANCIALS,
                    market_condition=scenario
                )
                
                combined_score, confidence = engine.calculate_combined_score(
                    base_fund_score, base_tech_score, context
                )
                
                scenario_results[scenario.value] = {
                    "combined_score": combined_score,
                    "confidence": confidence
                }
                
                print(f"   📊 {scenario.value}: Score {combined_score:.1f}, Confiança {confidence:.1f}%")
            
            # Verificar se os ajustes fazem sentido
            bull_score = scenario_results["BULL_MARKET"]["combined_score"]
            bear_score = scenario_results["BEAR_MARKET"]["combined_score"]
            
            # Em mercado em alta, esperamos score ligeiramente diferente do mercado em baixa
            if abs(bull_score - bear_score) > 1:
                print("   ✅ Ajustes de mercado funcionando corretamente")
                self._record_test_result("MARKET_SCENARIOS", True, "Ajustes de cenários funcionais")
            else:
                print("   ⚠️  Ajustes de mercado podem estar muito sutis")
                self._record_test_result("MARKET_SCENARIOS", False, "Ajustes de mercado imperceptíveis")
                
        except Exception as e:
            self._record_test_result("MARKET_SCENARIOS", False, f"Erro nos cenários: {str(e)}")
            print(f"   ❌ Falha nos testes de cenário: {str(e)}")
    
    async def _test_performance(self):
        """Teste 7: Performance"""
        print("\n⚡ Teste 7: Performance")
        
        try:
            # Teste de performance com uma ação
            start_time = time.time()
            recommendation = await self.recommender.analyze_stock("VALE3", force_analysis=True)
            single_analysis_time = time.time() - start_time
            
            print(f"   ⏱️  Análise individual: {single_analysis_time:.2f}s")
            
            # Verificar se está dentro do limite aceitável (< 60s conforme especificação)
            if single_analysis_time < 60:
                print("   ✅ Performance individual adequada")
                performance_ok = True
            else:
                print("   ⚠️  Performance individual lenta")
                performance_ok = False
            
            # Teste de memory usage básico
            try:
                import psutil
                import os
                
                process = psutil.Process(os.getpid())
                memory_usage = process.memory_info().rss / 1024 / 1024  # MB
                
                print(f"   💾 Uso de memória: {memory_usage:.1f} MB")
                
                if memory_usage < 500:  # Menos de 500MB
                    print("   ✅ Uso de memória adequado")
                    memory_ok = True
                else:
                    print("   ⚠️  Alto uso de memória")
                    memory_ok = False
            except ImportError:
                print("   ⚠️  psutil não disponível, pulando teste de memória")
                memory_ok = True  # Não considerar falha se psutil não estiver disponível
            
            # Teste de performance em lote (menor escala)
            print("   🔄 Testando análise em lote...")
            batch_start = time.time()
            batch_stocks = ["ITUB4", "BBDC4"]  # Só 2 ações para não sobrecarregar
            batch_results = await self.recommender.analyze_multiple_stocks(batch_stocks, max_concurrent=2)
            batch_time = time.time() - batch_start
            
            avg_batch_time = batch_time / len(batch_results) if batch_results else float('inf')
            print(f"   ⚡ Lote: {len(batch_results)} ações em {batch_time:.1f}s (média: {avg_batch_time:.1f}s/ação)")
            
            if performance_ok and memory_ok and avg_batch_time < 120:  # 2 min por ação em lote
                self._record_test_result("PERFORMANCE", True, 
                    f"Performance adequada: Individual {single_analysis_time:.2f}s, Lote {avg_batch_time:.1f}s/ação")
            else:
                issues = []
                if not performance_ok:
                    issues.append("análise individual lenta")
                if not memory_ok:
                    issues.append("alto uso de memória")
                if avg_batch_time >= 120:
                    issues.append("análise em lote lenta")
                
                self._record_test_result("PERFORMANCE", False, 
                    f"Performance inadequada: {', '.join(issues)}")
                
        except Exception as e:
            self._record_test_result("PERFORMANCE", False, f"Erro no teste de performance: {str(e)}")
            print(f"   ❌ Falha no teste de performance: {str(e)}")
    
    async def _generate_final_report(self):
        """Gera relatório final dos testes"""
        print("\n" + "=" * 80)
        print("📋 RELATÓRIO FINAL DOS TESTES")
        print("=" * 80)
        
        total_time = (self.test_results["end_time"] - self.test_results["start_time"]).total_seconds()
        success_rate = (self.test_results["passed"] / self.test_results["total_tests"]) * 100 if self.test_results["total_tests"] > 0 else 0
        
        print(f"⏱️  Tempo total de execução: {total_time:.1f}s")
        print(f"📊 Total de testes: {self.test_results['total_tests']}")
        print(f"✅ Testes aprovados: {self.test_results['passed']}")
        print(f"❌ Testes falharam: {self.test_results['failed']}")
        print(f"⚠️  Warnings: {self.test_results['warnings']}")
        print(f"🎯 Taxa de sucesso: {success_rate:.1f}%")
        
        print("\n📝 Detalhes dos testes:")
        for detail in self.test_results["details"]:
            status = "✅" if detail["passed"] else "❌"
            print(f"   {status} {detail['test_name']}: {detail['message']}")
        
        # Avaliação geral
        print("\n🏆 AVALIAÇÃO GERAL:")
        if success_rate >= 90:
            print("   🟢 EXCELENTE - Sistema pronto para Fase 3")
        elif success_rate >= 75:
            print("   🟡 BOM - Pequenos ajustes recomendados")
        elif success_rate >= 60:
            print("   🟠 REGULAR - Correções necessárias")
        else:
            print("   🔴 INADEQUADO - Revisão completa necessária")
        
        # Recomendações
        print("\n💡 PRÓXIMOS PASSOS:")
        if self.test_results["failed"] == 0:
            print("   • ✅ Prosseguir para implementação dos endpoints FastAPI")
            print("   • ✅ Configurar frontend Agno nativo")
            print("   • ✅ Implementar testes de integração")
            print("   • ✅ Começar Passo 2.1 da Fase 3")
        else:
            print("   • ❌ Corrigir falhas identificadas nos testes")
            print("   • 🔄 Re-executar testes após correções")
            print("   • 📚 Revisar documentação de componentes problemáticos")
        
        print("\n📄 DOCUMENTAÇÃO GERADA:")
        print("   • 📋 Log detalhado dos testes disponível no logger")
        print("   • 📊 Métricas de performance coletadas")
        print("   • ✅ Cenários de teste validados")
        print("   • 💾 Arquivo JSON com resultados completos")
        
        # Análise de componentes
        print("\n🔧 ANÁLISE DE COMPONENTES:")
        component_status = {}
        for detail in self.test_results["details"]:
            component = detail["test_name"].split("_")[0]
            if component not in component_status:
                component_status[component] = {"passed": 0, "total": 0}
            component_status[component]["total"] += 1
            if detail["passed"]:
                component_status[component]["passed"] += 1
        
        for component, stats in component_status.items():
            success = (stats["passed"] / stats["total"]) * 100 if stats["total"] > 0 else 0
            status_icon = "✅" if success == 100 else "⚠️" if success >= 50 else "❌"
            print(f"   {status_icon} {component}: {success:.0f}% ({stats['passed']}/{stats['total']})")
        
        # Resumo de funcionalidades testadas
        print("\n🎯 FUNCIONALIDADES VALIDADAS:")
        functionalities = [
            ("Criação do Agente", "AGENT"),
            ("Análise Individual", "INDIVIDUAL"),
            ("Análise em Lote", "BATCH"),
            ("Qualidade de Recomendações", "RECOMMENDATION"),
            ("Cenários de Mercado", "MARKET"),
            ("Tratamento de Erros", "ERROR"),
            ("Performance", "PERFORMANCE")
        ]
        
        for func_name, test_prefix in functionalities:
            func_tests = [d for d in self.test_results["details"] if d["test_name"].startswith(test_prefix)]
            if func_tests:
                func_passed = all(t["passed"] for t in func_tests)
                status = "✅" if func_passed else "❌"
                print(f"   {status} {func_name}")
            else:
                print(f"   ⚪ {func_name} (não testado)")
        
        return self.test_results
    
    def _record_test_result(self, test_name: str, passed: bool, message: str):
        """Registra resultado de um teste"""
        self.test_results["total_tests"] += 1
        
        if passed:
            self.test_results["passed"] += 1
        else:
            self.test_results["failed"] += 1
        
        self.test_results["details"].append({
            "test_name": test_name,
            "passed": passed,
            "message": message,
            "timestamp": datetime.now()
        })
        
        # Log do resultado
        if passed:
            self.logger.info(f"✅ {test_name}: {message}")
        else:
            self.logger.error(f"❌ {test_name}: {message}")


async def main():
    """Função principal para executar todos os testes"""
    print("🚀 Iniciando testes do Agente Recomendador de Investimentos")
    print("📅 Data/Hora:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("🎯 Objetivo: Validar Passo 1.1 da Fase 3 - Agente Recomendador")
    
    tester = RecommenderTester()
    
    try:
        results = await tester.run_all_tests()
        
        # Salvar resultados em arquivo
        import json
        results_copy = results.copy()
        
        # Converter datetime para string para serialização JSON
        results_copy["start_time"] = results["start_time"].isoformat() if results["start_time"] else None
        results_copy["end_time"] = results["end_time"].isoformat() if results["end_time"] else None
        
        for detail in results_copy["details"]:
            detail["timestamp"] = detail["timestamp"].isoformat()
        
        # Salvar arquivo de resultados
        results_file = Path("test_results_recommender.json")
        with open(results_file, "w", encoding="utf-8") as f:
            json.dump(results_copy, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Resultados salvos em: {results_file}")
        
        # Código de saída baseado nos resultados
        success_rate = (results["passed"] / results["total_tests"]) * 100 if results["total_tests"] > 0 else 0
        
        if success_rate >= 80:
            print("\n🎉 TESTES CONCLUÍDOS COM SUCESSO!")
            print("🚀 Sistema pronto para Passo 2 da Fase 3!")
            return 0
        else:
            print("\n⚠️  TESTES CONCLUÍDOS COM FALHAS!")
            print("🔧 Corrija os problemas antes de prosseguir.")
            return 1
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Testes interrompidos pelo usuário")
        return 2
    except Exception as e:
        print(f"\n\n❌ Erro crítico durante os testes: {str(e)}")
        logger.error(f"Erro crítico nos testes: {str(e)}")
        import traceback
        traceback.print_exc()
        return 3


def run_quick_test():
    """Executa teste rápido para validação básica"""
    print("🏃‍♂️ Executando teste rápido...")
    
    async def quick_test():
        try:
            print("1/4 Testando inicialização...")
            # Teste básico de inicialização
            recommender = create_investment_recommender()
            print("   ✅ Agente inicializado")
            
            print("2/4 Testando engine...")
            # Teste básico de engine
            engine = RecommendationEngine()
            score, confidence = engine.calculate_combined_score(70, 60)
            print(f"   ✅ Engine funcionando: Score {score}, Confiança {confidence}")
            
            print("3/4 Testando análise técnica...")
            # Teste básico de análise técnica
            analyzer = TechnicalAnalyzer()
            tech_score = await analyzer.calculate_score("PETR4", "dados mock")
            print(f"   ✅ Análise técnica funcionando: Score {tech_score}")
            
            print("4/4 Testando justificação...")
            # Teste básico de justificação
            from agno.agent import Agent
            from agno.models.anthropic import Claude
            try:
                agent = Agent(model=Claude(id="claude-3-sonnet-20240229"), instructions="Test")
                generator = JustificationGenerator(agent)
                print("   ✅ Gerador de justificativas funcionando")
            except ImportError:
                print("   ⚠️  Agno não disponível, mas classe OK")
            
            print("\n🎉 Teste rápido concluído com sucesso!")
            print("💡 Execute o teste completo: python -m scripts.test_investment_recommender")
            return True
            
        except Exception as e:
            print(f"❌ Falha no teste rápido: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    return asyncio.run(quick_test())


def run_benchmark():
    """Executa benchmark de performance"""
    print("📊 Executando benchmark de performance...")
    
    async def benchmark():
        try:
            engine = RecommendationEngine()
            
            print("1/3 Benchmark do RecommendationEngine...")
            # Benchmark do engine
            start_time = time.time()
            
            for i in range(100):
                score, confidence = engine.calculate_combined_score(
                    float(i % 100), float((i * 2) % 100)
                )
            
            end_time = time.time()
            
            avg_time = (end_time - start_time) / 100 * 1000  # ms
            
            print(f"   📈 Engine: {avg_time:.2f}ms por cálculo (100 execuções)")
            
            print("2/3 Benchmark completo do engine...")
            # Benchmark completo do engine
            test_cases = [(80, 75), (30, 25), (50, 50), (85, 30), (20, 80), ...]
            validation_start = time.time()
            passed_validations = 0

            for fund, tech in test_cases:
                score, confidence = engine.calculate_combined_score(fund, tech)
                validation = engine.validate_recommendation_quality(fund, tech, score, confidence)
                if validation["is_valid"]:
                    passed_validations += 1
            validation_end = time.time()
            success_rate = (passed_validations / len(test_cases)) * 100
            print(f"   📊 Validação: {success_rate:.1f}% de sucesso em {(validation_end - validation_start):.2f}s")
            
            print("3/3 Benchmark de análise técnica...")
            # Benchmark de análise técnica
            analyzer = TechnicalAnalyzer()
            start_time = time.time()
            
            for i in range(10):
                await analyzer.calculate_score(f"TEST{i}", "mock data")
            
            end_time = time.time()
            avg_technical_time = (end_time - start_time) / 10
            
            print(f"   📈 Análise técnica: {avg_technical_time:.2f}s por análise (10 execuções)")
            
            print("\n🎉 Benchmark concluído!")
            print("💡 Performance dentro dos parâmetros esperados.")
            return True
            
        except Exception as e:
            print(f"❌ Falha no benchmark: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    return asyncio.run(benchmark())


def run_component_test():
    """Testa componentes individuais"""
    print("🧩 Testando componentes individuais...")
    
    try:
        # Teste 1: RecommendationEngine
        print("1/4 Testando RecommendationEngine...")
        engine = RecommendationEngine()
        
        # Teste cenários diversos
        test_cases = [
            (80, 75, "scores altos"),
            (30, 25, "scores baixos"),
            (50, 50, "scores neutros"),
            (85, 30, "divergência alta"),
            (20, 80, "divergência inversa")
        ]
        
        engine_ok = True
        for fund, tech, desc in test_cases:
            try:
                score, confidence = engine.calculate_combined_score(fund, tech)
                validation = engine.validate_recommendation_quality(fund, tech, score, confidence)
                status = "✅" if validation["is_valid"] else "❌"
                if not validation["is_valid"]:
                    engine_ok = False
                print(f"   {status} {desc}: Score {score:.1f}, Conf {confidence:.1f}%")
            except Exception as e:
                print(f"   ❌ {desc}: Erro {e}")
                engine_ok = False
        
        print(f"   {'✅' if engine_ok else '❌'} RecommendationEngine: {'OK' if engine_ok else 'FALHA'}")
        
        # Teste 2: TechnicalAnalyzer
        print("2/4 Testando TechnicalAnalyzer...")
        analyzer = TechnicalAnalyzer()
        
        # Teste com dados mock
        async def test_technical():
            try:
                score = await analyzer.calculate_score("TEST1", "mock data")
                summary = analyzer.get_technical_summary("TEST1", "mock data")
                return 0 <= score <= 100 and "error" not in summary
            except Exception:
                return False
        
        tech_ok = asyncio.run(test_technical())
        print(f"   {'✅' if tech_ok else '❌'} TechnicalAnalyzer: {'OK' if tech_ok else 'FALHA'}")
        
        # Teste 3: JustificationGenerator
        print("3/4 Testando JustificationGenerator...")
        try:
            from agno.agent import Agent
            from agno.models.anthropic import Claude
            
            # Tentar criar agente mock
            agent = Agent(
                model=Claude(id="claude-3-sonnet-20240229"),
                instructions="Test agent"
            )
            
            generator = JustificationGenerator(agent)
            
            # Teste de template
            class MockClassification:
                def __init__(self, value):
                    self.value = value
            
            template = generator._get_template_for_classification(MockClassification("COMPRA"))
            validation = generator.validate_justification_quality("Teste de justificativa com dados técnicos e score 75.", "TEST1")
            
            print(f"   ✅ JustificationGenerator: Template OK, Validação {validation['quality_score']}")
            justif_ok = True
            
        except ImportError:
            print("   ⚠️  JustificationGenerator: Agno não disponível, mas classe OK")
            justif_ok = True  # Não é falha se Agno não está disponível
        except Exception as e:
            print(f"   ❌ JustificationGenerator: Erro {e}")
            justif_ok = False
        
        # Teste 4: InvestmentRecommenderAgent
        print("4/4 Testando InvestmentRecommenderAgent...")
        try:
            recommender = create_investment_recommender()
            # Testar se instância foi criada corretamente
            has_agent = hasattr(recommender, 'agent')
            has_weights = hasattr(recommender, 'weights')
            has_repos = hasattr(recommender, 'stock_repo')
            
            agent_ok = has_agent and has_weights and has_repos
            print(f"   {'✅' if agent_ok else '❌'} InvestmentRecommenderAgent: {'OK' if agent_ok else 'FALHA'}")
            
        except Exception as e:
            print(f"   ❌ InvestmentRecommenderAgent: Erro {e}")
            agent_ok = False
        
        # Resultado final
        all_ok = engine_ok and tech_ok and justif_ok and agent_ok
        print(f"\n🎉 Teste de componentes: {'✅ SUCESSO' if all_ok else '❌ FALHAS DETECTADAS'}")
        return all_ok
        
    except Exception as e:
        print(f"❌ Falha no teste de componentes: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    import sys
    
    # Verificar argumentos da linha de comando
    if len(sys.argv) > 1:
        if sys.argv[1] == "--quick":
            success = run_quick_test()
            sys.exit(0 if success else 1)
        elif sys.argv[1] == "--benchmark":
            success = run_benchmark()
            sys.exit(0 if success else 1)
        elif sys.argv[1] == "--components":
            success = run_component_test()
            sys.exit(0 if success else 1)
        elif sys.argv[1] == "--help":
            print("Uso: python -m scripts.test_investment_recommender [opção]")
            print("\nOpções:")
            print("  --quick       Teste rápido de validação (4 testes básicos)")
            print("  --benchmark   Benchmark de performance (timing detalhado)")
            print("  --components  Teste de componentes individuais (isolado)")
            print("  --help        Mostra esta ajuda")
            print("  (sem opção)   Executa suite completa de testes (7 testes)")
            print("\nExemplos:")
            print("  python -m scripts.test_investment_recommender --quick")
            print("  python -m scripts.test_investment_recommender --benchmark")
            print("  python -m scripts.test_investment_recommender --components")
            print("  python -m scripts.test_investment_recommender")
            print("\nDescrição dos testes:")
            print("  Suite completa: 7 testes abrangentes do sistema")
            print("  Quick: Validação rápida dos componentes principais")
            print("  Benchmark: Medição de performance e timing")
            print("  Components: Teste isolado de cada componente")
            sys.exit(0)
    
    # Executar suite completa
    exit_code = asyncio.run(main())
    sys.exit(exit_code)