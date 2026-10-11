"""
FreshMart Romania - Data Preparation Script
Phase 1: Load, clean, adapt, and export the main dataset.
We run this script ONCE for output: FreshMart_Dataset.csv
"""

import pandas as pd
import numpy as np

# ── 1. LOAD ───────────────────────────────────────────────────────────────────
df = pd.read_excel("Data/Data Source.xlsx")
print(f"Loaded: {df.shape[0]} rows × {df.shape[1]} columns")

# ── 2. RENAME COLUMNS (adapting to FreshMart Romania context) ───────────────────
df = df.rename(columns={
    "Row ID":        "Row_ID",
    "Order ID":      "Order_ID",
    "Order Date":    "Order_Date",
    "Ship Date":     "Ship_Date",
    "Ship Mode":     "Ship_Mode",
    "Customer ID":   "Customer_ID",
    "Customer Name": "Customer_Name",
    "Segment":       "Segment",
    "Country":       "Country",
    "City":          "City",
    "State":         "State",
    "Postal Code":   "Postal_Code",
    "Region":        "Region",
    "Product ID":    "Product_ID",
    "Category":      "Category",
    "Sub-Category":  "Sub_Category",
    "Product Name":  "Product_Name",
    "Sales":         "Sales",
    "Quantity":      "Quantity",
    "Discount":      "Discount",
    "Profit":        "Profit",
})

# ── 3. ADAPT COUNTRY & REGION TO ROMANIA CONTEXT ─────────────────────────────
df["Country"] = "Romania"

region_map = {
    "South":   "South",
    "West":    "West",
    "Central": "Center",
    "East":    "East",
}
df["Region"] = df["Region"].map(region_map)

# ── 4. MAP US STATES → ROMANIAN COUNTIES (Judete) ────────────────────────────
# 49 US states mapped to 41 Romanian counties (some counties repeat for less
# common states — realistic for a chain with uneven geographic coverage).
state_to_judet = {
    "California":             "Cluj",
    "New York":               "Iasi",
    "Texas":                  "Prahova",
    "Pennsylvania":           "Constanta",
    "Washington":             "Timis",
    "Illinois":               "Ilfov",
    "Ohio":                   "Brasov",
    "Florida":                "Dolj",
    "Michigan":               "Galati",
    "North Carolina":         "Arges",
    "Arizona":                "Sibiu",
    "Virginia":               "Bacau",
    "Georgia":                "Mures",
    "Tennessee":              "Suceava",
    "Colorado":               "Dambovita",
    "Indiana":                "Neamt",
    "Kentucky":               "Vrancea",
    "Massachusetts":          "Buzau",
    "New Jersey":             "Valcea",
    "Oregon":                 "Gorj",
    "Wisconsin":              "Mehedinti",
    "Utah":                   "Olt",
    "Nebraska":               "Teleorman",
    "Minnesota":              "Giurgiu",
    "Delaware":               "Calarasi",
    "Alabama":                "Ialomita",
    "South Carolina":         "Braila",
    "Missouri":               "Tulcea",
    "Oklahoma":               "Alba",
    "New Mexico":             "Bistrita-Nasaud",
    "Louisiana":              "Salaj",
    "Connecticut":            "Maramures",
    "Iowa":                   "Satu Mare",
    "Arizona":                "Harghita",
    "Nevada":                 "Covasna",
    "Rhode Island":           "Arad",
    "Mississippi":            "Bihor",
    "Arkansas":               "Hunedoara",
    "Montana":                "Caras-Severin",
    "New Hampshire":          "Botosani",
    "Maryland":               "Vaslui",
    "District of Columbia":   "Ilfov",
    "Kansas":                 "Cluj",
    "Vermont":                "Sibiu",
    "Maine":                  "Brasov",
    "South Dakota":           "Timis",
    "Idaho":                  "Constanta",
    "North Dakota":           "Iasi",
    "Wyoming":                "Prahova",
    "West Virginia":          "Dolj",
}
df["County"] = df["State"].map(state_to_judet)

# ── 5. RENAME CATEGORIES TO FRESHMART CONTEXT ─────────────────────────────────
category_map = {
    "Furniture":        "Home & Living",
    "Office Supplies":  "General Products",
    "Technology":       "Electronics",
}
df["Category"] = df["Category"].map(category_map)

# Sub-category — keep as-is, they still make sense under the new categories

# ── 6. DERIVE USEFUL COLUMNS ──────────────────────────────────────────────────
df["Order_Year"]  = df["Order_Date"].dt.year
df["Order_Month"] = df["Order_Date"].dt.month
df["Order_Quarter"] = df["Order_Date"].dt.quarter

# Shipping duration in days
df["Ship_Duration_Days"] = (df["Ship_Date"] - df["Order_Date"]).dt.days

# Profit margin (%) — avoid division by zero
df["Profit_Margin_Pct"] = np.where(
    df["Sales"] != 0,
    (df["Profit"] / df["Sales"] * 100).round(2),
    0.0
)

# Profitability flag
df["Is_Profitable"] = (df["Profit"] > 0).astype(int)

# Revenue per unit
df["Revenue_Per_Unit"] = (df["Sales"] / df["Quantity"]).round(2)

# ── 7. INTRODUCE MISSING VALUES (required by project specs) ──────────────────
# We intentionally inject NaN in ~3% of rows for two columns
# to allow demonstration of missing-value handling techniques.
np.random.seed(42)
n = len(df)

missing_idx_discount = np.random.choice(df.index, size=int(n * 0.03), replace=False)
missing_idx_ship_dur = np.random.choice(df.index, size=int(n * 0.03), replace=False)

df.loc[missing_idx_discount, "Discount"]           = np.nan
df.loc[missing_idx_ship_dur, "Ship_Duration_Days"] = np.nan

print(f"Introduced {df['Discount'].isna().sum()} missing values in 'Discount'")
print(f"Introduced {df['Ship_Duration_Days'].isna().sum()} missing values in 'Ship_Duration_Days'")

# ── 8. DROP COLUMNS NOT NEEDED ────────────────────────────────────────────────
# Drop original US geographic columns — replaced by County
df = df.drop(columns=["State", "Postal_Code", "City"])

# ── 9. REORDER COLUMNS FOR CLARITY ───────────────────────────────────────────
col_order = [
    "Row_ID", "Order_ID", "Order_Date", "Order_Year", "Order_Month",
    "Order_Quarter", "Ship_Date", "Ship_Mode", "Ship_Duration_Days",
    "Customer_ID", "Customer_Name", "Segment", "Country", "County",
    "Region", "Product_ID", "Product_Name", "Category", "Sub_Category",
    "Sales", "Quantity", "Discount", "Profit", "Profit_Margin_Pct",
    "Revenue_Per_Unit", "Is_Profitable",
]
df = df[col_order]

# ── 10. FINAL CHECKS ─────────────────────────────────────────────────────────
print(f"\nFinal dataset: {df.shape[0]} rows × {df.shape[1]} columns")
print(f"\nColumn list:\n{list(df.columns)}")
print(f"\nMissing values per column:\n{df.isnull().sum()[df.isnull().sum() > 0]}")
print(f"\nSample:\n{df.head(3).to_string()}")

# ── 11. EXPORT ────────────────────────────────────────────────────────────────
df.to_csv("FreshMart_Dataset.csv", index=False)
print("\nSaved: FreshMart_Dataset.csv")