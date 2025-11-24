import streamlit as st
import plotly.graph_objects as go

# ====== CONFIG ======
st.set_page_config(page_title="CRM Dashboard", layout="wide")

# ====== CUSTOM CSS ======
st.markdown("""
<style>
:root {
    --primary-color: #556BFF;
    --background-color: #F8F9FA;
    --card-background: #FFFFFF;
    --text-dark: #333333;
    --text-light: #6c757d;
}

.block-container {
    padding-top: 1rem;
}

.card {
    background-color: var(--card-background);
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.card-value {
    font-size: 2rem;
    font-weight: bold;
}

.card-title {
    color: var(--text-light);
    font-size: 0.9rem;
}

.card-change-up {
    color: #28a745;
}

.card-change-down {
    color: #dc3545;
}
</style>
""", unsafe_allow_html=True)

# ===== SIDEBAR =====
st.sidebar.title("Pivora CRM")
menu = st.sidebar.radio("Menu", ["Dashboard", "Deals", "Notes", "Reports"])

# ===== MAIN CONTENT =====
st.title("Dashboard")

# ====== CARDS ======
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="card">
        <div class="card-title">Leads</div>
        <div class="card-value">129</div>
        <div class="card-change-up">↑ 2% vs last week</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="card">
        <div class="card-title">CLV</div>
        <div class="card-value">14d</div>
        <div class="card-change-down">↓ 4% vs last week</div>
    </div>
    """, unsafe_allow_html=True)

# ====== DATA ======
file_path = 'TOPOLOGY SEPTEMBER_FOA - Update_2025.xlsb'
            sheet_name = 'FOA Active'
            df = pd.read_excel(file_path, sheet_name=sheet_name, engine="pyxlsb")
            df.columns = df.columns.str.strip()

            col_site = get_col(df, "New Site ID")
            col_dest = get_col(df, "New Destination", alt="New Destenation")
            col_fiber = get_col(df, "Fiber Type")
            col_site_name = get_col(df, "Site Name")
            col_host = get_col(df, "Host Name", alt="Hostname")
            col_flp = get_col(df, "FLP Vendor")
            col_flp_len = get_col(df, "FLP LENGTH")
            col_syskey = get_col(df, "System Key")
            col_dest_name = get_col(df, "Destination Name")
            col_ring = get_col(df, "Ring ID")
            col_member_ring = get_col(df, "Member Ring")

            required_cols = [col_site, col_dest, col_fiber, col_site_name, col_host, col_flp,
                             col_flp_len, col_syskey, col_dest_name, col_ring, col_member_ring]
            missing_cols = [c for c in required_cols if c is None]
            if missing_cols:
                st.error(f"Kolom berikut tidak ditemukan di file Excel: {missing_cols}")
                st.stop()

# ====== PLOTLY CHART ======
fig = go.Figure()

fig.add_trace(go.Bar(
    x=months,
    y=revenues,
    marker=dict(color="rgba(85,107,255,0.7)"),
))

fig.update_layout(
    title="Revenue ($32.209) – naik 22% vs bulan lalu",
    height=400,
    margin=dict(l=20, r=20, t=50, b=20)
)

# ====== SHOW CHART ======
st.plotly_chart(fig, use_container_width=True)
