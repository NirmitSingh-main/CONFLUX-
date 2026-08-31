# CONFLUX Physics & Orbital Mechanics

CONFLUX implements rigorous aerospace physics models to ensure that telemetry synthesis and mission risk assessments are grounded in real-world astrodynamics and thermodynamics.

---

## 1. Orbital Conjunction & Relative Motion

- **State Vectors**:
  Each orbital object is represented by:
  $$\mathbf{r} = (x, y, z) \quad [\text{km}], \quad \mathbf{v} = (v_x, v_y, v_z) \quad [\text{km/s}]$$
- **Relative Position & Velocity**:
  $$\Delta \mathbf{r} = \mathbf{r}_2 - \mathbf{r}_1, \quad \Delta \mathbf{v} = \mathbf{v}_2 - \mathbf{v}_1$$
- **Relative Speed**:
  $$v_{\text{rel}} = \|\Delta \mathbf{v}\| = \sqrt{\Delta v_x^2 + \Delta v_y^2 + \Delta v_z^2}$$
- **Time to Closest Approach (TCA)**:
  For rectilinear relative motion:
  $$t_{\text{TCA}} = -\frac{\Delta \mathbf{r} \cdot \Delta \mathbf{v}}{\|\Delta \mathbf{v}\|^2}$$
  - If $t_{\text{TCA}} \le 0$, the objects are diverging (past closest approach).
  - If $t_{\text{TCA}} > 0$, the objects are converging towards a conjunction at $t_{\text{TCA}}$.
- **Miss Distance**:
  $$d_{\text{miss}} = \|\Delta \mathbf{r} + \Delta \mathbf{v} \cdot t_{\text{TCA}}\|$$
- **Collision Risk Assessment**:
  - If $d_{\text{miss}} \le d_{\text{safety}}$, a collision risk alert (`CRITICAL` or `WARNING`) is triggered.

---

## 2. Thermal Radiation & Stefan-Boltzmann Law

- **Radiative Heat Transfer**:
  Emitted thermal radiation power is governed by the Stefan-Boltzmann law:
  $$P = \varepsilon \sigma A T^4$$
  Where:
  - $\varepsilon$: Surface emissivity ($0 \le \varepsilon \le 1$)
  - $\sigma$: Stefan-Boltzmann constant ($5.670374419 \times 10^{-8} \ \text{W} \cdot \text{m}^{-2} \cdot \text{K}^{-4}$)
  - $A$: Radiating surface area in $\text{m}^2$
  - $T$: Absolute temperature in Kelvin ($T_{\text{K}} = T_{^\circ\text{C}} + 273.15$)

---

## 3. Atmospheric Drag

- **Drag Acceleration**:
  $$a_{\text{drag}} = -\frac{1}{2} \rho \left(\frac{C_d A}{m}\right) v_{\text{rel}}^2$$
  Where $\rho$ is atmospheric density, $C_d$ is the drag coefficient, $A$ is the cross-sectional area, and $m$ is spacecraft mass.
