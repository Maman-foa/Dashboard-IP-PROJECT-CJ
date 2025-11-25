# dashboard_ipran.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import warnings
warnings.filterwarnings("ignore")

st.set_page_config(page_title="IPRAN Progress Dashboard", page_icon=":satellite:", layout="wide")

# -------------------------
# Helper: find a column among candidates
# -------------------------
def find_col(df, candidates):
    for c in candidates:
        if c in df.columns:
            return c
    return None

# -------------------------
# Header / UI style (modern)
# -------------------------
st.markdown(
    """
    <style>
    .header {
        display:flex;
        align-items:center;
        gap:18px;
    }
    .title {
        font-size:28px;
        font-weight:700;
        margin:0;
    }
    .subtitle {
        color:#666;
        margin:0;
        font-size:13px;
    }
    .card {
        padding:12px;
        border-radius:12px;
        background: linear-gradient(90deg, rgba(255,255,255,0.9), rgba(245,245,245,0.9));
        box-shadow: 0 6px 18px rgba(0,0,0,0.06);
    }
    </style>
    """,
    unsafe_allow_html=True
)

col_h1, col_h2 = st.columns([0.7, 0.3])
with col_h1:
    st.markdown('<div class="header"><div class="card"><div>'
                '<p class="title">IPRAN / IPBB Central Java — Progress Dashboard</p>'
                '<p class="subtitle">Source: Update Progress IPRAN IPBB Central Java 25112025 (sheet IPRAN)</p>'
                '</div></div></div>',
                unsafe_allow_html=True)

with col_h2:
    st.markdown('<div class="card"><p style="margin:0;font-weight:600">Last updated:</p>'
                f'<p style="margin:0">{datetime.now().strftime("%d %b %Y %H:%M")}</p></div>',
                unsafe_allow_html=True)

st.divider()

# -------------------------
# File uploader / load default
# -------------------------
st.sidebar.header("Data source")
uploaded = st.sidebar.file_uploader("Upload Excel (.xlsx) or CSV (optional)", type=["xlsx", "xls", "csv", "txt"])

if uploaded is not None:
    if uploaded.name.lower().endswith((".xlsx", ".xls")):
        df = pd.read_excel(uploaded, sheet_name="IPRAN" if "IPRAN" in pd.ExcelFile(uploaded).sheet_names else 0)
    else:
        df = pd.read_csv(uploaded)
else:
    DEFAULT = "Update Progress IPRAN IPBB Central Java 25112025.xlsx"
    st.sidebar.info(f"Using default file in repo: {DEFAULT}")
    try:
        df = pd.read_excel(DEFAULT, sheet_name="IPRAN")
    except Exception as e:
        st.sidebar.error(f"Cannot read default file: {e}")
        st.stop()

# show columns for debugging / mapping
with st.expander("Detected columns (click to expand)"):
    st.write(list(df.columns))

# -------------------------
# Column mapping (try multiple possible names)
# -------------------------
col_scope_candidates = ["Scope", "Scope Update", "SOW", "ScopeID"]
col_subcon_install_candidates = ["Subcon Install", "SubconInstall", "Subcon_Install"]
col_migration_plan_candidates = ["Migration Plan", "MigrationPlan", "New Mig Plan", "Plan Migration"]
col_migration_actual_candidates = ["Migration Actual", "MigrationActual", "Migration_Actual"]
col_inbound_candidates = ["Inbound Date", "InboundDate", "Inbound_Date"]
col_dismantle_candidates = ["Dismantle Date", "DismantleDate", "Dismantle_Date"]
col_province_candidates = ["Province", "PROVINCE", "Province Name"]
col_city_candidates = ["City", "CITY", "Kota"]
col_sow_candidates = ["SOW", "SOW " , "SOW"]  # SOW likely present
col_status_candidates = ["Status", "Site Status", "SPK Status"]

col_scope = find_col(df, col_scope_candidates)
col_subcon_install = find_col(df, col_subcon_install_candidates)
col_mig_plan = find_col(df, col_migration_plan_candidates)
col_mig_actual = find_col(df, col_migration_actual_candidates)
col_inbound = find_col(df, col_inbound_candidates)
col_dismantle = find_col(df, col_dismantle_candidates)
col_province = find_col(df, col_province_candidates)
col_city = find_col(df, col_city_candidates)
col_sow = find_col(df, col_sow_candidates)
col_status = find_col(df, col_status_candidates)

# Inform about mapping
mapping_info = {
    "Scope (for Swap/New/Modernize/Service Migration)": col_scope,
    "Subcon Install column": col_subcon_install,
    "Migration Plan (timeline)": col_mig_plan,
    "Migration Actual (done)": col_mig_actual,
    "Inbound Date": col_inbound,
    "Dismantle Date": col_dismantle,
    "Province": col_province,
    "City": col_city,
    "SOW": col_sow,
    "Status": col_status
}
st.sidebar.subheader("Column mapping (auto-detected)")
for k, v in mapping_info.items():
    st.sidebar.write(f"• {k}: **{v or 'NOT FOUND'}**")

# If critical columns missing, warn but continue with best-effort
if not col_scope:
    st.warning("Kolom untuk kategori (Scope/SOW) tidak ditemukan. Summary A mungkin tidak lengkap.")
if not (col_province and col_city and col_sow):
    st.warning("Treemap membutuhkan Province, City, dan SOW — bila salah satu tidak ada, treemap mungkin tidak lengkap.")

# -------------------------
# Preprocess dates (try parse)
# -------------------------
def try_parse_date(colname):
    if (colname is None) or (colname not in df.columns):
        return None
    # try to convert to datetime, coerce errors
    try:
        ser = pd.to_datetime(df[colname], errors="coerce")
        return ser
    except Exception:
        return pd.to_datetime(df[colname].astype(str), errors="coerce")

# create parsed date series
mig_plan_dates = try_parse_date(col_mig_plan)
mig_actual_dates = try_parse_date(col_mig_actual)
inbound_dates = try_parse_date(col_inbound)
dismantle_dates = try_parse_date(col_dismantle)

# attach parsed as temp columns for analysis
if mig_plan_dates is not None:
    df["_mig_plan_dt"] = mig_plan_dates
if mig_actual_dates is not None:
    df["_mig_actual_dt"] = mig_actual_dates
if inbound_dates is not None:
    df["_inbound_dt"] = inbound_dates
if dismantle_dates is not None:
    df["_dismantle_dt"] = dismantle_dates

# -------------------------
# A. Summary / Count: categories Swap / New / Modernize / Service Migration
# We'll try using Scope -> Scope Update -> SOW in that order
# -------------------------
cat_col = col_scope or find_col(df, ["Scope Update", "SOW", "ScopeID", "SOW "])
if cat_col:
    # normalize text
    df["_cat_norm"] = df[cat_col].astype(str).str.strip().str.title()
    # only keep the four categories requested if present; otherwise show top categories
    wanted = ["Swap", "New", "Modernize", "Service Migration"]
    # create counts
    cat_counts = df["_cat_norm"].value_counts().rename_axis("Category").reset_index(name="Count")
    # ensure wanted order present
    counts_wanted = cat_counts[cat_counts["Category"].isin(wanted)].set_index("Category").reindex(wanted).fillna(0).reset_index()
else:
    df["_cat_norm"] = "Unknown"
    counts_wanted = pd.DataFrame({"Category": ["Swap", "New", "Modernize", "Service Migration"], "Count": [0,0,0,0]})

# display summary cards
c1, c2, c3, c4 = st.columns(4)
for col_box, row in zip([c1, c2, c3, c4], counts_wanted.itertuples(index=False)):
    with col_box:
        st.metric(label=row[0], value=int(row[1]))

st.markdown("---")

# -------------------------
# B1. Bar Chart: Count by Subcon Install / Migration
# We'll produce two bars: count by Subcon Install (group value counts) and count of planned migrations by assignee/subcon if available
# -------------------------
st.subheader("Bar Chart — Subcon Install & Migration")

bar_df_list = []
if col_subcon_install and col_subcon_install in df.columns:
    subcon_counts = df[col_subcon_install].fillna("Unknown").astype(str).value_counts().reset_index()
    subcon_counts.columns = ["Key", "Subcon_Count"]
    subcon_counts = subcon_counts.head(20)
    bar_df_list.append(("Subcon Install", subcon_counts))
else:
    # use placeholder empty
    subcon_counts = pd.DataFrame({"Key": [], "Subcon_Count": []})

# For migration: count planned migrations per some key (e.g., SOW or Subcon Install)
if "_mig_plan_dt" in df.columns:
    # count plans per month
    mig_plan_month = df.dropna(subset=["_mig_plan_dt"])
    mig_plan_month["plan_month"] = mig_plan_month["_mig_plan_dt"].dt.to_period("M").dt.strftime("%Y-%b")
    mig_month_counts = mig_plan_month["plan_month"].value_counts().reset_index().sort_values("index")
    mig_month_counts.columns = ["Key", "Mig_Plan_Count"]
    bar_df_list.append(("Migration Plan (by Month)", mig_month_counts))
else:
    mig_month_counts = pd.DataFrame({"Key": [], "Mig_Plan_Count": []})

# Display bar charts side by side
b1, b2 = st.columns(2)
with b1:
    if not subcon_counts.empty:
        fig = px.bar(subcon_counts, x="Key", y="Subcon_Count", title="Top Subcon Install (count)", template="plotly_white")
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Kolom 'Subcon Install' tidak tersedia — tidak ada data untuk bar chart Subcon Install.")

with b2:
    if not mig_month_counts.empty:
        fig = px.bar(mig_month_counts.sort_values("Key"), x="Key", y="Mig_Plan_Count",
                     title="Migration Plan Count by Month", labels={"Key":"Month","Mig_Plan_Count":"Count"},
                     template="plotly_white")
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Kolom 'Migration Plan' tidak tersedia atau tidak ada tanggal plan untuk membuat chart timeline-by-month. Lihat Timeline di bawah.")

st.markdown("---")

# -------------------------
# B2. Pie Chart: Inbound, Dismantle, Migration Done
# We'll compute counts of records that have inbound date, dismantle date, migration actual date
# -------------------------
st.subheader("Pie Chart — Inbound / Dismantle / Migration Done")

pie_counts = {}
pie_counts["Inbound"] = int(df["_inbound_dt"].notna().sum()) if "_inbound_dt" in df.columns else 0
pie_counts["Dismantle"] = int(df["_dismantle_dt"].notna().sum()) if "_dismantle_dt" in df.columns else 0
pie_counts["Migration Done"] = int(df["_mig_actual_dt"].notna().sum()) if "_mig_actual_dt" in df.columns else 0

pie_df = pd.DataFrame({"Stage": list(pie_counts.keys()), "Count": list(pie_counts.values())})
if pie_df["Count"].sum() == 0:
    st.info("Tidak ada data tanggal Inbound / Dismantle / Migration Actual yang terdeteksi — pie chart kosong.")
else:
    fig = px.pie(pie_df, names="Stage", values="Count", hole=0.4, title="Inbound vs Dismantle vs Migration Done")
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# -------------------------
# B3. Timeline: Plan Migration (time-series of planned migrations)
# -------------------------
st.subheader("Timeline — Migration Plan (planned migrations over time)")
if "_mig_plan_dt" in df.columns and df["_mig_plan_dt"].notna().any():
    timeline_df = df.dropna(subset=["_mig_plan_dt"]).copy()
    # group by week or month depending on range
    days_range = (timeline_df["_mig_plan_dt"].max() - timeline_df["_mig_plan_dt"].min()).days
    if days_range <= 90:
        # show weekly
        timeline_df["period"] = timeline_df["_mig_plan_dt"].dt.to_period("W").apply(lambda r: r.start_time.strftime("%Y-%b-%d"))
    else:
        timeline_df["period"] = timeline_df["_mig_plan_dt"].dt.to_period("M").dt.strftime("%Y-%b")
    timeseries = timeline_df["period"].value_counts().reset_index().sort_values("index")
    timeseries.columns = ["Period", "Planned_Count"]
    fig = px.line(timeseries, x="Period", y="Planned_Count", markers=True, title="Planned Migrations over Time", template="plotly_white")
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Tidak menemukan tanggal pada kolom Migration Plan untuk membuat timeline. Pastikan kolom 'Migration Plan' terdeteksi.")

st.markdown("---")

# -------------------------
# B4. Treemap: Province -> City -> SOW
# -------------------------
st.subheader("Treemap — Province → City → SOW")
if col_province and col_city and col_sow:
    treemap_df = df[[col_province, col_city, col_sow]].fillna("Unknown")
    # aggregate counts or SOW counts
    treemap_df["_count"] = 1
    agg = treemap_df.groupby([col_province, col_city, col_sow])["_count"].sum().reset_index()
    fig = px.treemap(agg, path=[col_province, col_city, col_sow], values="_count", title="Treemap by Province / City / SOW", template="plotly_white")
    st.plotly_chart(fig, use_container_width=True, height=700)
else:
    st.info("Treemap memerlukan kolom Province, City, dan SOW. Salah satu atau lebih tidak terdeteksi.")

st.markdown("---")

# -------------------------
# C. Filters + Data table + Downloads
# -------------------------
st.sidebar.header("Filters")
# date filters for plan / actual if exist
if "_mig_plan_dt" in df.columns:
    min_date = df["_mig_plan_dt"].min()
    max_date = df["_mig_plan_dt"].max()
    plan_date_range = st.sidebar.date_input("Migration Plan date range", value=(min_date.date() if pd.notna(min_date) else None, max_date.date() if pd.notna(max_date) else None))
else:
    plan_date_range = None

# basic filters
province_sel = st.sidebar.multiselect("Province", options=sorted(df[col_province].dropna().unique()) if col_province else [])
city_sel = st.sidebar.multiselect("City", options=sorted(df[col_city].dropna().unique()) if col_city else [])
sow_sel = st.sidebar.multiselect("SOW", options=sorted(df[col_sow].dropna().unique()) if col_sow else [])
status_sel = st.sidebar.multiselect("Status", options=sorted(df[col_status].dropna().unique()) if col_status else [])

# apply filters
df_view = df.copy()
if province_sel and col_province:
    df_view = df_view[df_view[col_province].isin(province_sel)]
if city_sel and col_city:
    df_view = df_view[df_view[col_city].isin(city_sel)]
if sow_sel and col_sow:
    df_view = df_view[df_view[col_sow].isin(sow_sel)]
if status_sel and col_status:
    df_view = df_view[df_view[col_status].isin(status_sel)]
if plan_date_range and "_mig_plan_dt" in df_view.columns:
    start_dt = pd.to_datetime(plan_date_range[0])
    end_dt = pd.to_datetime(plan_date_range[1])
    df_view = df_view[(df_view["_mig_plan_dt"] >= start_dt) & (df_view["_mig_plan_dt"] <= end_dt)]

st.subheader("Filtered Data (preview)")
st.dataframe(df_view.head(500))

st.download_button("Download filtered data (CSV)", data=df_view.to_csv(index=False).encode("utf-8"), file_name="ipran_filtered.csv", mime="text/csv")

st.markdown("### Notes & mapping")
st.write(mapping_info)
st.write("Jika ada nama kolom yang berbeda dari dataset Anda, beri tahu saya nama kolom yang benar (mis. 'Scope Update' atau 'SOW') — saya akan sesuaikan mapping agar statistik lebih akurat.")
