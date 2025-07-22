#!/usr/bin/env python3
"""
Teste Simples de Integração - FinancialAnalysisTools
Valida se a análise está funcionando corretamente.
"""

import sys
from pathlib import Path

# Adicionar diretório raiz ao path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_integration():
    """Teste simples e direto da análise financeira"""
    
    print("🧪 TESTE SIMPLES DE INTEGRAÇÃO")
    print("=" * 40)
    
    # 1. Import e criação da tool
    try:
        from tools.financial_analysis_tools import create_financial_analysis_tools
        tools = create_financial_analysis_tools()
        print("✅ Tool criada com sucesso")
    except Exception as e:
        print(f"❌ Erro: {e}")
        return
    
    # 2. Dados de uma empresa exemplo (baseados em dados reais)
    petrobras_data = {
        'symbol': 'PETR4',
        'current_price': 38.50,
        'market_cap': 500_000_000_000,  # R$ 500bi
        'revenue': 400_000_000_000,     # R$ 400bi
        'net_income': 80_000_000_000,   # R$ 80bi
        'total_assets': 600_000_000_000,
        'shareholders_equity': 250_000_000_000,
        'total_debt': 200_000_000_000,
        'current_assets': 150_000_000_000,
        'current_liabilities': 100_000_000_000,
        'revenue_history': [350_000_000_000, 380_000_000_000, 390_000_000_000],
        'net_income_history': [45_000_000_000, 65_000_000_000, 75_000_000_000],
        'sector': 'Petróleo e Gás'
    }
    
    print(f"\n📊 ANALISANDO: {petrobras_data['symbol']}")
    print(f"Setor: {petrobras_data['sector']}")
    print(f"Preço: R$ {petrobras_data['current_price']:.2f}")
    
    # 3. Fazer análise completa
    result = tools.analyze_company(petrobras_data, include_score=True)
    
    # 4. Mostrar resultados
    if result['success']:
        print("\n✅ ANÁLISE CONCLUÍDA COM SUCESSO!")
        
        # Métricas principais
        if result['components']['metrics']['success']:
            metrics = result['components']['metrics']['metrics']
            print(f"\n📈 MÉTRICAS PRINCIPAIS:")
            print(f"   P/L: {metrics.get('pe_ratio', 'N/A'):.2f}")
            print(f"   P/VP: {metrics.get('pb_ratio', 'N/A'):.2f}")
            print(f"   ROE: {metrics.get('roe', 'N/A'):.1f}%")
            print(f"   Margem Líquida: {metrics.get('net_margin', 'N/A'):.1f}%")
            print(f"   Crescimento Receita: {metrics.get('revenue_growth_1y', 'N/A'):.1f}%")
            print(f"   Dívida/Patrimônio: {metrics.get('debt_to_equity', 'N/A'):.2f}")
        
        # Score fundamentalista
        if result['components']['score']['success']:
            score_data = result['components']['score']
            print(f"\n🏆 SCORE FUNDAMENTALISTA:")
            print(f"   Score Final: {score_data['composite_score']:.1f}/100")
            print(f"   Qualidade: {score_data['quality_tier']}")
            print(f"   Recomendação: {score_data['recommendation']}")
            
            print(f"\n📊 BREAKDOWN DO SCORE:")
            scores = score_data['scores']
            print(f"   Valuation: {scores['valuation']:.1f}/100")
            print(f"   Rentabilidade: {scores['profitability']:.1f}/100")
            print(f"   Crescimento: {scores['growth']:.1f}/100")
            print(f"   Saúde Financeira: {scores['financial_health']:.1f}/100")
            
            # Pontos fortes e fracos
            analysis = score_data['analysis']
            if analysis['strengths']:
                print(f"\n💪 PONTOS FORTES:")
                for strength in analysis['strengths'][:3]:  # Mostrar apenas 3
                    print(f"   • {strength}")
            
            if analysis['weaknesses']:
                print(f"\n⚠️ PONTOS FRACOS:")
                for weakness in analysis['weaknesses'][:3]:  # Mostrar apenas 3
                    print(f"   • {weakness}")
        
        print(f"\n🎯 RESULTADO FINAL:")
        if result['components']['score']['success']:
            score = score_data['composite_score']
            if score >= 80:
                print(f"   🟢 EXCELENTE ({score:.1f}/100) - Forte candidata a investimento")
            elif score >= 60:
                print(f"   🟡 BOA ({score:.1f}/100) - Considerar com cautela")
            elif score >= 40:
                print(f"   🟠 REGULAR ({score:.1f}/100) - Análise adicional necessária")
            else:
                print(f"   🔴 RUIM ({score:.1f}/100) - Evitar investimento")
        else:
            print(f"   ⚠️ Score não disponível, mas métricas calculadas")
    
    else:
        print(f"\n❌ ANÁLISE FALHOU")
        print(f"Erro: {result.get('error', 'Erro desconhecido')}")
    
    print(f"\n✅ TESTE DE INTEGRAÇÃO CONCLUÍDO")


if __name__ == "__main__":
    test_integration()