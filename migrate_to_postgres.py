#!/usr/bin/env python3
"""
Migrate Data from SQLite to PostgreSQL
Migrates all users, projects, forecasts, and actuals from SQLite to PostgreSQL

Usage:
    # Set PostgreSQL connection
    export DATABASE_URL="postgresql://user:password@localhost:5432/forecaster"

    # Run migration
    python migrate_to_postgres.py

    # Or specify SQLite file
    python migrate_to_postgres.py --sqlite forecaster.db
"""
import os
import sys
import argparse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User, Project, Forecast, Actual

def migrate_data(sqlite_path, postgres_url, dry_run=False):
    """
    Migrate all data from SQLite to PostgreSQL

    Args:
        sqlite_path: Path to SQLite database file
        postgres_url: PostgreSQL connection URL
        dry_run: If True, don't actually write to PostgreSQL
    """

    print("=" * 70)
    print("SQLite to PostgreSQL Migration")
    print("=" * 70)
    print()

    # Validate inputs
    if not os.path.exists(sqlite_path):
        print(f"❌ ERROR: SQLite file not found: {sqlite_path}")
        sys.exit(1)

    print(f"📂 Source (SQLite): {sqlite_path}")
    print(f"🐘 Destination (PostgreSQL): {postgres_url}")
    print()

    if dry_run:
        print("⚠️  DRY RUN MODE - No data will be written")
        print()

    # Create engines
    print("🔌 Connecting to databases...")
    try:
        sqlite_engine = create_engine(f'sqlite:///{sqlite_path}')
        SQLiteSession = sessionmaker(bind=sqlite_engine)
        sqlite_session = SQLiteSession()
        print("   ✅ Connected to SQLite")
    except Exception as e:
        print(f"   ❌ Failed to connect to SQLite: {e}")
        sys.exit(1)

    try:
        postgres_engine = create_engine(postgres_url)
        PostgresSession = sessionmaker(bind=postgres_engine)
        postgres_session = PostgresSession()
        print("   ✅ Connected to PostgreSQL")
    except Exception as e:
        print(f"   ❌ Failed to connect to PostgreSQL: {e}")
        sys.exit(1)

    print()

    # Create tables in PostgreSQL
    if not dry_run:
        print("🏗️  Creating tables in PostgreSQL...")
        try:
            Base.metadata.create_all(postgres_engine)
            print("   ✅ Tables created")
        except Exception as e:
            print(f"   ❌ Failed to create tables: {e}")
            sys.exit(1)
        print()

    # Count records in SQLite
    print("📊 Counting records in SQLite...")
    try:
        user_count = sqlite_session.query(User).count()
        project_count = sqlite_session.query(Project).count()
        forecast_count = sqlite_session.query(Forecast).count()
        actual_count = sqlite_session.query(Actual).count()

        print(f"   👥 Users: {user_count}")
        print(f"   📁 Projects: {project_count}")
        print(f"   📈 Forecasts: {forecast_count}")
        print(f"   ✓  Actuals: {actual_count}")

        total = user_count + project_count + forecast_count + actual_count
        print(f"   📦 Total records: {total}")
    except Exception as e:
        print(f"   ❌ Failed to count records: {e}")
        sys.exit(1)

    print()

    if total == 0:
        print("⚠️  No data to migrate. Exiting.")
        sys.exit(0)

    # Confirm migration
    if not dry_run:
        print("⚠️  WARNING: This will write data to PostgreSQL")
        response = input("Continue? (yes/no): ").strip().lower()
        if response != 'yes':
            print("Migration cancelled")
            sys.exit(0)
        print()

    # Migrate data
    try:
        # 1. Migrate Users
        if user_count > 0:
            print(f"👥 Migrating {user_count} users...")
            users = sqlite_session.query(User).all()

            for i, user in enumerate(users, 1):
                try:
                    if not dry_run:
                        # Detach from SQLite session
                        sqlite_session.expunge(user)
                        # Merge into PostgreSQL
                        postgres_session.merge(user)

                    print(f"   [{i}/{user_count}] {user.email}")
                except Exception as e:
                    print(f"   ❌ Error migrating user {user.email}: {e}")
                    raise

            if not dry_run:
                postgres_session.commit()
            print(f"   ✅ {user_count} users migrated")
            print()

        # 2. Migrate Projects
        if project_count > 0:
            print(f"📁 Migrating {project_count} projects...")
            projects = sqlite_session.query(Project).all()

            for i, project in enumerate(projects, 1):
                try:
                    if not dry_run:
                        sqlite_session.expunge(project)
                        postgres_session.merge(project)

                    print(f"   [{i}/{project_count}] {project.name}")
                except Exception as e:
                    print(f"   ❌ Error migrating project {project.name}: {e}")
                    raise

            if not dry_run:
                postgres_session.commit()
            print(f"   ✅ {project_count} projects migrated")
            print()

        # 3. Migrate Forecasts
        if forecast_count > 0:
            print(f"📈 Migrating {forecast_count} forecasts...")
            forecasts = sqlite_session.query(Forecast).all()

            for i, forecast in enumerate(forecasts, 1):
                try:
                    if not dry_run:
                        sqlite_session.expunge(forecast)
                        postgres_session.merge(forecast)

                    print(f"   [{i}/{forecast_count}] {forecast.name}")
                except Exception as e:
                    print(f"   ❌ Error migrating forecast {forecast.name}: {e}")
                    raise

            if not dry_run:
                postgres_session.commit()
            print(f"   ✅ {forecast_count} forecasts migrated")
            print()

        # 4. Migrate Actuals
        if actual_count > 0:
            print(f"✓  Migrating {actual_count} actuals...")
            actuals = sqlite_session.query(Actual).all()

            for i, actual in enumerate(actuals, 1):
                try:
                    if not dry_run:
                        sqlite_session.expunge(actual)
                        postgres_session.merge(actual)

                    print(f"   [{i}/{actual_count}] Actual #{actual.id}")
                except Exception as e:
                    print(f"   ❌ Error migrating actual #{actual.id}: {e}")
                    raise

            if not dry_run:
                postgres_session.commit()
            print(f"   ✅ {actual_count} actuals migrated")
            print()

        # Success!
        print("=" * 70)
        if dry_run:
            print("🎉 DRY RUN COMPLETE - No data was written")
        else:
            print("🎉 MIGRATION COMPLETE!")
        print("=" * 70)
        print()
        print(f"✅ {user_count} users")
        print(f"✅ {project_count} projects")
        print(f"✅ {forecast_count} forecasts")
        print(f"✅ {actual_count} actuals")
        print(f"✅ {total} total records migrated")
        print()

        if not dry_run:
            print("🔍 Verifying migration...")
            try:
                pg_users = postgres_session.query(User).count()
                pg_projects = postgres_session.query(Project).count()
                pg_forecasts = postgres_session.query(Forecast).count()
                pg_actuals = postgres_session.query(Actual).count()

                print(f"   PostgreSQL Users: {pg_users} (expected {user_count})")
                print(f"   PostgreSQL Projects: {pg_projects} (expected {project_count})")
                print(f"   PostgreSQL Forecasts: {pg_forecasts} (expected {forecast_count})")
                print(f"   PostgreSQL Actuals: {pg_actuals} (expected {actual_count})")

                if (pg_users == user_count and pg_projects == project_count and
                    pg_forecasts == forecast_count and pg_actuals == actual_count):
                    print("   ✅ Verification passed!")
                else:
                    print("   ⚠️  Verification failed - record counts don't match")
            except Exception as e:
                print(f"   ⚠️  Verification failed: {e}")

    except Exception as e:
        print()
        print("=" * 70)
        print(f"❌ MIGRATION FAILED")
        print("=" * 70)
        print(f"Error: {e}")
        print()

        if not dry_run:
            print("Rolling back PostgreSQL transaction...")
            postgres_session.rollback()
            print("Rollback complete")

        sys.exit(1)

    finally:
        sqlite_session.close()
        postgres_session.close()


def main():
    parser = argparse.ArgumentParser(description='Migrate data from SQLite to PostgreSQL')
    parser.add_argument(
        '--sqlite',
        default='forecaster.db',
        help='Path to SQLite database file (default: forecaster.db)'
    )
    parser.add_argument(
        '--postgres',
        default=os.environ.get('DATABASE_URL'),
        help='PostgreSQL connection URL (default: from DATABASE_URL env var)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Perform a dry run without writing to PostgreSQL'
    )

    args = parser.parse_args()

    # Validate PostgreSQL URL
    if not args.postgres:
        print("❌ ERROR: PostgreSQL URL not provided")
        print()
        print("Provide it via:")
        print("  1. --postgres argument")
        print("  2. DATABASE_URL environment variable")
        print()
        print("Example:")
        print("  export DATABASE_URL='postgresql://user:pass@localhost:5432/forecaster'")
        print("  python migrate_to_postgres.py")
        sys.exit(1)

    # Fix Heroku postgres:// URL
    postgres_url = args.postgres
    if postgres_url.startswith('postgres://'):
        postgres_url = postgres_url.replace('postgres://', 'postgresql://', 1)

    # Run migration
    migrate_data(args.sqlite, postgres_url, args.dry_run)


if __name__ == '__main__':
    main()
