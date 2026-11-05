import pandas as pd
import pymysql

PASSWORD = "MY_PASSWORD_HERE"

conn = pymysql.connect(
	host="localhost",
	user="root",
	password=PASSWORD,
	database="saas_analytics",
	charset="utf8mb4",
)
cur = conn.cursor()

path = "Data/"
# Parent tables first, then the tables that depend on them
order = ["plans", "accounts", "users", "subscriptions", "invoices", "churn_events"]

for table in order:
	df = pd.read_csv(f"{path}{table}.csv")
	df = df.astype(object).where(df.notna(), None)   # empty cells become NULL

	columns = ", ".join(f"`{c}`" for c in df.columns)
	placeholders = ", ".join(["%s"] * len(df.columns))
	sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"

	rows = df.values.tolist()
	for i in range(0, len(rows), 5000):
		cur.executemany(sql, rows[i:i + 5000])
	conn.commit()
	print(f"Loaded {table}: {len(rows)} rows")

cur.close()
conn.close()
print("Done!")
