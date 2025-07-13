# database/repository_patch.py
"""
Patch temporário para resolver problema da coluna 'industria'
"""

import sys
from pathlib import Path

# Setup path
current_dir = Path.cwd()
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

def get_stock_safe(stock_code: str):
    """Busca ação de forma segura, sem usar coluna 'industria'"""
    try:
        from database.repositories import get_stock_repository
        from database.connection import get_db_session
        from database.models import Stock
        
        # Usar sessão direta para evitar queries problemáticas
        with get_db_session() as db:
            stock = db.query(Stock).filter(Stock.codigo == stock_code.upper()).first()
            return stock
            
    except Exception as e:
        print(f"Erro na busca segura: {e}")
        return None

def test_safe_query():
    """Testa query segura"""
    stock = get_stock_safe("PETR4")
    if stock:
        print(f"✅ Query segura funcionou: {stock.codigo}")
        return True
    else:
        print("❌ Query segura falhou")
        return False

if __name__ == "__main__":
    test_safe_query()
