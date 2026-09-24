import streamlit as st
import pandas as pd
import plotly.express as px
from openai import OpenAI

from data import load_sales_data

client = OpenAI()

# ==========================================
# PAGE SETTINGS
# ==========================================

st.set_page_config(
    page_title="Taqi Sales Dashboard",
    page_icon="📊",
    layout="wide"
)


# ==========================================
# CUSTOM CSS
# ==========================================

st.markdown("""
<style>

    /* Main page */
    .main {
        padding-top: 2rem;
    }

    /* Dashboard title */
    .dashboard-title {
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    /* Dashboard subtitle */
    .dashboard-subtitle {
        font-size: 18px;
        margin-bottom: 30px;
    }

    /* KPI cards */
    div[data-testid="stMetric"] {
        padding: 20px;
        border-radius: 12px;
        border: 1px solid rgba(128, 128, 128, 0.25);
        background-color: rgba(128, 128, 128, 0.08);
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        padding-top: 2rem;
    }

    /* Dataframe */
    div[data-testid="stDataFrame"] {
        border-radius: 10px;
    }

</style>
""", unsafe_allow_html=True)


# ==========================================
# LOAD SALES DATA
# ==========================================

try:

    df = load_sales_data()

except FileNotFoundError as e:

    st.error(f"❌ {e}")
    st.stop()

except ValueError as e:

    st.error(f"❌ {e}")
    st.stop()


# ==========================================
# TITLE
# ==========================================

st.markdown(
    '<div class="dashboard-title">'
    '📊 Taqi Sales Dashboard'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="dashboard-subtitle">'
    'Analyze sales, revenue, products, regions, and salespeople interactively.'
    '</div>',
    unsafe_allow_html=True
)

# ==========================================
# SIDEBAR
# ==========================================

st.sidebar.title("Dashboard Filters")

st.sidebar.caption(
    "Filter the dashboard to explore specific sales data."
)


# ==========================================
# DATE FILTER
# ==========================================

st.sidebar.subheader("Time Period")

date_filter = st.sidebar.selectbox(
    "Select period",
    [
        "All Time",
        "Today",
        "This Month",
        "This Year",
        "Custom Date Range"
    ]
)


# ==========================================
# START FILTERING
# ==========================================

filtered_df = df.copy()

today = pd.Timestamp.today().normalize()


# ==========================================
# APPLY DATE FILTER
# ==========================================

if date_filter == "Today":

    filtered_df = filtered_df[
        filtered_df["Date"] == today
    ]


elif date_filter == "This Month":

    filtered_df = filtered_df[
        (filtered_df["Date"].dt.month == today.month)
        &
        (filtered_df["Date"].dt.year == today.year)
    ]


elif date_filter == "This Year":

    filtered_df = filtered_df[
        filtered_df["Date"].dt.year == today.year
    ]


elif date_filter == "Custom Date Range":

    min_date = df["Date"].min().date()
    max_date = df["Date"].max().date()

    selected_dates = st.sidebar.date_input(
        "Select date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    if len(selected_dates) == 2:

        start_date = pd.Timestamp(
            selected_dates[0]
        )

        end_date = pd.Timestamp(
            selected_dates[1]
        )

        filtered_df = filtered_df[
            (filtered_df["Date"] >= start_date)
            &
            (filtered_df["Date"] <= end_date)
        ]


# ==========================================
# PRODUCT FILTER
# ==========================================

st.sidebar.subheader("Product")

products = st.sidebar.multiselect(
    "Select products",
    options=sorted(df["Product"].unique()),
    default=sorted(df["Product"].unique())
)

filtered_df = filtered_df[
    filtered_df["Product"].isin(products)
]


# ==========================================
# REGION FILTER
# ==========================================

st.sidebar.subheader("Region")

regions = st.sidebar.multiselect(
    "Select regions",
    options=sorted(df["Region"].unique()),
    default=sorted(df["Region"].unique())
)

filtered_df = filtered_df[
    filtered_df["Region"].isin(regions)
]


# ==========================================
# SALESPERSON FILTER
# ==========================================

st.sidebar.subheader("Salesperson")

salespeople = st.sidebar.multiselect(
    "Select salespeople",
    options=sorted(df["Salesperson"].unique()),
    default=sorted(df["Salesperson"].unique())
)

filtered_df = filtered_df[
    filtered_df["Salesperson"].isin(salespeople)
]


# ==========================================
# SIDEBAR ACTIONS
# ==========================================

st.sidebar.divider()


# Reset filters
if st.sidebar.button(
    "Reset Filters",
    use_container_width=True
):

    st.rerun()


# ==========================================
# DOWNLOAD FILTERED DATA
# ==========================================

csv_data = filtered_df.to_csv(
    index=False
)

st.sidebar.download_button(
    label="Download Filtered CSV",
    data=csv_data,
    file_name="filtered_sales.csv",
    mime="text/csv",
    use_container_width=True
)


# ==========================================
# FILTER STATUS
# ==========================================

st.sidebar.divider()

st.sidebar.caption(
    f"Showing {len(filtered_df):,} "
    f"of {len(df):,} sales records"
)

# ==========================================
# KPI CALCULATIONS
# ==========================================

total_revenue = filtered_df["Revenue"].sum()

total_orders = filtered_df["Order_ID"].nunique()

total_units = filtered_df["Quantity"].sum()


# Avoid division by zero
if total_orders > 0:

    average_order = (
        total_revenue / total_orders
    )

else:

    average_order = 0


# ==========================================
# KPI CARDS
# ==========================================

st.subheader("📌 Key Performance Indicators")


# ==========================================
# CALCULATE KPI VALUES
# ==========================================

total_revenue = filtered_df["Revenue"].sum()

total_orders = filtered_df["Order_ID"].nunique()

total_units = filtered_df["Quantity"].sum()

average_order = (
    total_revenue / total_orders
    if total_orders > 0
    else 0
)


# ==========================================
# KPI COLUMNS
# ==========================================

col1, col2, col3, col4 = st.columns(4)


# ==========================================
# REVENUE
# ==========================================

with col1:

    st.metric(
        label="💰 Total Revenue",
        value=f"Rs. {total_revenue:,.0f}",
        help="Total revenue generated by the filtered sales records."
    )


# ==========================================
# ORDERS
# ==========================================

with col2:

    st.metric(
        label="🧾 Total Orders",
        value=f"{total_orders:,}",
        help="Number of unique orders in the filtered data."
    )


# ==========================================
# UNITS
# ==========================================

with col3:

    st.metric(
        label="📦 Units Sold",
        value=f"{total_units:,}",
        help="Total number of units sold."
    )


# ==========================================
# AVERAGE ORDER
# ==========================================

with col4:

    st.metric(
        label="💵 Average Order",
        value=f"Rs. {average_order:,.0f}",
        help="Average revenue generated per order."
    )

# ==========================================
# EXECUTIVE SUMMARY
# ==========================================

st.divider()

st.subheader("🏆 Executive Summary")


# ==========================================
# TOP PRODUCT
# ==========================================

product_summary = (
    filtered_df
    .groupby("Product")["Revenue"]
    .sum()
    .sort_values(ascending=False)
)


top_product = product_summary.idxmax()

top_product_revenue = product_summary.max()


# ==========================================
# TOP REGION
# ==========================================

region_summary = (
    filtered_df
    .groupby("Region")["Revenue"]
    .sum()
    .sort_values(ascending=False)
)


top_region = region_summary.idxmax()

top_region_revenue = region_summary.max()


# ==========================================
# TOP SALESPERSON
# ==========================================

salesperson_summary = (
    filtered_df
    .groupby("Salesperson")["Revenue"]
    .sum()
    .sort_values(ascending=False)
)


top_salesperson = salesperson_summary.idxmax()

top_salesperson_revenue = salesperson_summary.max()


# ==========================================
# REVENUE PER UNIT
# ==========================================

revenue_per_unit = (
    total_revenue / total_units
    if total_units > 0
    else 0
)


# ==========================================
# MOST SOLD PRODUCT
# ==========================================

quantity_summary = (
    filtered_df
    .groupby("Product")["Quantity"]
    .sum()
    .sort_values(ascending=False)
)


most_sold_product = quantity_summary.idxmax()

most_sold_quantity = quantity_summary.max()


# ==========================================
# BEST SALES DAY
# ==========================================

daily_summary = (
    filtered_df
    .groupby("Date")["Revenue"]
    .sum()
    .sort_values(ascending=False)
)


best_sales_day = daily_summary.index[0]

best_sales_day_revenue = daily_summary.iloc[0]

# ==========================================
# EXECUTIVE SUMMARY CARDS
# ==========================================

col1, col2, col3 = st.columns(3)


with col1:

    st.metric(
        "🏆 Top Product",
        top_product,
        f"Rs. {top_product_revenue:,.0f}"
    )


with col2:

    st.metric(
        "🌍 Top Region",
        top_region,
        f"Rs. {top_region_revenue:,.0f}"
    )


with col3:

    st.metric(
        "👤 Top Salesperson",
        top_salesperson,
        f"Rs. {top_salesperson_revenue:,.0f}"
    )


col1, col2, col3 = st.columns(3)


with col1:

    st.metric(
        "📦 Most Sold Product",
        most_sold_product,
        f"{most_sold_quantity:,.0f} units"
    )


with col2:

    st.metric(
        "💰 Revenue per Unit",
        f"Rs. {revenue_per_unit:,.0f}"
    )


with col3:

    st.metric(
        "📅 Best Sales Day",
        best_sales_day.strftime("%d %b %Y"),
        f"Rs. {best_sales_day_revenue:,.0f}"
    )
# ==========================================
# BUSINESS INSIGHTS
# ==========================================

st.divider()

st.subheader("💡 Business Insights")


# ==========================================
# INSIGHT 1 — TOP PRODUCT
# ==========================================

st.info(
    f"🏆 **{top_product}** generated the highest revenue "
    f"with **Rs. {top_product_revenue:,.0f}**."
)


# ==========================================
# INSIGHT 2 — TOP REGION
# ==========================================

st.info(
    f"🌍 **{top_region}** generated the highest regional "
    f"revenue with **Rs. {top_region_revenue:,.0f}**."
)


# ==========================================
# INSIGHT 3 — TOP SALESPERSON
# ==========================================

st.info(
    f"👤 **{top_salesperson}** generated the highest revenue "
    f"among salespeople with **Rs. {top_salesperson_revenue:,.0f}**."
)


# ==========================================
# INSIGHT 4 — MOST SOLD PRODUCT
# ==========================================

st.info(
    f"📦 **{most_sold_product}** had the highest sales volume "
    f"with **{most_sold_quantity:,} units sold**."
)


# ==========================================
# INSIGHT 5 — BEST SALES DAY
# ==========================================

st.info(
    f"📅 The highest-revenue sales day was "
    f"**{best_sales_day.strftime('%d %b %Y')}**, "
    f"with **Rs. {best_sales_day_revenue:,.0f}** in revenue."
)

# ==========================================
# AI SALES ANALYST
# ==========================================

st.divider()

st.subheader("🤖 AI Sales Analyst")

st.write(
    "Ask AI to analyze the currently filtered sales data."
)

if st.button("✨ Generate AI Analysis"):

    # Create a compact summary of the filtered data
    ai_summary = {
        "Total Revenue": float(total_revenue),
        "Total Orders": int(total_orders),
        "Total Units": int(total_units),
        "Average Order": float(average_order),
        "Top Product": str(top_product),
        "Top Product Revenue": float(top_product_revenue),
        "Top Region": str(top_region),
        "Top Region Revenue": float(top_region_revenue),
        "Top Salesperson": str(top_salesperson),
        "Top Salesperson Revenue": float(top_salesperson_revenue),
        "Most Sold Product": str(most_sold_product),
        "Most Sold Quantity": int(most_sold_quantity),
        "Best Sales Day": best_sales_day.strftime("%d %b %Y"),
        "Best Sales Day Revenue": float(best_sales_day_revenue)
    }

    prompt = f"""
    Analyze this sales dashboard data:

    {ai_summary}

    Give a concise business analysis containing:
    1. Overall performance
    2. Strongest areas
    3. Areas that may need attention
    4. Three practical observations

    Use simple language.
    """

    try:

        response = client.responses.create(
            model="gpt-5.6-luna",
            input=prompt
        )

        st.success("AI analysis generated!")
        st.markdown(response.output_text)

    except Exception as e:

        st.error(
            f"AI analysis failed: {e}"
        )

# ==========================================
# FILTER RESULT
# ==========================================

st.subheader("📋 Filtered Sales Data")

st.write(
    f"Showing **{len(filtered_df)}** sales records."
)


# ==========================================
# EMPTY DATA CHECK
# ==========================================

if filtered_df.empty:

    st.warning(
        "⚠️ No sales records match the selected filters."
    )

    st.info(
        "Try changing the date, product, region, "
        "or salesperson filters."
    )

    st.stop()

# ==========================================
# FILTER STATUS
# ==========================================

st.markdown(
    f"""
    <div style="
        padding: 14px 18px;
        border-radius: 10px;
        border: 1px solid rgba(128, 128, 128, 0.25);
        background-color: rgba(128, 128, 128, 0.06);
        margin-bottom: 20px;
    ">
        <strong>Current View</strong><br>
        {len(filtered_df):,} records
        &nbsp;•&nbsp;
        {len(products):,} products
        &nbsp;•&nbsp;
        {len(regions):,} regions
        &nbsp;•&nbsp;
        {len(salespeople):,} salespeople
    </div>
    """,
    unsafe_allow_html=True
)

# ==========================================
# EXECUTIVE SUMMARY
# ==========================================

st.divider()

st.subheader("🏆 Executive Summary")

# ==========================================
# SALES TABLE
# ==========================================

st.dataframe(
    filtered_df,
    use_container_width=True,
    hide_index=True
)


# ==========================================
# SALES ANALYSIS
# ==========================================

st.subheader("📊 Sales Analysis")


# ==========================================
# REVENUE OVER TIME
# ==========================================

daily_revenue = (
    filtered_df
    .groupby("Date")["Revenue"]
    .sum()
    .sort_index()
    .reset_index()
)


fig_line = px.line(
    daily_revenue,
    x="Date",
    y="Revenue",
    title="📈 Revenue Over Time",
    markers=True
)


# ==========================================
# CHART FORMATTING
# ==========================================

fig_line.update_traces(
    line=dict(width=3),
    marker=dict(size=8),
    hovertemplate=(
        "<b>%{x|%d %b %Y}</b><br>"
        "Revenue: Rs. %{y:,.0f}"
        "<extra></extra>"
    )
)

fig_line.update_layout(
    xaxis_title="Date",
    yaxis_title="Revenue (Rs.)",

    yaxis_tickformat=",.0f",

    xaxis=dict(
        tickformat="%d %b",
        tickangle=-45
    ),

    hovermode="x unified",

    height=450,

    margin=dict(
        l=20,
        r=20,
        t=70,
        b=60
    )
)

# ==========================================
# DISPLAY CHART
# ==========================================

st.plotly_chart(
    fig_line,
    use_container_width=True
)
# ==========================================
# SALES PERFORMANCE CHARTS
# ==========================================

st.subheader("📊 Sales Performance")

st.write(
    "Compare revenue performance across products, categories, "
    "regions, and salespeople."
)


# ==========================================
# REVENUE BY PRODUCT
# ==========================================

product_chart_data = (
    filtered_df
    .groupby("Product")["Revenue"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)

fig_product = px.bar(
    product_chart_data,
    x="Product",
    y="Revenue",
    title="💻 Revenue by Product",
    text="Revenue"
)

fig_product.update_traces(
    texttemplate="Rs. %{text:,.0f}",
    textposition="outside",
    hovertemplate=(
        "<b>%{x}</b><br>"
        "Revenue: Rs. %{y:,.0f}"
        "<extra></extra>"
    )
)

fig_product.update_layout(
    xaxis_title="Product",
    yaxis_title="Revenue (Rs.)",
    yaxis_tickformat=",.0f",
    hovermode="x",

    height=450,

    margin=dict(
        l=20,
        r=20,
        t=70,
        b=30
    )
)

# Full-width main chart
st.plotly_chart(
    fig_product,
    use_container_width=True
)


# ==========================================
# REVENUE BY CATEGORY
# ==========================================

category_revenue = (
    filtered_df
    .groupby("Category")["Revenue"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)

fig_category = px.bar(
    category_revenue,
    x="Category",
    y="Revenue",
    title="🏷️ Revenue by Category",
    text="Revenue"
)

fig_category.update_traces(
    texttemplate="Rs. %{text:,.0f}",
    textposition="outside",
    hovertemplate=(
        "<b>%{x}</b><br>"
        "Revenue: Rs. %{y:,.0f}"
        "<extra></extra>"
    )
)

fig_category.update_layout(
    xaxis_title="Category",
    yaxis_title="Revenue (Rs.)",
    yaxis_tickformat=",.0f",
    hovermode="x",
    margin=dict(
        l=20,
        r=20,
        t=70,
        b=30
    )
)


# ==========================================
# REVENUE BY REGION
# ==========================================

region_revenue = (
    filtered_df
    .groupby("Region")["Revenue"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)

fig_region = px.bar(
    region_revenue,
    x="Region",
    y="Revenue",
    title="🌍 Revenue by Region",
    text="Revenue"
)

fig_region.update_traces(
    texttemplate="Rs. %{text:,.0f}",
    textposition="outside",
    hovertemplate=(
        "<b>%{x}</b><br>"
        "Revenue: Rs. %{y:,.0f}"
        "<extra></extra>"
    )
)

fig_region.update_layout(
    xaxis_title="Region",
    yaxis_title="Revenue (Rs.)",
    yaxis_tickformat=",.0f",
    hovermode="x",
    margin=dict(
        l=20,
        r=20,
        t=70,
        b=30
    )
)


# ==========================================
# CATEGORY + REGION
# ==========================================

col1, col2 = st.columns(2)

with col1:

    st.plotly_chart(
        fig_category,
        use_container_width=True
    )

with col2:

    st.plotly_chart(
        fig_region,
        use_container_width=True
    )


# ==========================================
# REVENUE BY SALESPERSON
# ==========================================

salesperson_revenue = (
    filtered_df
    .groupby("Salesperson")["Revenue"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)

fig_salesperson = px.bar(
    salesperson_revenue,
    x="Salesperson",
    y="Revenue",
    title="👤 Revenue by Salesperson",
    text="Revenue"
)

fig_salesperson.update_traces(
    texttemplate="Rs. %{text:,.0f}",
    textposition="outside",
    hovertemplate=(
        "<b>%{x}</b><br>"
        "Revenue: Rs. %{y:,.0f}"
        "<extra></extra>"
    )
)

fig_salesperson.update_layout(
    xaxis_title="Salesperson",
    yaxis_title="Revenue (Rs.)",
    yaxis_tickformat=",.0f",
    hovermode="x",
    margin=dict(
        l=20,
        r=20,
        t=70,
        b=30
    )
)

# Full-width salesperson chart
st.plotly_chart(
    fig_salesperson,
    use_container_width=True
)

# ==========================================
# UNITS SOLD BY PRODUCT
# ==========================================

st.divider()

st.subheader("📦 Units Sold Analysis")


quantity_by_product = (
    filtered_df
    .groupby("Product")["Quantity"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)


fig_quantity = px.bar(
    quantity_by_product,
    x="Product",
    y="Quantity",
    title="📦 Units Sold by Product",
    text_auto=True
)


fig_quantity.update_layout(
    xaxis_title="Product",
    yaxis_title="Units Sold",
    yaxis_tickformat=",.0f",
    height=430
)


st.plotly_chart(
    fig_quantity,
    use_container_width=True
)
# ==========================================
# INTERACTIVE ANALYSIS EXPLORER
# ==========================================

st.divider()

st.subheader("🔬 Analysis Explorer")

st.write(
    "Choose a category and metric to explore the sales data."
)


# ==========================================
# EXPLORER CONTROLS
# ==========================================

col1, col2 = st.columns(2)


with col1:

    analyze_by = st.selectbox(
        "📊 Analyze By",
        [
            "Product",
            "Category",
            "Region",
            "Salesperson"
        ]
    )


with col2:

    metric = st.selectbox(
        "📈 Select Metric",
        [
            "Revenue",
            "Quantity"
        ]
    )


# ==========================================
# PREPARE ANALYSIS DATA
# ==========================================

explorer_data = (
    filtered_df
    .groupby(analyze_by)[metric]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)


# ==========================================
# CREATE EXPLORER CHART
# ==========================================

fig_explorer = px.bar(
    explorer_data,
    x=analyze_by,
    y=metric,
    title=f"{metric} by {analyze_by}",
    text_auto=True
)


# ==========================================
# CHART LABELS
# ==========================================

if metric == "Revenue":

    fig_explorer.update_layout(
        xaxis_title=analyze_by,
        yaxis_title="Revenue (Rs.)"
    )

else:

    fig_explorer.update_layout(
        xaxis_title=analyze_by,
        yaxis_title="Units Sold"
    )


# ==========================================
# DISPLAY EXPLORER CHART
# ==========================================

st.plotly_chart(
    fig_explorer,
    use_container_width=True
)

# ==========================================
# FOOTER
# ==========================================

st.divider()

st.caption(
    "🐍 Built with Python, Pandas, Streamlit, and Plotly | "
    "Taqi Sales Dashboard"
)