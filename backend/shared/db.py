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
# CORE FUNCTIONS
# -----------------------------
def write_trace(
    workflow_id,
    workflow_type,
    step_id,
    agent,
    status,
    input_data=None,
    output_data=None,
    error_hash=None,
    error_type=None,
    decision=None,
    decision_reason=None,
    log_message=None,
    duration_ms=None,
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


def read_pattern(error_hash):
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM pattern_memory WHERE error_hash = ?",
            (error_hash,),
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def update_pattern(error_hash, retry_succeeded):
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT attempts, successes FROM pattern_memory WHERE error_hash = ?",
            (error_hash,),
        ).fetchone()

        if not row:
            return

        new_attempts = row["attempts"] + 1
        new_successes = row["successes"] + (1 if retry_succeeded else 0)
        new_rate = new_successes / new_attempts

        conn.execute(
            """
            UPDATE pattern_memory
            SET attempts=?, successes=?, success_rate=?
            WHERE error_hash=?
            """,
            (new_attempts, new_successes, new_rate, error_hash),
        )
        conn.commit()
    finally:
        conn.close()


def count_affected_workflows(error_hash):
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT DISTINCT workflow_id
            FROM traces
            WHERE error_hash = ?
            AND status IN ('failed', 'escalated')
            """,
            (error_hash,),
        ).fetchall()

        affected = [row["workflow_id"] for row in rows]
        return len(affected), affected
    finally:
        conn.close()


def write_systemic_alert(error_hash, error_type, affected_workflows, context=None):
    import json

    conn = get_connection()
    try:
        conn.execute(
            """
            INSERT INTO systemic_alerts
            (error_hash, error_type, affected_workflows,
             occurrence_count, context, created_at)
            VALUES (?,?,?,?,?,datetime('now','localtime'))
            """,
            (
                error_hash,
                error_type,
                json.dumps(affected_workflows),
                len(affected_workflows),
                context,
            ),
        )
        conn.commit()
    finally:
        conn.close()


def get_all_traces(limit=100):
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM traces ORDER BY created_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()

def get_briefing_history(limit: int = 10):
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM briefing_log ORDER BY created_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def get_workflow_traces(workflow_id: str):
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM traces WHERE workflow_id = ? ORDER BY created_at ASC",
            (workflow_id,),
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def get_systemic_alerts():
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM systemic_alerts WHERE resolved = 0 ORDER BY created_at DESC"
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()
