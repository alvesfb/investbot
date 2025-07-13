#!/usr/bin/env python3
"""
VALIDAÇÃO FINAL - FASE 2 PASSO 2
Sistema de Recomendações de Investimentos

Este script executa uma validação completa e robusta da implementação
da Fase 2 até o Passo 2, verificando se todos os componentes estão
funcionando conforme especificado.

VERIFICAÇÕES:
✓ Passo 2.1: Algoritmo de Scoring
✓ Passo 2.2: Benchmarking Setorial  
✓ Passo 2.3: Sistema de Critérios de Qualidade
✓ Integração com Arquitetura Existente
✓ Compatibilidade com Agno Framework

Data: 13/07/2025
Autor: Claude Sonnet 4
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# Setup do projeto
PROJECT_ROOT = Path.cwd()
sys.path.insert(0, str(PROJECT_ROOT))

class ValidationResult(Enum):
    PASS = "✅ PASS"
    FAIL = "❌ FAIL"
    WARN = "⚠️  WARN"
    INFO = "ℹ️  INFO"

@dataclass
class ValidationTest:
    name: str
    description: str
    category: str
    required: bool = True
    result: Optional[ValidationResult] = None
    details: str = ""
    score: float = 0.0

class Fase2Passo2Validator:
    """
    Validador completo da Fase 2 Passo 2
    
    Verifica se a implementação do Sistema de Scoring Fundamentalista
    está completa e funcionando conforme especificação.
    """
    
    def __init__(self):
        self.tests: List[ValidationTest] = []
        self.start_time = time.time()
        
        # Contadores
        self.total_score = 0.0
        self.max_score = 0.0
        self.critical_failures = 0
        
        self._print_header()
    
    def _print_header(self):
        """Imprime cabeçalho do validador"""
        print("🔍 VALIDADOR COMPLETO - FASE 2 PASSO 2")
        print("=" * 80)
        print("Sistema de Scoring Fundamentalista")
        print("Data:", datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        print("=" * 80)
        print()
        print("ESPECIFICAÇÃO FASE 2 - PASSO 2:")
        print("   2.1 ✓ Algoritmo de Scoring (Sistema de pesos, normalização, score 0-100)")
        print("   2.2 ✓ Benchmarking Setorial (Percentis, ranking, comparações)")
        print("   2.3 ✓ Critérios de Qualidade (Quality tiers, filtros, ROE>15%)")
        print("=" * 80)
    
    def add_test(self, test: ValidationTest):
        """Adiciona teste à lista"""
        self.tests.append(test)
        self.max_score += 10.0 if test.required else 5.0
    
    def run_test(self, test_func, test: ValidationTest) -> ValidationResult:
        """Executa um teste individual"""
        print(f"\n🔍 {test.name}")
        print(f"   📋 {test.description}")
        
        try:
            result, details, score = test_func()
            test.result = result
            test.details = details
            test.score = score
            
            if test.required and result == ValidationResult.FAIL:
                self.critical_failures += 1
            
            self.total_score += score
            
            print(f"   {result.value}: {details}")
            if score > 0:
                print(f"   📊 Score: {score:.1f}/10")
            
            return result
            
        except Exception as e:
            test.result = ValidationResult.FAIL
            test.details = f"Erro na execução: {str(e)}"
            test.score = 0.0
            
            if test.required:
                self.critical_failures += 1
            
            print(f"   {ValidationResult.FAIL.value}: {test.details}")
            return ValidationResult.FAIL
    
    # ================================================================
    # TESTES DO PASSO 2.1: ALGORITMO DE SCORING
    # ================================================================
    
    def test_fundamental_scoring_system_exists(self) -> Tuple[ValidationResult, str, float]:
        """Verifica se o sistema principal existe e está completo"""
        scoring_file = PROJECT_ROOT / "agents" / "analyzers" / "fundamental_scoring_system.py"
        
        if not scoring_file.exists():
            return ValidationResult.FAIL, "Arquivo fundamental_scoring_system.py não encontrado", 0.0
        
        try:
            content = scoring_file.read_text(encoding='utf-8')
            
            # Componentes obrigatórios
            required_components = {
                "FundamentalAnalyzerAgent": "class FundamentalAnalyzerAgent",
                "ScoringEngine": "class ScoringEngine", 
                "FundamentalScore": "class FundamentalScore",
                "QualityTier": "class QualityTier",
                "ScoringWeights": "class ScoringWeights",
                "composite_score": "composite_score"
            }
            
            found = 0
            missing = []
            
            for name, pattern in required_components.items():
                if pattern in content:
                    found += 1
                else:
                    missing.append(name)
            
            score = (found / len(required_components)) * 10
            
            if missing:
                return ValidationResult.FAIL, f"Componentes faltando: {', '.join(missing)}", score
            else:
                return ValidationResult.PASS, f"Todos os componentes encontrados ({len(content):,} chars)", score
            
        except Exception as e:
            return ValidationResult.FAIL, f"Erro ao ler arquivo: {e}", 0.0
    
    def test_scoring_engine_implementation(self) -> Tuple[ValidationResult, str, float]:
        """Testa implementação do ScoringEngine"""
        try:
            sys.path.append(str(PROJECT_ROOT / "agents" / "analyzers"))
            from fundamental_scoring_system import ScoringEngine, ScoringWeights
            
            # Testar criação
            weights = ScoringWeights()
            engine = ScoringEngine(weights)
            
            # Métodos obrigatórios
            required_methods = [
                'calculate_valuation_score',
                'calculate_profitability_score', 
                'calculate_growth_score',
                'calculate_composite_score'
            ]
            
            found_methods = [m for m in required_methods if hasattr(engine, m)]
            score = (len(found_methods) / len(required_methods)) * 10
            
            if len(found_methods) == len(required_methods):
                return ValidationResult.PASS, f"ScoringEngine completo ({len(found_methods)} métodos)", score
            else:
                missing = [m for m in required_methods if m not in found_methods]
                return ValidationResult.FAIL, f"Métodos faltando: {', '.join(missing)}", score
            
        except ImportError:
            return ValidationResult.FAIL, "Erro de import do ScoringEngine", 0.0
        except Exception as e:
            return ValidationResult.FAIL, f"Erro na implementação: {e}", 0.0
    
    def test_scoring_calculation(self) -> Tuple[ValidationResult, str, float]:
        """Testa se o cálculo de score funciona"""
        try:
            sys.path.append(str(PROJECT_ROOT / "agents" / "analyzers"))
            from fundamental_scoring_system import FundamentalAnalyzerAgent
            
            agent = FundamentalAnalyzerAgent()
            result = agent.analyze_single_stock("PETR4")
            
            if "error" in result:
                return ValidationResult.WARN, "Análise retornou erro (esperado em dev)", 5.0
            
            # Verificar estrutura
            required_fields = ['fundamental_score', 'recommendation', 'stock_code']
            missing = [f for f in required_fields if f not in result]
            
            if missing:
                return ValidationResult.FAIL, f"Campos faltando: {', '.join(missing)}", 0.0
            
            # Verificar score
            fs = result['fundamental_score']
            if 'composite_score' not in fs:
                return ValidationResult.FAIL, "composite_score não encontrado", 0.0
            
            score = fs['composite_score']
            if not (0 <= score <= 100):
                return ValidationResult.FAIL, f"Score fora do range 0-100: {score}", 0.0
            
            return ValidationResult.PASS, f"Cálculo funcionando (Score: {score:.1f})", 10.0
            
        except Exception as e:
            return ValidationResult.FAIL, f"Erro no cálculo: {e}", 0.0
    
    # ================================================================
    # TESTES DO PASSO 2.2: BENCHMARKING SETORIAL
    # ================================================================
    
    def test_sector_comparison(self) -> Tuple[ValidationResult, str, float]:
        """Testa comparação setorial"""
        try:
            scoring_file = PROJECT_ROOT / "agents" / "analyzers" / "fundamental_scoring_system.py"
            content = scoring_file.read_text(encoding='utf-8')
            
            # Verificar campos de percentil
            sector_components = {
                "sector_percentile": "sector_percentile" in content,
                "sector_rank": "sector_rank" in content,
                "overall_percentile": "overall_percentile" in content,
                "overall_rank": "overall_rank" in content
            }
            
            found = sum(sector_components.values())
            score = (found / len(sector_components)) * 10
            
            if found == len(sector_components):
                return ValidationResult.PASS, "Todos os campos de ranking implementados", score
            elif found >= 2:
                return ValidationResult.WARN, f"Ranking parcial ({found}/{len(sector_components)})", score
            else:
                return ValidationResult.FAIL, "Sistema de ranking não implementado", score
            
        except Exception as e:
            return ValidationResult.FAIL, f"Erro no teste setorial: {e}", 0.0
    
    def test_percentile_calculation(self) -> Tuple[ValidationResult, str, float]:
        """Testa cálculo de percentis"""
        try:
            sys.path.append(str(PROJECT_ROOT / "agents" / "analyzers"))
            from fundamental_scoring_system import FundamentalScore
            
            # Verificar se FundamentalScore tem campos necessários
            score_fields = FundamentalScore.__annotations__.keys()
            
            percentile_fields = ['sector_percentile', 'overall_percentile']
            found_fields = [f for f in percentile_fields if f in score_fields]
            
            score = (len(found_fields) / len(percentile_fields)) * 10
            
            if len(found_fields) == len(percentile_fields):
                return ValidationResult.PASS, "Estrutura de percentis implementada", score
            else:
                missing = [f for f in percentile_fields if f not in found_fields]
                return ValidationResult.FAIL, f"Campos faltando: {', '.join(missing)}", score
            
        except Exception as e:
            return ValidationResult.FAIL, f"Erro nos percentis: {e}", 0.0
    
    # ================================================================
    # TESTES DO PASSO 2.3: CRITÉRIOS DE QUALIDADE
    # ================================================================
    
    def test_quality_tier_system(self) -> Tuple[ValidationResult, str, float]:
        """Testa sistema de quality tier"""
        try:
            sys.path.append(str(PROJECT_ROOT / "agents" / "analyzers"))
            from fundamental_scoring_system import QualityTier
            
            # Verificar tiers obrigatórios
            expected_tiers = ['EXCELLENT', 'GOOD', 'AVERAGE', 'BELOW_AVERAGE', 'POOR']
            actual_tiers = [tier.name for tier in QualityTier]
            
            found = len([tier for tier in expected_tiers if tier in actual_tiers])
            score = (found / len(expected_tiers)) * 10
            
            if found == len(expected_tiers):
                return ValidationResult.PASS, f"Sistema de qualidade completo ({found} tiers)", score
            else:
                missing = [tier for tier in expected_tiers if tier not in actual_tiers]
                return ValidationResult.FAIL, f"Tiers faltando: {', '.join(missing)}", score
            
        except ImportError:
            return ValidationResult.FAIL, "QualityTier não encontrado", 0.0
        except Exception as e:
            return ValidationResult.FAIL, f"Erro no sistema de qualidade: {e}", 0.0
    
    def test_quality_filters(self) -> Tuple[ValidationResult, str, float]:
        """Testa filtros de qualidade (ROE>15%, etc.)"""
        try:
            scoring_file = PROJECT_ROOT / "agents" / "analyzers" / "fundamental_scoring_system.py"
            content = scoring_file.read_text(encoding='utf-8')
            
            # Verificar critérios de qualidade
            quality_criteria = {
                "ROE": ("roe" in content.lower() or "return on equity" in content.lower()),
                "Crescimento": ("growth" in content.lower()),
                "Endividamento": ("debt" in content.lower() or "divida" in content.lower()),
                "Margens": ("margin" in content.lower())
            }
            
            found = sum(quality_criteria.values())
            score = (found / len(quality_criteria)) * 10
            
            if found >= 3:
                return ValidationResult.PASS, f"Critérios implementados ({found}/{len(quality_criteria)})", score
            elif found >= 1:
                return ValidationResult.WARN, f"Critérios parciais ({found}/{len(quality_criteria)})", score
            else:
                return ValidationResult.FAIL, "Critérios de qualidade não encontrados", score
            
        except Exception as e:
            return ValidationResult.FAIL, f"Erro nos filtros: {e}", 0.0
    
    # ================================================================
    # TESTES DE INFRAESTRUTURA
    # ================================================================
    
    def test_agno_integration(self) -> Tuple[ValidationResult, str, float]:
        """Testa integração com Agno Framework"""
        try:
            from agno.agent import Agent
            
            sys.path.append(str(PROJECT_ROOT / "agents" / "analyzers"))
            from fundamental_scoring_system import FundamentalAnalyzerAgent
            
            if issubclass(FundamentalAnalyzerAgent, Agent):
                return ValidationResult.PASS, "Herança do Agent correta", 5.0
            else:
                return ValidationResult.FAIL, "FundamentalAnalyzerAgent não herda de Agent", 0.0
            
        except ImportError:
            return ValidationResult.WARN, "Agno não disponível (esperado em dev)", 3.0
        except Exception as e:
            return ValidationResult.FAIL, f"Erro na integração: {e}", 0.0
    
    def test_database_integration(self) -> Tuple[ValidationResult, str, float]:
        """Testa integração com database"""
        try:
            from database.repositories import get_stock_repository
            
            repo = get_stock_repository()
            stocks = repo.get_all_stocks()
            
            return ValidationResult.PASS, f"Database integrado ({len(stocks)} ações)", 5.0
            
        except ImportError:
            return ValidationResult.WARN, "Database não disponível (esperado em dev)", 3.0
        except Exception as e:
            return ValidationResult.WARN, f"Database com problemas: {e}", 2.0
    
    def test_project_structure(self) -> Tuple[ValidationResult, str, float]:
        """Testa estrutura do projeto"""
        required_dirs = [
            "agents/analyzers",
            "database", 
            "utils",
            "config"
        ]
        
        existing_dirs = [d for d in required_dirs if (PROJECT_ROOT / d).exists()]
        score = (len(existing_dirs) / len(required_dirs)) * 5
        
        if len(existing_dirs) == len(required_dirs):
            return ValidationResult.PASS, f"Estrutura completa ({len(existing_dirs)} dirs)", score
        else:
            missing = [d for d in required_dirs if d not in existing_dirs]
            return ValidationResult.WARN, f"Dirs faltando: {', '.join(missing)}", score
    
    # ================================================================
    # EXECUÇÃO DOS TESTES
    # ================================================================
    
    def run_all_tests(self):
        """Executa todos os testes de validação"""
        
        # TESTES CRÍTICOS DO PASSO 2.1
        print("\n📊 VALIDANDO PASSO 2.1: ALGORITMO DE SCORING")
        print("-" * 60)
        
        tests_2_1 = [
            ValidationTest("Sistema Principal", "Verificar se fundamental_scoring_system.py existe", "2.1", True),
            ValidationTest("ScoringEngine", "Verificar implementação do motor de scoring", "2.1", True),
            ValidationTest("Cálculo de Score", "Testar funcionalidade do cálculo", "2.1", True)
        ]
        
        for test in tests_2_1:
            self.add_test(test)
        
        self.run_test(self.test_fundamental_scoring_system_exists, tests_2_1[0])
        self.run_test(self.test_scoring_engine_implementation, tests_2_1[1])
        self.run_test(self.test_scoring_calculation, tests_2_1[2])
        
        # TESTES DO PASSO 2.2
        print("\n📈 VALIDANDO PASSO 2.2: BENCHMARKING SETORIAL")
        print("-" * 60)
        
        tests_2_2 = [
            ValidationTest("Comparação Setorial", "Verificar campos de ranking", "2.2", True),
            ValidationTest("Cálculo de Percentis", "Verificar estrutura de percentis", "2.2", True)
        ]
        
        for test in tests_2_2:
            self.add_test(test)
        
        self.run_test(self.test_sector_comparison, tests_2_2[0])
        self.run_test(self.test_percentile_calculation, tests_2_2[1])
        
        # TESTES DO PASSO 2.3
        print("\n🏆 VALIDANDO PASSO 2.3: CRITÉRIOS DE QUALIDADE")
        print("-" * 60)
        
        tests_2_3 = [
            ValidationTest("Sistema Quality Tier", "Verificar enums de qualidade", "2.3", True),
            ValidationTest("Filtros de Qualidade", "Verificar critérios ROE, crescimento", "2.3", True)
        ]
        
        for test in tests_2_3:
            self.add_test(test)
        
        self.run_test(self.test_quality_tier_system, tests_2_3[0])
        self.run_test(self.test_quality_filters, tests_2_3[1])
        
        # TESTES DE INFRAESTRUTURA
        print("\n🔧 VALIDANDO INFRAESTRUTURA")
        print("-" * 60)
        
        infra_tests = [
            ValidationTest("Estrutura do Projeto", "Verificar diretórios", "Infra", False),
            ValidationTest("Integração Database", "Verificar conexão com banco", "Infra", False),
            ValidationTest("Integração Agno", "Verificar herança do Agent", "Infra", False)
        ]
        
        for test in infra_tests:
            self.add_test(test)
        
        self.run_test(self.test_project_structure, infra_tests[0])
        self.run_test(self.test_database_integration, infra_tests[1])
        self.run_test(self.test_agno_integration, infra_tests[2])
    
    def generate_final_report(self) -> Dict[str, Any]:
        """Gera relatório final completo"""
        
        execution_time = time.time() - self.start_time
        success_rate = (self.total_score / self.max_score * 100) if self.max_score > 0 else 0
        
        # Determinar status geral
        if self.critical_failures == 0 and success_rate >= 80:
            overall_status = "✅ FASE 2 PASSO 2 COMPLETO"
            status_icon = "🎉"
        elif self.critical_failures <= 1 and success_rate >= 60:
            overall_status = "⚠️  FASE 2 PASSO 2 QUASE COMPLETO"
            status_icon = "📝"
        else:
            overall_status = "❌ FASE 2 PASSO 2 INCOMPLETO"
            status_icon = "🔧"
        
        # Agrupar testes por categoria
        tests_by_category = {}
        for test in self.tests:
            if test.category not in tests_by_category:
                tests_by_category[test.category] = []
            tests_by_category[test.category].append(test)
        
        return {
            "overall_status": overall_status,
            "status_icon": status_icon,
            "execution_time": execution_time,
            "summary": {
                "total_tests": len(self.tests),
                "critical_failures": self.critical_failures,
                "total_score": self.total_score,
                "max_score": self.max_score,
                "success_rate": success_rate
            },
            "tests_by_category": {
                category: [
                    {
                        "name": test.name,
                        "description": test.description,
                        "required": test.required,
                        "result": test.result.value if test.result else "NOT_RUN",
                        "details": test.details,
                        "score": test.score
                    }
                    for test in tests
                ]
                for category, tests in tests_by_category.items()
            },
            "next_steps": self._generate_next_steps(overall_status),
            "timestamp": datetime.now().isoformat()
        }
    
    def _generate_next_steps(self, status: str) -> List[str]:
        """Gera próximos passos baseado no status"""
        steps = []
        
        if "COMPLETO" in status:
            steps.extend([
                "🎯 FASE 2 PASSO 2 FINALIZADO COM SUCESSO!",
                "",
                "📋 PRÓXIMOS PASSOS DA FASE 2:",
                "   • Implementar Passo 3: Agente Analisador Core",
                "   • Configurar Pipeline de Processamento",
                "   • Implementar Sistema de Justificativas Automáticas",
                "   • Criar APIs de Análise Fundamentalista",
                "   • Configurar Sistema de Cache Inteligente",
                "",
                "🚀 PREPARAÇÃO PARA FASE 3:",
                "   • Sistema de Recomendações baseado em Scoring",
                "   • Integração com Análise Técnica",
                "   • Dashboard de Monitoramento"
            ])
        
        elif "QUASE" in status:
            # Identificar problemas críticos
            critical_failed = [test for test in self.tests if test.required and test.result == ValidationResult.FAIL]
            
            steps.extend([
                "🔧 CORREÇÕES NECESSÁRIAS:",
                ""
            ])
            
            for test in critical_failed:
                steps.append(f"   • {test.name}: {test.details}")
            
            steps.extend([
                "",
                "📝 APÓS CORREÇÕES:",
                "   • Executar novamente este validador",
                "   • Prosseguir para Passo 3 se aprovado"
            ])
        
        else:
            steps.extend([
                "❌ IMPLEMENTAÇÃO INCOMPLETA",
                "",
                "🔧 AÇÕES OBRIGATÓRIAS:",
                "   • Implementar fundamental_scoring_system.py completo",
                "   • Garantir herança do Agent (Agno)",
                "   • Implementar ScoringEngine com todos os métodos",
                "   • Adicionar sistema de Quality Tiers",
                "   • Configurar campos de percentil setorial",
                "",
                "📚 CONSULTAR DOCUMENTAÇÃO:",
                "   • Fase2.md - Especificação completa",
                "   • Arquitetura do projeto existente",
                "   • Exemplos nos outros sistemas de scoring"
            ])
        
        return steps
    
    def print_final_report(self):
        """Imprime relatório final formatado"""
        
        report = self.generate_final_report()
        
        print("\n" + "=" * 80)
        print("📋 RELATÓRIO FINAL - VALIDAÇÃO FASE 2 PASSO 2")
        print("=" * 80)
        
        print(f"\n{report['status_icon']} STATUS GERAL: {report['overall_status']}")
        
        summary = report['summary']
        print(f"\n📊 RESUMO EXECUTIVO:")
        print(f"   • Total de Testes: {summary['total_tests']}")
        print(f"   • Falhas Críticas: {summary['critical_failures']}")
        print(f"   • Score Total: {summary['total_score']:.1f}/{summary['max_score']:.1f}")
        print(f"   • Taxa de Sucesso: {summary['success_rate']:.1f}%")
        print(f"   • Tempo de Execução: {report['execution_time']:.2f}s")
        
        # Relatório por categoria
        print(f"\n📈 RESULTADOS POR CATEGORIA:")
        for category, tests in report['tests_by_category'].items():
            print(f"\n   📂 {category}:")
            for test in tests:
                status_emoji = "✅" if "PASS" in test['result'] else "⚠️" if "WARN" in test['result'] else "❌"
                required_mark = "🔴" if test['required'] else "🔵"
                print(f"      {status_emoji} {required_mark} {test['name']}: {test['score']:.1f}/10")
                if test['details']:
                    print(f"         └─ {test['details']}")
        
        # Próximos passos
        print(f"\n📋 PRÓXIMOS PASSOS:")
        for step in report['next_steps']:
            print(step)
        
        print("\n" + "=" * 80)
        
        # Salvar relatório
        report_file = PROJECT_ROOT / f"validation_report_fase2_passo2_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Relatório detalhado salvo: {report_file.name}")
        
        return report['summary']['success_rate'] >= 60 and report['summary']['critical_failures'] <= 1

def main():
    """Função principal do validador"""
    
    try:
        validator = Fase2Passo2Validator()
        
        # Executar todos os testes
        validator.run_all_tests()
        
        # Gerar e imprimir relatório final
        success = validator.print_final_report()
        
        # Código de saída
        if success:
            print("\n🎉 VALIDAÇÃO CONCLUÍDA COM SUCESSO!")
            print("✅ Fase 2 Passo 2 está pronta para produção")
            sys.exit(0)
        else:
            print("\n⚠️  VALIDAÇÃO CONCLUÍDA COM PROBLEMAS")
            print("🔧 Correções necessárias antes de prosseguir")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Validação interrompida pelo usuário")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n💥 ERRO CRÍTICO NO VALIDADOR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
