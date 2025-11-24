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
months = ['Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec','Jan','Feb']
revenues = [22000,20000,25000,18000,21000,15000,18200,14678,8000,7500,9000,6000]

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
