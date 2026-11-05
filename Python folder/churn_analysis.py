import pandas as pd

path = "Data/"
tables = ["plans", "accounts", "users", "subscriptions", "invoices", "churn_events"]
dfs = {table: pd.read_csv(f"{path}{table}.csv") for table in tables}

for name, df in dfs.items():
	print(name, df.shape)
	print(df.dtypes, "\n")
	print(df.isna().sum(), "\n")
# ---------- INTEGRITY CHECKS ----------
print("\n" + "=" * 50)
print("INTEGRITY CHECKS (every number should be 0)")
print("=" * 50)

plans = dfs["plans"]
accounts = dfs["accounts"]
subs = dfs["subscriptions"]
invoices = dfs["invoices"]
churn = dfs["churn_events"]

# Turn text dates into real dates so we can compare them
subs["started_on"] = pd.to_datetime(subs["started_on"])
subs["ended_on"] = pd.to_datetime(subs["ended_on"])
churn["churned_on"] = pd.to_datetime(churn["churned_on"])
accounts["signup_date"] = pd.to_datetime(accounts["signup_date"])
invoices["issued_on"] = pd.to_datetime(invoices["issued_on"])
invoices["paid_on"] = pd.to_datetime(invoices["paid_on"])

# What status words exist? (so we know what to look for)
print("\nSubscription statuses:")
print(subs["status"].value_counts())

# Check 1: MRR = seats x plan price
merged = subs.merge(plans, on="plan_id")
bad = (merged["seats"] * merged["monthly_price"] != merged["mrr"]).sum()
print("\n1. MRR does not equal seats x price:", bad)

# Check 2: ended_on is filled in only for cancelled subscriptions
is_cancelled = subs["status"] == "cancelled"
bad = (subs["ended_on"].notna() != is_cancelled).sum()
print("2. ended_on does not match cancelled status:", bad)

# Check 3: every cancelled subscription has a churn event
cancelled_ids = subs.loc[is_cancelled, "subscription_id"]
bad = (~cancelled_ids.isin(churn["subscription_id"])).sum()
print("3. Cancelled subscriptions with no churn event:", bad)

# Check 4: churn date matches the subscription end date
joined = churn.merge(subs, on="subscription_id")
bad = (joined["churned_on"] != joined["ended_on"]).sum()
print("4. Churn date differs from end date:", bad)

# Check 5: invoice amount equals the subscription's MRR
inv = invoices.merge(subs[["subscription_id", "mrr"]], on="subscription_id")
bad = (inv["amount_due"] != inv["mrr"]).sum()
print("5. Invoice amount differs from MRR:", bad)

# Check 6: subscription starts on or after the account signed up
s = subs.merge(accounts[["account_id", "signup_date"]], on="account_id")
bad = (s["started_on"] < s["signup_date"]).sum()
print("6. Subscriptions starting before signup:", bad)

# Check 7: duplicate IDs
print("7. Duplicate subscription IDs:", subs["subscription_id"].duplicated().sum())

# ---------- QUICK PREVIEW OF KEY NUMBERS ----------
print("\n" + "=" * 50)
print("QUICK PREVIEW")
print("=" * 50)
live = subs[subs["status"] != "cancelled"]
print("Live subscriptions (active + past_due):", len(live))
print("Current MRR (all live):", live["mrr"].sum())
print("   of which past_due MRR:", live.loc[live["status"] == "past_due", "mrr"].sum())
print("Cancelled subscriptions:", is_cancelled.sum())
print("Overall logo churn %:", round(100 * is_cancelled.mean(), 1))