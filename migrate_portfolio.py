#!/usr/bin/env python3
"""
Database migration script to add Portfolio tables
Adds: portfolios, portfolio_projects, simulation_runs
"""
import sys
from sqlalchemy import create_engine, inspect
from models import Base, Portfolio, PortfolioProject, SimulationRun

def check_table_exists(engine, table_name):
    """Check if table already exists"""
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()

def migrate_database(database_url='sqlite:///forecaster.db'):
    """
    Create new Portfolio tables if they don't exist

    Args:
        database_url: Database connection string
    """
    print("=" * 80)
    print("PORTFOLIO DATABASE MIGRATION")
    print("=" * 80)
    print(f"\nConnecting to database: {database_url}")

    try:
        # Create engine
        engine = create_engine(database_url)

        # Check which tables need to be created
        tables_to_create = []

        for table_name in ['portfolios', 'portfolio_projects', 'simulation_runs']:
            if check_table_exists(engine, table_name):
                print(f"✓ Table '{table_name}' already exists - skipping")
            else:
                print(f"✗ Table '{table_name}' does not exist - will create")
                tables_to_create.append(table_name)

        if not tables_to_create:
            print("\n✅ All tables already exist. No migration needed.")
            return True

        # Create only the new tables
        print(f"\n📝 Creating {len(tables_to_create)} new table(s)...")

        # Create tables using SQLAlchemy metadata
        # This will only create tables that don't exist
        Base.metadata.create_all(engine, checkfirst=True)

        print("\n✅ Migration completed successfully!")
        print("\nNew tables created:")
        for table in tables_to_create:
            print(f"  - {table}")

        # Verify tables were created
        print("\n🔍 Verifying tables...")
        inspector = inspect(engine)
        all_tables = inspector.get_table_names()

        for table in tables_to_create:
            if table in all_tables:
                columns = inspector.get_columns(table)
                print(f"\n  ✓ {table} ({len(columns)} columns):")
                for col in columns[:5]:  # Show first 5 columns
                    print(f"      - {col['name']} ({col['type']})")
                if len(columns) > 5:
                    print(f"      ... and {len(columns) - 5} more columns")
            else:
                print(f"\n  ✗ {table} - NOT FOUND!")
                return False

        print("\n" + "=" * 80)
        print("MIGRATION SUMMARY")
        print("=" * 80)
        print(f"✅ Successfully created {len(tables_to_create)} new table(s)")
        print("\nYou can now:")
        print("  1. Create portfolios via /api/portfolios")
        print("  2. Add projects to portfolios via /api/portfolios/<id>/projects")
        print("  3. Run portfolio simulations via /api/portfolios/<id>/simulate")
        print("=" * 80)

        return True

    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def rollback_migration(database_url='sqlite:///forecaster.db'):
    """
    Remove Portfolio tables (for testing/development)
    WARNING: This will delete all portfolio data!
    """
    print("=" * 80)
    print("⚠️  PORTFOLIO TABLE ROLLBACK")
    print("=" * 80)
    print("\nWARNING: This will DELETE all portfolio data!")

    response = input("Type 'DELETE' to confirm rollback: ")
    if response != 'DELETE':
        print("Rollback cancelled.")
        return False

    try:
        engine = create_engine(database_url)

        # Drop tables in reverse order (due to foreign keys)
        tables_to_drop = ['simulation_runs', 'portfolio_projects', 'portfolios']

        for table_name in tables_to_drop:
            if check_table_exists(engine, table_name):
                print(f"Dropping table: {table_name}")
                engine.execute(f"DROP TABLE {table_name}")
                print(f"  ✓ Dropped {table_name}")
            else:
                print(f"  - {table_name} does not exist")

        print("\n✅ Rollback completed")
        return True

    except Exception as e:
        print(f"\n❌ Rollback failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == '--rollback':
        success = rollback_migration()
    else:
        success = migrate_database()

    sys.exit(0 if success else 1)
