import os, sys, re
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config.settings import (
    LLM_BACKEND, LLM_TEMPERATURE, LLM_MAX_TOKENS,
    GROQ_API_KEY, GROQ_MODEL, COMPANY_NAME
)

SYSTEM_PROMPT = f"""You are SuperBot, the intelligent enterprise AI assistant for {COMPANY_NAME}.
You help employees with HR policies, Jira tracking, data analytics, IT support, and general questions.
Be concise, helpful, and professional. Use the context provided to give accurate answers.
When context is from HR documents, quote the relevant policy sections precisely.
When writing SQL, use proper T-SQL/Azure Synapse syntax."""

def _call_groq(messages, temperature=None, max_tokens=None):
    """Call Groq API - tries groq package first, then requests HTTP."""
    temp = temperature or LLM_TEMPERATURE
    mtok = max_tokens or LLM_MAX_TOKENS
    # Try groq package
    try:
        from groq import Groq
        resp = Groq(api_key=GROQ_API_KEY).chat.completions.create(
            model=GROQ_MODEL, messages=messages, temperature=temp, max_tokens=mtok)
        return resp.choices[0].message.content
    except ImportError:
        pass
    # Try requests HTTP
    try:
        import requests, json
        resp = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
            json={"model": GROQ_MODEL, "messages": messages, "temperature": temp, "max_tokens": mtok},
            timeout=15
        )
        if resp.status_code == 200:
            return resp.json()["choices"][0]["message"]["content"]
    except:
        pass
    return None

def call_llm(user_query: str, context: str = "", chat_history: list = None, system_override: str = None) -> str:
    messages = [{"role": "system", "content": system_override or SYSTEM_PROMPT}]
    if chat_history:
        for m in chat_history[-6:]:
            messages.append({"role": m["role"], "content": m["content"]})
    content = f"{context}\n\nUser: {user_query}" if context else user_query
    messages.append({"role": "user", "content": content})
    if LLM_BACKEND == "groq" and GROQ_API_KEY:
        result = _call_groq(messages)
        if result:
            return result
    return _mock(user_query)

def _mock(q):
    return (f"🤖 **[Mock Response]** I received: *\"{q[:80]}\"*\n\n"
            "Install `groq` package and add `GROQ_API_KEY` to `.env` for real AI-powered answers.\n"
            "Get a free key at https://console.groq.com")

def generate_sql(schema: str, request: str) -> str:
    """Generate SQL — tries LLM first, falls back to smart templates."""
    sys_p = "You are a SQL expert. Generate ONLY clean T-SQL with inline comments. No explanation outside code."
    msgs = [{"role":"system","content":sys_p},
            {"role":"user","content":f"Schema:\n{schema}\n\nGenerate SQL for: {request}"}]
    if LLM_BACKEND == "groq" and GROQ_API_KEY:
        result = _call_groq(msgs, temperature=0.1, max_tokens=600)
        if result:
            return result
    return _smart_sql(request, schema)

def _smart_sql(request: str, schema: str = "") -> str:
    """Generate intelligent SQL from natural language without an LLM."""
    q = request.lower()

    # Extract table from schema hint
    table = "sales.fact_orders"
    m = re.search(r'Table:\s*(\S+)', schema)
    if m: table = m.group(1)

    # TOP N customers by revenue
    if any(x in q for x in ["top", "highest", "largest", "best"]):
        n = re.search(r'\b(\d+)\b', q); n = n.group(1) if n else "10"
        if "customer" in q and any(x in q for x in ["revenue", "sales", "amount", "spend"]):
            return f"""-- Top {n} customers by total revenue
SELECT TOP {n}
    customer_id,
    customer_name,
    SUM(order_amount)   AS total_revenue,
    COUNT(order_id)     AS total_orders,
    AVG(order_amount)   AS avg_order_value
FROM {table}
WHERE order_status != 'CANCELLED'
GROUP BY customer_id, customer_name
ORDER BY total_revenue DESC;"""
        if "product" in q:
            return f"""-- Top {n} products by revenue
SELECT TOP {n}
    product_id,
    product_name,
    product_category,
    SUM(quantity_sold)  AS units_sold,
    SUM(order_amount)   AS total_revenue
FROM {table}
GROUP BY product_id, product_name, product_category
ORDER BY total_revenue DESC;"""
        if "region" in q or "country" in q:
            return f"""-- Top {n} regions by revenue
SELECT TOP {n}
    region,
    country,
    SUM(order_amount)   AS total_revenue,
    COUNT(order_id)     AS total_orders
FROM {table}
GROUP BY region, country
ORDER BY total_revenue DESC;"""

    # Daily / monthly trend
    if any(x in q for x in ["daily", "trend", "over time"]):
        n = re.search(r'\b(\d+)\b', q); n = int(n.group(1)) if n else 30
        return f"""-- Daily sales trend (last {n} days)
SELECT
    CAST(order_date AS DATE)    AS order_day,
    COUNT(order_id)             AS total_orders,
    SUM(order_amount)           AS daily_revenue,
    AVG(order_amount)           AS avg_order_value,
    SUM(SUM(order_amount)) OVER (
        ORDER BY CAST(order_date AS DATE)
    )                           AS cumulative_revenue
FROM {table}
WHERE order_date >= DATEADD(DAY, -{n}, GETDATE())
GROUP BY CAST(order_date AS DATE)
ORDER BY order_day;"""

    if "month" in q and any(x in q for x in ["trend", "revenue", "sales"]):
        return f"""-- Monthly revenue trend
SELECT
    YEAR(order_date)                AS year,
    MONTH(order_date)               AS month_num,
    DATENAME(MONTH, order_date)     AS month_name,
    COUNT(order_id)                 AS total_orders,
    SUM(order_amount)               AS monthly_revenue,
    AVG(order_amount)               AS avg_order_value
FROM {table}
WHERE order_date >= DATEADD(MONTH, -12, GETDATE())
GROUP BY YEAR(order_date), MONTH(order_date), DATENAME(MONTH, order_date)
ORDER BY year, month_num;"""

    # Duplicate detection
    if "duplicate" in q:
        col = "email" if "email" in q else ("customer_id" if "customer" in q else "order_id")
        return f"""-- Find duplicate {col} values
SELECT
    {col},
    COUNT(*)        AS occurrences
FROM {table}
GROUP BY {col}
HAVING COUNT(*) > 1
ORDER BY occurrences DESC;"""

    # Null / missing
    if any(x in q for x in ["null", "missing", "empty", "blank"]):
        col = "email" if "email" in q else ("phone" if "phone" in q else "customer_id")
        return f"""-- Records with missing {col}
SELECT
    COUNT(*)                            AS total_records,
    SUM(CASE WHEN {col} IS NULL THEN 1 ELSE 0 END)  AS null_count,
    ROUND(
        100.0 * SUM(CASE WHEN {col} IS NULL THEN 1 ELSE 0 END) / COUNT(*), 2
    )                                   AS null_percentage
FROM {table};

-- View the actual records
SELECT *
FROM {table}
WHERE {col} IS NULL
   OR LTRIM(RTRIM(CAST({col} AS VARCHAR(MAX)))) = ''
ORDER BY created_date DESC;"""

    # Date filter
    for month_name, month_num in [("january","01"),("february","02"),("march","03"),("april","04"),
        ("may","05"),("june","06"),("july","07"),("august","08"),("september","09"),
        ("october","10"),("november","11"),("december","12")]:
        if month_name in q:
            year = re.search(r'\b(202[0-9])\b', q); year = year.group(1) if year else "2024"
            extra = "\n  AND order_status = 'DELIVERED'" if "delivered" in q else (
                    "\n  AND order_status = 'PENDING'" if "pending" in q else "")
            return f"""-- Orders in {month_name.title()} {year}
SELECT
    order_id,
    customer_id,
    customer_name,
    order_date,
    order_amount,
    order_status,
    product_category
FROM {table}
WHERE YEAR(order_date)  = {year}
  AND MONTH(order_date) = {month_num}{extra}
ORDER BY order_date DESC;"""

    # Revenue summary
    if any(x in q for x in ["revenue", "sales total", "total amount", "summary"]):
        return f"""-- Revenue summary dashboard
SELECT
    COUNT(order_id)             AS total_orders,
    SUM(order_amount)           AS total_revenue,
    AVG(order_amount)           AS avg_order_value,
    MIN(order_amount)           AS min_order,
    MAX(order_amount)           AS max_order,
    COUNT(DISTINCT customer_id) AS unique_customers
FROM {table}
WHERE order_date >= DATEADD(DAY, -30, GETDATE());

-- Breakdown by status
SELECT
    order_status,
    COUNT(*)            AS count,
    SUM(order_amount)   AS revenue
FROM {table}
GROUP BY order_status
ORDER BY revenue DESC;"""

    # Count
    if any(x in q for x in ["count", "how many", "total records", "number of"]):
        return f"""-- Record count summary
SELECT
    COUNT(*)                            AS total_rows,
    COUNT(DISTINCT customer_id)         AS unique_customers,
    COUNT(DISTINCT product_id)          AS unique_products,
    MIN(order_date)                     AS first_order_date,
    MAX(order_date)                     AS last_order_date
FROM {table};"""

    # Default
    return f"""-- Query results from {table}
SELECT TOP 100
    order_id,
    customer_id,
    customer_name,
    order_date,
    order_amount,
    order_status,
    product_category
FROM {table}
ORDER BY order_date DESC;"""
