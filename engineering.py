"""
engineering.py
================
Core engineering classes for the Fluid Flow & Heat Transfer Engineering Suite.

This module contains all the object-oriented "physics" used by the Streamlit
pages in pages/. Keeping the calculations here (separate from the UI code)
means the same, tested logic backs every page, and the classes can be
unit-tested or reused on their own.

Classes
-------
Fluid          Represents a flowing fluid (density, viscosity) with presets
               for water, air and crude oil.
Pipe           Represents a circular pipe and computes flow hydraulics
               (velocity, Reynolds number, friction factor, pressure drop).
HeatTransfer   Static/class methods for steady-state conduction (Fourier's
               law) and transient convective cooling (Newton's Law of
               Cooling).
"""

import math


# ---------------------------------------------------------------------------
# Fluid
# ---------------------------------------------------------------------------
class Fluid:
    """Represents a fluid by its density and dynamic viscosity.

    Attributes:
        name (str): Descriptive name of the fluid.
        density (float): Fluid density, rho, in kg/m^3.
        viscosity (float): Dynamic viscosity, mu, in Pa.s (kg/m.s).
    """

    # Common engineering fluids at approximately room conditions (20 C, 1 atm).
    PRESETS = {
        "Water (20 C)": {"density": 998.0, "viscosity": 1.002e-3},
        "Air (20 C, 1 atm)": {"density": 1.204, "viscosity": 1.825e-5},
        "Crude Oil (medium, 20 C)": {"density": 870.0, "viscosity": 1.0e-2},
    }

    def __init__(self, name: str, density: float, viscosity: float):
        """Create a Fluid.

        Args:
            name: Descriptive label for the fluid.
            density: Density in kg/m^3. Must be positive.
            viscosity: Dynamic viscosity in Pa.s. Must be positive.

        Raises:
            ValueError: If density or viscosity is not a positive number.
        """
        if density is None or density <= 0:
            raise ValueError("Fluid density must be a positive number (kg/m^3).")
        if viscosity is None or viscosity <= 0:
            raise ValueError("Fluid viscosity must be a positive number (Pa.s).")
        self.name = name
        self.density = float(density)
        self.viscosity = float(viscosity)

    @classmethod
    def from_preset(cls, preset_name: str) -> "Fluid":
        """Build a Fluid from one of the built-in PRESETS.

        Args:
            preset_name: Key into Fluid.PRESETS (e.g. "Water (20 C)").

        Returns:
            A Fluid instance with the preset's properties.

        Raises:
            ValueError: If preset_name is not a recognised preset.
        """
        if preset_name not in cls.PRESETS:
            raise ValueError(f"Unknown fluid preset: {preset_name}")
        props = cls.PRESETS[preset_name]
        return cls(preset_name, props["density"], props["viscosity"])

    def __repr__(self) -> str:
        return f"Fluid(name={self.name!r}, rho={self.density} kg/m^3, mu={self.viscosity} Pa.s)"


# ---------------------------------------------------------------------------
# Pipe
# ---------------------------------------------------------------------------
class Pipe:
    """Represents a straight, circular pipe and computes internal-flow hydraulics.

    All calculations use SI units internally (metres, m^3/s, Pa).

    Attributes:
        diameter (float): Internal diameter, D, in metres.
        length (float): Pipe length, L, in metres.
        roughness (float): Absolute (internal) roughness, e, in metres.
    """

    def __init__(self, diameter: float, length: float, roughness: float = 0.0):
        """Create a Pipe.

        Args:
            diameter: Internal diameter in metres. Must be positive.
            length: Pipe length in metres. Must be positive.
            roughness: Absolute roughness in metres. Must be >= 0.

        Raises:
            ValueError: If diameter/length are not positive, or roughness < 0.
        """
        if diameter is None or diameter <= 0:
            raise ValueError("Pipe diameter must be a positive number (m).")
        if length is None or length <= 0:
            raise ValueError("Pipe length must be a positive number (m).")
        if roughness is None or roughness < 0:
            raise ValueError("Pipe roughness cannot be negative (m).")
        self.diameter = float(diameter)
        self.length = float(length)
        self.roughness = float(roughness)

    @property
    def area(self) -> float:
        """Cross-sectional flow area in m^2 (pi * D^2 / 4)."""
        return math.pi * self.diameter ** 2 / 4.0

    def velocity(self, flow_rate: float) -> float:
        """Mean flow velocity for a given volumetric flow rate.

        Args:
            flow_rate: Volumetric flow rate, Q, in m^3/s. Must be >= 0.

        Returns:
            Mean velocity in m/s.

        Raises:
            ValueError: If flow_rate is negative.
        """
        if flow_rate < 0:
            raise ValueError("Flow rate cannot be negative.")
        return flow_rate / self.area

    def reynolds_number(self, flow_rate: float, fluid: Fluid) -> float:
        """Reynolds number, Re = rho * v * D / mu.

        Args:
            flow_rate: Volumetric flow rate in m^3/s.
            fluid: The Fluid flowing through the pipe.

        Returns:
            Dimensionless Reynolds number.
        """
        v = self.velocity(flow_rate)
        return fluid.density * v * self.diameter / fluid.viscosity

    def friction_factor(self, reynolds: float) -> float:
        """Darcy friction factor, f.

        Laminar flow (Re < 2300): f = 64 / Re (exact).
        Turbulent flow (Re >= 2300): Swamee-Jain explicit approximation of
        the Colebrook equation, valid for 5000 < Re < 1e8 and
        1e-6 < relative roughness < 1e-2 (used here as a general-purpose
        approximation across the turbulent range).

        Args:
            reynolds: Reynolds number (dimensionless).

        Returns:
            Darcy (Moody) friction factor, dimensionless.

        Raises:
            ValueError: If reynolds is not positive.
        """
        if reynolds <= 0:
            raise ValueError("Reynolds number must be positive to compute a friction factor.")
        if reynolds < 2300:
            return 64.0 / reynolds
        rel_rough = self.roughness / self.diameter
        denom = math.log10((rel_rough / 3.7) + (5.74 / reynolds ** 0.9))
        return 0.25 / denom ** 2

    def pressure_drop(self, flow_rate: float, fluid: Fluid) -> dict:
        """Full Darcy-Weisbach pressure-drop calculation.

        dP = f * (L / D) * (rho * v^2 / 2)

        Args:
            flow_rate: Volumetric flow rate in m^3/s. Must be >= 0.
            fluid: The Fluid flowing through the pipe.

        Returns:
            A dict with keys: velocity (m/s), reynolds (-), friction_factor (-),
            pressure_drop_pa (Pa), pressure_drop_bar (bar), pressure_drop_psi (psi).
        """
        v = self.velocity(flow_rate)
        if v == 0:
            return {
                "velocity": 0.0, "reynolds": 0.0, "friction_factor": 0.0,
                "pressure_drop_pa": 0.0, "pressure_drop_bar": 0.0, "pressure_drop_psi": 0.0,
            }
        re = self.reynolds_number(flow_rate, fluid)
        f = self.friction_factor(re)
        dp_pa = f * (self.length / self.diameter) * (fluid.density * v ** 2 / 2.0)
        return {
            "velocity": v,
            "reynolds": re,
            "friction_factor": f,
            "pressure_drop_pa": dp_pa,
            "pressure_drop_bar": dp_pa / 1e5,
            "pressure_drop_psi": dp_pa / 6894.76,
        }

    def __repr__(self) -> str:
        return f"Pipe(D={self.diameter} m, L={self.length} m, roughness={self.roughness} m)"


# ---------------------------------------------------------------------------
# HeatTransfer
# ---------------------------------------------------------------------------
class HeatTransfer:
    """Groups the two heat-transfer calculations used in Module B.

    Implemented as static/class methods (no instance state needed) so the
    class can be called directly, e.g. HeatTransfer.conduction(...).
    """

    @staticmethod
    def conduction_flat_wall(k: float, area: float, thickness: float,
                              t_hot: float, t_cold: float) -> dict:
        """Steady-state 1-D conduction through a single-layer flat wall (Fourier's law).

        q = k * A * (T_hot - T_cold) / L

        Args:
            k: Thermal conductivity of the wall material, W/(m.K). Must be > 0.
            area: Cross-sectional area normal to heat flow, m^2. Must be > 0.
            thickness: Wall thickness, L, in m. Must be > 0.
            t_hot: Hot-face temperature, deg C or K (consistent with t_cold).
            t_cold: Cold-face temperature, same units as t_hot.

        Returns:
            A dict with keys: heat_rate_w (W) and heat_flux_w_m2 (W/m^2).

        Raises:
            ValueError: If k, area or thickness are not positive.
        """
        if k <= 0:
            raise ValueError("Thermal conductivity k must be positive (W/m.K).")
        if area <= 0:
            raise ValueError("Area must be positive (m^2).")
        if thickness <= 0:
            raise ValueError("Wall thickness must be positive (m).")
        heat_flux = k * (t_hot - t_cold) / thickness
        heat_rate = heat_flux * area
        return {"heat_rate_w": heat_rate, "heat_flux_w_m2": heat_flux}

    @staticmethod
    def cooling_temperature(t0: float, t_inf: float, h: float, area: float,
                             mass: float, cp: float, time_s: float) -> float:
        """Temperature at time t under Newton's Law of Cooling (lumped capacitance).

        T(t) = T_inf + (T0 - T_inf) * exp(-h * A * t / (m * cp))

        Args:
            t0: Initial object temperature.
            t_inf: Ambient (surrounding fluid) temperature, same units as t0.
            h: Convective heat-transfer coefficient, W/(m^2.K). Must be > 0.
            area: Surface area exposed to the fluid, m^2. Must be > 0.
            mass: Mass of the object, kg. Must be > 0.
            cp: Specific heat capacity of the object, J/(kg.K). Must be > 0.
            time_s: Elapsed time, seconds. Must be >= 0.

        Returns:
            Object temperature at time_s, in the same units as t0/t_inf.

        Raises:
            ValueError: If h, area, mass or cp are not positive, or time_s < 0.
        """
        if h <= 0 or area <= 0 or mass <= 0 or cp <= 0:
            raise ValueError("h, area, mass and cp must all be positive.")
        if time_s < 0:
            raise ValueError("time_s cannot be negative.")
        k = h * area / (mass * cp)
        return t_inf + (t0 - t_inf) * math.exp(-k * time_s)

    @staticmethod
    def cooling_time_to_target(t0: float, t_target: float, t_inf: float,
                                h: float, area: float, mass: float, cp: float) -> float:
        """Time required to cool (or heat) from T0 to T_target in ambient T_inf.

        Rearranges Newton's Law of Cooling:
            t = -(m * cp) / (h * A) * ln[(T_target - T_inf) / (T0 - T_inf)]

        Args:
            t0: Initial object temperature.
            t_target: Target temperature to reach (must lie strictly between
                t0 and t_inf, exclusive of t_inf, for a finite time to exist).
            t_inf: Ambient temperature.
            h: Convective heat-transfer coefficient, W/(m^2.K). Must be > 0.
            area: Surface area, m^2. Must be > 0.
            mass: Mass, kg. Must be > 0.
            cp: Specific heat capacity, J/(kg.K). Must be > 0.

        Returns:
            Time in seconds to reach t_target.

        Raises:
            ValueError: If inputs are non-physical, or t_target is not
                reachable (it is beyond t_inf, or equal to t0/t_inf).
        """
        if h <= 0 or area <= 0 or mass <= 0 or cp <= 0:
            raise ValueError("h, area, mass and cp must all be positive.")
        if t0 == t_inf:
            raise ValueError("Initial temperature equals ambient temperature; no cooling occurs.")
        # T_target must be strictly between T_inf and T0 for a finite, positive time.
        lower, upper = sorted([t_inf, t0])
        if not (lower < t_target < upper):
            raise ValueError(
                "Target temperature must lie strictly between the ambient and "
                "initial temperatures for a finite cooling time to exist."
            )
        k = h * area / (mass * cp)
        ratio = (t_target - t_inf) / (t0 - t_inf)
        return -math.log(ratio) / k

    def __repr__(self) -> str:  # pragma: no cover - simple utility class
        return "HeatTransfer(static utility class)"
