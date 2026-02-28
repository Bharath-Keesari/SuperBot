"""Data / Analytics Handler — SQL warehouse queries."""
import os, sys, sqlite3
from typing import Optional
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config.settings import DB_BACKEND, SQLITE_PATH

DB = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", SQLITE_PATH))

def _q(sql, params=()):
    conn = sqlite3.connect(DB); conn.row_factory = sqlite3.Row
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def _get_connection():
    if DB_BACKEND == "sqlite":
        db_path = os.path.join(os.path.dirname(__file__), "..", SQLITE_PATH)
        db_path = os.path.normpath(db_path)
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn

    elif DB_BACKEND == "synapse":
        import pyodbc
        from config.settings import (
            SYNAPSE_SERVER,
            SYNAPSE_DATABASE,
            SYNAPSE_USERNAME,
            SYNAPSE_PASSWORD
        )

        conn_str = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={SYNAPSE_SERVER};"
            f"DATABASE={SYNAPSE_DATABASE};"
            f"UID={SYNAPSE_USERNAME};"
            f"PWD={SYNAPSE_PASSWORD}"
        )

        return pyodbc.connect(conn_str)

    else:
        raise ValueError(f"Unknown DB_BACKEND: {DB_BACKEND}")
    
def _query(sql: str, params: tuple = ()) -> list[dict]:
    conn = _get_connection()
    cur = conn.cursor()
    cur.execute(sql, params)

    columns = [col[0] for col in cur.description]
    rows = [dict(zip(columns, row)) for row in cur.fetchall()]

    conn.close()
    return rows

def find_tables_by_column(column: str, schema: Optional[str] = None) -> dict:
    if DB_BACKEND == "sqlite":
        schema_meta = get_schema_metadata()
        matches = []

        def normalize(name: str) -> str:
            return name.lower().replace("_", "").replace(" ", "")

        search_term = normalize(column)

        for table, cols in schema_meta["tables"].items():
            for col in cols:
                if normalize(col) == search_term:
                    matches.append({
                        "TABLE_NAME": table,
                        "COLUMN_NAME": col,
                        "DATA_TYPE": "UNKNOWN"
                    })

        return {
            "intent": "UC1_COLUMN_FINDER",
            "query_term": column,
            "count": len(matches),
            "results": matches
        }

    else:
        if schema:
            rows = _query("""
                SELECT TABLE_SCHEMA, TABLE_NAME, COLUMN_NAME, DATA_TYPE,
                       IS_NULLABLE, ORDINAL_POSITION
                FROM information_schema_columns
                WHERE LOWER(COLUMN_NAME) LIKE LOWER(?)
                  AND LOWER(TABLE_SCHEMA) = LOWER(?)
                ORDER BY TABLE_SCHEMA, TABLE_NAME
            """, (f"%{column}%", schema))
        else:
            rows = _query("""
                SELECT TABLE_SCHEMA, TABLE_NAME, COLUMN_NAME, DATA_TYPE,
                       IS_NULLABLE, ORDINAL_POSITION
                FROM information_schema_columns
                WHERE LOWER(COLUMN_NAME) LIKE LOWER(?)
                ORDER BY TABLE_SCHEMA, TABLE_NAME
            """, (f"%{column}%",))

        return {
            "intent": "UC1_COLUMN_FINDER",
            "query_term": column,
            "count": len(rows),
            "results": rows
        }

def get_table_schema(table: str) -> dict:
    cols  = _q("SELECT * FROM dw_columns WHERE LOWER(table_name)=? ORDER BY ordinal_position", (table.lower(),))
    meta  = _q("SELECT * FROM dw_tables WHERE LOWER(table_name)=?", (table.lower(),))
    return {"table": table, "metadata": meta[0] if meta else {}, "columns": cols, "column_count": len(cols)}

def list_all_tables(schema: str = None) -> dict:
    sql = "SELECT * FROM dw_tables"
    p = []
    if schema:
        sql += " WHERE LOWER(table_schema) LIKE ?"; p.append(f"%{schema.lower()}%")
    rows = _q(sql + " ORDER BY table_schema,table_name", p)
    return {"count": len(rows), "tables": rows}

def get_pipeline_status(pipeline: str = None) -> dict:
    sql = "SELECT * FROM pipeline_runs"
    p = []
    if pipeline:
        sql += " WHERE LOWER(pipeline_name) LIKE ?"; p.append(f"%{pipeline.lower()}%")
    rows = _q(sql + " ORDER BY start_time DESC", p)
    failed = [r for r in rows if r["status"] == "FAILED"]
    return {"runs": rows, "failed_count": len(failed), "total": len(rows)}

def get_quality_checks(table: str = None) -> dict:
    sql = "SELECT * FROM data_quality_checks"
    p = []
    if table:
        sql += " WHERE LOWER(table_name) LIKE ?"; p.append(f"%{table.lower()}%")
    rows = _q(sql, p)
    summary = {s: sum(1 for r in rows if r["check_status"]==s) for s in ["PASS","WARN","FAIL"]}
    return {"checks": rows, "summary": summary}

def get_schema_metadata() -> dict:

    if DB_BACKEND == "sqlite":
        conn = _get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        schema_dict = {}

        for table in tables:
            table_name = table[0]

            if table_name.startswith("sqlite_"):
                continue

            cursor.execute(f"PRAGMA table_info({table_name});")
            cols = cursor.fetchall()
            schema_dict[table_name] = [col[1] for col in cols]

        conn.close()

    else:
        rows = _query("""
            SELECT TABLE_SCHEMA, TABLE_NAME, COLUMN_NAME
            FROM information_schema_columns
            ORDER BY TABLE_SCHEMA, TABLE_NAME, ORDINAL_POSITION
        """)

        schema_dict = {}
        for r in rows:
            full_table = f"{r['TABLE_SCHEMA']}.{r['TABLE_NAME']}"
            schema_dict.setdefault(full_table, []).append(r["COLUMN_NAME"])

    return {
        "intent": "DATA_SCHEMA",
        "tables": schema_dict,
        "table_count": len(schema_dict)
    }