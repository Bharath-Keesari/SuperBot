"""SuperBot Orchestrator — central pipeline for all modules."""
import os, sys, re
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.intent_router import route, LABELS
from backend import llm_handler as llm
from backend import rag_handler as rag

def _db():
    from backend import jira_handler, hr_handler, data_handler
    return jira_handler, hr_handler, data_handler

def process(query: str, chat_history: list = None, user_context: dict = None) -> dict:
    r   = route(query)
    j, h, d = _db()
    intent = r.intent
    ex     = r.extracted
    q      = query.lower()
    ans    = ""
    data   = None
    rag_docs = []

    # ── JIRA VIEW ─────────────────────────────────────────────────────────────
    if intent == "JIRA_VIEW":
        if ex.get("issue_key"):
            issue = j.get_issue_detail(ex["issue_key"])
            if issue:
                data = issue
                ans  = _fmt_issue(issue)
            else:
                ans = f"❌ Issue **{ex['issue_key']}** not found."
        elif "my" in q or (user_context and "name" in user_context):
            person = user_context.get("name","") if user_context else ""
            for name in ["priya","arjun","kavya","ravi","vikram","mohan","deepa","rahul","anita","kiran","sunita"]:
                if name in q: person = name; break
            result = j.get_my_issues(person)
            data   = result
            ans    = _fmt_my_issues(result)
        elif ex.get("person"):
            result = j.get_my_issues(ex["person"])
            data   = result; ans = _fmt_my_issues(result)
        elif ex.get("sprint"):
            result = j.get_sprint_board(ex["sprint"])
            data   = result; ans = _fmt_sprint(result)
        else:
            filters = {k: ex.get(k) for k in ["status","issue_type","project","priority","keyword"] if ex.get(k)}
            issues = j.get_issues(filters)
            data   = {"issues": issues, "count": len(issues), "filters": filters}
            ans    = _fmt_issue_list(issues, f"Issues matching your query ({len(issues)} found)")

    # ── JIRA CREATE ───────────────────────────────────────────────────────────
    elif intent == "JIRA_CREATE":
        # Use LLM to extract structured fields from natural language
        extract_prompt = f"""Extract Jira issue details from this request. Return ONLY a JSON object with these keys:
title, issue_type (Story/Task/Bug/Subtask/Epic), project_key (ACME/DATA/BI/INFRA/HR), 
description, priority (LOW/MEDIUM/HIGH/CRITICAL), assignee_name, story_points (number or null).
Request: "{query}"
JSON:"""
        import json
        raw = llm.call_llm(extract_prompt, system_override="Extract JSON only. No explanation.")
        try:
            clean = re.sub(r'```json|```','', raw).strip()
            fields = json.loads(clean)
        except:
            fields = {"title": query, "issue_type": ex.get("issue_type","Story").title(),
                      "project_key": ex.get("project","ACME"), "description": "", "priority": ex.get("priority","MEDIUM")}
        
        created = j.create_issue(
            title        = fields.get("title", query[:100]),
            issue_type   = fields.get("issue_type","Story"),
            project_key  = fields.get("project_key","ACME"),
            description  = fields.get("description",""),
            priority     = fields.get("priority","MEDIUM"),
            assignee_name= fields.get("assignee_name"),
            story_points = fields.get("story_points"),
        )
        data = created
        key  = created.get("issue_key","?")
        ans  = (f"✅ **Jira issue created!**\n\n"
                f"**{key}** — {created.get('title','')}\n"
                f"- **Type:** {created.get('issue_type','')} | **Priority:** {created.get('priority','')} | **Status:** {created.get('status','OPEN')}\n"
                f"- **Assignee:** {created.get('assignee_name','Unassigned')}\n"
                f"- **Project:** {created.get('project_key','')}\n\n"
                f"_Issue is now in the backlog. You can update status anytime._")

    # ── JIRA UPDATE ───────────────────────────────────────────────────────────
    elif intent == "JIRA_UPDATE":
        if ex.get("issue_key") and ex.get("status"):
            ok = j.update_issue_status(ex["issue_key"], ex["status"])
            ans = (f"✅ **{ex['issue_key']}** status updated to **{ex['status']}**" if ok
                   else f"❌ Could not update {ex['issue_key']}. Valid statuses: OPEN, IN PROGRESS, IN REVIEW, DONE, CLOSED.")
        elif "comment" in q and ex.get("issue_key"):
            comment_text = re.sub(r'add comment (to|on) [A-Z]+-\d+', '', query, flags=re.I).strip() or query
            result = j.add_comment(ex["issue_key"], comment_text)
            ans = f"✅ Comment added to **{ex['issue_key']}**."
        else:
            ans = ("Please specify the issue key and new status.\n\nExample: _Update ACME-102 to IN REVIEW_\n"
                   "Or: _Mark DATA-203 as DONE_")

    # ── HR POLICY ─────────────────────────────────────────────────────────────
    elif intent == "HR_POLICY":
        rag_docs = rag.retrieve(query, source_filter=None)
        ctx = rag.format_context(rag_docs)
        if rag_docs:
            ans = llm.call_llm(query, ctx, chat_history,
                               system_override=f"You are an HR policy expert. Answer based ONLY on the provided policy documents. "
                                               f"Quote exact policies with numbers/days when available. Be precise.")
        else:
            ans = llm.call_llm(query, "", chat_history)

    # ── HR LEAVE ──────────────────────────────────────────────────────────────
    elif intent == "HR_LEAVE":
        if any(w in q for w in ["apply","request","take","need","want"]):
            # Extract leave details and guide user
            rag_docs = rag.retrieve("leave application policy rules", source_filter=None)
            ctx = rag.format_context(rag_docs)
            ans = llm.call_llm(
                f"Employee wants to apply for leave. Query: {query}\n"
                "Explain the process, required fields, and any relevant policy rules. "
                "Ask for missing info (leave type, dates) if not provided.",
                ctx, chat_history)
        elif any(w in q for w in ["balance","remaining","how many","available","left"]):
            # Show leave balance for current user or mentioned person
            person = ex.get("person","EMP002")
            emp = h.search_employees(name=person)
            if emp:
                balances = h.get_leave_balance(emp[0]["emp_id"])
                data = balances
                ans  = _fmt_leave_balance(emp[0]["full_name"], balances)
            else:
                rag_docs = rag.retrieve(query)
                ans = llm.call_llm(query, rag.format_context(rag_docs), chat_history)
        else:
            rag_docs = rag.retrieve(query)
            ans = llm.call_llm(query, rag.format_context(rag_docs), chat_history)

    # ── HR EMPLOYEE ───────────────────────────────────────────────────────────
    elif intent == "HR_EMPLOYEE":
        if ex.get("person"):
            emp = h.get_employee(ex["person"])
            data = emp
            ans  = _fmt_employee(emp) if emp else f"❌ No employee found matching **{ex['person']}**."
        else:
            depts = h.get_departments()
            data  = depts
            ans   = "### 👥 Department Directory\n\n" + "\n".join(
                f"- **{d['department']}** — {d['headcount']} employees" for d in depts)

    # ── IT HELPDESK ───────────────────────────────────────────────────────────
    elif intent == "HELPDESK":
        if any(w in q for w in ["create","raise","log","open","new","submit"]):
            # Extract ticket info with LLM
            ctx_prompt = f"Extract IT helpdesk ticket details from: '{query}'. Return a JSON with: title, description, category (Hardware/Software/Network/Access), priority (LOW/MEDIUM/HIGH/CRITICAL). JSON only."
            import json
            raw = llm.call_llm(ctx_prompt, system_override="Return JSON only.")
            try:
                fields = json.loads(re.sub(r'```json|```','',raw).strip())
            except:
                fields = {"title": query[:80], "description": query, "category": "General", "priority": "MEDIUM"}
            result = h.create_helpdesk_ticket(
                fields.get("title", query[:80]), fields.get("description", query),
                fields.get("category","General"), fields.get("priority","MEDIUM"),
                user_context.get("name","Employee") if user_context else "Employee"
            )
            data = result; ans = result["message"]
        else:
            tickets = h.get_helpdesk_tickets()
            data    = {"tickets": tickets}
            ans     = _fmt_tickets(tickets)

    # ── DATA / SQL ────────────────────────────────────────────────────────────
    elif intent in ("DATA_SQL","DATA_COLUMN","DATA_SCHEMA","DATA_PIPELINE"):
        if intent == "DATA_COLUMN":
            # Extract full column name (supports quoted names like "Lease Cost")
            import re

            # 1️⃣ First priority: quoted column name
            match = re.search(r'"([^"]+)"', query)

            if match:
                col = match.group(1)
            else:
                # 2️⃣ Fallback to router extraction
                col = ex.get("column") or query.split()[-1].strip("?.,")
        
            col = col.strip()
            schema = ex.get("schema")

            data = d.find_tables_by_column(col, schema)

            if not data or data.get("count", 0) == 0:
                ans = (
                    f"❌ No tables found with column matching **`{col}`**.\n\n"
                    "Tip: Try a partial name like `customer` instead of `customer_id`."
                )
            else:
                lines = [f"### 🔍 Column → Table Finder\n"]
                lines.append(f"✅ Found **{data['count']} occurrence(s)** of `{col}`:\n")

                for r in data.get("results", []):
                    schema_name = r.get("TABLE_SCHEMA") or r.get("table_schema") or ""
                    table_name = r.get("TABLE_NAME") or r.get("table_name") or ""
                    column_name = r.get("COLUMN_NAME") or r.get("column_name") or ""
                    data_type = r.get("DATA_TYPE") or r.get("data_type") or "UNKNOWN"

                    full_table = f"{schema_name}.{table_name}" if schema_name else table_name

                    lines.append(
                        f"- **`{full_table}`** → `{column_name}` ({data_type})"
                    )

                ans = "\n".join(lines)

        elif intent == "DATA_SCHEMA":
            table  = ex.get("table")
            schema = ex.get("schema")
            if table:
                data = d.get_table_schema(table, schema)
                sql_used = f"SELECT columns WHERE TABLE_NAME='{table}'"

                if not data or data.get("column_count", 0) == 0:
                    answer = f"❌ Table **`{table}`** not found."
                else:
                    lines = [f"### 📋 Schema: `{table}`\n"]
                    lines.append(f"**Total Columns:** {data['column_count']}\n")

                    for col in data.get("columns", []):
                        col_name = col.get("COLUMN_NAME") or col.get("column_name", "")
                        col_type = col.get("DATA_TYPE") or col.get("data_type", "")
                        lines.append(f"- `{col_name}` ({col_type})")

                    answer = "\n".join(lines)
            else:
                data = d.list_all_tables(schema)
                sql_used = "SELECT * FROM information_schema_tables"
                lines = [f"### 📋 All Tables ({data['count']} total)\n"]
                cur_schema = None
                for t in data.get("tables", []):
                    s = t.get("TABLE_SCHEMA") or t.get("table_schema","")
                    n = t.get("TABLE_NAME")   or t.get("table_name","")
                    rc= t.get("ROW_COUNT")    or t.get("row_count", 0) or 0
                    sz= t.get("SIZE_MB")      or t.get("size_mb", 0)   or 0
                    if s != cur_schema:
                        cur_schema = s
                        lines.append(f"\n**Schema: {s}**")
                    lines.append(f"- `{n}` — {int(rc):,} rows, {sz} MB")
                answer = "\n".join(lines)

        elif intent == "DATA_SQL":
            table = ex.get("table","fact_orders")
            schema_data = d.get_table_schema(table)
            schema_str  = "\n".join(f"  {c['column_name']} {c['data_type']}" for c in schema_data.get("columns",[]))
            sql_code = llm.generate_sql(f"Table: {table}\nColumns:\n{schema_str}", query)
            data = {"sql": sql_code}
            ans  = f"### ⚡ Generated SQL\n\n```sql\n{sql_code}\n```"
        elif intent == "DATA_PIPELINE":
            data = d.get_pipeline_status()
            ans  = _fmt_pipelines(data)

    # ── ANNOUNCEMENTS ─────────────────────────────────────────────────────────
    elif intent == "ANNOUNCE":
        items = h.get_announcements()
        data  = items
        ans   = _fmt_announcements(items)

    # ── EXPENSES ──────────────────────────────────────────────────────────────
    elif intent == "EXPENSE":
        items = h.get_expenses()
        data  = items
        ans   = "### 💰 Recent Expense Reports\n\n" + "\n".join(
            f"- **{e['full_name']}** — ₹{e['amount']:,.0f} ({e['category']}) — _{e['status']}_" for e in items[:10])

    # ── GENERAL / AI ──────────────────────────────────────────────────────────
    else:
        rag_docs = rag.retrieve(query)
        ctx = rag.format_context(rag_docs)
        ans = llm.call_llm(query, ctx, chat_history)

    return {
        "intent":       intent,
        "module":       r.module,
        "label":        LABELS.get(intent, "🧠 AI"),
        "confidence":   r.confidence,
        "answer":       ans or "I couldn't process that request. Please try rephrasing.",
        "data":         data,
        "rag_docs":     rag_docs,
    }

# ── Formatters ────────────────────────────────────────────────────────────────

def _fmt_issue(i: dict) -> str:
    st_icons = {"DONE":"✅","IN PROGRESS":"🔧","OPEN":"📬","TODO":"📋","BLOCKED":"🚫","IN REVIEW":"👁️"}
    pri_icons = {"CRITICAL":"🔴","HIGH":"🟠","MEDIUM":"🟡","LOW":"🟢"}
    si = st_icons.get(i.get("status",""),"❓")
    pi = pri_icons.get(i.get("priority",""),"⚪")
    lines = [f"## {si} {i.get('issue_key')} — {i.get('title','')}",
             f"**Type:** {i.get('issue_type','')} | **Status:** {i.get('status','')} | {pi} **Priority:** {i.get('priority','')}",
             f"**Assignee:** {i.get('assignee_name','Unassigned')} | **Reporter:** {i.get('reporter_name','?')}",
             f"**Sprint:** {i.get('sprint','?')} | **Story Points:** {i.get('story_points','?')} | **Due:** {i.get('due_date','?')}"]
    if i.get("description"):
        lines.append(f"\n**Description:**\n{i['description'][:300]}")
    subs = i.get("subtasks", [])
    if subs:
        lines.append(f"\n**Subtasks ({len(subs)}):**")
        for s in subs:
            lines.append(f"- [{s.get('status','')}] `{s.get('issue_key','')}` — {s.get('title','')[:60]}")
    comments = i.get("comments", [])
    if comments:
        lines.append(f"\n**Latest Comment:**")
        c = comments[-1]
        lines.append(f"> {c.get('author_name','?')} ({c.get('created_at','')[:10]}): {c.get('body','')[:150]}")
    return "\n".join(lines)

def _fmt_my_issues(r: dict) -> str:
    person = r.get("person","").title()
    lines = [f"### 🎫 Issues for {person} ({r['total']} total)\n"]
    bs = r.get("by_status", {})
    lines.append("**By Status:** " + "  ".join(f"{k}: **{v}**" for k,v in bs.items()))
    open_issues = r.get("open", [])
    if open_issues:
        lines.append(f"\n**Open Issues ({len(open_issues)}):**")
        for i in open_issues[:8]:
            pi = {"CRITICAL":"🔴","HIGH":"🟠","MEDIUM":"🟡","LOW":"🟢"}.get(i.get("priority",""),"⚪")
            lines.append(f"{pi} `{i.get('issue_key','')}` — {i.get('title','')[:60]} _{i.get('status','')}_")
    return "\n".join(lines)

def _fmt_sprint(r: dict) -> str:
    lines = [f"### 🏃 {r['sprint']} Board ({r['total']} issues)\n"]
    for status, count in r.get("by_status",{}).items():
        bar = "█" * min(count, 10)
        lines.append(f"**{status}** {bar} {count}")
    lines.append("\n**Issues:**")
    for i in r.get("issues",[])[:10]:
        lines.append(f"- `{i.get('issue_key','')}` {i.get('title','')[:55]} — {i.get('assignee_name','?')}")
    return "\n".join(lines)

def _fmt_issue_list(issues: list, title: str) -> str:
    if not issues: return "No issues found matching your criteria."
    lines = [f"### {title}\n"]
    for i in issues[:10]:
        pi = {"CRITICAL":"🔴","HIGH":"🟠","MEDIUM":"🟡","LOW":"🟢"}.get(i.get("priority",""),"⚪")
        si = {"DONE":"✅","IN PROGRESS":"🔧","OPEN":"📬","TODO":"📋"}.get(i.get("status",""),"❓")
        lines.append(f"{si} {pi} `{i.get('issue_key','')}` — **{i.get('title','')[:55]}** — {i.get('assignee_name','?')}")
    if len(issues) > 10: lines.append(f"\n_...and {len(issues)-10} more_")
    return "\n".join(lines)

def _fmt_employee(e: dict) -> str:
    lines = [f"### 👤 {e.get('full_name','')}",
             f"**{e.get('job_title','')}** · {e.get('department','')}",
             f"📧 {e.get('email','')} | 📱 {e.get('phone','')} | 💬 {e.get('slack_handle','')}",
             f"📍 {e.get('location','')} | 🗓️ Joined: {e.get('join_date','')}"]
    if e.get("manager_name"):
        lines.append(f"**Reports to:** {e['manager_name']}")
    dr = e.get("direct_reports",[])
    if dr:
        lines.append(f"**Direct Reports ({len(dr)}):** " + ", ".join(x["full_name"] for x in dr))
    balances = e.get("leave_balances",[])
    if balances:
        lines.append("\n**Leave Balances:**")
        for b in balances:
            lines.append(f"- {b['leave_type']}: **{b['remaining']}** days remaining ({b['used']}/{b['allocated']} used)")
    return "\n".join(lines)

def _fmt_leave_balance(name: str, balances: list) -> str:
    lines = [f"### 🏖️ Leave Balance — {name}\n"]
    for b in balances:
        pct = int((b["used"]/b["allocated"]*100)) if b["allocated"] else 0
        bar = "█" * (pct//10) + "░" * (10 - pct//10)
        lines.append(f"**{b['leave_type']}:** {b['remaining']} days remaining  `{bar}` {pct}% used")
    return "\n".join(lines)

def _fmt_tickets(tickets: list) -> str:
    lines = ["### 🖥️ IT Helpdesk Tickets\n"]
    for t in tickets[:8]:
        si = {"RESOLVED":"✅","IN PROGRESS":"🔧","OPEN":"📬"}.get(t.get("status",""),"❓")
        pi = {"CRITICAL":"🔴","HIGH":"🟠","MEDIUM":"🟡","LOW":"🟢"}.get(t.get("priority",""),"⚪")
        lines.append(f"{si} {pi} **{t.get('ticket_id','')}** — {t.get('title','')[:60]}")
        lines.append(f"   👤 {t.get('raised_by','')} | 📅 {t.get('created_date','')}")
    return "\n".join(lines)

def _fmt_columns(d: dict) -> str:
    if not d["count"]: return f"No columns found matching **{d['column']}**."
    lines = [f"### 🔍 Found `{d['column']}` in {d['count']} location(s)\n"]
    for r in d["results"]:
        lines.append(f"- **`{r['table_schema']}.{r['table_name']}`** → `{r['column_name']}` ({r['data_type']})")
    return "\n".join(lines)

def _fmt_schema(d: dict) -> str:
    m = d.get("metadata",{}); t = d.get("table","")
    lines = [f"### 📊 Schema: `{t}`",
             f"**{int(m.get('row_count',0) or 0):,} rows** | {m.get('size_mb',0)} MB | Owner: {m.get('owner_team','?')}\n",
             "| Column | Type | Nullable |", "|--------|------|----------|"]
    for c in d.get("columns",[]):
        lines.append(f"| `{c['column_name']}` | {c['data_type']} | {c['is_nullable']} |")
    return "\n".join(lines)

def _fmt_pipelines(d: dict) -> str:
    lines = ["### 🔄 ETL Pipeline Status\n"]
    for r in d.get("runs",[]):
        si = {"SUCCESS":"✅","FAILED":"❌","RUNNING":"🔄"}.get(r.get("status",""),"❓")
        lines.append(f"{si} **{r['pipeline_name']}** — {r['status']}")
        if r.get("error_message"):
            lines.append(f"   ⚠️ `{r['error_message']}`")
    return "\n".join(lines)

def _fmt_announcements(items: list) -> str:
    lines = ["### 📣 Company Announcements\n"]
    for a in items[:5]:
        pin = "📌 " if a.get("pinned") else ""
        lines.append(f"{pin}**{a['title']}**")
        lines.append(f"{a['body'][:180]}...")
        lines.append(f"_Posted by {a['author']} · {a['posted_date']}_\n")
    return "\n".join(lines)
