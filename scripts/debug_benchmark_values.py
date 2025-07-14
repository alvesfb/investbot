#!/usr/bin/env python3
"""
Debug dos Valores dos Benchmarks
Vamos descobrir exatamente quais valores estão sendo carregados

Data: 14/07/2025
"""
import sys
from pathlib import Path

# Adicionar projeto ao path
project_root = Path.cwd()
sys.path.insert(0, str(project_root))

def debug_current_benchmark_values():
    """Debug para ver os valores reais que estão sendo carregados"""
    print("🔍 DEBUG DOS VALORES ATUAIS DOS BENCHMARKS")
    print("=" * 60)
    
    try:
        # Tentar importar do scoring_engine
        try:
            from agents.analyzers.scoring_engine import SectorBenchmarks
            source = "scoring_engine"
        except ImportError:
            try:
                # Fallback para financial_calculator se scoring_engine não estiver disponível
                from utils.financial_calculator import FinancialCalculator
                calc = FinancialCalculator()
                benchmarks_dict = calc.sector_benchmarks
                source = "financial_calculator"
            except ImportError:
                print("❌ Nenhuma fonte de benchmarks disponível")
                return False
        
        print(f"📊 FONTE DOS BENCHMARKS: {source}")
        
        if source == "scoring_engine":
            benchmarks = SectorBenchmarks.get_default_benchmarks()
            
            print(f"\n🔢 VALORES REAIS CARREGADOS:")
            for sector_name, benchmark in benchmarks.items():
                print(f"\n   {sector_name}:")
                print(f"      ROE: {benchmark.roe_median}")
                print(f"      P/L: {benchmark.pe_ratio_median}")
                print(f"      P/VP: {benchmark.pb_ratio_median}")
                print(f"      Margem: {benchmark.net_margin_median}")
                print(f"      Crescimento: {benchmark.revenue_growth_median}")
                print(f"      D/E: {benchmark.debt_to_equity_median}")
            
            # Testar as validações específicas que falharam
            banks = benchmarks['Bancos']
            tech = benchmarks['Tecnologia']
            oil = benchmarks['Petróleo e Gás']
            
            print(f"\n🧪 TESTE DAS VALIDAÇÕES QUE FALHARAM:")
            
            # 1. Bancos ROE > Tech ROE
            test1 = banks.roe_median > tech.roe_median
            print(f"   Bancos ROE ({banks.roe_median}) > Tech ROE ({tech.roe_median}): {'✅' if test1 else '❌'}")
            
            # 2. Bancos ROE > 20%
            test2 = banks.roe_median > 20
            print(f"   Bancos ROE ({banks.roe_median}) > 20: {'✅' if test2 else '❌'}")
            
            # 3. Tech P/L > 25x
            test3 = tech.pe_ratio_median > 25
            print(f"   Tech P/L ({tech.pe_ratio_median}) > 25: {'✅' if test3 else '❌'}")
            
            # 4. Oil P/L < 10x
            test4 = oil.pe_ratio_median < 10
            print(f"   Oil P/L ({oil.pe_ratio_median}) < 10: {'✅' if test4 else '❌'}")
            
            all_tests_pass = test1 and test2 and test3 and test4
            print(f"\n📊 RESULTADO: {'Todos passaram ✅' if all_tests_pass else 'Alguns falharam ❌'}")
            
            if not all_tests_pass:
                print(f"\n🔧 VALORES NECESSÁRIOS PARA PASSAR:")
                if not test1:
                    print(f"   Bancos ROE deve ser > {tech.roe_median} (atual: {banks.roe_median})")
                if not test2:
                    print(f"   Bancos ROE deve ser > 20 (atual: {banks.roe_median})")
                if not test3:
                    print(f"   Tech P/L deve ser > 25 (atual: {tech.pe_ratio_median})")
                if not test4:
                    print(f"   Oil P/L deve ser < 10 (atual: {oil.pe_ratio_median})")
        
        elif source == "financial_calculator":
            print(f"\n🔢 VALORES DO FINANCIAL_CALCULATOR:")
            for sector, values in benchmarks_dict.items():
                print(f"   {sector}: {values}")
        
        return True
        
    except Exception as e:
        print(f"❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_file_locations():
    """Verifica onde estão os arquivos e se foram atualizados"""
    print(f"\n📁 VERIFICANDO LOCALIZAÇÃO DOS ARQUIVOS")
    print("=" * 60)
    
    files_to_check = [
        "agents/analyzers/scoring_engine.py",
        "utils/financial_calculator.py", 
        "agents/analyzers/fundamental_scoring_system.py"
    ]
    
    for file_path in files_to_check:
        full_path = project_root / file_path
        if full_path.exists():
            # Verificar timestamp de modificação
            import os
            mod_time = os.path.getmtime(full_path)
            from datetime import datetime
            mod_datetime = datetime.fromtimestamp(mod_time)
            
            print(f"   ✅ {file_path}")
            print(f"      Modificado: {mod_datetime.strftime('%d/%m/%Y %H:%M:%S')}")
            
            # Verificar se contém os valores atualizados
            content = full_path.read_text(encoding='utf-8')
            if "roe_median=23.0" in content:
                print(f"      ✅ Contém ROE=23.0 (corrigido)")
            elif "roe_median=22.0" in content:
                print(f"      ⚠️ Contém ROE=22.0 (valor antigo)")
            else:
                print(f"      ❓ ROE não encontrado ou formato diferente")
                
            if "pe_ratio_median=30.0" in content:
                print(f"      ✅ Contém Tech P/L=30.0 (corrigido)")
            elif "pe_ratio_median=28.0" in content:
                print(f"      ⚠️ Contém Tech P/L=28.0 (valor antigo)")
                
        else:
            print(f"   ❌ {file_path} - NÃO ENCONTRADO")


def try_direct_import_test():
    """Tenta importar diretamente e testar"""
    print(f"\n🎯 TESTE DIRETO DE IMPORTAÇÃO")
    print("=" * 60)
    
    try:
        # Forçar reimportação
        import importlib
        
        # Tentar scoring_engine primeiro
        try:
            if 'agents.analyzers.scoring_engine' in sys.modules:
                importlib.reload(sys.modules['agents.analyzers.scoring_engine'])
            
            from agents.analyzers.scoring_engine import SectorBenchmarks
            
            benchmarks = SectorBenchmarks.get_default_benchmarks()
            banks = benchmarks['Bancos']
            tech = benchmarks['Tecnologia']
            
            print(f"   Bancos ROE após reload: {banks.roe_median}")
            print(f"   Tech P/L após reload: {tech.pe_ratio_median}")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Erro no scoring_engine: {e}")
            
        # Tentar financial_calculator
        try:
            if 'utils.financial_calculator' in sys.modules:
                importlib.reload(sys.modules['utils.financial_calculator'])
                
            from utils.financial_calculator import FinancialCalculator
            
            calc = FinancialCalculator()
            print(f"   Financial calculator benchmarks: {calc.sector_benchmarks}")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Erro no financial_calculator: {e}")
            
        return False
        
    except Exception as e:
        print(f"❌ ERRO GERAL: {e}")
        return False


def main():
    """Função principal de debug"""
    print("🔍 DEBUG COMPLETO DOS BENCHMARKS SETORIAIS")
    print("=" * 80)
    print("Investigando por que os valores não estão sendo aplicados")
    print("=" * 80)
    
    # 1. Verificar arquivos
    check_file_locations()
    
    # 2. Debug valores atuais
    values_ok = debug_current_benchmark_values()
    
    # 3. Teste direto de importação
    import_ok = try_direct_import_test()
    
    print("\n" + "=" * 80)
    print("📋 DIAGNÓSTICO FINAL")
    print("=" * 80)
    
    if values_ok:
        print("✅ Consegui carregar e testar os benchmarks")
    else:
        print("❌ Não consegui carregar os benchmarks corretamente")
        
    if import_ok:
        print("✅ Importações funcionando")
    else:
        print("❌ Problema nas importações")
        
    print("\n🔧 PRÓXIMOS PASSOS:")
    print("1. Verifique se o arquivo scoring_engine.py foi salvo corretamente")
    print("2. Execute 'python -c \"from agents.analyzers.scoring_engine import SectorBenchmarks; print(SectorBenchmarks.get_default_benchmarks()['Bancos'].roe_median)\"'")
    print("3. Se necessário, reinicie o Python/terminal para limpar cache de imports")


if __name__ == "__main__":
    main()