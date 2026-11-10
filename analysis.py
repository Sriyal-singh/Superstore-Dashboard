# %%
# # Superstore Sales Performance Analysis
# Python analysis + SQLite database (for the SQL queries in `sql/`) + export for Power BI.
# Dataset: Kaggle "Superstore Sales" -> `data/superstore.csv` (synthetic sample used if missing).

# %%
import os, sqlite3
import pandas as pd, numpy as np
import matplotlib.pyplot as plt, seaborn as sns
import matplotlib.ticker as mt
sns.set_theme(style="whitegrid")
os.makedirs("images", exist_ok=True)
PATH = "data/superstore.csv"
if not os.path.exists(PATH):
    from generate_data import generate
    generate(PATH)
try:
    df = pd.read_csv(PATH)
except UnicodeDecodeError:          # the original Kaggle file is latin-1 encoded
    df = pd.read_csv(PATH, encoding="latin-1")
df.head()

# %%
# ## 1. Cleaning
df = df.drop_duplicates().copy()
df["Order Date"] = pd.to_datetime(df["Order Date"], format="mixed")
df["Ship Date"] = pd.to_datetime(df["Ship Date"], format="mixed")
df["Month"] = df["Order Date"].dt.to_period("M").dt.to_timestamp()
df["Year"] = df["Order Date"].dt.year
df["Ship Days"] = (df["Ship Date"] - df["Order Date"]).dt.days
print("Nulls:", int(df.isna().sum().sum()), "| Rows:", len(df))
df.to_csv("cleaned_dataset.csv", index=False)

# %%
# ## 2. KPIs
revenue, profit = df["Sales"].sum(), df["Profit"].sum()
orders = df["Order ID"].nunique()
kpi = {"Revenue": revenue, "Profit": profit, "Profit Margin": profit / revenue,
       "Orders": orders, "Average Order Value": revenue / orders}
for k, v in kpi.items():
    print(f"{k:22s}{v:>14,.2f}" if "Margin" not in k else f"{k:22s}{v:>14.1%}")

# %%
# ## 3. Monthly revenue & profit trend
m = df.groupby("Month")[["Sales", "Profit"]].sum()
fig, ax = plt.subplots(figsize=(11, 4.5))
m["Sales"].plot(ax=ax, marker="o", label="Revenue", color="#1f77b4")
m["Profit"].plot(ax=ax, marker="s", label="Profit", color="#2ca02c")
ax.yaxis.set_major_formatter(mt.FuncFormatter(lambda x, _: f"${x/1e3:,.0f}K"))
ax.set_title("Monthly revenue and profit"); ax.set_xlabel(""); ax.legend()
plt.tight_layout(); plt.savefig("images/monthly_trend.png", dpi=150); plt.show()

# %%
# ## 4. Top customers and products
top_c = df.groupby("Customer Name")[["Sales", "Profit"]].sum().sort_values("Sales", ascending=False).head(10)
top_p = df.groupby("Product Name")[["Sales", "Profit"]].sum().sort_values("Profit", ascending=False).head(10)
fig, ax = plt.subplots(1, 2, figsize=(14, 5))
top_c["Sales"].iloc[::-1].plot.barh(ax=ax[0], color="#1f77b4").set_title("Top 10 customers by revenue")
top_p["Profit"].iloc[::-1].plot.barh(ax=ax[1], color="#2ca02c").set_title("Top 10 products by profit")
for a in ax: a.set_ylabel("")
plt.tight_layout(); plt.savefig("images/top_customers_products.png", dpi=150); plt.show()

# %%
# ## 5. Regional performance
reg = df.groupby("Region").agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"), Orders=("Order ID", "nunique"))
reg["Margin"] = reg["Profit"] / reg["Sales"]
fig, ax = plt.subplots(1, 2, figsize=(12, 4.5))
reg[["Sales", "Profit"]].plot.bar(ax=ax[0], color=["#1f77b4", "#2ca02c"], rot=0).set_title("Revenue & profit by region")
by_state = df.groupby("State")["Profit"].sum().sort_values()
by_state.plot.barh(ax=ax[1], color=np.where(by_state < 0, "#d62728", "#2ca02c")).set_title("Profit by state")
ax[0].yaxis.set_major_formatter(mt.FuncFormatter(lambda x, _: f"${x/1e6:.1f}M")); ax[0].grid(axis="x", visible=False)
ax[1].xaxis.set_major_formatter(mt.FuncFormatter(lambda x, _: f"${x/1e3:,.0f}K")); ax[1].grid(axis="y", visible=False)
plt.tight_layout(); plt.savefig("images/regional_performance.png", dpi=150); plt.show()
reg

# %%
# ## 6. Category and discount analysis
cat = df.groupby(["Category", "Sub-Category"])[["Sales", "Profit"]].sum()
disc = df.groupby("Discount")["Profit"].mean()
fig, ax = plt.subplots(1, 2, figsize=(12, 4.5))
sns.heatmap(df.pivot_table(index="Sub-Category", columns="Region", values="Profit", aggfunc="sum"),
            annot=True, fmt=".0f", cmap="RdYlGn", center=0, ax=ax[0]); ax[0].set_title("Profit: sub-category x region")
disc.plot.bar(ax=ax[1], color="#ff7f0e", rot=0); ax[1].set_title("Average profit per order line by discount level")
plt.tight_layout(); plt.savefig("images/category_discount.png", dpi=150); plt.show()

# %%
# ## 7. Build SQLite DB (used by sql/queries.sql) and export for Power BI
con = sqlite3.connect("superstore.db")
df.assign(**{"Order Date": df["Order Date"].dt.strftime("%Y-%m-%d"), "Ship Date": df["Ship Date"].dt.strftime("%Y-%m-%d"),
             "Month": df["Month"].dt.strftime("%Y-%m")}).rename(columns=lambda c: c.replace(" ", "_").replace("-", "_")) \
  .to_sql("orders", con, if_exists="replace", index=False)
con.close()
df.drop(columns=["Month"]).to_csv("powerbi/superstore_for_powerbi.csv", index=False)
print("Insights:")
print(f"1. Revenue ${revenue:,.0f}, profit ${profit:,.0f} ({profit/revenue:.1%} margin) across {orders:,} orders")
print(f"2. Best region by profit: {reg['Profit'].idxmax()} | weakest: {reg['Profit'].idxmin()}")
print(f"3. Peak revenue month: {m['Sales'].idxmax():%B %Y}")
print(f"4. Loss-making states: {', '.join(by_state[by_state < 0].index) or 'none'}")
print(f"5. Orders with 30%+ discount average ${df[df.Discount >= .3]['Profit'].mean():,.0f} profit vs ${df[df.Discount == 0]['Profit'].mean():,.0f} with no discount")
