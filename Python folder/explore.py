import pandas as pd
import matplotlib.pyplot as plt

path = "Data/"
subs = pd.read_csv(path + "subscriptions.csv", parse_dates=["started_on", "ended_on"])
plans = pd.read_csv(path + "plans.csv")
churn = pd.read_csv(path + "churn_events.csv")

END_OF_DATA = pd.Timestamp("2026-09-30")

# ---------- 1. SURVIVAL CURVE (Kaplan-Meier, built by hand) ----------
# Each subscription gets a duration (days alive) and an event flag (1 = cancelled).
# Active and past_due subscriptions are "still alive", so event = 0.
subs["duration"] = (subs["ended_on"].fillna(END_OF_DATA) - subs["started_on"]).dt.days
subs["event"] = (subs["status"] == "cancelled").astype(int)


def survival_curve(df):
	t = df.groupby("duration").agg(events=("event", "sum"), exits=("event", "size")).sort_index()
	t["at_risk"] = len(df) - t["exits"].cumsum().shift(fill_value=0)
	t["survival"] = (1 - t["events"] / t["at_risk"]).cumprod()
	return t


overall = survival_curve(subs)

plt.figure(figsize=(9, 5))
plt.step(overall.index, overall["survival"] * 100, where="post")
plt.title("Share of subscriptions still alive by days since start")
plt.xlabel("Days since subscription started")
plt.ylabel("% still alive")
plt.ylim(0, 105)
plt.grid(alpha=0.3)
plt.savefig("survival_overall.png", dpi=150, bbox_inches="tight")
plt.show()

for d in [90, 180, 365, 730]:
	s = overall.loc[overall.index <= d, "survival"].iloc[-1]
	print(f"Still alive after {d} days: {s * 100:.1f}%")

# ---------- 2. DOES CHURN DIFFER BY TIER? ----------
subs = subs.merge(plans[["plan_id", "tier"]], on="plan_id")

plt.figure(figsize=(9, 5))
for tier, g in subs.groupby("tier"):
	c = survival_curve(g)
	plt.step(c.index, c["survival"] * 100, where="post", label=tier)
plt.title("Survival curve by tier (lines on top of each other = churn doesn't depend on tier)")
plt.xlabel("Days since subscription started")
plt.ylabel("% still alive")
plt.legend()
plt.grid(alpha=0.3)
plt.savefig("survival_by_tier.png", dpi=150, bbox_inches="tight")
plt.show()

# ---------- 3. CHURN REASONS, FEEDBACK AND MONEY LOST ----------
cm = churn.merge(subs[["subscription_id", "mrr"]], on="subscription_id")
reasons = cm.groupby("reason").agg(
	events=("churn_id", "count"),
	avg_feedback=("feedback_score", "mean"),
	mrr_lost=("mrr", "sum"),
).sort_values("events", ascending=False).round(2)
print("\n", reasons)

fig, ax = plt.subplots(1, 3, figsize=(15, 4))
reasons["events"].plot.bar(ax=ax[0], title="Cancellations by reason")
reasons["avg_feedback"].plot.bar(ax=ax[1], title="Average feedback score", color="orange")
reasons["mrr_lost"].plot.bar(ax=ax[2], title="MRR lost by reason", color="red")
plt.tight_layout()
plt.savefig("churn_reasons.png", dpi=150, bbox_inches="tight")
plt.show()
