from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
source = ROOT / "data" / "indian_banking_customers.csv"
output = ROOT / "data" / "cleaned_indian_banking_customers.csv"

df = pd.read_csv(source)
# Standardize categorical text and remove duplicate customer IDs.
for col in ["gender", "state", "city", "nationality", "employment_type", "account_type", "income_band"]:
    df[col] = df[col].astype("string").str.strip().str.title()
df = df.drop_duplicates(subset=["customer_id"])
# Recalculate the project's analytical income bands consistently.
df["income_band"] = pd.cut(
    df["annual_income_inr"],
    bins=[-1, 300000, 1000000, float("inf")],
    labels=["Low", "Mid", "High"]
).astype("string")
# Monetary fields are non-negative INR integer amounts.
money = [c for c in df.columns if c.endswith("_inr")]
for col in money:
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).clip(lower=0).round().astype("int64")
df.to_csv(output, index=False)
print(f"Saved {len(df):,} cleaned rows to {output}")
