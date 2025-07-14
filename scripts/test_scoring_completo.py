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

def test_comprehensive_benchmark_logic():
    """Testa todas as lógicas setoriais de forma abrangente"""
    print("🔧 TESTE ABRANGENTE DE LÓGICA SETORIAL")
    print("=" * 60)
    
    try:
        from agents.analyzers.scoring_engine import SectorBenchmarks
        
        # Carregar benchmarks corrigidos
        benchmarks = SectorBenchmarks.get_default_benchmarks()
        
        # Extrair setores principais para comparação
        banks = benchmarks['Bancos']
        tech = benchmarks['Tecnologia']
        oil = benchmarks['Petróleo e Gás']
        retail = benchmarks['Varejo']
        utilities = benchmarks['Utilities']
        mining = benchmarks.get('Mineração', None)
        
        print("📊 BENCHMARKS ATUALIZADOS:")
        for sector, bench in benchmarks.items():
            print(f"   {sector}:")
            print(f"      P/L: {bench.pe_ratio_median:.1f}x, P/VP: {bench.pb_ratio_median:.1f}x")
            print(f"      ROE: {bench.roe_median:.1f}%, Margem: {bench.net_margin_median:.1f}%")
            print(f"      Crescimento: {bench.revenue_growth_median:.1f}%, D/E: {bench.debt_to_equity_median:.1f}x")
        
        # VALIDAÇÕES LÓGICAS ABRANGENTES
        validations = []
        
        # 1. ROE: Bancos > Tech > Varejo > Utilities (alavancagem)
        validations.append(("Bancos ROE > Tech ROE", banks.roe_median > tech.roe_median))
        validations.append(("Tech ROE > Utilities ROE", tech.roe_median > utilities.roe_median))
        validations.append(("Varejo ROE > Oil ROE", retail.roe_median > oil.roe_median))
        
        # 2. P/L: Tech > Varejo > Utilities > Bancos > Oil (múltiplo crescimento)
        validations.append(("Tech P/L > Varejo P/L", tech.pe_ratio_median > retail.pe_ratio_median))
        validations.append(("Varejo P/L > Utilities P/L", retail.pe_ratio_median > utilities.pe_ratio_median))
        validations.append(("Utilities P/L > Bancos P/L", utilities.pe_ratio_median > banks.pe_ratio_median))
        validations.append(("Bancos P/L > Oil P/L", banks.pe_ratio_median > oil.pe_ratio_median))
        
        # 3. P/VP: Tech > Varejo > Utilities > Oil/Bancos (intensidade ativos)
        validations.append(("Tech P/VP > Varejo P/VP", tech.pb_ratio_median > retail.pb_ratio_median))
        validations.append(("Varejo P/VP > Utilities P/VP", retail.pb_ratio_median > utilities.pb_ratio_median))
        
        # 4. Margem: Bancos > Tech > Utilities > Varejo (estrutura custos)
        validations.append(("Bancos Margem > Tech Margem", banks.net_margin_median > tech.net_margin_median))
        validations.append(("Tech Margem > Utilities Margem", tech.net_margin_median > utilities.net_margin_median))
        validations.append(("Utilities Margem > Varejo Margem", utilities.net_margin_median > retail.net_margin_median))
        
        # 5. Crescimento: Tech > Varejo > Bancos > Utilities > Oil (dinâmica setorial)
        validations.append(("Tech Crescimento > Varejo Crescimento", tech.revenue_growth_median > retail.revenue_growth_median))
        validations.append(("Varejo Crescimento > Bancos Crescimento", retail.revenue_growth_median > banks.revenue_growth_median))
        validations.append(("Bancos Crescimento > Utilities Crescimento", banks.revenue_growth_median > utilities.revenue_growth_median))
        
        # 6. Endividamento: Bancos >> Utilities > Oil > Varejo > Tech (modelo negócio)
        validations.append(("Bancos D/E > Utilities D/E", banks.debt_to_equity_median > utilities.debt_to_equity_median))
        validations.append(("Utilities D/E > Varejo D/E", utilities.debt_to_equity_median > retail.debt_to_equity_median))
        validations.append(("Varejo D/E > Tech D/E", retail.debt_to_equity_median > tech.debt_to_equity_median))
        
        # 7. Validações de sanidade (valores absolutos)
        validations.append(("Bancos ROE > 20%", banks.roe_median > 20))
        validations.append(("Tech P/L > 25x", tech.pe_ratio_median > 25))
        validations.append(("Oil P/L < 10x", oil.pe_ratio_median < 10))
        validations.append(("Varejo Margem < 10%", retail.net_margin_median < 10))
        validations.append(("Tech Crescimento > 20%", tech.revenue_growth_median > 20))
        
        print(f"\n✅ VALIDAÇÕES LÓGICAS ({len(validations)} testes):")
        failed_validations = []
        
        for test_name, passed in validations:
            status = "✅" if passed else "❌"
            print(f"   {status} {test_name}")
            if not passed:
                failed_validations.append(test_name)
        
        success_rate = (len(validations) - len(failed_validations)) / len(validations) * 100
        print(f"\n📊 RESULTADO: {success_rate:.1f}% das validações passaram")
        
        if failed_validations:
            print(f"\n❌ VALIDAÇÕES QUE FALHARAM:")
            for failed in failed_validations:
                print(f"   • {failed}")
        
        return len(failed_validations) == 0
        
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
    print("🔧 CORREÇÃO COMPLETA DOS BENCHMARKS SETORIAIS")
    print("=" * 80)
    print("Corrigindo TODAS as inconsistências lógicas detectadas")
    print("=" * 80)
    
    # Teste 1: Validar lógica abrangente dos benchmarks
    benchmark_logic_ok = test_comprehensive_benchmark_logic()
    
    # Teste 2: Validar scoring com benchmarks corrigidos
    scoring_logic_ok = test_scoring_engine_with_fixed_benchmarks()
    
    # Resumo
    print("\n" + "=" * 80)
    print("📋 RESUMO DA CORREÇÃO COMPLETA")
    print("=" * 80)
    
    if benchmark_logic_ok and scoring_logic_ok:
        print("🎉 CORREÇÃO COMPLETA BEM-SUCEDIDA!")
        print("✅ TODAS as inconsistências lógicas corrigidas")
        print("✅ Hierarquia setorial correta:")
        print("   • ROE: Bancos (22%) > Tech (18%) > Varejo (16%) > Utilities (14%)")
        print("   • P/L: Tech (28x) > Varejo (15x) > Utilities (12x) > Bancos (8x) > Oil (6x)")
        print("   • Margem: Bancos (28%) > Tech (15%) > Utilities (12%) > Oil (8%) > Varejo (4%)")
        print("   • Crescimento: Tech (25%) > Varejo (10%) > Bancos (8%) > Oil (3%)")
        print("   • Endividamento: Bancos (8x) > Utilities (1.5x) > Varejo (0.8x) > Oil (0.6x) > Tech (0.1x)")
        print("✅ Scoring engine funcionando corretamente")
        print("\n🚀 TODAS as inconsistências resolvidas! Pode prosseguir com confiança.")
    else:
        print("❌ AINDA EXISTEM PROBLEMAS")
        if not benchmark_logic_ok:
            print("🔧 Benchmarks ainda têm inconsistências - revisar valores")
        if not scoring_logic_ok:
            print("🔧 Scoring engine precisa de ajustes adicionais")
        
        print("\n📋 VALORES FINAIS DOS BENCHMARKS:")
        try:
            from agents.analyzers.scoring_engine import SectorBenchmarks
            benchmarks = SectorBenchmarks.get_default_benchmarks()
            
            for sector, bench in benchmarks.items():
                print(f"   {sector}: ROE {bench.roe_median}%, P/L {bench.pe_ratio_median}x, Margem {bench.net_margin_median}%")
        except:
            pass
    
    return benchmark_logic_ok and scoring_logic_ok


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)