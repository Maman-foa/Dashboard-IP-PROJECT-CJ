import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image

st.set_page_config(page_title="IPRAN Dashboard", layout="wide")

# =============================
# CUSTOM CSS — STYLE ADIDAS
# =============================
st.markdown("""
<style>
body {
    background-color: #f5f7fa;
}
.sidebar .sidebar-content {
    background-color: #ffffff;
}
.block-container {
    padding-top: 1rem;
}
.card {
    background: white;
    padding: 15px 25px;
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    margin-bottom: 25px;
}
h1, h2, h3 {
    font-weight: 700;
}
</style>
""", unsafe_allow_html=True)

# =============================
# LOAD FILE
# =============================
FILE_DEFAULT = "Update Progress IPRAN IPBB Central Java 25112025.xlsx"

uploaded = st.file_uploader("Upload Excel", type=["xlsx"])

if uploaded:
    df = pd.read_excel(uploaded, sheet_name="IPRAN")
else:
    st.info(f"Using default file in repo: {FILE_DEFAULT}")
    df = pd.read_excel(FILE_DEFAULT, sheet_name="IPRAN")

# =============================
# CLEAN / DATE PARSING
# =============================
date_cols = ["Migration Plan", "Migration Actual", "Inbound Date", "Dismantle Date"]
for c in date_cols:
    df[c] = pd.to_datetime(df[c], errors="coerce")

# Create Month column for migration timeline
df["Plan_Month"] = df["Migration Plan"].dt.to_period("M").astype(str)

# =============================
# HEADER
# =============================
col1, col2 = st.columns([0.15, 0.85])
with col1:
    st.image(Image.open("adidas-logo.jpg"), width=90)

with col2:
    st.markdown("<h1>IPRAN Interactive Dashboard</h1>", unsafe_allow_html=True)
    st.write("Last Update:", pd.Timestamp.today().strftime("%d %B %Y"))

st.markdown("### **A. Summary / Count**")

# =============================
# SUMMARY COUNT — BASED ON Scope Update
# =============================
scope_list = ["Swap", "New", "Modernize", "Service Migration"]

col_a, col_b, col_c, col_d = st.columns(4)
for (col, sc) in zip([col_a, col_b, col_c, col_d], scope_list):
    with col:
        count = df[df["Scope Update"] == sc].shape[0]  # <-- Ubah kolom di sini
        st.markdown(f"""
        <div class="card">
            <h3 style='color:#0055aa'>{sc}</h3>
            <h2>{count}</h2>
        </div>
        """, unsafe_allow_html=True)


# =============================
# SECTION B — GRAFIK
# =============================
st.markdown("## **B. Grafik**")

# === 1. Bar Chart — Subcon Install / Migration ===
bar_data = (
    df.groupby("Subcon Install")["Uniq ID"]
    .count()
    .reset_index()
    .rename(columns={"Uniq ID": "Count"})
)

st.markdown("### **Bar Chart — Subcon Install & Migration**")
fig_bar = px.bar(
    bar_data, 
    x="Subcon Install", 
    y="Count",
    color="Count",
    title="Subcon Install Count",
    template="simple_white"
)
st.plotly_chart(fig_bar, use_container_width=True)

# === 2. Pie Chart – Inbound, Dismantle, Migration Done ===
pie_data = {
    "Inbound": df["Inbound Date"].notna().sum(),
    "Dismantle": df["Dismantle Date"].notna().sum(),
    "Migration Done": df["Migration Actual"].notna().sum()
}
pie_df = pd.DataFrame({"Category": pie_data.keys(), "Count": pie_data.values()})

st.markdown("### **Pie Chart — Inbound / Dismantle / Migration Done**")
fig_pie = px.pie(
    pie_df,
    names="Category",
    values="Count",
    title="Inbound / Dismantle / Migration Done"
)
st.plotly_chart(fig_pie, use_container_width=True)

# === 3. Timeline — Plan Migration ===
st.markdown("### **Timeline — Migration Plan**")

timeline_data = (
    df["Plan_Month"]
    .value_counts()
    .reset_index()
    .rename(columns={"index": "Month", "Plan_Month": "Count"})
    .sort_values("Month")
)

fig_time = px.line(
    timeline_data, 
    x="Month", 
    y="Count",
    markers=True,
    title="Migration Plan Timeline"
)
st.plotly_chart(fig_time, use_container_width=True)

# === 4. Treemap Province → City → SOW ===
st.markdown("### **Treemap — Province → City → SOW**")

df_treemap = df.groupby(["Province", "City", "SOW"])["Uniq ID"].count().reset_index()

fig_tree = px.treemap(
    df_treemap,
    path=["Province", "City", "SOW"],
    values="Uniq ID",
    title="Treemap: Province → City → SOW"
)
st.plotly_chart(fig_tree, use_container_width=True)

# =============================
# END
# =============================
st.success("Dashboard loaded successfully!")
