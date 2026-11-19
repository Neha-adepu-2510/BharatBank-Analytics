import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(page_title="BharatBank | Analytics", page_icon="🏦", layout="wide")
DATA = Path(__file__).parent / "data" / "indian_banking_customers.csv"

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@600;700;800&display=swap');
html, body, [class*="css"] {font-family:'DM Sans',sans-serif;}
.stApp {background:linear-gradient(135deg,#f6f8fc 0%,#eef3f9 100%);}
.block-container {padding-top:1.5rem; padding-bottom:2rem; max-width:1500px;}
.hero {background:linear-gradient(115deg,#102a43,#176b87 62%,#39a6a3);padding:26px 30px;border-radius:20px;color:white;margin-bottom:18px;box-shadow:0 12px 30px rgba(16,42,67,.16);}
.hero h1 {font-family:Manrope,sans-serif;font-size:30px;margin:0;color:white;}
.hero p {margin:6px 0 0;color:#d9edf2;font-size:14px;}
.kpi {background:white;border:1px solid #e5ebf2;border-radius:16px;padding:17px 18px;box-shadow:0 5px 18px rgba(16,42,67,.045);min-height:112px;}
.kpi-label {color:#64748b;font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:.7px;}
.kpi-value {color:#102a43;font-family:Manrope,sans-serif;font-size:25px;font-weight:800;margin-top:7px;}
.kpi-note {color:#8492a6;font-size:11px;margin-top:3px;}
.panel {background:white;border:1px solid #e5ebf2;border-radius:16px;padding:14px 18px 4px;box-shadow:0 5px 18px rgba(16,42,67,.04);}
.section-title {font-family:Manrope,sans-serif;font-size:18px;font-weight:800;color:#16324f;margin:12px 0 8px;}
div[data-testid="stMetric"] {background:white;border:1px solid #e5ebf2;padding:14px;border-radius:14px;}
[data-testid="stSidebar"] {background:#102a43;}
[data-testid="stSidebar"] * {color:#f3f7fa;}
[data-testid="stSidebar"] .stMultiSelect label,[data-testid="stSidebar"] label {color:#e6f1f5!important;}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    d = pd.read_csv(DATA)
    return d

df = load_data()
money_cols = ["annual_income_inr","bank_deposits_inr","bank_loans_inr","savings_account_balance_inr",
              "checking_account_balance_inr","fixed_deposits_inr","recurring_deposits_inr",
              "credit_card_balance_inr","superannuation_savings_inr"]
def inr(x):
    if x >= 1e7: return f"₹{x/1e7:,.2f} Cr"
    if x >= 1e5: return f"₹{x/1e5:,.2f} L"
    if x >= 1e3: return f"₹{x/1e3:,.1f} K"
    return f"₹{x:,.0f}"

st.sidebar.markdown("## 🏦 BharatBank")
st.sidebar.caption("Indian Banking Analytics")
page = st.sidebar.radio("NAVIGATION",["Home","Loan Analysis","Deposit Analysis","Summary"])
st.sidebar.markdown("---")
st.sidebar.markdown("### FILTER DATA")
states = st.sidebar.multiselect("State", sorted(df.state.unique()), default=sorted(df.state.unique()))
gender = st.sidebar.multiselect("Gender", sorted(df.gender.unique()), default=sorted(df.gender.unique()))
income_bands = st.sidebar.multiselect("Income band", ["Low","Mid","High"], default=["Low","Mid","High"])
age_range = st.sidebar.slider("Customer age", int(df.age.min()), int(df.age.max()), (int(df.age.min()),int(df.age.max())))
filtered = df[df.state.isin(states) & df.gender.isin(gender) & df.income_band.isin(income_bands) & df.age.between(*age_range)]
st.sidebar.markdown("---")
st.sidebar.caption(f"Showing {len(filtered):,} of {len(df):,} customers")
st.sidebar.caption("Dataset: synthetic / demonstration")

st.markdown(f"""<div class="hero"><h1>🏦 BharatBank Analytics</h1><p>Indian retail banking performance · INR reporting · Interactive insights</p></div>""",unsafe_allow_html=True)
if filtered.empty:
    st.warning("No records match the selected filters. Adjust the filters in the sidebar.")
    st.stop()

customers = len(filtered)
deposits = filtered.bank_deposits_inr.sum()
loans = filtered.bank_loans_inr.sum()
income = filtered.annual_income_inr.mean()
loan_customers = (filtered.bank_loans_inr>0).sum()
deposit_avg = filtered.bank_deposits_inr.mean()
credit_bal = filtered.credit_card_balance_inr.sum()

def kpi(label,value,note):
    st.markdown(f'<div class="kpi"><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div><div class="kpi-note">{note}</div></div>',unsafe_allow_html=True)

if page == "Home":
    st.markdown('<div class="section-title">Portfolio snapshot</div>',unsafe_allow_html=True)
    c=st.columns(4)
    with c[0]: kpi("Total customers",f"{customers:,}","Customers in current selection")
    with c[1]: kpi("Total deposits",inr(deposits),"Bank deposit portfolio")
    with c[2]: kpi("Total loans",inr(loans),"Outstanding loan amount")
    with c[3]: kpi("Average annual income",inr(income),"Mean customer income")
    left,right=st.columns([1.15,1])
    with left:
        st.markdown('<div class="section-title">Deposits vs loans by state</div>',unsafe_allow_html=True)
        by=filtered.groupby("state",as_index=False)[["bank_deposits_inr","bank_loans_inr"]].sum().sort_values("bank_deposits_inr",ascending=False)
        long=by.melt("state",var_name="Portfolio",value_name="Amount (INR)")
        long["Portfolio"]=long.Portfolio.map({"bank_deposits_inr":"Deposits","bank_loans_inr":"Loans"})
        fig=px.bar(long,x="state",y="Amount (INR)",color="Portfolio",barmode="group",template="plotly_white",color_discrete_sequence=["#168aad","#f4a261"])
        fig.update_layout(height=390,margin=dict(l=5,r=5,t=20,b=5),legend_title_text="")
        st.plotly_chart(fig,use_container_width=True)
    with right:
        st.markdown('<div class="section-title">Customer income mix</div>',unsafe_allow_html=True)
        inc=filtered.income_band.value_counts().reindex(["Low","Mid","High"]).reset_index()
        inc.columns=["Income band","Customers"]
        fig=px.pie(inc,names="Income band",values="Customers",hole=.62,template="plotly_white",color_discrete_sequence=["#f4a261","#168aad","#1b4965"])
        fig.update_layout(height=390,margin=dict(l=5,r=5,t=20,b=5),legend_title_text="")
        st.plotly_chart(fig,use_container_width=True)
    st.markdown('<div class="section-title">Customer distribution</div>',unsafe_allow_html=True)
    a,b=st.columns(2)
    with a:
        g=filtered.gender.value_counts().reset_index();g.columns=["Gender","Customers"]
        fig=px.bar(g,x="Gender",y="Customers",color="Gender",template="plotly_white",color_discrete_sequence=["#168aad","#f4a261","#8d99ae"])
        fig.update_layout(showlegend=False,height=300,margin=dict(l=5,r=5,t=15,b=5))
        st.plotly_chart(fig,use_container_width=True)
    with b:
        e=filtered.employment_type.value_counts().reset_index();e.columns=["Employment","Customers"]
        fig=px.pie(e,names="Employment",values="Customers",hole=.48,template="plotly_white")
        fig.update_layout(height=300,margin=dict(l=5,r=5,t=15,b=5))
        st.plotly_chart(fig,use_container_width=True)

elif page == "Loan Analysis":
    st.markdown('<div class="section-title">Loan portfolio performance</div>',unsafe_allow_html=True)
    c=st.columns(4)
    with c[0]: kpi("Total loans",inr(loans),"Outstanding balance")
    with c[1]: kpi("Borrowers",f"{loan_customers:,}",f"{loan_customers/customers:.1%} of selected customers")
    with c[2]: kpi("Average loan",inr(loans/max(loan_customers,1)),"Among borrowers")
    with c[3]: kpi("Credit card balance",inr(credit_bal),"Outstanding card balance")
    a,b=st.columns(2)
    with a:
        types=pd.DataFrame({"Loan type":["Home loan","Personal loan","Vehicle loan"],"Amount":[filtered.home_loan_inr.sum(),filtered.personal_loan_inr.sum(),filtered.vehicle_loan_inr.sum()]})
        fig=px.bar(types,x="Loan type",y="Amount",color="Loan type",template="plotly_white",color_discrete_sequence=["#176b87","#f4a261","#2a9d8f"])
        fig.update_layout(showlegend=False,height=360,margin=dict(l=5,r=5,t=20,b=5),yaxis_title="Amount (INR)")
        st.plotly_chart(fig,use_container_width=True)
    with b:
        fig=px.histogram(filtered[filtered.bank_loans_inr>0],x="bank_loans_inr",nbins=30,color="income_band",template="plotly_white",color_discrete_sequence=["#f4a261","#168aad","#1b4965"])
        fig.update_layout(height=360,margin=dict(l=5,r=5,t=20,b=5),xaxis_title="Loan amount (INR)",yaxis_title="Borrowers")
        st.plotly_chart(fig,use_container_width=True)
    st.markdown('<div class="section-title">Borrowers by state</div>',unsafe_allow_html=True)
    by=filtered[filtered.bank_loans_inr>0].groupby("state",as_index=False).agg(Borrowers=("customer_id","count"),Loan_amount=("bank_loans_inr","sum")).sort_values("Loan_amount",ascending=False)
    fig=px.bar(by,x="state",y="Loan_amount",hover_data=["Borrowers"],template="plotly_white",color="Loan_amount",color_continuous_scale="Teal")
    fig.update_layout(height=340,margin=dict(l=5,r=5,t=15,b=5),xaxis_title="")
    st.plotly_chart(fig,use_container_width=True)

elif page == "Deposit Analysis":
    st.markdown('<div class="section-title">Deposit portfolio performance</div>',unsafe_allow_html=True)
    c=st.columns(4)
    with c[0]: kpi("Total deposits",inr(deposits),"Total bank deposits")
    with c[1]: kpi("Average deposit",inr(deposit_avg),"Per selected customer")
    with c[2]: kpi("Fixed deposits",inr(filtered.fixed_deposits_inr.sum()),"FD portfolio")
    with c[3]: kpi("Recurring deposits",inr(filtered.recurring_deposits_inr.sum()),"RD portfolio")
    a,b=st.columns(2)
    with a:
        products=pd.DataFrame({"Deposit product":["Savings","Checking","Fixed deposits","Recurring deposits","Foreign currency"],"Balance":[filtered.savings_account_balance_inr.sum(),filtered.checking_account_balance_inr.sum(),filtered.fixed_deposits_inr.sum(),filtered.recurring_deposits_inr.sum(),filtered.foreign_currency_balance_inr.sum()]})
        fig=px.bar(products,x="Deposit product",y="Balance",color="Deposit product",template="plotly_white",color_discrete_sequence=["#168aad","#1b4965","#2a9d8f","#f4a261","#8d99ae"])
        fig.update_layout(showlegend=False,height=370,margin=dict(l=5,r=5,t=20,b=5),xaxis_title="",yaxis_title="Balance (INR)")
        st.plotly_chart(fig,use_container_width=True)
    with b:
        by=filtered.groupby("income_band",as_index=False).bank_deposits_inr.sum()
        fig=px.pie(by,names="income_band",values="bank_deposits_inr",hole=.58,template="plotly_white",color_discrete_sequence=["#f4a261","#168aad","#1b4965"])
        fig.update_layout(height=370,margin=dict(l=5,r=5,t=20,b=5),legend_title_text="Income band")
        st.plotly_chart(fig,use_container_width=True)
    st.markdown('<div class="section-title">Deposit trends by customer tenure</div>',unsafe_allow_html=True)
    tenure=filtered.groupby("customer_since_year",as_index=False).agg(Customers=("customer_id","count"),Deposits=("bank_deposits_inr","sum"))
    fig=px.line(tenure,x="customer_since_year",y="Deposits",markers=True,template="plotly_white")
    fig.update_traces(line_color="#168aad",line_width=3)
    fig.update_layout(height=330,margin=dict(l=5,r=5,t=15,b=5),xaxis_title="Year joined",yaxis_title="Deposits (INR)")
    st.plotly_chart(fig,use_container_width=True)

else:
    st.markdown('<div class="section-title">Executive summary</div>',unsafe_allow_html=True)
    c=st.columns(3)
    with c[0]: kpi("Deposit-to-loan ratio",f"{deposits/max(loans,1):.2f}x","Deposits divided by loans")
    with c[1]: kpi("Credit card adoption",f"{(filtered.credit_card=='Yes').mean():.1%}","Share with a credit card")
    with c[2]: kpi("NRI customers",f"{(filtered.nationality=='NRI').mean():.1%}","Share marked NRI")
    st.markdown('<div class="section-title">Portfolio relationship explorer</div>',unsafe_allow_html=True)
    corr=filtered[["bank_deposits_inr","bank_loans_inr","annual_income_inr","savings_account_balance_inr","checking_account_balance_inr","superannuation_savings_inr"]].corr()
    corr.index=["Deposits","Loans","Annual income","Savings balance","Checking balance","Superannuation"]
    corr.columns=corr.index
    fig=px.imshow(corr,text_auto=".2f",color_continuous_scale="RdBu",zmin=-1,zmax=1,aspect="auto",template="plotly_white")
    fig.update_layout(height=460,margin=dict(l=5,r=5,t=20,b=5))
    st.plotly_chart(fig,use_container_width=True)
    st.markdown('<div class="section-title">Filtered customer records</div>',unsafe_allow_html=True)
    cols=["customer_id","age","gender","state","city","employment_type","income_band","annual_income_inr","bank_deposits_inr","bank_loans_inr"]
    st.dataframe(filtered[cols].rename(columns={"customer_id":"Customer ID","annual_income_inr":"Annual income (INR)","bank_deposits_inr":"Deposits (INR)","bank_loans_inr":"Loans (INR)"}),use_container_width=True,height=360)
    st.download_button("Download filtered records (CSV)",filtered.to_csv(index=False).encode("utf-8"),"filtered_indian_banking_customers.csv","text/csv")

st.markdown("---")
st.caption("BharatBank Analytics · Portfolio demonstration only · Synthetic data, not real customer or bank information.")
