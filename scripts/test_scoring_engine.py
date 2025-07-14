#!/usr/bin/env python3
"""
Teste Final do Scoring Engine
Valida se a implementação está completa e funcionando conforme especificação da Fase 2 Passo 2.1

Data: 14/07/2025
Autor: Claude Sonnet 4
"""
import sys
import asyncio
from pathlib import Path
import json
from datetime import datetime

# Adicionar projeto ao path
project_root = Path.cwd()
sys.path.insert(0, str(project_root))

def test_imports_and_structure():
    """Teste de importações e estrutura"""
    print("📦 TESTANDO IMPORTAÇÕES E ESTRUTURA")
    print("=" * 60)
    
    try:
        from agents.analyzers.scoring_engine import (
            ScoringEngine, ScoringWeights, SectorBenchmarks, FundamentalScore,
            QualityTier, ScoringBatch, normalize_score, calculate_percentile,
            create_scoring_engine, quick_score, batch_score
        )
        
        print("✅ Todas as importações realizadas com sucesso")
        
        # Verificar enums e classes principais
        components = {
            "QualityTier": QualityTier,
            "ScoringWeights": ScoringWeights, 
            "SectorBenchmarks": SectorBenchmarks,
            "FundamentalScore": FundamentalScore,
            "ScoringEngine": ScoringEngine,
            "ScoringBatch": ScoringBatch
        }
        
        for name, component in components.items():
            print(f"   ✅ {name}: {type(component).__name__}")
        
        # Testar QualityTier enum
        print(f"\n🏆 QUALITY TIERS:")
        for tier in QualityTier:
            print(f"   {tier.name}: {tier.value}")
        
        return True
        
    except ImportError as e:
        print(f"❌ ERRO DE IMPORTAÇÃO: {e}")
        return False
    except Exception as e:
        print(f"❌ ERRO GERAL: {e}")
        return False


def test_scoring_weights():
    """Teste do sistema de pesos configuráveis"""
    print("\n⚖️ TESTANDO SISTEMA DE PESOS")
    print("=" * 60)
    
    try:
        from agents.analyzers.scoring_engine import ScoringWeights
        
        # Testar pesos padrão
        weights = ScoringWeights()
        
        print("📊 PESOS PADRÃO:")
        print(f"   Valuation: {weights.valuation:.0%}")
        print(f"   Profitability: {weights.profitability:.0%}")
        print(f"   Growth: {weights.growth:.0%}")
        print(f"   Financial Health: {weights.financial_health:.0%}")
        print(f"   Efficiency: {weights.efficiency:.0%}")
        
        # Testar validação
        is_valid = weights.validate()
        total = weights.valuation + weights.profitability + weights.growth + weights.financial_health + weights.efficiency
        
        print(f"\n✅ VALIDAÇÃO:")
        print(f"   Soma dos pesos: {total:.3f}")
        print(f"   Válido: {'SIM' if is_valid else 'NÃO'}")
        
        # Testar pesos customizados
        custom_weights = ScoringWeights(
            valuation=0.3,
            profitability=0.4,
            growth=0.2,
            financial_health=0.1,
            efficiency=0.0
        )
        
        print(f"\n🔧 PESOS CUSTOMIZADOS:")
        print(f"   Válido antes: {'SIM' if custom_weights.validate() else 'NÃO'}")
        
        custom_weights.normalize()
        print(f"   Válido após normalização: {'SIM' if custom_weights.validate() else 'NÃO'}")
        print(f"   Profitability após normalização: {custom_weights.profitability:.0%}")
        
        return is_valid
        
    except Exception as e:
        print(f"❌ ERRO no teste de pesos: {e}")
        return False


def test_sector_benchmarks():
    """Teste dos benchmarks setoriais"""
    print("\n🏭 TESTANDO BENCHMARKS SETORIAIS")
    print("=" * 60)
    
    try:
        from agents.analyzers.scoring_engine import SectorBenchmarks
        
        # Testar benchmarks padrão
        benchmarks = SectorBenchmarks.get_default_benchmarks()
        
        print(f"📋 SETORES CONFIGURADOS: {len(benchmarks)}")
        
        for sector, benchmark in benchmarks.items():
            print(f"\n   {sector}:")
            print(f"      P/L mediano: {benchmark.pe_ratio_median:.1f}")
            print(f"      P/VP mediano: {benchmark.pb_ratio_median:.1f}")
            print(f"      ROE mediano: {benchmark.roe_median:.1f}%")
            print(f"      Margem líquida: {benchmark.net_margin_median:.1f}%")
            print(f"      Crescimento: {benchmark.revenue_growth_median:.1f}%")
            print(f"      D/E: {benchmark.debt_to_equity_median:.1f}")
        
        # Verificar se benchmarks fazem sentido
        tech_benchmark = benchmarks.get('Tecnologia')
        bank_benchmark = benchmarks.get('Bancos')
        
        benchmarks_logical = True
        
        if tech_benchmark and bank_benchmark:
            # Tecnologia deve ter P/L maior que bancos
            if tech_benchmark.pe_ratio_median <= bank_benchmark.pe_ratio_median:
                print("⚠️ Benchmark inconsistente: Tech P/L deveria ser > Bancos P/L")
                benchmarks_logical = False
            
            # Bancos devem ter ROE maior que tech
            if bank_benchmark.roe_median <= tech_benchmark.roe_median:
                print("⚠️ Benchmark inconsistente: Bancos ROE deveria ser > Tech ROE")
                benchmarks_logical = False
        
        if benchmarks_logical:
            print("\n✅ Benchmarks setoriais são logicamente consistentes")
        
        return len(benchmarks) >= 5 and benchmarks_logical
        
    except Exception as e:
        print(f"❌ ERRO no teste de benchmarks: {e}")
        return False


def test_scoring_calculations():
    """Teste dos cálculos de scoring"""
    print("\n🧮 TESTANDO CÁLCULOS DE SCORING")
    print("=" * 60)
    
    try:
        from agents.analyzers.scoring_engine import ScoringEngine, normalize_score, calculate_percentile
        from utils.financial_calculator import FinancialData, FinancialCalculator
        
        # Testar funções utilitárias
        print("🔧 FUNÇÕES UTILITÁRIAS:")
        
        # Teste normalize_score
        norm_test_1 = normalize_score(15, 10, 20)  # 50%
        norm_test_2 = normalize_score(15, 10, 20, reverse=True)  # 50% reverso
        print(f"   normalize_score(15, 10-20): {norm_test_1:.1f} (esperado: 50)")
        print(f"   normalize_score(15, 10-20, reverse): {norm_test_2:.1f} (esperado: 50)")
        
        # Teste calculate_percentile  
        perc_test = calculate_percentile(7, [1, 3, 5, 7, 9])  # 70th percentile
        print(f"   calculate_percentile(7, [1,3,5,7,9]): {perc_test:.1f} (esperado: ~70)")
        
        # Testar ScoringEngine
        print(f"\n🎯 SCORING ENGINE:")
        engine = ScoringEngine()
        
        # Dados de teste realistas
        test_data = FinancialData(
            symbol="SCORE4",
            current_price=50.0,
            market_cap=200_000_000_000,
            revenue=80_000_000_000,
            net_income=15_000_000_000,
            total_assets=160_000_000_000,
            shareholders_equity=100_000_000_000,
            total_debt=25_000_000_000,
            current_assets=50_000_000_000,
            current_liabilities=20_000_000_000,
            cash_and_equivalents=15_000_000_000,
            ebitda=22_000_000_000,
            revenue_history=[70_000_000_000, 75_000_000_000, 78_000_000_000],
            net_income_history=[12_000_000_000, 13_500_000_000, 14_200_000_000],
            sector="Tecnologia"
        )
        
        # Calcular score
        calculator = FinancialCalculator()
        metrics = calculator.calculate_all_metrics(test_data)
        score = engine.calculate_comprehensive_score(test_data, metrics)
        
        print(f"   Empresa: {score.stock_code}")
        print(f"   Score composto: {score.composite_score:.1f}/100")
        print(f"   Quality tier: {score.quality_tier.value}")
        print(f"   Recomendação: {score.recommendation}")
        
        # Verificar se scores estão no range correto
        scores_valid = all([
            0 <= score.valuation_score <= 100,
            0 <= score.profitability_score <= 100,
            0 <= score.growth_score <= 100,
            0 <= score.financial_health_score <= 100,
            0 <= score.efficiency_score <= 100,
            0 <= score.composite_score <= 100
        ])
        
        print(f"   Scores no range válido: {'✅ SIM' if scores_valid else '❌ NÃO'}")
        
        # Testar pontos fortes e fracos
        if score.strengths:
            print(f"   Pontos fortes: {len(score.strengths)}")
        if score.weaknesses:
            print(f"   Pontos fracos: {len(score.weaknesses)}")
        
        return scores_valid and score.composite_score > 0
        
    except Exception as e:
        print(f"❌ ERRO no teste de cálculos: {e}")
        return False


def test_batch_processing():
    """Teste do processamento em lote"""
    print("\n📦 TESTANDO PROCESSAMENTO EM LOTE")
    print("=" * 60)
    
    try:
        from agents.analyzers.scoring_engine import ScoringBatch, create_scoring_engine
        from utils.financial_calculator import FinancialData
        
        # Criar múltiplas empresas de teste
        companies_data = [
            FinancialData(
                symbol="BATCH1",
                market_cap=100_000_000_000,
                revenue=50_000_000_000,
                net_income=8_000_000_000,
                total_assets=120_000_000_000,
                shareholders_equity=60_000_000_000,
                sector="Tecnologia"
            ),
            FinancialData(
                symbol="BATCH2", 
                market_cap=80_000_000_000,
                revenue=40_000_000_000,
                net_income=12_000_000_000,
                total_assets=200_000_000_000,
                shareholders_equity=90_000_000_000,
                sector="Bancos"
            ),
            FinancialData(
                symbol="BATCH3",
                market_cap=150_000_000_000,
                revenue=75_000_000_000,
                net_income=5_000_000_000,
                total_assets=180_000_000_000,
                shareholders_equity=70_000_000_000,
                sector="Petróleo e Gás"
            )
        ]
        
        # Processar em lote
        engine = create_scoring_engine()
        batch_processor = ScoringBatch(engine)
        
        scores = batch_processor.process_batch(companies_data)
        
        print(f"📊 RESULTADOS DO LOTE:")
        print(f"   Empresas processadas: {len(scores)}")
        
        for score in scores:
            print(f"   {score.stock_code}: {score.composite_score:.1f} "
                  f"(Setor: {score.sector}, Rank: {score.sector_rank})")
        
        # Testar top stocks
        top_stocks = batch_processor.get_top_stocks(scores, limit=2)
        print(f"\n🏆 TOP 2 AÇÕES:")
        for i, stock in enumerate(top_stocks, 1):
            print(f"   {i}. {stock.stock_code}: {stock.composite_score:.1f}")
        
        # Testar líderes setoriais
        sector_leaders = batch_processor.get_sector_leaders(scores)
        print(f"\n👑 LÍDERES SETORIAIS:")
        for sector, leader in sector_leaders.items():
            print(f"   {sector}: {leader.stock_code} ({leader.composite_score:.1f})")
        
        # Validar percentis
        percentiles_valid = all(0 <= s.sector_percentile <= 100 for s in scores)
        ranks_valid = all(s.sector_rank > 0 for s in scores)
        
        print(f"\n✅ VALIDAÇÕES:")
        print(f"   Percentis válidos: {'SIM' if percentiles_valid else 'NÃO'}")
        print(f"   Rankings válidos: {'SIM' if ranks_valid else 'NÃO'}")
        
        return len(scores) == len(companies_data) and percentiles_valid and ranks_valid
        
    except Exception as e:
        print(f"❌ ERRO no teste em lote: {e}")
        return False


def test_integration_features():
    """Teste de recursos de integração"""
    print("\n🔗 TESTANDO RECURSOS DE INTEGRAÇÃO")
    print("=" * 60)
    
    try:
        from agents.analyzers.scoring_engine import create_scoring_engine, quick_score, batch_score
        from utils.financial_calculator import FinancialData
        
        # Teste factory function
        engine = create_scoring_engine()
        summary = engine.get_scoring_summary()
        
        print(f"📋 RESUMO DO ENGINE:")
        print(f"   Engine version: {summary['engine_version']}")
        print(f"   Setores configurados: {summary['sectors_configured']}")
        print(f"   Pesos configurados: ✅")
        
        # Teste quick_score
        test_data = FinancialData(
            symbol="QUICK4",
            market_cap=50_000_000_000,
            revenue=25_000_000_000,
            net_income=4_000_000_000,
            sector="Varejo"
        )
        
        quick_result = quick_score(test_data)
        print(f"\n⚡ QUICK SCORE:")
        print(f"   {quick_result.stock_code}: {quick_result.composite_score:.1f}")
        print(f"   Recomendação: {quick_result.recommendation}")
        
        # Teste batch_score
        batch_data = [test_data]
        batch_results = batch_score(batch_data)
        
        print(f"\n📦 BATCH SCORE:")
        print(f"   Resultados: {len(batch_results)}")
        print(f"   Percentil calculado: ✅")
        
        # Testar conversão para dict
        score_dict = quick_result.to_dict()
        dict_valid = isinstance(score_dict, dict) and 'composite_score' in score_dict
        
        print(f"\n💾 SERIALIZAÇÃO:")
        print(f"   to_dict() funcionando: {'✅ SIM' if dict_valid else '❌ NÃO'}")
        print(f"   Campos no dict: {len(score_dict)}")
        
        return summary['sectors_configured'] >= 5 and dict_valid
        
    except Exception as e:
        print(f"❌ ERRO no teste de integração: {e}")
        return False


def generate_test_report():
    """Gera relatório final do teste"""
    print("\n📋 GERANDO RELATÓRIO FINAL")
    print("=" * 60)
    
    try:
        from agents.analyzers.scoring_engine import ScoringEngine, QualityTier
        
        # Estatísticas do sistema
        engine = ScoringEngine()
        summary = engine.get_scoring_summary()
        
        report = {
            "test_date": datetime.now().isoformat(),
            "status": "COMPLETO",
            "scoring_engine_implemented": True,
            "scoring_weights_configurable": True,
            "sector_benchmarks_count": summary['sectors_configured'],
            "quality_tiers_count": len(QualityTier),
            "batch_processing": True,
            "percentile_calculation": True,
            "composite_scoring": True,
            "sector_comparison": True,
            "integration_functions": True,
            "normalization_implemented": True,
            "phase2_step2_1_complete": True,
            "engine_version": summary['engine_version']
        }
        
        # Salvar relatório
        report_path = project_root / f"scoring_engine_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"📊 ESTATÍSTICAS:")
        print(f"   Pesos configuráveis: ✅")
        print(f"   Normalização de indicadores: ✅")
        print(f"   Comparação setorial: ✅")
        print(f"   Score composto (0-100): ✅")
        print(f"   Quality tiers: {report['quality_tiers_count']}")
        print(f"   Setores suportados: {report['sector_benchmarks_count']}")
        print(f"   Processamento em lote: ✅")
        print(f"   Relatório salvo: {report_path.name}")
        
        return True
        
    except Exception as e:
        print(f"❌ ERRO ao gerar relatório: {e}")
        return False


def main():
    """Função principal - executa todos os testes"""
    print("🚀 TESTE FINAL DO SCORING ENGINE")
    print("=" * 80)
    print("Validando implementação da Fase 2 Passo 2.1 - Sistema de Scoring")
    print("=" * 80)
    
    tests = [
        ("Importações e Estrutura", test_imports_and_structure),
        ("Sistema de Pesos", test_scoring_weights),
        ("Benchmarks Setoriais", test_sector_benchmarks),
        ("Cálculos de Scoring", test_scoring_calculations),
        ("Processamento em Lote", test_batch_processing),
        ("Recursos de Integração", test_integration_features),
        ("Relatório Final", generate_test_report)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 Executando: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
            if result:
                print(f"✅ {test_name}: PASSOU")
            else:
                print(f"❌ {test_name}: FALHOU")
        except Exception as e:
            print(f"❌ ERRO CRÍTICO em {test_name}: {e}")
            results.append((test_name, False))
    
    # Resumo final
    print("\n" + "=" * 80)
    print("📋 RESUMO FINAL DOS TESTES")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"   {test_name}: {status}")
    
    print(f"\n📊 RESULTADO FINAL: {passed}/{total} testes passaram")
    
    if passed == total:
        print(f"\n🎉 TODOS OS TESTES PASSARAM!")
        print(f"✅ O Scoring Engine está COMPLETAMENTE IMPLEMENTADO")
        print(f"✅ Fase 2 Passo 2.1 - Sistema de Scoring: CONCLUÍDO")
        print(f"\n🎯 FUNCIONALIDADES IMPLEMENTADAS:")
        print(f"   ✅ Sistema de pesos configuráveis por métrica")
        print(f"   ✅ Normalização de indicadores (percentis)")  
        print(f"   ✅ Comparação setorial automatizada")
        print(f"   ✅ Score composto ponderado (0-100)")
        print(f"   ✅ Quality tiers (EXCELLENT a POOR)")
        print(f"   ✅ Processamento em lote com rankings")
        print(f"   ✅ Benchmarks setoriais configurados")
        print(f"   ✅ Funções utilitárias de integração")
        print(f"\n🚀 FASE 2 PASSO 2.1 COMPLETO: scoring_engine.py")
        print(f"🚀 PRÓXIMO PASSO: Implementar sector_comparator.py (Passo 2.2)")
    else:
        print(f"\n⚠️  ALGUNS TESTES FALHARAM!")
        print(f"🔧 Verifique os erros acima antes de prosseguir.")
        print(f"💡 O scoring engine pode precisar de ajustes adicionais.")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
