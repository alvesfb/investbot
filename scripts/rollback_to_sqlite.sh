#!/bin/bash
# Script de rollback para SQLite (caso necessário)

echo "⚠️  ROLLBACK PARA SQLITE"
echo "Tem certeza? Este comando reverterá TODA a migração PostgreSQL."
read -p "Digite 'CONFIRMA' para continuar: " confirm

if [ "$confirm" != "CONFIRMA" ]; then
    echo "❌ Rollback cancelado"
    exit 1
fi

echo "🔄 Executando rollback..."

# Parar PostgreSQL
docker-compose -f docker-compose.postgresql.yml down

# Restaurar arquivos SQLite
if [ -d "database/migration_archive" ]; then
    cp database/migration_archive/models_sqlite_old.py database/models.py 2>/dev/null
    cp database/migration_archive/connection_sqlite_old.py database/connection.py 2>/dev/null
    cp database/migration_archive/repositories_sqlite_old.py database/repositories.py 2>/dev/null
    cp config/settings_sqlite_old.py config/settings.py 2>/dev/null
fi

# Restaurar .env
if [ -f ".env.sqlite_backup" ]; then
    rm .env 2>/dev/null
    mv .env.sqlite_backup .env
fi

# Restaurar banco SQLite
if [ -f "database/sqlite_backup_*/investment_system.db" ]; then
    cp database/sqlite_backup_*/investment_system.db data/
fi

echo "✅ Rollback para SQLite concluído"
echo "Reinicie o sistema com: python -m database.init_db"
