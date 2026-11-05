# SaaS Subscription Analytics
## **Table of Contents** <br>
- [Project Overview](#project-overview) <br>
- [Technologies and Skills](#technologies--skills)
- [Project Objectives](#project-objectives)
- [Process](#process)
- [Key Insights](#key-insights)
- [Reommendations](#recommendations)
- [Limitations](#limitations)
- [Files](#files)
  
## Project Overview
This document provides an analysis of key performance data for a business-software company from January 2023 to 30 September 2026. Metrics reviewed include monthly recurring revenue (MRR), customer sign up cohorts and churn rate across different plans, tiers, company size, and year.This dataset, sourced from Kaggle, a widely recognized platform offering copyright-free datasets, contains a six tables covering the full subscription business: the price list, customer accounts and their users, subscriptions with monthly recurring revenue, invoices and churn events. The analysis was conducted using MySQL, Python and Power BI.

## Technologies & Skills
- **Technologies**: SQL (MySQL), MySQL Workbench, Python (pandas, matplotlib), Power BI, DAX
- **Skills**: Data modeling, database development, data wrangling, data cleaning, data analysis, data visualization/dashboarding

## Project Objectives
The analysis addresses the following objectives:
+ Calculating Churn rate by tier.
+ Calculating Current MRR by plan and Average revenue per account by company size.
+ Analyzing why customers leave, and how do they feel about it.
+ Calculating new subscriptions and cancellations per quarter.
+ Delivering actionable recommendations to the company stakeholders.

## Process
1. Python: loaded 6 CSVs, ran integrity checks (MRR = seats x price, churn
   events match cancellations, etc.). All passed.
2. MySQL: created schema with foreign keys, loaded data, built SQL views.
3. Python: survival curve, churn by tier, reasons vs feedback.
4. Power BI: 5-page dashboard (Summary, Overview, Churn, Customers, Collections).

## Key Insights
### 1. Revenue
- **Live MRR is $39.28M** across 12,687 live subscriptions (active + past due), an average of $3.74K per account.
- **Enterprise plans generate about 46% of MRR** ($17.9M of $39.3M). Monthly plans out-earn annual plans in every tier.
- **$1.86M of MRR (4.7%) is past due.** These customers haven't cancelled, so this is revenue to recover through collections.
- New subscriptions grow every quarter, from a handful in early 2023 to about 2,500 in 2026-Q3. Cancellations grow far more slowly, so the base is expanding.

### 2. Churn
- **15.4% of all subscriptions have cancelled** (2,313 of 15,000), costing **$7.52M in MRR**.
- **Churn is a steady leak, not an onboarding problem.** The survival curve falls at a near-constant rate: about 84% of subscriptions are still alive at 400 days, about 70% at 800 days, and about 56% at 1,200 days. There is no cliff in the first 90 days.
- **Tier does not predict churn.** Survival curves for Starter, Team, Business and Enterprise overlap for the first 700 days. Moving customers between tiers is not a retention strategy.
- Cancelled subscriptions lasted 296 days on average. This understates real lifetime, because it only counts customers who have already left.

### 3. Why customers leave
- **Price is the top reason:** about 27% of cancellations and about 28% of lost MRR.
- **Price and support leavers are unhappy** (average feedback about 3 out of 10). Every other reason scores about 7.5.
- Support failures are rare (about 155 cancellations) but cause the same dissatisfaction as price.
- Most other leavers (low usage, switched tool, missing feature, company closed) go neutrally, so engagement and product work may win some of them back.

### 4. Customers
- **Revenue per account depends strongly on company size:** about $20K for 1000+ employees versus about $1K for 11-50 employees.
- **Organic is the largest channel by total MRR ($12M), but not by quality.** Value per account is nearly flat across channels ($3.6K to $4.0K), with outbound highest at $4.0K and organic second at $3.9K.
- **87% of accounts (10,492 of 12,000) still have a live subscription.** Older signup cohorts show lower retention (80% for 2023 versus 95% for 2026) because they have had longer to churn, not because they are worse customers.

### 5. Collections
- **$502.1M invoiced, $455.6M collected, $46.5M outstanding: a 91% collection rate.**
- **The rate is stable across years** (92.1%, 90.8%, 90.8%, 90.6%), so unpaid money is not just a timing effect on recent invoices.
- **Customers pay at an even pace**: paid invoices are spread across 0 to 20 days after issue, averaging 10 days.
- **14,393 invoices (about 9%) are unpaid.** Outstanding balances follow customer size (Enterprise $22M, Business $13M, Team $8M, Starter $4M).

## Recommendations
- **Review pricing and packaging.** Price is the most expensive churn reason and the most negative one.
- **Fix the support experience.** Cancellations are few but equally unhappy.
- **Run retention programmes across the whole lifetime**, not just onboarding.
- **Prioritise larger accounts** for acquisition, since value per account scales with company size.
- **Chase past-due accounts early** to protect $1.86M of MRR.

## Limitations
- Invoices are dated at random within each subscription's life, so they support collections analysis only, not month-by-month revenue.
- 2026 is a partial year (to 30 September).

## Files
- sql/ - schema and views
- python/ - load_to_mysql.py, churn_analysis.py, explore.py
- powerbi/ - screenshots of dashboard pages
