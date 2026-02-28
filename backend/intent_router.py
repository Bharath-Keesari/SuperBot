"""
SuperBot Intent Router — classifies every query into one of 14 intents.
Pure regex, zero LLM cost, <1ms latency.
"""
import re
from dataclasses import dataclass, field

@dataclass
class Route:
    intent: str
    module: str       # jira | hr | data | helpdesk | general
    confidence: str
    extracted: dict = field(default_factory=dict)
    raw_query: str = ""

# ── Pattern Groups ────────────────────────────────────────────────────────────
_JIRA_VIEW = [
    r"\b(show|list|get|find|what)\b.*(ticket|issue|story|task|subtask|bug|epic)",
    r"\b(my|assigned|sprint|backlog)\b.*(ticket|issue|task|story|jira)",
    r"\bjira\b.*(status|update|progress)",
    r"\b(open|closed|done|in progress)\b.*(ticket|issue|story|bug)",
    r"\b[A-Z]{2,6}-\d+\b",
    r"\bsprint\b.*(board|status|ticket|story)",
    r"\bwhat.*(assigned|working on)\b",
    r"\b(ticket|issue|story|task|bug)\b.*(priya|arjun|kavya|ravi|vikram|mohan|deepa|rahul|anita|kiran)",
]
_JIRA_CREATE = [
    r"\b(create|add|new|raise|open|log)\b.*(ticket|issue|story|task|subtask|bug|epic)",
    r"\b(create|make|write)\b.*\bjira\b",
    r"\bneed.*(ticket|story|task|jira)",
    r"\b(raise|log)\b.*(bug|issue|story)",
]
_JIRA_UPDATE = [
    r"\b(update|change|move|set|mark|close|resolve|assign)\b.*(ticket|issue|story|task|status)",
    r"\b(mark|move)\b.*\b(done|complete|closed|resolved|progress|review)\b",
    r"\bassign\b.*\b(ticket|issue|task)\b",
    r"\badd comment\b",
]
_HR_POLICY = [
    r"\b(policy|policies|rule|guideline|handbook)\b",
    r"\b(leave|pto|vacation|sick|maternity|paternity|wfh|work from home)\b.*(policy|rule|allow|entitle|day|week)",
    r"\bhow many\b.*(leave|day|vacation|sick)\b",
    r"\b(can i|am i allowed|is it allowed|eligible)\b",
    r"\b(notice period|probation|nda|code of conduct|ethics|harassment)\b",
    r"\b(reimburs|expense|claim|allowance)\b.*(policy|rule|limit|max)",
    r"\b(salary|ctc|benefits|pf|provident|gratuity|esop|insurance)\b.*(policy|structure|detail|how)",
    r"\b(onboard|joining|new hire|induction)\b",
    r"\bperformance review\b",
]
_HR_LEAVE = [
    r"\b(apply|request|take|need|want)\b.*(leave|day off|vacation|pto|sick)",
    r"\b(leave|balance|remaining|available|how many)\b.*(day|count|check|leave|pto|vacation)",
    r"\bhow many.*(leave|day|vacation|pto)\b",
    r"\bmy leave\b",
    r"\b(approve|reject)\b.*leave",
    r"\boff\b.*(tomorrow|monday|friday|next week|this week)",
    r"\bleave balance\b",
]
_HR_EMPLOYEE = [
    r"\bwho is\b",
    r"\bcontact for\b",
    r"\b(who is|find|search|look up|contact)\b.*(employee|person|staff|team member)",
    r"\b(email|phone|slack|contact)\b.*(priya|arjun|kavya|ravi|vikram|mohan|deepa|rahul|anita|kiran)",
    r"\bwho.*(reports to|works in|team|department)\b",
    r"\borg chart\b",
    r"\bheadcount\b",
    r"\bdirectory\b",
]
_HELPDESK = [
    r"\bit ticket\b",
    r"\braise.*ticket\b",
    r"\b(raise|create|log|open)\b.*(it|helpdesk|support|ticket)\b",
    r"\b(laptop|computer|vpn|access|password|software|hardware|wifi|wi-fi|internet)\b.*(issue|problem|not working|broken|slow|error)",
    r"\bit helpdesk\b",
    r"\bcan.*(install|access|get)\b.*\b(software|tool|license|vpn)\b",
    r"\b(my ticket|support request|it request)\b",
]
_DATA_COLUMN = [r"\bwhich table.*(column|field)\b", r"\bfind.*column\b", r"\bwhere is.*column\b"]
_DATA_SCHEMA = [r"\bschema\b", r"\bcolumns of\b", r"\bdescribe.*table\b", r"\blist.*table\b"]
_DATA_SQL    = [r"\bwrite.*sql\b", r"\bgenerate.*query\b", r"\bsql.*for\b", r"\bselect.*from\b"]
_DATA_PIPE   = [r"\bpipeline\b", r"\betl\b", r"\bdata.*fail\b", r"\bpipeline.*status\b"]
_ANNOUNCE    = [r"\bannouncement\b", r"\bnews\b", r"\bnotice\b", r"\bupdate\b.*company", r"\bwhat.*(new|happening)\b"]
_EXPENSE     = [r"\b(my expense|claim|reimburs|submit.*expense)\b", r"\bexpense.*status\b"]

PATTERNS = [
    ("JIRA_CREATE",   "jira",     _JIRA_CREATE),
    ("JIRA_UPDATE",   "jira",     _JIRA_UPDATE),
    ("JIRA_VIEW",     "jira",     _JIRA_VIEW),
    ("HR_LEAVE",      "hr",       _HR_LEAVE),
    ("HR_POLICY",     "hr",       _HR_POLICY),
    ("HR_EMPLOYEE",   "hr",       _HR_EMPLOYEE),
    ("HELPDESK",      "helpdesk", _HELPDESK),
    ("DATA_SQL",      "data",     _DATA_SQL),
    ("DATA_COLUMN",   "data",     _DATA_COLUMN),
    ("DATA_SCHEMA",   "data",     _DATA_SCHEMA),
    ("DATA_PIPELINE", "data",     _DATA_PIPE),
    ("ANNOUNCE",      "hr",       _ANNOUNCE),
    ("EXPENSE",       "hr",       _EXPENSE),
]

KNOWN_PEOPLE = ["priya","arjun","kavya","ravi","vikram","mohan","deepa","rahul","anita","kiran","sunita","neha"]
KNOWN_PROJECTS = ["acme","data","bi","infra","hr"]
ISSUE_KEY_RE = re.compile(r'\b([A-Z]{2,6}-\d+)\b')
JIRA_STATUSES = ["open","todo","in progress","done","closed","resolved","blocked","in review"]
PRIORITIES = ["critical","high","medium","low"]
ISSUE_TYPES = ["story","task","subtask","bug","epic","issue"]

def _extract(query: str) -> dict:
    q = query.lower()
    ex = {}
    # Issue key
    m = ISSUE_KEY_RE.search(query)
    if m: ex["issue_key"] = m.group(1)
    # Person name
    for p in KNOWN_PEOPLE:
        if p in q: ex["person"] = p; break
    # Project
    for p in KNOWN_PROJECTS:
        if p in q: ex["project"] = p.upper(); break
    # Status
    for s in JIRA_STATUSES:
        if s in q: ex["status"] = s.upper(); break
    # Priority
    for p in PRIORITIES:
        if p in q: ex["priority"] = p.upper(); break
    # Issue type
    for t in ISSUE_TYPES:
        if t in q: ex["issue_type"] = t.upper(); break
    # Sprint
    sm = re.search(r'sprint\s*(\d+)', q)
    if sm: ex["sprint"] = f"Sprint {sm.group(1)}"
    # Table/column names
    tm = re.search(r'table[s]?\s+[`"]?(\w+)[`"]?', q)
    if tm: ex["table"] = tm.group(1)
    cm = re.search(r'column[s]?\s+[`"]?(\w+)[`"]?', q)
    if cm: ex["column"] = cm.group(1)
    # Keyword (first meaningful noun for Jira search)
    words = [w.strip(".,?!\"'") for w in q.split() if len(w) > 4 and w not in
             ("which","where","what","there","their","about","would","could","should","those","these","have","show","list","find","create","update","please","thanks")]
    if words: ex["keyword"] = words[0]
    return ex

def route(query: str) -> Route:
    q = query.lower().strip()
    scores = {}
    for intent, module, patterns in PATTERNS:
        hits = sum(1 for p in patterns if re.search(p, q))
        if hits: scores[intent] = (hits, module)
    if not scores:
        return Route("GENERAL", "general", "low", _extract(query), query)
    best = max(scores, key=lambda k: scores[k][0])
    conf = "high" if scores[best][0] >= 2 else "medium"
    return Route(best, scores[best][1], conf, _extract(query), query)

LABELS = {
    "JIRA_VIEW":     "🎫 Jira Tracker",
    "JIRA_CREATE":   "✏️ Create Issue",
    "JIRA_UPDATE":   "🔄 Update Issue",
    "HR_POLICY":     "📋 HR Policy",
    "HR_LEAVE":      "🏖️ Leave Management",
    "HR_EMPLOYEE":   "👤 Employee Directory",
    "HELPDESK":      "🖥️ IT Helpdesk",
    "DATA_SQL":      "⚡ SQL Generator",
    "DATA_COLUMN":   "🔍 Column Finder",
    "DATA_SCHEMA":   "📊 Schema Explorer",
    "DATA_PIPELINE": "🔄 Pipeline Monitor",
    "ANNOUNCE":      "📣 Announcements",
    "EXPENSE":       "💰 Expenses",
    "GENERAL":       "🧠 AI Assistant",
}
