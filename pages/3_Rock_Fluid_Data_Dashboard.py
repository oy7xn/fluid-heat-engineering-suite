"""
pages/3_Rock_Fluid_Dashboard.py
=================================
Module C of the capstone: Rock & Fluid Data Dashboard (5 marks).

Lets the user upload a CSV of rock/fluid lab data, view summary statistics,
filter by a porosity threshold, view a porosity histogram and a
porosity-permeability crossplot, and download the filtered data as CSV.

Expected (flexible) columns: a porosity column and, optionally, a
permeability column. Column names are auto-detected by keyword so the
app works with slightly different header naming conventions.
"""

import io

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Rock & Fluid Data Dashboard", page_icon="📊", layout="wide")

st.title("📊 Rock & Fluid Data Dashboard")
st.caption("Module C — Upload, explore, filter and export core/fluid lab data")


def find_column(df: pd.DataFrame, keywords: list) -> str | None:
    """Find the first column whose name contains any of the given keywords.

    Args:
        df: The DataFrame to search.
        keywords: Lowercase keywords to look for within column names.

    Returns:
        The matching column name, or None if no column matches.
    """
    for col in df.columns:
        col_lower = str(col).lower()
        if any(kw in col_lower for kw in keywords):
            return col
    return None


uploaded_file = st.file_uploader(
    "Upload a CSV of rock or fluid data",
    type=["csv"],
    help="Needs at least a porosity column. A permeability column enables the crossplot.",
)

st.caption(
    "No file yet? A sample dataset (`sample_rock_data.csv`) is included in this "
    "repository for testing — download it from GitHub and upload it here."
)

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        if df.empty:
            st.error("The uploaded CSV has no rows.")
            st.stop()

        st.subheader("Data preview")
        st.dataframe(df.head(10), use_container_width=True)

        st.subheader("Summary statistics")
        st.dataframe(df.describe(), use_container_width=True)

        poro_col = find_column(df, ["poro"])
        perm_col = find_column(df, ["perm"])

        if poro_col is None:
            st.warning(
                "No column with 'poro' in its name was found, so filtering and "
                "the histogram cannot be generated. Rename your porosity column "
                "to include 'porosity', e.g. 'porosity_frac'."
            )
        else:
            # Porosity may be stored as a fraction (0-0.35) or a percentage (0-35).
            poro_series = pd.to_numeric(df[poro_col], errors="coerce")
            is_percent = poro_series.max() > 1.5
            poro_pct = poro_series * 100 if not is_percent else poro_series

            st.subheader("Filter by porosity")
            min_p, max_p = float(poro_pct.min()), float(poro_pct.max())
            threshold = st.slider(
                "Show only samples where porosity > X%",
                min_value=round(min_p, 1), max_value=round(max_p, 1),
                value=round(min_p, 1),
                help="Drag to filter out low-porosity samples.",
            )
            filtered = df[poro_pct > threshold].copy()
            st.write(f"Showing **{len(filtered)}** of **{len(df)}** samples with porosity > {threshold}%.")
            st.dataframe(filtered, use_container_width=True)

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Porosity histogram**")
                st.bar_chart(
                    pd.cut(poro_pct[poro_pct > threshold], bins=10).value_counts().sort_index().rename_axis(
                        "porosity_%_bin").reset_index(name="count").set_index("porosity_%_bin")
                )
            with col2:
                if perm_col is not None:
                    st.markdown("**Porosity-permeability crossplot**")
                    plot_df = filtered[[poro_col, perm_col]].dropna().rename(
                        columns={poro_col: "porosity", perm_col: "permeability"}
                    )
                    st.scatter_chart(plot_df, x="porosity", y="permeability")
                    st.caption(
                        "Tip: permeability commonly spans orders of magnitude; "
                        "consider a log scale in your own analysis if the trend "
                        "looks compressed."
                    )
                else:
                    st.info(
                        "No column with 'perm' in its name was found, so the "
                        "porosity-permeability crossplot is unavailable for this file."
                    )

            csv_buffer = io.StringIO()
            filtered.to_csv(csv_buffer, index=False)
            st.download_button(
                label="⬇️ Download filtered data as CSV",
                data=csv_buffer.getvalue(),
                file_name="filtered_rock_data.csv",
                mime="text/csv",
            )

    except pd.errors.ParserError:
        st.error("Could not parse this file as a CSV. Please check the file format.")
    except Exception as e:  # noqa: BLE001 - surface any unexpected error to the user, not a crash
        st.error(f"Something went wrong while processing this file: {e}")
else:
    st.info("Upload a CSV file above to get started.")
