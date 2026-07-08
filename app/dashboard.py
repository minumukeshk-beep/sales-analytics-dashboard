import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px
import plotly.io as pio
from pathlib import Path

# ---------------------------------------------------------
# Sage green and cream chart theme
# ---------------------------------------------------------
SAGE_COLORS = [
    "#5F7F63",  # deep sage
    "#88A982",  # sage green
    "#A8C3A0",  # soft green
    "#C7D9BF",  # pale sage
    "#DDE8D6"   # very light sage
]

CHART_TEMPLATE = "plotly_white"
CHART_FONT = "Georgia"

# ---------------------------------------------------------
# Page settings
# ---------------------------------------------------------
st.set_page_config(
    page_title="SalesPulse Dashboard",
    page_icon="📊",
    layout="wide"
)

# NOTE: unsafe_allow_html=True was missing before — without it,
# Streamlit shows the raw CSS as text instead of applying it.
st.markdown("""
<style>
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}
[data-testid="stMetric"] {
    background-color: #FFFDF6;
    border: 1px solid #C9D8C5;
    border-radius: 16px;
    padding: 18px;
    box-shadow: 0 4px 12px rgba(74, 98, 78, 0.10);
}
[data-testid="stMetricLabel"] {
    color: #5F7F63;
    font-size: 15px;
    font-weight: 600;
}
[data-testid="stMetricValue"] {
    color: #2F3E34;
    font-size: 28px;
    font-weight: 700;
}
[data-testid="stSidebar"] {
    background-color: #E8F0E6;
}
h1, h2, h3 {
    color: #2F3E34;
    font-family: Georgia, serif;
}
            /* Premium sidebar styling */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #E8F0E6 0%, #DDE8D6 100%);
    border-right: 1px solid #C9D8C5;
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #2F3E34;
    font-family: Georgia, serif;
}

/* Filter labels */
[data-testid="stSidebar"] label {
    color: #3F5945 !important;
    font-weight: 650 !important;
    font-size: 15px !important;
}

/* Multiselect outer box */
[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background-color: #FFFDF6 !important;
    border: 1px solid #A8C3A0 !important;
    border-radius: 12px !important;
    min-height: 44px !important;
}

/* Selected filter chips */
[data-testid="stSidebar"] [data-baseweb="tag"] {
    background-color: #6B8E73 !important;
    border-radius: 8px !important;
    padding: 2px 4px !important;
}

[data-testid="stSidebar"] [data-baseweb="tag"] span {
    color: #FFFFFF !important;
    font-weight: 600 !important;
}

/* Reset button */
[data-testid="stSidebar"] .stButton > button {
    width: 100%;
    background-color: #FFFDF6;
    color: #3F5945;
    border: 1px solid #A8C3A0;
    border-radius: 12px;
    padding: 10px 14px;
    font-weight: 650;
    transition: 0.2s;
}

[data-testid="stSidebar"] .stButton > button:hover {
    background-color: #6B8E73;
    color: white;
    border-color: #6B8E73;
}
   h1, h2, h3 {
    color: #2F3E34;
    font-family: Georgia, serif;
}

/* Sidebar container */
[data-testid="stSidebar"] {
    background-color: #E8F0E6;
    border-right: 1px solid #C9D8C5;
}

/* Sidebar headings */
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #5F7F63;
    font-family: Georgia, serif;
    font-size: 18px;
}

/* Multiselect tags */
[data-testid="stSidebar"] .stMultiSelect [data-baseweb="tag"] {
    background-color: #5F7F63 !important;
    color: #FFF8E7 !important;
    border-radius: 8px;
}

/* Multiselect dropdown box */
[data-testid="stSidebar"] .stMultiSelect > div > div {
    background-color: #FFFDF6;
    border: 1px solid #C9D8C5;
    border-radius: 10px;
}

/* Buttons */
[data-testid="stSidebar"] button,
div.stDownloadButton button {
    background-color: #5F7F63;
    color: #FFF8E7;
    border-radius: 10px;
    border: none;
    font-weight: 600;
    padding: 8px 16px;
    transition: background-color 0.2s ease;
}

[data-testid="stSidebar"] button:hover,
div.stDownloadButton button:hover {
    background-color: #4A6B4E;
    color: #FFFFFF;
}

/* Sidebar help text */
[data-testid="stSidebar"] .stCaption,
[data-testid="stSidebar"] small {
    color: #6B8E73;
}

/* Divider lines */
hr {
    border-color: #C9D8C5 !important;
}
            /* Premium tab styling */
[data-baseweb="tab-list"] {
    gap: 24px;
    border-bottom: 1px solid #C9D8C5;
}

[data-baseweb="tab"] {
    color: #5F7F63;
    font-family: Georgia, serif;
    font-size: 16px;
    font-weight: 600;
    padding: 12px 4px;
}

[data-baseweb="tab"][aria-selected="true"] {
    color: #2F3E34;
    font-weight: 700;
}

[data-baseweb="tab-highlight"] {
    background-color: #5F7F63;
    height: 3px;
    border-radius: 4px;
}
</style>
""", unsafe_allow_html=True)



# ---------------------------------------------------------
# Database connection (deployment-safe)
# If sales.db doesn't exist (e.g. fresh Streamlit Cloud deploy,
# since the .db file is gitignored), rebuild it automatically
# from the committed processed CSV.
# ---------------------------------------------------------
DB_PATH = Path("database/sales.db")
CSV_PATH = Path("data/processed/superstore_clean.csv")

@st.cache_resource
def get_engine():
    if not DB_PATH.exists():
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        clean_df = pd.read_csv(CSV_PATH)
        engine = create_engine(f"sqlite:///{DB_PATH}")
        clean_df.to_sql("sales", engine, if_exists="replace", index=False)
    return create_engine(f"sqlite:///{DB_PATH}")

@st.cache_data
def load_data():
    engine = get_engine()
    return pd.read_sql("SELECT * FROM sales", engine)

df = load_data()

# ---------------------------------------------------------
# Apply one consistent style to every Plotly chart
# ---------------------------------------------------------
pio.templates["sage_cream"] = pio.templates[CHART_TEMPLATE]
pio.templates["sage_cream"].layout.update(
    font=dict(family=CHART_FONT, color="#2F3E34"),
    paper_bgcolor="#FFF8E7",
    plot_bgcolor="#FFF8E7",
    colorway=SAGE_COLORS,
    title_font=dict(family=CHART_FONT, size=22, color="#2F3E34"),
    legend=dict(font=dict(family=CHART_FONT))
)
pio.templates.default = "sage_cream"

# ---------------------------------------------------------
# Dashboard title
# ---------------------------------------------------------
st.markdown("""
<div style="
    background: linear-gradient(135deg, #E8F0E6, #FFF8E7);
    border: 1px solid #C9D8C5;
    border-radius: 18px;
    padding: 24px 28px;
    margin-bottom: 22px;
    box-shadow: 0 4px 12px rgba(74, 98, 78, 0.08);
">
    <h1 style="margin: 0; color: #2F3E34; font-family: Georgia, serif;">
        📊 SalesPulse
    </h1>
    <p style="margin: 8px 0 0 0; color: #5F7F63; font-size: 17px;">
        Sales & Business Analytics Dashboard · Python · SQLite · Streamlit · Plotly
    </p>
</div>
""", unsafe_allow_html=True)
# ---------------------------------------------------------
# Sidebar filters
# ---------------------------------------------------------
st.sidebar.header("Filters")
if st.sidebar.button("↩ Reset All Filters"):
    st.rerun()
st.sidebar.markdown("""
<div style="
    background-color: #FFFDF6;
    border: 1px solid #C9D8C5;
    border-radius: 12px;
    padding: 12px;
    margin-bottom: 16px;
    color: #2F3E34;
">
    <b>How to use</b><br>
    Select one or more filters below to explore sales, profit, and margin insights.
</div>
""", unsafe_allow_html=True)

regions = st.sidebar.multiselect(
    "Select Region",
    options=sorted(df["Region"].dropna().unique()),
    default=sorted(df["Region"].dropna().unique())
)

categories = st.sidebar.multiselect(
    "Select Category",
    options=sorted(df["Category"].dropna().unique()),
    default=sorted(df["Category"].dropna().unique())
)

sub_categories = st.sidebar.multiselect(
    "Select Sub-Category",
    options=sorted(df["Sub_Category"].dropna().unique()),
    default=sorted(df["Sub_Category"].dropna().unique())
)

filtered_df = df[
    (df["Region"].isin(regions)) &
    (df["Category"].isin(categories)) &
    (df["Sub_Category"].isin(sub_categories))
]

# Guard against empty selections instead of crashing on blank charts
if filtered_df.empty:
    st.warning("No data matches the current filter selection. Please adjust the filters in the sidebar.")
    st.stop()

# ---------------------------------------------------------
# KPI calculations
# ---------------------------------------------------------
total_sales = filtered_df["Sales"].sum()
total_profit = filtered_df["Profit"].sum()
total_records = len(filtered_df)
profit_margin = (total_profit / total_sales * 100) if total_sales != 0 else 0

col1, col2, col3, col4 = st.columns(4)
def format_currency(value):
    if abs(value) >= 1_000_000:
        return f"${value / 1_000_000:.2f}M"
    if abs(value) >= 1_000:
        return f"${value / 1_000:.1f}K"
    return f"${value:,.2f}"


col1.metric("Total Sales", format_currency(total_sales))
col2.metric("Total Profit", format_currency(total_profit))
col3.metric("Sales Records", f"{total_records:,}")
col4.metric("Profit Margin", f"{profit_margin:.2f}%")
st.caption(
    f"Data quality check: {len(filtered_df):,} records currently selected · "
    f"{filtered_df['Region'].nunique()} regions · "
    f"{filtered_df['Category'].nunique()} categories · "
    f"{filtered_df['Sub_Category'].nunique()} sub-categories"
)
st.divider()

# ---------------------------------------------------------
# Key Insights (auto-generated from current filtered data)
# ---------------------------------------------------------
st.markdown("""
<div style="
    background-color: #FFFDF6;
    border: 1px solid #C9D8C5;
    border-left: 6px solid #5F7F63;
    border-radius: 14px;
    padding: 16px 20px;
    margin-top: 8px;
    margin-bottom: 10px;
">
    <h2 style="margin: 0; color: #2F3E34; font-family: Georgia, serif;">
        🔍 Key Insights
    </h2>
    <p style="margin: 5px 0 0 0; color: #5F7F63;">
        Live observations based on your selected filters
    </p>
</div>
""", unsafe_allow_html=True)
top_region = filtered_df.groupby("Region")["Profit"].sum().idxmax()
weakest_category = filtered_df.groupby("Category")["Profit_Margin_Percent"].mean().idxmin()
discount_corr = filtered_df["Discount_Percent"].corr(filtered_df["Profit"])

best_segment = (
    filtered_df.groupby("Segment")["Profit_Margin_Percent"]
    .mean()
    .idxmax()
)

worst_ship_mode = (
    filtered_df.groupby("Ship_Mode")["Profit_Margin_Percent"]
    .mean()
    .idxmin()
)

corr_note = (
    "heavier discounts tend to reduce profit"
    if discount_corr < -0.2
    else "discount level has limited direct effect on profit"
)

st.markdown(f"""
- **{top_region}** region generates the highest total profit in the current selection.
- **{weakest_category}** has the lowest average profit margin — worth reviewing pricing or discount policy.
- Discount and Profit show a correlation of **{discount_corr:.2f}**, suggesting {corr_note}.
- **{best_segment}** has the strongest average profit margin among customer segments.
- **{worst_ship_mode}** has the lowest average profit margin among shipping modes.
""")

st.divider()

# ---------------------------------------------------------
# Sales by Region & Sales by Category (side by side)
# ---------------------------------------------------------
region_sales = (
    filtered_df.groupby("Region", as_index=False)["Sales"]
    .sum()
    .sort_values("Sales", ascending=False)
)

region_chart = px.bar(
    region_sales,
    x="Region",
    y="Sales",
    title="Sales by Region",
    text_auto=".2s",
    color="Region"
)
region_chart.update_layout(
    title_x=0.02,
    margin=dict(l=20, r=20, t=55, b=20),
    xaxis_title=None,
    yaxis_title="Sales ($)",
    showlegend=False
)

category_sales = (
    filtered_df.groupby("Category", as_index=False)["Sales"]
    .sum()
    .sort_values("Sales", ascending=False)
)

category_chart = px.pie(
    category_sales,
    names="Category",
    values="Sales",
    title="Sales by Category",
    hole=0.4
)
category_chart.update_layout(title_x=0.02)



# ---------------------------------------------------------
# Top 10 Sub-Categories by Sales
# ---------------------------------------------------------
top_subcategories = (
    filtered_df.groupby("Sub_Category", as_index=False)["Sales"]
    .sum()
    .nlargest(10, "Sales")
    .sort_values("Sales")
)

top_subcategory_chart = px.bar(
    top_subcategories,
    x="Sales",
    y="Sub_Category",
    orientation="h",
    title="Top 10 Sub-Categories by Sales",
    text_auto=".2s"
)
top_subcategory_chart.update_layout(
    title_x=0.02,
    margin=dict(l=20, r=20, t=55, b=20)
)



# ---------------------------------------------------------
# Top 10 Sub-Categories by Profit
# ---------------------------------------------------------
top_profit_subcategories = (
    filtered_df.groupby("Sub_Category", as_index=False)["Profit"]
    .sum()
    .nlargest(10, "Profit")
    .sort_values("Profit")
)

top_profit_subcategory_chart = px.bar(
    top_profit_subcategories,
    x="Profit",
    y="Sub_Category",
    orientation="h",
    title="Top 10 Sub-Categories by Profit",
    text_auto=".2s",
    color="Profit",
    color_continuous_scale=["#DDE8D6", "#A8C3A0", "#5F7F63"]
)

top_profit_subcategory_chart.update_layout(
    title_x=0.02,
    margin=dict(l=20, r=20, t=55, b=20),
    coloraxis_showscale=False
)


# ---------------------------------------------------------
# Profit vs Discount
# ---------------------------------------------------------
profit_discount_chart = px.scatter(
    filtered_df,
    x="Discount_Percent",
    y="Profit",
    color="Category",
    size="Sales",
    hover_data=["Sub_Category", "Region", "Sales"],
    title="Profit vs Discount"
)
profit_discount_chart.update_layout(title_x=0.02)



# ---------------------------------------------------------
# Sales by Category and Sub-Category Treemap
# ---------------------------------------------------------
treemap_df = (
    filtered_df.groupby(["Category", "Sub_Category"], as_index=False)
    .agg(
        Sales=("Sales", "sum"),
        Profit_Margin_Percent=("Profit_Margin_Percent", "mean")
    )
)

treemap_chart = px.treemap(
    treemap_df,
    path=["Category", "Sub_Category"],
    values="Sales",
    color="Profit_Margin_Percent",
    color_continuous_scale=["#DDE8D6", "#A8C3A0", "#5F7F63"],
    title="Sales by Category and Sub-Category"
)

treemap_chart.update_layout(
    title_x=0.02,
    margin=dict(l=10, r=10, t=55, b=10)
)



# ---------------------------------------------------------
# Sales and Profit by Segment
# ---------------------------------------------------------
segment_data = (
    filtered_df.groupby("Segment", as_index=False)
    .agg(
        Sales=("Sales", "sum"),
        Profit=("Profit", "sum")
    )
)

segment_chart = px.bar(
    segment_data,
    x="Segment",
    y=["Sales", "Profit"],
    barmode="group",
    title="Sales and Profit by Segment",
    color_discrete_sequence=["#5F7F63", "#A8C3A0"]
)

segment_chart.update_layout(
    title_x=0.02,
    margin=dict(l=20, r=20, t=55, b=20),
    xaxis_title=None,
    yaxis_title="Amount ($)",
    legend_title_text=""
)



# ---------------------------------------------------------
# Sales and Profit by Ship Mode
# ---------------------------------------------------------
ship_data = (
    filtered_df.groupby("Ship_Mode", as_index=False)
    .agg(
        Sales=("Sales", "sum"),
        Profit=("Profit", "sum")
    )
)

ship_chart = px.bar(
    ship_data,
    x="Ship_Mode",
    y=["Sales", "Profit"],
    barmode="group",
    title="Sales and Profit by Ship Mode",
    color_discrete_sequence=["#5F7F63", "#A8C3A0"]
)

ship_chart.update_layout(
    title_x=0.02,
    margin=dict(l=20, r=20, t=55, b=20),
    xaxis_title=None,
    yaxis_title="Amount ($)",
    legend_title_text=""
)
# ---------------------------------------------------------
# Dashboard Chart Tabs
# ---------------------------------------------------------
tab1, tab2, tab3 = st.tabs([
    "📈 Overview",
    "📦 Product Analysis",
    "🚚 Segment & Shipping"
])

with tab1:
    overview_col1, overview_col2 = st.columns(2)

    with overview_col1:
        st.plotly_chart(region_chart, use_container_width=True)

    with overview_col2:
        st.plotly_chart(category_chart, use_container_width=True)

    st.plotly_chart(profit_discount_chart, use_container_width=True)

with tab2:
    st.plotly_chart(treemap_chart, use_container_width=True)

    product_col1, product_col2 = st.columns(2)

    with product_col1:
        st.plotly_chart(top_subcategory_chart, use_container_width=True)

    with product_col2:
        st.plotly_chart(top_profit_subcategory_chart, use_container_width=True)

with tab3:
    shipping_col1, shipping_col2 = st.columns(2)

    with shipping_col1:
        st.plotly_chart(segment_chart, use_container_width=True)

    with shipping_col2:
        st.plotly_chart(ship_chart, use_container_width=True)

# ---------------------------------------------------------
# Filtered data table (shown once)
# ---------------------------------------------------------
with st.expander("📌 Dataset Scope and Analysis Notes"):
    st.write(
        "This dashboard analyzes sales, profit, discount, shipping mode, "
        "customer segment, region, category, and sub-category performance. "
        "Time-based trends, order-level analysis, customer-level analysis, "
        "and product-name analysis are not included because the dataset does "
        "not contain date, order ID, customer ID, customer name, or product name columns."
    )
st.subheader("Filtered Sales Data")
st.dataframe(filtered_df, use_container_width=True)

csv_data = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="⬇️ Download Filtered Data as CSV",
    data=csv_data,
    file_name="salespulse_filtered_data.csv",
    mime="text/csv"
)

st.divider()

st.markdown(f"""
<div style="
    text-align: center;
    color: #5F7F63;
    font-size: 14px;
    padding: 12px 0 4px 0;
">
    SalesPulse Dashboard · Showing <b>{len(filtered_df):,}</b> filtered records ·
    Built with Python, SQLite, Streamlit and Plotly
</div>
""", unsafe_allow_html=True)
st.caption(
    f"Data source: Sample Superstore dataset · {len(df):,} cleaned records · "
    "Interactive analysis by region, category, segment, shipping mode, profit and discount"
)

with st.expander("ℹ️ About this dashboard"):
    st.write(
        "SalesPulse helps users explore sales and profit performance across regions, "
        "categories, sub-categories, customer segments, and shipping modes. "
        "Use the sidebar filters to update all KPIs, charts, and business insights."
    )

st.markdown("""
<div style="
    background-color: #FFFDF6;
    border: 1px solid #C9D8C5;
    border-radius: 14px;
    padding: 14px 18px;
    margin: 12px 0 18px 0;
    color: #2F3E34;
">
    <b style="color: #5F7F63;">Dashboard Guide</b><br>
    📈 <b>Overview:</b> Region, category, profit and discount performance<br>
    📦 <b>Product Analysis:</b> Category and sub-category sales and profit performance<br>
    🚚 <b>Segment & Shipping:</b> Customer segment and shipping mode comparison
</div>
""", unsafe_allow_html=True)