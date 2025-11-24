import streamlit as st
import pandas as pd
import plotly.express as px

# =============================
# STREAMLIT CONFIG
# =============================
st.set_page_config(page_title="IPRAN Dashboard", layout="wide")

st.title("📊 IPRAN Project Dashboard")

# =============================
# FILE UPLOADER
# =============================
uploaded = st.file_uploader(
    "Upload File XLSX Database IPRAN",
    type=["xlsx"],
    help="Upload file: Database IP Project Central Java Area 24112025.xlsx"
)

if uploaded is None:
    st.warning("Silakan upload file XLSX terlebih dahulu.")
    st.stop()

# =============================
# LOAD SHEET IPRAN
# =============================
try:
    df = pd.read_excel(uploaded, sheet_name="IPRAN")
except Exception as e:
    st.error("❌ Gagal membaca sheet 'IPRAN'. Pastikan sheet tersebut ada di file.")
    st.stop()

# Normalisasi kolom
df.columns = df.columns.str.strip()

# Pastikan kolom numerik tetap aman
if "Region" in df.columns:
    df["Region"] = df["Region"].astype(str)

# =============================
# MILESTONE MAP OTOMATIS
# =============================
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

# =============================
# HITUNG STATUS MILESTONE
# =============================
def milestone_completed(df):
    result = {}
    for milestone, col in MILESTONE_MAP.items():
        if col not in df.columns:
            result[milestone] = 0
        else:
            result[milestone] = df[col].notna().sum()
    return result

milestone_status = milestone_completed(df)

# =============================
# JENIS DASHBOARD
# =============================
dashboard_type = st.selectbox(
    "Pilih Jenis Dashboard",
    ["Summary", "Geographic Map", "Status Tracking"]
)

# =============================
# SUMMARY PROGRESS (BAR CHART)
# =============================
st.subheader("📈 Milestone Progress Summary")

ms_df = pd.DataFrame({
    "Milestone": list(milestone_status.keys()),
    "Completed": list(milestone_status.values())
})

fig = px.bar(
    ms_df,
    x="Milestone",
    y="Completed",
    text="Completed",
    title="Progress Semua Milestone",
    color="Completed"
)

st.plotly_chart(fig, use_container_width=True)

# =============================
# DASHBOARD DETAIL
# =============================
if dashboard_type == "Geographic Map":
    st.subheader("🗺 Site Location Map")

    if {"Lat", "Long"}.issubset(df.columns):
        df_map = df.dropna(subset=["Lat", "Long"])
        df_map = df_map.rename(columns={"Lat": "lat", "Long": "lon"})
        st.map(df_map)
    else:
        st.error("Kolom Lat / Long tidak ditemukan.")

elif dashboard_type == "Status Tracking":
    st.subheader("📋 Full Tracking Data")

    if "Region" not in df.columns:
        st.error("Kolom 'Region' tidak ditemukan di file.")
        st.stop()

    region_list = ["All"] + sorted(df["Region"].astype(str).unique().tolist())

    region = st.selectbox("Filter Region", region_list)

    df_filtered = df if region == "All" else df[df["Region"].astype(str) == region]

    st.dataframe(df_filtered, use_container_width=True)

else:
    st.subheader("📌 Summary Angka")

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Site", len(df))
    col2.metric("Survey Done", df["Survey Actual"].notna().sum() if "Survey Actual" in df.columns else 0)
    col3.metric("Migration Done", df["Migration Actual"].notna().sum() if "Migration Actual" in df.columns else 0)
