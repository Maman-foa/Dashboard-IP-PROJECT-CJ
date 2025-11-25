import streamlit as st
import plotly.express as px
import plotly.figure_factory as ff
import pandas as pd
import warnings

warnings.filterwarnings('ignore')

# ================================
# PAGE CONFIG
# ================================
st.set_page_config(page_title="Superstore!!!", page_icon=":bar_chart:", layout="wide")

st.title(" :bar_chart: Sample SuperStore EDA")
st.markdown('<style>div.block-container{padding-top:1rem;}</style>', unsafe_allow_html=True)

# ================================
# FILE UPLOADER
# ================================
st.sidebar.header("Upload or Use Default File")

uploaded_file = st.file_uploader(":file_folder: Upload a file", type=["csv", "txt", "xlsx", "xls"])

if uploaded_file is not None:
    st.write("File uploaded:", uploaded_file.name)

    # Baca otomatis jenis file
    if uploaded_file.name.endswith((".csv", ".txt")):
        df = pd.read_csv(uploaded_file, encoding="ISO-8859-1")
    else:
        df = pd.read_excel(uploaded_file)

else:
    # Fallback: gunakan file default di repo
    DEFAULT_FILE = "Database IP Project Central Java Area 24112025.xlsx"
    st.sidebar.warning(f"Using default file: {DEFAULT_FILE}")
    df = pd.read_excel(DEFAULT_FILE)

# ================================
# CLEAN DATA
# ================================
df["Order Date"] = pd.to_datetime(df["Order Date"])

startDate = df["Order Date"].min()
endDate = df["Order Date"].max()

# ================================
# DATE FILTER
# ================================
col1, col2 = st.columns((2))

with col1:
    date1 = pd.to_datetime(st.date_input("Start Date", startDate))

with col2:
    date2 = pd.to_datetime(st.date_input("End Date", endDate))

df = df[(df["Order Date"] >= date1) & (df["Order Date"] <= date2)].copy()

# ================================
# SIDEBAR FILTERS
# ================================
st.sidebar.header("Choose your filter: ")

region = st.sidebar.multiselect("Pick your Region", df["Region"].unique())

df2 = df if not region else df[df["Region"].isin(region)]

state = st.sidebar.multiselect("Pick the State", df2["State"].unique())

df3 = df2 if not state else df2[df2["State"].isin(state)]

city = st.sidebar.multiselect("Pick the City", df3["City"].unique())

# ================================
# APPLY FILTERS
# ================================
if not region and not state and not city:
    filtered_df = df
elif region and not state and not city:
    filtered_df = df[df["Region"].isin(region)]
elif not region and state and not city:
    filtered_df = df[df["State"].isin(state)]
elif city:
    filtered_df = df3[df3["City"].isin(city)]
else:
    filtered_df = df3

# ================================
# CATEGORY SALES CHART
# ================================
category_df = filtered_df.groupby("Category", as_index=False)["Sales"].sum()

col1, col2 = st.columns((2))

with col1:
    st.subheader("Category wise Sales")
    fig = px.bar(category_df, x="Category", y="Sales",
                 text=[f"${x:,.2f}" for x in category_df["Sales"]],
                 template="seaborn")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Region wise Sales")
    fig = px.pie(filtered_df, values="Sales", names="Region", hole=0.5)
    fig.update_traces(textposition="outside")
    st.plotly_chart(fig, use_container_width=True)

# ================================
# TABLE DOWNLOADS
# ================================
cl1, cl2 = st.columns((2))

with cl1:
    with st.expander("Category_ViewData"):
        st.write(category_df.style.background_gradient(cmap="Blues"))
        st.download_button("Download Data", 
                           data=category_df.to_csv(index=False).encode('utf-8'),
                           file_name="Category.csv",
                           mime="text/csv")

with cl2:
    with st.expander("Region_ViewData"):
        region_table = filtered_df.groupby("Region", as_index=False)["Sales"].sum()
        st.write(region_table.style.background_gradient(cmap="Oranges"))
        st.download_button("Download Data",
                           data=region_table.to_csv(index=False).encode('utf-8'),
                           file_name="Region.csv",
                           mime="text/csv")

# ================================
# TIME SERIES
# ================================
filtered_df["month_year"] = filtered_df["Order Date"].dt.to_period("M")

st.subheader("Time Series Analysis")

linechart = (
    filtered_df.groupby(filtered_df["month_year"].dt.strftime("%Y : %b"))["Sales"].sum()
    .reset_index()
)

fig2 = px.line(linechart, x="month_year", y="Sales",
               labels={"Sales": "Amount"}, height=500, template="gridon")
st.plotly_chart(fig2, use_container_width=True)

with st.expander("View Data of TimeSeries:"):
    st.write(linechart.T.style.background_gradient(cmap="Blues"))
    st.download_button('Download Data',
                       data=linechart.to_csv(index=False).encode("utf-8"),
                       file_name="TimeSeries.csv",
                       mime='text/csv')

# ================================
# TREEMAP
# ================================
st.subheader("Hierarchical view of Sales using TreeMap")

fig3 = px.treemap(filtered_df,
                  path=["Region", "Category", "Sub-Category"],
                  values="Sales",
                  hover_data=["Sales"],
                  color="Sub-Category")
st.plotly_chart(fig3, use_container_width=True)

# ================================
# PIE CHARTS
# ================================
chart1, chart2 = st.columns((2))

with chart1:
    st.subheader('Segment wise Sales')
    fig = px.pie(filtered_df, values="Sales", names="Segment", template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

with chart2:
    st.subheader('Category wise Sales')
    fig = px.pie(filtered_df, values="Sales", names="Category", template="gridon")
    st.plotly_chart(fig, use_container_width=True)

# ================================
# TABLE SUMMARY
# ================================
st.subheader(":point_right: Month wise Sub-Category Sales Summary")

with st.expander("Summary_Table"):
    df_sample = df[["Region", "State", "City", "Category", "Sales", "Profit", "Quantity"]].head(5)
    fig = ff.create_table(df_sample)
    st.plotly_chart(fig, use_container_width=True)

    filtered_df["month"] = filtered_df["Order Date"].dt.month_name()
    pivot_table = pd.pivot_table(filtered_df, values="Sales",
                                 index="Sub-Category", columns="month")
    st.write(pivot_table.style.background_gradient(cmap="Blues"))

# ================================
# SCATTER PLOT
# ================================
scatter_fig = px.scatter(filtered_df, x="Sales", y="Profit", size="Quantity")
st.plotly_chart(scatter_fig, use_container_width=True)

with st.expander("View Data"):
    st.write(filtered_df.iloc[:500, 1:20:2].style.background_gradient(cmap="Oranges"))

# ================================
# DOWNLOAD ORIGINAL DATA
# ================================
st.download_button("Download Data",
                   data=df.to_csv(index=False).encode('utf-8'),
                   file_name="Data.csv",
                   mime="text/csv")
