# CONFLUX Intelligence & Machine Learning Architecture

CONFLUX uses specialized, localized machine learning models and thresholding detectors to evaluate spacecraft telemetry, imagery, optical wavefronts, and space-weather data in real time.

---

## 1. Subsystem Telemetry Isolation Model

- **Model Type**: Isolation Forest (`telemetry_isolation_forest.joblib`).
- **Input Features (6-Dimensional)**:
  1. `temperature` (°C)
  2. `voltage` (V)
  3. `current` (A)
  4. `battery` (%)
  5. `pressure` (kPa)
  6. `vibration` (g)
- **Anomaly Detection Logic**:
  - Predicts `+1` for nominal operating envelope and `-1` for anomaly.
  - Generates continuous `decision_value` representing the distance to the separating hyperplane.
  - When an anomaly is detected, an `AnomalyEvent` of type `TELEMETRY_ANOMALY` is persisted to SQLite.

---

## 2. Radiometric Thermal Hotspot Detector

- **Algorithm**: Adaptive statistical intensity thresholding.
- **Input**: Radiometric infrared 2D matrix (PNG, JPG, TIFF).
- **Processing**:
  1. Computes mean intensity ($\mu$) and standard deviation ($\sigma$).
  2. Calculates hotspot threshold: $T = \mu + k \cdot \sigma$ (default $k = 2.5$).
  3. Detects pixels exceeding threshold $T$ and identifies maximum pixel intensity coordinate $(x, y)$.
  4. Computes hotspot ratio: $\text{ratio} = \frac{\text{hotspot\_pixels}}{\text{total\_pixels}}$.
  5. Flags thermal anomaly if $\text{ratio} > 0.01$ (1%).

---

## 3. Optical Wavefront Aberration & Wavelet Detector

- **Model**: Trained Wavefront Detector (`wavefront_detector.pkl`).
- **Feature Vector**:
  1. `wavefront_rms_um`
  2. `tip_error_um`
  3. `tilt_error_um`
  4. `defocus_um`
  5. `astigmatism_um`
  6. `coma_um`
- **Signal Processing**:
  - Computes Z-scores against diffraction-limited baseline distributions.
  - Evaluates multi-level 1D discrete wavelet transform energy ratio ($E_{\text{wavelet}} / E_{\text{baseline}}$).
  - Flags optical aberrations when anomaly score or wavelet energy exceeds safety thresholds.

---

## 4. Space Weather Environmental Analyzer

- **Features**:
  - Solar Activity ($S$, solar flux units / index).
  - Ionizing Radiation Level ($R$, flux index).
  - Geomagnetic Activity ($K_p$, planetary index).
- **Trained Thresholds**:
  - Solar Activity Threshold: $492.545$
  - Radiation Threshold: $7.749$
  - Geomagnetic Threshold: $3.565$
- **Classification**:
  - Classifies events into `ELEVATED_SOLAR_ACTIVITY`, `ELEVATED_RADIATION`, and `ELEVATED_GEOMAGNETIC_ACTIVITY`.
  - Flags environmental anomaly when any measurement breaches threshold.

---

## 5. Multimodal Fusion & Consensus Engine

- **Input**: Status vectors from all 5 modalities (Telemetry, Thermal, Wavelet, Orbital, Space Weather).
- **Consensus Metrics**:
  - `anomaly_count`: Total number of anomalous channels (0 to 5).
  - `multi_modal_agreement`: Boolean flag set to `True` when cross-modal consensus indicates correlated mission degradation.
  - `anomalous_modalities` & `normal_modalities`: Partitioned lists of active subsystems.
- **Persistence**: Results are stored in the `fusion_events` table for audit and operator review.
