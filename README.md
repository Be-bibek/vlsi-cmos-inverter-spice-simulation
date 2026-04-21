# CMOS Inverter Design & Simulation — 180nm Technology Node

A complete SPICE simulation of a static CMOS inverter using a 180nm BSIM3v3
technology model.  The project includes:

- **SPICE netlist** with DC and transient analyses
- **180nm CMOS BSIM3v3 model** file (NMOS + PMOS)
- **Shell run-script** to launch ngspice / HSPICE / Spectre
- **Python post-processor** to parse results and produce publication-quality plots

---

## Circuit Overview

```
           VDD (1.8 V)
              │
         ┌────┴────┐
    vin ─┤  PMOS   │  W/L = 2.0 µm / 180 nm
         │ (Mp)    │
         └────┬────┘
              │──── vout ──── CL (40 fF)
         ┌────┴────┐
    vin ─┤  NMOS   │  W/L = 1.0 µm / 180 nm
         │ (Mn)    │
         └────┬────┘
             GND
```

| Parameter         | NMOS             | PMOS             |
|-------------------|------------------|------------------|
| Channel length    | 180 nm           | 180 nm           |
| Channel width     | 1.0 µm           | 2.0 µm           |
| Threshold voltage | +0.50 V          | −0.50 V          |
| Mobility (µ₀)     | 270 cm²/V·s      | 95 cm²/V·s       |
| Gate oxide (Tox)  | 4 nm             | 4 nm             |
| Supply (VDD)      | 1.8 V            | 1.8 V            |

> **W/L ratio for PMOS = 2×NMOS** because hole mobility is ~2.8× lower than
> electron mobility, ensuring balanced rise/fall times and a switching
> threshold close to VDD/2 ≈ 0.9 V.

---

## Repository Structure

```
.
├── cmos_inverter.sp     # SPICE netlist (DC + Transient + .MEAS)
├── 180nm_models.lib     # BSIM3v3 NMOS & PMOS models (180nm)
├── run_simulation.sh    # Simulation launcher (ngspice/hspice/spectre)
├── plot_results.py      # Python post-processor & plotter
└── README.md
```

---

## Quick Start

### 1 — Install ngspice

```bash
# Ubuntu / Debian
sudo apt-get install ngspice

# Fedora / RHEL
sudo dnf install ngspice

# macOS (Homebrew)
brew install ngspice
```

### 2 — Run the simulation

```bash
chmod +x run_simulation.sh
./run_simulation.sh           # auto-detects ngspice/hspice/spectre
# or explicitly:
./run_simulation.sh ngspice
```

Simulation output is written to `simulation_output/`.

### 3 — Interactive ngspice session

```bash
ngspice cmos_inverter.sp
```

Inside the ngspice prompt:

```
ngspice> plot v(vout_dc) vs v(vin_dc)    # VTC
ngspice> plot v(vin_tr) v(vout_tr)       # Transient
ngspice> show all                        # Operating-point results
ngspice> quit
```

### 4 — Generate plots with Python

```bash
pip install numpy matplotlib
python plot_results.py                   # uses simulation_output/ngspice_output.log
# or pass the log path directly:
python plot_results.py simulation_output/ngspice_output.log
```

This produces `simulation_output/cmos_inverter_results.png` with four panels:
- Voltage Transfer Characteristic (VTC)
- Transient waveforms
- Noise-margin bar chart
- Numeric summary table

---

## Analyses

### DC Sweep — Voltage Transfer Characteristic (VTC)

Sweeps `Vin` from 0 V to 1.8 V in 1 mV steps and plots `Vout`.
Automatic `.MEAS` statements extract:

| Metric                      | Symbol | Typical value |
|-----------------------------|--------|---------------|
| Switching threshold         | VM     | ≈ 0.90 V      |
| Output high level           | VOH    | ≈ 1.80 V      |
| Output low level            | VOL    | ≈ 0.00 V      |
| Input low threshold (slope −1) | VIL | ≈ 0.72 V    |
| Input high threshold (slope −1)| VIH | ≈ 1.08 V   |
| Low noise margin  NML = VIL − VOL | NML | ≈ 720 mV |
| High noise margin NMH = VOH − VIH | NMH | ≈ 720 mV |

### Transient Analysis

Applies a 0 V / 1.8 V pulse (period = 10 ns, rise/fall = 50 ps, load = 40 fF)
and extracts:

| Metric                          | Typical value |
|---------------------------------|---------------|
| Propagation delay HL (tpHL)     | ≈ 25–35 ps    |
| Propagation delay LH (tpLH)     | ≈ 30–40 ps    |
| Average propagation delay (tp)  | ≈ 30 ps       |
| Output rise time  (10%→90%)     | ≈ 55–65 ps    |
| Output fall time  (90%→10%)     | ≈ 40–55 ps    |

### Operating Point (.OP)

Reports DC bias currents through M_PMOS and M_NMOS and all node voltages
at the quiescent state.

---

## Technology Model

The file `180nm_models.lib` provides BSIM3v3 (Level 7) models for both
NMOS and PMOS transistors targeting a generic 180nm node:

- Gate oxide thickness: **Tox = 4 nm**
- Supply voltage: **VDD = 1.8 V**
- NMOS electron mobility: **µ₀ = 270 cm²/V·s**
- PMOS hole mobility: **µ₀ = 95 cm²/V·s**
- NMOS threshold: **Vth = +0.50 V**
- PMOS threshold: **Vth = −0.50 V**

The models include:
- Short-channel effects (DVT0/DVT1/DVT2)
- Velocity saturation (VSAT)
- DIBL (ETA0/ETAB)
- Channel-length modulation (PCLM)
- Gate-oxide capacitance and overlap capacitances (CGD0, CGS0, CGB0)
- Drain/source junction capacitances (CJ, CJSW, CJSWG)

---

## References

1. Weste, N. & Harris, D. *CMOS VLSI Design*, 4th ed. Addison-Wesley, 2011.
2. Rabaey, J. M., Chandrakasan, A. & Nikolic, B. *Digital Integrated Circuits*,
   2nd ed. Prentice-Hall, 2003.
3. Predictive Technology Model (PTM) — http://ptm.asu.edu/
4. BSIM3v3 MOSFET Model Manual — UC Berkeley Device Group.