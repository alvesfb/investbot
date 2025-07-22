#!/usr/bin/env python3
"""
Debug - Verificar se Score está sendo Calculado ou é Mock/Padrão

Investigar especificamente o valor 50 que pode estar sendo retornado
como fallback/padrão ao invés de cálculo real.
"""

import sys
from pathlib import Path
from typing import Dict, Any

# Adicionar diretório raiz ao path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def debug_financial_calculator():
    """Debug do FinancialCalculator para verificar scores"""
    
    print("🔍 DEBUG - FINANCIAL CALCULATOR")
    print("=" * 50)
    
    try:
        from utils.financial_calculator import FinancialCalculator, FinancialData
        
        # Dados de teste com valores bem definidos
        test_data = FinancialData(
            symbol='DEBUG_TEST',
            current_price=100.0,
            market_cap=10_000_000_000,  # 10 bilhões
            revenue=5_000_000_000,     # 5 bilhões
            net_income=500_000_000,    # 500 milhões
            total_assets=8_000_000_000,
            shareholders_equity=4_000_000_000,
            total_debt=2_000_000_000,
            current_assets=3_000_000_000,
            current_liabilities=1_000_000_000,
            sector='Tecnologia'
        )
        
        print("📊 DADOS DE TESTE:")
        print(f"   Market Cap: R$ {test_data.market_cap:,.0f}")
        print(f"   Receita: R$ {test_data.revenue:,.0f}")
        print(f"   Lucro Líquido: R$ {test_data.net_income:,.0f}")
        print(f"   Patrimônio: R$ {test_data.shareholders_equity:,.0f}")
        
        # Calcular métricas
        calculator = FinancialCalculator()
        metrics = calculator.calculate_all_metrics(test_data)
        
        print(f"\n🧮 MÉTRICAS CALCULADAS:")
        print(f"   P/L: {metrics.pe_ratio}")
        print(f"   P/VP: {metrics.pb_ratio}")
        print(f"   ROE: {metrics.roe}")
        print(f"   Margem Líquida: {metrics.net_margin}")
        
        # FOCO: Investigar o overall_score
        print(f"\n🎯 SCORE INVESTIGATION:")
        print(f"   Overall Score: {metrics.overall_score}")
        print(f"   Category Scores: {metrics.category_scores}")
        
        # Verificar se há warnings que indicam fallback
        if metrics.warnings:
            print(f"\n⚠️ WARNINGS:")
            for warning in metrics.warnings:
                print(f"   • {warning}")
        
        # Tentar acessar método interno de score
        if hasattr(calculator, '_calculate_overall_score'):
            manual_score = calculator._calculate_overall_score(metrics)
            print(f"   Manual Score Calculation: {manual_score}")
        
        # Verificar se score é exatamente 50 (indicativo de fallback)
        if metrics.overall_score == 50.0:
            print(f"   🚨 SCORE É EXATAMENTE 50.0 - PROVÁVEL FALLBACK!")
        else:
            print(f"   ✅ Score calculado: {metrics.overall_score}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no debug: {e}")
        return False

def debug_scoring_engine():
    """Debug do ScoringEngine para verificar scores"""
    
    print(f"\n🔍 DEBUG - SCORING ENGINE")
    print("=" * 50)
    
    try:
        from agents.analyzers.scoring_engine import ScoringEngine, create_scoring_engine
        from utils.financial_calculator import FinancialData
        
        # Mesmos dados de teste
        test_data = FinancialData(
            symbol='DEBUG_TEST',
            current_price=100.0,
            market_cap=10_000_000_000,
            revenue=5_000_000_000,
            net_income=500_000_000,
            total_assets=8_000_000_000,
            shareholders_equity=4_000_000_000,
            total_debt=2_000_000_000,
            current_assets=3_000_000_000,
            current_liabilities=1_000_000_000,
            sector='Tecnologia'
        )
        
        # Testar scoring engine
        engine = create_scoring_engine()
        score_result = engine.calculate_comprehensive_score(test_data)
        
        print(f"📊 SCORING ENGINE RESULT:")
        print(f"   Composite Score: {score_result.composite_score}")
        print(f"   Valuation Score: {score_result.valuation_score}")
        print(f"   Profitability Score: {score_result.profitability_score}")
        print(f"   Growth Score: {score_result.growth_score}")
        print(f"   Financial Health Score: {score_result.financial_health_score}")
        print(f"   Efficiency Score: {score_result.efficiency_score}")
        
        # Verificar se algum score é exatamente 50
        scores_to_check = [
            ('Composite', score_result.composite_score),
            ('Valuation', score_result.valuation_score),
            ('Profitability', score_result.profitability_score),
            ('Growth', score_result.growth_score),
            ('Financial Health', score_result.financial_health_score),
            ('Efficiency', score_result.efficiency_score)
        ]
        
        fallback_scores = []
        for name, score in scores_to_check:
            if score == 50.0:
                fallback_scores.append(name)
        
        if fallback_scores:
            print(f"\n🚨 SCORES COM VALOR 50.0 (FALLBACK):")
            for score_name in fallback_scores:
                print(f"   • {score_name}")
        else:
            print(f"\n✅ Todos os scores parecem calculados (não são 50.0)")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no debug scoring engine: {e}")
        return False

def debug_financial_analysis_tools():
    """Debug da FinancialAnalysisTools para verificar integração"""
    
    print(f"\n🔍 DEBUG - FINANCIAL ANALYSIS TOOLS")
    print("=" * 50)
    
    try:
        from tools.financial_analysis_tools import create_financial_analysis_tools
        
        # Dados de teste como dict (formato da tool)
        test_data = {
            'symbol': 'DEBUG_TEST',
            'current_price': 100.0,
            'market_cap': 10_000_000_000,
            'revenue': 5_000_000_000,
            'net_income': 500_000_000,
            'total_assets': 8_000_000_000,
            'shareholders_equity': 4_000_000_000,
            'total_debt': 2_000_000_000,
            'current_assets': 3_000_000_000,
            'current_liabilities': 1_000_000_000,
            'sector': 'Tecnologia'
        }
        
        # Testar tool
        tools = create_financial_analysis_tools()
        result = tools.analyze_company(test_data, include_score=True)
        
        if result['success']:
            print(f"✅ Análise bem-sucedida")
            
            # Verificar métricas
            if result['components']['metrics']['success']:
                metrics = result['components']['metrics']['metrics']
                overall_score = metrics.get('overall_score')
                print(f"   Metrics Overall Score: {overall_score}")
                
                if overall_score == 50.0:
                    print(f"   🚨 METRICS SCORE É 50.0 - FALLBACK!")
            
            # Verificar score
            if result['components']['score']['success']:
                composite_score = result['components']['score']['composite_score']
                print(f"   Composite Score: {composite_score}")
                
                if composite_score == 50.0:
                    print(f"   🚨 COMPOSITE SCORE É 50.0 - FALLBACK!")
                
                # Verificar scores individuais
                individual_scores = result['components']['score']['scores']
                print(f"   Individual Scores: {individual_scores}")
                
                fallback_individual = [k for k, v in individual_scores.items() if v == 50.0]
                if fallback_individual:
                    print(f"   🚨 SCORES INDIVIDUAIS COM 50.0: {fallback_individual}")
        else:
            print(f"❌ Análise falhou: {result.get('error')}")
            
        return True
        
    except Exception as e:
        print(f"❌ Erro no debug tools: {e}")
        return False

def analyze_fallback_sources():
    """Analisar possíveis fontes do valor 50.0"""
    
    print(f"\n🕵️ ANÁLISE DE FONTES DO FALLBACK 50.0")
    print("=" * 50)
    
    # Possíveis locais onde 50.0 é retornado
    fallback_sources = [
        "utils/financial_calculator.py: _calculate_overall_score() -> return 50.0",
        "agents/analyzers/scoring_engine.py: normalize_score() -> return 50.0",
        "Absence of proper data causing default values",
        "Exception handling returning neutral score",
        "Missing sector benchmarks causing fallback"
    ]
    
    print("🔍 POSSÍVEIS FONTES DO SCORE 50.0:")
    for i, source in enumerate(fallback_sources, 1):
        print(f"   {i}. {source}")
    
    print(f"\n💡 RECOMENDAÇÕES PARA INVESTIGAÇÃO:")
    print("   1. Verificar se dados de entrada são válidos")
    print("   2. Verificar se benchmarks setoriais existem")
    print("   3. Verificar se há exceptions sendo capturadas")
    print("   4. Verificar se pesos das categorias estão corretos")
    print("   5. Verificar se normalize_score está funcionando")

def main():
    """Função principal de debug"""
    
    print("🔍 DEBUG COMPLETO - INVESTIGAÇÃO SCORE 50.0")
    print("=" * 60)
    
    # Executar todos os debugs
    results = []
    
    print("FASE 1: FinancialCalculator")
    results.append(debug_financial_calculator())
    
    print("FASE 2: ScoringEngine") 
    results.append(debug_scoring_engine())
    
    print("FASE 3: FinancialAnalysisTools")
    results.append(debug_financial_analysis_tools())
    
    print("FASE 4: Análise de Fontes")
    analyze_fallback_sources()
    
    # Resumo
    successful_debugs = sum(results)
    print(f"\n📋 RESUMO DO DEBUG")
    print("=" * 30)
    print(f"Debugs executados: {len(results)}")
    print(f"Debugs bem-sucedidos: {successful_debugs}")
    
    if successful_debugs == len(results):
        print(f"✅ Todos os debugs executados - verificar outputs acima")
    else:
        print(f"⚠️ Alguns debugs falharam - verificar erros")
    
    print(f"\n🎯 PRÓXIMOS PASSOS:")
    print("   1. Analisar outputs acima para identificar onde score = 50.0")
    print("   2. Verificar se dados estão sendo processados corretamente") 
    print("   3. Verificar se exceções estão sendo capturadas silenciosamente")
    print("   4. Implementar logging mais detalhado nos cálculos")

if __name__ == "__main__":
    main()