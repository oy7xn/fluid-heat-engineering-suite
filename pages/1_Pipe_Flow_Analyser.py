"""
pages/1_Pipe_Flow_Analyser.py
==============================
Module A of the capstone: Pipe Flow Analyser (5 marks).

Lets the user pick a fluid, define pipe geometry, and enter a flow rate.
Displays velocity, Reynolds number, friction factor and Darcy-Weisbach
pressure drop; plots pressure drop vs flow rate over a range; and lets
the user export the curve to CSV.
"""

import io

import numpy as np
import pandas as pd
import streamlit as st

from engineering import Fluid, Pipe

st.set_page_config(page_title="Pipe Flow Analyser", page_icon="🔧", layout="wide")

st.title("🔧 Pipe Flow Analyser")
st.caption("Module A — Darcy-Weisbach pressure drop for internal pipe flow")

# ---------------------------------------------------------------------
# Sidebar inputs
# ---------------------------------------------------------------------
st.sidebar.header("Fluid")

fluid_choice = st.sidebar.selectbox(
    "Fluid type",
    list(Fluid.PRESETS.keys()) + ["User-defined"],
    help="Pick a preset fluid, or choose User-defined to enter your own properties.",
)

try:
    if fluid_choice == "User-defined":
        density = st.sidebar.number_input(
            "Density, ρ (kg/m³)", min_value=0.001, value=1000.0, step=1.0,
            help="Mass per unit volume of the fluid.",
        )
        viscosity = st.sidebar.number_input(
            "Dynamic viscosity, μ (Pa·s)", min_value=1e-6, value=1.0e-3,
            step=1e-4, format="%.6f",
            help="Resistance of the fluid to shear/flow.",
        )
        fluid = Fluid("User-defined", density, viscosity)
    else:
        fluid = Fluid.from_preset(fluid_choice)
        st.sidebar.caption(
            f"ρ = {fluid.density:g} kg/m³  |  μ = {fluid.viscosity:.3e} Pa·s"
        )

    st.sidebar.header("Pipe geometry")
    diameter_mm = st.sidebar.number_input(
        "Internal diameter, D (mm)", min_value=1.0, value=50.0, step=1.0,
        help="Internal (bore) diameter of the pipe.",
    )
    length_m = st.sidebar.number_input(
        "Pipe length, L (m)", min_value=0.1, value=100.0, step=1.0,
        help="Total straight-line length of the pipe run.",
    )
    roughness_mm = st.sidebar.number_input(
        "Absolute roughness, ε (mm)", min_value=0.0, value=0.15, step=0.01,
        format="%.3f",
        help="Internal pipe-wall roughness (e.g. ~0.15 mm for commercial steel).",
    )

    st.sidebar.header("Flow rate")
    flow_rate_ls = st.sidebar.number_input(
        "Flow rate, Q (L/s)", min_value=0.0, value=10.0, step=0.5,
        help="Volumetric flow rate through the pipe.",
    )

    pipe = Pipe(diameter=diameter_mm / 1000.0, length=length_m, roughness=roughness_mm / 1000.0)
    flow_rate_m3s = flow_rate_ls / 1000.0

    # -------------------------------------------------------------
    # Results
    # -------------------------------------------------------------
    result = pipe.pressure_drop(flow_rate_m3s, fluid)

    st.subheader("Results")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Velocity", f"{result['velocity']:.3f} m/s")
    c2.metric("Reynolds number", f"{result['reynolds']:,.0f}")
    c3.metric("Friction factor, f", f"{result['friction_factor']:.4f}")
    c4.metric("Pressure drop", f"{result['pressure_drop_bar']:.4f} bar")

    flow_regime = "Laminar" if result["reynolds"] < 2300 else (
        "Transitional" if result["reynolds"] < 4000 else "Turbulent"
    )
    st.info(
        f"Flow regime: **{flow_regime}**  |  "
        f"ΔP = {result['pressure_drop_pa']:.1f} Pa "
        f"= {result['pressure_drop_bar']:.4f} bar "
        f"= {result['pressure_drop_psi']:.3f} psi"
    )

    with st.expander("Verification against a hand-calculated example"):
        st.markdown(
            """
            **Check case:** Water (ρ = 998 kg/m³, μ = 1.002×10⁻³ Pa·s) flowing
            at Q = 0.01 m³/s through a pipe D = 0.05 m, L = 100 m, ε = 0.15 mm.

            - Area = πD²/4 = 1.963×10⁻³ m² → v = Q/A = **5.093 m/s**
            - Re = ρvD/μ = **253,631** → turbulent, so use Swamee-Jain for f
            - f (Swamee-Jain) = **0.0269**
            - ΔP = f·(L/D)·(ρv²/2) = **6.95 bar**

            These figures were computed independently by hand (Darcy-Weisbach
            + Swamee-Jain formulas) and matched the app's output to 3
            significant figures, confirming the calculation is correct.
            Set the sidebar to this exact case (Water, D = 50 mm, L = 100 m,
            ε = 0.15 mm, Q = 10 L/s) to reproduce it.
            """
        )

    # -------------------------------------------------------------
    # Interactive plot: pressure drop vs flow rate
    # -------------------------------------------------------------
    st.subheader("Pressure drop vs flow rate")

    max_q_ls = st.slider(
        "Flow-rate range to plot (up to, L/s)",
        min_value=1.0, max_value=max(50.0, flow_rate_ls * 3), value=max(flow_rate_ls * 2, 5.0),
        help="Sets the upper end of the flow-rate axis for the curve below.",
    )

    q_range_ls = np.linspace(0.01, max_q_ls, 60)
    rows = []
    for q_ls in q_range_ls:
        r = pipe.pressure_drop(q_ls / 1000.0, fluid)
        rows.append({
            "flow_rate_L_s": q_ls,
            "velocity_m_s": r["velocity"],
            "reynolds": r["reynolds"],
            "friction_factor": r["friction_factor"],
            "pressure_drop_bar": r["pressure_drop_bar"],
            "pressure_drop_pa": r["pressure_drop_pa"],
        })
    curve_df = pd.DataFrame(rows)

    st.line_chart(curve_df.set_index("flow_rate_L_s")["pressure_drop_bar"])
    st.caption("Pressure drop (bar) vs flow rate (L/s) — recomputed live as you change any sidebar input.")

    # -------------------------------------------------------------
    # CSV export
    # -------------------------------------------------------------
    csv_buffer = io.StringIO()
    curve_df.to_csv(csv_buffer, index=False)
    st.download_button(
        label="⬇️ Export curve data to CSV",
        data=csv_buffer.getvalue(),
        file_name="pipe_flow_pressure_drop_curve.csv",
        mime="text/csv",
    )

except ValueError as e:
    st.error(f"Invalid input: {e}")
