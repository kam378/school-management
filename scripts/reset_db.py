
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
import sys

# Default credentials from settings.py
DB_NAME = os.environ.get('POSTGRES_DB', 'school_db')
DB_USER = os.environ.get('POSTGRES_USER', 'school_user')
DB_PASSWORD = os.environ.get('POSTGRES_PASSWORD', 'school_password')
DB_HOST = os.environ.get('POSTGRES_HOST', '127.0.0.1')
DB_PORT = os.environ.get("DB_PORT", "5432")

def reset_db():
    print(f"Connecting to Postgres at {DB_HOST}:{DB_PORT} as {DB_USER}...")
    try:
        # Connect to 'postgres' db to drop the target db
        conn = psycopg2.connect(
            dbname="postgres",
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()

        # Terminate existing connections
        print(f"Terminating connections to {DB_NAME}...")
        cur.execute(f"""
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = '{DB_NAME}'
            AND pid <> pg_backend_pid();
        """)

        # Drop DB
        print(f"Dropping database {DB_NAME}...")
        cur.execute(f"DROP DATABASE IF EXISTS {DB_NAME};")

        # Create DB
        print(f"Creating database {DB_NAME}...")
        cur.execute(f"CREATE DATABASE {DB_NAME};")

        cur.close()
        conn.close()
        print("Database reset successfully.")

    except Exception as e:
        print(f"Error: {e}")
        print("Ensure the database container is running and port 5432 is accessible.")
        sys.exit(1)

if __name__ == "__main__":
    reset_db()
