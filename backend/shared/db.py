import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

TURSO_URL = os.getenv("TURSO_DB_URL")
TURSO_TOKEN = os.getenv("TURSO_DB_TOKEN")


# -----------------------------
# Dict wrappers
# -----------------------------
class DictRow:
    def __init__(self, cursor, row):
        self._row = row
        self._cols = [col[0] for col in cursor.description] if cursor.description else []

    def keys(self):
        return self._cols

    def __getitem__(self, key):
        if isinstance(key, str):
            if key in self._cols:
                return self._row[self._cols.index(key)]
            raise KeyError(key)
        return self._row[key]


class DictCursor:
    def __init__(self, cursor):
        self._cursor = cursor

    def execute(self, *args, **kwargs):
        self._cursor.execute(*args, **kwargs)
        return self

    def executemany(self, *args, **kwargs):
        self._cursor.executemany(*args, **kwargs)
        return self

    def fetchone(self):
        row = self._cursor.fetchone()
        return DictRow(self._cursor, row) if row else None

    def fetchall(self):
        rows = self._cursor.fetchall()
        return [DictRow(self._cursor, row) for row in rows] if rows else []

    def __iter__(self):
        for row in self._cursor:
            yield DictRow(self._cursor, row)

    def close(self):
        self._cursor.close()

    @property
    def description(self):
        return self._cursor.description

    @property
    def rowcount(self):
        return self._cursor.rowcount

    @property
    def lastrowid(self):
        return self._cursor.lastrowid


class DictConnection:
    def __init__(self, conn):
        self._conn = conn

    def cursor(self):
        return DictCursor(self._conn.cursor())

    def execute(self, *args, **kwargs):
        return self.cursor().execute(*args, **kwargs)

    def executemany(self, *args, **kwargs):
        return self.cursor().executemany(*args, **kwargs)

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()

    def close(self):
        self._conn.close()


# -----------------------------
# CONNECTION
# -----------------------------
def get_connection():
    if TURSO_URL and TURSO_TOKEN:
        import libsql_experimental as sqlite3

        conn = sqlite3.connect(
            database=TURSO_URL,
            auth_token=TURSO_TOKEN,
            check_same_thread=False
        )

        return DictConnection(conn)

    else:
        import sqlite3

        DB_PATH = str(Path(__file__).resolve().parent.parent / "auditpilot.db")

        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        conn.row_factory = sqlite3.Row

        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA cache_size=-64000")

        return conn


# -----------------------------
# REQUIRED FUNCTIONS (ADD BACK)
# -----------------------------
def write_trace(
    workflow_id: str,
    workflow_type: str,
    step_id: str,
    agent: str,
    status: str,
    input_data: dict = None,
    output_data: dict = None,
    error_hash: str = None,
    error_type: str = None,
    decision: str = None,
    decision_reason: str = None,
    log_message: str = None,
    duration_ms: int = None,
):
    import json

    conn = get_connection()

    try:
        conn.execute(
            """
            INSERT INTO traces
            (workflow_id, workflow_type, step_id, agent,
             input_data, output_data, status,
             error_hash, error_type, decision, decision_reason,
             log_message, duration_ms, created_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,datetime('now','localtime'))
            """,
            (
                workflow_id,
                workflow_type,
                step_id,
                agent,
                json.dumps(input_data) if input_data else None,
                json.dumps(output_data) if output_data else None,
                status,
                error_hash,
                error_type,
                decision,
                decision_reason,
                log_message,
                duration_ms,
            ),
        )
        conn.commit()
    finally:
        conn.close()
