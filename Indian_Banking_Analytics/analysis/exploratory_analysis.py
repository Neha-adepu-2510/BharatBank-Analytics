from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
df = pd.read_csv(ROOT / "data" / "cleaned_indian_banking_customers.csv")
out = ROOT / "analysis" / "outputs"
out.mkdir(exist_ok=True)

print("Shape:", df.shape)
print("\nMissing values:\n", df.isna().sum())
print("\nNumeric summary:\n", df.select_dtypes("number").describe().T)

state = df.groupby("state")[["bank_deposits_inr","bank_loans_inr"]].sum().sort_values("bank_deposits_inr",ascending=False)
state.to_csv(out/"state_portfolio.csv")
state.plot(kind="bar", figsize=(12,6), title="Deposits and loans by state")
plt.ylabel("Amount (INR)")
plt.tight_layout()
plt.savefig(out/"state_portfolio.png",dpi=160)
plt.close()

corr_cols = ["annual_income_inr","bank_deposits_inr","bank_loans_inr",
             "savings_account_balance_inr","checking_account_balance_inr",
             "superannuation_savings_inr"]
corr = df[corr_cols].corr()
corr.to_csv(out/"portfolio_correlations.csv")
print("\nCorrelation matrix:\n", corr.round(2))
