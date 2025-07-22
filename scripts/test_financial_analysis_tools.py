#!/usr/bin/env python3
"""
Teste com Dados Reais - Validação da Correção do Growth Score
Verifica se o Growth Score não é mais 50.0 após correção da FinancialAnalysisTools
"""

import sys
import asyncio
from pathlib import Path
from datetime import datetime
import logging

# Adicionar diretório raiz ao path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configurar logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

def convert_collector_data_to_analysis_format(stock_data: dict, symbol: str) -> dict:
    """
    Converte dados do stock_collector para formato da FinancialAnalysisTools
    """
    
    # Mapear setor brasileiro para inglês se necessário
    sector_mapping = {
        'Petróleo e Gás': 'Energy',
        'Bancos': 'Financial Services',
        'Mineração': 'Basic Materials',
        'Tecnologia': 'Technology',
        'Varejo': 'Consumer Cyclical',
        'Utilities': 'Utilities'
    }
    
    # Detectar setor baseado no símbolo (heurística simples)
    sector = 'Geral'  # Default
    if symbol.startswith('PETR'):
        sector = 'Petróleo e Gás'
    elif symbol.startswith('VALE'):
        sector = 'Mineração'
    elif symbol.startswith('ITUB') or symbol.startswith('BBDC'):
        sector = 'Bancos'
    elif symbol.startswith('MGLU') or symbol.startswith('AMER'):
        sector = 'Varejo'
    
    return {
        'symbol': symbol,
        'current_price': stock_data.get('regularMarketPrice') or stock_data.get('currentPrice'),
        'market_cap': stock_data.get('marketCap'),
        'shares_outstanding': stock_data.get('sharesOutstanding'),
        'revenue': stock_data.get('totalRevenue'),
        'net_income': stock_data.get('netIncomeToCommon'),
        'total_assets': stock_data.get('totalAssets'),
        'shareholders_equity': stock_data.get('totalStockholderEquity'),
        'total_debt': stock_data.get('totalDebt'),
        'current_assets': stock_data.get('totalCurrentAssets'),
        'current_liabilities': stock_data.get('totalCurrentLiabilities'),
        'gross_profit': stock_data.get('grossProfit'),
        'operating_income': stock_data.get('operatingIncome'),
        'ebitda': stock_data.get('ebitda'),
        'revenue_history': [],  # YFinance não retorna histórico direto
        'net_income_history': [],
        'sector': sector_mapping.get(sector, sector),
        'industry': stock_data.get('industry', 'N/A'),
        # Metadados do YFinance
        'yfinance_data': {
            'longName': stock_data.get('longName'),
            'shortName': stock_data.get('shortName'),
            'currency': stock_data.get('currency', 'BRL'),
            'country': stock_data.get('country', 'Brazil'),
            'pe_ratio': stock_data.get('trailingPE'),
            'pb_ratio': stock_data.get('priceToBook'),
            'dividend_yield': stock_data.get('dividendYield')
        }
    }

async def test_with_stock_collector():
    """Teste completo usando o stock_collector existente - VALIDAÇÃO GROWTH SCORE"""
    
    print("🏢 TESTE DE VALIDAÇÃO - CORREÇÃO GROWTH SCORE")
    print("=" * 60)
    print("🎯 OBJETIVO: Verificar se Growth Score não é mais 50.0")
    print("🔧 CORREÇÃO: Implementação de histórico estimado")
    
    # Lista de empresas brasileiras para testar
    companies = [
        'PETR4',  # Petrobras
        'VALE3',  # Vale
        'ITUB4',  # Itaú
    ]
    
    # 1. Verificar disponibilidade dos componentes
    print("\n📦 1. VERIFICANDO COMPONENTES")
    
    # Tentar importar stock collector
    try:
        from agents.collectors.stock_collector import YFinanceClient
        collector_available = True
        print("   ✅ YFinanceClient (Stock Collector) disponível")
    except ImportError as e:
        print(f"   ❌ Stock Collector não disponível: {e}")
        collector_available = False
    
    # Tentar importar agente completo (se disponível)
    try:
        from agents.collectors.stock_collector import StockCollectorAgent
        agent_available = True
        print("   ✅ StockCollectorAgent disponível")
    except ImportError:
        agent_available = False
        print("   ⚠️ StockCollectorAgent não disponível (usando só o client)")
    
    # Importar FinancialAnalysisTools
    try:
        from tools.financial_analysis_tools import create_financial_analysis_tools
        analysis_tools = create_financial_analysis_tools()
        tools_available = True
        print("   ✅ FinancialAnalysisTools disponível")
        
        # Verificar capacidades
        status = analysis_tools.get_tool_status()
        if status['capabilities']['full_analysis']:
            print("   ✅ Análise completa disponível")
        else:
            print("   ⚠️ Análise limitada (alguns componentes faltando)")
            
    except Exception as e:
        print(f"   ❌ FinancialAnalysisTools não disponível: {e}")
        tools_available = False
        return
    
    if not collector_available:
        print("   ❌ Não é possível continuar sem o Stock Collector")
        return
    
    # 2. Inicializar cliente
    print("\n🔧 2. INICIALIZANDO STOCK COLLECTOR")
    try:
        yf_client = YFinanceClient()
        print("   ✅ YFinanceClient inicializado")
    except Exception as e:
        print(f"   ❌ Erro ao inicializar: {e}")
        return
    
    # 3. Testar coleta + análise para cada empresa COM FOCO NO GROWTH SCORE
    print(f"\n📊 3. VALIDANDO CORREÇÃO EM {len(companies)} EMPRESAS")
    print("🔍 FOCO: Verificar se Growth Score ≠ 50.0")
    
    successful_analyses = 0
    results = []
    growth_score_analysis = {
        'fallback_count': 0,  # Quantos growth scores = 50.0
        'calculated_count': 0,  # Quantos growth scores ≠ 50.0
        'scores': []  # Lista de todos os growth scores
    }
    
    for i, symbol in enumerate(companies, 1):
        print(f"\n--- {i}. ANALISANDO {symbol} ---")
        
        try:
            # Coletar dados usando stock_collector
            print(f"   📡 Coletando dados via Stock Collector...")
            raw_data = await yf_client.get_stock_info(symbol)
            
            if not raw_data or not raw_data.get('regularMarketPrice'):
                print(f"   ❌ Dados não coletados ou inválidos para {symbol}")
                continue
            
            # Mostrar dados básicos coletados
            price = raw_data.get('regularMarketPrice') or raw_data.get('currentPrice', 0)
            market_cap = raw_data.get('marketCap', 0)
            name = raw_data.get('longName') or raw_data.get('shortName', symbol)
            
            print(f"   📈 Empresa: {name}")
            print(f"   💰 Preço: R$ {price:.2f}")
            print(f"   🏭 Market Cap: R$ {market_cap:,.0f}" if market_cap else "   🏭 Market Cap: N/A")
            
            # Converter para formato da FinancialAnalysisTools
            analysis_data = convert_collector_data_to_analysis_format(raw_data, symbol)
            
            # 🔍 DEBUG: Mostrar se há dados históricos
            print(f"   📊 Dados históricos:")
            print(f"      Revenue History: {len(analysis_data.get('revenue_history', []))} anos")
            print(f"      Net Income History: {len(analysis_data.get('net_income_history', []))} anos")
            
            # Fazer análise financeira
            print(f"   🧮 Executando análise financeira...")
            analysis_result = analysis_tools.analyze_company(analysis_data, include_score=True)
            
            if analysis_result['success']:
                print(f"   ✅ Análise concluída com sucesso!")
                
                # Extrair métricas
                if analysis_result['components']['metrics']['success']:
                    metrics = analysis_result['components']['metrics']['metrics']
                    print(f"   📊 P/L: {metrics.get('pe_ratio', 'N/A'):.2f}" if metrics.get('pe_ratio') else "   📊 P/L: N/A")
                    print(f"   📊 P/VP: {metrics.get('pb_ratio', 'N/A'):.2f}" if metrics.get('pb_ratio') else "   📊 P/VP: N/A")
                    print(f"   💎 ROE: {metrics.get('roe', 'N/A'):.1f}%" if metrics.get('roe') else "   💎 ROE: N/A")
                    print(f"   💰 Margem Líq.: {metrics.get('net_margin', 'N/A'):.1f}%" if metrics.get('net_margin') else "   💰 Margem Líq.: N/A")
                
                # Extrair score com FOCO no Growth Score
                if analysis_result['components']['score']['success']:
                    score_data = analysis_result['components']['score']
                    score = score_data['composite_score']
                    scores = score_data['scores']
                    
                    # 🎯 VALIDAÇÃO PRINCIPAL: Growth Score
                    growth_score = scores.get('growth', 50.0)
                    print(f"   🎯 GROWTH SCORE: {growth_score:.1f}/100")
                    
                    if growth_score == 50.0:
                        print(f"   🚨 GROWTH SCORE É FALLBACK (50.0)")
                        growth_score_analysis['fallback_count'] += 1
                    else:
                        print(f"   ✅ GROWTH SCORE CALCULADO ({growth_score:.1f})")
                        growth_score_analysis['calculated_count'] += 1
                    
                    growth_score_analysis['scores'].append({
                        'symbol': symbol,
                        'growth_score': growth_score,
                        'is_fallback': growth_score == 50.0
                    })
                    
                    print(f"   🏆 Score Fundamentalista: {score:.1f}/100")
                    print(f"   📝 Qualidade: {score_data['quality_tier']}")
                    print(f"   📝 Recomendação: {score_data['recommendation']}")
                    
                    # Breakdown detalhado dos scores
                    print(f"   📊 BREAKDOWN COMPLETO:")
                    print(f"      • Valuation: {scores.get('valuation', 0):.1f}/100")
                    print(f"      • Profitability: {scores.get('profitability', 0):.1f}/100")
                    print(f"      • Growth: {scores.get('growth', 0):.1f}/100 {'🚨' if scores.get('growth') == 50.0 else '✅'}")
                    print(f"      • Financial Health: {scores.get('financial_health', 0):.1f}/100")
                    print(f"      • Efficiency: {scores.get('efficiency', 0):.1f}/100")
                
                successful_analyses += 1
                results.append({
                    'symbol': symbol,
                    'name': name,
                    'price': price,
                    'score': score_data.get('composite_score') if analysis_result['components']['score']['success'] else None,
                    'recommendation': score_data.get('recommendation') if analysis_result['components']['score']['success'] else None,
                    'growth_score': scores.get('growth', 50.0) if analysis_result['components']['score']['success'] else 50.0
                })
                
            else:
                print(f"   ❌ Análise falhou: {analysis_result.get('error', 'Erro desconhecido')}")
        
        except Exception as e:
            print(f"   ❌ Erro durante processamento: {str(e)}")
            logger.error(f"Erro detalhado para {symbol}: {e}", exc_info=True)
    
    # 4. Resumo da validação do Growth Score
    print(f"\n🎯 4. VALIDAÇÃO DO GROWTH SCORE")
    print("   " + "="*50)
    
    total_analyses = growth_score_analysis['fallback_count'] + growth_score_analysis['calculated_count']
    
    if total_analyses > 0:
        print(f"   📊 ESTATÍSTICAS DO GROWTH SCORE:")
        print(f"      Total analisado: {total_analyses}")
        print(f"      Fallback (50.0): {growth_score_analysis['fallback_count']}")
        print(f"      Calculado (≠50.0): {growth_score_analysis['calculated_count']}")
        print(f"      Taxa de sucesso: {growth_score_analysis['calculated_count']/total_analyses*100:.1f}%")
        
        print(f"\n   📋 DETALHAMENTO POR EMPRESA:")
        for score_info in growth_score_analysis['scores']:
            status = "🚨 FALLBACK" if score_info['is_fallback'] else "✅ CALCULADO"
            print(f"      {score_info['symbol']}: {score_info['growth_score']:.1f} {status}")
        
        # Verificação do sucesso da correção
        if growth_score_analysis['calculated_count'] > growth_score_analysis['fallback_count']:
            print(f"\n   🎉 CORREÇÃO BEM-SUCEDIDA!")
            print(f"   ✅ Maioria dos Growth Scores foram calculados (não fallback)")
        elif growth_score_analysis['calculated_count'] > 0:
            print(f"\n   🟡 CORREÇÃO PARCIAL")
            print(f"   ✅ Alguns Growth Scores foram calculados")
            print(f"   ⚠️ Mas ainda há fallbacks - pode precisar de mais dados históricos")
        else:
            print(f"\n   🚨 CORREÇÃO NÃO FUNCIONOU")
            print(f"   ❌ Todos os Growth Scores ainda são fallback (50.0)")
            print(f"   💡 Verificar implementação de _extract_historical_data()")
    
    # 5. Resumo comparativo (mantido para compatibilidade)
    print(f"\n📋 5. RESUMO COMPARATIVO")
    print("   " + "="*50)
    
    if results:
        print(f"   {'EMPRESA':<10} {'PREÇO':<10} {'SCORE':<8} {'GROWTH':<8} {'RECOMENDAÇÃO'}")
        print("   " + "-"*60)
        
        # Ordenar por score (maior primeiro)
        sorted_results = sorted(
            [r for r in results if r['score'] is not None], 
            key=lambda x: x['score'], 
            reverse=True
        )
        
        for result in sorted_results:
            score_str = f"{result['score']:.1f}" if result['score'] else "N/A"
            growth_str = f"{result['growth_score']:.1f}" if result['growth_score'] else "N/A"
            growth_indicator = "🚨" if result['growth_score'] == 50.0 else "✅"
            recommendation = result['recommendation'] or "N/A"
            print(f"   {result['symbol']:<10} R${result['price']:<8.2f} {score_str:<8} {growth_str:<7}{growth_indicator} {recommendation}")
        
        # Estatísticas
        if sorted_results:
            scores = [r['score'] for r in sorted_results if r['score']]
            growth_scores = [r['growth_score'] for r in sorted_results if r['growth_score'] != 50.0]
            
            if scores:
                avg_score = sum(scores) / len(scores)
                best_company = sorted_results[0]
                print(f"\n   📊 ESTATÍSTICAS:")
                print(f"      Score médio: {avg_score:.1f}/100")
                print(f"      Melhor empresa: {best_company['symbol']} ({best_company['score']:.1f})")
                print(f"      Empresas analisadas: {len(sorted_results)}")
                
                if growth_scores:
                    avg_growth = sum(growth_scores) / len(growth_scores)
                    print(f"      Growth Score médio (calculados): {avg_growth:.1f}/100")
    
    # 6. Resumo final com foco na validação
    print(f"\n🎯 6. RESUMO FINAL DA VALIDAÇÃO")
    print("   " + "="*40)
    print(f"   Empresas testadas: {len(companies)}")
    print(f"   Análises bem-sucedidas: {successful_analyses}")
    print(f"   Taxa de sucesso: {successful_analyses/len(companies)*100:.1f}%")
    
    # Resultado específico da correção
    if growth_score_analysis['calculated_count'] > 0:
        print(f"   🎉 CORREÇÃO GROWTH SCORE: FUNCIONANDO!")
        print(f"   ✅ {growth_score_analysis['calculated_count']} Growth Scores calculados")
        if growth_score_analysis['fallback_count'] > 0:
            print(f"   ⚠️ {growth_score_analysis['fallback_count']} ainda em fallback")
    else:
        print(f"   🚨 CORREÇÃO GROWTH SCORE: NÃO FUNCIONOU")
        print(f"   ❌ Todos os Growth Scores ainda são 50.0")
    
    if successful_analyses > 0:
        print(f"   ✅ Stock Collector → FinancialAnalysisTools ✅")
        print(f"   ✅ Dados reais do Yahoo Finance processados")
        print(f"   ✅ Análise fundamentalista completa operacional")
    else:
        print(f"   ⚠️ Nenhuma análise foi concluída com sucesso")
        print(f"   💡 Verifique logs para detalhes dos erros")
    
    print(f"\n🌐 Dados coletados via Stock Collector (YFinance)")
    print(f"📅 Teste executado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"🎯 OBJETIVO: Validar correção do Growth Score ≠ 50.0")


def main():
    """Função principal"""
    try:
        asyncio.run(test_with_stock_collector())
    except KeyboardInterrupt:
        print(f"\n⏹️ Teste interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro fatal no teste: {e}")
        logger.error("Erro fatal", exc_info=True)


if __name__ == "__main__":
    main()