# Fluid Flow & Heat Transfer Engineering Suite

**PE 262 — Computer Programming for Petroleum Engineers, KNUST**
Capstone Project — Full Engineering Application

A multi-page Streamlit application bundling three engineering calculators
that a petroleum/process engineer uses routinely: pipe flow hydraulics,
heat transfer (conduction and transient cooling), and a rock/fluid lab-data
dashboard. All physics/engineering logic lives in `engineering.py` as
object-oriented classes (`Fluid`, `Pipe`, `HeatTransfer`), imported and
reused by every page rather than re-implemented in the UI code.

**Live app:** *[ADD YOUR STREAMLIT COMMUNITY CLOUD URL HERE AFTER DEPLOYING]*

---

## Modules

| Module | File | Description |
|---|---|---|
| A — Pipe Flow Analyser | `pages/1_Pipe_Flow_Analyser.py` | Velocity, Reynolds number, Darcy friction factor and Darcy-Weisbach pressure drop for water/air/crude oil/custom fluid; interactive pressure-drop-vs-flow-rate curve; CSV export. |
| B — Heat Transfer Calculator | `pages/2_Heat_Transfer_Calculator.py` | Steady-state conduction through a flat wall (Fourier's law) and Newton's Law of Cooling (time to target temperature + live cooling curve). |
| C — Rock & Fluid Data Dashboard | `pages/3_Rock_Fluid_Dashboard.py` | Upload a CSV of core/fluid data, view summary stats, filter by porosity, view a histogram and a porosity-permeability crossplot, download filtered data. |

## Project structure

```
engineering-suite/
├── app.py                          # Home page (Streamlit entry point)
├── engineering.py                  # Fluid, Pipe, HeatTransfer classes (OOP core)
├── pages/
│   ├── 1_Pipe_Flow_Analyser.py
│   ├── 2_Heat_Transfer_Calculator.py
│   └── 3_Rock_Fluid_Dashboard.py
├── sample_rock_data.csv            # Sample dataset for testing Module C
├── requirements.txt
└── README.md
```

## Running locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploying to Streamlit Community Cloud

1. Push this repository to a **public** GitHub repo.
2. Go to [share.streamlit.io](https://share.streamlit.io), sign in with GitHub.
3. Click **New app**, select this repository, branch `main`, and set the
   main file path to `app.py`.
4. Click **Deploy**. Once live, copy the URL and paste it into this README
   (above) and into your developer report.

## Verification

Every calculation was checked against an independent hand calculation or
known analytical solution before being trusted (see the "Verification"
expanders inside each app page for the worked check case and result):

- **Pipe flow:** Darcy-Weisbach + Swamee-Jain, checked against a
  hand-worked example (water, D = 50 mm, L = 100 m, Q = 10 L/s → ΔP ≈ 6.95 bar).
- **Conduction:** Fourier's law, checked against a direct analytical
  calculation (k = 0.7 W/m·K, A = 10 m², L = 200 mm → q = 700 W).
- **Newton's cooling:** rearranged analytical solution, checked against a
  hand-worked example (T₀ = 90 °C → 30 °C in T∞ = 20 °C → t ≈ 1626.8 s).

## AI usage documentation

AI assistance (Claude) was used to help draft and structure the code for
this project. All generated code was read, tested, and understood before
submission; results below reflect what was checked and what had to be
fixed.

1. **Prompt:** "Write a Python class-based pipe-flow calculator using the
   Darcy-Weisbach equation with a Swamee-Jain friction factor, including
   input validation and docstrings."
   **Verified:** Recomputed the pressure drop by hand for a fixed test
   case (water, D = 50 mm, L = 100 m, Q = 10 L/s) and confirmed the app's
   output matched to 3 significant figures.
   **Corrected:** The first draft used the laminar friction factor formula
   (64/Re) for all Reynolds numbers. This was wrong for turbulent flow —
   fixed by branching on Re < 2300 (laminar) vs Re ≥ 2300 (Swamee-Jain).

2. **Prompt:** "Write a Newton's Law of Cooling function that solves for
   the time needed to reach a target temperature, with error handling."
   **Verified:** Solved the rearranged cooling equation by hand for
   T₀ = 90 °C, T∞ = 20 °C, T_target = 30 °C and matched the app's output
   (≈ 1626.8 s / 27.1 min) exactly.
   **Corrected:** The first draft did not check whether T_target was
   physically reachable (e.g. beyond T∞, or equal to T0/T∞), which caused
   a `math domain error` from `log()` of a negative/zero ratio. Added an
   explicit range check that raises a clear `ValueError` instead of
   crashing.

3. **Prompt:** "Build a Streamlit page that lets a user upload a CSV of
   rock data, filter by a porosity threshold, and plot a
   porosity-permeability crossplot, without assuming exact column names."
   **Verified:** Tested with the included `sample_rock_data.csv` (60
   synthetic samples) and confirmed the filter, histogram, crossplot and
   CSV download all update correctly as the porosity threshold slider moves.
   **Corrected:** The first draft assumed porosity was always stored as a
   fraction (0–1). Real lab CSVs sometimes report porosity as a percentage
   (0–100), which broke the filter slider's range. Added a check that
   detects which convention the uploaded file uses and adjusts the slider
   range accordingly.

## Author

Petroleum Engineering student, KNUST — PE 262, 2026.
