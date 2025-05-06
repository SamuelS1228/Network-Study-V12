import streamlit as st
import pandas as pd

from optimization import optimize
from visualization import plot_network, summary

# ───────────────────────── Streamlit config ─────────────────────────
st.set_page_config(page_title="Warehouse Network Optimizer",
                   page_icon="🏭", layout="wide")
st.title("Warehouse Location & Cost Optimizer")
st.markdown("Upload a CSV with **Latitude**, **Longitude**, **DemandLbs** columns.")

uploaded = st.file_uploader("Upload store demand file", type=["csv"])

# ───────────────────────── Sidebar inputs ───────────────────────────
with st.sidebar:
    st.header("Cost Parameters")
    rate = st.number_input("Transportation cost ($ per lb‑mile)",
                           value=0.02, format="%.10f")
    fixed_cost = st.number_input("Fixed cost per warehouse ($/yr)",
                                 value=250_000.0, step=50_000.0, format="%.2f")
    sqft_per_lb = st.number_input("Warehouse sqft per lb",
                                  value=0.02, format="%.10f")
    cost_per_sqft = st.number_input("Variable cost ($ per sqft per yr)",
                                    value=6.0, format="%.10f")

    st.markdown("---")
    auto_k = st.checkbox("Optimize number of warehouses", value=True)
    if auto_k:
        k_min, k_max = st.slider("k range", 1, 10, (2, 5))
    else:
        k_fixed = st.number_input("Number of warehouses", 1, 10, 3, 1)

    # ─────────── Fixed‑center interface (up to 5) ───────────
    st.markdown("---")
    st.subheader("Fixed Warehouse Locations (optional)")
    fixed_centers = []
    for i in range(1, 6):
        with st.expander(f"Fixed Warehouse {i}", expanded=False):
            lat = st.number_input(f"Latitude {i}", value=0.0,
                                  key=f"lat{i}", format="%.6f")
            lon = st.number_input(f"Longitude {i}", value=0.0,
                                  key=f"lon{i}", format="%.6f")
            use = st.checkbox("Use this location", key=f"use{i}")
            if use:
                fixed_centers.append([lon, lat])

# ───────────────────────── Main logic ───────────────────────────────
if uploaded:
    df = pd.read_csv(uploaded)
    required = {"Latitude", "Longitude", "DemandLbs"}
    if not required.issubset(df.columns):
        st.error(f"CSV must contain columns: {', '.join(required)}")
        st.stop()

    if auto_k:
        result = optimize(df,
                          range(k_min, k_max + 1),
                          rate, sqft_per_lb, cost_per_sqft, fixed_cost,
                          fixed_centers=fixed_centers)
        st.success(f"Optimal k = {result['k']}")
    else:
        result = optimize(df,
                          [int(k_fixed)],
                          rate, sqft_per_lb, cost_per_sqft, fixed_cost,
                          fixed_centers=fixed_centers)

    # Visuals & summaries
    plot_network(result["assigned_df"], result["centers"])
    summary(result["assigned_df"],
            result["total_cost"],
            result["trans_cost"],
            result["wh_cost"],
            result["centers"],
            result["demand_per_wh"],
            sqft_per_lb)
