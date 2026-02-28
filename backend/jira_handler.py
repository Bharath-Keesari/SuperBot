"""Jira Handler — Full CRUD for stories, tasks, subtasks, bugs, epics."""
import os, sys, sqlite3
from datetime import datetime
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config.settings import SQLITE_PATH

DB = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", SQLITE_PATH))

def _q(sql, params=(), one=False):
    conn = sqlite3.connect(DB); conn.row_factory = sqlite3.Row
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    result = [dict(r) for r in rows]
    return result[0] if one and result else result

def _exec(sql, params=()):
    conn = sqlite3.connect(DB)
    cur = conn.execute(sql, params)
    conn.commit(); last = cur.lastrowid; conn.close()
    return last

def _emp_name(emp_id):
    if not emp_id: return "Unassigned"
    r = _q("SELECT full_name FROM employees WHERE id=?", (emp_id,), one=True)
    return r["full_name"] if r else "Unknown"

# ── Read Operations ───────────────────────────────────────────────────────────

def get_issues(filters: dict = None) -> list:
    """Get issues with optional filters: assignee_name, status, type, project, sprint, priority"""
    sql = """SELECT i.*, 
             (SELECT full_name FROM employees WHERE id=i.assignee_id) as assignee_name,
             (SELECT full_name FROM employees WHERE id=i.reporter_id) as reporter_name
             FROM jira_issues i WHERE 1=1"""
    params = []
    if filters:
        if filters.get("assignee_name"):
            sql += " AND LOWER((SELECT full_name FROM employees WHERE id=i.assignee_id)) LIKE ?"
            params.append(f"%{filters['assignee_name'].lower()}%")
        if filters.get("status"):
            sql += " AND LOWER(i.status)=?"
            params.append(filters["status"].lower())
        if filters.get("issue_type"):
            sql += " AND LOWER(i.issue_type)=?"
            params.append(filters["issue_type"].lower())
        if filters.get("project"):
            sql += " AND LOWER(i.project_key) LIKE ?"
            params.append(f"%{filters['project'].lower()}%")
        if filters.get("sprint"):
            sql += " AND LOWER(i.sprint) LIKE ?"
            params.append(f"%{filters['sprint'].lower()}%")
        if filters.get("priority"):
            sql += " AND LOWER(i.priority)=?"
            params.append(filters["priority"].lower())
        if filters.get("parent_key"):
            sql += " AND i.parent_key=?"
            params.append(filters["parent_key"])
        if filters.get("issue_key"):
            sql += " AND i.issue_key=?"
            params.append(filters["issue_key"])
        if filters.get("keyword"):
            sql += " AND (LOWER(i.title) LIKE ? OR LOWER(i.description) LIKE ?)"
            k = f"%{filters['keyword'].lower()}%"
            params.extend([k, k])
    sql += " ORDER BY i.updated_date DESC LIMIT 50"
    return _q(sql, params)

def get_issue_detail(issue_key: str) -> dict:
    issue = _q("SELECT i.*, (SELECT full_name FROM employees WHERE id=i.assignee_id) as assignee_name, "
               "(SELECT full_name FROM employees WHERE id=i.reporter_id) as reporter_name "
               "FROM jira_issues i WHERE i.issue_key=?", (issue_key,), one=True)
    if not issue: return {}
    issue["subtasks"] = get_issues({"parent_key": issue_key})
    issue["comments"] = _q("SELECT c.*, (SELECT full_name FROM employees WHERE id=c.author_id) as author_name "
                            "FROM jira_comments c WHERE c.issue_key=? ORDER BY c.created_at", (issue_key,))
    return issue

def get_my_issues(person_name: str) -> dict:
    """Get all issues for a person — assigned, reported, grouped by type."""
    assigned  = get_issues({"assignee_name": person_name})
    all_issues = assigned
    return {
        "person": person_name,
        "total":  len(all_issues),
        "by_status": _group(all_issues, "status"),
        "by_type":   _group(all_issues, "issue_type"),
        "issues":    all_issues,
        "open":      [x for x in all_issues if x["status"] not in ("DONE","CLOSED","RESOLVED")],
        "critical":  [x for x in all_issues if x["priority"] in ("CRITICAL","HIGH") and x["status"] not in ("DONE","CLOSED")],
    }

def get_sprint_board(sprint: str = "Sprint 42") -> dict:
    issues = get_issues({"sprint": sprint})
    return {"sprint": sprint, "total": len(issues),
            "by_status": _group(issues, "status"), "issues": issues}

def _group(items, key):
    g = {}
    for i in items:
        v = i.get(key, "Unknown")
        g[v] = g.get(v, 0) + 1
    return g

# ── Create Operations ─────────────────────────────────────────────────────────

def create_issue(
    title: str, issue_type: str = "Story", project_key: str = "ACME",
    description: str = "", priority: str = "MEDIUM",
    assignee_name: str = None, reporter_name: str = None,
    parent_key: str = None, story_points: int = None,
    sprint: str = "Sprint 43", labels: str = "", due_date: str = None
) -> dict:
    """Create a new Jira issue and return the created issue."""
    # Find assignee/reporter by name
    assignee_id = _find_emp(assignee_name)
    reporter_id = _find_emp(reporter_name)

    # Generate next issue key
    count = _q(f"SELECT COUNT(*) as c FROM jira_issues WHERE project_key=?", (project_key,), one=True)["c"]
    next_num = 100 + count + 1
    issue_key = f"{project_key}-{next_num}"

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    today = datetime.now().strftime("%Y-%m-%d")

    _exec("""INSERT INTO jira_issues 
             (issue_key, project_key, issue_type, title, description, status, priority,
              assignee_id, reporter_id, parent_key, sprint, story_points,
              created_date, updated_date, due_date, labels, epic_key)
             VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
          (issue_key, project_key, issue_type, title, description, "OPEN", priority,
           assignee_id, reporter_id, parent_key, sprint, story_points,
           now, now, due_date or today, labels, parent_key or ""))

    return get_issue_detail(issue_key)

def update_issue_status(issue_key: str, new_status: str) -> bool:
    valid = ["OPEN","TODO","IN PROGRESS","IN REVIEW","DONE","CLOSED","RESOLVED","BLOCKED"]
    if new_status.upper() not in valid: return False
    _exec("UPDATE jira_issues SET status=?, updated_date=? WHERE issue_key=?",
          (new_status.upper(), datetime.now().strftime("%Y-%m-%d %H:%M"), issue_key))
    return True

def add_comment(issue_key: str, body: str, author_name: str = None) -> dict:
    author_id = _find_emp(author_name)
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    _exec("INSERT INTO jira_comments (issue_key, author_id, body, created_at) VALUES (?,?,?,?)",
          (issue_key, author_id, body, now))
    return {"issue_key": issue_key, "body": body, "author": author_name or "SuperBot", "created_at": now}

def _find_emp(name: str):
    if not name: return None
    r = _q("SELECT id FROM employees WHERE LOWER(full_name) LIKE ?", (f"%{name.lower()}%",), one=True)
    return r["id"] if r else None

def get_projects() -> list:
    return _q("SELECT * FROM jira_projects")

def get_summary() -> dict:
    total    = _q("SELECT COUNT(*) as c FROM jira_issues", one=True)["c"]
    open_c   = _q("SELECT COUNT(*) as c FROM jira_issues WHERE status NOT IN ('DONE','CLOSED','RESOLVED')", one=True)["c"]
    bugs     = _q("SELECT COUNT(*) as c FROM jira_issues WHERE issue_type='Bug' AND status NOT IN ('DONE','CLOSED')", one=True)["c"]
    critical = _q("SELECT COUNT(*) as c FROM jira_issues WHERE priority='CRITICAL' AND status NOT IN ('DONE','CLOSED','RESOLVED')", one=True)["c"]
    return {"total": total, "open": open_c, "bugs": bugs, "critical": critical}
