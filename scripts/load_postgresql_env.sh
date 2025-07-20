#!/bin/bash
# Script para carregar ambiente PostgreSQL

echo "🔄 Carregando ambiente PostgreSQL..."

# Carregar variáveis do .env.postgresql
if [ -f ".env.postgresql" ]; then
    export $(cat .env.postgresql | grep -v '^#' | xargs)
    echo "✅ Variáveis PostgreSQL carregadas"
else
    echo "❌ Arquivo .env.postgresql não encontrado"
    exit 1
fi

# Verificar se PostgreSQL está rodando
if docker-compose -f docker-compose.postgresql.yml ps postgres | grep -q "Up"; then
    echo "✅ PostgreSQL está rodando"
else
    echo "⚠️  PostgreSQL não está rodando - iniciando..."
    docker-compose -f docker-compose.postgresql.yml up -d postgres
    sleep 5
fi

echo "🎯 Ambiente PostgreSQL pronto!"
echo ""
echo "📊 URLs de acesso:"
echo "   PostgreSQL: localhost:5432"
echo "   pgAdmin: http://localhost:5050"
echo "   Redis: localhost:6379"
echo ""
echo "🔐 Credenciais:"
echo "   DB User: $POSTGRES_USER"
echo "   DB Name: $POSTGRES_DB"
echo "   pgAdmin: admin@investment.local / pgadmin_secure_2024"
