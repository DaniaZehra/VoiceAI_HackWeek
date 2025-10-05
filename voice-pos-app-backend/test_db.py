import psycopg

url = "postgresql://postgres:tILHebFZFIqqlZcxmsFMgcxMcsRkTZfj@yamanote.proxy.rlwy.net:46383/railway?sslmode=require"

try:
    conn = psycopg.connect(url)
    cur = conn.cursor()
    cur.execute("SELECT 1;")
    print("Connected successfully:", cur.fetchone())
    conn.close()
except Exception as e:
    print("Error:", e)