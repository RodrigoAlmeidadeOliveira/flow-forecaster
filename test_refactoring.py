"""
Test script for the refactored application structure.

This script performs static analysis and validation of the refactored code
without requiring Flask or other dependencies to be installed.
"""

import ast
import os
import sys
from pathlib import Path


def analyze_file(filepath):
    """
    Analyze a Python file for imports and basic structure.

    Returns:
        dict: Analysis results
    """
    try:
        with open(filepath, 'r') as f:
            content = f.read()

        tree = ast.parse(content, filename=filepath)

        imports = []
        functions = []
        classes = []
        routes = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                imports.append(f"from {node.module}")
            elif isinstance(node, ast.FunctionDef):
                functions.append(node.name)
                # Check for route decorators
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Call):
                        if hasattr(decorator.func, 'attr') and 'route' in decorator.func.attr:
                            routes.append(node.name)
            elif isinstance(node, ast.ClassDef):
                classes.append(node.name)

        return {
            'filepath': filepath,
            'imports': imports,
            'functions': functions,
            'classes': classes,
            'routes': routes,
            'success': True
        }
    except SyntaxError as e:
        return {
            'filepath': filepath,
            'error': str(e),
            'success': False
        }
    except Exception as e:
        return {
            'filepath': filepath,
            'error': str(e),
            'success': False
        }


def test_refactored_structure():
    """Test the refactored application structure."""

    print("=" * 70)
    print("TESTING REFACTORED APPLICATION STRUCTURE")
    print("=" * 70)
    print()

    base_dir = Path(__file__).parent

    # Files to test
    files_to_test = [
        'app_new.py',
        'app_package/__init__.py',
        'app_package/auth/routes.py',
        'app_package/web/routes.py',
        'app_package/utils/auth_helpers.py',
        'app_package/utils/db_helpers.py',
        'app_package/utils/date_helpers.py',
        'app_package/utils/helpers.py',
        'app_package/utils/__init__.py',
    ]

    results = []
    all_success = True

    print("📝 Testing Python files...")
    print()

    for filepath in files_to_test:
        full_path = base_dir / filepath
        if not full_path.exists():
            print(f"❌ File not found: {filepath}")
            all_success = False
            continue

        result = analyze_file(full_path)
        results.append(result)

        if result['success']:
            print(f"✅ {filepath}")
            if result['routes']:
                print(f"   📍 Routes: {len(result['routes'])}")
            if result['functions']:
                print(f"   🔧 Functions: {len(result['functions'])}")
        else:
            print(f"❌ {filepath}")
            print(f"   Error: {result.get('error', 'Unknown error')}")
            all_success = False

    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)

    # Count routes
    total_routes = sum(len(r['routes']) for r in results if r['success'])
    print(f"📍 Total routes found: {total_routes}")

    # List routes by blueprint
    print()
    print("Routes by blueprint:")
    for result in results:
        if result['success'] and result['routes']:
            filename = Path(result['filepath']).name
            print(f"  {filename}:")
            for route in result['routes']:
                print(f"    - {route}()")

    # Check for expected imports
    print()
    print("Key imports verification:")

    # Check app_new.py imports create_app
    app_new_result = next((r for r in results if 'app_new.py' in str(r['filepath'])), None)
    if app_new_result and app_new_result['success']:
        has_create_app = any('app_package' in imp for imp in app_new_result['imports'])
        if has_create_app:
            print("  ✅ app_new.py imports create_app from app_package")
        else:
            print("  ❌ app_new.py missing import of create_app")
            all_success = False

    # Check factory imports Flask
    factory_result = next((r for r in results if 'app_package/__init__.py' in str(r['filepath'])), None)
    if factory_result and factory_result['success']:
        has_flask = any('flask' in imp.lower() for imp in factory_result['imports'])
        if has_flask:
            print("  ✅ Application factory imports Flask")
        else:
            print("  ❌ Application factory missing Flask import")
            all_success = False

    print()
    print("=" * 70)
    if all_success:
        print("✅ ALL TESTS PASSED - Structure is valid!")
    else:
        print("❌ SOME TESTS FAILED - Check errors above")
    print("=" * 70)

    return all_success


def test_import_paths():
    """Test that import paths are correct."""

    print()
    print("=" * 70)
    print("TESTING IMPORT PATHS")
    print("=" * 70)
    print()

    base_dir = Path(__file__).parent

    # Check that all __init__.py files exist
    init_files = [
        'app_package/__init__.py',
        'app_package/auth/__init__.py',
        'app_package/web/__init__.py',
        'app_package/api/__init__.py',
        'app_package/utils/__init__.py',
    ]

    all_exist = True
    for init_file in init_files:
        full_path = base_dir / init_file
        if full_path.exists():
            print(f"✅ {init_file} exists")
        else:
            print(f"❌ {init_file} missing")
            all_exist = False

    print()
    if all_exist:
        print("✅ All __init__.py files present")
    else:
        print("❌ Some __init__.py files missing")

    return all_exist


def test_blueprint_structure():
    """Test blueprint directory structure."""

    print()
    print("=" * 70)
    print("TESTING BLUEPRINT DIRECTORY STRUCTURE")
    print("=" * 70)
    print()

    base_dir = Path(__file__).parent

    expected_structure = {
        'app_package': ['__init__.py', 'auth', 'web', 'api', 'utils'],
        'app_package/auth': ['__init__.py', 'routes.py'],
        'app_package/web': ['__init__.py', 'routes.py'],
        'app_package/utils': [
            '__init__.py',
            'auth_helpers.py',
            'db_helpers.py',
            'date_helpers.py',
            'helpers.py'
        ],
    }

    all_correct = True

    for directory, expected_files in expected_structure.items():
        dir_path = base_dir / directory
        print(f"📁 {directory}/")

        if not dir_path.exists():
            print(f"   ❌ Directory does not exist")
            all_correct = False
            continue

        for expected_file in expected_files:
            file_path = dir_path / expected_file
            if file_path.exists():
                if file_path.is_file():
                    print(f"   ✅ {expected_file}")
                else:
                    print(f"   📁 {expected_file}/ (directory)")
            else:
                print(f"   ❌ {expected_file} missing")
                all_correct = False

    print()
    if all_correct:
        print("✅ Blueprint structure is correct")
    else:
        print("❌ Blueprint structure has issues")

    return all_correct


if __name__ == '__main__':
    print()

    # Run all tests
    test1 = test_blueprint_structure()
    test2 = test_import_paths()
    test3 = test_refactored_structure()

    print()
    print("=" * 70)
    print("FINAL RESULT")
    print("=" * 70)

    if test1 and test2 and test3:
        print("✅ ALL VALIDATION TESTS PASSED!")
        print()
        print("The refactored application structure is valid.")
        print("Ready for runtime testing with Flask installed.")
        sys.exit(0)
    else:
        print("❌ SOME VALIDATION TESTS FAILED")
        print()
        print("Please review the errors above and fix the issues.")
        sys.exit(1)
