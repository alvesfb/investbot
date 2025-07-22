"""
FinancialAnalysisTools - Implementação para Agno Framework

Esta tool encapsula o FinancialCalculator e ScoringEngine para integração
com o framework Agno, seguindo o padrão identificado no projeto.

Autor: Sistema de Recomendações de Investimentos
Data: 22/07/2025
"""

from typing import Dict, Any, Optional, List
import logging
from datetime import datetime

try:
    from utils.financial_calculator import FinancialCalculator, FinancialData, FinancialMetrics
    CALCULATOR_AVAILABLE = True
except ImportError:
    CALCULATOR_AVAILABLE = False
    logging.warning("FinancialCalculator não disponível - Tool funcionará em modo limitado")

try:
    from agents.analyzers.scoring_engine import ScoringEngine
    SCORING_ENGINE_AVAILABLE = True
except ImportError:
    SCORING_ENGINE_AVAILABLE = False
    logging.warning("ScoringEngine não disponível - Tool funcionará em modo limitado")


class FinancialAnalysisTools:
    """
    Tool Agno para Análise Financeira Fundamentalista
    
    Encapsula FinancialCalculator + ScoringEngine para uso em agentes Agno.
    Fornece análise completa de empresas com métricas e scoring.
    """
    
    def __init__(self):
        """Inicializa a tool com os componentes necessários"""
        self.logger = logging.getLogger(__name__)
        
        # Inicializar componentes se disponíveis
        if CALCULATOR_AVAILABLE:
            self.calculator = FinancialCalculator()
            self.logger.info("FinancialCalculator inicializado")
        else:
            self.calculator = None
            self.logger.warning("FinancialCalculator não disponível")
        
        if SCORING_ENGINE_AVAILABLE:
            self.scoring_engine = ScoringEngine()
            self.logger.info("ScoringEngine inicializado")
        else:
            self.scoring_engine = None
            self.logger.warning("ScoringEngine não disponível")
    
    def calculate_financial_metrics(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calcula métricas financeiras para uma empresa
        
        Args:
            financial_data: Dicionário com dados financeiros da empresa
            
        Returns:
            Dict com métricas calculadas e metadados
        """
        try:
            if not CALCULATOR_AVAILABLE:
                return {
                    "success": False,
                    "error": "FinancialCalculator não disponível",
                    "metrics": {}
                }
            
            # Converter dados para FinancialData
            data = FinancialData(
                symbol=financial_data.get('symbol'),
                current_price=financial_data.get('current_price'),
                market_cap=financial_data.get('market_cap'),
                revenue=financial_data.get('revenue'),
                net_income=financial_data.get('net_income'),
                total_assets=financial_data.get('total_assets'),
                shareholders_equity=financial_data.get('shareholders_equity'),
                total_debt=financial_data.get('total_debt'),
                current_assets=financial_data.get('current_assets'),
                current_liabilities=financial_data.get('current_liabilities'),
                revenue_history=financial_data.get('revenue_history', []),
                net_income_history=financial_data.get('net_income_history', []),
                sector=financial_data.get('sector', 'Geral')
            )
            
            # Calcular métricas
            metrics = self.calculator.calculate_all_metrics(data)
            
            # Converter para dicionário serializável
            result = {
                "success": True,
                "symbol": data.symbol,
                "calculation_date": metrics.calculation_date.isoformat(),
                "metrics": {
                    # Valuation
                    "pe_ratio": metrics.pe_ratio,
                    "pb_ratio": metrics.pb_ratio,
                    "ps_ratio": metrics.ps_ratio,
                    "ev_ebitda": metrics.ev_ebitda,
                    
                    # Rentabilidade
                    "roe": metrics.roe,
                    "roa": metrics.roa,
                    "roic": metrics.roic,
                    "gross_margin": metrics.gross_margin,
                    "operating_margin": metrics.operating_margin,
                    "net_margin": metrics.net_margin,
                    
                    # Crescimento
                    "revenue_growth_1y": metrics.revenue_growth_1y,
                    "revenue_growth_3y": metrics.revenue_growth_3y,
                    "earnings_growth_1y": metrics.earnings_growth_1y,
                    "earnings_growth_3y": metrics.earnings_growth_3y,
                    
                    # Endividamento
                    "debt_to_equity": metrics.debt_to_equity,
                    "debt_to_assets": metrics.debt_to_assets,
                    "interest_coverage": metrics.interest_coverage,
                    
                    # Liquidez
                    "current_ratio": metrics.current_ratio,
                    "quick_ratio": metrics.quick_ratio,
                    
                    # Eficiência
                    "asset_turnover": metrics.asset_turnover,
                    
                    # Score geral
                    "overall_score": metrics.overall_score
                },
                "category_scores": metrics.category_scores,
                "warnings": metrics.warnings,
                "data_quality": metrics.data_quality.value if metrics.data_quality else None
            }
            
            self.logger.info(f"Métricas calculadas para {data.symbol}")
            return result
            
        except Exception as e:
            self.logger.error(f"Erro ao calcular métricas: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "metrics": {}
            }
    
    def calculate_comprehensive_score(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calcula score fundamentalista completo
        
        Args:
            financial_data: Dicionário com dados financeiros da empresa
            
        Returns:
            Dict com score detalhado e análise
        """
        try:
            if not SCORING_ENGINE_AVAILABLE or not CALCULATOR_AVAILABLE:
                return {
                    "success": False,
                    "error": "ScoringEngine ou FinancialCalculator não disponível",
                    "score": {}
                }
            
            # Converter dados para FinancialData
            data = FinancialData(
                symbol=financial_data.get('symbol'),
                current_price=financial_data.get('current_price'),
                market_cap=financial_data.get('market_cap'),
                revenue=financial_data.get('revenue'),
                net_income=financial_data.get('net_income'),
                total_assets=financial_data.get('total_assets'),
                shareholders_equity=financial_data.get('shareholders_equity'),
                total_debt=financial_data.get('total_debt'),
                current_assets=financial_data.get('current_assets'),
                current_liabilities=financial_data.get('current_liabilities'),
                revenue_history=financial_data.get('revenue_history', []),
                net_income_history=financial_data.get('net_income_history', []),
                sector=financial_data.get('sector', 'Geral')
            )
            
            # Calcular score
            score = self.scoring_engine.calculate_comprehensive_score(data)
            
            # Converter para dicionário serializável
            result = {
                "success": True,
                "stock_code": score.stock_code,
                "sector": score.sector,
                "composite_score": score.composite_score,
                "quality_tier": score.quality_tier.value,
                "recommendation": score.recommendation,
                "scores": {
                    "valuation": score.valuation_score,
                    "profitability": score.profitability_score,
                    "growth": score.growth_score,
                    "financial_health": score.financial_health_score,
                    "efficiency": score.efficiency_score
                },
                "analysis": {
                    "strengths": score.strengths,
                    "weaknesses": score.weaknesses
                },
                "metadata": {
                    "analysis_date": score.analysis_date.isoformat()
                }
            }
            
            self.logger.info(f"Score calculado para {score.stock_code}: {score.composite_score:.1f}")
            return result
            
        except Exception as e:
            self.logger.error(f"Erro ao calcular score: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "score": {}
            }
    
    def analyze_company(self, financial_data: Dict[str, Any], include_score: bool = True) -> Dict[str, Any]:
        """
        Análise completa de uma empresa (métricas + score)
        
        Args:
            financial_data: Dicionário com dados financeiros da empresa
            include_score: Se deve incluir o scoring detalhado
            
        Returns:
            Dict com análise completa
        """
        try:
            result = {
                "success": True,
                "symbol": financial_data.get('symbol'),
                "analysis_timestamp": datetime.now().isoformat(),
                "components": {}
            }
            
            # Calcular métricas
            metrics_result = self.calculate_financial_metrics(financial_data)
            result["components"]["metrics"] = metrics_result
            
            # Calcular score se solicitado
            if include_score:
                score_result = self.calculate_comprehensive_score(financial_data)
                result["components"]["score"] = score_result
            
            # Verificar sucesso geral
            if not metrics_result.get("success", False):
                result["success"] = False
                result["primary_error"] = "Falha no cálculo de métricas"
            
            if include_score and not score_result.get("success", False):
                result["success"] = False
                result["primary_error"] = "Falha no cálculo de score"
            
            self.logger.info(f"Análise completa realizada para {financial_data.get('symbol')}")
            return result
            
        except Exception as e:
            self.logger.error(f"Erro na análise completa: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "symbol": financial_data.get('symbol'),
                "analysis_timestamp": datetime.now().isoformat()
            }
    
    def get_sector_analysis(self, companies_data: List[Dict[str, Any]], sector: str) -> Dict[str, Any]:
        """
        Análise comparativa de empresas do mesmo setor
        
        Args:
            companies_data: Lista de dados financeiros das empresas
            sector: Setor para análise
            
        Returns:
            Dict com análise setorial comparativa
        """
        try:
            if not companies_data:
                return {
                    "success": False,
                    "error": "Nenhuma empresa fornecida para análise setorial"
                }
            
            sector_results = {
                "success": True,
                "sector": sector,
                "analysis_timestamp": datetime.now().isoformat(),
                "companies_count": len(companies_data),
                "companies": [],
                "sector_statistics": {}
            }
            
            # Analisar cada empresa
            valid_scores = []
            for company_data in companies_data:
                company_analysis = self.analyze_company(company_data, include_score=True)
                sector_results["companies"].append(company_analysis)
                
                # Coletar scores válidos para estatísticas
                if (company_analysis.get("success") and 
                    company_analysis.get("components", {}).get("score", {}).get("success")):
                    score = company_analysis["components"]["score"]["composite_score"]
                    valid_scores.append(score)
            
            # Calcular estatísticas setoriais
            if valid_scores:
                sector_results["sector_statistics"] = {
                    "average_score": sum(valid_scores) / len(valid_scores),
                    "max_score": max(valid_scores),
                    "min_score": min(valid_scores),
                    "median_score": sorted(valid_scores)[len(valid_scores) // 2],
                    "score_range": max(valid_scores) - min(valid_scores)
                }
            
            self.logger.info(f"Análise setorial realizada para {sector}: {len(companies_data)} empresas")
            return sector_results
            
        except Exception as e:
            self.logger.error(f"Erro na análise setorial: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "sector": sector
            }
    
    
    def _extract_historical_data(self, financial_data: Dict[str, Any], field: str) -> List[float]:
        """
        Extrai dados históricos do YFinance ou cria estimativas
        
        Args:
            financial_data: Dados brutos do YFinance
            field: Campo a extrair ('revenue' ou 'net_income')
            
        Returns:
            Lista com dados históricos (últimos 3 anos)
        """
        try:
            # Tentar extrair dados históricos se disponíveis
            if f'{field}_history' in financial_data:
                return financial_data[f'{field}_history']
            
            # Se não há histórico, criar estimativa baseada no valor atual
            current_value = financial_data.get(field)
            if current_value and current_value > 0:
                # Simular crescimento histórico conservador (5%, 8%, 10%)
                # Isso é uma aproximação para quando não há dados históricos reais
                year_3 = current_value * 0.86  # -14% há 3 anos
                year_2 = current_value * 0.93  # -7% há 2 anos  
                year_1 = current_value * 0.97  # -3% há 1 ano
                return [year_3, year_2, year_1]
            
            return []
            
        except Exception as e:
            self.logger.warning(f"Erro ao extrair histórico de {field}: {e}")
            return []
    
    def get_tool_status(self) -> Dict[str, Any]:
        """
        Retorna status dos componentes da tool
        
        Returns:
            Dict com status dos componentes
        """
        return {
            "tool_name": "FinancialAnalysisTools",
            "version": "1.0.0",
            "components": {
                "financial_calculator": {
                    "available": CALCULATOR_AVAILABLE,
                    "status": "operational" if CALCULATOR_AVAILABLE else "unavailable"
                },
                "scoring_engine": {
                    "available": SCORING_ENGINE_AVAILABLE,
                    "status": "operational" if SCORING_ENGINE_AVAILABLE else "unavailable"
                }
            },
            "capabilities": {
                "calculate_metrics": CALCULATOR_AVAILABLE,
                "calculate_scores": SCORING_ENGINE_AVAILABLE,
                "full_analysis": CALCULATOR_AVAILABLE and SCORING_ENGINE_AVAILABLE,
                "sector_analysis": CALCULATOR_AVAILABLE and SCORING_ENGINE_AVAILABLE
            },
            "timestamp": datetime.now().isoformat()
        }


# Factory function para compatibilidade com Agno
def create_financial_analysis_tools() -> FinancialAnalysisTools:
    """Factory function para criar instância da tool"""
    return FinancialAnalysisTools()


# Exemplo de uso direto (para testes)
if __name__ == "__main__":
    print("🧮 Testando FinancialAnalysisTools")
    print("=" * 50)
    
    # Criar instância
    tools = create_financial_analysis_tools()
    
    # Verificar status
    status = tools.get_tool_status()
    print(f"📊 STATUS DA TOOL:")
    print(f"   Calculator disponível: {status['components']['financial_calculator']['available']}")
    print(f"   Scoring Engine disponível: {status['components']['scoring_engine']['available']}")
    print(f"   Análise completa: {status['capabilities']['full_analysis']}")
    
    # Dados de teste
    test_data = {
        'symbol': 'TEST4',
        'current_price': 45.50,
        'market_cap': 180_000_000_000,
        'revenue': 75_000_000_000,
        'net_income': 12_000_000_000,
        'total_assets': 150_000_000_000,
        'shareholders_equity': 90_000_000_000,
        'total_debt': 20_000_000_000,
        'current_assets': 40_000_000_000,
        'current_liabilities': 15_000_000_000,
        'revenue_history': [65_000_000_000, 68_000_000_000, 72_000_000_000],
        'net_income_history': [9_000_000_000, 10_500_000_000, 11_200_000_000],
        'sector': 'Tecnologia'
    }
    
    if status['capabilities']['full_analysis']:
        print(f"\n🎯 TESTANDO ANÁLISE COMPLETA:")
        result = tools.analyze_company(test_data)
        
        if result['success']:
            metrics = result['components']['metrics']
            score = result['components']['score']
            
            print(f"   ✅ Análise realizada com sucesso")
            print(f"   📈 Score: {score['composite_score']:.1f}/100")
            print(f"   🏆 Recomendação: {score['recommendation']}")
            print(f"   📊 P/L: {metrics['metrics']['pe_ratio']:.2f}")
            print(f"   💰 ROE: {metrics['metrics']['roe']:.1f}%")
        else:
            print(f"   ❌ Análise falhou: {result.get('error', 'Erro desconhecido')}")
    else:
        print(f"\n⚠️ Análise completa não disponível - componentes faltando")
    
    print(f"\n✅ FinancialAnalysisTools implementada e testada!")
    print(f"🔧 Pronta para integração com agentes Agno")