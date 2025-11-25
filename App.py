import streamlit as st
import pandas as pd
import plotly.express as px

# =========================================================
# LOAD DATA
# =========================================================
FILE_PATH = "Database IP Project Central Java Area 24112025.xlsx"

@st.cache_data
def load_data():
    df = pd.read_excel(FILE_PATH, sheet_name="IPRAN")
    return df

df = load_data()

# =========================================================
# MILESTONE OTOMATIS (berdasarkan kolom Migration Actual)
# =========================================================
MILESTONE_MAP = {
    "00 Not Started": ["", None, "NA", "N/A"],
    "10 On Progress": ["IN PROGRESS", "ONGOING"],
    "20 Done & Verified": ["DONE", "VERIFIED", "COMPLETED"]
}

def map_milestone(value):
    if pd.isna(value) or str(value).strip() in ["", "-", "None"]:
        return "00 Not Started"
    val = str(value).upper().strip()

    for milestone, keys in MILESTONE_MAP.items():
        for key in keys:
            if key and key in val:
                return milestone

    # Jika ada tanggal → otomatis Done
    try:
        pd.to_datetime(value)
        return "20 Done & Verified"
    except:
        pass

    return "10 On Progress"

df["Milestone Auto"] = df["Migration Actual"].apply(map_milestone)

# =========================================================
# UI/UX HEADER
# =========================================================
st.set_page_config(page_title="Dashboard IP Project", layout="wide")

st.markdown("""
    <h2 style='text-align:center; color:#4CAF50;'>📊 IP PROJECT DASHBOARD – CENTRAL JAVA</h2>
    <hr>
""", unsafe_allow_html=True)

# =========================================================
# FILTERS
# =========================================================
col1, col2, col3 = st.columns(3)

with col1:
    selected_witel = st.multiselect(
        "Pilih Witel:",
        sorted(df["WITEL"].unique()),
        default=None
    )

with col2:
    selected_status = st.multiselect(
        "Pilih Milestone:",
        sorted(df["Milestone Auto"].unique()),
        default=None
    )

with col3:
    selected_odp = st.text_input("Cari ODP (optional):")

# Apply filters
filtered_df = df.copy()

if selected_witel:
    filtered_df = filtered_df[filtered_df["WITEL"].isin(selected_witel)]

if selected_status:
    filtered_df = filtered_df[filtered_df["Milestone Auto"].isin(selected_status)]

if selected_odp:
    filtered_df = filtered_df[filtered_df["ODP NAME"].str.contains(selected_odp, case=False, na=False)]

# =========================================================
# KPI CARDS
# =========================================================
total = len(filtered_df)
done = len(filtered_df[filtered_df["Milestone Auto"] == "20 Done & Verified"])
progress = len(filtered_df[filtered_df["Milestone Auto"] == "10 On Progress"])
not_started = len(filtered_df[filtered_df["Milestone Auto"] == "00 Not Started"])

colA, colB, colC, colD = st.columns(4)

colA.metric("Total Project", total)
colB.metric("Completed", done)
colC.metric("On Progress", progress)
colD.metric("Not Started", not_started)

# =========================================================
# VISUALIZATION
# =========================================================
st.subheader("📈 Distribusi Milestone")

fig = px.pie(
    filtered_df,
    names="Milestone Auto",
    title="Milestone Distribution",
    hole=0.5
)
st.plotly_chart(fig, use_container_width=True)

# =========================================================
# TABEL DATA
# =========================================================
st.subheader("📋 Detail Data Project")
st.dataframe(filtered_df, use_container_width=True)

# =========================================================
# DOWNLOAD BUTTON
# =========================================================
st.download_button(
    label="Download Data (Filtered)",
    data=filtered_df.to_csv(index=False).encode("utf-8"),
    file_name="filtered_ip_project.csv",
    mime="text/csv"
)
