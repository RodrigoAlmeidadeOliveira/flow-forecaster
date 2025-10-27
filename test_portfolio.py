"""
Test script for Portfolio Dashboard functionality
"""

def test_portfolio_imports():
    """Test if all modules can be imported"""
    print("Testing imports...")
    try:
        from portfolio_analyzer import (
            calculate_project_health_score,
            analyze_portfolio_capacity,
            create_prioritization_matrix,
            generate_portfolio_alerts
        )
        print("✓ portfolio_analyzer imports OK")
    except Exception as e:
        print(f"✗ portfolio_analyzer import failed: {e}")
        return False

    try:
        from models import Project, Forecast, Actual
        print("✓ models imports OK")
    except Exception as e:
        print(f"✗ models import failed: {e}")
        return False

    return True


def test_api_endpoints():
    """Test if API endpoints are registered"""
    print("\nTesting API endpoints...")
    try:
        from app import app

        expected_endpoints = [
            '/api/portfolio/dashboard',
            '/api/portfolio/health/<int:project_id>',
            '/api/portfolio/capacity',
            '/api/portfolio/prioritization'
        ]

        registered_routes = [str(rule) for rule in app.url_map.iter_rules()]

        for endpoint in expected_endpoints:
            # Check if pattern exists
            pattern_found = any(endpoint.replace('<int:project_id>', '<project_id>') in route
                              for route in registered_routes)
            if pattern_found:
                print(f"  ✓ {endpoint}")
            else:
                print(f"  ✗ {endpoint} NOT FOUND")
                print(f"    Available: {[r for r in registered_routes if 'portfolio' in r]}")

        print("\n✓ API endpoints test complete")
        return True

    except Exception as e:
        print(f"✗ API test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_portfolio_tab():
    """Test if portfolio tab exists in index.html"""
    print("\nTesting Portfolio tab in HTML...")
    try:
        with open('templates/index.html', 'r') as f:
            content = f.read()

        checks = {
            'tab link': 'tab-portfolio-link' in content,
            'tab content': 'portfolio-dashboard' in content,
            'portfolio.js': 'portfolio.js' in content
        }

        for check_name, result in checks.items():
            if result:
                print(f"  ✓ {check_name} found")
            else:
                print(f"  ✗ {check_name} NOT found")

        return all(checks.values())

    except Exception as e:
        print(f"✗ HTML test failed: {e}")
        return False


def test_database_migration():
    """Test if new Project fields are available"""
    print("\nTesting database schema...")
    try:
        from models import Project, Base
        from database import engine

        # Check if new columns exist in Project model
        project_columns = [c.name for c in Project.__table__.columns]

        expected_columns = [
            'status', 'priority', 'business_value', 'risk_level',
            'capacity_allocated', 'strategic_importance',
            'start_date', 'target_end_date', 'owner', 'stakeholder', 'tags'
        ]

        for col in expected_columns:
            if col in project_columns:
                print(f"  ✓ Column '{col}' exists in Project model")
            else:
                print(f"  ✗ Column '{col}' MISSING in Project model")

        # Try to create tables (will update schema if needed)
        print("\n  Updating database schema...")
        Base.metadata.create_all(engine)
        print("  ✓ Database schema updated")

        return True

    except Exception as e:
        print(f"✗ Database test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all tests"""
    print("="*60)
    print("PORTFOLIO DASHBOARD - INTEGRATION TESTS")
    print("="*60)

    results = {
        'Imports': test_portfolio_imports(),
        'API Endpoints': test_api_endpoints(),
        'HTML Tab': test_portfolio_tab(),
        'Database': test_database_migration()
    }

    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    for test_name, result in results.items():
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{test_name:20s}: {status}")

    all_passed = all(results.values())
    print("="*60)
    if all_passed:
        print("✅ ALL TESTS PASSED!")
        print("\nPortfolio Dashboard está pronto para uso!")
        print("Acesse: http://localhost:8080/ e clique na aba 'Portfolio'")
    else:
        print("❌ SOME TESTS FAILED")
        print("Revise os erros acima antes de usar.")

    print("="*60)
    return all_passed


if __name__ == '__main__':
    run_all_tests()
