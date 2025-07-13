# utils/volume_analyzer.py
"""
Analisador de Volume - Helper para métricas de volume
"""

import sys
from pathlib import Path
from typing import Optional, Dict, Any

# Setup path
current_dir = Path.cwd()
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

def analyze_volume_metrics(stock_code: str) -> Dict[str, Any]:
    """
    Analisa métricas de volume de uma ação
    
    Args:
        stock_code: Código da ação
        
    Returns:
        Dict com métricas de volume
    """
    try:
        from database.repositories import get_stock_repository
        
        repo = get_stock_repository()
        stock = repo.get_stock_by_code(stock_code)
        
        if not stock:
            return {"error": f"Ação {stock_code} não encontrada"}
        
        # Extrair métricas de volume de forma segura
        volume_metrics = {
            "stock_code": stock_code,
            "volume_medio": getattr(stock, 'volume_medio', None),
            "last_analysis_date": getattr(stock, 'last_analysis_date', None),
            "preco_atual": getattr(stock, 'preco_atual', None)
        }
        
        # Calcular métricas derivadas
        if volume_metrics["last_analysis_date"] and volume_metrics["preco_atual"]:
            # Volume financeiro (volume * preço)
            volume_financeiro = volume_metrics["last_analysis_date"] * volume_metrics["preco_atual"]
            volume_metrics["volume_financeiro_90d"] = volume_financeiro
            
            # Classificação de liquidez
            if volume_financeiro > 50000000:  # R$ 50M
                liquidez = "Alta"
            elif volume_financeiro > 10000000:  # R$ 10M
                liquidez = "Média"
            elif volume_financeiro > 1000000:  # R$ 1M
                liquidez = "Baixa"
            else:
                liquidez = "Muito Baixa"
            
            volume_metrics["classificacao_liquidez"] = liquidez
        
        # Comparação entre volumes
        if volume_metrics["volume_medio"] and volume_metrics["last_analysis_date"]:
            ratio = volume_metrics["last_analysis_date"] / volume_metrics["volume_medio"]
            volume_metrics["ratio_90d_vs_medio"] = ratio
            
            if ratio > 1.2:
                volume_metrics["tendencia_volume"] = "Crescente"
            elif ratio < 0.8:
                volume_metrics["tendencia_volume"] = "Decrescente"
            else:
                volume_metrics["tendencia_volume"] = "Estável"
        
        return volume_metrics
        
    except Exception as e:
        return {"error": f"Erro na análise de volume: {str(e)}"}

def get_high_volume_stocks(min_volume_90d: float = 10000000) -> Dict[str, Any]:
    """
    Retorna ações com alto volume nos últimos 30 dias
    
    Args:
        min_volume_90d: Volume mínimo em 30 dias
        
    Returns:
        Lista de ações com alto volume
    """
    try:
        from database.repositories import get_stock_repository
        
        repo = get_stock_repository()
        stocks = repo.get_all_stocks()
        
        high_volume_stocks = []
        
        for stock in stocks:
            volume_90d = getattr(stock, 'last_analysis_date', None)
            
            if volume_90d and volume_90d >= min_volume_90d:
                preco = getattr(stock, 'preco_atual', None)
                volume_financeiro = (volume_90d * preco) if preco else None
                
                high_volume_stocks.append({
                    "codigo": stock.codigo,
                    "nome": getattr(stock, 'nome', 'N/A'),
                    "setor": getattr(stock, 'setor', 'N/A'),
                    "last_analysis_date": volume_90d,
                    "preco_atual": preco,
                    "volume_financeiro": volume_financeiro
                })
        
        # Ordenar por volume decrescente
        high_volume_stocks.sort(key=lambda x: x['last_analysis_date'], reverse=True)
        
        return {
            "total_stocks": len(high_volume_stocks),
            "min_volume_filter": min_volume_90d,
            "stocks": high_volume_stocks
        }
        
    except Exception as e:
        return {"error": f"Erro ao buscar ações de alto volume: {str(e)}"}

def test_volume_analyzer():
    """Testa o analisador de volume"""
    print("🧪 Testando analisador de volume...")
    
    try:
        # Teste 1: Análise individual
        result = analyze_volume_metrics("PETR4")
        
        if "error" in result:
            print(f"❌ Erro na análise: {result['error']}")
        else:
            print(f"✅ PETR4 Volume 90d: {result.get('last_analysis_date', 'N/A')}")
            print(f"   Liquidez: {result.get('classificacao_liquidez', 'N/A')}")
        
        # Teste 2: Ações de alto volume
        high_vol = get_high_volume_stocks(5000000)  # 5M mínimo
        
        if "error" in high_vol:
            print(f"❌ Erro no alto volume: {high_vol['error']}")
        else:
            print(f"✅ Ações de alto volume: {high_vol['total_stocks']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

if __name__ == "__main__":
    test_volume_analyzer()
