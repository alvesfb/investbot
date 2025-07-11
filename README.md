# Sistema de Recomendações de Investimentos

> Sistema automatizado de análise e recomendações de ações do mercado brasileiro usando Agno Framework + Claude API

## 🎯 Visão Geral

Sistema inteligente que combina análise fundamentalista, técnica e macroeconômica para gerar recomendações de investimento em ações brasileiras, focado em operações de swing trade (2-30 dias).

### Principais Características

- **Multi-agente**: Sistema baseado em Agno Framework com agentes especializados
- **Análise Híbrida**: Fundamentalista + Técnica + Macro
- **Automação**: Processamento diário automatizado
- **Interface Intuitiva**: Dashboard baseado em Agent UI
- **APIs Robustas**: FastAPI para integração externa

## 🚀 Quick Start

### Pré-requisitos

- Python 3.11+
- Git
- Docker (opcional)
- Chave da API do Claude (Anthropic)

### Instalação Rápida

```bash
# 1. Clone o repositório
git clone <your-repo-url>
cd investbot

# 2. Execute o script de setup
chmod +x scripts/setup.sh
./scripts/setup.sh

# 3. Configure suas chaves de API no arquivo .env
nano .env

# 4. Ative o ambiente virtual
source venv/bin/activate

# 5. Execute o sistema
python -m api.main
```

### Usando Docker

```bash
# Construir e executar com Docker Compose
docker-compose up -d

# Ver logs
docker-compose logs -f investbot
```

## 📁 Estrutura do Projeto

```
investbot/
├── agents/                 # Agentes Agno especializados
│   ├── collectors/        # Agentes de coleta de dados
│   ├── analyzers/         # Agentes de análise
│   └── recommenders/      # Agentes de recomendação
├── database/              # Modelos e persistência
│   ├── models/           # Modelos SQLAlchemy
│   ├── migrations/       # Migrações Alembic
│   └── repositories/     # Camada de acesso a dados
├── api/                   # APIs FastAPI
│   ├── endpoints/        # Endpoints REST
│   ├── schemas/          # Schemas Pydantic
│   └── dependencies/     # Dependências FastAPI
├── frontend/              # Interface Agent UI
├── config/                # Configurações centralizadas
├── tests/                 # Testes automatizados
├── data/                  # Dados locais (SQLite, CSV)
├── logs/                  # Logs do sistema
├── docker/                # Configurações Docker
└── scripts/               # Scripts de manutenção
```

## 🤖 Arquitetura de Agentes

### Fase 1: MVP (Atual)
- **Agente Coletor**: Coleta dados via MCP YFinance
- **Agente Analisador**: Análise fundamentalista básica
- **Agente Recomendador**: Gera recomendações iniciais

### Fases Futuras
- **Agente Técnico**: Análise técnica avançada (Fase 5)
- **Agente Macro**: Contexto macroeconômico (Fase 7)
- **Agente Gestor**: Gestão de carteira (Fase 6)

## 🔧 Configuração

### Variáveis de Ambiente Essenciais

```env
# Claude API (OBRIGATÓRIO)
ANTHROPIC_API_KEY=sk-ant-api03-...

# Ambiente
ENVIRONMENT=development
DEBUG=true

# Database
DATABASE_URL=sqlite:///./data/investment_system.db

# APIs Externas (opcional)
ALPHA_VANTAGE_API_KEY=your_key_here
```

### Configuração Avançada

Edite `config/settings.py` para ajustar:
- Parâmetros dos agentes
- Thresholds de classificação
- Rate limiting
- Logging

## 🚦 Uso Básico

### 1. Iniciar o Sistema

```bash
# Ambiente virtual
source venv/bin/activate

# Executar API
uvicorn api.main:app --reload

# Ou usar o script direto
python -m api.main
```

### 2. Acessar Interfaces

- **API Docs**: http://localhost:8000/docs
- **Agent UI**: http://localhost:3000 (quando disponível)
- **Health Check**: http://localhost:8000/health

### 3. Executar Análises

```bash
# Via CLI (futuro)
python -m agents.collectors.stock_collector --stocks PETR4,VALE3

# Via API
curl -X POST "http://localhost:8000/api/v1/analyze/PETR4"
```

## 📊 APIs Disponíveis

### Endpoints Principais

```http
GET    /health                    # Health check
GET    /api/v1/recommendations    # Últimas recomendações
POST   /api/v1/analyze/{stock}    # Análise individual
GET    /api/v1/stocks             # Lista de ações
POST   /api/v1/portfolio/upload   # Upload de carteira
```

### Exemplo de Response

```json
{
  "stock": "PETR4",
  "recommendation": "COMPRA",
  "score": 78.5,
  "justification": "Empresa com fundamentos sólidos...",
  "stop_loss": 30.92,
  "target_price": 36.00,
  "analysis_date": "2025-07-11T10:30:00Z"
}
```

## 🧪 Testes

### Executar Testes

```bash
# Todos os testes
pytest

# Com cobertura
pytest --cov=. --cov-report=html

# Testes específicos
pytest tests/unit/agents/
pytest tests/integration/
```

### Tipos de Teste

- **Unit**: Testes de unidade para agentes e modelos
- **Integration**: Testes de integração com APIs
- **E2E**: Testes end-to-end do pipeline completo

## 📈 Roadmap de Desenvolvimento

### ✅ Fase 1: Fundação (Atual)
- [x] Setup inicial
- [x] Agente coletor básico
- [x] Banco de dados SQLite
- [x] API FastAPI básica

### 🔄 Fase 2: Análise Fundamentalista (Em andamento)
- [ ] Agente analisador fundamentalista
- [ ] Métricas: P/L, P/VPA, ROE, ROIC
- [ ] Score fundamentalista
- [ ] Pipeline automático

### 📅 Próximas Fases
- **Fase 3**: Recomendações básicas
- **Fase 4**: Automação e agendamento
- **Fase 5**: Análise técnica
- **Fase 6**: Gestão de carteira
- **Fase 7**: Contexto macro

## 🛠️ Desenvolvimento

### Setup do Ambiente de Desenvolvimento

```bash
# Instalar dependências de desenvolvimento
pip install -r requirements-dev.txt

# Configurar pre-commit hooks
pre-commit install

# Executar linting
black .
isort .
flake8 .
mypy .
```

### Adicionando Novos Agentes

1. Criar classe em `agents/`
2. Herdar de `AgnoAgent`
3. Implementar tools necessários
4. Adicionar testes
5. Documentar no README

### Contribuindo

1. Fork o projeto
2. Crie feature branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para branch (`git push origin feature/nova-funcionalidade`)
5. Abra Pull Request

## 📚 Documentação

### Links Úteis

- [Documentação Agno](https://docs.agno.ai)
- [FastAPI Docs](https://fastapi.tiangolo.com)
- [Claude API](https://docs.anthropic.com)
- [Arquitetura Detalhada](docs/architecture.md)
- [Guia de Deploy](docs/deployment.md)

### Troubleshooting

#### Problemas Comuns

**Erro de API Key**
```bash
# Verificar se .env está configurado
cat .env | grep ANTHROPIC_API_KEY
```

**Problemas de Database**
```bash
# Recriar banco de dados
rm data/investment_system.db
python -m database.init_db
```

**Dependências**
```bash
# Reinstalar ambiente
rm -rf venv
./scripts/setup.sh
```

## 📊 Monitoramento

### Logs

```bash
# Ver logs em tempo real
tail -f logs/investment_system.log

# Logs estruturados
python -c "
from loguru import logger
logger.info('Sistema funcionando')
"
```

### Métricas

- **Uptime**: Health checks automáticos
- **Performance**: Tempo de resposta das APIs
- **Qualidade**: Hit rate das recomendações
- **Dados**: Completude e atualização

## 🔒 Segurança

### Boas Práticas

- ✅ Chaves de API em variáveis de ambiente
- ✅ Validação de entrada com Pydantic
- ✅ Rate limiting implementado
- ✅ Logs de auditoria
- ✅ HTTPS em produção

### Compliance

- **LGPD**: Dados pessoais criptografados
- **CVM**: Disclaimers sobre riscos
- **Financeiro**: Não garantia de retorno

## 🎯 Métricas de Sucesso

### KPIs Principais

- **Retorno**: >15% anualizado
- **Hit Rate**: >60% recomendações positivas
- **Sharpe Ratio**: >1.5
- **Drawdown**: <15%
- **Uptime**: >99.5%

### Dashboards

- Performance vs Ibovespa
- Distribuição de recomendações
- Acurácia por setor
- Tempo de execução dos agentes

## 📞 Suporte

### Canais de Contato

- **Issues**: GitHub Issues para bugs e features
- **Discussions**: GitHub Discussions para dúvidas
- **Email**: [seu-email@dominio.com]
- **Discord**: [link-do-servidor] (futuro)

### FAQ

**Q: O sistema garante lucro?**
A: Não. Este é um sistema de análise que oferece recomendações baseadas em dados históricos. Investimentos sempre envolvem risco.

**Q: Posso usar para day trade?**
A: O sistema é otimizado para swing trade (2-30 dias). Para day trade, seria necessário adaptações.

**Q: Suporta criptomoedas?**
A: Atualmente apenas ações brasileiras (B3). Crypto pode ser adicionado futuramente.

## 📄 Licença

Este projeto está licenciado sob a MIT License - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🙏 Agradecimentos

- [Agno Framework](https://agno.ai) - Sistema multi-agente
- [Anthropic](https://anthropic.com) - Claude API
- [YFinance](https://github.com/ranaroussi/yfinance) - Dados financeiros
- [FastAPI](https://fastapi.tiangolo.com) - Framework web
- [B3](https://www.b3.com.br) - Dados do mercado brasileiro

---

**⚠️ Disclaimer**: Este sistema é para fins educacionais e de pesquisa. Não constitui recomendação de investimento. Sempre consulte um profissional qualificado antes de tomar decisões financeiras.

**🚀 Status**: Fase 1 (MVP) - Em desenvolvimento ativo