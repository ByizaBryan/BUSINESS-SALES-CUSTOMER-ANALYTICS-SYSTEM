"""
InsightMart Business Sales & Customer Analytics System
Module: src/database.py
Description: Enterprise-grade database connection manager supporting MySQL with automatic
             fallback to SQLite for seamless development, testing, and cloud deployment.
"""

import os
import re
import sqlite3
import logging
from pathlib import Path
from contextlib import contextmanager
from dotenv import load_dotenv

# Configure module logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("DatabaseManager")

# Load environment variables from .env if present
ROOT_DIR = Path(__file__).resolve().parent.parent
env_path = ROOT_DIR / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()

# Database configuration settings
DB_TYPE = os.getenv("DB_TYPE", "mysql").lower()
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_NAME = os.getenv("DB_NAME", "business_sales_db")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
SQLITE_PATH = os.getenv("SQLITE_PATH", str(ROOT_DIR / "data" / "processed" / "business_sales.db"))


class DatabaseConnectionError(Exception):
    """Custom exception for database connection issues."""
    pass


# Global cached connection status for the current runtime process
_MYSQL_AVAILABLE = None


def _init_serverless_sqlite(target_path: Path):
    """Initializes SQLite database in /tmp if bundled db was not found."""
    conn = sqlite3.connect(str(target_path))
    schema_path = ROOT_DIR / "database" / "database_schema.sql"
    seed_path = ROOT_DIR / "database" / "sample_data.sql"
    if schema_path.exists():
        with open(schema_path, "r", encoding="utf-8") as f:
            clean_script = f.read()
            clean_script = re.sub(r'CREATE DATABASE.*?;', '', clean_script, flags=re.IGNORECASE | re.DOTALL)
            clean_script = re.sub(r'USE\s+\w+;', '', clean_script, flags=re.IGNORECASE)
            clean_script = re.sub(r'ENGINE\s*=\s*InnoDB', '', clean_script, flags=re.IGNORECASE)
            clean_script = re.sub(r'AUTO_INCREMENT', 'AUTOINCREMENT', clean_script, flags=re.IGNORECASE)
            clean_script = re.sub(r'INT\s+AUTOINCREMENT', 'INTEGER', clean_script, flags=re.IGNORECASE)
            clean_script = re.sub(r'INT\s+PRIMARY KEY\s+AUTOINCREMENT', 'INTEGER PRIMARY KEY AUTOINCREMENT', clean_script, flags=re.IGNORECASE)
            clean_script = re.sub(r'CREATE OR REPLACE VIEW', 'CREATE VIEW IF NOT EXISTS', clean_script, flags=re.IGNORECASE)
            conn.executescript(clean_script)
    if seed_path.exists():
        with open(seed_path, "r", encoding="utf-8") as f:
            seed_script = f.read()
            seed_script = re.sub(r'USE\s+\w+;', '', seed_script, flags=re.IGNORECASE)
            conn.executescript(seed_script)
    conn.commit()
    conn.close()


def get_connection():
    """
    Establishes and returns a database connection based on configuration.
    Attempts MySQL first if DB_TYPE is 'mysql'. Falls back cleanly to SQLite if
    the MySQL server cannot be reached, ensuring zero-downtime development and testing.
    Caches connection reachability during runtime to prevent repeated socket timeouts.
    Supports Vercel serverless functions by isolating SQLite in /tmp.
    """
    global DB_TYPE, _MYSQL_AVAILABLE

    # Serverless runtime detection (Vercel / AWS Lambda)
    is_serverless = os.getenv("VERCEL") == "1" or "AWS_LAMBDA_FUNCTION_NAME" in os.environ
    if is_serverless:
        has_remote_mysql = DB_TYPE == "mysql" and DB_HOST not in ["localhost", "127.0.0.1", ""] and DB_PASSWORD
        if not has_remote_mysql:
            tmp_db = Path("/tmp/business_sales.db")
            bundled_db = ROOT_DIR / "data" / "processed" / "business_sales.db"
            if not tmp_db.exists() or tmp_db.stat().st_size < 1000:
                if bundled_db.exists() and bundled_db.stat().st_size > 1000:
                    import shutil
                    shutil.copyfile(bundled_db, tmp_db)
                else:
                    _init_serverless_sqlite(tmp_db)
            conn = sqlite3.connect(str(tmp_db))
            conn.row_factory = sqlite3.Row
            return conn, "sqlite"

    if DB_TYPE == "sqlite" or _MYSQL_AVAILABLE is False:
        os.makedirs(os.path.dirname(os.path.abspath(SQLITE_PATH)), exist_ok=True)
        conn = sqlite3.connect(SQLITE_PATH)
        conn.row_factory = sqlite3.Row
        return conn, "sqlite"

    if DB_TYPE == "mysql" and _MYSQL_AVAILABLE is not False:
        try:
            import pymysql
            from pymysql.cursors import DictCursor

            # Check if database exists; if not, connect without db to create it if needed
            try:
                conn = pymysql.connect(
                    host=DB_HOST,
                    port=DB_PORT,
                    user=DB_USER,
                    password=DB_PASSWORD,
                    database=DB_NAME,
                    cursorclass=DictCursor,
                    autocommit=False,
                    connect_timeout=3
                )
                return conn, "mysql"
            except pymysql.err.OperationalError as op_err:
                # Error 1049: Unknown database -> try connecting to host and creating it
                if op_err.args[0] == 1049:
                    logger.info(f"Database '{DB_NAME}' not found. Creating database on {DB_HOST}...")
                    init_conn = pymysql.connect(
                        host=DB_HOST,
                        port=DB_PORT,
                        user=DB_USER,
                        password=DB_PASSWORD,
                        cursorclass=DictCursor,
                        autocommit=True,
                        connect_timeout=3
                    )
                    with init_conn.cursor() as cur:
                        cur.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` CHARACTER SET utf8mb4;")
                    init_conn.close()
                    # Now reconnect with database
                    conn = pymysql.connect(
                        host=DB_HOST,
                        port=DB_PORT,
                        user=DB_USER,
                        password=DB_PASSWORD,
                        database=DB_NAME,
                        cursorclass=DictCursor,
                        autocommit=False,
                        connect_timeout=3
                    )
                    return conn, "mysql"
                else:
                    raise op_err

        except Exception as e:
            _MYSQL_AVAILABLE = False
            logger.warning(f"MySQL connection to {DB_HOST}:{DB_PORT}/{DB_NAME} failed ({e}). "
                           f"Falling back to local SQLite engine ({SQLITE_PATH}).")

    # SQLite Engine
    os.makedirs(os.path.dirname(os.path.abspath(SQLITE_PATH)), exist_ok=True)
    conn = sqlite3.connect(SQLITE_PATH)
    conn.row_factory = sqlite3.Row  # Access columns by name like a dictionary
    return conn, "sqlite"


@contextmanager
def get_db_cursor(commit=False):
    """
    Context manager that yields (cursor, engine_type) and handles transaction commit/rollback.
    """
    conn, engine = get_connection()
    cursor = conn.cursor()
    try:
        yield cursor, engine
        if commit:
            conn.commit()
    except Exception as err:
        if commit:
            conn.rollback()
        logger.error(f"Database operation failed: {err}")
        raise
    finally:
        cursor.close()
        conn.close()


def _normalize_query_for_engine(query: str, engine: str) -> str:
    """
    Adapts SQL syntax between MySQL and SQLite if necessary.
    - Parameter placeholders: converts %s to ? for SQLite
    - Date format conversions if required
    """
    if engine == "sqlite":
        # Replace MySQL %s parameter placeholder with SQLite ? placeholder
        # Careful not to replace % inside string literals like '%Y-%m'
        # We replace %s when preceded by whitespace, comma, parenthesis or equals
        normalized = re.sub(r'(?<=[(\s,=])%s', '?', query)
        return normalized
    return query


def execute_query(query: str, params: tuple = None, fetch_one: bool = False):
    """
    Executes a SELECT query and returns the results as a list of dicts (or single dict).
    Uses parameterized execution to guarantee protection against SQL injection.
    """
    with get_db_cursor(commit=False) as (cursor, engine):
        normalized_sql = _normalize_query_for_engine(query, engine)
        if params:
            cursor.execute(normalized_sql, params)
        else:
            cursor.execute(normalized_sql)

        if fetch_one:
            row = cursor.fetchone()
            if row is None:
                return None
            return dict(row) if engine == "sqlite" else row
        else:
            rows = cursor.fetchall()
            if engine == "sqlite":
                return [dict(row) for row in rows]
            return list(rows)


def execute_non_query(query: str, params: tuple = None) -> int:
    """
    Executes an INSERT, UPDATE, or DELETE statement within a transaction and returns affected rows.
    """
    with get_db_cursor(commit=True) as (cursor, engine):
        normalized_sql = _normalize_query_for_engine(query, engine)
        if params:
            cursor.execute(normalized_sql, params)
        else:
            cursor.execute(normalized_sql)
        return cursor.rowcount


def execute_script(script_content: str):
    """
    Executes a multi-statement SQL script.
    """
    conn, engine = get_connection()
    try:
        cursor = conn.cursor()
        if engine == "sqlite":
            # Strip MySQL-specific engine clauses and database definitions for SQLite
            clean_script = script_content
            clean_script = re.sub(r'CREATE DATABASE.*?;', '', clean_script, flags=re.IGNORECASE | re.DOTALL)
            clean_script = re.sub(r'USE\s+\w+;', '', clean_script, flags=re.IGNORECASE)
            clean_script = re.sub(r'ENGINE\s*=\s*InnoDB', '', clean_script, flags=re.IGNORECASE)
            clean_script = re.sub(r'AUTO_INCREMENT', 'AUTOINCREMENT', clean_script, flags=re.IGNORECASE)
            clean_script = re.sub(r'INT\s+AUTOINCREMENT', 'INTEGER', clean_script, flags=re.IGNORECASE)
            clean_script = re.sub(r'INT\s+PRIMARY KEY\s+AUTOINCREMENT', 'INTEGER PRIMARY KEY AUTOINCREMENT', clean_script, flags=re.IGNORECASE)
            clean_script = re.sub(r'CREATE OR REPLACE VIEW', 'CREATE VIEW IF NOT EXISTS', clean_script, flags=re.IGNORECASE)
            conn.executescript(clean_script)
            conn.commit()
        else:
            # For MySQL, split statements by semicolon
            statements = [s.strip() for s in script_content.split(";") if s.strip()]
            for stmt in statements:
                cursor.execute(stmt)
            conn.commit()
        cursor.close()
        logger.info(f"Successfully executed SQL script using {engine} engine.")
    except Exception as e:
        conn.rollback()
        logger.error(f"Failed to execute SQL script on {engine}: {e}")
        raise
    finally:
        conn.close()


def initialize_schema():
    """
    Initializes the database schema using database/database_schema.sql.
    """
    schema_path = ROOT_DIR / "database" / "database_schema.sql"
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found at: {schema_path}")

    with open(schema_path, "r", encoding="utf-8") as f:
        sql_content = f.read()

    logger.info("Applying database schema definition...")
    execute_script(sql_content)
    logger.info("Database schema initialized successfully.")


if __name__ == "__main__":
    logger.info("Testing database connection...")
    conn, engine = get_connection()
    logger.info(f"Connected to database successfully using engine: {engine}")
    conn.close()
    initialize_schema()
