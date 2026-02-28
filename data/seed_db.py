"""Seed the SuperBot SQLite database with all mock data."""
import os, sys, sqlite3
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

DB_PATH = os.path.join(os.path.dirname(__file__), "superbot.db")

SCHEMA = """
-- Employees
CREATE TABLE IF NOT EXISTS employees (
    id INTEGER PRIMARY KEY, emp_id TEXT UNIQUE, full_name TEXT, email TEXT,
    department TEXT, job_title TEXT, manager_id INTEGER, location TEXT,
    phone TEXT, slack_handle TEXT, join_date TEXT, status TEXT DEFAULT 'active',
    avatar_initials TEXT
);

-- Jira Projects
CREATE TABLE IF NOT EXISTS jira_projects (
    id INTEGER PRIMARY KEY, key TEXT UNIQUE, name TEXT, lead TEXT, status TEXT
);

-- Jira Issues (Stories, Tasks, Subtasks, Bugs, Epics)
CREATE TABLE IF NOT EXISTS jira_issues (
    id INTEGER PRIMARY KEY, issue_key TEXT UNIQUE, project_key TEXT,
    issue_type TEXT, title TEXT, description TEXT, status TEXT,
    priority TEXT, assignee_id INTEGER, reporter_id INTEGER,
    parent_key TEXT, sprint TEXT, story_points INTEGER,
    created_date TEXT, updated_date TEXT, due_date TEXT,
    labels TEXT, epic_key TEXT
);

-- Jira Comments
CREATE TABLE IF NOT EXISTS jira_comments (
    id INTEGER PRIMARY KEY, issue_key TEXT, author_id INTEGER,
    body TEXT, created_at TEXT
);

-- Leave requests
CREATE TABLE IF NOT EXISTS leave_requests (
    id INTEGER PRIMARY KEY, emp_id TEXT, leave_type TEXT,
    start_date TEXT, end_date TEXT, days INTEGER,
    status TEXT, reason TEXT, applied_date TEXT, approved_by TEXT
);

-- Leave balances
CREATE TABLE IF NOT EXISTS leave_balances (
    id INTEGER PRIMARY KEY, emp_id TEXT, leave_type TEXT,
    allocated INTEGER, used INTEGER, remaining INTEGER, year INTEGER
);

-- IT Helpdesk tickets
CREATE TABLE IF NOT EXISTS helpdesk_tickets (
    id INTEGER PRIMARY KEY, ticket_id TEXT UNIQUE, title TEXT,
    description TEXT, category TEXT, priority TEXT, status TEXT,
    raised_by TEXT, assigned_to TEXT, created_date TEXT,
    resolved_date TEXT, resolution TEXT
);

-- Announcements
CREATE TABLE IF NOT EXISTS announcements (
    id INTEGER PRIMARY KEY, title TEXT, body TEXT, category TEXT,
    author TEXT, posted_date TEXT, pinned INTEGER DEFAULT 0, audience TEXT
);

-- Data warehouse tables (for analytics module)
CREATE TABLE IF NOT EXISTS dw_tables (
    id INTEGER PRIMARY KEY, table_schema TEXT, table_name TEXT,
    table_type TEXT, row_count INTEGER, size_mb REAL,
    owner_team TEXT, created_date TEXT, last_modified TEXT
);
CREATE TABLE IF NOT EXISTS dw_columns (
    id INTEGER PRIMARY KEY, table_schema TEXT, table_name TEXT,
    column_name TEXT, data_type TEXT, is_nullable TEXT, ordinal_position INTEGER
);
CREATE TABLE IF NOT EXISTS data_lineage (
    id INTEGER PRIMARY KEY, source_schema TEXT, source_table TEXT,
    target_schema TEXT, target_table TEXT, pipeline_name TEXT, transformation TEXT
);
CREATE TABLE IF NOT EXISTS pipeline_runs (
    id INTEGER PRIMARY KEY, pipeline_name TEXT, status TEXT,
    start_time TEXT, end_time TEXT, rows_processed INTEGER, error_message TEXT
);
CREATE TABLE IF NOT EXISTS data_quality_checks (
    id INTEGER PRIMARY KEY, table_schema TEXT, table_name TEXT,
    column_name TEXT, check_type TEXT, check_status TEXT,
    null_count INTEGER, distinct_count INTEGER
);

-- Expense reports
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY, emp_id TEXT, category TEXT, amount REAL,
    currency TEXT, description TEXT, date TEXT, status TEXT, approved_by TEXT
);
"""

EMPLOYEES = [
    (1,"EMP001","Ravi Kumar","ravi.kumar@acmecorp.com","Engineering","VP Engineering",None,"Hyderabad","9876543210","@ravi","2019-03-01","active","RK"),
    (2,"EMP002","Priya Sharma","priya.sharma@acmecorp.com","Engineering","Senior Data Engineer",1,"Hyderabad","9876543211","@priya","2020-06-15","active","PS"),
    (3,"EMP003","Arjun Singh","arjun.singh@acmecorp.com","Engineering","Full Stack Developer",1,"Bangalore","9876543212","@arjun","2021-01-10","active","AS"),
    (4,"EMP004","Kavya Menon","kavya.menon@acmecorp.com","Business Intelligence","BI Lead",1,"Hyderabad","9876543213","@kavya","2020-09-01","active","KM"),
    (5,"EMP005","Sunita Rao","sunita.rao@acmecorp.com","Finance","Finance Manager",None,"Mumbai","9876543214","@sunita","2018-11-15","active","SR"),
    (6,"EMP006","Vikram Patel","vikram.patel@acmecorp.com","Engineering","DevOps Engineer",1,"Pune","9876543215","@vikram","2021-07-01","active","VP"),
    (7,"EMP007","Mohan Reddy","mohan.reddy@acmecorp.com","HR","HR Manager",None,"Hyderabad","9876543216","@mohan","2019-01-20","active","MR"),
    (8,"EMP008","Deepa Nair","deepa.nair@acmecorp.com","Engineering","Python Developer",1,"Bangalore","9876543217","@deepa","2022-03-01","active","DN"),
    (9,"EMP009","Rahul Gupta","rahul.gupta@acmecorp.com","Sales","Sales Lead",None,"Delhi","9876543218","@rahul","2020-04-01","active","RG"),
    (10,"EMP010","Anita Joshi","anita.joshi@acmecorp.com","Engineering","QA Engineer",1,"Hyderabad","9876543219","@anita","2022-08-15","active","AJ"),
    (11,"EMP011","Kiran Babu","kiran.babu@acmecorp.com","Engineering","Data Analyst",4,"Hyderabad","9876543220","@kiran","2023-01-05","active","KB"),
    (12,"EMP012","Neha Kapoor","neha.kapoor@acmecorp.com","HR","HR Executive",7,"Mumbai","9876543221","@neha","2023-03-20","active","NK"),
]

JIRA_PROJECTS = [
    (1,"ACME","ACME Platform","Ravi Kumar","active"),
    (2,"DATA","Data Engineering","Priya Sharma","active"),
    (3,"BI","Business Intelligence","Kavya Menon","active"),
    (4,"INFRA","Infrastructure","Vikram Patel","active"),
    (5,"HR","HR Systems","Mohan Reddy","active"),
]

JIRA_ISSUES = [
    (1,"ACME-101","ACME","Epic","Customer Portal v2.0","Full rebuild of customer portal with new design system",
     "IN PROGRESS","HIGH",3,1,None,"Sprint 42",None,"2024-01-15","2024-06-01","2024-07-31","portal,frontend",""),
    (2,"ACME-102","ACME","Story","Implement OAuth2 SSO login","As an employee I want to login with company SSO",
     "IN PROGRESS","HIGH",3,1,"ACME-101","Sprint 42",5,"2024-05-01","2024-06-01","2024-06-30","auth,security","ACME-101"),
    (3,"ACME-103","ACME","Task","Set up Azure AD app registration","Register OAuth app in Azure AD tenant",
     "DONE","HIGH",3,3,"ACME-102","Sprint 42",3,"2024-05-01","2024-05-20","2024-05-25","azure,auth","ACME-101"),
    (4,"ACME-104","ACME","Task","Implement PKCE flow in frontend","Add PKCE auth code flow to React login",
     "IN PROGRESS","HIGH",3,1,"ACME-102","Sprint 42",5,"2024-05-05","2024-06-01","2024-06-15","react,auth","ACME-101"),
    (5,"ACME-105","ACME","Subtask","Write unit tests for auth module","Cover edge cases: expired tokens, refresh flow",
     "TODO","MEDIUM",10,3,"ACME-104","Sprint 43",2,"2024-05-10","2024-05-10","2024-06-20","testing","ACME-101"),
    (6,"ACME-106","ACME","Bug","Login page crashes on Safari 17","TypeError in token parser, affects 23% of users",
     "OPEN","CRITICAL",3,10,"ACME-102","Sprint 42",None,"2024-06-01","2024-06-01","2024-06-05","bug,safari","ACME-101"),
    (7,"ACME-107","ACME","Story","User profile management page","Allow users to update personal info, avatar, preferences",
     "TODO","MEDIUM",8,2,None,"Sprint 43",8,"2024-05-20","2024-05-20","2024-07-15","profile,ui","ACME-101"),
    (8,"DATA-201","DATA","Epic","Real-time Data Pipeline","Build Kafka-based real-time ingestion for sales events",
     "IN PROGRESS","HIGH",2,1,None,"Sprint 42",None,"2024-03-01","2024-06-01","2024-09-30","kafka,pipeline",""),
    (9,"DATA-202","DATA","Story","Design Kafka topic schema","Define Avro schemas for order and customer events",
     "DONE","HIGH",2,2,"DATA-201","Sprint 40",5,"2024-03-15","2024-04-30","2024-04-30","kafka,schema","DATA-201"),
    (10,"DATA-203","DATA","Story","Implement Kafka consumer in Python","Consume events and write to staging Delta Lake",
     "IN PROGRESS","HIGH",2,2,"DATA-201","Sprint 42",13,"2024-04-01","2024-06-01","2024-06-30","kafka,python","DATA-201"),
    (11,"DATA-204","DATA","Task","Set up Kafka cluster on Azure","Deploy 3-node Kafka cluster with monitoring",
     "DONE","HIGH",6,2,"DATA-203","Sprint 41",8,"2024-04-01","2024-05-15","2024-05-15","kafka,azure,infra","DATA-201"),
    (12,"DATA-205","DATA","Bug","Duplicate events in consumer","Exactly-once semantics not working for payment events",
     "OPEN","CRITICAL",2,11,"DATA-203","Sprint 42",None,"2024-06-01","2024-06-01","2024-06-08","bug,kafka","DATA-201"),
    (13,"DATA-206","DATA","Story","dbt transformation models for sales","Build dbt models: staging → intermediate → mart",
     "IN PROGRESS","MEDIUM",11,2,None,"Sprint 43",8,"2024-05-01","2024-06-01","2024-07-01","dbt,sql","DATA-201"),
    (14,"BI-301","BI","Story","Executive KPI Dashboard","C-suite dashboard: revenue, headcount, CSAT, burn rate",
     "IN PROGRESS","HIGH",4,1,None,"Sprint 42",13,"2024-04-15","2024-06-01","2024-06-30","powerbi,executive",""),
    (15,"BI-302","BI","Task","Connect Power BI to Synapse","Set up DirectQuery connection for real-time dashboard",
     "DONE","HIGH",4,4,"BI-301","Sprint 41",5,"2024-04-20","2024-05-20","2024-05-20","powerbi,synapse",""),
    (16,"BI-303","BI","Bug","Sales chart shows wrong YTD","YTD calculation off by 1 day due to timezone issue",
     "OPEN","HIGH",4,11,"BI-301","Sprint 42",None,"2024-06-01","2024-06-01","2024-06-07","bug,powerbi,timezone",""),
    (17,"INFRA-401","INFRA","Story","Kubernetes migration for microservices","Move 8 services from EC2 to AKS",
     "IN PROGRESS","HIGH",6,1,None,"Sprint 42",21,"2024-02-01","2024-06-01","2024-08-31","kubernetes,azure,migration",""),
    (18,"INFRA-402","INFRA","Task","Dockerize legacy auth service","Write Dockerfile + compose for auth-service",
     "DONE","MEDIUM",6,6,"INFRA-401","Sprint 39",5,"2024-03-01","2024-04-01","2024-04-01","docker",""),
    (19,"INFRA-403","INFRA","Task","Set up AKS cluster","Provision AKS with 3 node pools, RBAC, networking",
     "DONE","HIGH",6,6,"INFRA-401","Sprint 40",8,"2024-03-15","2024-05-01","2024-05-01","aks,azure",""),
    (20,"INFRA-404","INFRA","Bug","Pod OOMKilled in production","Auth service pods being OOMKilled under load",
     "OPEN","CRITICAL",6,6,"INFRA-401","Sprint 42",None,"2024-06-02","2024-06-02","2024-06-04","bug,kubernetes,memory",""),
    (21,"HR-501","HR","Story","Self-service leave portal","Employees can apply/track leave without email",
     "IN PROGRESS","MEDIUM",7,7,None,"Sprint 43",8,"2024-05-01","2024-06-01","2024-07-31","hr,leave",""),
    (22,"HR-502","HR","Story","Onboarding checklist automation","Auto-generate onboarding tasks for new joiners",
     "TODO","LOW",12,7,None,"Sprint 44",5,"2024-05-15","2024-05-15","2024-08-31","hr,onboarding",""),
]

LEAVE_BALANCES = [
    ("EMP001","Annual Leave",24,8,16,2024),
    ("EMP001","Sick Leave",10,2,8,2024),
    ("EMP001","Casual Leave",6,1,5,2024),
    ("EMP002","Annual Leave",24,5,19,2024),
    ("EMP002","Sick Leave",10,0,10,2024),
    ("EMP002","Casual Leave",6,2,4,2024),
    ("EMP003","Annual Leave",24,12,12,2024),
    ("EMP003","Sick Leave",10,3,7,2024),
    ("EMP004","Annual Leave",24,6,18,2024),
    ("EMP004","Maternity Leave",180,0,180,2024),
    ("EMP005","Annual Leave",24,10,14,2024),
    ("EMP005","Sick Leave",10,1,9,2024),
]

LEAVE_REQUESTS = [
    (1,"EMP002","Annual Leave","2024-07-01","2024-07-05",5,"APPROVED","Family vacation","2024-06-01","Ravi Kumar"),
    (2,"EMP003","Annual Leave","2024-06-10","2024-06-14",5,"PENDING","Wedding anniversary trip","2024-06-01",None),
    (3,"EMP004","Sick Leave","2024-05-20","2024-05-21",2,"APPROVED","Fever","2024-05-19","Ravi Kumar"),
    (4,"EMP008","Casual Leave","2024-06-15","2024-06-15",1,"PENDING","Personal work","2024-06-01",None),
]

HELPDESK_TICKETS = [
    ("TKT-001","Laptop running slow — 8GB RAM","Dell XPS laptop taking 5 mins to boot, high CPU always","Hardware","HIGH","RESOLVED","EMP003","IT Team","2024-05-01","2024-05-03","Increased RAM to 16GB"),
    ("TKT-002","VPN disconnects every 30 mins","GlobalProtect VPN drops connection frequently on home network","Network","MEDIUM","IN PROGRESS","EMP002","EMP006","2024-06-01",None,None),
    ("TKT-003","Cannot access Jira — 403 error","Getting 403 forbidden when accessing DATA project in Jira","Access","HIGH","OPEN","EMP011","IT Team","2024-06-02",None,None),
    ("TKT-004","Need Adobe Acrobat Pro license","Require PDF editing for contract management","Software","LOW","OPEN","EMP005","IT Team","2024-06-01",None,None),
    ("TKT-005","Office 365 license not activated","New laptop doesn't have O365 activated","Software","HIGH","RESOLVED","EMP010","IT Team","2024-05-28","2024-05-29","License assigned from pool"),
    ("TKT-006","Wi-Fi dropping in conference room B","Meeting disruptions due to poor Wi-Fi signal","Network","MEDIUM","IN PROGRESS","EMP009","EMP006","2024-05-30",None,None),
]

ANNOUNCEMENTS = [
    (1,"🎉 Q2 All-Hands Meeting — June 20th","Join us for our quarterly all-hands! CEO Ravi Kumar will present Q2 results, product roadmap, and we'll have a live Q&A. Zoom link will be shared 24h before.","Company","HR Team","2024-06-01",1,"All"),
    (2,"🏥 New Health Insurance Plan from July 1st","We have upgraded our group health insurance to include dental, vision, and mental health coverage. Sum insured increased to ₹10 Lakhs per family. Details in the attachment.","HR","Mohan Reddy","2024-06-01",1,"All"),
    (3,"🚀 SuperBot v2.0 Launch","Our internal AI assistant SuperBot is now live! Ask HR policy questions, track Jira tickets, query data — all in one place. Try it now!","Tech","Engineering Team","2024-06-03",0,"All"),
    (4,"📅 Public Holiday: June 17 (Eid)","June 17th is a company holiday. Please plan your sprints and deadlines accordingly. Emergency contacts listed in the HR portal.","HR","Mohan Reddy","2024-06-02",0,"All"),
    (5,"💰 Referral Bonus Doubled — ₹50,000","We're hiring! Successfully refer a candidate who joins and completes 6 months — earn ₹50,000 (was ₹25,000). Open roles listed in the careers portal.","HR","Mohan Reddy","2024-05-28",0,"All"),
    (6,"🛡️ Mandatory Security Training Due June 30","Complete the annual cybersecurity awareness training on the LMS by June 30th. Non-completion will result in access restrictions.","IT","IT Security","2024-05-25",0,"All"),
]

DW_TABLES = [
    ("sales","fact_orders","BASE TABLE",8420000,1240.5,"Sales Analytics","2022-01-15","2024-06-01"),
    ("sales","dim_customer","BASE TABLE",350000,45.2,"CRM Team","2022-01-15","2024-05-28"),
    ("sales","dim_product","BASE TABLE",12000,3.1,"Product Team","2022-01-15","2024-04-10"),
    ("finance","fact_transactions","BASE TABLE",22000000,4800.0,"Finance Analytics","2021-06-01","2024-06-01"),
    ("hr","dim_employee","BASE TABLE",18000,4.2,"HR Analytics","2022-09-01","2024-05-31"),
    ("staging","stg_raw_orders","BASE TABLE",1200000,180.0,"Data Engineering","2023-01-01","2024-06-01"),
    ("dbo","vw_sales_summary","VIEW",0,0.0,"BI Team","2023-03-01","2024-04-01"),
]

DW_COLUMNS = [
    ("sales","fact_orders","order_id","BIGINT","NO",1),
    ("sales","fact_orders","customer_id","BIGINT","NO",2),
    ("sales","fact_orders","order_date","DATE","NO",3),
    ("sales","fact_orders","total_amount","DECIMAL","NO",4),
    ("sales","fact_orders","order_status","NVARCHAR","YES",5),
    ("sales","dim_customer","customer_id","BIGINT","NO",1),
    ("sales","dim_customer","customer_name","NVARCHAR","NO",2),
    ("sales","dim_customer","email","NVARCHAR","YES",3),
    ("sales","dim_customer","customer_segment","NVARCHAR","YES",4),
    ("finance","fact_transactions","transaction_id","BIGINT","NO",1),
    ("finance","fact_transactions","amount","DECIMAL","NO",2),
    ("finance","fact_transactions","currency_code","NCHAR","NO",3),
    ("finance","fact_transactions","customer_id","BIGINT","YES",4),
]

PIPELINE_RUNS = [
    ("PL_Orders_ETL","SUCCESS","2024-06-01 02:00","2024-06-01 02:47",1200000,None),
    ("PL_Finance_ETL","FAILED","2024-06-01 03:00","2024-06-01 03:12",0,"Connection timeout to source"),
    ("PL_Customer_ETL","SUCCESS","2024-06-01 01:30","2024-06-01 01:58",95000,None),
    ("PL_HR_ETL","SUCCESS","2024-06-01 00:30","2024-06-01 00:55",18000,None),
]

EXPENSES = [
    ("EMP003","Travel",12500.0,"INR","Flight HYD-BLR for client meeting","2024-05-15","APPROVED","Ravi Kumar"),
    ("EMP002","Conference",45000.0,"INR","PyConf India 2024 registration + hotel","2024-05-20","PENDING",None),
    ("EMP004","Software",8999.0,"INR","Power BI Pro license annual","2024-05-10","APPROVED","Ravi Kumar"),
    ("EMP005","Entertainment",3200.0,"INR","Client dinner at Taj Hotel","2024-05-25","APPROVED","Ravi Kumar"),
    ("EMP006","Hardware",6500.0,"INR","USB-C hub and HDMI cable for home office","2024-05-28","REJECTED","Sunita Rao"),
]

def seed():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.executescript(SCHEMA)

    c.execute("SELECT COUNT(*) FROM employees")
    if c.fetchone()[0] == 0:
        c.executemany("INSERT OR IGNORE INTO employees VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", EMPLOYEES)
        c.executemany("INSERT OR IGNORE INTO jira_projects VALUES (?,?,?,?,?)", JIRA_PROJECTS)
        c.executemany("INSERT OR IGNORE INTO jira_issues VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", JIRA_ISSUES)
        c.executemany("INSERT OR IGNORE INTO leave_balances VALUES (NULL,?,?,?,?,?,?)", LEAVE_BALANCES)
        c.executemany("INSERT OR IGNORE INTO leave_requests VALUES (?,?,?,?,?,?,?,?,?,?)", LEAVE_REQUESTS)
        c.executemany("INSERT OR IGNORE INTO helpdesk_tickets VALUES (NULL,?,?,?,?,?,?,?,?,?,?,?)", HELPDESK_TICKETS)
        c.executemany("INSERT OR IGNORE INTO announcements VALUES (?,?,?,?,?,?,?,?)", ANNOUNCEMENTS)
        c.executemany("INSERT OR IGNORE INTO dw_tables VALUES (NULL,?,?,?,?,?,?,?,?)", DW_TABLES)
        c.executemany("INSERT OR IGNORE INTO dw_columns VALUES (NULL,?,?,?,?,?,?)", DW_COLUMNS)
        c.executemany("INSERT OR IGNORE INTO pipeline_runs VALUES (NULL,?,?,?,?,?,?)", PIPELINE_RUNS)
        c.executemany("INSERT OR IGNORE INTO expenses VALUES (NULL,?,?,?,?,?,?,?,?)", EXPENSES)

    conn.commit()
    conn.close()
    print(f"✅ SuperBot DB seeded: {DB_PATH}")

if __name__ == "__main__":
    seed()

EXTRA_SCHEMA = """
CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY, user_name TEXT, action TEXT, module TEXT,
    details TEXT, ip_address TEXT, timestamp TEXT
);
CREATE TABLE IF NOT EXISTS conversation_history (
    id INTEGER PRIMARY KEY, session_id TEXT, user_name TEXT, role TEXT,
    content TEXT, module TEXT, feedback INTEGER DEFAULT 0, timestamp TEXT
);
CREATE TABLE IF NOT EXISTS feedback (
    id INTEGER PRIMARY KEY, message_id INTEGER, user_name TEXT,
    rating INTEGER, comment TEXT, timestamp TEXT
);
CREATE TABLE IF NOT EXISTS usage_analytics (
    id INTEGER PRIMARY KEY, user_name TEXT, module TEXT, intent TEXT,
    query_length INTEGER, response_time_ms INTEGER, date TEXT, hour INTEGER
);
CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY, alert_type TEXT, title TEXT, message TEXT,
    severity TEXT, is_read INTEGER DEFAULT 0, created_at TEXT, resolved_at TEXT
);
CREATE TABLE IF NOT EXISTS mcp_tools (
    id INTEGER PRIMARY KEY, tool_name TEXT, description TEXT,
    module TEXT, enabled INTEGER DEFAULT 1, call_count INTEGER DEFAULT 0
);
CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY, filename TEXT, file_type TEXT, file_size INTEGER,
    uploaded_by TEXT, uploaded_at TEXT, chunk_count INTEGER, status TEXT
);
"""

SEED_ALERTS = [
    ("pipeline","PL_Finance_ETL Failed","Finance ETL pipeline failed at 03:12 — connection timeout to SAP source","critical",0,"2024-06-01 03:12",None),
    ("quality","Data Quality Warning — dim_customer","1,240 NULL emails detected in dim_customer. Exceeds 1% threshold.","warning",0,"2024-06-01 06:00",None),
    ("jira","5 Critical Bugs Open > 48hrs","ACME-106 (Safari crash), DATA-205 (duplicate events), INFRA-404 (OOMKilled) unresolved","warning",0,"2024-06-02 09:00",None),
    ("system","Security Training Due June 30","42 employees have not completed mandatory cybersecurity training","info",1,"2024-05-25 09:00",None),
]

SEED_MCP_TOOLS = [
    ("sql_query","Execute SQL queries against the data warehouse","data",1,0),
    ("jira_create","Create Jira issues, stories, tasks, bugs","jira",1,0),
    ("jira_update","Update Jira issue status and add comments","jira",1,0),
    ("hr_lookup","Look up employee info and leave balances","hr",1,0),
    ("doc_search","Semantic search across uploaded documents","rag",1,0),
    ("pipeline_status","Check ETL pipeline run status","data",1,0),
    ("helpdesk_create","Create IT helpdesk tickets","helpdesk",1,0),
    ("summarize_doc","Summarize an uploaded document","rag",1,0),
    ("leave_apply","Submit leave application","hr",1,0),
    ("send_alert","Send proactive alert notification","system",1,0),
]

def seed_extra():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.executescript(EXTRA_SCHEMA)
    c.execute("SELECT COUNT(*) FROM alerts")
    if c.fetchone()[0] == 0:
        c.executemany("INSERT INTO alerts (alert_type,title,message,severity,is_read,created_at,resolved_at) VALUES (?,?,?,?,?,?,?)", SEED_ALERTS)
        c.executemany("INSERT INTO mcp_tools (tool_name,description,module,enabled,call_count) VALUES (?,?,?,?,?)", SEED_MCP_TOOLS)
    conn.commit(); conn.close()
    print("✅ Extra tables seeded")

if __name__ == "__main__":
    seed()
    seed_extra()
