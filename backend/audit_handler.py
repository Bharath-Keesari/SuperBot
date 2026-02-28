"""Audit logging, analytics, alerts, feedback."""
import os, sys, sqlite3
from datetime import datetime
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config.settings import SQLITE_PATH

DB = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", SQLITE_PATH))

def _exec(sql, params=()):
    conn = sqlite3.connect(DB); conn.row_factory = sqlite3.Row
    cur = conn.execute(sql, params); conn.commit()
    result = cur.lastrowid; conn.close(); return result

def _q(sql, params=()):
    conn = sqlite3.connect(DB); conn.row_factory = sqlite3.Row
    rows = conn.execute(sql, params).fetchall(); conn.close()
    return [dict(r) for r in rows]

# ── Audit ──────────────────────────────────────────────────────────────────
def log_action(user: str, action: str, module: str, details: str = ""):
    try:
        _exec("INSERT INTO audit_logs (user_name,action,module,details,timestamp) VALUES (?,?,?,?,?)",
              (user, action, module, details[:500], datetime.now().isoformat()))
    except: pass

def get_audit_log(limit=50) -> list:
    try: return _q("SELECT * FROM audit_logs ORDER BY timestamp DESC LIMIT ?", (limit,))
    except: return []

# ── Conversation History ────────────────────────────────────────────────────
def save_message(session_id: str, user: str, role: str, content: str, module: str = "general") -> int:
    try:
        return _exec("INSERT INTO conversation_history (session_id,user_name,role,content,module,timestamp) VALUES (?,?,?,?,?,?)",
                     (session_id, user, role, content[:2000], module, datetime.now().isoformat()))
    except: return 0

def get_history(session_id: str, limit=20) -> list:
    try: return _q("SELECT * FROM conversation_history WHERE session_id=? ORDER BY timestamp DESC LIMIT ?", (session_id, limit))
    except: return []

def get_all_sessions(user: str = None) -> list:
    sql = "SELECT session_id, user_name, MIN(timestamp) as started, COUNT(*) as messages FROM conversation_history"
    if user: sql += f" WHERE user_name='{user}'"
    sql += " GROUP BY session_id ORDER BY started DESC LIMIT 20"
    try: return _q(sql)
    except: return []

# ── Feedback ───────────────────────────────────────────────────────────────
def save_feedback(message_id: int, user: str, rating: int, comment: str = "") -> bool:
    try:
        _exec("INSERT INTO feedback (message_id,user_name,rating,comment,timestamp) VALUES (?,?,?,?,?)",
              (message_id, user, rating, comment, datetime.now().isoformat()))
        return True
    except: return False

def get_feedback_stats() -> dict:
    try:
        rows = _q("SELECT rating, COUNT(*) as count FROM feedback GROUP BY rating")
        total = sum(r["count"] for r in rows)
        positive = sum(r["count"] for r in rows if r["rating"] > 0)
        return {"total": total, "positive": positive, "negative": total-positive,
                "satisfaction": round(positive/total*100) if total else 0}
    except: return {"total":0,"positive":0,"negative":0,"satisfaction":0}

# ── Analytics ──────────────────────────────────────────────────────────────
def log_query(user: str, module: str, intent: str, query_len: int, resp_ms: int):
    try:
        now = datetime.now()
        _exec("INSERT INTO usage_analytics (user_name,module,intent,query_length,response_time_ms,date,hour) VALUES (?,?,?,?,?,?,?)",
              (user, module, intent, query_len, resp_ms, now.strftime("%Y-%m-%d"), now.hour))
    except: pass

def get_analytics() -> dict:
    try:
        total = _q("SELECT COUNT(*) as c FROM usage_analytics", ())[0]["c"] if _q("SELECT COUNT(*) as c FROM usage_analytics") else 0
        by_module = _q("SELECT module, COUNT(*) as count FROM usage_analytics GROUP BY module ORDER BY count DESC")
        by_day    = _q("SELECT date, COUNT(*) as count FROM usage_analytics GROUP BY date ORDER BY date DESC LIMIT 7")
        avg_resp  = _q("SELECT AVG(response_time_ms) as avg FROM usage_analytics")[0]["avg"] or 0
        return {"total_queries": total, "by_module": by_module, "by_day": by_day, "avg_response_ms": round(avg_resp)}
    except: return {"total_queries":0,"by_module":[],"by_day":[],"avg_response_ms":0}

# ── Alerts ─────────────────────────────────────────────────────────────────
def get_alerts(unread_only=True) -> list:
    try:
        sql = "SELECT * FROM alerts"
        if unread_only: sql += " WHERE is_read=0"
        return _q(sql + " ORDER BY created_at DESC")
    except: return []

def mark_alert_read(alert_id: int):
    try: _exec("UPDATE alerts SET is_read=1 WHERE id=?", (alert_id,))
    except: pass

def create_alert(alert_type: str, title: str, message: str, severity: str = "info"):
    try:
        _exec("INSERT INTO alerts (alert_type,title,message,severity,is_read,created_at) VALUES (?,?,?,?,0,?)",
              (alert_type, title, message, severity, datetime.now().isoformat()))
    except: pass

# ── MCP Tools ──────────────────────────────────────────────────────────────
def get_mcp_tools(enabled_only=True) -> list:
    try:
        sql = "SELECT * FROM mcp_tools"
        if enabled_only: sql += " WHERE enabled=1"
        return _q(sql + " ORDER BY module, tool_name")
    except: return []

def increment_tool_call(tool_name: str):
    try: _exec("UPDATE mcp_tools SET call_count=call_count+1 WHERE tool_name=?", (tool_name,))
    except: pass

# ── Documents ──────────────────────────────────────────────────────────────
def register_document(filename: str, file_type: str, size: int, user: str, chunks: int) -> int:
    try:
        return _exec("INSERT INTO documents (filename,file_type,file_size,uploaded_by,uploaded_at,chunk_count,status) VALUES (?,?,?,?,?,?,'indexed')",
                     (filename, file_type, size, user, datetime.now().isoformat(), chunks))
    except: return 0

def get_documents() -> list:
    try: return _q("SELECT * FROM documents ORDER BY uploaded_at DESC")
    except: return []

def delete_document_record(filename: str):
    try: _exec("DELETE FROM documents WHERE filename=?", (filename,))
    except: pass
