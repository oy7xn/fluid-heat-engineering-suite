"""
app.py
======
Entry point for the Fluid Flow & Heat Transfer Engineering Suite.

This is a multi-page Streamlit app. Streamlit automatically turns every
file in pages/ into a page and lists them in the sidebar, so this file
only needs to render the home / landing screen.

Run locally with:
    streamlit run app.py
"""

import streamlit as st

st.set_page_config(
    page_title="Fluid Flow & Heat Transfer Engineering Suite",
    page_icon="🛢️",
    layout="wide",
)


def main() -> None:
    """Render the landing page of the engineering suite."""
    st.title("🛢️ Fluid Flow & Heat Transfer Engineering Suite")
    st.caption("PE 262 Capstone Project — KNUST Petroleum Engineering")

    st.markdown(
        """
        Welcome. This application bundles three engineering calculators that a
        petroleum/process engineer uses on a routine basis. Use the sidebar to
        open a module.
        """
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("🔧 Pipe Flow Analyser")
        st.write(
            "Calculate velocity, Reynolds number, friction factor and "
            "Darcy-Weisbach pressure drop for flow of water, air, crude "
            "oil, or a custom fluid through a pipe. Includes an "
            "interactive pressure-drop-vs-flow-rate curve and CSV export."
        )

    with col2:
        st.subheader("🌡️ Heat Transfer Calculator")
        st.write(
            "Compute steady-state conduction through a flat wall "
            "(Fourier's law) and the time needed to cool an object under "
            "Newton's Law of Cooling, with a live cooling-curve plot."
        )

    with col3:
        st.subheader("📊 Rock & Fluid Data Dashboard")
        st.write(
            "Upload a CSV of core/rock or fluid lab data, view summary "
            "statistics, filter by porosity, and generate a porosity "
            "histogram and a porosity-permeability crossplot."
        )

    st.divider()
    st.markdown(
        """
        **About this app**
        Built for the PE 262 (Computer Programming for Petroleum Engineers)
        capstone. All engineering calculations live in `engineering.py`
        (object-oriented `Fluid`, `Pipe`, and `HeatTransfer` classes) and are
        imported by each page — the UI code never repeats a formula.
        """
    )


if __name__ == "__main__":
    main()
