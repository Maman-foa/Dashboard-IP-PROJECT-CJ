import streamlit as st
import pandas as pd
import plotly.express as px

# =========================
# LOAD DATA
# =========================
FILE_PATH = "Database IP Project Central Java Area 24112025.xlsx"
df = pd.read_excel(FILE_PATH, sheet_name="IPRAN")

# =========================
# MILESTONE MAPPING OTOMATIS
# =========================
MILESTONE_MAP = {
    "00. Migration Done": "Migration Actual",
    "01. Integration Done": "Integration Actual",
    "02. Installation Done": "Install Actual",
    "02a. Permit Install Release": "Permit Install MS Release",
    "02b. Permit Install Submit": "Permit Install MS Submit",
    "03. Material On Delivery": "DO Release",
    "04. Material On Region": "Material in WH",
    "05. Delivery Transfer": "Inbound Date",
    "06. RFI": "RFI Status",
    "07. DRM Done": "DRM Status",
    "08. eTSS Approve XLS": "TSSR Approve XLS",
    "08a. eTSS Approve ZTE": "TSSR Approve ZTE",
    "08b. eTSS Upload": "TSSR Submit by Subcon",
    "09. Survey Done": "Survey Actual",
    "10. PO Batch 1 Total": "Batch"
}

# =========================
# BUAT KOLOM STATUS MILESTONE SECARA OTOMATIS
# =========================
def milestone_completed(df):
    status = {}
    for m, col in MILESTONE_MAP.items():
        status[m] = df[col].notna().sum() if col in df.columns else 0
    return status

# =========================
# STREAMLIT UI
# =========================
st.set_page_config(
    page_title="📊 IPRAN Project Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📊 IPRAN Project Dashboard")
st.markdown("---")

# =========================
# SIDEBAR FILTER
# =========================
st.sidebar.header("Dashboard Options")
dashboard_type = st.sidebar.radio(
    "Pilih Jenis Dashboard",
    ["Summary", "Geographic Map", "Status Tracking"]
)

# Filter Scope Update multi-select
if "Scope Update" in df.columns:
    scope_update_options = sorted(df["Scope Update"].astype(str).unique().tolist())
else:
    scope_update_options = []

selected_scope_update = st.sidebar.multiselect(
    "Filter Scope Update (bisa pilih lebih dari satu)",
    options=scope_update_options,
    default=scope_update_options  # default pilih semua
)

# Filter dataframe sesuai Scope Update
df_filtered = df.copy()
if selected_scope_update:
    df_filtered = df_filtered[df_filtered["Scope Update"].astype(str).isin(selected_scope_update)]

# =========================
# MILESTONE STATUS
# =========================
milestone_status = milestone_completed(df_filtered)

# =========================
# DASHBOARD SUMMARY
# =========================
if dashboard_type == "Summary":
    st.subheader("📈 Milestone Progress Summary")

    # Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Site", len(df_filtered))
    col2.metric("Survey Done", df_filtered["Survey Actual"].notna().sum())
    col3.metric("Migration Done", df_filtered["Migration Actual"].notna().sum())

    st.markdown("### Milestone Completion Chart")
    ms_df = pd.DataFrame({
        "Milestone": list(milestone_status.keys()),
        "Completed": list(milestone_status.values())
    })

    fig = px.bar(
        ms_df.sort_values("Completed", ascending=True),
        x="Completed",
        y="Milestone",
        orientation="h",
        text="Completed",
        title="Progress Semua Milestone",
        color="Completed",
        color_continuous_scale="Viridis"
    )
    fig.update_layout(
        yaxis={'categoryorder':'total ascending'},
        plot_bgcolor="rgba(0,0,0,0)"
    )
    st.plotly_chart(fig, use_container_width=True)

# =========================
# DASHBOARD MAP
# =========================
elif dashboard_type == "Geographic Map":
    st.subheader("🗺 Site Location Map")

    df_map = df_filtered.dropna(subset=["Lat", "Long"])
    st.map(df_map.rename(columns={"Lat": "lat", "Long": "lon"}))

# =========================
# DASHBOARD STATUS TRACKING
# =========================
elif dashboard_type == "Status Tracking":
    st.subheader("📋 Data Tracking Full")
    st.dataframe(df_filtered, use_container_width=True)
