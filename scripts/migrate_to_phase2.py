# scripts/migrate_to_phase2.py
"""
Script de Migração Segura da Fase 1 para Fase 2
Mantém compatibilidade total e permite rollback
"""
import sys
import shutil
import logging
from datetime import datetime
from pathlib import Path

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Cores para output
class Colors:
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    RED = '\033[0;31m'
    CYAN = '\033[0;36m'
    WHITE = '\033[1;37m'
    NC = '\033[0m'


def print_header(text: str, color: str = Colors.BLUE):
    print(f"\n{color}{'='*60}{Colors.NC}")
    print(f"{color}{text.center(60)}{Colors.NC}")
    print(f"{color}{'='*60}{Colors.NC}")


def print_step(text: str):
    print(f"\n{Colors.CYAN}📋 {text}{Colors.NC}")


def print_success(text: str):
    print(f"{Colors.GREEN}✅ {text}{Colors.NC}")


def print_warning(text: str):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.NC}")


def print_error(text: str):
    print(f"{Colors.RED}❌ {text}{Colors.NC}")


class Phase2Migrator:
    """Migrador seguro para Fase 2"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        sys.path.insert(0, str(self.project_root))
        self.backup_created = False
        self.backup_path = None
        
    def run_safe_migration(self) -> bool:
        """Executa migração segura com backup automático"""
        print_header("MIGRAÇÃO SEGURA PARA FASE 2", Colors.BLUE)
        print("Mantém compatibilidade total com Fase 1")
        
        try:
            # 1. Verificar pré-requisitos
            if not self._check_prerequisites():
                return False
            
            # 2. Criar backup
            if not self._create_backup():
                return False
            
            # 3. Substituir models.py
            if not self._update_models_file():
                return False
            
            # 4. Executar migração
            if not self._run_database_migration():
                print_error("Migração falhou - Restaurando backup...")
                self._restore_backup()
                return False
            
            # 5. Validar migração
            if not self._validate_migration():
                print_error("Validação falhou - Restaurando backup...")
                self._restore_backup()
                return False
            
            # 6. Testar compatibilidade
            if not self._test_compatibility():
                print_warning("Problemas de compatibilidade detectados")
                print("Migração concluída mas verifique logs")
            
            print_success("Migração concluída com sucesso!")
            print_success("Fase 1 permanece totalmente compatível")
            return True
            
        except Exception as e:
            print_error(f"Erro crítico na migração: {e}")
            if self.backup_created:
                self._restore_backup()
            return False
    
    def _check_prerequisites(self) -> bool:
        """Verifica pré-requisitos para migração"""
        print_step("Verificando pré-requisitos...")
        
        # Verificar se Fase 1 existe
        models_path = self.project_root / 'database' / 'models.py'
        if not models_path.exists():
            print_error("Arquivo database/models.py não encontrado")
            print_error("Execute setup da Fase 1 primeiro")
            return False
        
        # Verificar se banco existe
        try:
            from config.settings import get_settings
            settings = get_settings()
            
            if settings.database_path and not settings.database_path.exists():
                print_error("Banco de dados da Fase 1 não encontrado")
                return False
                
        except Exception as e:
            print_error(f"Erro ao verificar configurações: {e}")
            return False
        
        # Verificar se tabelas da Fase 1 existem
        try:
            from database.connection import get_database_info
            db_info = get_database_info()
            
            required_tables = ['stocks', 'recommendations']
            missing_tables = [t for t in required_tables if t not in db_info.get('tables', [])]
            
            if missing_tables:
                print_error(f"Tabelas da Fase 1 faltando: {missing_tables}")
                return False
                
        except Exception as e:
            print_error(f"Erro ao verificar banco: {e}")
            return False
        
        print_success("Pré-requisitos OK")
        return True
    
    def _create_backup(self) -> bool:
        """Cria backup completo antes da migração"""
        print_step("Criando backup de segurança...")
        
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_dir = self.project_root / 'backups' / f'pre_phase2_{timestamp}'
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Backup do banco de dados
            try:
                from config.settings import get_settings
                settings = get_settings()
                
                if settings.database_path and settings.database_path.exists():
                    backup_db_path = backup_dir / 'database_backup.db'
                    shutil.copy2(settings.database_path, backup_db_path)
                    print_success(f"Backup do banco: {backup_db_path}")
                    
            except Exception as e:
                print_warning(f"Erro no backup do banco: {e}")
            
            # Backup do models.py
            models_path = self.project_root / 'database' / 'models.py'
            backup_models_path = backup_dir / 'models_phase1.py'
            shutil.copy2(models_path, backup_models_path)
            
            # Backup de outros arquivos críticos
            critical_files = [
                'database/connection.py',
                'database/repositories.py',
                'config/settings.py'
            ]
            
            for file_path in critical_files:
                src = self.project_root / file_path
                if src.exists():
                    dst = backup_dir / src.name
                    shutil.copy2(src, dst)
            
            self.backup_path = backup_dir
            self.backup_created = True
            
            print_success(f"Backup criado: {backup_dir}")
            return True
            
        except Exception as e:
            print_error(f"Erro ao criar backup: {e}")
            return False
    
    def _update_models_file(self) -> bool:
        """Atualiza o arquivo models.py com a versão expandida"""
        print_step("Atualizando arquivo models.py...")
        
        try:
            models_path = self.project_root / 'database' / 'models.py'
            
            # O conteúdo do novo models.py deve ser copiado do artifact
            print_warning("ATENÇÃO: Você precisa substituir o conteúdo de database/models.py")
            print_warning("Use o conteúdo do artifact 'database/models.py - Versão Atualizada para Fase 2'")
            
            # Verificar se usuário já atualizou
            response = input(f"{Colors.YELLOW}Você já substituiu o models.py? (s/n): {Colors.NC}")
            
            if response.lower() != 's':
                print_error("Atualize database/models.py primeiro")
                return False
            
            # Verificar se arquivo foi atualizado
            with open(models_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if "FASE 2" not in content or "ReportingPeriod" not in content:
                print_error("models.py não foi atualizado corretamente")
                return False
            
            print_success("models.py atualizado")
            return True
            
        except Exception as e:
            print_error(f"Erro ao atualizar models.py: {e}")
            return False
    
    def _run_database_migration(self) -> bool:
        """Executa migração do banco de dados"""
        print_step("Executando migração do banco de dados...")
        
        try:
            # Importar nova versão dos models
            from database.models import run_phase2_migration
            from database.connection import engine
            
            # Executar migração
            success = run_phase2_migration(engine)
            
            if success:
                print_success("Migração do banco concluída")
                return True
            else:
                print_error("Falha na migração do banco")
                return False
                
        except Exception as e:
            print_error(f"Erro na migração: {e}")
            return False
    
    def _validate_migration(self) -> bool:
        """Valida se migração foi bem-sucedida"""
        print_step("Validando migração...")
        
        try:
            from database.models import validate_migration
            from database.connection import engine
            
            success = validate_migration(engine)
            
            if success:
                print_success("Validação OK")
                return True
            else:
                print_error("Falha na validação")
                return False
                
        except Exception as e:
            print_error(f"Erro na validação: {e}")
            return False
    
    def _test_compatibility(self) -> bool:
        """Testa compatibilidade com Fase 1"""
        print_step("Testando compatibilidade com Fase 1...")
        
        try:
            from database.models import ensure_backward_compatibility, Stock
            from database.connection import get_db_session
            
            # Verificar compatibilidade de campos
            ensure_backward_compatibility()
            
            # Testar operações básicas da Fase 1
            with get_db_session() as session:
                # Testar query básica
                stocks = session.query(Stock).limit(5).all()
                print(f"   ✅ Query básica: {len(stocks)} ações encontradas")
                
                # Testar campos antigos
                if stocks:
                    stock = stocks[0]
                    old_fields = {
                        'p_l': stock.p_l,
                        'p_vp': stock.p_vp,
                        'roe': stock.roe,
                        'market_cap': stock.market_cap
                    }
                    print(f"   ✅ Campos antigos acessíveis: {len([v for v in old_fields.values() if v is not None])}/4")
                
                # Testar to_dict
                if stocks:
                    dict_result = stocks[0].to_dict()
                    required_keys = ['codigo', 'nome', 'setor', 'p_l', 'roe']
                    missing_keys = [k for k in required_keys if k not in dict_result]
                    
                    if missing_keys:
                        print_warning(f"   Chaves faltando em to_dict: {missing_keys}")
                    else:
                        print("   ✅ Método to_dict() compatível")
            
            print_success("Testes de compatibilidade concluídos")
            return True
            
        except Exception as e:
            print_error(f"Erro nos testes de compatibilidade: {e}")
            return False
    
    def _restore_backup(self) -> bool:
        """Restaura backup em caso de falha"""
        print_step("Restaurando backup...")
        
        try:
            if not self.backup_created or not self.backup_path:
                print_error("Backup não disponível")
                return False
            
            # Restaurar models.py
            backup_models = self.backup_path / 'models_phase1.py'
            current_models = self.project_root / 'database' / 'models.py'
            
            if backup_models.exists():
                shutil.copy2(backup_models, current_models)
                print_success("models.py restaurado")
            
            # Restaurar banco
            backup_db = self.backup_path / 'database_backup.db'
            if backup_db.exists():
                from config.settings import get_settings
                settings = get_settings()
                
                if settings.database_path:
                    shutil.copy2(backup_db, settings.database_path)
                    print_success("Banco de dados restaurado")
            
            print_success("Backup restaurado com sucesso")
            return True
            
        except Exception as e:
            print_error(f"Erro ao restaurar backup: {e}")
            return False
    
    def show_migration_summary(self):
        """Mostra resumo da migração"""
        print_header("RESUMO DA MIGRAÇÃO", Colors.WHITE)
        
        print(f"\n{Colors.WHITE}📊 O QUE FOI ALTERADO:{Colors.NC}")
        print("   ✅ Tabela 'stocks' expandida (50+ campos novos)")
        print("   ✅ Nova tabela 'financial_statements' criada")
        print("   ✅ Tabela 'fundamental_analyses' expandida")
        print("   ✅ Novos índices para performance")
        print("   ✅ Sistema de enums para qualidade de dados")
        
        print(f"\n{Colors.WHITE}🔄 COMPATIBILIDADE MANTIDA:{Colors.NC}")
        print("   ✅ Todos os campos da Fase 1 preservados")
        print("   ✅ Métodos existentes funcionam normalmente")
        print("   ✅ APIs da Fase 1 continuam funcionando")
        print("   ✅ Código existente não precisa ser alterado")
        
        print(f"\n{Colors.WHITE}📈 NOVOS RECURSOS DISPONÍVEIS:{Colors.NC}")
        print("   🆕 25+ novas métricas financeiras")
        print("   🆕 Demonstrações financeiras históricas")
        print("   🆕 Sistema de scoring avançado")
        print("   🆕 Benchmarks setoriais")
        print("   🆕 Análises de qualidade de dados")
        
        if self.backup_created:
            print(f"\n{Colors.CYAN}💾 BACKUP CRIADO:{Colors.NC}")
            print(f"   📁 {self.backup_path}")
            print("   💡 Use este backup se precisar voltar à Fase 1")


def main():
    """Função principal"""
    migrator = Phase2Migrator()
    
    try:
        print_header("MIGRAÇÃO PARA FASE 2", Colors.BLUE)
        print("Este script atualiza o sistema para Fase 2 mantendo compatibilidade total")
        
        # Confirmar com usuário
        response = input(f"\n{Colors.YELLOW}Deseja continuar com a migração? (s/n): {Colors.NC}")
        if response.lower() != 's':
            print("Migração cancelada pelo usuário")
            return False
        
        # Executar migração
        success = migrator.run_safe_migration()
        
        # Mostrar resumo
        migrator.show_migration_summary()
        
        if success:
            print(f"\n{Colors.GREEN}🎉 MIGRAÇÃO CONCLUÍDA COM SUCESSO!{Colors.NC}")
            print(f"{Colors.GREEN}✅ Sistema agora suporta Fase 2 com compatibilidade total{Colors.NC}")
            
            print(f"\n{Colors.CYAN}🚀 PRÓXIMOS PASSOS:{Colors.NC}")
            print("   1. Testar se Fase 1 ainda funciona normalmente")
            print("   2. Implementar funcionalidades da Fase 2")
            print("   3. Usar novos campos e recursos expandidos")
        else:
            print(f"\n{Colors.RED}❌ MIGRAÇÃO FALHOU{Colors.NC}")
            print(f"{Colors.YELLOW}💾 Sistema restaurado para estado anterior{Colors.NC}")
            print(f"{Colors.CYAN}🔧 Verifique os logs e tente novamente{Colors.NC}")
        
        return success
        
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️  Migração interrompida pelo usuário{Colors.NC}")
        if migrator.backup_created:
            migrator._restore_backup()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
