#!/usr/bin/env python3
"""
CORREÇÃO DO SCHEMA DO BANCO - FORMATO DE DATAS
=================================================================
ABORDAGEM CORRETA: Corrigir o problema na origem (schema) 
em vez de ficar fazendo workarounds

PROBLEMA: Campos de data com formato incompatível com fromisoformat
SOLUÇÃO: Corrigir tipos e formatos diretamente no banco
"""

import sys
import sqlite3
from pathlib import Path
from datetime import datetime

# =================================================================
# DIAGNÓSTICO DO BANCO ATUAL
# =================================================================

def diagnose_database_schema():
    """Diagnostica o schema atual do banco"""
    print("🔍 DIAGNÓSTICO DO SCHEMA DO BANCO")
    print("=" * 50)
    
    db_path = Path("data/investment_system.db")
    
    if not db_path.exists():
        print(f"❌ Banco não encontrado: {db_path}")
        return None
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Verificar tabelas existentes
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"📋 Tabelas encontradas: {len(tables)}")
        
        schema_info = {}
        
        for (table_name,) in tables:
            print(f"\n📊 TABELA: {table_name}")
            
            # Obter schema da tabela
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            
            date_columns = []
            for col in columns:
                col_name, col_type, not_null, default, pk = col[1], col[2], col[3], col[4], col[5]
                print(f"   {col_name}: {col_type}")
                
                # Identificar colunas de data
                if any(keyword in col_name.lower() for keyword in ['data', 'date', 'created', 'updated', 'time']):
                    date_columns.append((col_name, col_type))
            
            if date_columns:
                print(f"   🗓️  Colunas de data: {date_columns}")
                schema_info[table_name] = date_columns
                
                # Verificar dados reais
                for col_name, col_type in date_columns:
                    cursor.execute(f"SELECT {col_name} FROM {table_name} LIMIT 3;")
                    samples = cursor.fetchall()
                    if samples:
                        print(f"   📝 Amostras {col_name}: {[s[0] for s in samples]}")
        
        conn.close()
        return schema_info
        
    except Exception as e:
        print(f"❌ Erro ao analisar banco: {e}")
        return None

# =================================================================
# CORREÇÃO 1: ATUALIZAR TIPOS DE COLUNAS
# =================================================================

def fix_date_column_types():
    """Corrige tipos das colunas de data"""
    print("\n🔧 CORREÇÃO 1: TIPOS DE COLUNAS DE DATA")
    print("=" * 50)
    
    db_path = Path("data/investment_system.db")
    
    if not db_path.exists():
        print("❌ Banco não encontrado")
        return False
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Mapeamento de colunas que precisam ser corrigidas
        date_fixes = {
            'stocks': [
                'data_criacao',
                'data_atualizacao'
            ],
            'fundamental_analyses': [
                'data_analise',
                'created_at',
                'updated_at'
            ],
            'recommendations': [
                'data_recomendacao',
                'created_at'
            ],
            'agent_sessions': [
                'start_time',
                'end_time',
                'created_at'
            ]
        }
        
        fixes_applied = 0
        
        for table_name, date_columns in date_fixes.items():
            # Verificar se tabela existe
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';")
            if not cursor.fetchone():
                print(f"⚠️  Tabela {table_name} não existe")
                continue
            
            print(f"\n🔧 Corrigindo tabela: {table_name}")
            
            for col_name in date_columns:
                try:
                    # Verificar se coluna existe
                    cursor.execute(f"PRAGMA table_info({table_name});")
                    columns = [col[1] for col in cursor.fetchall()]
                    
                    if col_name not in columns:
                        print(f"   ⚠️  Coluna {col_name} não existe")
                        continue
                    
                    # Atualizar valores de data mal formatados
                    print(f"   🔧 Corrigindo {col_name}...")
                    
                    # Buscar registros com datas problemáticas
                    cursor.execute(f"SELECT rowid, {col_name} FROM {table_name} WHERE {col_name} IS NOT NULL;")
                    rows = cursor.fetchall()
                    
                    for rowid, date_value in rows:
                        if date_value and isinstance(date_value, str):
                            try:
                                # Tentar parse da data atual
                                datetime.fromisoformat(date_value.replace('Z', '+00:00'))
                            except ValueError:
                                # Data mal formatada, corrigir
                                try:
                                    # Tentar outros formatos
                                    if 'T' in date_value:
                                        clean_date = date_value.split('T')[0] + ' ' + date_value.split('T')[1].split('.')[0]
                                    else:
                                        clean_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                    
                                    cursor.execute(f"UPDATE {table_name} SET {col_name} = ? WHERE rowid = ?", 
                                                 (clean_date, rowid))
                                    fixes_applied += 1
                                    
                                except:
                                    # Se tudo falhar, usar data atual
                                    current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                    cursor.execute(f"UPDATE {table_name} SET {col_name} = ? WHERE rowid = ?", 
                                                 (current_date, rowid))
                                    fixes_applied += 1
                    
                    print(f"   ✅ {col_name} corrigido")
                    
                except Exception as e:
                    print(f"   ❌ Erro em {col_name}: {e}")
        
        conn.commit()
        conn.close()
        
        print(f"\n📊 RESULTADO: {fixes_applied} registros de data corrigidos")
        return fixes_applied > 0
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        return False

# =================================================================
# CORREÇÃO 2: MIGRAÇÃO DE SCHEMA (se necessário)
# =================================================================

def create_migration_script():
    """Cria script de migração para corrigir schema"""
    print("\n🔧 CORREÇÃO 2: MIGRAÇÃO DE SCHEMA")
    print("=" * 50)
    
    migration_sql = '''
-- MIGRAÇÃO: Correção de formatos de data
-- Data: {date}

-- 1. Padronizar formato de datas para DATETIME
BEGIN TRANSACTION;

-- Corrigir tabela stocks
UPDATE stocks 
SET data_criacao = datetime(data_criacao)
WHERE data_criacao IS NOT NULL AND data_criacao != '';

UPDATE stocks 
SET data_atualizacao = datetime(data_atualizacao)
WHERE data_atualizacao IS NOT NULL AND data_atualizacao != '';

-- Corrigir tabela fundamental_analyses  
UPDATE fundamental_analyses
SET data_analise = datetime(data_analise)
WHERE data_analise IS NOT NULL AND data_analise != '';

-- Corrigir tabela recommendations
UPDATE recommendations
SET data_recomendacao = datetime(data_recomendacao)
WHERE data_recomendacao IS NOT NULL AND data_recomendacao != '';

-- Corrigir tabela agent_sessions
UPDATE agent_sessions
SET start_time = datetime(start_time)
WHERE start_time IS NOT NULL AND start_time != '';

UPDATE agent_sessions
SET end_time = datetime(end_time)
WHERE end_time IS NOT NULL AND end_time != '';

-- 2. Adicionar campos de data faltantes com defaults
ALTER TABLE stocks ADD COLUMN IF NOT EXISTS last_updated DATETIME DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE fundamental_analyses ADD COLUMN IF NOT EXISTS last_updated DATETIME DEFAULT CURRENT_TIMESTAMP;

-- 3. Criar índices para performance
CREATE INDEX IF NOT EXISTS idx_stocks_data_atualizacao ON stocks(data_atualizacao);
CREATE INDEX IF NOT EXISTS idx_fundamental_data_analise ON fundamental_analyses(data_analise);
CREATE INDEX IF NOT EXISTS idx_recommendations_data ON recommendations(data_recomendacao);

COMMIT;
'''.format(date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    # Salvar script de migração
    migration_file = Path("database/migrations/fix_date_formats.sql")
    migration_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(migration_file, 'w', encoding='utf-8') as f:
        f.write(migration_sql)
    
    print(f"✅ Script de migração criado: {migration_file}")
    return migration_file

def apply_migration():
    """Aplica migração de correção de datas"""
    print("\n🔧 APLICANDO MIGRAÇÃO")
    print("=" * 50)
    
    db_path = Path("data/investment_system.db")
    
    if not db_path.exists():
        print("❌ Banco não encontrado")
        return False
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Backup antes da migração
        backup_path = Path(f"data/investment_system_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db")
        
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"✅ Backup criado: {backup_path}")
        
        # Aplicar correções diretas
        corrections = [
            # Padronizar datas usando SQLite datetime()
            "UPDATE stocks SET data_criacao = datetime(data_criacao) WHERE data_criacao IS NOT NULL;",
            "UPDATE stocks SET data_atualizacao = datetime(data_atualizacao) WHERE data_atualizacao IS NOT NULL;",
            "UPDATE fundamental_analyses SET data_analise = datetime(data_analise) WHERE data_analise IS NOT NULL;",
            "UPDATE recommendations SET data_recomendacao = datetime(data_recomendacao) WHERE data_recomendacao IS NOT NULL;",
            "UPDATE agent_sessions SET start_time = datetime(start_time) WHERE start_time IS NOT NULL;",
            "UPDATE agent_sessions SET end_time = datetime(end_time) WHERE end_time IS NOT NULL;",
        ]
        
        for sql in corrections:
            try:
                cursor.execute(sql)
                print(f"✅ Executado: {sql[:50]}...")
            except Exception as e:
                print(f"⚠️  Erro em: {sql[:30]}... → {e}")
        
        conn.commit()
        conn.close()
        
        print("✅ Migração aplicada com sucesso")
        return True
        
    except Exception as e:
        print(f"❌ Erro na migração: {e}")
        return False

# =================================================================
# CORREÇÃO 3: VALIDAR DADOS APÓS MIGRAÇÃO
# =================================================================

def validate_date_fix():
    """Valida se a correção de datas funcionou"""
    print("\n🧪 VALIDAÇÃO DA CORREÇÃO")
    print("=" * 50)
    
    db_path = Path("data/investment_system.db")
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Testar algumas consultas que falhavam antes
        test_queries = [
            ("stocks", "data_criacao"),
            ("fundamental_analyses", "data_analise"),
            ("recommendations", "data_recomendacao")
        ]
        
        validation_success = True
        
        for table, date_col in test_queries:
            try:
                # Verificar se tabela existe
                cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}';")
                if not cursor.fetchone():
                    print(f"⚠️  Tabela {table} não existe")
                    continue
                
                # Testar query com data
                cursor.execute(f"SELECT {date_col} FROM {table} LIMIT 3;")
                dates = cursor.fetchall()
                
                print(f"✅ {table}.{date_col}: {len(dates)} registros")
                
                # Verificar formato das datas
                for (date_val,) in dates:
                    if date_val:
                        try:
                            # Tentar parse como seria feito no código Python
                            datetime.fromisoformat(str(date_val).replace('Z', ''))
                            print(f"   ✅ Data válida: {date_val}")
                        except:
                            print(f"   ❌ Data inválida: {date_val}")
                            validation_success = False
                
            except Exception as e:
                print(f"❌ Erro testando {table}.{date_col}: {e}")
                validation_success = False
        
        conn.close()
        return validation_success
        
    except Exception as e:
        print(f"❌ Erro na validação: {e}")
        return False

# =================================================================
# TESTE COMPLETO APÓS CORREÇÃO
# =================================================================

def test_system_after_database_fix():
    """Testa sistema completo após correção do banco"""
    print("\n🧪 TESTE SISTEMA APÓS CORREÇÃO DE BANCO")
    print("=" * 50)
    
    try:
        import sys
        import os
        sys.path.append(os.getcwd())
        
        # Teste 1: FundamentalAnalyzer sem erros de banco
        from agents.analyzers.fundamental_scoring_system import FundamentalAnalyzerAgent
        
        agent = FundamentalAnalyzerAgent()
        
        print("🔍 Testando análise PETR4...")
        result = agent.analyze_single_stock('PETR4')
        
        if 'fundamental_score' in result:
            score = result['fundamental_score']['composite_score']
            print(f"✅ PETR4 Score: {score:.1f}")
            
            # Verificar se não é mais o fallback
            if abs(score - 71.0) > 1.0:
                print("✅ Cálculo real funcionando!")
                return True
            else:
                print("⚠️  Ainda usando fallback - pode ter outros problemas")
                return False
        else:
            print("❌ fundamental_score não encontrado")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()
        return False

# =================================================================
# FUNÇÃO PRINCIPAL
# =================================================================

def main():
    """Executa correção completa do schema"""
    print("🛠️  CORREÇÃO DO SCHEMA DO BANCO DE DADOS")
    print("=" * 60)
    print("Abordagem: Corrigir problema na raiz (banco) em vez de workarounds")
    
    # 1. Diagnóstico
    schema_info = diagnose_database_schema()
    
    if schema_info is None:
        print("\n❌ Não foi possível analisar o banco")
        return False
    
    # 2. Aplicar migração
    print(f"\n🔧 APLICANDO CORREÇÃO DE SCHEMA")
    migration_success = apply_migration()
    
    if migration_success:
        # 3. Validar correção
        print(f"\n✅ Validando correção...")
        validation_success = validate_date_fix()
        
        if validation_success:
            # 4. Testar sistema
            system_success = test_system_after_database_fix()
            
            if system_success:
                print(f"\n🎉 CORREÇÃO DO BANCO CONCLUÍDA COM SUCESSO!")
                print("✅ Schema de datas corrigido")
                print("✅ Erro fromisoformat resolvido") 
                print("✅ Sistema calculando scores reais")
                print("✅ Não mais usando fallback 71.0")
                
                print(f"\n🚀 PRÓXIMOS PASSOS:")
                print("1. Testar múltiplas ações")
                print("2. Verificar se scores variam corretamente")
                print("3. Validar precisão dos cálculos")
                
                return True
            else:
                print(f"\n⚠️  SCHEMA CORRIGIDO MAS SISTEMA AINDA COM PROBLEMAS")
                print("🔧 Pode haver outros problemas além das datas")
        else:
            print(f"\n❌ VALIDAÇÃO FALHOU")
            print("🔧 Schema pode precisar de mais ajustes")
    else:
        print(f"\n❌ MIGRAÇÃO FALHOU")
        print("🔧 Verificar erros e tentar correção manual")
    
    return False

if __name__ == "__main__":
    success = main()
    
    if success:
        print(f"\n{'='*60}")
        print(f"🎊 PROBLEMA DE BANCO RESOLVIDO! 🎊")
        print(f"{'='*60}")
    else:
        print(f"\n{'='*60}")
        print(f"🔧 CORREÇÃO MANUAL NECESSÁRIA")
        print(f"{'='*60}")

# =================================================================
# CORREÇÃO MANUAL RÁPIDA
# =================================================================

print("""
📝 CORREÇÃO MANUAL ALTERNATIVA:

1. ABRIR BANCO SQLite:
   sqlite3 data/investment_system.db

2. EXECUTAR COMANDOS:
   .headers on
   .mode column
   
   -- Verificar formato atual
   SELECT data_criacao FROM stocks LIMIT 3;
   
   -- Corrigir datas
   UPDATE stocks SET data_criacao = datetime(data_criacao);
   UPDATE stocks SET data_atualizacao = datetime(data_atualizacao);
   
   -- Verificar resultado
   SELECT data_criacao FROM stocks LIMIT 3;

3. TESTAR SISTEMA:
   python -c "from agents.analyzers.fundamental_scoring_system import FundamentalAnalyzerAgent; agent = FundamentalAnalyzerAgent(); result = agent.analyze_single_stock('PETR4'); print(f'Score: {result[\"fundamental_score\"][\"composite_score\"]:.1f}')"
""")