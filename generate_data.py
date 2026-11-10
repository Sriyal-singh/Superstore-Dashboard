"""Synthetic data with the same columns as the Kaggle 'Superstore Sales' dataset (Sample - Superstore.csv)."""
import numpy as np, pandas as pd, os

STATES = {"West": ["California", "Washington", "Oregon", "Colorado"], "East": ["New York", "Pennsylvania", "Massachusetts", "Ohio"],
          "Central": ["Texas", "Illinois", "Michigan", "Minnesota"], "South": ["Florida", "Georgia", "Virginia", "North Carolina"]}
CATALOG = {"Technology": {"Phones": (60, 900), "Accessories": (10, 200), "Machines": (300, 3000)},
           "Furniture": {"Chairs": (80, 700), "Tables": (150, 1500), "Bookcases": (90, 800)},
           "Office Supplies": {"Paper": (5, 60), "Binders": (4, 80), "Storage": (15, 250)}}

def generate(path="data/superstore.csv", n=8000, seed=11):
    rng = np.random.default_rng(seed)
    cust = [(f"CU-{i:04d}", f"Customer {i}", rng.choice(["Consumer", "Corporate", "Home Office"], p=[.52, .30, .18])) for i in range(1, 701)]
    prods = []
    for cat, subs in CATALOG.items():
        for sub, (lo, hi) in subs.items():
            for k in range(1, 13):
                prods.append((f"{cat[:3].upper()}-{sub[:2].upper()}-{k:03d}", cat, sub, f"{sub} Model {k}", rng.uniform(lo, hi)))
    rows = []
    for i in range(n):
        od = pd.Timestamp("2021-01-01") + pd.Timedelta(days=int(rng.integers(0, 1460)))
        od += pd.Timedelta(days=int(30 * np.sin((od.month - 3) / 12 * 2 * np.pi) * 0 ))
        if od.month in (11, 12) and rng.random() < .5: pass
        region = rng.choice(list(STATES), p=[.32, .28, .22, .18]); state = rng.choice(STATES[region])
        c = cust[rng.integers(len(cust))]; p = prods[rng.integers(len(prods))]
        qty = int(rng.integers(1, 8)); disc = float(rng.choice([0, 0, 0, .1, .2, .3, .5], p=[.4, .15, .1, .1, .1, .1, .05]))
        sales = p[4] * qty * (1 - disc)
        margin = {"Technology": .22, "Furniture": .06, "Office Supplies": .15}[p[1]] - disc * .9 + rng.normal(0, .05)
        rows.append({"Row ID": i + 1, "Order ID": f"US-{od.year}-{100000 + i // 2}", "Order Date": od.strftime("%m/%d/%Y"),
                     "Ship Date": (od + pd.Timedelta(days=int(rng.integers(2, 8)))).strftime("%m/%d/%Y"),
                     "Ship Mode": rng.choice(["Standard Class", "Second Class", "First Class", "Same Day"], p=[.6, .2, .15, .05]),
                     "Customer ID": c[0], "Customer Name": c[1], "Segment": c[2], "Country": "United States",
                     "City": f"{state} City", "State": state, "Postal Code": int(rng.integers(10000, 99999)), "Region": region,
                     "Product ID": p[0], "Category": p[1], "Sub-Category": p[2], "Product Name": p[3],
                     "Sales": round(sales, 2), "Quantity": qty, "Discount": disc, "Profit": round(sales * margin, 2)})
    df = pd.DataFrame(rows)
    # seasonality: duplicate some Nov/Dec orders
    extra = df[pd.to_datetime(df["Order Date"]).dt.month.isin([11, 12])].sample(900, random_state=1).copy()
    extra["Row ID"] = range(len(df) + 1, len(df) + 1 + len(extra)); df = pd.concat([df, extra], ignore_index=True)
    os.makedirs(os.path.dirname(path), exist_ok=True); df.to_csv(path, index=False)
    return df

if __name__ == "__main__":
    generate(); print("Sample data written.")
