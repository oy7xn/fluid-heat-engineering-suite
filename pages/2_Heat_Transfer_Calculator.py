"""
pages/2_Heat_Transfer_Calculator.py
=====================================
Module B of the capstone: Heat Transfer Calculator (5 marks).

Two calculators:
1. Steady-state 1-D conduction through a single-layer flat wall (Fourier's law).
2. Newton's Law of Cooling — time to cool an object from T0 to Ttarget in an
   ambient at Tinf, plus a live temperature-vs-time cooling curve.
"""

import numpy as np
import pandas as pd
import streamlit as st

from engineering import HeatTransfer

st.set_page_config(page_title="Heat Transfer Calculator", page_icon="🌡️", layout="wide")

st.title("🌡️ Heat Transfer Calculator")
st.caption("Module B — Steady-state conduction and Newton's Law of Cooling")

tab1, tab2 = st.tabs(["🧱 Conduction through a flat wall", "☕ Newton's Law of Cooling"])

# =======================================================================
# TAB 1 — Conduction
# =======================================================================
with tab1:
    st.subheader("Steady-state conduction (Fourier's Law)")
    st.write(
        "Computes the rate of heat flow through a single, uniform layer of "
        "material, e.g. heat loss through a tank wall or insulation layer: "
        "**q = k·A·(T_hot − T_cold) / L**"
    )

    col1, col2 = st.columns(2)
    with col1:
        k = st.number_input(
            "Thermal conductivity, k (W/m·K)", min_value=0.001, value=0.70, step=0.01,
            help="Material property — how easily heat conducts through it. "
                 "e.g. still air ≈ 0.026, brick ≈ 0.7, mild steel ≈ 50 W/m·K.",
        )
        area = st.number_input(
            "Wall area, A (m²)", min_value=0.001, value=10.0, step=0.5,
            help="Surface area of the wall, measured perpendicular to the direction of heat flow.",
        )
        thickness_mm = st.number_input(
            "Wall thickness, L (mm)", min_value=1.0, value=200.0, step=10.0,
            help="Distance the heat has to travel through the wall material.",
        )
    with col2:
        t_hot = st.number_input(
            "Hot-face temperature, T_hot (°C)", value=25.0, step=1.0,
            help="Temperature on the warmer side of the wall.",
        )
        t_cold = st.number_input(
            "Cold-face temperature, T_cold (°C)", value=5.0, step=1.0,
            help="Temperature on the cooler side of the wall.",
        )

    try:
        cond = HeatTransfer.conduction_flat_wall(
            k=k, area=area, thickness=thickness_mm / 1000.0, t_hot=t_hot, t_cold=t_cold
        )
        c1, c2 = st.columns(2)
        c1.metric("Heat transfer rate, q", f"{cond['heat_rate_w']:.2f} W")
        c2.metric("Heat flux, q\"", f"{cond['heat_flux_w_m2']:.2f} W/m²")

        with st.expander("Verification against an analytical solution"):
            st.markdown(
                """
                **Check case:** k = 0.7 W/m·K, A = 10 m², L = 0.2 m,
                T_hot = 25 °C, T_cold = 5 °C.

                q = k·A·ΔT / L = 0.7 × 10 × 20 / 0.2 = **700 W**, q" = **70 W/m²**

                This matches the app output exactly when the defaults above
                are used — confirming the analytical (Fourier's law) formula
                is implemented correctly.
                """
            )
    except ValueError as e:
        st.error(f"Invalid input: {e}")

# =======================================================================
# TAB 2 — Newton's Law of Cooling
# =======================================================================
with tab2:
    st.subheader("Newton's Law of Cooling")
    st.write(
        "Models how an object's temperature approaches the ambient "
        "temperature over time, assuming convective heat transfer and a "
        "uniform (lumped) object temperature: "
        "**T(t) = T∞ + (T₀ − T∞)·e^(−hAt / mc_p)**"
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        t0 = st.number_input(
            "Initial temperature, T₀ (°C)", value=90.0, step=1.0,
            help="Starting temperature of the object.",
        )
        t_inf = st.number_input(
            "Ambient temperature, T∞ (°C)", value=20.0, step=1.0,
            help="Temperature of the surrounding fluid (air/water) far from the object.",
        )
        t_target = st.number_input(
            "Target temperature (°C)", value=30.0, step=1.0,
            help="The temperature you want the object to reach. Must lie strictly "
                 "between T₀ and T∞.",
        )
    with col2:
        h = st.number_input(
            "Convective coefficient, h (W/m²·K)", min_value=0.1, value=10.0, step=0.5,
            help="How effectively the surrounding fluid carries heat away. "
                 "Still air ≈ 5–25, moving air ≈ 25–250, water ≈ 500–10,000 W/m²·K.",
        )
        area_c = st.number_input(
            "Surface area, A (m²)", min_value=0.001, value=0.5, step=0.05,
            help="Object surface area exposed to the ambient fluid.",
        )
    with col3:
        mass = st.number_input(
            "Mass, m (kg)", min_value=0.001, value=1.0, step=0.1,
            help="Mass of the cooling object.",
        )
        cp = st.number_input(
            "Specific heat, c_p (J/kg·K)", min_value=1.0, value=4180.0, step=10.0,
            help="Heat capacity of the object's material. Water ≈ 4180, steel ≈ 490 J/kg·K.",
        )

    try:
        t_needed = HeatTransfer.cooling_time_to_target(
            t0=t0, t_target=t_target, t_inf=t_inf, h=h, area=area_c, mass=mass, cp=cp
        )
        m1, m2 = st.columns(2)
        m1.metric("Time to reach target", f"{t_needed:,.1f} s")
        m2.metric("", f"{t_needed / 60:,.2f} min")

        with st.expander("Verification against an analytical solution"):
            st.markdown(
                """
                **Check case:** T₀ = 90 °C, T∞ = 20 °C, T_target = 30 °C,
                h = 10 W/m²·K, A = 0.5 m², m = 1 kg, c_p = 4180 J/kg·K.

                t = −(mc_p / hA)·ln[(T_target − T∞) / (T₀ − T∞)]
                  = −(4180 / 5)·ln(10 / 70) = **1626.8 s ≈ 27.11 min**

                Matches the app's default output exactly.
                """
            )

        st.subheader("Cooling curve")
        max_time_s = st.slider(
            "Plot time range (s)", min_value=10, max_value=int(max(t_needed * 3, 60)),
            value=int(max(t_needed * 1.5, 60)),
            help="How far along the time axis the cooling curve is plotted.",
        )
        t_arr = np.linspace(0, max_time_s, 100)
        temps = [
            HeatTransfer.cooling_temperature(t0, t_inf, h, area_c, mass, cp, float(t))
            for t in t_arr
        ]
        curve_df = pd.DataFrame({"time_s": t_arr, "temperature_C": temps})
        st.line_chart(curve_df.set_index("time_s")["temperature_C"])
        st.caption("Object temperature vs time — updates live as you change any input above.")

    except ValueError as e:
        st.error(f"Invalid input: {e}")
