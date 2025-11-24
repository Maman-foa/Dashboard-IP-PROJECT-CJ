import streamlit as st
import pandas as pd
import plotly.express as px

# =========================
# LOAD DATA
# =========================
FILE_PATH = "/mnt/data/Database IP Project Central Java Area 24112025.xlsx"
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
        if col not in df.columns:
            status[m] = 0
        else:
            status[m] = df[col].notna().sum()
    return status

milestone_status = milestone_completed(df)

# =========================
# STREAMLIT UI
# =========================
st.title("📊 IPRAN Project Dashboard")

dashboard_type = st.selectbox(
    "Pilih Jenis Dashboard",
    ["Summary", "Geographic Map", "Status Tracking"]
)

st.subheader("Milestone Progress Summary")

# =========================
# CHART
# =========================
ms_df = pd.DataFrame({
    "Milestone": list(milestone_status.keys()),
    "Completed": list(milestone_status.values())
})

fig = px.bar(
    ms_df,
    x="Milestone",
    y="Completed",
    title="Progress Semua Milestone",
    text="Completed"
)

st.plotly_chart(fig, use_container_width=True)

# =========================
# DASHBOARD DETAIL
# =========================
if dashboard_type == "Geographic Map":
    st.subheader("🗺 Site Location Map")

    df_map = df.dropna(subset=["Lat", "Long"])

    st.map(df_map.rename(columns={"Lat": "lat", "Long": "lon"}))

elif dashboard_type == "Status Tracking":
    st.subheader("📋 Data Tracking Full")

    region = st.selectbox("Filter Region", ["All"] + sorted(df["Region"].unique().tolist()))

    df_filtered = df if region == "All" else df[df["Region"] == region]

    st.dataframe(df_filtered)

else:
    st.subheader("Summary Angka")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Site", len(df))
    col2.metric("Survey Done", df["Survey Actual"].notna().sum())
    col3.metric("Migration Done", df["Migration Actual"].notna().sum())
