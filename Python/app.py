import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import matplotlib.patches as mpatches
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable

from sklearn.preprocessing import LabelEncoder, StandardScaler, MinMaxScaler
from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.model_selection import train_test_split
from  sklearn.metrics import classification_report, confusion_matrix, ConfusionMatrixDisplay

import statsmodels.api as sm

import geopandas as gpd
from shapely.geometry import Point

import warnings
warnings.filterwarnings("ignore")

#PAGE CONFIG
st.set_page_config(
    page_title="FreshMart Romania - Analytics",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

#CONSTANTS - Romania county coordinates (for mapping)
COUNTY_COORDS = {
    "Alba": (46.07, 23.57), "Arad": (46.17, 21.31), "Arges": (44.85, 24.87),
    "Bacau": (46.57, 26.91), "Bihor": (47.05, 21.93), "Bistrita-Nasaud": (47.13, 24.50),
    "Botosani": (47.74, 26.67), "Brasov": (45.65, 25.61), "Braila": (45.27, 27.96),
    "Buzau": (45.15, 26.83), "Caras-Severin": (45.32, 22.07), "Calarasi": (44.20, 27.33),
    "Cluj": (46.77, 23.59), "Constanta": (44.18, 28.65), "Covasna": (45.85, 26.18),
    "Dambovita": (44.93, 25.46), "Dolj": (44.32, 23.80), "Galati": (45.44, 28.05),
    "Giurgiu": (43.90, 25.97), "Gorj": (44.95, 23.27), "Harghita": (46.36, 25.81),
    "Hunedoara": (45.71, 22.91), "Ialomita": (44.57, 27.35), "Iasi": (47.16, 27.59),
    "Ilfov": (44.56, 26.27), "Maramures": (47.66, 24.10), "Mehedinti": (44.64, 22.90),
    "Mures": (46.55, 24.56), "Neamt": (46.97, 26.38), "Olt": (44.43, 24.37),
    "Prahova": (44.94, 26.02), "Satu Mare": (47.79, 22.89), "Salaj": (47.19, 23.06),
    "Sibiu": (45.80, 24.15), "Suceava": (47.65, 26.25), "Teleorman": (43.90, 25.39),
    "Timis": (45.75, 21.22), "Tulcea": (45.18, 29.02), "Vaslui": (46.64, 27.73),
    "Valcea": (45.10, 24.37), "Vrancea": (45.70, 27.18),
}
 
CATEGORY_COLORS = {
    "Electronics":       "#2685D3DC",
    "Home & Living":     "#E89211FF",
    "General Products":  "#BDF2BF",
}

#DATA LOADING
@st.cache_data
def load_data(path: str="FreshMart_Dataset.csv") -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["Order_Date", "Ship_Date"])
    return df

#SIDEBAR 
def render_sidebar(df: pd.DataFrame):
    st.sidebar.image(
        "https://img.icons8.com/fluency/96/shopping-cart.png", width=72
    )
    st.sidebar.title("FreshMart Romania")
    st.sidebar.caption("Analytics Dashboard - 2014-2017")

    st.sidebar.markdown("---")
    st.sidebar.subheader("Global Filters")

    years = sorted(df["Order_Year"].unique().tolist())
    sel_years = st.sidebar.multiselect(
        "Order Year", years, default=years, key="sidebar_years"
    )

    categories = sorted(df["Category"].unique().tolist())
    sel_categories = st.sidebar.multiselect(
        "Category", categories, default=categories, key="sidebar_categories"
    )

    regions = sorted(df["Region"].unique().tolist())
    sel_regions = st.sidebar.multiselect(
        "Region", regions, default=regions, key="sidebar_regions"
    )

    segments = sorted(df["Segment"].unique().tolist())
    sel_segments = st.sidebar.multiselect(
        "Segment", segments, default=segments, key="sidebar_segments"
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown(
        "**Dataset:** 9,994 transactions · 26 columns  \n"
        "**Period:** Jan 2014 – Dec 2017  \n"
        "**Country:** Romania"
    )

    mask = (
        df["Order_Year"].isin(sel_years)
        & df["Category"].isin(sel_categories)
        & df["Region"].isin(sel_regions)
        & df["Segment"].isin(sel_segments)
    )

    return df[mask].copy()

# SECTION 1 - STREAMLIT DISPLAY + KPIs
def section_overview(df: pd.DataFrame):
    st.header("📊 1. Overview & KPI Dashboard")
    st.markdown(
        "Display using **Streamlit** widgets: metrics, dataframe preview, "
        "selectboxes, sliders, and expanders."
    )

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Revenue (RON)", f"{df['Sales'].sum():,.0f}")
    c2.metric("Total Profit (RON)",  f"{df['Profit'].sum():,.0f}")
    c3.metric("Transactions",        f"{len(df):,}")
    c4.metric("Avg Profit Margin",   f"{df['Profit_Margin_Pct'].mean():.1f}%")
    c5.metric("Profitable Orders",   f"{df['Is_Profitable'].mean()*100:.1f}%")

    st.markdown("---")
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.subheader("Sales & Profit by Year")
        year_agg = (
            df.groupby("Order_Year")[["Sales", "Profit"]]
            .sum()
            .reset_index()
            .rename(columns= {"Order_Year": "Year"})
        )
        fig, ax = plt.subplots(figsize=(7, 3.5))
        x = np.arange(len(year_agg))
        bars1 = ax.bar(x-0.2,year_agg["Sales"], 0.4, label ="Sales", color="#1976D2")
        bars1 = ax.bar(x - 0.2, year_agg["Sales"], 0.4, label="Sales", color="#1976D2")
        bars2 = ax.bar(x + 0.2, year_agg["Profit"], 0.4, label="Profit", color="#43A047")
        ax.set_xticks(x)
        ax.set_xticklabels(year_agg["Year"])
        ax.set_ylabel("RON")
        ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda v, _: f"{v/1e3:.0f}K"))
        ax.legend()
        ax.set_title("Annual Sales vs Profit", fontweight="bold")
        ax.spines[["top", "right"]].set_visible(False)
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    with col_right:
        st.subheader("Revenue by Category")
        cat_sales = df.groupby("Category")["Sales"].sum().sort_values()
        fig2, ax2 = plt.subplots(figsize=(4, 3.5))
        colors = [CATEGORY_COLORS.get(c, "#888888") for c in cat_sales.index]
        ax2.barh(cat_sales.index, cat_sales.values, color=colors)
        ax2.xaxis.set_major_formatter(mtick.FuncFormatter(lambda v, _: f"{v/1e3:.0f}K"))
        ax2.set_xlabel("RON")
        ax2.set_title("Sales by Category", fontweight="bold")
        ax2.spines[["top", "right"]].set_visible(False)
        fig2.tight_layout()
        st.pyplot(fig2)
        plt.close(fig2)
 
    with st.expander("View Raw Data Sample (first 100 rows)"):
        st.dataframe(df.head(100),use_container_width=True)

    with st.expander("Column Descriptions"):
        col_desc ={
           "Row_ID": "Unique row identifier",
            "Order_ID": "Unique order identifier",
            "Order_Date": "Date when the order was placed",
            "Order_Year/Month/Quarter": "Derived time components",
            "Ship_Date": "Date when the order was shipped",
            "Ship_Mode": "Shipping method chosen",
            "Ship_Duration_Days": "Days between order and shipment (has ~3% missing)",
            "Customer_ID / Name": "Customer identifiers",
            "Segment": "Customer segment: Consumer, Corporate, Home Office",
            "County / Region": "Romanian geographic breakdown",
            "Category / Sub_Category": "Product taxonomy",
            "Sales": "Revenue from the transaction (RON)",
            "Quantity": "Units sold",
            "Discount": "Discount rate applied (has ~3% missing)",
            "Profit": "Profit from the transaction (RON)",
            "Profit_Margin_Pct": "Profit / Sales x 100",
            "Revenue_Per_Unit": "Sales / Quantity",
            "Is_Profitable": "Binary: 1 if Profit > 0",
        }

        st.table(pd.DataFrame.from_dict(col_desc, orient="index", columns=["Description"]))


#SECTION 2 - GEOPANDAS MAPPING
def section_geopandas(df: pd.DataFrame):
    st.header("🗺️ 2. GeoPandas – Sales Map of Romania")
    st.markdown(
        "A **GeoDataFrame** is built from county-level aggregated sales. Each county "
        "is represented as a `Point` geometry (centroid). Bubble size encodes total "
        "revenue; colour encodes average profit margin."
    )

    metric_col= st.selectbox(
        "Metric for bubble colour",
        ["Profit_Margin_Pct", "Profit", "Sales", "Quantity"],
        key="geo_metric",
    )

    county_agg =(
        df.groupby("County")
        .agg(
            Total_Sales = ("Sales", "sum"),
            Avg_Profit_Margin = ("Profit_Margin_Pct", "mean"),
            Total_Profit = ("Profit", "sum"),
            Avg_Quantity = ("Quantity", "mean"),
            Orders = ("Row_ID", "count"),
        )
        .reset_index()
    )

    metric_map = {
        "Profit_Margin_Pct": "Avg_Profit_Margin",
        "Profit": "Total_Profit",
        "Sales": "Total_Sales",
        "Quantity": "Avg_Quantity",
    }

    county_agg["lat"] = county_agg["County"].map(lambda c: COUNTY_COORDS.get(c, (45.9, 24.9))[0])
    county_agg["lon"] = county_agg["County"].map(lambda c: COUNTY_COORDS.get(c, (45.9, 24.9))[1])

    geometry = [Point(lon, lat) for lat, lon in zip(county_agg["lat"], county_agg["lon"])]
    gdf = gpd.GeoDataFrame(county_agg, geometry=geometry, crs="EPSG:4326")
    
    color_col = metric_map[metric_col]
    norm = Normalize(vmin=gdf[color_col].min(), vmax=gdf[color_col].max())
    cmap = plt.cm.RdYlGn
    sizes = (gdf["Total_Sales"] / gdf["Total_Sales"].max()) * 800 + 30

    fig, ax = plt.subplots(figsize=(11, 7))
    ax.set_facecolor("#EAF2FB")
    fig.patch.set_facecolor("#F8FBFF")
 
    romania_bounds = {"minx": 20.2, "maxx": 29.8, "miny": 43.5, "maxy": 48.3}
    ax.set_xlim(romania_bounds["minx"], romania_bounds["maxx"])
    ax.set_ylim(romania_bounds["miny"], romania_bounds["maxy"])
    ax.set_aspect("equal")
 
    ax.axhline(y=44.5, color="#B0BEC5", linewidth=0.3, alpha=0.4)
    ax.axhline(y=46.0, color="#B0BEC5", linewidth=0.3, alpha=0.4)
    ax.axvline(x=22.0, color="#B0BEC5", linewidth=0.3, alpha=0.4)
    ax.axvline(x=25.5, color="#B0BEC5", linewidth=0.3, alpha=0.4)
    ax.axvline(x=28.0, color="#B0BEC5", linewidth=0.3, alpha=0.4)
 
    scatter = ax.scatter(
        gdf.geometry.x,
        gdf.geometry.y,
        s=sizes,
        c=gdf[color_col],
        cmap=cmap,
        norm=norm,
        alpha=0.85,
        edgecolors="white",
        linewidths=0.8,
        zorder=5,
    )
 
    for _, row in gdf.iterrows():
        if row["Total_Sales"] > gdf["Total_Sales"].quantile(0.6):
            ax.annotate(
                row["County"],
                xy=(row.geometry.x, row.geometry.y),
                xytext=(4, 4),
                textcoords="offset points",
                fontsize=6.5,
                color="#1A237E",
                fontweight="bold",
            )
 
    cb = fig.colorbar(scatter, ax=ax, shrink=0.6, pad=0.02)
    cb.set_label(metric_col, fontsize=9)
 
    from matplotlib.lines import Line2D
    size_vals = [gdf["Total_Sales"].min(), gdf["Total_Sales"].median(), gdf["Total_Sales"].max()]
    size_legend = [
        Line2D([0], [0], marker="o", color="w",
               markerfacecolor="#607D8B",
               markersize=np.sqrt((v / gdf["Total_Sales"].max()) * 800 + 30) / 1.5,
               label=f"RON {v:,.0f}")
        for v in size_vals
    ]
    ax.legend(handles=size_legend, title="Total Sales", loc="lower left",
              fontsize=7, title_fontsize=8)
 
    ax.set_title("FreshMart Romania – Sales by County\n(bubble size = total revenue, colour = selected metric)",
                 fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Longitude", fontsize=8)
    ax.set_ylabel("Latitude", fontsize=8)
    ax.tick_params(labelsize=7)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)
 
    st.subheader("County-Level Summary Table")
    st.dataframe(
        gdf[["County", "Orders", "Total_Sales", "Total_Profit", "Avg_Profit_Margin"]]
        .sort_values("Total_Sales", ascending=False)
        .rename(columns={
            "Total_Sales": "Sales (RON)",
            "Total_Profit": "Profit (RON)",
            "Avg_Profit_Margin": "Avg Margin (%)",
        })
        .reset_index(drop=True),
        use_container_width=True,
    )
 

#SECTION 3 - MISSING VALUES & EXTREME VALUES
def section_missing_extreme(df: pd.DataFrame):
    st.header("🔧 3. Missing Values & Extreme Values")
 
    st.subheader("3a. Missing Values Analysis")
    st.markdown(
        "The dataset has **~3% missing values** intentionally introduced in `Discount` "
        "and `Ship_Duration_Days` to simulate a realistic data quality scenario."
    )
 
    missing = df.isnull().sum()
    missing_pct = (missing / len(df) * 100).round(2)
    missing_df = pd.DataFrame({
        "Missing Count": missing,
        "Missing %": missing_pct,
    }).query("`Missing Count` > 0")

    col1, col2 = st.columns([1, 2])
    with col1:
        st.dataframe(missing_df, use_container_width=True)

    with col2:
        fig, ax = plt.subplots(figsize=(6, 2.5))
        cols_miss= missing_df.index.tolist()
        vals_miss= missing_df["Missing %"].values
        ax.barh(cols_miss, vals_miss, color=["#EF5350", "#FFA726"])
        ax.set_xlabel("Missing %")
        ax.set_title("Missing Values by Column", fontweight="bold")
        ax.spines[["top", "right"]].set_visible(False)
        for i, v in enumerate(vals_miss):
            ax.text(v + 0.05, i, f"{v:.2f}%", va="center", fontsize=9)
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    st.subheader("Imputation Strategy")
    strategy = st.radio(
        "Choose imputation method for missing values:",
        ["Median imputation", "Mean imputation", "Drop rows with missing values"],
        key="impute_strategy",
        horizontal=True,
    )

    df_imp = df.copy()
    if strategy == "Median imputation":
        df_imp["Discount"].fillna(df_imp["Discount"].median(), inplace=True)
        df_imp["Ship_Duration_Days"].fillna(df_imp["Ship_Duration_Days"].median(), inplace=True)
        note = "Filled with **median** — robust to outliers."
    elif strategy == "Mean imputation":
        df_imp["Discount"].fillna(df_imp["Discount"].mean(), inplace=True)
        df_imp["Ship_Duration_Days"].fillna(df_imp["Ship_Duration_Days"].mean(), inplace=True)
        note = "Filled with **mean** — sensitive to outliers."
    else:
        df_imp.dropna(subset= ["Discount", "Ship_Duration_Days"], inplace=True)
        note = f"Dropped rows → dataset reduced to **{len(df_imp):,}** rows."
    
    st.info(note)
    st.metric("Remaining missing values", int(df_imp[["Discount", "Ship_Duration_Days"]].isnull().sum().sum()))

    st.markdown("---")
    st.subheader("3b. Extreme Values (Outliers Detection)")
    st.markdown(
        "Using the **IQR method**: values below Q1 - 1.5·IQR or above Q3 + 1.5·IQR "
        "are flagged as outliers."
    )

    num_cols = ["Sales", "Profit", "Quantity", "Discount", "Ship_Duration_Days", "Revenue_Per_Unit"]
    outlier_col = st.selectbox("Select column to inspect", num_cols, key="outlier_col")

    col_data = df_imp[outlier_col].dropna()
    Q1, Q3 = col_data.quantile(0.25), col_data.quantile(0.75)
    IQR = Q3 - Q1
    lower, upper = Q1 - 1.5 * IQR, Q3 + 1.5 * IQR
    n_outliers = ((col_data < lower) | (col_data > upper)).sum()
    
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Q1", f"{Q1:.2f}")
    col_b.metric("Q3", f"{Q3:.2f}")
    col_c.metric("Outliers detected", f"{n_outliers} ({n_outliers/len(col_data)*100:.1f}%)")

    fig, axes= plt.subplots(1, 2, figsize=(10, 3.5))

    axes[0].boxplot(col_data, vert=True, patch_artist=True,
                    boxprops=dict(facecolor="#BBDEFB"),
                    medianprops=dict(color="#1565C0", linewidth=2))
    axes[0].set_title(f"Boxplot – {outlier_col}", fontweight="bold")
    axes[0].axhline(upper, color="red", linestyle="--", linewidth=1, label=f"Upper fence: {upper:.1f}")
    axes[0].axhline(lower, color="orange", linestyle="--", linewidth=1, label=f"Lower fence: {lower:.1f}")
    axes[0].legend(fontsize=7)
    axes[0].spines[["top", "right"]].set_visible(False)
 
    axes[1].hist(col_data, bins=40, color="#42A5F5", edgecolor="white")
    axes[1].axvline(upper, color="red",    linestyle="--", linewidth=1.5, label="Upper fence")
    axes[1].axvline(lower, color="orange", linestyle="--", linewidth=1.5, label="Lower fence")
    axes[1].set_title(f"Distribution – {outlier_col}", fontweight="bold")
    axes[1].set_xlabel(outlier_col)
    axes[1].legend(fontsize=7)
    axes[1].spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)
 
    handle = st.radio(
        "Outlier treatment:",
        ["Keep all", "Cap to fences (Winsorize)", "Remove outliers"],
        key="outlier_handle", horizontal=True,
    )
    if handle == "Cap to fences (Winsorize)":
        st.success(f"Values in `{outlier_col}` capped to [{lower:.2f}, {upper:.2f}].")
    elif handle == "Remove outliers":
        n_removed = n_outliers
        st.success(f"Would remove {n_removed} rows ({n_removed/len(df)*100:.1f}% of data).")
    else:
        st.info("No treatment applied — outliers retained.")
 
# SECTION 4 — ENCODING METHODS
def section_encoding(df: pd.DataFrame):
    st.header("🔤 4. Encoding Methods")
    st.markdown(
        "Categorical variables must be converted to numeric form before applying "
        "machine-learning algorithms. Two standard techniques are demonstrated:"
    )
 
    cat_cols = ["Segment", "Category", "Region", "Ship_Mode"]
    chosen = st.multiselect("Select columns to encode", cat_cols,
                            default=["Segment", "Category"], key="enc_cols")
    enc_method = st.radio("Encoding method", ["Label Encoding", "One-Hot Encoding"],
                          key="enc_method", horizontal=True)
 
    df_enc = df[chosen].copy().head(200)
 
    if enc_method == "Label Encoding":
        le = LabelEncoder()
        result_df = df_enc.copy()
        mapping_info = {}
        for col in chosen:
            result_df[col + "_encoded"] = le.fit_transform(df_enc[col].astype(str))
            mapping_info[col] = dict(zip(le.classes_, le.transform(le.classes_)))
        st.write("**Label Encoding Result (first 10 rows):**")
        st.dataframe(result_df.head(10), use_container_width=True)
        st.write("**Encoding mappings:**")
        for col, mapping in mapping_info.items():
            st.write(f"`{col}`: {mapping}")
 
    else:
        result_ohe = pd.get_dummies(df_enc, columns=chosen, drop_first=False)
        st.write(f"**One-Hot Encoding Result** — {result_ohe.shape[1]} columns after encoding (first 10 rows):")
        st.dataframe(result_ohe.head(10), use_container_width=True)
        st.caption(
            "Each categorical level becomes a binary (0/1) column. "
            "`drop_first=False` keeps all levels for interpretability."
        )
 
    st.markdown("---")
    st.markdown(
        "**When to use each:**\n"
        "- **Label Encoding** — ordinal variables or tree-based models where order doesn't introduce bias.\n"
        "- **One-Hot Encoding** — nominal variables with no natural order; preferred for linear/distance-based models."
    )
 
 
# SECTION 5 — SCALING METHODS
def section_scaling(df: pd.DataFrame):
    st.header("📐 5. Scaling Methods")
    st.markdown(
        "Feature scaling is essential for distance-based and gradient-based algorithms. "
        "The two most common methods are compared side by side."
    )
 
    num_features = ["Sales", "Profit", "Quantity", "Revenue_Per_Unit", "Profit_Margin_Pct"]
    selected_feat = st.multiselect("Select features to scale", num_features,
                                   default=["Sales", "Profit", "Quantity"], key="scale_feats")
 
    if not selected_feat:
        st.warning("Select at least one feature.")
        return
 
    X = df[selected_feat].dropna().head(500)
    scaler_std  = StandardScaler()
    scaler_mms  = MinMaxScaler()
 
    X_std = pd.DataFrame(scaler_std.fit_transform(X), columns=[c+"_std"  for c in selected_feat])
    X_mms = pd.DataFrame(scaler_mms.fit_transform(X), columns=[c+"_mms"  for c in selected_feat])
 
    col1, col2 = st.columns(2)
 
    with col1:
        st.subheader("StandardScaler (Z-score)")
        st.caption("μ=0, σ=1 · Best for normally distributed data and linear models.")
        st.dataframe(X_std.describe().round(3), use_container_width=True)
 
    with col2:
        st.subheader("MinMaxScaler [0, 1]")
        st.caption("Scales to [0,1] range · Best for bounded distributions and neural nets.")
        st.dataframe(X_mms.describe().round(3), use_container_width=True)
 
    fig, axes = plt.subplots(1, len(selected_feat), figsize=(4 * len(selected_feat), 3.5))
    if len(selected_feat) == 1:
        axes = [axes]
    for i, col in enumerate(selected_feat):
        axes[i].hist(X[col],                    bins=30, alpha=0.5, label="Original",  color="#78909C")
        axes[i].hist(X_std[col+"_std"],          bins=30, alpha=0.5, label="Z-score",   color="#1E88E5")
        axes[i].hist(X_mms[col+"_mms"],          bins=30, alpha=0.5, label="MinMax",    color="#43A047")
        axes[i].set_title(col, fontweight="bold", fontsize=9)
        axes[i].legend(fontsize=7)
        axes[i].spines[["top", "right"]].set_visible(False)
    fig.suptitle("Original vs Scaled Distributions", fontweight="bold", fontsize=11)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)
 
 
# SECTION 6 — STATISTICAL PROCESSING, GROUPING & AGGREGATION
def section_statistics(df: pd.DataFrame):
    st.header("📈 6. Statistical Processing, Grouping & Aggregation")
    st.markdown(
        "Comprehensive use of **pandas** `groupby`, `agg`, `pivot_table`, `describe`, "
        "and `corr` to extract business insights from the FreshMart dataset."
    )
 
    # 6a Descriptive statistics
    st.subheader("6a. Descriptive Statistics")
    num_cols = ["Sales", "Profit", "Quantity", "Discount", "Profit_Margin_Pct", "Revenue_Per_Unit"]
    st.dataframe(df[num_cols].describe().round(2), use_container_width=True)
 
    st.markdown("---")
 
    # 6b Groupby aggregation
    st.subheader("6b. Multi-Level Groupby Aggregation")
    group_col = st.selectbox("Group by", ["Category", "Region", "Segment", "Ship_Mode",
                                           "Order_Year", "Order_Quarter"], key="grp_col")
    agg_df = (
        df.groupby(group_col)
        .agg(
            Transactions  =("Row_ID",             "count"),
            Total_Sales   =("Sales",              "sum"),
            Total_Profit  =("Profit",             "sum"),
            Avg_Margin    =("Profit_Margin_Pct",  "mean"),
            Avg_Discount  =("Discount",           "mean"),
            Total_Qty     =("Quantity",           "sum"),
        )
        .round(2)
        .sort_values("Total_Sales", ascending=False)
    )
    st.dataframe(agg_df, use_container_width=True)
 
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    agg_sorted = agg_df.sort_values("Total_Sales")
    axes[0].barh(agg_sorted.index.astype(str), agg_sorted["Total_Sales"],
                 color="#42A5F5", edgecolor="white")
    axes[0].set_title(f"Total Sales by {group_col}", fontweight="bold")
    axes[0].xaxis.set_major_formatter(mtick.FuncFormatter(lambda v,_: f"{v/1e3:.0f}K"))
    axes[0].spines[["top","right"]].set_visible(False)
 
    axes[1].barh(agg_sorted.index.astype(str), agg_sorted["Avg_Margin"],
                 color=["#EF5350" if v < 0 else "#66BB6A" for v in agg_sorted["Avg_Margin"]])
    axes[1].set_title(f"Avg Profit Margin by {group_col}", fontweight="bold")
    axes[1].set_xlabel("%")
    axes[1].axvline(0, color="black", linewidth=0.8)
    axes[1].spines[["top","right"]].set_visible(False)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)
 
    st.markdown("---")
 
    # 6c Pivot table
    st.subheader("6c. Pivot Table - Sales by Region x Category")
    pivot = df.pivot_table(
        values="Sales", index="Region", columns="Category",
        aggfunc="sum", margins=True, margins_name="TOTAL"
    ).round(0)
    st.dataframe(pivot, use_container_width=True)
 
    st.markdown("---")
 
    # 6d Correlation matrix
    st.subheader("6d. Correlation Matrix")
    corr = df[num_cols].corr().round(3)
    fig3, ax3 = plt.subplots(figsize=(7, 5))
    im = ax3.imshow(corr.values, cmap="coolwarm", vmin=-1, vmax=1)
    ax3.set_xticks(range(len(num_cols)))
    ax3.set_yticks(range(len(num_cols)))
    ax3.set_xticklabels(num_cols, rotation=40, ha="right", fontsize=8)
    ax3.set_yticklabels(num_cols, fontsize=8)
    for i in range(len(num_cols)):
        for j in range(len(num_cols)):
            ax3.text(j, i, f"{corr.values[i,j]:.2f}",
                     ha="center", va="center", fontsize=7.5,
                     color="white" if abs(corr.values[i,j]) > 0.5 else "black")
    fig3.colorbar(im, ax=ax3, shrink=0.8)
    ax3.set_title("Pearson Correlation Matrix", fontweight="bold")
    fig3.tight_layout()
    st.pyplot(fig3)
    plt.close(fig3)
 
    st.markdown("---")
 
    # 6e Monthly trend
    st.subheader("6e. Monthly Sales Trend (all years)")
    monthly = (
        df.groupby(["Order_Year", "Order_Month"])["Sales"]
        .sum()
        .reset_index()
        .sort_values(["Order_Year", "Order_Month"])
    )
    monthly["Period"] = monthly["Order_Year"].astype(str) + "-" + monthly["Order_Month"].astype(str).str.zfill(2)
    fig4, ax4 = plt.subplots(figsize=(13, 3.5))
    for yr, grp in monthly.groupby("Order_Year"):
        ax4.plot(grp["Period"], grp["Sales"], marker="o", markersize=3, linewidth=1.5, label=str(yr))
    ax4.set_xticks(ax4.get_xticks()[::3])
    ax4.set_xticklabels(ax4.get_xticklabels(), rotation=60, ha="right", fontsize=7)
    ax4.yaxis.set_major_formatter(mtick.FuncFormatter(lambda v, _: f"{v/1e3:.0f}K"))
    ax4.set_title("Monthly Revenue Trend by Year", fontweight="bold")
    ax4.set_ylabel("Sales (RON)")
    ax4.legend(title="Year")
    ax4.spines[["top","right"]].set_visible(False)
    ax4.grid(axis="y", alpha=0.3)
    fig4.tight_layout()
    st.pyplot(fig4)
    plt.close(fig4)
 
 
# SECTION 7 — MERGE / JOIN
def section_merge(df: pd.DataFrame):
    st.header("🔗 7. Merge / Join Datasets")
    st.markdown(
        "Two derived DataFrames are extracted from the main dataset and then joined "
        "using different **pandas merge strategies**, simulating a multi-table "
        "warehouse schema (orders + product catalog)."
    )
 
    # Simulate product catalog table
    product_catalog = (
        df.groupby("Product_ID")
        .agg(
            Product_Name  =("Product_Name", "first"),
            Category =("Category", "first"),
            Sub_Category =("Sub_Category", "first"),
            Avg_Unit_Price=("Revenue_Per_Unit","mean"),
        )
        .reset_index()
        .round(2)
    )
    product_catalog["In_Stock"] = np.random.choice([True, False], size=len(product_catalog), p=[0.9, 0.1])
    product_catalog["Supplier"] = np.random.choice(
        ["FreshSupply SRL", "RomLogistics SA", "EastFresh SRL", "PremiumDist SRL"],
        size=len(product_catalog)
    )
 
    # Transaction summary table
    transactions = (
        df.groupby("Product_ID")
        .agg(
            Total_Revenue=("Sales",    "sum"),
            Total_Profit =("Profit",   "sum"),
            Order_Count  =("Row_ID",   "count"),
        )
        .reset_index()
        .round(2)
    )
 
    st.subheader("Source Tables")
    c1, c2 = st.columns(2)
    with c1:
        st.caption(f"**Product Catalog** — {len(product_catalog)} products")
        st.dataframe(product_catalog.head(8), use_container_width=True)
    with c2:
        st.caption(f"**Transaction Summary** — {len(transactions)} products")
        st.dataframe(transactions.head(8), use_container_width=True)
 
    join_type = st.radio(
        "Join type", ["inner", "left", "right", "outer"],
        horizontal=True, key="join_type"
    )
 
    merged = product_catalog.merge(transactions, on="Product_ID", how=join_type)
 
    st.subheader(f"Result: {join_type.upper()} JOIN on `Product_ID`")
    st.metric("Rows in result", len(merged))
    st.dataframe(merged.head(20), use_container_width=True)
 
    st.markdown("---")
    st.subheader("Business Insight from Merged Table")
    st.markdown("Top 10 products by Total Revenue with full catalog context:")
    top10 = (
        merged.sort_values("Total_Revenue", ascending=False)
        .head(10)[["Product_Name", "Category", "Supplier", "In_Stock",
                   "Total_Revenue", "Total_Profit", "Order_Count"]]
    )
    fig, ax = plt.subplots(figsize=(10, 4))
    colors = [CATEGORY_COLORS.get(c, "#888") for c in top10["Category"]]
    bars = ax.barh(top10["Product_Name"].str[:35], top10["Total_Revenue"], color=colors)
    ax.xaxis.set_major_formatter(mtick.FuncFormatter(lambda v,_: f"{v/1e3:.0f}K"))
    ax.set_title("Top 10 Products by Revenue (post-merge)", fontweight="bold")
    ax.set_xlabel("Total Revenue (RON)")
    patches = [mpatches.Patch(color=v, label=k) for k,v in CATEGORY_COLORS.items()]
    ax.legend(handles=patches, loc="lower right", fontsize=8)
    ax.spines[["top","right"]].set_visible(False)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)
 
 
# SECTION 8 — MATPLOTLIB VISUALISATIONS
def section_matplotlib(df: pd.DataFrame):
    st.header("🎨 8. Matplotlib Visualisations")
    st.markdown(
        "A gallery of six chart types produced exclusively with **matplotlib**, "
        "showcasing diverse visual encodings."
    )
 
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Scatter", "Stacked Bar", "Pie", "Heatmap", "Time Series", "Histogram"
    ])
 
    with tab1:
        st.subheader("Sales vs Profit (coloured by Category)")
        sample = df.sample(min(1500, len(df)), random_state=42)
        fig, ax = plt.subplots(figsize=(9, 5))
        for cat, grp in sample.groupby("Category"):
            ax.scatter(grp["Sales"], grp["Profit"],
                       alpha=0.45, s=18, label=cat, color=CATEGORY_COLORS.get(cat, "#888888"))
        ax.axhline(0, color="black", linewidth=0.8, linestyle="--")
        ax.set_xlabel("Sales (RON)", fontsize=10)
        ax.set_ylabel("Profit (RON)", fontsize=10)
        ax.set_title("Sales vs Profit by Category", fontweight="bold", fontsize=12)
        ax.legend(fontsize=9)
        ax.spines[["top","right"]].set_visible(False)
        fig.tight_layout()
        st.pyplot(fig); plt.close(fig)
 
    with tab2:
        st.subheader("Quarterly Revenue — Stacked by Category")
        q_cat = (
            df.groupby(["Order_Quarter", "Category"])["Sales"]
            .sum()
            .unstack(fill_value=0)
        )
        fig, ax = plt.subplots(figsize=(8, 4))
        bottom = np.zeros(4)
        for cat in q_cat.columns:
            vals = q_cat[cat].values
            ax.bar([f"Q{q}" for q in q_cat.index], vals, bottom=bottom,
                   label=cat, color=CATEGORY_COLORS.get(cat, "#888888"), edgecolor="white")
            bottom += vals
        ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda v,_: f"{v/1e3:.0f}K"))
        ax.set_title("Quarterly Sales – Stacked by Category", fontweight="bold")
        ax.set_ylabel("Revenue (RON)")
        ax.legend()
        ax.spines[["top","right"]].set_visible(False)
        fig.tight_layout()
        st.pyplot(fig); plt.close(fig)
 
    with tab3:
        st.subheader("Revenue Share by Segment")
        seg = df.groupby("Segment")["Sales"].sum()
        colors_pie = ["#42A5F5", "#66BB6A", "#FFA726"]
        fig, ax = plt.subplots(figsize=(6, 5))
        wedges, texts, autotexts = ax.pie(
            seg.values, labels=seg.index, autopct="%1.1f%%",
            colors=colors_pie, startangle=140,
            wedgeprops=dict(edgecolor="white", linewidth=2)
        )
        for at in autotexts:
            at.set_fontsize(11)
        ax.set_title("Revenue Share by Customer Segment", fontweight="bold")
        fig.tight_layout()
        st.pyplot(fig); plt.close(fig)
 
    with tab4:
        st.subheader("Heatmap – Average Profit Margin by Region × Category")
        heat = df.pivot_table(
            values="Profit_Margin_Pct", index="Region", columns="Category", aggfunc="mean"
        ).round(1)
        fig, ax = plt.subplots(figsize=(7, 4))
        im = ax.imshow(heat.values, cmap="RdYlGn", aspect="auto")
        ax.set_xticks(range(len(heat.columns))); ax.set_xticklabels(heat.columns, fontsize=9)
        ax.set_yticks(range(len(heat.index)));   ax.set_yticklabels(heat.index, fontsize=9)
        for i in range(len(heat.index)):
            for j in range(len(heat.columns)):
                ax.text(j, i, f"{heat.values[i,j]:.1f}%", ha="center", va="center",
                        fontsize=9, color="black")
        fig.colorbar(im, ax=ax, label="Avg Profit Margin %")
        ax.set_title("Avg Profit Margin % – Region × Category", fontweight="bold")
        fig.tight_layout()
        st.pyplot(fig); plt.close(fig)
 
    with tab5:
        st.subheader("Cumulative Revenue by Year")
        cum = (
            df.sort_values("Order_Date")
            .groupby("Order_Year")
            .apply(lambda g: g.set_index("Order_Date")["Sales"].cumsum())
            .reset_index()
        )
        fig, ax = plt.subplots(figsize=(10, 4))
        line_colors = ["#1E88E5","#43A047","#FB8C00","#E53935"]
        for i, (yr, grp) in enumerate(df.groupby("Order_Year")):
            g = grp.sort_values("Order_Date")
            ax.plot(range(len(g)), g["Sales"].cumsum().values,
                    label=str(yr), color=line_colors[i], linewidth=1.8)
        ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda v,_: f"{v/1e3:.0f}K"))
        ax.set_xlabel("Transaction index (within year)")
        ax.set_ylabel("Cumulative Sales (RON)")
        ax.set_title("Cumulative Sales Trajectory by Year", fontweight="bold")
        ax.legend(title="Year"); ax.grid(alpha=0.3)
        ax.spines[["top","right"]].set_visible(False)
        fig.tight_layout()
        st.pyplot(fig); plt.close(fig)
 
    with tab6:
        st.subheader("Profit Margin Distribution by Category")
        fig, ax = plt.subplots(figsize=(9, 4))
        for cat, grp in df.groupby("Category"):
            data = grp["Profit_Margin_Pct"].dropna()
            ax.hist(data, bins=40, alpha=0.55, label=cat,
                    color=CATEGORY_COLORS.get(cat, "#888888"), edgecolor="none")
        ax.axvline(0, color="black", linestyle="--", linewidth=1)
        ax.set_xlabel("Profit Margin %")
        ax.set_ylabel("Frequency")
        ax.set_title("Profit Margin Distribution by Category", fontweight="bold")
        ax.legend(); ax.spines[["top","right"]].set_visible(False)
        fig.tight_layout()
        st.pyplot(fig); plt.close(fig)
 
 
# SECTION 9 — SCIKIT-LEARN (K-MEANS + LOGISTIC REGRESSION)
def section_sklearn(df: pd.DataFrame):
    st.header("🤖 9. Scikit-learn - Clustering & Logistic Regression")
 
    # ── 9a K-MEANS CLUSTERING ──────────────────────────────────────────────
    st.subheader("9a. K-Means Customer Segmentation (RFM-style)")
    st.markdown(
        "Each customer is aggregated into three features:\n"
        "- **Frequency** — number of orders\n"
        "- **Monetary** — total spend\n"
        "- **Avg Discount** — price sensitivity\n\n"
        "K-Means groups customers into clusters; StandardScaler normalises features beforehand."
    )
 
    customer_agg = (
        df.groupby("Customer_ID")
        .agg(
            Frequency    =("Order_ID",   "nunique"),
            Monetary     =("Sales",      "sum"),
            Avg_Discount =("Discount",   "mean"),
            Avg_Profit   =("Profit",     "mean"),
        )
        .fillna(0)
        .reset_index()
    )
 
    k = st.slider("Number of clusters (K)", 2, 6, 3, key="kmeans_k")
 
    X_km = customer_agg[["Frequency", "Monetary", "Avg_Discount"]].values
    scaler_km = StandardScaler()
    X_km_scaled = scaler_km.fit_transform(X_km)
 
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = km.fit_predict(X_km_scaled)
    customer_agg["Cluster"] = labels
 
    # Elbow method
    inertias = []
    K_range = range(2, 8)
    for kk in K_range:
        inertias.append(KMeans(n_clusters=kk, random_state=42, n_init=10).fit(X_km_scaled).inertia_)
 
    col_left, col_right = st.columns([1, 1])
 
    with col_left:
        fig, ax = plt.subplots(figsize=(5, 3.5))
        ax.plot(list(K_range), inertias, "o-", color="#1E88E5", linewidth=2)
        ax.axvline(k, color="red", linestyle="--", linewidth=1, label=f"Selected K={k}")
        ax.set_xlabel("K"); ax.set_ylabel("Inertia")
        ax.set_title("Elbow Method", fontweight="bold")
        ax.legend(); ax.spines[["top","right"]].set_visible(False)
        fig.tight_layout(); st.pyplot(fig); plt.close(fig)
 
    with col_right:
        cluster_summary = (
            customer_agg.groupby("Cluster")
            [["Frequency","Monetary","Avg_Discount","Avg_Profit"]]
            .mean()
            .round(2)
        )
        st.write("**Cluster Centroids:**")
        st.dataframe(cluster_summary, use_container_width=True)
 
    palette = plt.cm.tab10(np.linspace(0, 1, k))
    fig2, axes = plt.subplots(1, 2, figsize=(12, 4.5))
    for c in range(k):
        mask_c = customer_agg["Cluster"] == c
        axes[0].scatter(
            customer_agg.loc[mask_c, "Frequency"],
            customer_agg.loc[mask_c, "Monetary"],
            alpha=0.55, s=20, color=palette[c], label=f"Cluster {c}"
        )
    axes[0].set_xlabel("Order Frequency"); axes[0].set_ylabel("Total Spend (RON)")
    axes[0].set_title("Clusters: Frequency vs Monetary", fontweight="bold")
    axes[0].legend(fontsize=8); axes[0].spines[["top","right"]].set_visible(False)
 
    for c in range(k):
        mask_c = customer_agg["Cluster"] == c
        axes[1].scatter(
            customer_agg.loc[mask_c, "Monetary"],
            customer_agg.loc[mask_c, "Avg_Discount"],
            alpha=0.55, s=20, color=palette[c], label=f"Cluster {c}"
        )
    axes[1].set_xlabel("Total Spend (RON)"); axes[1].set_ylabel("Avg Discount Rate")
    axes[1].set_title("Clusters: Monetary vs Discount", fontweight="bold")
    axes[1].legend(fontsize=8); axes[1].spines[["top","right"]].set_visible(False)
    fig2.tight_layout(); st.pyplot(fig2); plt.close(fig2)
 
    st.markdown("---")
 
    # ── 9b LOGISTIC REGRESSION ────────────────────────────────────────────
    st.subheader("9b. Logistic Regression – Predicting Order Profitability")
    st.markdown(
        "Binary target: `Is_Profitable` (1 = profit > 0). "
        "Features: `Sales`, `Quantity`, `Discount`, `Ship_Duration_Days`, "
        "encoded `Category` and `Segment`."
    )
 
    df_lr = df[["Sales","Quantity","Discount","Ship_Duration_Days",
                "Category","Segment","Is_Profitable"]].dropna().copy()
 
    le_cat = LabelEncoder(); le_seg = LabelEncoder()
    df_lr["Cat_enc"] = le_cat.fit_transform(df_lr["Category"])
    df_lr["Seg_enc"] = le_seg.fit_transform(df_lr["Segment"])
 
    feature_cols = ["Sales","Quantity","Discount","Ship_Duration_Days","Cat_enc","Seg_enc"]
    X_lr = df_lr[feature_cols].values
    y_lr = df_lr["Is_Profitable"].values
 
    X_lr_scaled = StandardScaler().fit_transform(X_lr)
    X_train, X_test, y_train, y_test = train_test_split(
        X_lr_scaled, y_lr, test_size=0.2, random_state=42, stratify=y_lr
    )
 
    lr = LogisticRegression(max_iter=500, random_state=42)
    lr.fit(X_train, y_train)
    y_pred = lr.predict(X_test)
 
    report = classification_report(y_test, y_pred, output_dict=True)
    report_df = pd.DataFrame(report).T.round(3)
 
    col_a, col_b = st.columns([1.2, 1])
    with col_a:
        st.write("**Classification Report:**")
        st.dataframe(report_df, use_container_width=True)
    with col_b:
        fig3, ax3 = plt.subplots(figsize=(4, 3.5))
        cm = confusion_matrix(y_test, y_pred)
        disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=["Not Profitable","Profitable"])
        disp.plot(ax=ax3, colorbar=False, cmap="Blues")
        ax3.set_title("Confusion Matrix", fontweight="bold")
        fig3.tight_layout(); st.pyplot(fig3); plt.close(fig3)
 
    coef_df = pd.DataFrame({
        "Feature": feature_cols,
        "Coefficient": lr.coef_[0]
    }).sort_values("Coefficient")
    fig4, ax4 = plt.subplots(figsize=(7, 3.5))
    ax4.barh(coef_df["Feature"], coef_df["Coefficient"],
             color=["#EF5350" if v < 0 else "#43A047" for v in coef_df["Coefficient"]])
    ax4.axvline(0, color="black", linewidth=0.8)
    ax4.set_title("Logistic Regression Coefficients", fontweight="bold")
    ax4.spines[["top","right"]].set_visible(False)
    fig4.tight_layout(); st.pyplot(fig4); plt.close(fig4)
 
 
# SECTION 10 — STATSMODELS MULTIPLE REGRESSION
def section_statsmodels(df: pd.DataFrame):
    st.header("📉 10. Statsmodels – Multiple Linear Regression")
    st.markdown(
        "**Objective:** Model `Profit` as a function of `Sales`, `Quantity`, `Discount`, "
        "`Ship_Duration_Days`, and categorical dummies for `Category` and `Segment`. "
        "The full OLS regression summary produced by **statsmodels** is reported below."
    )
 
    # Select relevant columns and coerce numeric types to avoid object-dtype issues
    df_ols = df[["Profit","Sales","Quantity","Discount","Ship_Duration_Days",
                 "Category","Segment"]].copy()

    # Coerce numeric columns, invalid parsing becomes NaN
    for _col in ["Profit", "Sales", "Quantity", "Discount", "Ship_Duration_Days"]:
        df_ols[_col] = pd.to_numeric(df_ols[_col], errors="coerce")

    # Create categorical dummies
    cat_dummies = pd.get_dummies(df_ols["Category"].astype(str), prefix="Cat", drop_first=True)
    seg_dummies = pd.get_dummies(df_ols["Segment"].astype(str), prefix="Seg", drop_first=True)

    # Build design matrix and target, then ensure numeric dtype
    X_ols = pd.concat([
        df_ols[["Sales","Quantity","Discount","Ship_Duration_Days"]],
        cat_dummies, seg_dummies
    ], axis=1)
    X_ols = X_ols.apply(pd.to_numeric, errors="coerce")
    X_ols = sm.add_constant(X_ols)
    y_ols = pd.to_numeric(df_ols["Profit"], errors="coerce")

    # Drop any rows with NaNs introduced by coercion
    valid_mask = X_ols.notnull().all(axis=1) & y_ols.notnull()
    X_ols = X_ols.loc[valid_mask]
    y_ols = y_ols.loc[valid_mask]

    if X_ols.shape[0] == 0:
        st.warning("No valid rows available for OLS after coercing to numeric types.")
        return

    # Ensure numeric numpy arrays for statsmodels (float dtype) and aligned indices
    X_ols = X_ols.astype(float).reset_index(drop=True)
    y_ols = y_ols.astype(float).reset_index(drop=True)
 
    model = sm.OLS(y_ols, X_ols).fit()
 
    st.subheader("OLS Regression Summary")
    st.text(str(model.summary()))
 
    st.markdown("---")
 
    # Key stats
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("R²",            f"{model.rsquared:.4f}")
    c2.metric("Adj. R²",       f"{model.rsquared_adj:.4f}")
    c3.metric("F-statistic",   f"{model.fvalue:.2f}")
    c4.metric("Prob (F-stat)", f"{model.f_pvalue:.2e}")
 
    st.markdown("---")
 
    # Coefficient chart
    coef_df = (
        model.params
        .reset_index()
        .rename(columns={"index": "Variable", 0: "Coefficient"})
        .merge(
            model.pvalues.reset_index().rename(columns={"index": "Variable", 0: "p_value"}),
            on="Variable"
        )
        .query("Variable != 'const'")
        .sort_values("Coefficient")
    )
 
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
 
    bar_colors = ["#EF5350" if v < 0 else "#43A047" for v in coef_df["Coefficient"]]
    axes[0].barh(coef_df["Variable"], coef_df["Coefficient"], color=bar_colors)
    axes[0].axvline(0, color="black", linewidth=0.8)
    axes[0].set_title("OLS Coefficients", fontweight="bold")
    axes[0].spines[["top","right"]].set_visible(False)
 
    # Actual vs Predicted
    y_pred_ols = model.fittedvalues
    sample_idx = np.random.choice(len(y_ols), size=min(800, len(y_ols)), replace=False)
    axes[1].scatter(y_ols.iloc[sample_idx], y_pred_ols.iloc[sample_idx],
                    alpha=0.3, s=10, color="#1E88E5")
    lims = [min(y_ols.min(), y_pred_ols.min()), max(y_ols.max(), y_pred_ols.max())]
    axes[1].plot(lims, lims, "r--", linewidth=1.5, label="Perfect fit")
    axes[1].set_xlabel("Actual Profit (RON)"); axes[1].set_ylabel("Predicted Profit (RON)")
    axes[1].set_title("Actual vs Predicted Profit", fontweight="bold")
    axes[1].legend(fontsize=8); axes[1].spines[["top","right"]].set_visible(False)
    fig.tight_layout()
    st.pyplot(fig); plt.close(fig)
 
    st.markdown("---")
    st.subheader("Residual Analysis")
    residuals = model.resid
    fig2, axes2 = plt.subplots(1, 2, figsize=(11, 3.5))
    axes2[0].hist(residuals, bins=60, color="#42A5F5", edgecolor="white")
    axes2[0].set_title("Residuals Distribution", fontweight="bold")
    axes2[0].set_xlabel("Residual"); axes2[0].spines[["top","right"]].set_visible(False)
 
    axes2[1].scatter(y_pred_ols.iloc[sample_idx], residuals.iloc[sample_idx],
                     alpha=0.3, s=10, color="#FB8C00")
    axes2[1].axhline(0, color="red", linestyle="--", linewidth=1)
    axes2[1].set_xlabel("Fitted values"); axes2[1].set_ylabel("Residuals")
    axes2[1].set_title("Residuals vs Fitted", fontweight="bold")
    axes2[1].spines[["top","right"]].set_visible(False)
    fig2.tight_layout(); st.pyplot(fig2); plt.close(fig2)
 
 
# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
def main():
    df_raw = load_data("Data/FreshMart_Dataset.csv")
    df = render_sidebar(df_raw)
 
    if df.empty:
        st.warning("No data matches the current filters. Please adjust the sidebar.")
        return
 
    st.title("🛒 FreshMart Romania - Analytics Platform")
    st.caption(
        "Software Packages Project · IIIrd Year ECSI · ASE Bucharest · 2014–2017 Sales Data"
    )
    st.markdown("---")
 
    pages = {
        "1 · Overview & KPIs":              section_overview,
        "2 · GeoPandas Map":                section_geopandas,
        "3 · Missing & Extreme Values":     section_missing_extreme,
        "4 · Encoding Methods":             section_encoding,
        "5 · Scaling Methods":              section_scaling,
        "6 · Statistics & Aggregation":     section_statistics,
        "7 · Merge / Join":                 section_merge,
        "8 · Matplotlib Gallery":           section_matplotlib,
        "9 · Scikit-learn (ML)":            section_sklearn,
        "10 · Statsmodels (Regression)":    section_statsmodels,
    }

    selected_page = st.sidebar.radio("Navigate", list(pages.keys()), key="nav")
    pages[selected_page](df)
 
    st.markdown("---")
    st.caption("FreshMart Romania Analytics · Built with Streamlit, Pandas, Matplotlib, GeoPandas, Scikit-learn, Statsmodels")
 
 
if __name__ == "__main__":
    main()
 