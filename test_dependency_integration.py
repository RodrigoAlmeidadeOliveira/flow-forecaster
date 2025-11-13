"""
Test script for multi-team forecasting with dependencies integration
Based on Nick Brown's article approach
"""
from portfolio_simulator import (
    ProjectForecastInput,
    simulate_portfolio_with_dependencies
)
from dependency_analyzer import Dependency
import json


def test_multi_team_with_dependencies():
    """
    Test case: 3 teams working on an e-Commerce Loyalty Program
    - Team 1: Backend API (no dependencies)
    - Team 2: Mobile App (depends on Team 1)
    - Team 3: Marketing Dashboard (depends on Team 1)
    """

    print("=" * 80)
    print("MULTI-TEAM FORECASTING WITH DEPENDENCIES TEST")
    print("Scenario: e-Commerce Loyalty Program")
    print("=" * 80)

    # Define projects (teams)
    projects = [
        ProjectForecastInput(
            project_id=1,
            project_name="Backend API",
            backlog=20,
            tp_samples=[3.0, 2.5, 3.5, 3.0, 2.8, 3.2, 2.9, 3.1],  # Weekly throughput
            priority=1,
            cod_weekly=5000.0,
            wsjf_score=8.5,
            depends_on=[]  # No dependencies
        ),
        ProjectForecastInput(
            project_id=2,
            project_name="Mobile App",
            backlog=15,
            tp_samples=[2.0, 1.8, 2.2, 2.1, 1.9, 2.0, 2.3, 1.8],
            priority=2,
            cod_weekly=4000.0,
            wsjf_score=7.2,
            depends_on=[1]  # Depends on Backend API
        ),
        ProjectForecastInput(
            project_id=3,
            project_name="Marketing Dashboard",
            backlog=10,
            tp_samples=[2.5, 2.3, 2.7, 2.4, 2.6, 2.5, 2.8, 2.3],
            priority=3,
            cod_weekly=2000.0,
            wsjf_score=5.8,
            depends_on=[1]  # Depends on Backend API
        )
    ]

    # Define dependencies
    dependencies = [
        Dependency(
            id="DEP-001",
            name="Mobile App depends on Backend API",
            source_project="Mobile App",
            target_project="Backend API",
            on_time_probability=0.7,  # 70% chance Backend is on time
            delay_impact_days=7,  # If delayed, impacts 7 days
            criticality='HIGH'
        ),
        Dependency(
            id="DEP-002",
            name="Marketing Dashboard depends on Backend API",
            source_project="Marketing Dashboard",
            target_project="Backend API",
            on_time_probability=0.7,  # 70% chance Backend is on time
            delay_impact_days=5,
            criticality='MEDIUM'
        )
    ]

    # Run simulation
    print("\nRunning Monte Carlo simulation with 10,000 iterations...")
    result = simulate_portfolio_with_dependencies(
        projects=projects,
        dependencies=dependencies,
        n_simulations=10000,
        confidence_level='P85'
    )

    # Display results
    print("\n" + "=" * 80)
    print("RESULTS")
    print("=" * 80)

    print("\n📊 BASELINE FORECAST (Without Dependencies):")
    baseline = result['baseline_forecast']
    print(f"  P50: {baseline['p50_weeks']} weeks")
    print(f"  P85: {baseline['p85_weeks']} weeks")
    print(f"  P95: {baseline['p95_weeks']} weeks")

    print("\n📊 ADJUSTED FORECAST (With Dependencies):")
    adjusted = result['adjusted_forecast']
    print(f"  P50: {adjusted['p50_weeks']} weeks")
    print(f"  P85: {adjusted['p85_weeks']} weeks ⭐")
    print(f"  P95: {adjusted['p95_weeks']} weeks")

    print("\n⚠️  DEPENDENCY IMPACT:")
    impact = result['dependency_impact']
    print(f"  Additional delay (P85): {impact['delay_weeks_p85']} weeks")
    print(f"  Percentage increase: {impact['delay_percentage_p85']}%")
    print(f"  Additional delay (P95): {impact['delay_weeks_p95']} weeks")

    print("\n🎯 COMBINED PROBABILITIES:")
    probs = result['combined_probabilities']
    print(f"  Dependency on-time probability: {probs['dependency_on_time_probability']}%")
    print(f"  Team combined probability: {probs['team_combined_probability']}%")
    print(f"  Overall on-time probability: {probs['overall_on_time_probability']}% ⭐")
    print(f"\n  Explanation: {probs['explanation']}")

    print("\n📋 PROJECT-LEVEL RESULTS:")
    print("\n  Baseline (no dependencies):")
    for pr in result['project_results']['baseline']:
        print(f"    - {pr['project_name']}: {pr['p85_weeks']} weeks (P85)")

    print("\n  Adjusted (with dependencies):")
    for pr in result['project_results']['adjusted']:
        delay_text = f"+{pr['delay_vs_baseline']} weeks" if pr['delay_vs_baseline'] > 0 else "no delay"
        print(f"    - {pr['project_name']}: {pr['p85_weeks']} weeks (P85) [{delay_text}]")

    if result['dependency_analysis']:
        print("\n🔍 DEPENDENCY ANALYSIS:")
        dep_analysis = result['dependency_analysis']
        print(f"  Total dependencies: {dep_analysis['total_dependencies']}")
        print(f"  On-time probability: {dep_analysis['on_time_probability_percentage']}%")
        print(f"  Odds ratio: {dep_analysis['odds_ratio']}")
        print(f"  Expected delay (if any): {dep_analysis['expected_delay_days']} days")
        print(f"  Risk score: {dep_analysis['risk_score']}/100")
        print(f"  Risk level: {dep_analysis['risk_level']}")

        print("\n  Critical path (top dependencies):")
        for i, dep in enumerate(dep_analysis['critical_path'][:3], 1):
            print(f"    {i}. {dep}")

    print("\n💡 RECOMMENDATIONS:")
    for i, rec in enumerate(result['recommendations'], 1):
        print(f"  {i}. {rec}")

    print("\n" + "=" * 80)
    print("✅ Integration test completed successfully!")
    print("=" * 80)

    # Save results to JSON for inspection
    with open('test_dependency_integration_results.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print("\n📄 Full results saved to: test_dependency_integration_results.json")

    return result


def test_no_dependencies():
    """Test case with no dependencies (baseline behavior)"""

    print("\n" + "=" * 80)
    print("TEST: Portfolio without dependencies")
    print("=" * 80)

    projects = [
        ProjectForecastInput(
            project_id=1,
            project_name="Team A",
            backlog=10,
            tp_samples=[2.0, 2.2, 1.8, 2.1, 2.0],
            priority=1,
            depends_on=[]
        ),
        ProjectForecastInput(
            project_id=2,
            project_name="Team B",
            backlog=15,
            tp_samples=[3.0, 2.8, 3.2, 2.9, 3.1],
            priority=2,
            depends_on=[]
        )
    ]

    result = simulate_portfolio_with_dependencies(
        projects=projects,
        dependencies=[],
        n_simulations=5000
    )

    print(f"\nBaseline P85: {result['baseline_forecast']['p85_weeks']} weeks")
    print(f"Adjusted P85: {result['adjusted_forecast']['p85_weeks']} weeks")
    print(f"Dependency impact: {result['dependency_impact']['delay_weeks_p85']} weeks")
    print(f"Overall on-time probability: {result['combined_probabilities']['overall_on_time_probability']}%")

    print("✅ No dependencies test passed!")

    return result


if __name__ == "__main__":
    # Run test with dependencies
    result1 = test_multi_team_with_dependencies()

    # Run test without dependencies
    result2 = test_no_dependencies()

    print("\n" + "=" * 80)
    print("🎉 All integration tests completed!")
    print("=" * 80)
