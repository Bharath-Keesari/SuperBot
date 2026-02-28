"""HR Handler — employees, leave, policies, org chart."""
import os, sys, sqlite3
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config.settings import SQLITE_PATH

DB = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", SQLITE_PATH))

def _q(sql, params=(), one=False):
    conn = sqlite3.connect(DB); conn.row_factory = sqlite3.Row
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    r = [dict(x) for x in rows]
    return r[0] if one and r else r

def _exec(sql, params=()):
    conn = sqlite3.connect(DB)
    conn.execute(sql, params); conn.commit(); conn.close()

# ── Employees ─────────────────────────────────────────────────────────────────

def search_employees(name: str = None, dept: str = None, location: str = None) -> list:
    sql = "SELECT * FROM employees WHERE status='active'"
    p = []
    if name:
        sql += " AND LOWER(full_name) LIKE ?"; p.append(f"%{name.lower()}%")
    if dept:
        sql += " AND LOWER(department) LIKE ?"; p.append(f"%{dept.lower()}%")
    if location:
        sql += " AND LOWER(location) LIKE ?"; p.append(f"%{location.lower()}%")
    return _q(sql, p)

def get_employee(identifier: str) -> dict:
    r = _q("SELECT e.*, m.full_name as manager_name FROM employees e "
           "LEFT JOIN employees m ON e.manager_id=m.id "
           "WHERE e.emp_id=? OR LOWER(e.full_name) LIKE ? OR e.email=?",
           (identifier, f"%{identifier.lower()}%", identifier), one=True)
    if r:
        r["direct_reports"] = _q("SELECT id,full_name,job_title,email FROM employees WHERE manager_id=?", (r["id"],))
        r["leave_balances"] = get_leave_balance(r["emp_id"])
    return r or {}

def get_org_chart(dept: str = None) -> list:
    sql = "SELECT id,emp_id,full_name,job_title,department,manager_id,avatar_initials FROM employees WHERE status='active'"
    p = []
    if dept:
        sql += " AND LOWER(department) LIKE ?"; p.append(f"%{dept.lower()}%")
    return _q(sql, p)

def get_departments() -> list:
    return _q("SELECT DISTINCT department, COUNT(*) as headcount FROM employees WHERE status='active' GROUP BY department")

# ── Leave ─────────────────────────────────────────────────────────────────────

def get_leave_balance(emp_id: str) -> list:
    return _q("SELECT * FROM leave_balances WHERE emp_id=? AND year=2024", (emp_id,))

def get_leave_requests(emp_id: str = None, status: str = None) -> list:
    sql = "SELECT lr.*, e.full_name FROM leave_requests lr JOIN employees e ON lr.emp_id=e.emp_id WHERE 1=1"
    p = []
    if emp_id: sql += " AND lr.emp_id=?"; p.append(emp_id)
    if status: sql += " AND LOWER(lr.status)=?"; p.append(status.lower())
    return _q(sql + " ORDER BY lr.applied_date DESC", p)

def apply_leave(emp_id: str, leave_type: str, start_date: str, end_date: str, reason: str) -> dict:
    from datetime import datetime
    from datetime import date as dt_date
    try:
        s = dt_date.fromisoformat(start_date); e = dt_date.fromisoformat(end_date)
        days = (e - s).days + 1
    except:
        return {"success": False, "message": "Invalid date format. Use YYYY-MM-DD"}

    # Check balance
    bal = _q("SELECT remaining FROM leave_balances WHERE emp_id=? AND leave_type=? AND year=2024",
             (emp_id, leave_type), one=True)
    if bal and bal["remaining"] < days:
        return {"success": False, "message": f"Insufficient {leave_type} balance. Available: {bal['remaining']} days, Requested: {days} days"}

    today = datetime.now().strftime("%Y-%m-%d")
    _exec("INSERT INTO leave_requests (emp_id,leave_type,start_date,end_date,days,status,reason,applied_date) VALUES (?,?,?,?,?,?,?,?)",
          (emp_id, leave_type, start_date, end_date, days, "PENDING", reason, today))
    return {"success": True, "message": f"Leave request submitted! {leave_type}: {start_date} to {end_date} ({days} days). Awaiting manager approval."}

# ── Helpdesk ──────────────────────────────────────────────────────────────────

def get_helpdesk_tickets(raised_by: str = None, status: str = None, category: str = None) -> list:
    sql = "SELECT * FROM helpdesk_tickets WHERE 1=1"
    p = []
    if raised_by: sql += " AND LOWER(raised_by) LIKE ?"; p.append(f"%{raised_by.lower()}%")
    if status: sql += " AND LOWER(status)=?"; p.append(status.lower())
    if category: sql += " AND LOWER(category) LIKE ?"; p.append(f"%{category.lower()}%")
    return _q(sql + " ORDER BY created_date DESC", p)

def create_helpdesk_ticket(title: str, description: str, category: str, priority: str, raised_by: str) -> dict:
    from datetime import datetime
    count = _q("SELECT COUNT(*) as c FROM helpdesk_tickets", one=True)["c"]
    tid = f"TKT-{count+1:03d}"
    today = datetime.now().strftime("%Y-%m-%d")
    _exec("INSERT INTO helpdesk_tickets (ticket_id,title,description,category,priority,status,raised_by,assigned_to,created_date) VALUES (?,?,?,?,?,?,?,?,?)",
          (tid, title, description, category, priority, "OPEN", raised_by, "IT Team", today))
    return {"ticket_id": tid, "status": "OPEN", "message": f"✅ IT ticket {tid} created! IT team will respond within 4 hours for HIGH priority, 24 hours for MEDIUM/LOW."}

# ── Announcements ─────────────────────────────────────────────────────────────

def get_announcements(pinned_only: bool = False) -> list:
    sql = "SELECT * FROM announcements"
    if pinned_only: sql += " WHERE pinned=1"
    return _q(sql + " ORDER BY pinned DESC, posted_date DESC")

# ── Expenses ──────────────────────────────────────────────────────────────────

def get_expenses(emp_id: str = None, status: str = None) -> list:
    sql = "SELECT e.*, emp.full_name FROM expenses e JOIN employees emp ON e.emp_id=emp.emp_id WHERE 1=1"
    p = []
    if emp_id: sql += " AND e.emp_id=?"; p.append(emp_id)
    if status: sql += " AND LOWER(e.status)=?"; p.append(status.lower())
    return _q(sql + " ORDER BY e.date DESC", p)
