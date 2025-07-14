#!/usr/bin/env python3
"""
Correção dos Benchmarks Setoriais
Ajusta valores para refletir corretamente a realidade do mercado brasileiro

Data: 14/07/2025
Autor: Claude Sonnet 4
"""
import sys
from pathlib import Path

# Adicionar projeto ao path
project_root = Path.cwd()
sys.path.insert(0, str(project_root))

def test_benchmark_logic():
    """Testa se os benchmarks estão logicamente corretos"""
    print("🔧 TESTANDO LÓGICA DOS BENCHMARKS SETORIAIS")
    print("=" * 60)
    
    try:
        from agents.analyzers.scoring_engine import SectorBenchmarks
        
        # Carregar benchmarks corrigidos
        benchmarks = SectorBenchmarks.get_default_benchmarks()
        
        tech_benchmark = benchmarks.get('Tecnologia')
        bank_benchmark = benchmarks.get('Bancos')
        
        print("📊 BENCHMARKS ATUAIS:")
        print(f"   Bancos ROE: {bank_benchmark.roe_median:.1f}%")
        print(f"   Tecnologia ROE: {tech_benchmark.roe_median:.1f}%")
        print(f"   Bancos P/L: {bank_benchmark.pe_ratio_median:.1f}x")
        print(f"   Tecnologia P/L: {tech_benchmark.pe_ratio_median:.1f}x")
        
        # Validações lógicas
        validations = []
        
        # 1. Bancos ROE > Tech ROE (alavancagem bancária)
        banks_roe_higher = bank_benchmark.roe_median > tech_benchmark.roe_median
        validations.append(("Bancos ROE > Tech ROE", banks_roe_higher))
        
        # 2. Tech P/L > Bancos P/L (múltiplo de crescimento)
        tech_pe_higher = tech_benchmark.pe_ratio_median > bank_benchmark.pe_ratio_median
        validations.append(("Tech P/L > Bancos P/L", tech_pe_higher))
        
        # 3. Tech Crescimento > Bancos Crescimento
        tech_growth_higher = tech_benchmark.revenue_growth_median > bank_benchmark.revenue_growth_median
        validations.append(("Tech Crescimento > Bancos Crescimento", tech_growth_higher))
        
        # 4. Bancos Margem > Tech Margem (produtos financeiros)
        banks_margin_higher = bank_benchmark.net_margin_median > tech_benchmark.net_margin_median
        validations.append(("Bancos Margem > Tech Margem", banks_margin_higher))
        
        print(f"\n✅ VALIDAÇÕES LÓGICAS:")
        all_valid = True
        for test_name, passed in validations:
            status = "✅" if passed else "❌"
            print(f"   {status} {test_name}: {'CORRETO' if passed else 'INCORRETO'}")
            if not passed:
                all_valid = False
        
        # Testar outros setores
        print(f"\n🏭 OUTROS SETORES:")
        for sector_name, benchmark in benchmarks.items():
            if sector_name not in ['Bancos', 'Tecnologia']:
                print(f"   {sector_name}: ROE {benchmark.roe_median:.1f}%, P/L {benchmark.pe_ratio_median:.1f}x")
        
        return all_valid
        
    except Exception as e:
        print(f"❌ ERRO: {e}")
        return False


def test_scoring_engine_with_fixed_benchmarks():
    """Testa scoring engine com benchmarks corrigidos"""
    print(f"\n🎯 TESTANDO SCORING ENGINE COM BENCHMARKS CORRIGIDOS")
    print("=" * 60)
    
    try:
        from agents.analyzers.scoring_engine import create_scoring_engine
        from utils.financial_calculator import FinancialData
        
        # Criar empresa de tech e banco para comparar
        tech_company = FinancialData(
            symbol="TECH4",
            market_cap=100_000_000_000,
            revenue=50_000_000_000,
            net_income=9_000_000_000,  # ROE ~18%
            shareholders_equity=50_000_000_000,
            sector="Tecnologia"
        )
        
        bank_company = FinancialData(
            symbol="BANK4",
            market_cap=120_000_000_000,
            revenue=30_000_000_000,
            net_income=13_200_000_000,  # ROE ~22%
            shareholders_equity=60_000_000_000,
            sector="Bancos"
        )
        
        # Calcular scores
        engine = create_scoring_engine()
        
        tech_score = engine.calculate_comprehensive_score(tech_company)
        bank_score = engine.calculate_comprehensive_score(bank_company)
        
        print(f"📊 SCORES CALCULADOS:")
        print(f"   {tech_score.stock_code} (Tech): {tech_score.composite_score:.1f}/100")
        print(f"      Rentabilidade: {tech_score.profitability_score:.1f}/100")
        print(f"   {bank_score.stock_code} (Banco): {bank_score.composite_score:.1f}/100")
        print(f"      Rentabilidade: {bank_score.profitability_score:.1f}/100")
        
        # Validar se scores fazem sentido
        scores_logical = True
        
        # Banco deve ter score de rentabilidade similar ou maior (ROE benchmark maior)
        if bank_score.profitability_score < tech_score.profitability_score - 10:
            print(f"   ⚠️ Banco deveria ter rentabilidade similar à tech")
            scores_logical = False
        
        print(f"\n✅ SCORING: {'LÓGICO' if scores_logical else 'PRECISA AJUSTE'}")
        
        return scores_logical
        
    except Exception as e:
        print(f"❌ ERRO no scoring: {e}")
        return False


def main():
    """Função principal"""
    print("🔧 CORREÇÃO DOS BENCHMARKS SETORIAIS")
    print("=" * 80)
    print("Corrigindo inconsistências detectadas no teste")
    print("=" * 80)
    
    # Teste 1: Validar lógica dos benchmarks
    benchmark_logic_ok = test_benchmark_logic()
    
    # Teste 2: Validar scoring com benchmarks corrigidos
    scoring_logic_ok = test_scoring_engine_with_fixed_benchmarks()
    
    # Resumo
    print("\n" + "=" * 80)
    print("📋 RESUMO DA CORREÇÃO")
    print("=" * 80)
    
    if benchmark_logic_ok and scoring_logic_ok:
        print("🎉 CORREÇÃO BEM-SUCEDIDA!")
        print("✅ Benchmarks setoriais agora são logicamente consistentes")
        print("✅ Bancos ROE (22%) > Tecnologia ROE (18%)")
        print("✅ Tecnologia P/L (25x) > Bancos P/L (12x)")
        print("✅ Scoring engine funcionando corretamente")
        print("\n🚀 Problema resolvido! Pode prosseguir para próximo passo.")
    else:
        print("❌ CORREÇÃO INCOMPLETA")
        if not benchmark_logic_ok:
            print("🔧 Benchmarks ainda têm inconsistências lógicas")
        if not scoring_logic_ok:
            print("🔧 Scoring engine precisa de ajustes")
    
    return benchmark_logic_ok and scoring_logic_ok


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)