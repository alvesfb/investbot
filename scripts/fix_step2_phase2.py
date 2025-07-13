#!/usr/bin/env python3
"""
FIX DIRETO - Adicionar ScoringEngine ao fundamental_scoring_system.py

PROBLEMA IDENTIFICADO:
O teste falha porque tenta importar:
`from agents.analyzers.fundamental_scoring_system import ScoringEngine`

Mas a classe ScoringEngine NÃO EXISTE no arquivo fundamental_scoring_system.py

SOLUÇÃO:
Adicionar a classe ScoringEngine diretamente no arquivo fundamental_scoring_system.py
"""

import sys
from pathlib import Path

def fix_scoring_engine_direct():
    """Fix direto adicionando ScoringEngine ao arquivo principal"""
    
    print("🔧 FIX DIRETO - ADICIONANDO SCORINGENGINE")
    print("=" * 50)
    
    project_root = Path.cwd()
    main_file = project_root / "agents" / "analyzers" / "fundamental_scoring_system.py"
    
    if not main_file.exists():
        print(f"❌ Arquivo não encontrado: {main_file}")
        return False
    
    # Ler arquivo atual
    with open(main_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar se ScoringEngine já existe
    if "class ScoringEngine" in content:
        print("ℹ️  ScoringEngine já existe no arquivo")
        return True
    
    print("📝 Adicionando classe ScoringEngine...")
    
    # Código da classe ScoringEngine para adicionar
    scoring_engine_code = '''
# =================================================================
# SCORING ENGINE - ADICIONADO PARA CORRIGIR IMPORT
# =================================================================

class ScoringEngine:
    """
    Motor de Scoring Fundamentalista
    
    CORREÇÃO: Esta classe resolve o erro de import identificado no teste.
    """
    
    def __init__(self, weights: Optional[ScoringWeights] = None):
        self.weights = weights or ScoringWeights()
        self.logger = logging.getLogger(__name__)
        
        if not self.weights.validate():
            self.logger.warning("Pesos não somam 1.0, normalizando...")
            self._normalize_weights()
        
        self._sector_benchmarks = {}
        self._percentile_cache = {}
        
        self.logger.info("ScoringEngine inicializado com sucesso")
    
    def _normalize_weights(self):
        """Normaliza os pesos para somar 1.0"""
        total = sum([self.weights.valuation, self.weights.profitability, 
                    self.weights.growth, self.weights.financial_health, 
                    self.weights.efficiency])
        
        if total > 0:
            self.weights.valuation /= total
            self.weights.profitability /= total
            self.weights.growth /= total
            self.weights.financial_health /= total
            self.weights.efficiency /= total
    
    def calculate_valuation_score(self, metrics: Dict[str, Any], 
                                sector_benchmarks: Optional[Dict[str, float]] = None) -> float:
        """Calcula score de valuation (0-100)"""
        try:
            score_components = []
            
            # P/L Score (menor é melhor)
            pe_ratio = metrics.get('pe_ratio')
            if pe_ratio and pe_ratio > 0:
                if pe_ratio <= 8:
                    pe_score = 100
                elif pe_ratio <= 15:
                    pe_score = 100 - ((pe_ratio - 8) / 7) * 30
                elif pe_ratio <= 25:
                    pe_score = 70 - ((pe_ratio - 15) / 10) * 50
                else:
                    pe_score = max(0, 20 - ((pe_ratio - 25) / 10) * 20)
                
                score_components.append(pe_score * 0.4)
            
            # P/VP Score
            pb_ratio = metrics.get('pb_ratio')
            if pb_ratio and pb_ratio > 0:
                if pb_ratio <= 0.8:
                    pb_score = 100
                elif pb_ratio <= 2.0:
                    pb_score = 100 - ((pb_ratio - 0.8) / 1.2) * 30
                elif pb_ratio <= 4.0:
                    pb_score = 70 - ((pb_ratio - 2.0) / 2.0) * 50
                else:
                    pb_score = max(0, 20 - ((pb_ratio - 4.0) / 2.0) * 20)
                
                score_components.append(pb_score * 0.3)
            
            if score_components:
                total_weight = sum([0.4, 0.3][:len(score_components)])
                final_score = sum(score_components) / total_weight
                return max(0, min(100, final_score))
            else:
                return 50.0
            
        except Exception as e:
            self.logger.error(f"Erro no cálculo de valuation: {e}")
            return 50.0
    
    def calculate_profitability_score(self, metrics: Dict[str, Any], 
                                    sector_benchmarks: Optional[Dict[str, float]] = None) -> float:
        """Calcula score de rentabilidade (0-100)"""
        try:
            score_components = []
            
            # ROE Score (maior é melhor)
            roe = metrics.get('roe')
            if roe is not None:
                if roe >= 25:
                    roe_score = 100
                elif roe >= 20:
                    roe_score = 90 + ((roe - 20) / 5) * 10
                elif roe >= 15:
                    roe_score = 70 + ((roe - 15) / 5) * 20
                elif roe >= 10:
                    roe_score = 40 + ((roe - 10) / 5) * 30
                elif roe >= 0:
                    roe_score = (roe / 10) * 40
                else:
                    roe_score = 0
                
                score_components.append(roe_score)
            
            if score_components:
                return max(0, min(100, sum(score_components) / len(score_components)))
            else:
                return 50.0
            
        except Exception as e:
            self.logger.error(f"Erro no cálculo de rentabilidade: {e}")
            return 50.0
    
    def calculate_growth_score(self, metrics: Dict[str, Any], 
                             sector_benchmarks: Optional[Dict[str, float]] = None) -> float:
        """Calcula score de crescimento (0-100)"""
        try:
            revenue_growth = metrics.get('revenue_growth_3y', 8.0)
            
            if revenue_growth >= 20:
                return 100
            elif revenue_growth >= 15:
                return 85 + ((revenue_growth - 15) / 5) * 15
            elif revenue_growth >= 10:
                return 65 + ((revenue_growth - 10) / 5) * 20
            elif revenue_growth >= 5:
                return 40 + ((revenue_growth - 5) / 5) * 25
            elif revenue_growth >= 0:
                return 20 + (revenue_growth / 5) * 20
            else:
                return max(0, 20 + revenue_growth * 2)
            
        except Exception as e:
            self.logger.error(f"Erro no cálculo de crescimento: {e}")
            return 50.0
    
    def calculate_financial_health_score(self, metrics: Dict[str, Any], 
                                       sector_benchmarks: Optional[Dict[str, float]] = None) -> float:
        """Calcula score de saúde financeira (0-100)"""
        try:
            score_components = []
            
            # Dívida/EBITDA Score
            debt_ebitda = metrics.get('debt_ebitda', 2.5)
            if debt_ebitda <= 1:
                debt_score = 100
            elif debt_ebitda <= 2:
                debt_score = 85 - ((debt_ebitda - 1) / 1) * 15
            elif debt_ebitda <= 3:
                debt_score = 60 - ((debt_ebitda - 2) / 1) * 25
            elif debt_ebitda <= 4:
                debt_score = 30 - ((debt_ebitda - 3) / 1) * 30
            else:
                debt_score = max(0, 30 - ((debt_ebitda - 4) / 2) * 30)
            
            score_components.append(debt_score)
            
            # Current Ratio Score
            current_ratio = metrics.get('current_ratio', 1.5)
            if current_ratio >= 2.0:
                cr_score = 100
            elif current_ratio >= 1.5:
                cr_score = 80 + ((current_ratio - 1.5) / 0.5) * 20
            elif current_ratio >= 1.2:
                cr_score = 60 + ((current_ratio - 1.2) / 0.3) * 20
            elif current_ratio >= 1.0:
                cr_score = 40 + ((current_ratio - 1.0) / 0.2) * 20
            else:
                cr_score = (current_ratio / 1.0) * 40
            
            score_components.append(cr_score)
            
            return max(0, min(100, sum(score_components) / len(score_components)))
            
        except Exception as e:
            self.logger.error(f"Erro no cálculo de saúde financeira: {e}")
            return 50.0
    
    def calculate_efficiency_score(self, metrics: Dict[str, Any], 
                                 sector_benchmarks: Optional[Dict[str, float]] = None) -> float:
        """Calcula score de eficiência (0-100)"""
        try:
            asset_turnover = metrics.get('asset_turnover', 0.8)
            
            if asset_turnover >= 1.5:
                return 100
            elif asset_turnover >= 1.0:
                return 70 + ((asset_turnover - 1.0) / 0.5) * 30
            elif asset_turnover >= 0.5:
                return 40 + ((asset_turnover - 0.5) / 0.5) * 30
            else:
                return (asset_turnover / 0.5) * 40
            
        except Exception as e:
            self.logger.error(f"Erro no cálculo de eficiência: {e}")
            return 50.0
    
    def calculate_composite_score(self, metrics: Dict[str, Any], 
                                sector: Optional[str] = None) -> Tuple[float, Dict[str, float]]:
        """Calcula o score composto final (0-100)"""
        try:
            # Calcular scores individuais
            scores = {
                'valuation': self.calculate_valuation_score(metrics),
                'profitability': self.calculate_profitability_score(metrics),
                'growth': self.calculate_growth_score(metrics),
                'financial_health': self.calculate_financial_health_score(metrics),
                'efficiency': self.calculate_efficiency_score(metrics)
            }
            
            # Score composto ponderado
            composite_score = (
                scores['valuation'] * self.weights.valuation +
                scores['profitability'] * self.weights.profitability +
                scores['growth'] * self.weights.growth +
                scores['financial_health'] * self.weights.financial_health +
                scores['efficiency'] * self.weights.efficiency
            )
            
            # Garantir que está no range 0-100
            composite_score = max(0, min(100, composite_score))
            
            return composite_score, scores
            
        except Exception as e:
            self.logger.error(f"Erro no cálculo do score composto: {e}")
            return 50.0, {'valuation': 50, 'profitability': 50, 'growth': 50, 
                         'financial_health': 50, 'efficiency': 50}
    
    def get_quality_tier(self, score: float) -> QualityTier:
        """Determina o tier de qualidade baseado no score"""
        if score >= 85:
            return QualityTier.EXCELLENT
        elif score >= 70:
            return QualityTier.GOOD
        elif score >= 50:
            return QualityTier.AVERAGE
        elif score >= 30:
            return QualityTier.BELOW_AVERAGE
        else:
            return QualityTier.POOR
    
    def apply_quality_filters(self, metrics: Dict[str, Any]) -> Dict[str, bool]:
        """Aplica filtros de qualidade fundamentalista"""
        filters = {}
        
        try:
            # Filtro ROE > 15%
            roe = metrics.get('roe')
            filters['roe_above_15'] = roe is not None and roe >= 15.0
            
            # Filtro crescimento sustentável
            revenue_growth = metrics.get('revenue_growth_3y')
            filters['sustainable_growth'] = revenue_growth is not None and revenue_growth >= 5.0
            
            # Filtro endividamento controlado
            debt_ebitda = metrics.get('debt_ebitda')
            filters['controlled_debt'] = debt_ebitda is None or debt_ebitda <= 4.0
            
            # Filtro margens estáveis
            net_margin = metrics.get('net_margin')
            filters['stable_margins'] = net_margin is not None and net_margin >= 5.0
            
            # Score geral dos filtros
            passed_filters = sum(1 for passed in filters.values() if passed)
            total_filters = len(filters)
            filters['quality_score'] = (passed_filters / total_filters) * 100
            
            return filters
            
        except Exception as e:
            self.logger.error(f"Erro na aplicação de filtros: {e}")
            return {'quality_score': 50.0}
    
    def identify_red_flags(self, metrics: Dict[str, Any]) -> List[str]:
        """Identifica red flags em empresas problemáticas"""
        red_flags = []
        
        try:
            # ROE negativo
            roe = metrics.get('roe')
            if roe is not None and roe < 0:
                red_flags.append("ROE negativo")
            
            # Endividamento excessivo
            debt_ebitda = metrics.get('debt_ebitda')
            if debt_ebitda is not None and debt_ebitda > 6:
                red_flags.append("Endividamento excessivo")
            
            # Margem líquida negativa
            net_margin = metrics.get('net_margin')
            if net_margin is not None and net_margin < 0:
                red_flags.append("Margem líquida negativa")
            
            # Queda de receita
            revenue_growth = metrics.get('revenue_growth_3y')
            if revenue_growth is not None and revenue_growth < -10:
                red_flags.append("Queda acentuada de receita")
            
            return red_flags
            
        except Exception as e:
            self.logger.error(f"Erro na identificação de red flags: {e}")
            return []
    
    def get_recommendation(self, score: float, quality_filters: Dict[str, bool], 
                          red_flags: List[str]) -> str:
        """Gera recomendação baseada no score e filtros"""
        try:
            # Se há muitos red flags, recomendação negativa
            if len(red_flags) >= 3:
                return "VENDA FORTE"
            elif len(red_flags) >= 2:
                return "VENDA"
            
            # Baseado no score e filtros
            quality_score = quality_filters.get('quality_score', 50.0)
            
            if score >= 85 and quality_score >= 80:
                return "COMPRA FORTE"
            elif score >= 70 and quality_score >= 70:
                return "COMPRA"
            elif score >= 50 and quality_score >= 60:
                return "NEUTRO"
            elif score >= 30:
                return "VENDA"
            else:
                return "VENDA FORTE"
            
        except Exception as e:
            self.logger.error(f"Erro na geração de recomendação: {e}")
            return "NEUTRO"

'''
    
    # Encontrar onde inserir (antes da classe FundamentalAnalyzerAgent)
    if "class FundamentalAnalyzerAgent" in content:
        insert_position = content.find("class FundamentalAnalyzerAgent")
        
        # Inserir a classe ScoringEngine antes do FundamentalAnalyzerAgent
        new_content = (
            content[:insert_position] + 
            scoring_engine_code + 
            "\n# =================================================================\n" +
            "# AGENTE ANALISADOR ORIGINAL\n" +
            "# =================================================================\n\n" +
            content[insert_position:]
        )
        
        # Salvar arquivo modificado
        with open(main_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✅ ScoringEngine adicionado ao arquivo: {main_file}")
        print("✅ Classe inserida antes de FundamentalAnalyzerAgent")
        
        return True
    else:
        print("❌ Não foi possível encontrar FundamentalAnalyzerAgent no arquivo")
        return False

def test_fix():
    """Testa se o fix funcionou"""
    print("\n🧪 TESTANDO O FIX")
    print("=" * 30)
    
    try:
        # Tentar import que estava falhando
        sys.path.append('agents/analyzers')
        from agents.analyzers.fundamental_scoring_system import ScoringEngine, FundamentalAnalyzerAgent
        
        print("✅ Import ScoringEngine: SUCESSO")
        
        # Testar criação
        engine = ScoringEngine()
        print("✅ Criação ScoringEngine: SUCESSO")
        
        # Testar agente
        agent = FundamentalAnalyzerAgent()
        print("✅ Criação FundamentalAnalyzerAgent: SUCESSO")
        
        print("\n🎉 FIX APLICADO COM SUCESSO!")
        print("O erro de import foi resolvido")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import ainda falhando: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

def main():
    """Função principal"""
    print("🚀 FIX DIRETO - RESOLVER ERRO DE IMPORT SCORINGENGINE")
    print("=" * 60)
    print("Problema: ScoringEngine não existe em fundamental_scoring_system.py")
    print("Solução: Adicionar classe diretamente no arquivo")
    print("=" * 60)
    
    # Aplicar fix
    success = fix_scoring_engine_direct()
    
    if success:
        # Testar fix
        test_success = test_fix()
        
        if test_success:
            print("\n✅ PROBLEMA RESOLVIDO!")
            print("🔧 Execute novamente o teste de validação:")
            print("   python validation_final_fase2.py")
        else:
            print("\n❌ Fix aplicado mas teste ainda falha")
    else:
        print("\n❌ Falha ao aplicar fix")
    
    return success

if __name__ == "__main__":
    main()
