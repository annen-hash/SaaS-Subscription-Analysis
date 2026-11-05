CREATE DATABASE IF NOT EXISTS saas_analytics;
USE saas_analytics;

CREATE TABLE plans (
  plan_id INT PRIMARY KEY,
  plan_name VARCHAR(50),
  tier VARCHAR(20),
  monthly_price DECIMAL(10,2),
  seats_included INT
);

CREATE TABLE accounts (
  account_id INT PRIMARY KEY,
  company_name VARCHAR(150),
  industry VARCHAR(60),
  country VARCHAR(60),
  employee_band VARCHAR(20),
  signup_date DATE,
  acquisition_channel VARCHAR(30)
);

CREATE TABLE users (
  user_id INT PRIMARY KEY,
  account_id INT,
  email VARCHAR(150),
  role VARCHAR(20),
  created_at DATETIME,
  last_login_at DATETIME,
  is_active TINYINT,
  FOREIGN KEY (account_id) REFERENCES accounts(account_id)
);

CREATE TABLE subscriptions (
  subscription_id INT PRIMARY KEY,
  account_id INT,
  plan_id INT,
  seats INT,
  billing_cycle VARCHAR(10),
  started_on DATE,
  ended_on DATE NULL,
  status VARCHAR(15),
  mrr DECIMAL(12,2),
  FOREIGN KEY (account_id) REFERENCES accounts(account_id),
  FOREIGN KEY (plan_id) REFERENCES plans(plan_id)
);

CREATE TABLE invoices (
  invoice_id INT PRIMARY KEY,
  subscription_id INT,
  period_start DATE,
  period_end DATE,
  amount_due DECIMAL(12,2),
  amount_paid DECIMAL(12,2),
  status VARCHAR(15),
  issued_on DATE,
  paid_on DATE NULL,
  FOREIGN KEY (subscription_id) REFERENCES subscriptions(subscription_id)
);

CREATE TABLE churn_events (
  churn_id INT PRIMARY KEY,
  subscription_id INT UNIQUE,
  churned_on DATE,
  reason VARCHAR(40),
  feedback_score INT,
  FOREIGN KEY (subscription_id) REFERENCES subscriptions(subscription_id)
);



-- checking if the table matches the Python file
USE saas_analytics;
SELECT 'plans' AS tbl, COUNT(*) AS n FROM plans
UNION ALL SELECT 'accounts', COUNT(*) FROM accounts
UNION ALL SELECT 'users', COUNT(*) FROM users
UNION ALL SELECT 'subscriptions', COUNT(*) FROM subscriptions
UNION ALL SELECT 'invoices', COUNT(*) FROM invoices
UNION ALL SELECT 'churn_events', COUNT(*) FROM churn_events;



-- Cross-checking the number of live subscriptions and monthly recurring revenue
SELECT COUNT(*) AS live_subs, SUM(mrr) AS live_mrr
FROM subscriptions
WHERE status <> 'cancelled';


-- Current MRR by plan
SELECT p.plan_name, p.tier, COUNT(*) AS live_subs, SUM(s.mrr) AS mrr
FROM subscriptions s
JOIN plans p ON p.plan_id = s.plan_id
WHERE s.status <> 'cancelled'
GROUP BY p.plan_name, p.tier
ORDER BY mrr DESC;


-- Churn rate by tier
SELECT p.tier,
       COUNT(*) AS total_subs,
       SUM(s.status = 'cancelled') AS cancelled,
       ROUND(100 * SUM(s.status = 'cancelled') / COUNT(*), 1) AS churn_pct
FROM subscriptions s
JOIN plans p ON p.plan_id = s.plan_id
GROUP BY p.tier
ORDER BY churn_pct DESC;


-- Why customers leave, and how they feel
SELECT reason,
       COUNT(*) AS events,
       ROUND(AVG(feedback_score), 2) AS avg_feedback
FROM churn_events
GROUP BY reason
ORDER BY events DESC;


-- New subscriptions and cancellations per quarter
SELECT q, SUM(new_subs) AS new_subs, SUM(cancels) AS cancels
FROM (
  SELECT CONCAT(YEAR(started_on), '-Q', QUARTER(started_on)) AS q,
         1 AS new_subs, 0 AS cancels
  FROM subscriptions
  UNION ALL
  SELECT CONCAT(YEAR(ended_on), '-Q', QUARTER(ended_on)), 0, 1
  FROM subscriptions
  WHERE ended_on IS NOT NULL
) t
GROUP BY q
ORDER BY q;


-- How long cancelled subscriptions last
SELECT ROUND(AVG(DATEDIFF(ended_on, started_on))) AS avg_days,
       MIN(DATEDIFF(ended_on, started_on)) AS shortest_days,
       MAX(DATEDIFF(ended_on, started_on)) AS longest_days
FROM subscriptions
WHERE status = 'cancelled';


-- 	The Average revenue per account by company size
SELECT a.employee_band,
       COUNT(DISTINCT a.account_id) AS accounts,
       SUM(s.mrr) AS total_mrr,
       ROUND(SUM(s.mrr) / COUNT(DISTINCT a.account_id), 2) AS revenue_per_account
FROM accounts a
JOIN subscriptions s ON s.account_id = a.account_id
WHERE s.status <> 'cancelled'
GROUP BY a.employee_band
ORDER BY revenue_per_account DESC;


-- Invoice collections per year
SELECT YEAR(issued_on) AS yr,
       SUM(amount_due) AS invoiced,
       SUM(amount_paid) AS collected,
       SUM(amount_due - amount_paid) AS outstanding
FROM invoices
GROUP BY YEAR(issued_on)
ORDER BY yr;


-- How fast customers pay
SELECT ROUND(AVG(DATEDIFF(paid_on, issued_on)), 1) AS avg_days_to_pay,
       MIN(DATEDIFF(paid_on, issued_on)) AS fastest,
       MAX(DATEDIFF(paid_on, issued_on)) AS slowest
FROM invoices
WHERE paid_on IS NOT NULL;


-- Which acquisition channel brings the most valuable accounts
SELECT a.acquisition_channel,
       COUNT(DISTINCT a.account_id) AS accounts,
       SUM(s.mrr) AS total_mrr,
       ROUND(SUM(s.mrr) / COUNT(DISTINCT a.account_id), 2) AS mrr_per_account
FROM accounts a
JOIN subscriptions s ON s.account_id = a.account_id
WHERE s.status <> 'cancelled'
GROUP BY a.acquisition_channel
ORDER BY mrr_per_account DESC;


-- Signup cohorts: share of each year’s accounts that still have a live subscription
SELECT YEAR(a.signup_date) AS cohort_year,
       COUNT(*) AS accounts,
       SUM(EXISTS (SELECT 1 FROM subscriptions s
                   WHERE s.account_id = a.account_id
                     AND s.status <> 'cancelled')) AS still_live,
       ROUND(100 * SUM(EXISTS (SELECT 1 FROM subscriptions s
                               WHERE s.account_id = a.account_id
                                 AND s.status <> 'cancelled')) / COUNT(*), 1) AS pct_live
FROM accounts a
GROUP BY YEAR(a.signup_date)
ORDER BY cohort_year;