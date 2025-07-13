#!/usr/bin/env python3
# =================================================================
# INVESTIGADOR DO FINANCIAL CALCULATOR
# =================================================================
# Script para investigar e resolver problemas de import do FinancialCalculator
# Data: 13/07/2025
# =================================================================

import os
import sys
import ast
import importlib.util
from pathlib import Path
from typing import List, Dict, Any

def print_header(title: str):
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print(f"{'='*60}")

def print_section(title: str):
    print(f"\n📋 {title}")
    print("-" * 40)

def print_success(msg: str):
    print(f"✅ {msg}")

def print_error(msg: str):
    print(f"❌ {msg}")

def print_warning(msg: str):
    print(f"⚠️  {msg}")

def print_info(msg: str):
    print(f"ℹ️  {msg}")

def investigate_file_structure():
    """Investiga estrutura de arquivos"""
    print_section("ESTRUTURA DE ARQUIVOS")
    
    current_dir = Path.cwd()
    print(f"Diretório atual: {current_dir}")
    
    # Verificar estrutura utils/
    utils_dir = current_dir / "utils"
    calc_file = utils_dir / "financial_calculator.py"
    init_file = utils_dir / "__init__.py"
    
    print(f"utils/ existe: {utils_dir.exists()}")
    print(f"utils/__init__.py existe: {init_file.exists()}")
    print(f"utils/financial_calculator.py existe: {calc_file.exists()}")
    
    if calc_file.exists():
        stat = calc_file.stat()
        print(f"Tamanho: {stat.st_size} bytes")
        print(f"Modificado: {stat.st_mtime}")
        
        # Verificar se é arquivo válido
        try:
            with open(calc_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if content.strip():
                print_success("Arquivo não está vazio")
                
                # Verificar estrutura básica
                if "class FinancialCalculator" in content:
                    print_success("Classe FinancialCalculator encontrada")
                else:
                    print_error("Classe FinancialCalculator NÃO encontrada")
                    
                if "class FinancialData" in content:
                    print_success("Classe FinancialData encontrada")
                else:
                    print_error("Classe FinancialData NÃO encontrada")
                    
                if "class FinancialMetrics" in content:
                    print_success("Classe FinancialMetrics encontrada")
                else:
                    print_error("Classe FinancialMetrics NÃO encontrada")
            else:
                print_error("Arquivo está vazio!")
                
        except Exception as e:
            print_error(f"Erro ao ler arquivo: {e}")
    
    return calc_file.exists()

def analyze_python_syntax():
    """Analisa sintaxe Python do arquivo"""
    print_section("ANÁLISE DE SINTAXE")
    
    calc_file = Path("utils/financial_calculator.py")
    
    if not calc_file.exists():
        print_error("Arquivo não existe")
        return False
    
    try:
        with open(calc_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar sintaxe Python
        try:
            ast.parse(content)
            print_success("Sintaxe Python válida")
        except SyntaxError as e:
            print_error(f"Erro de sintaxe: {e}")
            print_error(f"Linha {e.lineno}: {e.text}")
            return False
        
        # Analisar estrutura AST
        tree = ast.parse(content)
        
        classes = []
        functions = []
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes.append(node.name)
            elif isinstance(node, ast.FunctionDef):
                functions.append(node.name)
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    imports.append(f"{module}.{alias.name}")
        
        print_info("Classes encontradas:")
        for cls in classes:
            print(f"   • {cls}")
        
        print_info("Funções encontradas:")
        for func in functions[:10]:  # Primeiras 10
            print(f"   • {func}")
        
        print_info("Imports encontrados:")
        for imp in imports[:10]:  # Primeiros 10
            print(f"   • {imp}")
        
        # Verificar classes essenciais
        required_classes = ['FinancialCalculator', 'FinancialData', 'FinancialMetrics']
        missing_classes = [cls for cls in required_classes if cls not in classes]
        
        if missing_classes:
            print_error(f"Classes faltando: {missing_classes}")
            return False
        else:
            print_success("Todas as classes essenciais encontradas")
            return True
    
    except Exception as e:
        print_error(f"Erro na análise: {e}")
        return False

def test_import_paths():
    """Testa diferentes caminhos de import"""
    print_section("TESTANDO CAMINHOS DE IMPORT")
    
    current_dir = Path.cwd()
    
    # Garantir que diretório atual está no path
    if str(current_dir) not in sys.path:
        sys.path.insert(0, str(current_dir))
        print_info(f"Adicionado ao sys.path: {current_dir}")
    
    # Diferentes formas de import
    import_methods = [
        ("Direct module", "utils.financial_calculator"),
        ("Absolute path", str(current_dir / "utils" / "financial_calculator.py")),
    ]
    
    for method_name, import_path in import_methods:
        print(f"\n🧪 Testando: {method_name}")
        print(f"   Caminho: {import_path}")
        
        try:
            if method_name == "Direct module":
                # Import normal
                module = importlib.import_module(import_path)
                
            else:
                # Import por arquivo
                spec = importlib.util.spec_from_file_location("financial_calculator", import_path)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                else:
                    raise ImportError("Não foi possível criar spec")
            
            print_success(f"Módulo importado: {module}")
            
            # Verificar atributos
            attrs = dir(module)
            required_classes = ['FinancialCalculator', 'FinancialData', 'FinancialMetrics']
            
            for cls_name in required_classes:
                if cls_name in attrs:
                    print_success(f"   • {cls_name}: Disponível")
                    
                    # Tentar instanciar
                    try:
                        cls = getattr(module, cls_name)
                        if cls_name == 'FinancialCalculator':
                            instance = cls()
                            print_success(f"   • {cls_name}: Instanciável")
                        else:
                            print_success(f"   • {cls_name}: Classe válida")
                    except Exception as e:
                        print_error(f"   • {cls_name}: Erro ao instanciar - {e}")
                else:
                    print_error(f"   • {cls_name}: NÃO encontrado")
            
            return True
            
        except ImportError as e:
            print_error(f"Erro de import: {e}")
        except Exception as e:
            print_error(f"Erro inesperado: {e}")
    
    return False

def test_specific_imports():
    """Testa imports específicos das classes"""
    print_section("TESTANDO IMPORTS ESPECÍFICOS")
    
    current_dir = Path.cwd()
    if str(current_dir) not in sys.path:
        sys.path.insert(0, str(current_dir))
    
    # Testar cada classe individualmente
    classes_to_test = [
        'FinancialCalculator',
        'FinancialData', 
        'FinancialMetrics'
    ]
    
    results = {}
    
    for class_name in classes_to_test:
        print(f"\n🧪 Testando import: {class_name}")
        
        try:
            # Import do módulo
            from utils.financial_calculator import FinancialCalculator, FinancialData, FinancialMetrics
            
            # Obter classe específica
            cls = locals()[class_name]
            print_success(f"Classe {class_name} importada")
            
            # Testar instanciação básica
            if class_name == 'FinancialCalculator':
                instance = cls()
                print_success(f"FinancialCalculator instanciado")
                
                # Testar método principal
                if hasattr(instance, 'calculate_all_metrics'):
                    print_success("Método calculate_all_metrics encontrado")
                    
                    # Criar dados mock para teste
                    data = FinancialData()
                    metrics = instance.calculate_all_metrics(data)
                    print_success("Método calculate_all_metrics executado")
                    
                    results[class_name] = True
                else:
                    print_error("Método calculate_all_metrics NÃO encontrado")
                    results[class_name] = False
                    
            elif class_name in ['FinancialData', 'FinancialMetrics']:
                instance = cls()
                print_success(f"{class_name} instanciado")
                results[class_name] = True
            
        except ImportError as e:
            print_error(f"Erro de import para {class_name}: {e}")
            results[class_name] = False
        except Exception as e:
            print_error(f"Erro inesperado para {class_name}: {e}")
            results[class_name] = False
    
    return results

def check_utils_init():
    """Verifica utils/__init__.py"""
    print_section("VERIFICANDO UTILS/__INIT__.PY")
    
    init_file = Path("utils/__init__.py")
    
    if not init_file.exists():
        print_error("utils/__init__.py não existe")
        
        # Criar __init__.py básico
        print_info("Criando utils/__init__.py básico...")
        try:
            init_content = '''# utils/__init__.py
"""
Utilitários do Sistema de Recomendações de Investimentos
"""

try:
    from utils.financial_calculator import (
        FinancialCalculator,
        FinancialData,
        FinancialMetrics
    )
    
    __all__ = [
        "FinancialCalculator",
        "FinancialData", 
        "FinancialMetrics"
    ]
    
except ImportError as e:
    print(f"Aviso: Erro ao importar financial_calculator: {e}")
    __all__ = []

__version__ = "1.0.0"
'''
            
            with open(init_file, 'w', encoding='utf-8') as f:
                f.write(init_content)
            
            print_success("utils/__init__.py criado")
            
        except Exception as e:
            print_error(f"Erro ao criar __init__.py: {e}")
            return False
    
    else:
        print_success("utils/__init__.py existe")
        
        # Verificar conteúdo
        try:
            with open(init_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if "FinancialCalculator" in content:
                print_success("FinancialCalculator mencionado no __init__.py")
            else:
                print_warning("FinancialCalculator NÃO mencionado no __init__.py")
            
        except Exception as e:
            print_error(f"Erro ao ler __init__.py: {e}")
    
    return True

def create_minimal_test():
    """Cria teste mínimo para validação"""
    print_section("CRIANDO TESTE MÍNIMO")
    
    test_code = '''# test_financial_calculator.py
"""
Teste mínimo do FinancialCalculator
"""

import sys
from pathlib import Path

# Adicionar projeto ao path
current_dir = Path.cwd()
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

def test_financial_calculator():
    """Teste básico do FinancialCalculator"""
    try:
        print("🧪 Testando FinancialCalculator...")
        
        # Import
        from utils.financial_calculator import FinancialCalculator, FinancialData, FinancialMetrics
        print("✅ Import realizado com sucesso")
        
        # Instanciar calculator
        calc = FinancialCalculator()
        print("✅ FinancialCalculator instanciado")
        
        # Criar dados de teste
        data = FinancialData(
            symbol="PETR4",
            revenue=50000000000,
            net_income=6000000000,
            current_price=25.50
        )
        print("✅ FinancialData criado")
        
        # Calcular métricas
        metrics = calc.calculate_all_metrics(data)
        print("✅ Métricas calculadas")
        
        # Verificar resultado
        if hasattr(metrics, 'roe') or hasattr(metrics, 'profit_margin'):
            print("✅ Métricas contêm dados esperados")
            
            # Exibir algumas métricas
            if hasattr(metrics, 'roe') and metrics.roe:
                print(f"   ROE: {metrics.roe:.2f}%")
            if hasattr(metrics, 'profit_margin') and metrics.profit_margin:
                print(f"   Margem: {metrics.profit_margin:.2f}%")
                
            return True
        else:
            print("❌ Métricas não contêm dados esperados")
            return False
            
    except ImportError as e:
        print(f"❌ Erro de import: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

if __name__ == "__main__":
    success = test_financial_calculator()
    print(f"\\nResultado: {'✅ SUCESSO' if success else '❌ FALHA'}")
'''
    
    test_file = Path("test_financial_calculator.py")
    
    try:
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_code)
        
        print_success(f"Teste criado: {test_file}")
        
        # Executar teste
        print_info("Executando teste...")
        try:
            exec(test_code)
        except Exception as e:
            print_error(f"Erro ao executar teste: {e}")
        
        return True
        
    except Exception as e:
        print_error(f"Erro ao criar teste: {e}")
        return False

def generate_fix_recommendations():
    """Gera recomendações de correção"""
    print_section("RECOMENDAÇÕES DE CORREÇÃO")
    
    recommendations = []
    
    # Verificar se arquivo existe
    calc_file = Path("utils/financial_calculator.py")
    if not calc_file.exists():
        recommendations.append("1. Criar arquivo utils/financial_calculator.py")
    
    # Verificar __init__.py
    init_file = Path("utils/__init__.py")
    if not init_file.exists():
        recommendations.append("2. Criar utils/__init__.py")
    
    # Verificar sintaxe
    try:
        if calc_file.exists():
            with open(calc_file, 'r') as f:
                content = f.read()
            ast.parse(content)
    except:
        recommendations.append("3. Corrigir erros de sintaxe em financial_calculator.py")
    
    # Verificar imports
    try:
        current_dir = Path.cwd()
        if str(current_dir) not in sys.path:
            sys.path.insert(0, str(current_dir))
        from utils.financial_calculator import FinancialCalculator
    except:
        recommendations.append("4. Corrigir problemas de import")
    
    if recommendations:
        print("Recomendações:")
        for rec in recommendations:
            print(f"   {rec}")
    else:
        print_success("Nenhuma correção necessária detectada")
    
    return recommendations

def main():
    """Função principal de investigação"""
    print_header("INVESTIGADOR DO FINANCIAL CALCULATOR")
    
    print("Este script investiga problemas de import do FinancialCalculator")
    print("e fornece diagnósticos detalhados e soluções.")
    
    # 1. Investigar estrutura de arquivos
    file_exists = investigate_file_structure()
    
    if not file_exists:
        print_error("Arquivo financial_calculator.py não existe!")
        print_info("Execute o script de setup para criar o arquivo")
        return False
    
    # 2. Analisar sintaxe
    syntax_ok = analyze_python_syntax()
    
    if not syntax_ok:
        print_error("Problemas de sintaxe detectados!")
        return False
    
    # 3. Verificar __init__.py
    init_ok = check_utils_init()
    
    # 4. Testar imports
    import_ok = test_import_paths()
    
    if import_ok:
        # 5. Testar imports específicos
        specific_results = test_specific_imports()
        
        all_working = all(specific_results.values())
        
        if all_working:
            print_success("\n🎉 TODOS OS TESTES PASSARAM!")
            print_success("FinancialCalculator está funcionando corretamente")
            
            # 6. Criar teste mínimo
            create_minimal_test()
            
        else:
            failed_classes = [cls for cls, success in specific_results.items() if not success]
            print_error(f"\n❌ Classes com problema: {failed_classes}")
    
    # 7. Gerar recomendações
    generate_fix_recommendations()
    
    print_header("INVESTIGAÇÃO CONCLUÍDA")
    
    return import_ok

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print_error(f"Erro crítico: {e}")
        sys.exit(1)
