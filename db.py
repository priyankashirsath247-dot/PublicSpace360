import os
import sqlite3
import pymysql
import pymysql.cursors
from config import Config

_engine_type = None

def detect_engine():
    """Detect whether MySQL is accessible, else fallback to SQLite."""
    global _engine_type
    if _engine_type is not None:
        return _engine_type

    if Config.DB_BACKEND == 'sqlite':
        _engine_type = 'sqlite'
        return _engine_type

    # Try connecting to MySQL
    try:
        conn = pymysql.connect(
            host=Config.MYSQL_HOST,
            port=Config.MYSQL_PORT,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor,
            connect_timeout=3
        )
        # Create database if not exists
        with conn.cursor() as cur:
            cur.execute(f"CREATE DATABASE IF NOT EXISTS `{Config.MYSQL_DB}` CHARACTER SET utf8mb4;")
        conn.select_db(Config.MYSQL_DB)
        conn.close()
        _engine_type = 'mysql'
        print(f"[Database] Successfully connected to MySQL database '{Config.MYSQL_DB}' at {Config.MYSQL_HOST}:{Config.MYSQL_PORT}")
    except Exception as e:
        print(f"[Database] MySQL connection notice: {e}")
        print(f"[Database] Running in reliable local SQLite fallback mode at: {Config.SQLITE_DB}")
        _engine_type = 'sqlite'

    return _engine_type

def get_connection():
    """Returns an active connection for either MySQL or SQLite."""
    engine = detect_engine()
    if engine == 'mysql':
        conn = pymysql.connect(
            host=Config.MYSQL_HOST,
            port=Config.MYSQL_PORT,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True
        )
        return conn
    else:
        os.makedirs(os.path.dirname(Config.SQLITE_DB), exist_ok=True)
        conn = sqlite3.connect(Config.SQLITE_DB)
        conn.row_factory = sqlite3.Row
        return conn

def query_db(query, args=(), one=False):
    """Executes a SELECT query and returns dictionary rows."""
    engine = detect_engine()
    conn = get_connection()
    try:
        if engine == 'mysql':
            with conn.cursor() as cursor:
                cursor.execute(query, args)
                rows = cursor.fetchall()
                return (rows[0] if rows else None) if one else rows
        else:
            # For SQLite, translate %s to ?
            sqlite_query = query.replace('%s', '?')
            cursor = conn.cursor()
            cursor.execute(sqlite_query, args)
            rows = cursor.fetchall()
            dict_rows = [dict(row) for row in rows]
            return (dict_rows[0] if dict_rows else None) if one else dict_rows
    finally:
        conn.close()

def execute_db(query, args=()):
    """Executes an INSERT, UPDATE, or DELETE query and returns lastrowid."""
    engine = detect_engine()
    conn = get_connection()
    try:
        if engine == 'mysql':
            with conn.cursor() as cursor:
                cursor.execute(query, args)
                last_id = cursor.lastrowid
                conn.commit()
                return last_id
        else:
            sqlite_query = query.replace('%s', '?')
            cursor = conn.cursor()
            cursor.execute(sqlite_query, args)
            conn.commit()
            return cursor.lastrowid
    finally:
        conn.close()

def init_db(force_reinit=False):
    """Initializes tables and seeds Panvel dataset if empty or schema upgraded."""
    engine = detect_engine()
    sql_file = os.path.join(Config.BASE_DIR, 'database', 'publicspace360.sql')
    
    if engine == 'mysql':
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                # Check if public_space_images exists
                cursor.execute("SHOW TABLES LIKE 'public_space_images';")
                has_gallery_table = cursor.fetchone()
                
                # Check if public_spaces has Panvel area column
                has_area_col = False
                if has_gallery_table:
                    cursor.execute("SHOW COLUMNS FROM `public_spaces` LIKE 'area';")
                    has_area_col = cursor.fetchone() is not None

                if force_reinit or not has_gallery_table or not has_area_col:
                    print("[Database] Initializing MySQL tables from publicspace360.sql with Panvel dataset...")
                    with open(sql_file, 'r', encoding='utf-8') as f:
                        sql_content = f.read()
                    statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
                    for stmt in statements:
                        upper_stmt = stmt.upper()
                        if upper_stmt.startswith('USE ') or upper_stmt.startswith('CREATE DATABASE'):
                            continue
                        try:
                            cursor.execute(stmt)
                        except Exception as ex:
                            print(f"[MySQL Init Notice] {ex}")
                    conn.commit()
                    print("[Database] MySQL initialized with complete Panvel dataset!")
        finally:
            conn.close()
    else:
        # SQLite initialization
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='public_space_images';")
            has_gallery_table = cursor.fetchone()
            
            has_area_col = False
            if has_gallery_table:
                cursor.execute("PRAGMA table_info(public_spaces);")
                cols = [row['name'] for row in cursor.fetchall()]
                has_area_col = 'area' in cols

            if force_reinit or not has_gallery_table or not has_area_col:
                print("[Database] Initializing SQLite tables with complete Panvel dataset & multi-image gallery...")
                _init_sqlite_schema(conn)
                print("[Database] SQLite initialized with complete Panvel dataset!")
        finally:
            conn.close()

def _init_sqlite_schema(conn):
    cursor = conn.cursor()
    # Drop old tables to ensure clean Panvel schema
    cursor.executescript('''
    DROP TABLE IF EXISTS public_space_images;
    DROP TABLE IF EXISTS feedback;
    DROP TABLE IF EXISTS reports;
    DROP TABLE IF EXISTS surveys;
    DROP TABLE IF EXISTS public_spaces;
    DROP TABLE IF EXISTS areas;
    DROP TABLE IF EXISTS admins;
    DROP TABLE IF EXISTS contact_messages;
    DROP TABLE IF EXISTS users;

    CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      email TEXT NOT NULL UNIQUE,
      mobile TEXT NOT NULL,
      password TEXT NOT NULL,
      age_group TEXT NOT NULL,
      gender TEXT NOT NULL,
      role TEXT DEFAULT 'user',
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS admins (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      email TEXT NOT NULL UNIQUE,
      password TEXT NOT NULL,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS areas (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL UNIQUE,
      city TEXT DEFAULT 'Panvel'
    );

    CREATE TABLE IF NOT EXISTS public_spaces (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      area_id INTEGER NULL,
      area TEXT NOT NULL,
      name TEXT NOT NULL,
      type TEXT NOT NULL,
      address TEXT NOT NULL,
      latitude REAL NOT NULL,
      longitude REAL NOT NULL,
      description TEXT,
      facilities TEXT,
      opening_time TEXT DEFAULT '05:30 AM',
      closing_time TEXT DEFAULT '09:30 PM',
      average_visitors INTEGER DEFAULT 500,
      condition TEXT DEFAULT 'Good',
      primary_image TEXT,
      image_source TEXT DEFAULT 'Field Survey',
      image_credit TEXT DEFAULT 'Academic Research Team',
      google_maps_url TEXT,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (area_id) REFERENCES areas(id) ON DELETE SET NULL
    );

    CREATE TABLE IF NOT EXISTS public_space_images (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      public_space_id INTEGER NOT NULL,
      image_path TEXT NOT NULL,
      image_source TEXT DEFAULT 'Field Survey',
      image_credit TEXT DEFAULT 'Academic Research Team',
      is_primary INTEGER DEFAULT 0,
      uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (public_space_id) REFERENCES public_spaces(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS surveys (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      user_id INTEGER NULL,
      space_id INTEGER NOT NULL,
      visit_frequency TEXT NOT NULL,
      purpose TEXT NOT NULL,
      age_group TEXT NOT NULL,
      safety_rating INTEGER NOT NULL,
      cleanliness_rating INTEGER NOT NULL,
      lighting_rating INTEGER NOT NULL,
      seating_rating INTEGER NOT NULL,
      water_rating INTEGER NOT NULL,
      accessibility_rating INTEGER NOT NULL,
      improvement TEXT,
      suggestion TEXT,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (space_id) REFERENCES public_spaces(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS reports (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      user_id INTEGER NULL,
      space_id INTEGER NOT NULL,
      issue_type TEXT NOT NULL,
      description TEXT NOT NULL,
      photo TEXT,
      location TEXT,
      priority TEXT DEFAULT 'Medium',
      status TEXT DEFAULT 'Reported',
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (space_id) REFERENCES public_spaces(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS feedback (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      user_id INTEGER NULL,
      space_id INTEGER NOT NULL,
      user_name TEXT NOT NULL DEFAULT 'Community Visitor',
      user_email TEXT,
      rating INTEGER NOT NULL,
      comment TEXT NOT NULL,
      status TEXT DEFAULT 'Approved',
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (space_id) REFERENCES public_spaces(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS contact_messages (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      email TEXT NOT NULL,
      subject TEXT NOT NULL,
      message TEXT NOT NULL,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    ''')
    
    # Read seeds from SQL file
    sql_file = os.path.join(Config.BASE_DIR, 'database', 'publicspace360.sql')
    if os.path.exists(sql_file):
        with open(sql_file, 'r', encoding='utf-8') as f:
            raw_sql = f.read()

        # Remove line comments
        clean_lines = []
        for line in raw_sql.splitlines():
            s = line.strip()
            if not s or s.startswith('--') or s.startswith('/*'):
                continue
            clean_lines.append(line)
        cleaned_text = "\n".join(clean_lines)

        stmts = [s.strip() for s in cleaned_text.split(';') if s.strip()]
        for stmt in stmts:
            if stmt.upper().startswith('INSERT INTO'):
                try:
                    clean_stmt = stmt.replace('`', '"')
                    clean_stmt = clean_stmt.replace("\\'", "''")
                    cursor.execute(clean_stmt)
                except Exception as ex:
                    print(f"[SQLite Seed Notice] {ex}")
        conn.commit()

if __name__ == '__main__':
    init_db(force_reinit=True)
