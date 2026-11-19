-- BharatBank Analytics | MySQL 8+
CREATE DATABASE IF NOT EXISTS indian_banking;
USE indian_banking;

DROP TABLE IF EXISTS customers;
CREATE TABLE customers (
  customer_id VARCHAR(12) PRIMARY KEY,
  age TINYINT UNSIGNED NOT NULL,
  gender VARCHAR(10) NOT NULL,
  state VARCHAR(40) NOT NULL,
  city VARCHAR(50) NOT NULL,
  nationality VARCHAR(10) NOT NULL,
  employment_type VARCHAR(20) NOT NULL,
  account_type VARCHAR(20) NOT NULL,
  branch_code VARCHAR(10) NOT NULL,
  branch_name VARCHAR(80) NOT NULL,
  customer_since_year SMALLINT NOT NULL,
  annual_income_inr BIGINT NOT NULL,
  income_band VARCHAR(10) NOT NULL,
  bank_deposits_inr BIGINT NOT NULL,
  savings_account_balance_inr BIGINT NOT NULL,
  checking_account_balance_inr BIGINT NOT NULL,
  fixed_deposits_inr BIGINT NOT NULL,
  recurring_deposits_inr BIGINT NOT NULL,
  foreign_currency_balance_inr BIGINT NOT NULL,
  bank_loans_inr BIGINT NOT NULL,
  home_loan_inr BIGINT NOT NULL,
  personal_loan_inr BIGINT NOT NULL,
  vehicle_loan_inr BIGINT NOT NULL,
  credit_card VARCHAR(3) NOT NULL,
  credit_limit_inr BIGINT NOT NULL,
  credit_card_balance_inr BIGINT NOT NULL,
  superannuation_savings_inr BIGINT NOT NULL
);

-- Import data/indian_banking_customers.csv using MySQL Workbench:
-- Server > Data Import (or Table Data Import Wizard), target table: customers.

-- 1. Portfolio KPIs
SELECT COUNT(*) AS customers,
       SUM(bank_deposits_inr) AS total_deposits_inr,
       SUM(bank_loans_inr) AS total_loans_inr,
       AVG(annual_income_inr) AS average_annual_income_inr
FROM customers;

-- 2. State-level portfolio
SELECT state, COUNT(*) AS customers,
       SUM(bank_deposits_inr) AS deposits_inr,
       SUM(bank_loans_inr) AS loans_inr
FROM customers GROUP BY state ORDER BY deposits_inr DESC;

-- 3. Income segment analysis
SELECT income_band, COUNT(*) AS customers,
       AVG(annual_income_inr) AS avg_income_inr,
       AVG(bank_deposits_inr) AS avg_deposit_inr
FROM customers GROUP BY income_band
ORDER BY FIELD(income_band, 'Low', 'Mid', 'High');

-- 4. Loan product mix
SELECT SUM(home_loan_inr) AS home_loans_inr,
       SUM(personal_loan_inr) AS personal_loans_inr,
       SUM(vehicle_loan_inr) AS vehicle_loans_inr
FROM customers;

-- 5. Deposit product mix
SELECT SUM(savings_account_balance_inr) AS savings_inr,
       SUM(checking_account_balance_inr) AS checking_inr,
       SUM(fixed_deposits_inr) AS fixed_deposits_inr,
       SUM(recurring_deposits_inr) AS recurring_deposits_inr,
       SUM(foreign_currency_balance_inr) AS foreign_currency_inr
FROM customers;

-- 6. Credit card utilization
SELECT ROUND(100 * SUM(credit_card_balance_inr) /
       NULLIF(SUM(credit_limit_inr),0), 2) AS utilization_pct
FROM customers WHERE credit_card = 'Yes';

-- 7. Branch performance
SELECT branch_name, COUNT(*) AS customers,
       SUM(bank_deposits_inr) AS deposits_inr,
       SUM(bank_loans_inr) AS loans_inr
FROM customers GROUP BY branch_name ORDER BY deposits_inr DESC LIMIT 15;

-- 8. Customer tenure cohorts
SELECT customer_since_year, COUNT(*) AS customers,
       SUM(bank_deposits_inr) AS deposits_inr
FROM customers GROUP BY customer_since_year ORDER BY customer_since_year;
