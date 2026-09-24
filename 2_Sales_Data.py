import streamlit as st
import pandas as pd

from data import load_sales_data


# ==========================================
# PAGE SETTINGS
# ==========================================

st.set_page_config(
    page_title="Sales Data",
    page_icon="📋",
    layout="wide"
)


# ==========================================
# CUSTOM CSS
# ==========================================

st.markdown("""
<style>

    .main {
        padding-top: 1.5rem;
    }

    .page-title {
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .page-subtitle {
        font-size: 18px;
        margin-bottom: 30px;
    }

    .section-title {
        font-size: 25px;
        font-weight: 650;
        margin-top: 15px;
        margin-bottom: 15px;
    }

    div[data-testid="stMetric"] {
        padding: 20px;
        border-radius: 14px;
        border: 1px solid rgba(128, 128, 128, 0.25);
        background-color: rgba(128, 128, 128, 0.08);
    }

    .info-box {
        padding: 15px 20px;
        border-radius: 12px;
        border: 1px solid rgba(128, 128, 128, 0.25);
        background-color: rgba(128, 128, 128, 0.06);
        margin-bottom: 20px;
    }

    .footer {
        text-align: center;
        padding: 25px;
        margin-top: 30px;
        font-size: 14px;
        opacity: 0.7;
    }

</style>
""", unsafe_allow_html=True)


# ==========================================
# LOAD DATA
# ==========================================

try:

    df = load_sales_data()

except FileNotFoundError as e:

    st.error(f"File error: {e}")
    st.stop()

except ValueError as e:

    st.error(f"Data error: {e}")
    st.stop()


# ==========================================
# PAGE HEADER
# ==========================================

st.markdown(
    '<div class="page-title">'
    '📋 Sales Data'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="page-subtitle">'
    'Explore, filter, and download your sales records.'
    '</div>',
    unsafe_allow_html=True
)


# ==========================================
# FILTER SECTION
# ==========================================

st.markdown(
    '<div class="section-title">'
    'Filters'
    '</div>',
    unsafe_allow_html=True
)


# ==========================================
# DATE FILTER
# ==========================================

min_date = df["Date"].min().date()

max_date = df["Date"].max().date()


selected_date_range = st.date_input(
    "Date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
    key="sales_data_date_range"
)


# ==========================================
# PRODUCT / REGION / SALESPERSON FILTERS
# ==========================================

col1, col2, col3 = st.columns(3)


with col1:

    selected_products = st.multiselect(
        "Product",
        options=sorted(
            df["Product"].unique()
        ),
        default=sorted(
            df["Product"].unique()
        ),
        key="sales_data_products"
    )


with col2:

    selected_regions = st.multiselect(
        "Region",
        options=sorted(
            df["Region"].unique()
        ),
        default=sorted(
            df["Region"].unique()
        ),
        key="sales_data_regions"
    )


with col3:

    selected_salespeople = st.multiselect(
        "Salesperson",
        options=sorted(
            df["Salesperson"].unique()
        ),
        default=sorted(
            df["Salesperson"].unique()
        ),
        key="sales_data_salespeople"
    )


# ==========================================
# APPLY FILTERS
# ==========================================

filtered_df = df.copy()


# ------------------------------------------
# DATE FILTER
# ------------------------------------------

if len(selected_date_range) == 2:

    start_date = pd.Timestamp(
        selected_date_range[0]
    )

    end_date = pd.Timestamp(
        selected_date_range[1]
    )

    filtered_df = filtered_df[
        (filtered_df["Date"] >= start_date)
        &
        (filtered_df["Date"] <= end_date)
    ]


# ------------------------------------------
# PRODUCT FILTER
# ------------------------------------------

filtered_df = filtered_df[
    filtered_df["Product"].isin(
        selected_products
    )
]


# ------------------------------------------
# REGION FILTER
# ------------------------------------------

filtered_df = filtered_df[
    filtered_df["Region"].isin(
        selected_regions
    )
]


# ------------------------------------------
# SALESPERSON FILTER
# ------------------------------------------

filtered_df = filtered_df[
    filtered_df["Salesperson"].isin(
        selected_salespeople
    )
]


# ==========================================
# DATA SUMMARY
# ==========================================

st.divider()

st.markdown(
    '<div class="section-title">'
    '📊 Sales Summary'
    '</div>',
    unsafe_allow_html=True
)


# ==========================================
# EMPTY DATA CHECK
# ==========================================

if filtered_df.empty:

    st.warning(
        "No sales records match your filters."
    )

    st.info(
        "Try selecting a different date range, "
        "product, region, or salesperson."
    )

    st.stop()


# ==========================================
# KPI CALCULATIONS
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
# KPI CARDS
# ==========================================

col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "Revenue",
        f"Rs. {total_revenue:,.0f}"
    )


with col2:

    st.metric(
        "Orders",
        f"{total_orders:,}"
    )


with col3:

    st.metric(
        "Units Sold",
        f"{total_units:,}"
    )


with col4:

    st.metric(
        "Average Order",
        f"Rs. {average_order:,.0f}"
    )


# ==========================================
# RECORD INFORMATION
# ==========================================

st.markdown(
    f"""
    <div class="info-box">
        Showing <strong>{len(filtered_df)}</strong>
        sales records from
        <strong>{filtered_df["Date"].min().strftime("%d %b %Y")}</strong>
        to
        <strong>{filtered_df["Date"].max().strftime("%d %b %Y")}</strong>.
    </div>
    """,
    unsafe_allow_html=True
)


# ==========================================
# DATA QUALITY
# ==========================================

st.markdown(
    '<div class="section-title">'
    '🛡️ Data Quality'
    '</div>',
    unsafe_allow_html=True
)


missing_values = filtered_df.isna().sum().sum()

duplicate_rows = filtered_df.duplicated().sum()


col1, col2, col3 = st.columns(3)


with col1:

    st.metric(
        "Records",
        f"{len(filtered_df):,}"
    )


with col2:

    st.metric(
        "Missing Values",
        f"{missing_values:,}"
    )


with col3:

    st.metric(
        "Duplicate Rows",
        f"{duplicate_rows:,}"
    )


# ==========================================
# SALES TABLE
# ==========================================

st.divider()

st.markdown(
    '<div class="section-title">'
    '📋 Sales Records'
    '</div>',
    unsafe_allow_html=True
)


st.dataframe(
    filtered_df,
    use_container_width=True,
    hide_index=True
)


# ==========================================
# DOWNLOAD SECTION
# ==========================================

st.divider()

st.markdown(
    '<div class="section-title">'
    '📥 Export'
    '</div>',
    unsafe_allow_html=True
)


csv_data = filtered_df.to_csv(
    index=False
)


st.download_button(
    label="Download Filtered CSV",
    data=csv_data,
    file_name="filtered_sales_data.csv",
    mime="text/csv",
    use_container_width=True
)


# ==========================================
# FOOTER
# ==========================================

st.markdown(
    """
    <div class="footer">
        Taqi Sales Dashboard • Sales Data
        <br>
        Python • Pandas • Streamlit
    </div>
    """,
    unsafe_allow_html=True
)