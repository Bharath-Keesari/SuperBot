"""SuperBot — ChatGPT-style Enterprise AI Assistant"""
import streamlit as st
import sys, os, time, uuid
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

st.set_page_config(
    page_title="SuperBot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════════════
#  STYLES — ChatGPT-style
# ═══════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

/* ── BASE ── */
:root {
  --sidebar-bg:   #202123;
  --sidebar-hover:#2a2b32;
  --sidebar-act:  #343541;
  --main-bg:      #343541;
  --input-bg:     #40414f;
  --input-border: #565869;
  --user-bubble:  #343541;
  --bot-bubble:   #444654;
  --text:         #ececf1;
  --text-muted:   #8e8ea0;
  --text-dim:     #565869;
  --green:        #19c37d;
  --border:       rgba(255,255,255,0.1);
  --r:            8px;
}

*,*::before,*::after { box-sizing:border-box; margin:0; padding:0; }

html, body, .stApp, [data-testid="stAppViewContainer"] {
  background: var(--main-bg) !important;
  font-family: 'Inter', sans-serif !important;
  color: var(--text) !important;
}

/* ── HIDE CHROME ── */
#MainMenu, header[data-testid="stHeader"],
footer, .stDeployButton { display:none !important; }

/* ── SIDEBAR ── */
section[data-testid="stSidebar"] {
  background: var(--sidebar-bg) !important;
  border-right: 1px solid var(--border) !important;
  min-width: 260px !important;
  max-width: 260px !important;
}
section[data-testid="stSidebar"] > div { padding: 0 !important; }
section[data-testid="stSidebar"] * {
  font-family: 'Inter', sans-serif !important;
  color: var(--text) !important;
}

/* ── BLOCK CONTAINER ── */
.block-container { padding: 0 !important; max-width: 100% !important; }

/* ── BUTTONS ── */
.stButton > button {
  font-family: 'Inter', sans-serif !important;
  font-size: 14px !important;
  font-weight: 400 !important;
  color: var(--text) !important;
  background: transparent !important;
  border: none !important;
  border-radius: var(--r) !important;
  text-align: left !important;
  transition: background .15s !important;
  padding: 8px 12px !important;
}
.stButton > button:hover {
  background: var(--sidebar-hover) !important;
  border: none !important;
  color: var(--text) !important;
}
.stButton > button[kind="primary"] {
  background: #19c37d !important;
  color: #000 !important;
  font-weight: 600 !important;
  border-radius: var(--r) !important;
}
.stButton > button[kind="primary"]:hover {
  background: #1aa86d !important;
  transform: none !important;
  box-shadow: none !important;
}

/* ── CHAT INPUT + BOTTOM STRIP — full dark fix ── */
/* Kill the white footer/strip Streamlit renders under the chat input */
.stChatFloatingInputContainer,
[data-testid="stChatInputContainer"],
[data-testid="stBottom"],
[data-testid="stBottom"] > div,
[data-testid="stBottom"] > div > div {
  background: #000000 !important;
}

[data-testid="stChatInput"] {
  background: #1c1c1e !important;
  border: 1px solid #3a3a4a !important;
  border-radius: 12px !important;
  box-shadow: none !important;
  max-width: 800px !important;
  margin: 0 auto !important;
}
[data-testid="stChatInput"]:focus-within {
  border-color: #565869 !important;
  box-shadow: 0 0 0 2px rgba(255,255,255,0.06) !important;
}
[data-testid="stChatInput"] textarea {
  font-family: 'Inter', sans-serif !important;
  font-size: 15px !important;

  background: #ffffff !important;   /* input box white */
  color: #000000 !important;        /* typing black */
  caret-color: #000000 !important;  /* cursor visible */
}
/* FORCE readable chat input */
[data-testid="stChatInput"] textarea {
  background: #1c1c1e !important;
  color: #ffffff !important;
  caret-color: #ffffff !important;
}
/* placeholder */
[data-testid="stChatInput"] textarea::placeholder {color: #6b7280 !important;}
[data-testid="stChatInput"] > div { background: transparent !important; }

/* Praval logo styles */ 
.praval-logo {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 18px 16px 14px;
  border-bottom: 1px solid rgba(255,255,255,0.08);
  text-decoration: none;
}
.praval-wordmark {
  font-size: 19px;
  font-weight: 800;
  color: #ffffff !important;
  letter-spacing: 0.08em;
  font-family: 'Inter', sans-serif;
}

/* ── MARKDOWN ── */
.stMarkdown p, .stMarkdown li {
  color: var(--text) !important;
  font-size: 15px !important;
  line-height: 1.7 !important;
}
.stMarkdown h1,.stMarkdown h2,.stMarkdown h3 {
  color: var(--text) !important;
  font-weight: 600 !important;
}
.stMarkdown strong { color: var(--text) !important; font-weight: 600 !important; }
.stMarkdown code {
  font-family: 'Menlo','Monaco',monospace !important;
  background: rgba(0,0,0,0.3) !important;
  color: #e5c07b !important;
  padding: 2px 6px !important;
  border-radius: 4px !important;
  font-size: 13px !important;
}
.stMarkdown pre {
  background: #1e1e2e !important;
  border-radius: 8px !important;
  padding: 16px !important;
  overflow-x: auto !important;
}
.stMarkdown pre code {
  background: transparent !important;
  color: #a6e3a1 !important;
  padding: 0 !important;
  font-size: 13px !important;
}
.stMarkdown table { border-collapse: collapse !important; width: 100% !important; }
.stMarkdown th {
  background: rgba(255,255,255,0.1) !important;
  color: var(--text) !important;
  padding: 8px 12px !important;
  font-size: 13px !important;
  border: 1px solid var(--border) !important;
}
.stMarkdown td {
  padding: 8px 12px !important;
  border: 1px solid var(--border) !important;
  font-size: 13px !important;
  color: var(--text) !important;
}
.stMarkdown a { color: #19c37d !important; }

/* ── DATAFRAME ── */
[data-testid="stDataFrame"] {
  border-radius: var(--r) !important;
  overflow: hidden !important;
}
[data-testid="stDataFrame"] thead th {
  background: rgba(255,255,255,0.08) !important;
  color: var(--text) !important;
  font-size: 12px !important;
  font-weight: 600 !important;
}
[data-testid="stDataFrame"] tbody td {
  font-size: 12px !important;
  color: var(--text-muted) !important;
  background: rgba(255,255,255,0.03) !important;
}

/* ── EXPANDER ── */
[data-testid="stExpander"] {
  background: rgba(255,255,255,0.04) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--r) !important;
}
[data-testid="stExpander"] summary { color: var(--text-muted) !important; font-size: 12px !important; }

/* ── FILE UPLOADER ── */
[data-testid="stFileUploadDropzone"] {
  background: rgba(255,255,255,0.03) !important;
  border: 2px dashed var(--border) !important;
  border-radius: var(--r) !important;
  color: var(--text-muted) !important;
}
[data-testid="stFileUploadDropzone"]:hover {
  border-color: var(--green) !important;
  background: rgba(25,195,125,0.05) !important;
}

/* ── SELECTS / INPUTS ── */
[data-testid="stSelectbox"] > div > div,
[data-testid="stTextInput"] > div > div > input,
[data-testid="stTextArea"] textarea {
  background: var(--input-bg) !important;
  border: 1px solid var(--input-border) !important;
  border-radius: var(--r) !important;
  color: var(--text) !important;
  font-size: 14px !important;
}
[data-testid="stSelectbox"] > div > div svg { fill: var(--text-muted) !important; }
label { color: var(--text-muted) !important; font-size: 13px !important; }

/* ── TABS ── */
[data-testid="stTabs"] { background: transparent !important; }
button[role="tab"] {
  color: var(--text-muted) !important;
  font-size: 14px !important;
  background: transparent !important;
  border-bottom: 2px solid transparent !important;
}
button[role="tab"][aria-selected="true"] {
  color: var(--text) !important;
  border-bottom-color: var(--green) !important;
}
[data-testid="stTabsContent"] { background: transparent !important; }

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.15); border-radius: 4px; }
::-webkit-scrollbar-track { background: transparent; }

/* ── METRIC ── */
[data-testid="stMetric"] { background: rgba(255,255,255,0.04) !important; border-radius: var(--r) !important; padding: 12px 16px !important; border: 1px solid var(--border) !important; }
[data-testid="stMetricLabel"] { color: var(--text-muted) !important; font-size: 12px !important; }
[data-testid="stMetricValue"] { color: var(--text) !important; font-size: 24px !important; font-weight: 700 !important; }

/* ── CUSTOM HTML COMPONENTS ── */

/* Sidebar header */
.sb-logo {
  padding: 16px;
  border-bottom: 1px solid var(--border);
  display: flex; align-items: center; gap: 10px;
  font-size: 17px; font-weight: 700; color: var(--text);
}
.sb-logo-icon { font-size: 22px; }

/* New chat button */
.new-chat-btn {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 14px; margin: 8px 10px;
  border: 1px solid var(--border); border-radius: var(--r);
  font-size: 14px; font-weight: 500; color: var(--text);
  cursor: pointer; transition: background .15s;
}
.new-chat-btn:hover { background: var(--sidebar-hover); }
.sb-section-label {
  font-size: 11px; font-weight: 600; color: var(--text-dim);
  text-transform: uppercase; letter-spacing: .08em;
  padding: 12px 16px 4px;
}
.nav-item {
  display: flex; align-items: center; gap: 10px;
  padding: 9px 14px; margin: 1px 8px;
  border-radius: var(--r); font-size: 14px;
  color: var(--text-muted); cursor: pointer; transition: all .15s;
}
.nav-item:hover { background: var(--sidebar-hover); color: var(--text); }
.nav-item.active { background: var(--sidebar-act); color: var(--text); }
.nav-icon { width: 18px; text-align: center; font-size: 15px; }
.sb-divider { height: 1px; background: var(--border); margin: 8px 0; }
.sb-bottom {
  border-top: 1px solid var(--border); padding: 12px 14px;
  display: flex; align-items: center; gap: 10px;
}
.sb-user-av {
  width: 32px; height: 32px; border-radius: 50%;
  background: #19c37d; display: flex; align-items: center; justify-content: center;
  font-size: 13px; font-weight: 700; color: #000; flex-shrink: 0;
}
.sb-user-name { font-size: 14px; font-weight: 500; color: var(--text); }
.sb-user-role { font-size: 11px; color: var(--text-dim); }

/* Chat messages */
.msg-wrap {
  display: flex; gap: 16px; padding: 20px 0;
  max-width: 800px; margin: 0 auto;
}
.msg-av {
  width: 32px; height: 32px; border-radius: 4px; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
  font-size: 15px; font-weight: 700;
}
.msg-av.user { background: #19c37d; color: #000; font-size: 13px; border-radius: 50%; }
.msg-av.bot  { background: #19c37d; color: #000; font-size: 17px; border-radius: 4px; }
.msg-content { flex: 1; min-width: 0; }
.msg-name { font-size: 13px; font-weight: 600; color: var(--text); margin-bottom: 6px; }
.msg-text-user {
  font-size: 15px; line-height: 1.65; color: var(--text);
  background: rgba(255,255,255,0.07); border-radius: var(--r);
  padding: 12px 16px; display: inline-block; max-width: 100%;
}
.msg-row-user { display:flex; gap:16px; padding:20px 0; max-width:800px; margin:0 auto; flex-direction:row-reverse; }

/* Module tag */
.mod-tag {
  display: inline-flex; align-items: center; gap: 4px;
  padding: 2px 8px; border-radius: 4px; font-size: 11px;
  font-weight: 600; margin-bottom: 8px; letter-spacing: .02em;
}
.mt-jira { background: rgba(59,130,246,.2); color: #93c5fd; }
.mt-hr   { background: rgba(34,197,94,.2);  color: #86efac; }
.mt-data { background: rgba(168,85,247,.2); color: #d8b4fe; }
.mt-rag  { background: rgba(245,158,11,.2); color: #fcd34d; }
.mt-help { background: rgba(249,115,22,.2); color: #fdba74; }
.mt-ai   { background: rgba(255,255,255,.1); color: #c7c7d1; }

/* Source pills */
.src-row { display: flex; flex-wrap: wrap; gap: 4px; margin-top: 8px; }
.src-pill {
  display: inline-flex; align-items: center; gap: 4px;
  background: rgba(255,255,255,0.07); border: 1px solid rgba(255,255,255,0.12);
  padding: 2px 8px; border-radius: 4px; font-size: 11px; color: var(--text-muted);
}

/* MCP tags */
.mcp-row { display: flex; flex-wrap: wrap; gap: 4px; margin-top: 6px; }
.mcp-tag {
  display: inline-flex; align-items: center; gap: 4px;
  background: rgba(25,195,125,.1); border: 1px solid rgba(25,195,125,.2);
  padding: 2px 8px; border-radius: 4px; font-size: 11px; color: #19c37d;
}

/* Feedback */
.fb-row { display: flex; gap: 8px; margin-top: 10px; }
.fb-btn {
  font-size: 14px; background: transparent; border: none;
  color: var(--text-dim); cursor: pointer; padding: 4px; border-radius: 4px;
  transition: color .15s;
}
.fb-btn:hover { color: var(--text); }

/* Welcome screen */
.welcome-wrap { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 60px 24px 30px; }
.welcome-icon { font-size: 52px; margin-bottom: 16px; }
.welcome-title { font-size: 28px; font-weight: 700; color: var(--text); margin-bottom: 8px; }
.welcome-sub { font-size: 15px; color: var(--text-muted); margin-bottom: 36px; text-align: center; max-width: 500px; line-height: 1.6; }
.suggestions { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; max-width: 700px; width: 100%; }
.suggestion-card {
  background: rgba(255,255,255,0.05); border: 1px solid var(--border);
  border-radius: var(--r); padding: 14px 16px; cursor: pointer;
  transition: all .15s; text-align: left;
}
.suggestion-card:hover { background: rgba(255,255,255,0.09); border-color: rgba(255,255,255,0.2); }
.sc-title { font-size: 14px; font-weight: 600; color: var(--text); margin-bottom: 3px; }
.sc-desc  { font-size: 12px; color: var(--text-dim); line-height: 1.5; }

/* Stat card */
.stat-box {
  background: rgba(255,255,255,0.05); border: 1px solid var(--border);
  border-radius: var(--r); padding: 16px 20px;
}
.stat-num { font-size: 28px; font-weight: 700; color: var(--text); }
.stat-lbl { font-size: 12px; color: var(--text-muted); margin-top: 3px; }

/* Alert */
.alert-bar {
  display: flex; align-items: flex-start; gap: 10px;
  padding: 10px 14px; border-radius: var(--r); margin-bottom: 8px;
  font-size: 13px; border-left: 3px solid;
}
.alert-c { background: rgba(239,68,68,.1);  border-color: #ef4444; color: #fca5a5; }
.alert-w { background: rgba(245,158,11,.1); border-color: #f59e0b; color: #fcd34d; }
.alert-i { background: rgba(59,130,246,.1); border-color: #3b82f6; color: #93c5fd; }

/* Doc row */
.doc-row {
  display: flex; align-items: center; justify-content: space-between;
  padding: 10px 14px; border-radius: var(--r); margin: 4px 0;
  background: rgba(255,255,255,0.04); border: 1px solid var(--border);
  transition: background .15s;
}
.doc-row:hover { background: rgba(255,255,255,0.07); }
.doc-name { font-size: 13px; font-weight: 500; color: var(--text); }
.doc-meta { font-size: 11px; color: var(--text-dim); margin-top: 2px; }
.doc-badge {
  font-size: 10px; font-weight: 600; padding: 2px 8px; border-radius: 4px;
  background: rgba(25,195,125,.15); color: #19c37d;
}

/* Board card */
.board-col { background: rgba(255,255,255,0.03); border-radius: var(--r); padding: 10px; }
.board-col-hdr { font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: .08em; color: var(--text-dim); margin-bottom: 8px; }
.board-card { background: rgba(255,255,255,0.06); border: 1px solid var(--border); border-radius: var(--r); padding: 10px; margin: 5px 0; cursor: pointer; transition: background .15s; border-left: 3px solid transparent; }
.board-card:hover { background: rgba(255,255,255,0.09); }
.bc-key { font-size: 10px; color: var(--text-dim); margin-bottom: 3px; }
.bc-title { font-size: 12px; font-weight: 500; color: var(--text); line-height: 1.4; margin-bottom: 6px; }
.bc-meta { display: flex; gap: 6px; align-items: center; }
.bc-type { font-size: 10px; padding: 1px 6px; border-radius: 3px; font-weight: 600; }
.bc-s { background: rgba(59,130,246,.2); color: #93c5fd; }
.bc-b { background: rgba(239,68,68,.2); color: #fca5a5; }
.bc-t { background: rgba(34,197,94,.2); color: #86efac; }

/* Leave bar */
.lbar-wrap { background: rgba(255,255,255,0.1); border-radius: 4px; height: 6px; overflow: hidden; }
.lbar-fill { height: 100%; background: #19c37d; border-radius: 4px; }

/* Settings row */pythin
.set-row { display: flex; justify-content: space-between; align-items: center; padding: 12px 0; border-bottom: 1px solid var(--border); }
.set-row:last-child { border: none; }
.set-label { font-size: 14px; font-weight: 500; color: var(--text); }
.set-val { font-size: 13px; color: var(--text-muted); }

            
            
/* MCP tool row */
.tool-row {
  display: flex; align-items: center; justify-content: space-between;
  padding: 12px 14px; border-radius: var(--r); margin: 4px 0;
  background: rgba(255,255,255,0.04); border: 1px solid var(--border);
  border-left: 3px solid;
}
.tool-name { font-size: 13px; font-weight: 600; color: var(--text); font-family: monospace; }
.tool-desc { font-size: 12px; color: var(--text-dim); margin-top: 2px; }
.tool-calls { font-size: 20px; font-weight: 700; color: var(--text); text-align: right; }
.tool-calls-lbl { font-size: 10px; color: var(--text-dim); }
.tool-status { font-size: 11px; font-weight: 600; margin-top: 3px; }

/* Announcement */
.ann-card {
  background: rgba(255,255,255,0.04); border: 1px solid var(--border);
  border-radius: var(--r); padding: 16px; margin: 8px 0;
  border-left: 3px solid;
}
.ann-title { font-size: 14px; font-weight: 600; color: var(--text); margin-bottom: 6px; }
.ann-body  { font-size: 13px; color: var(--text-muted); line-height: 1.6; }
.ann-footer { font-size: 11px; color: var(--text-dim); margin-top: 8px; }

/* Integration row */
.int-row { display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid var(--border); }
.int-row:last-child { border: none; }
.int-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.int-name { font-size: 14px; color: var(--text); }

/* Bar chart placeholder style */
[data-testid="stVegaLiteChart"] { border-radius: var(--r) !important; overflow: hidden !important; }

/* Hide text on overlay nav buttons (visual handled by markdown) */
section[data-testid="stSidebar"] .stButton > button {
  opacity: 0 !important;
  position: absolute !important;
  top: -32px !important;
  left: 0 !important;
  width: 100% !important;
  height: 42px !important;
  cursor: pointer !important;
  z-index: 10 !important;
}
section[data-testid="stSidebar"] .stButton {
  position: relative !important;
  margin-top: -42px !important;
  height: 0 !important;
}

/* REMOVE Streamlit header (contains sidebar toggle + keyboard text) */
header[data-testid="stHeader"] {
  display: none !important;
}

/* Remove sidebar collapse control */
[data-testid="collapsedControl"] {
  display: none !important;
}

/* Prevent sidebar from sliding */
section[data-testid="stSidebar"] {
  transform: none !important;
  margin-left: 0 !important;
}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
#  BOOT & SESSION
# ═══════════════════════════════════════════════════════════
@st.cache_resource(show_spinner=False)
def boot():
    from data.seed_db import seed
    seed()
    try:
        from backend.rag_handler import init
        init()
    except Exception as e:
        print(f"RAG: {e}")
    return True

@st.cache_resource(show_spinner=False)
def get_process():
    from backend.orchestrator import process
    return process

for k, v in [("msgs", []), ("sid", str(uuid.uuid4())), ("mod", "chat"),
              ("qcnt", 0), ("uname", "Bharath K"), ("uini", "BK"), ("pend", None)]:
    if k not in st.session_state:
        st.session_state[k] = v

with st.spinner(""):
    try:
        boot()
        process_q = get_process()
        ok = True
    except Exception as e:
        st.error(f"Boot error: {e}")
        ok = False

# ═══════════════════════════════════════════════════════════
#  DB
# ═══════════════════════════════════════════════════════════
import sqlite3 as _sq
_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/superbot.db")

def dbq(sql, p=()):
    try:
        c = _sq.connect(_DB); c.row_factory = _sq.Row
        r = c.execute(sql, p).fetchall(); c.close()
        return [dict(x) for x in r]
    except: return []

def dbx(sql, p=()):
    try:
        c = _sq.connect(_DB); c.execute(sql, p); c.commit(); c.close()
    except: pass

def audit(action, mod, detail=""):
    dbx("INSERT INTO audit_logs(user_name,action,module,details,timestamp)VALUES(?,?,?,?,?)",
        (st.session_state.uname, action, mod, str(detail)[:300], datetime.now().isoformat()))

def save_conv(role, content, mod):
    dbx("INSERT INTO conversation_history(session_id,user_name,role,content,module,timestamp)VALUES(?,?,?,?,?,?)",
        (st.session_state.sid, st.session_state.uname, role, content[:1500], mod, datetime.now().isoformat()))

def log_usage(mod, intent, qlen, ms):
    n = datetime.now()
    dbx("INSERT INTO usage_analytics(user_name,module,intent,query_length,response_time_ms,date,hour)VALUES(?,?,?,?,?,?,?)",
        (st.session_state.uname, mod, intent, qlen, ms, n.strftime("%Y-%m-%d"), n.hour))

def get_alerts():
    return dbq("SELECT * FROM alerts WHERE is_read=0 ORDER BY created_at DESC")

# ═══════════════════════════════════════════════════════════
#  SIDEBAR
# ═══════════════════════════════════════════════════════════
alerts = get_alerts()

with st.sidebar:
    # Praval Logo - Image version
    logo_path = "assets/Praval-logo.png"
    
    # Check if logo exists, if not show fallback text
    if os.path.exists(logo_path):
        st.image(logo_path, width=180)
    else:
        st.markdown("""
        <div class="praval-logo">
          <span style="font-size: 24px; font-weight: 800; color: #ffffff;">PRAVAL</span>
        </div>
        """, unsafe_allow_html=True)

    # New chat button
    if st.button("✏️   New Chat", key="__newchat", use_container_width=True):
        st.session_state.msgs = []
        st.session_state.sid  = str(uuid.uuid4())
        st.session_state.mod  = "chat"
        st.rerun()
        
    # Navigation
    st.markdown('<div class="sb-section-label">Features</div>', unsafe_allow_html=True)

    NAV = [
        ("chat",     "💬", "Chat"),
        ("jira",     "🎫", "Jira Issues"),
        ("hr",       "👔", "HR & Leave"),
        ("data",     "📊", "Data & SQL"),
        ("kb",       "📚", "Knowledge Base"),
        ("helpdesk", "🔧", "IT Helpdesk"),
    ]
    for key, icon, label in NAV:
        active = " active" if st.session_state.mod == key else ""
        st.markdown(f'<div class="nav-item{active}"><span class="nav-icon">{icon}</span>{label}</div>',
                    unsafe_allow_html=True)
        if st.button(label, key=f"__nav_{key}", use_container_width=True):
            st.session_state.mod = key
            st.rerun()

    st.markdown('<div class="sb-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sb-section-label">Admin</div>', unsafe_allow_html=True)
    for key, icon, label in [("admin", "⚙️", "Admin Panel"), ("settings", "🔧", "Settings")]:
        active = " active" if st.session_state.mod == key else ""
        st.markdown(f'<div class="nav-item{active}"><span class="nav-icon">{icon}</span>{label}</div>',
                    unsafe_allow_html=True)
        if st.button(label, key=f"__nav_{key}", use_container_width=True):
            st.session_state.mod = key
            st.rerun()

    # Alerts badge
    if alerts:
        st.markdown('<div class="sb-divider"></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="sb-section-label">🔔 Alerts ({len(alerts)})</div>', unsafe_allow_html=True)
        for a in alerts[:2]:
            col = {"critical":"#ef4444","warning":"#f59e0b","info":"#3b82f6"}.get(a["severity"],"#6b7280")
            ic  = {"critical":"🚨","warning":"⚠️","info":"ℹ️"}.get(a["severity"],"❓")
            st.markdown(f"""
            <div style="margin:2px 8px 2px 10px;padding:7px 10px;background:rgba(255,255,255,.04);
              border-radius:6px;border-left:2px solid {col}">
              <div style="font-size:11px;font-weight:600;color:{col}">{ic} {a['title'][:28]}</div>
              <div style="font-size:10px;color:var(--text-dim);margin-top:1px">{a['message'][:40]}…</div>
            </div>""", unsafe_allow_html=True)

    # User info at bottom
    st.markdown('<div style="flex:1"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sb-divider"></div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="sb-bottom">
      <div class="sb-user-av">{st.session_state.uini}</div>
      <div>
        <div class="sb-user-name">{st.session_state.uname}</div>
        <div class="sb-user-role">💬 {st.session_state.qcnt} queries</div>
      </div>
    </div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
#  MAIN CONTENT
# ═══════════════════════════════════════════════════════════
mod = st.session_state.mod

# ── CHAT ────────────────────────────────────────────────────
if mod == "chat":
    # Show alert banners at top if any
    if alerts:
        for a in alerts[:1]:
            cls = {"critical":"alert-c","warning":"alert-w","info":"alert-i"}.get(a["severity"],"alert-i")
            ic  = {"critical":"🚨","warning":"⚠️","info":"ℹ️"}.get(a["severity"],"ℹ️")
            st.markdown(f'<div style="max-width:800px;margin:12px auto 0">',unsafe_allow_html=True)
            st.markdown(f'<div class="alert-bar {cls}">{ic} <strong>{a["title"]}</strong> — {a["message"][:90]}</div>',unsafe_allow_html=True)
            st.markdown('</div>',unsafe_allow_html=True)

    # Welcome screen when no messages
    if not st.session_state.msgs:
        st.markdown("""
        <div class="welcome-wrap">
          <div class="welcome-icon">🤖</div>
          <div class="welcome-title">How can I help you today?</div>
          <div class="welcome-sub">I'm SuperBot — your enterprise AI assistant. Ask me about Jira tickets,
          HR policies, SQL queries, IT helpdesk, or anything else.</div>
        </div>
        """, unsafe_allow_html=True)

        # Suggestion cards
        suggestions = [
            ("🎫 What are my open Jira tickets?",         "Show all Jira issues assigned to me"),
            ("🏖️ Check leave balance",                     "How many annual leave days do I have remaining?"),
            ("📊 Generate SQL query",                      "Write SQL for top 10 customers by revenue"),
            ("📋 HR Policy question",                      "What is the work from home policy?"),
            ("🔧 Raise IT ticket",                        "Raise IT helpdesk ticket: VPN keeps disconnecting"),
            ("🗄️ Pipeline status",                        "Show ETL pipeline status and any failures"),
            ("👤 Find employee",                          "Who is Priya Sharma and what team does she work in?"),
            ("📄 Search knowledge base",                   "Search knowledge base for expense reimbursement rules"),
        ]
        st.markdown('<div style="max-width:700px;margin:0 auto;display:grid;grid-template-columns:1fr 1fr;gap:10px">',
                    unsafe_allow_html=True)
        cols = st.columns(2)
        for i, (title, prompt) in enumerate(suggestions):
            with cols[i % 2]:
                if st.button(title, key=f"__sug_{i}", use_container_width=True):
                    st.session_state.pend = prompt
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    else:
        # Conversation
        st.markdown('<div style="padding-top: 12px;">', unsafe_allow_html=True)
        for i, msg in enumerate(st.session_state.msgs):
            role    = msg["role"]
            content = msg["content"]
            ts      = msg.get("ts", "")
            module  = msg.get("module", "general")

            if role == "user":
                st.markdown(f"""
                <div class="msg-row-user">
                  <div class="msg-av user">{st.session_state.uini}</div>
                  <div class="msg-content" style="text-align:right">
                    <div class="msg-name" style="text-align:right">{st.session_state.uname} &nbsp;<span style="color:var(--text-dim);font-weight:400">{ts}</span></div>
                    <div class="msg-text-user">{content}</div>
                  </div>
                </div>""", unsafe_allow_html=True)
            else:
                mm  = {"jira":"mt-jira","hr":"mt-hr","data":"mt-data",
                       "rag":"mt-rag","helpdesk":"mt-help"}.get(module, "mt-ai")
                lbl = msg.get("lbl", "🧠 AI")
                st.markdown(f"""
                <div class="msg-wrap">
                  <div class="msg-av bot">🤖</div>
                  <div class="msg-content">
                    <div class="msg-name">SuperBot &nbsp;<span class="mod-tag {mm}">{lbl}</span></div>
                """, unsafe_allow_html=True)
                st.markdown(content)

                if msg.get("rag"):
                    st.markdown('<div class="src-row">', unsafe_allow_html=True)
                    for d in msg["rag"]:
                        src = d["metadata"].get("source","?")
                        rel = round(1 - d["distance"], 2)
                        st.markdown(f'<span class="src-pill">📄 {src[:24]} · {rel}</span>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)

                if msg.get("mcp"):
                    st.markdown('<div class="mcp-row">', unsafe_allow_html=True)
                    for t in msg["mcp"]:
                        st.markdown(f'<span class="mcp-tag">⚡ {t}</span>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)

                st.markdown('</div></div>', unsafe_allow_html=True)

                # Feedback
                fb1, fb2, _ = st.columns([1, 1, 14])
                with fb1:
                    if st.button("👍", key=f"__up_{i}", help="Helpful"):
                        dbx("INSERT INTO feedback(message_id,user_name,rating,comment,timestamp)VALUES(?,?,1,'',?)",
                            (i, st.session_state.uname, datetime.now().isoformat()))
                        st.toast("Thanks!", icon="✅")
                with fb2:
                    if st.button("👎", key=f"__dn_{i}", help="Not helpful"):
                        dbx("INSERT INTO feedback(message_id,user_name,rating,comment,timestamp)VALUES(?,?,-1,'',?)",
                            (i, st.session_state.uname, datetime.now().isoformat()))
                        st.toast("Noted!", icon="📝")

        st.markdown('</div>', unsafe_allow_html=True)

    # Chat input — always visible
    pend  = st.session_state.pop("pend", None)
    inp   = st.chat_input("Message SuperBot…")
    query = inp or pend

    if query and ok:
        ts_now = datetime.now().strftime("%H:%M")
        st.session_state.msgs.append({"role":"user","content":query,"ts":ts_now})
        save_conv("user", query, "input")
        audit("chat_query", "chat", query[:80])

        with st.spinner(""):
            t0   = time.time()
            hist = [{"role":x["role"],"content":x["content"]}
                    for x in st.session_state.msgs[:-1][-8:]]
            try:
                res = process_q(query, hist, {"name": st.session_state.uname})
            except Exception as e:
                res = {"intent":"ERR","module":"general","label":"⚠️ Error",
                       "answer":f"Something went wrong: `{e}`","data":None,"rag_docs":[]}
            ms = int((time.time()-t0)*1000)

        rm     = res.get("module","general")
        rl     = res.get("label","🧠 AI")
        intent = res.get("intent","")
        mcp_used = []
        if "JIRA"    in intent: mcp_used.append("jira_create" if "CREATE" in intent else "jira_update")
        if "DATA"    in intent: mcp_used.append("sql_query")
        if "HR"      in intent: mcp_used.append("hr_lookup")
        if "HELPDESK"in intent: mcp_used.append("helpdesk_create")
        if res.get("rag_docs"): mcp_used.append("doc_search")
        for t in mcp_used:
            dbx("UPDATE mcp_tools SET call_count=call_count+1 WHERE tool_name=?", (t,))

        st.session_state.msgs.append({
            "role":"assistant","content":res["answer"],
            "module":rm,"lbl":rl,"ts":ts_now,
            "rag":res.get("rag_docs",[]),"mcp":mcp_used,
        })
        save_conv("assistant", res["answer"], rm)
        log_usage(rm, intent, len(query), ms)
        st.session_state.qcnt += 1
        st.rerun()

# ── JIRA ────────────────────────────────────────────────────
elif mod == "jira":
    import pandas as pd
    from backend.jira_handler import get_issues, get_summary, get_sprint_board

    st.markdown('<div style="padding:24px 32px;max-width:1100px">', unsafe_allow_html=True)
    st.markdown("## 🎫 Jira Issues")

    js = get_summary()
    c1,c2,c3,c4 = st.columns(4)
    for col,(v,l,c) in zip([c1,c2,c3,c4],[
        (js["total"],"Total Issues","#3b82f6"),(js["open"],"Open","#f59e0b"),
        (js["bugs"],"Open Bugs","#ef4444"),(js["critical"],"Critical","#dc2626")]):
        with col:
            st.markdown(f'<div class="stat-box"><div class="stat-num" style="color:{c}">{v}</div><div class="stat-lbl">{l}</div></div>',unsafe_allow_html=True)

    st.markdown("<br>",unsafe_allow_html=True)
    jt1,jt2,jt3 = st.tabs(["All Issues","Sprint Board","Create Issue"])

    with jt1:
        fc = st.columns(5)
        with fc[0]: fp  = st.selectbox("Project", ["All","ACME","DATA","BI","INFRA","HR"], label_visibility="collapsed")
        with fc[1]: fs  = st.selectbox("Status",  ["All","OPEN","IN PROGRESS","IN REVIEW","DONE","BLOCKED"], label_visibility="collapsed")
        with fc[2]: ft  = st.selectbox("Type",    ["All","Story","Task","Subtask","Bug","Epic"], label_visibility="collapsed")
        with fc[3]: fpr = st.selectbox("Priority",["All","CRITICAL","HIGH","MEDIUM","LOW"], label_visibility="collapsed")
        with fc[4]: fa  = st.text_input("__fa","",placeholder="Assignee…",label_visibility="collapsed")
        filt = {}
        if fp!="All": filt["project"]=fp
        if fs!="All": filt["status"]=fs
        if ft!="All": filt["issue_type"]=ft
        if fpr!="All": filt["priority"]=fpr
        if fa: filt["assignee_name"]=fa
        issues = get_issues(filt)
        if issues:
            df = pd.DataFrame([{"Key":i["issue_key"],"Title":i.get("title","")[:50],
                "Type":i["issue_type"],"Status":i["status"],"Priority":i["priority"],
                "Assignee":i.get("assignee_name","?") or "?",
                "Sprint":i.get("sprint",""),"Pts":i.get("story_points","")} for i in issues])
            st.dataframe(df, use_container_width=True, hide_index=True)
        else: st.markdown('<p style="color:var(--text-muted)">No issues match the current filters.</p>',unsafe_allow_html=True)

    with jt2:
        board = get_sprint_board("Sprint 42"); ilist = board.get("issues",[])
        statuses = ["TODO","OPEN","IN PROGRESS","IN REVIEW","DONE"]
        bcols = st.columns(len(statuses))
        type_cls = {"Story":"bc-s","Bug":"bc-b","Task":"bc-t","Epic":"bc-s","Subtask":"bc-t"}
        for col, status in zip(bcols, statuses):
            with col:
                grp = [x for x in ilist if x["status"]==status]
                pc_map = {"CRITICAL":"#ef4444","HIGH":"#f59e0b","MEDIUM":"#3b82f6","LOW":"#22c55e"}
                st.markdown(f'<div class="board-col"><div class="board-col-hdr">{status} ({len(grp)})</div>',unsafe_allow_html=True)
                for i in grp[:4]:
                    pc = pc_map.get(i.get("priority",""),"#6b7280")
                    tc = type_cls.get(i.get("issue_type","Task"),"bc-t")
                    st.markdown(f"""<div class="board-card" style="border-left-color:{pc}">
                      <div class="bc-key">{i['issue_key']}</div>
                      <div class="bc-title">{i.get('title','')[:46]}</div>
                      <div class="bc-meta"><span class="bc-type {tc}">{i.get('issue_type','?')}</span>
                        <span style="font-size:10px;color:var(--text-dim);margin-left:auto">{i.get('story_points') or '?'}pts</span></div>
                    </div>""",unsafe_allow_html=True)
                st.markdown('</div>',unsafe_allow_html=True)

    with jt3:
        cfc = st.columns(2)
        with cfc[0]:
            jtitle  = st.text_input("Title *", placeholder="Brief description of the issue")
            jtype   = st.selectbox("Issue Type", ["Story","Bug","Task","Subtask","Epic"])
            jproj   = st.selectbox("Project", ["ACME","DATA","BI","INFRA","HR"])
            jpri    = st.selectbox("Priority", ["MEDIUM","HIGH","CRITICAL","LOW"])
        with cfc[1]:
            jdesc   = st.text_area("Description", height=110, placeholder="Detailed description…")
            jassign = st.text_input("Assignee", placeholder="e.g. Priya Sharma")
            jpts    = st.number_input("Story Points", 0, 21, 3)
        jnl = st.text_input("__jnl","",placeholder='Or natural language: "Create HIGH bug for login crash on Safari, assign to Arjun, 5 points"',label_visibility="collapsed")
        if st.button("🚀 Create Issue", type="primary"):
            pq = jnl if jnl else (
                f"Create a {jtype} titled '{jtitle}' in {jproj} with {jpri} priority."
                + (f" {jdesc}" if jdesc else "")
                + (f" Assign to {jassign}." if jassign else "")
                + f" {jpts} story points."
            )
            if jtitle.strip() or jnl.strip():
                st.session_state.pend = pq; st.session_state.mod="chat"; st.rerun()
            else: st.warning("Please enter a title or describe the issue.")

    st.markdown('</div>',unsafe_allow_html=True)

# ── HR ───────────────────────────────────────────────────────
elif mod == "hr":
    import pandas as pd
    from backend.hr_handler import search_employees, get_leave_requests, get_announcements, get_leave_balance

    st.markdown('<div style="padding:24px 32px;max-width:1100px">',unsafe_allow_html=True)
    st.markdown("## 👔 HR & Leave")
    ht1,ht2,ht3,ht4 = st.tabs(["Policy Q&A","Leave","Directory","Announcements"])

    with ht1:
        st.markdown("#### Ask HR Policy Questions")
        topics = [("🏖️ Annual Leave","What is the annual leave policy and how many days per year?"),
                  ("🤒 Sick Leave","What are the sick leave rules? When is a medical certificate required?"),
                  ("🏠 Work From Home","What is the WFH policy and how many days per week?"),
                  ("💰 Expenses","What are the expense reimbursement limits and process?"),
                  ("👶 Parental Leave","Explain maternity and paternity leave entitlements"),
                  ("📈 Performance","How does the performance review process work?"),
                  ("🛡️ Code of Conduct","What are the key code of conduct and ethics rules?"),
                  ("💼 Salary & Benefits","Explain CTC structure, PF, insurance and ESOP benefits")]
        c1,c2 = st.columns(2)
        for i,(lbl,pq) in enumerate(topics):
            with(c1 if i%2==0 else c2):
                if st.button(lbl,key=f"__hrp_{i}",use_container_width=True):
                    st.session_state.pend=pq; st.session_state.mod="chat"; st.rerun()

    with ht2:
        lc1,lc2 = st.columns(2)
        with lc1:
            st.markdown("**Leave Requests**")
            for r in get_leave_requests()[:5]:
                sc = {"APPROVED":"#19c37d","PENDING":"#f59e0b","REJECTED":"#ef4444"}.get(r["status"],"#6b7280")
                st.markdown(f"""<div class="doc-row" style="border-left:3px solid {sc}">
                  <div><div class="doc-name">{r.get('full_name','?')}</div>
                  <div class="doc-meta">{r['leave_type']} · {r['start_date']} → {r['end_date']} ({r['days']}d)</div></div>
                  <span style="font-size:11px;font-weight:600;color:{sc}">{r['status']}</span></div>""",unsafe_allow_html=True)
        with lc2:
            st.markdown("**Leave Balance (Priya)**")
            emps = search_employees(name="priya")
            if emps:
                for b in get_leave_balance(emps[0]["emp_id"]):
                    pct = int(b["used"]/b["allocated"]*100) if b["allocated"] else 0
                    st.markdown(f"""
                    <div style="background:rgba(255,255,255,.04);border:1px solid var(--border);border-radius:var(--r);padding:12px 14px;margin:5px 0">
                      <div style="display:flex;justify-content:space-between;margin-bottom:6px">
                        <span style="font-size:13px;font-weight:500;color:var(--text)">{b['leave_type']}</span>
                        <span style="font-size:13px;font-weight:700;color:#19c37d">{b['remaining']} left</span></div>
                      <div class="lbar-wrap"><div class="lbar-fill" style="width:{pct}%"></div></div>
                      <div style="font-size:10px;color:var(--text-dim);margin-top:3px">{b['used']} / {b['allocated']} used</div>
                    </div>""",unsafe_allow_html=True)

    with ht3:
        srch = st.text_input("__drsrch","",placeholder="Search name, department, location…",label_visibility="collapsed")
        emps = search_employees(name=srch if srch else None)
        if emps:
            df = pd.DataFrame([{"Name":e["full_name"],"Role":e["job_title"],"Dept":e["department"],
                "Location":e["location"],"Email":e["email"],"Slack":e["slack_handle"]} for e in emps])
            st.dataframe(df,use_container_width=True,hide_index=True)

    with ht4:
        for a in get_announcements():
            cc = {"Company":"#7c3aed","HR":"#19c37d","Tech":"#3b82f6","IT":"#f59e0b"}.get(a["category"],"#6b7280")
            st.markdown(f"""<div class="ann-card" style="border-left-color:{cc}">
              <div style="display:flex;justify-content:space-between;margin-bottom:6px">
                <div class="ann-title">{'📌 ' if a.get('pinned') else ''}{a['title']}</div>
                <span style="font-size:10px;font-weight:600;color:{cc};padding:2px 8px;background:{cc}22;border-radius:4px">{a['category']}</span></div>
              <div class="ann-body">{a['body'][:200]}</div>
              <div class="ann-footer">📢 {a['author']} · {a['posted_date']}</div>
            </div>""",unsafe_allow_html=True)

    st.markdown('</div>',unsafe_allow_html=True)

# ── DATA ─────────────────────────────────────────────────────
elif mod == "data":
    import pandas as pd
    from backend.data_handler import list_all_tables, get_pipeline_status, get_quality_checks

    st.markdown('<div style="padding:24px 32px;max-width:1100px">',unsafe_allow_html=True)
    st.markdown("## 📊 Data & SQL")

    tbls  = list_all_tables(); pipes = get_pipeline_status(); qual = get_quality_checks()
    total_r = sum(int(t.get("row_count") or 0) for t in tbls["tables"])
    fp = pipes["failed_count"]; qf = qual["summary"].get("FAIL",0)

    c1,c2,c3,c4 = st.columns(4)
    for col,(v,l,c) in zip([c1,c2,c3,c4],[
        (tbls["count"],"DW Tables","#3b82f6"),(f"{total_r/1e6:.1f}M","Total Rows","#8b5cf6"),
        (fp,"Failed Pipelines","#ef4444" if fp else "#19c37d"),
        (qf,"Quality Fails","#ef4444" if qf else "#19c37d")]):
        with col:
            st.markdown(f'<div class="stat-box"><div class="stat-num" style="color:{c}">{v}</div><div class="stat-lbl">{l}</div></div>',unsafe_allow_html=True)

    st.markdown("<br>",unsafe_allow_html=True)
    dt1,dt2,dt3,dt4 = st.tabs(["Tables","Pipelines","Data Quality","SQL Generator"])

    with dt1:
        if tbls["tables"]:
            df = pd.DataFrame([{"Schema":t["table_schema"],"Table":t["table_name"],"Type":t["table_type"],
                "Rows":f"{int(t.get('row_count') or 0):,}","Size MB":t.get("size_mb",0),"Owner":t.get("owner_team","")} for t in tbls["tables"]])
            st.dataframe(df,use_container_width=True,hide_index=True)

    with dt2:
        for r in pipes["runs"]:
            c  = {"SUCCESS":"#19c37d","FAILED":"#ef4444","RUNNING":"#f59e0b"}.get(r["status"],"#6b7280")
            ic = {"SUCCESS":"✅","FAILED":"❌","RUNNING":"🔄"}.get(r["status"],"❓")
            st.markdown(f"""<div class="doc-row" style="border-left:3px solid {c}">
              <div><div class="doc-name">{ic} {r['pipeline_name']}</div>
              <div class="doc-meta">{r.get('start_time','')[:16]} · {f"{int(r.get('rows_processed') or 0):,} rows"}
              {'  ⚠️ '+str(r.get('error_message','')) if r.get('error_message') else ''}</div></div>
              <span style="font-size:11px;font-weight:600;color:{c}">{r['status']}</span></div>""",unsafe_allow_html=True)

    with dt3:
        s = qual["summary"]
        c1_,c2_,c3_ = st.columns(3)
        with c1_: st.markdown(f'<div class="stat-box"><div class="stat-num" style="color:#19c37d">{s.get("PASS",0)}</div><div class="stat-lbl">✅ Passed</div></div>',unsafe_allow_html=True)
        with c2_: st.markdown(f'<div class="stat-box"><div class="stat-num" style="color:#f59e0b">{s.get("WARN",0)}</div><div class="stat-lbl">⚠️ Warnings</div></div>',unsafe_allow_html=True)
        with c3_: st.markdown(f'<div class="stat-box"><div class="stat-num" style="color:#ef4444">{s.get("FAIL",0)}</div><div class="stat-lbl">❌ Failed</div></div>',unsafe_allow_html=True)
        if qual["checks"]:
            st.markdown("<br>",unsafe_allow_html=True)
            df = pd.DataFrame([{"Schema":c["table_schema"],"Table":c["table_name"],
                "Column":c["column_name"],"Check":c["check_type"],"Status":c["check_status"]} for c in qual["checks"]])
            st.dataframe(df,use_container_width=True,hide_index=True)

    with dt4:
        st.markdown("**Quick SQL prompts — click to generate:**")
        sq_qs = ["Write SQL for top 10 customers by total revenue",
                 "Generate daily sales trend for last 30 days",
                 "Find duplicate customer email addresses",
                 "Monthly revenue breakdown by region",
                 "Show orders from June 2024 with DELIVERED status",
                 "Count total records and unique customers per table"]
        sc_ = st.columns(2)
        for i,p in enumerate(sq_qs):
            with sc_[i%2]:
                if st.button(p,key=f"__sql_{i}",use_container_width=True):
                    st.session_state.pend=p; st.session_state.mod="chat"; st.rerun()

        st.markdown("<br>",unsafe_allow_html=True)
        cq = st.text_input("__cq","",placeholder="Describe what SQL you need…",label_visibility="collapsed")
        if st.button("⚡ Generate SQL",type="primary") and cq.strip():
            st.session_state.pend=cq; st.session_state.mod="chat"; st.rerun()

    st.markdown('</div>',unsafe_allow_html=True)

# ── KNOWLEDGE BASE ───────────────────────────────────────────
elif mod == "kb":
    from backend.rag_handler import get_indexed_sources, add_pdf, delete_source

    st.markdown('<div style="padding:24px 32px;max-width:1100px">',unsafe_allow_html=True)
    st.markdown("## 📚 Knowledge Base")

    kbc1,kbc2 = st.columns([3,2])
    with kbc1:
        st.markdown("#### Upload Documents")
        st.markdown('<p style="color:var(--text-muted);font-size:13px;margin-bottom:12px">Upload HR policies, manuals, or any document. SuperBot will answer questions with source citations.</p>',unsafe_allow_html=True)
        ups = st.file_uploader("Drop files here",type=["pdf","txt","docx"],
                               accept_multiple_files=True,label_visibility="collapsed")
        if ups:
            for f in ups:
                with st.spinner(f"Indexing {f.name}…"):
                    raw=f.read(); n=add_pdf(raw,f.name,"Uploaded Document")
                if n>0:
                    dbx("INSERT OR IGNORE INTO documents(filename,file_type,file_size,uploaded_by,uploaded_at,chunk_count,status)VALUES(?,?,?,?,?,?,'indexed')",
                        (f.name,f.name.split(".")[-1],len(raw),st.session_state.uname,datetime.now().isoformat(),n))
                    audit("doc_upload","kb",f.name)
                    st.success(f"✅ {f.name} — {n} chunks indexed")
                else: st.warning(f"⚠️ Could not index {f.name}")

        st.markdown("#### Indexed Documents")
        sources = get_indexed_sources()
        builtin_names = {"HR Policy Manual","Onboarding Guide","Compensation Guide","IT Policy Manual"}
        for s in sources:
            if s["source"] == "internal": continue
            is_builtin = s["source"] in builtin_names
            c1_,c2_ = st.columns([5,1])
            with c1_:
                st.markdown(f"""<div class="doc-row">
                  <div style="display:flex;align-items:center;gap:10px">
                    <span style="font-size:18px">{'📋' if is_builtin else '📄'}</span>
                    <div><div class="doc-name">{s['source']}</div>
                    <div class="doc-meta">{s['chunks']} chunks · {'Always available' if is_builtin else 'Uploaded'}</div></div>
                  </div>
                  <span class="doc-badge">{'BUILT-IN' if is_builtin else 'INDEXED'}</span>
                </div>""",unsafe_allow_html=True)
            with c2_:
                if not is_builtin:
                    if st.button("🗑️",key=f"__del_{s['source'][:8]}",help="Remove"):
                        delete_source(s["source"]); dbx("DELETE FROM documents WHERE filename=?",(s["source"],)); st.rerun()

    with kbc2:
        st.markdown("#### Ask a Question")
        kbq = st.text_input("__kbq","",placeholder="Ask about your documents…",label_visibility="collapsed")
        if st.button("🔍 Search",type="primary",use_container_width=True) and kbq.strip():
            st.session_state.pend=kbq; st.session_state.mod="chat"; st.rerun()

        st.markdown("<br>#### Example Questions")
        for e in ["WFH policy rules?","Annual leave days?","Expense claim limit?",
                  "Performance review process?","Password policy?","Onboarding checklist?"]:
            if st.button(e,key=f"__kbe_{e[:12]}",use_container_width=True):
                st.session_state.pend=e; st.session_state.mod="chat"; st.rerun()

        st.markdown("<br>")
        total_ch = sum(s["chunks"] for s in sources)
        st.markdown(f"""
        <div style="background:rgba(255,255,255,.04);border:1px solid var(--border);border-radius:var(--r);padding:14px 16px">
          <div class="set-row" style="padding:6px 0"><span class="set-label" style="font-size:13px">Documents</span><span class="set-val">{len([s for s in sources if s['source']!='internal'])}</span></div>
          <div class="set-row" style="padding:6px 0"><span class="set-label" style="font-size:13px">Total Chunks</span><span class="set-val">{total_ch:,}</span></div>
          <div class="set-row" style="padding:6px 0;border:none"><span class="set-label" style="font-size:13px">Vector Store</span><span style="color:#19c37d;font-size:13px;font-weight:600">NumPy RAG ✅</span></div>
        </div>""",unsafe_allow_html=True)

    st.markdown('</div>',unsafe_allow_html=True)

# ── HELPDESK ─────────────────────────────────────────────────
elif mod == "helpdesk":
    import pandas as pd
    from backend.hr_handler import get_helpdesk_tickets

    st.markdown('<div style="padding:24px 32px;max-width:1100px">',unsafe_allow_html=True)
    st.markdown("## 🔧 IT Helpdesk")

    tix = get_helpdesk_tickets()
    ot=len([t for t in tix if t["status"]=="OPEN"])
    pt=len([t for t in tix if t["status"]=="IN PROGRESS"])
    dt=len([t for t in tix if t["status"]=="RESOLVED"])
    c1,c2,c3 = st.columns(3)
    for col,(v,l,c) in zip([c1,c2,c3],[(ot,"Open","#ef4444"),(pt,"In Progress","#f59e0b"),(dt,"Resolved","#19c37d")]):
        with col:
            st.markdown(f'<div class="stat-box"><div class="stat-num" style="color:{c}">{v}</div><div class="stat-lbl">{l}</div></div>',unsafe_allow_html=True)

    st.markdown("<br>",unsafe_allow_html=True)
    hc1,hc2 = st.columns([3,2])
    with hc1:
        st.markdown("**All Tickets**")
        if tix:
            df = pd.DataFrame([{"Ticket":t["ticket_id"],"Title":t["title"][:44],"Category":t["category"],
                "Priority":t["priority"],"Status":t["status"],"By":t["raised_by"],"Date":t["created_date"]} for t in tix])
            st.dataframe(df,use_container_width=True,hide_index=True)
    with hc2:
        st.markdown("**Raise via Chat**")
        st.markdown('<p style="color:var(--text-muted);font-size:13px;margin-bottom:10px">Describe your IT issue and SuperBot creates a ticket automatically.</p>',unsafe_allow_html=True)
        for p in ["Laptop running very slow, needs more RAM","VPN keeps disconnecting every 30 minutes",
                  "Can't access Jira — getting 403 error","Need Adobe Acrobat Pro license",
                  "Wi-Fi dropping in conference room B"]:
            if st.button(p[:44]+"…",key=f"__hd_{p[:7]}",use_container_width=True):
                st.session_state.pend=f"Raise IT helpdesk ticket: {p}"; st.session_state.mod="chat"; st.rerun()

    st.markdown('</div>',unsafe_allow_html=True)

# ── ADMIN ────────────────────────────────────────────────────
elif mod == "admin":
    import pandas as pd

    st.markdown('<div style="padding:24px 32px;max-width:1100px">',unsafe_allow_html=True)
    st.markdown("## ⚙️ Admin Panel")

    at1,at2,at3,at4,at5 = st.tabs(["Analytics","MCP Tools","Audit Log","Chat History","Alerts"])

    with at1:
        by_mod = dbq("SELECT module,COUNT(*) as count FROM usage_analytics GROUP BY module ORDER BY count DESC")
        by_day = dbq("SELECT date,COUNT(*) as count FROM usage_analytics GROUP BY date ORDER BY date DESC LIMIT 7")
        total_q2 = sum(r["count"] for r in by_mod)
        fb_pos = len(dbq("SELECT id FROM feedback WHERE rating>0"))
        fb_neg = len(dbq("SELECT id FROM feedback WHERE rating<0"))
        sat = round(fb_pos/(fb_pos+fb_neg)*100) if fb_pos+fb_neg else 0
        c1,c2,c3,c4 = st.columns(4)
        with c1: st.metric("Total Queries",total_q2)
        with c2: st.metric("Positive Feedback",fb_pos)
        with c3: st.metric("Negative Feedback",fb_neg)
        with c4: st.metric("Satisfaction",f"{sat}%")
        ac1_,ac2_ = st.columns(2)
        with ac1_:
            st.markdown("**Queries by Module**")
            if by_mod:
                df_m=pd.DataFrame(by_mod); st.bar_chart(df_m.set_index("module")["count"])
        with ac2_:
            st.markdown("**Daily Volume (7 days)**")
            if by_day:
                df_d=pd.DataFrame(by_day); st.bar_chart(df_d.set_index("date")["count"])

    with at2:
        tools=dbq("SELECT * FROM mcp_tools ORDER BY call_count DESC")
        mc={"data":"#3b82f6","jira":"#0052cc","hr":"#19c37d","rag":"#f59e0b","helpdesk":"#f97316","system":"#8b5cf6"}
        for t in tools:
            tc=mc.get(t["module"],"#6b7280")
            st.markdown(f"""<div class="tool-row" style="border-left-color:{tc}">
              <div><div class="tool-name">⚡ {t['tool_name']}</div><div class="tool-desc">{t['description']}</div>
              <span style="font-size:10px;padding:1px 7px;border-radius:3px;background:{tc}22;color:{tc};font-weight:600;margin-top:4px;display:inline-block">{t['module'].upper()}</span></div>
              <div style="text-align:right;padding-left:16px">
                <div class="tool-calls">{t['call_count']:,}</div><div class="tool-calls-lbl">calls</div>
                <div class="tool-status" style="color:{'#19c37d' if t['enabled'] else '#ef4444'}">{'● Active' if t['enabled'] else '○ Off'}</div></div>
            </div>""",unsafe_allow_html=True)

    with at3:
        logs=dbq("SELECT * FROM audit_logs ORDER BY timestamp DESC LIMIT 100")
        if logs:
            df_l=pd.DataFrame([{"Time":l["timestamp"][:16],"User":l["user_name"],
                "Action":l["action"],"Module":l["module"],"Details":l["details"][:60]} for l in logs])
            st.dataframe(df_l,use_container_width=True,hide_index=True)
        else: st.markdown('<p style="color:var(--text-muted)">Audit log activates after first chat interactions.</p>',unsafe_allow_html=True)

    with at4:
        sessions=dbq("SELECT session_id,user_name,MIN(timestamp) as started,COUNT(*) as msgs FROM conversation_history GROUP BY session_id ORDER BY started DESC LIMIT 20")
        if sessions:
            for s in sessions[:5]:
                with st.expander(f"💬 {s['user_name']} — {s['started'][:16]} ({s['msgs']} messages)"):
                    conv=dbq("SELECT role,content,module,timestamp FROM conversation_history WHERE session_id=? ORDER BY timestamp",(s["session_id"],))
                    for cm in conv:
                        ic2="👤" if cm["role"]=="user" else "🤖"
                        st.markdown(f"**{ic2} {cm['role'].title()}** `{cm['timestamp'][:16]}` `{cm['module']}`")
                        st.caption(cm["content"][:200])
        else: st.markdown('<p style="color:var(--text-muted)">No history yet.</p>',unsafe_allow_html=True)

    with at5:
        all_al=dbq("SELECT * FROM alerts ORDER BY created_at DESC")
        for a in all_al:
            sc2={"critical":"#ef4444","warning":"#f59e0b","info":"#3b82f6"}.get(a["severity"],"#6b7280")
            ic2={"critical":"🚨","warning":"⚠️","info":"ℹ️"}.get(a["severity"],"❓")
            st.markdown(f"""<div class="doc-row" style="border-left:3px solid {sc2}">
              <div><div class="doc-name">{ic2} {a['title']}</div>
              <div class="doc-meta">{a['message'][:80]}</div>
              <div class="doc-meta">{a['created_at'][:16]}</div></div>
              <span style="font-size:11px;font-weight:600;color:{'#19c37d' if a['is_read'] else '#ef4444'}">{'✅ Read' if a['is_read'] else '🔴 Unread'}</span>
            </div>""",unsafe_allow_html=True)
            if not a["is_read"]:
                if st.button("Mark Read",key=f"__mr_{a['id']}"):
                    dbx("UPDATE alerts SET is_read=1 WHERE id=?",(a["id"],)); st.rerun()

    st.markdown('</div>',unsafe_allow_html=True)

# ── SETTINGS ─────────────────────────────────────────────────
elif mod == "settings":
    from config.settings import GROQ_API_KEY, GROQ_MODEL, LLM_BACKEND
    from backend.rag_handler import get_indexed_sources

    st.markdown('<div style="padding:24px 32px;max-width:800px">',unsafe_allow_html=True)
    st.markdown("## 🔧 Settings")

    st.markdown("#### Profile")
    nn = st.text_input("Display Name", value=st.session_state.uname)
    ni = st.text_input("Initials (2–3 chars)", value=st.session_state.uini, max_chars=3)
    if st.button("💾 Save", type="primary"):
        st.session_state.uname=nn; st.session_state.uini=ni.upper(); st.success("Saved!")

    st.markdown("<br>#### AI Configuration")
    st.markdown(f"""<div style="background:rgba(255,255,255,.04);border:1px solid var(--border);border-radius:var(--r);padding:16px">
      <div class="set-row"><span class="set-label">LLM Backend</span><code style="color:#e5c07b">{LLM_BACKEND}</code></div>
      <div class="set-row"><span class="set-label">Model</span><code style="color:#e5c07b">{GROQ_MODEL}</code></div>
      <div class="set-row"><span class="set-label">API Key</span><span style="color:{'#19c37d' if GROQ_API_KEY else '#ef4444'};font-weight:600">{'✅ Configured' if GROQ_API_KEY else '❌ Missing — add to .env'}</span></div>
    </div>""",unsafe_allow_html=True)

    st.markdown("<br>#### Integrations")
    intgs=[("Jira (Mock)",True,"#19c37d"),("Azure Synapse",True,"#19c37d"),
           ("Groq LLM",bool(GROQ_API_KEY),"#19c37d"),
           ("NumPy RAG Store",True,"#19c37d"),("MS Teams",False,""),
           ("Slack",False,""),("Power BI",False,""),("SSO / RBAC",False,"")]
    st.markdown('<div style="background:rgba(255,255,255,.04);border:1px solid var(--border);border-radius:var(--r);padding:16px">',unsafe_allow_html=True)
    for name,connected,_ in intgs:
        c_c = "#19c37d" if connected else "#6b7280"
        st.markdown(f"""<div class="int-row">
          <div style="display:flex;align-items:center;gap:10px">
            <div class="int-dot" style="background:{c_c}"></div>
            <span class="int-name">{name}</span></div>
          <span style="font-size:12px;font-weight:600;color:{c_c}">{'Connected' if connected else 'Not connected'}</span>
        </div>""",unsafe_allow_html=True)
    st.markdown('</div>',unsafe_allow_html=True)

    st.markdown("<br>#### Actions")
    c1_,c2_,c3_ = st.columns(3)
    with c1_:
        if st.button("🗑️ Clear Chat",use_container_width=True):
            st.session_state.msgs=[]; st.session_state.sid=str(uuid.uuid4()); st.success("Cleared")
    with c2_:
        if st.button("📥 Export Chat",use_container_width=True):
            conv=dbq("SELECT role,content,module,timestamp FROM conversation_history WHERE session_id=? ORDER BY timestamp",(st.session_state.sid,))
            if conv:
                txt="\n\n".join(f"[{m['timestamp'][:16]}] {m['role'].upper()}\n{m['content']}" for m in conv)
                st.download_button("💾 Download",txt,f"superbot_{st.session_state.sid[:8]}.txt","text/plain")
            else: st.info("No conversation yet.")
    with c3_:
        if st.button("🔄 Rebuild Index",use_container_width=True):
            with st.spinner("Rebuilding…"):
                try:
                    from backend.rag_handler import init
                    idx=os.path.join(os.path.dirname(__file__),"data/rag_index.pkl")
                    if os.path.exists(idx): os.remove(idx)
                    init(); st.success("Done!")
                except Exception as e: st.error(str(e))

    st.markdown('</div>',unsafe_allow_html=True)
