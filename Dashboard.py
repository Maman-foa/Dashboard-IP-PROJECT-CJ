import streamlit as st
import pandas as pd

st.set_page_config(page_title="IPRAN Dashboard", layout="wide")

st.title("📊 IPRAN Dashboard")

# ===========================
# UPLOAD FILE
# ===========================
uploaded_file = st.file_uploader("Upload File XLSX:", type=["xlsx"])

if uploaded_file is None:
    st.warning("Silakan upload file XLSX untuk melanjutkan.")
    st.stop()

# ===========================
# BACA SHEET IPRAN
# ===========================
try:
    df = pd.read_excel(uploaded_file, sheet_name="IPRAN")
except Exception as e:
    st.error("❌ Gagal membaca sheet 'IPRAN'. Pastikan sheet ada pada file.")
    st.stop()

st.success("File berhasil dibaca!")
st.dataframe(df.head())

# ===========================
# PILIH DASHBOARD
# ===========================
dashboard_type = st.selectbox(
    "Pilih jenis dashboard:",
    ["Summary Milestone", "Progress Harian", "Ringkasan Region"]
)

# ===========================
# MAPPING OTOMATIS MILESTONE
# ===========================
milestone_mapping = {
    "00. Migration Done": "Migration Actual",
    "01. Integration Done": "Integration Actual",
    "02. Installation Done": "Install Actual",
    "02a. Permit Install Release": "Permit Install MS Release",
    "02b. Permit Install Submit": "Permit Install MS Submit",
    "03. Material On Delivery": "Material in WH",
    "04. Material On Region": "Material Source",
    "05. Delivery Transfer": "Inbound Date",
    "06. RFI": "RFI Status",
    "07. DRM Done": "DRM Status",
    "08. eTSS Approve XLS": "TSSR Approve XLS",
    "08a. eTSS Approve ZTE": "TSSR Approve ZTE",
    "08b. eTSS Upload": "TSSR Submit by Subcon",
    "09. Survey Done": "Survey Actual",
    "10. PO Batch 1 Total": "Batch"
}

st.write("### Mapping Milestone → Kolom File")
st.table(pd.DataFrame(milestone_mapping.items(), columns=["Milestone", "Kolom XLSX"]))

# ===========================
# OUTPUT STREAMLIT
# ===========================
st.write("### Output Dashboard")
st.info(f"Menampilkan dashboard: **{dashboard_type}**")
