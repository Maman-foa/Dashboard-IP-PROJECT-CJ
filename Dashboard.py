import streamlit as st
import plotly.express as px
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="Superstore Dashboard", page_icon=":bar_chart:", layout="wide")

st.title("📊 SuperStore / Adidas EDA Dashboard")
st.markdown('<style>div.block-container{padding-top:1rem;}</style>', unsafe_allow_html=True)

# ==============================================
# FILE UPLOADER
# ==============================================
uploaded = st.file_uploader(":file_folder: Upload CSV / Excel", type=["csv","txt","xlsx","xls"])

if uploaded is not None:
    st.success(f"File uploaded: **{uploaded.name}**")

    if uploaded.name.endswith((".csv", ".txt")):
        df = pd.read_csv(uploaded, encoding="ISO-8859-1")
    else:
        df = pd.read_excel(uploaded)
else:
    # DEFAULT FILE — sesuaikan dengan file Anda
    DEFAULT_FILE = "Adidas.xlsx"   # wajib ada dalam folder Streamlit Cloud
    df = pd.read_excel(DEFAULT_FILE)

# ==============================================
# Tampilkan kolom untuk CEK struktur dataset
# ==============================================
st.write("### 🧩 Columns Detected in Dataset:")
st.write(df.columns.tolist())

# ==============================================
# CEK apakah kolom wajib ada
# ==============================================
required_cols = ["Order Date", "Region", "State", "City",
                 "Category", "Sub-Category", "Segment",
                 "Sales", "Profit", "Quantity"]

missing = [col for col in required_cols if col not in df.columns]

if missing:
    st.error(f"❌ Dataset Anda tidak memiliki kolom berikut:\n\n{missing}\n\n"
             "Silakan sesuaikan nama kolom atau beri tahu saya untuk mapping otomatis.")
    st.stop()

# ==============================================
# KONVERSI TANGGAL
# ==============================================
df["Order Date"] = pd.to_datetime(df["Order Date"])

# ==============================================
# FILTER DATE
# ==============================================
col1, col2 = st.columns((2))

startDate = df["Order Date"].min()
endDate   = df["Order Date"].max()

with col1:
    date1 = st.date_input("Start Date", startDate)

with col2:
    date2 = st.date_input("End Date", endDate)

df = df[(df["Order Date"] >= pd.to_datetime(date1)) &
        (df["Order Date"] <= pd.to_datetime(date2))]

# ==============================================
# SIDEBAR FILTER
# ==============================================
st.sidebar.header("🧭 Filters")

region = st.sidebar.multiselect("Region", df["Region"].unique())
state  = st.sidebar.multiselect("State", df["State"].unique())
city   = st.sidebar.multiselect("City", df["City"].unique())

filtered_df = df.copy()

if region:
    filtered_df = filtered_df[filtered_df["Region"].isin(region)]

if state:
    filtered_df = filtered_df[filtered_df["State"].isin(state)]

if city:
    filtered_df = filtered_df[filtered_df["City"].isin(city)]

# ==============================================
# CATEGORY SALES BAR CHART
# ==============================================
category_df = filtered_df.groupby("Category")["Sales"].sum().reset_index()

c1, c2 = st.columns(2)

with c1:
    st.subheader("Category wise Sales")
    fig = px.bar(
        category_df, x="Category", y="Sales",
        text=[f"${x:,.2f}" for x in category_df["Sales"]],
        template="seaborn"
    )
    st.plotly_chart(fig, use_container_width=True)

with c2:
    st.subheader("Region wise Sales")
    fig = px.pie(filtered_df, values="Sales", names="Region", hole=0.5)
    st.plotly_chart(fig, use_container_width=True)

# ==============================================
# TIME SERIES
# ==============================================
filtered_df["month_year"] = filtered_df["Order Date"].dt.to_period("M")
linechart = filtered_df.groupby(
    filtered_df["month_year"].dt.strftime("%Y-%b")
)["Sales"].sum().reset_index()

st.subheader("Time Series Sales Trend")
fig2 = px.line(linechart, x="month_year", y="Sales", markers=True)
st.plotly_chart(fig2, use_container_width=True)

# ==============================================
# TREEMAP
# ==============================================
st.subheader("Hierarchical Sales (Treemap)")
fig3 = px.treemap(
    filtered_df,
    path=["Region", "Category", "Sub-Category"],
    values="Sales",
    color="Sub-Category"
)
st.plotly_chart(fig3, use_container_width=True)

# ==============================================
# SEGMENT PIE & CATEGORY PIE
# ==============================================
s1, s2 = st.columns(2)

with s1:
    st.subheader("Segment wise Sales")
    fig = px.pie(filtered_df, values="Sales", names="Segment")
    st.plotly_chart(fig, use_container_width=True)

with s2:
    st.subheader("Category wise Sales")
    fig = px.pie(filtered_df, values="Sales", names="Category")
    st.plotly_chart(fig, use_container_width=True)

# ==============================================
# SCATTER PLOT
# ==============================================
st.subheader("Relationship: Sales vs Profit")
fig = px.scatter(filtered_df, x="Sales", y="Profit", size="Quantity")
st.plotly_chart(fig, use_container_width=True)

# ==============================================
# DOWNLOAD ORIGINAL DATA
# ==============================================
csv = df.to_csv(index=False).encode("utf-8")
st.download_button("Download Dataset", csv, "Dataset.csv", "text/csv")
