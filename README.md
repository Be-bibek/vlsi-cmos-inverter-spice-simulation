# ⚡ CMOS Inverter Design & Simulation — 180nm Technology Node

<div align="center">

![VLSI](https://img.shields.io/badge/Domain-VLSI%20Design-blue?style=for-the-badge&logo=circuit)
![Technology](https://img.shields.io/badge/Technology-180nm%20CMOS-green?style=for-the-badge)
![Tool](https://img.shields.io/badge/Tool-Tanner%20S--Edit-orange?style=for-the-badge)
![Simulator](https://img.shields.io/badge/Simulator-T--Spice-red?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Completed-brightgreen?style=for-the-badge)

**A complete VLSI design project implementing a CMOS Inverter from schematic to simulation using Tanner EDA Tools.**

</div>

---

## 📖 Table of Contents

- [Project Overview](#-project-overview)
- [What is a CMOS Inverter?](#-what-is-a-cmos-inverter)
- [Design Specifications](#-design-specifications)
- [Tools Used](#-tools-used)
- [Repository Structure](#-repository-structure)
- [Schematic Design](#-schematic-design)
- [Simulation Setup](#-simulation-setup)
- [Results & Waveforms](#-results--waveforms)
- [Theory Behind the Results](#-theory-behind-the-results)
- [How to Reproduce](#-how-to-reproduce)
- [Key Learnings](#-key-learnings)
- [References](#-references)

---

## 🎯 Project Overview

This project demonstrates the complete design flow of a **CMOS (Complementary Metal-Oxide-Semiconductor) Inverter** using **Tanner S-Edit** as the schematic capture tool and **T-Spice** as the SPICE simulator. The inverter is designed at the **180nm technology node** — a widely studied process node in academic VLSI education.

The project covers:
- Schematic entry in a professional EDA environment
- SPICE netlist generation
- DC Sweep simulation to obtain the **Voltage Transfer Characteristic (VTC)**
- Analysis and interpretation of the output waveform

This documentation is intended to help students and junior engineers understand the design and simulation process step by step.

---

## 🔬 What is a CMOS Inverter?

A **CMOS Inverter** is the most fundamental building block in digital VLSI design. It converts a logic HIGH input to a logic LOW output, and vice versa — it **inverts** the input signal.

### Circuit Composition

A CMOS inverter is made of two transistors:

| Transistor | Type | Role |
|------------|------|------|
| M1 (Top) | **PMOS** | Pull-Up Network — connects output to VDD when input is LOW |
| M2 (Bottom) | **NMOS** | Pull-Down Network — connects output to GND when input is HIGH |

### Working Principle

```
Input = LOW (0V)  → PMOS ON,  NMOS OFF → Output = HIGH (VDD)
Input = HIGH (VDD) → PMOS OFF, NMOS ON  → Output = LOW  (GND)
```

This complementary switching ensures that there is **never a direct path from VDD to GND** in steady state, which is why CMOS circuits have extremely low static power consumption.

---

## 📐 Design Specifications

| Parameter | Value |
|-----------|-------|
| **Technology Node** | 180nm CMOS |
| **Supply Voltage (VDD)** | 1.0 V |
| **PMOS Width (W)** | 800 nm |
| **PMOS Length (L)** | 180 nm |
| **PMOS Multiplier (M)** | 1 |
| **NMOS Width (W)** | 400 nm |
| **NMOS Length (L)** | 180 nm |
| **NMOS Multiplier (M)** | 1 |
| **W/L Ratio (PMOS)** | ~4.44 |
| **W/L Ratio (NMOS)** | ~2.22 |
| **PMOS/NMOS Width Ratio** | 2:1 |

> 💡 **Why is PMOS wider?**
> Hole mobility (µₚ) in PMOS is roughly **2× lower** than electron mobility (µₙ) in NMOS. To compensate and achieve **symmetric switching** (equal rise and fall times), the PMOS is made approximately **2× wider** than NMOS. Here PMOS W=800nm and NMOS W=400nm, maintaining the 2:1 ratio.

---

## 🛠 Tools Used

| Tool | Purpose | Version |
|------|---------|---------|
| **Tanner S-Edit** | Schematic Capture (EDA Tool) | Licensed |
| **T-Spice** | SPICE Circuit Simulator | 15.23 |
| **W-Edit** | Waveform Viewer | Bundled with Tanner |
| **Process File** | `180nm_nominal.md` | 180nm PDK |

### About Tanner EDA
Tanner EDA (now part of Mentor, a Siemens Business) provides a suite of tools for analog, mixed-signal, and custom digital IC design. **S-Edit** is its schematic editor, and **T-Spice** is a high-performance SPICE simulator compatible with industry-standard SPICE models.

---

## 📁 Repository Structure

```
cmos-inverter-180nm/
│
├── 📄 README.md                  ← You are here
│
├── 📂 schematics/
│   ├── inverter_schematic.png    ← Full schematic screenshot (S-Edit)
│   └── cell0_schematic.sp        ← SPICE netlist (exported from S-Edit)
│
├── 📂 simulation/
│   ├── setup_general.png         ← SPICE simulation general settings screenshot
│   ├── setup_dc_sweep.png        ← DC Sweep analysis settings screenshot
│   └── Cell0.sp                  ← T-Spice simulation file
│
├── 📂 results/
│   ├── vtc_waveform.png          ← VTC output waveform (from W-Edit)
│   └── analysis.md               ← Detailed analysis of results
│
├── 📂 docs/
│   ├── theory.md                 ← CMOS inverter theory & background
│   └── step_by_step_guide.md    ← How to reproduce this project
│
└── 📂 process/
    └── 180nm_nominal.md          ← Process model file (PDK reference)
```

> 📌 **Note for contributors:** Please upload your screenshots/files to the corresponding folders before committing.

---

## 🖥 Schematic Design

The schematic was designed in **Tanner S-Edit** under the cell name `Cell0`.

### Schematic Overview

<img width="1600" height="900" alt="IMG-20260421-WA0004" src="https://github.com/user-attachments/assets/11027e3d-5ab1-4fb0-ae60-d334e0ae0272" />


### Circuit Description

The schematic consists of:

- **V1 (1.0V)** — Power supply (VDD), connected to the source of PMOS (PMOS_1)
- **V2 (1.0V)** — Input voltage source used for DC sweep; connected to the gate of both PMOS_1 and NMOS_1 via the **In** port
- **PMOS_1** — Pull-up transistor (W=800nm, L=180nm), drain connected to output
- **NMOS_1** — Pull-down transistor (W=400nm, L=180nm), drain connected to output
- **In** — Input port (gate of both MOSFETs)
- **Out** — Output port (common drain of PMOS and NMOS)
- **GND** — Ground reference (source of NMOS)
- **PrintVoltage** — Voltage probes placed to monitor In and Out signals during simulation

---

## ⚙️ Simulation Setup

The simulation was configured using the **Setup SPICE Simulation** dialog in S-Edit.

### General Settings

<img width="1600" height="900" alt="IMG-20260421-WA0006" src="https://github.com/user-attachments/assets/9b7159e6-ebd6-4e84-9284-3e40c73d584a" />

| Setting | Value |
|---------|-------|
| **Simulator** | T-Spice |
| **Include Files** | `../../180nm_nominal.md` |
| **Show Waveforms** | During simulation |
| **Analysis Type** | DC Sweep Analysis ✅ |

### DC Sweep Configuration

<img width="1600" height="900" alt="IMG-20260421-WA0007" src="https://github.com/user-attachments/assets/afcd6288-67ec-41d8-9dd3-81a5d55ae174" />


| Parameter | Value |
|-----------|-------|
| **Source Swept (Source 1)** | `vv2` (Input voltage V2) |
| **Start Value** | 0 V |
| **Stop Value** | 1 V |
| **Step** | 0.1 V |
| **Sweep Type** | Linear (`lin`) |

> 💡 **What is DC Sweep?**
> DC Sweep varies the input voltage from a start to stop value in defined steps, recording the output at each point. This gives us the **Voltage Transfer Characteristic (VTC)** — the most important static characteristic of a digital gate.

---

## 📊 Results & Waveforms

### Voltage Transfer Characteristic (VTC)

The simulation was run in **T-Spice 15.23** and the waveform was viewed in **W-Edit**.

 </div><img width="1600" height="900" alt="IMG-20260421-WA0008" src="https://github.com/user-attachments/assets/83e294db-3284-479b-a7b7-a84dd2b893f1" />



### What the VTC Shows


| Input (In:V) | Output (Out:V) | Transistor State |
|-------------|----------------|-----------------|
| 0.0 V → ~0.35 V | ~1.0 V (HIGH) | PMOS ON, NMOS OFF |
| ~0.35 V → ~0.65 V | Transition region | Both partially ON |
| ~0.65 V → 1.0 V | ~0.0 V (LOW) | PMOS OFF, NMOS ON |

- The **red diagonal line** represents the input voltage (In:V) sweeping linearly from 0V to 1V
- The **green curve** represents the output voltage (Out:V)
- The **sharp switching** around ~0.45–0.55V is the **switching threshold (Vth)**, which appears close to VDD/2 = 0.5V — confirming good symmetric design

---

## 📚 Theory Behind the Results

### Voltage Transfer Characteristic (VTC) Regions

A CMOS inverter VTC has **5 operating regions**:

```
Output (Vout)
   │
VDD├────────╮
   │        │  Region A: PMOS linear, NMOS cutoff
   │        │
   │        │  Region B: PMOS linear, NMOS saturation
   │         ╲
   │          ╲  Region C: Both in saturation (transition)
   │           ╲
   │            │  Region D: PMOS saturation, NMOS linear
   │            │
  0├────────────╯──────────────────────────► Input (Vin)
   0           Vth                         VDD
```

### Key Parameters from VTC

| Parameter | Description | Significance |
|-----------|-------------|-------------|
| **VOH** (Output High) | ~VDD = 1.0V | Logic HIGH output level |
| **VOL** (Output Low) | ~GND = 0.0V | Logic LOW output level |
| **VM** (Switching Threshold) | ~VDD/2 ≈ 0.5V | Midpoint — symmetric design goal |
| **VIL** (Input Low Max) | ~0.35V | Max input voltage read as logic LOW |
| **VIH** (Input High Min) | ~0.65V | Min input voltage read as logic HIGH |
| **Noise Margin LOW (NML)** | VIL − VOL | Tolerance to LOW-side noise |
| **Noise Margin HIGH (NMH)** | VOH − VIH | Tolerance to HIGH-side noise |

### Why 2:1 PMOS/NMOS Width Ratio?

The switching threshold VM is given by:

```
VM = (VTp + VDD·√(kn/kp)) / (1 + √(kn/kp))
```

Where `kn/kp = (µn·Cox·Wn/Ln) / (µp·Cox·Wp/Lp)`.

Since `µn ≈ 2µp`, setting `Wp/Wn = 2` makes `kn/kp ≈ 1`, which gives `VM ≈ VDD/2 = 0.5V`. This is the ideal symmetric inverter design.

---

## 🔄 How to Reproduce

Follow these steps to replicate this project from scratch:

### Step 1: Install Tanner EDA Tools
- Obtain a licensed copy of **Tanner S-Edit** and **T-Spice**
- Install the **180nm PDK** (Process Design Kit) — model file: `180nm_nominal.md`

### Step 2: Create the Schematic in S-Edit
1. Open S-Edit → New Cell → Name it `Cell0`
2. From the **Devices** library, place:
   - `PMOS` transistor → Set W=800nm, L=180nm, M=1
   - `NMOS` transistor → Set W=400nm, L=180nm, M=1
3. From **SPICE_Elements**, place two voltage sources:
   - V1 = 1.0V (VDD, connected to PMOS source)
   - V2 = 1.0V (Input source, to be swept)
4. Add **In** and **Out** ports
5. Add **GND** symbol
6. Add **PrintVoltage** probes on In and Out nodes
7. Wire all connections as shown in the schematic

### Step 3: Configure Simulation
1. Go to **Setup → SPICE Simulation**
2. Under **General**:
   - Set Include Files to your `180nm_nominal.md` path
   - Set Simulator to `T-Spice`
3. Check **DC Sweep Analysis**:
   - Source: `vv2`
   - Start: `0v`, Stop: `1v`, Step: `0.1v`
   - Sweep Type: `lin`
4. Click **Run Simulation**

### Step 4: View Results in W-Edit
1. W-Edit opens automatically after simulation
2. Select `vv2` as the X-axis (independent variable)
3. Plot `In:V` and `Out:V`
4. Observe the VTC curve

---

## 💡 Key Learnings

After completing this project, you should understand:

- ✅ How to use **Tanner S-Edit** for schematic capture in a professional VLSI workflow
- ✅ The role of **PMOS and NMOS** transistors in a complementary digital circuit
- ✅ Why the **PMOS is made 2× wider** than NMOS for symmetric switching
- ✅ How to set up a **DC Sweep simulation** in T-Spice
- ✅ How to read and interpret a **VTC (Voltage Transfer Characteristic)**
- ✅ The definitions of **VOH, VOL, VIL, VIH, VM**, and **Noise Margins**
- ✅ The significance of the **180nm technology node** in CMOS design education

---

## 📚 References

1. **Weste, N. & Harris, D.** — *CMOS VLSI Design: A Circuits and Systems Perspective*, 4th Ed., Pearson
2. **Rabaey, J., Chandrakasan, A. & Nikolic, B.** — *Digital Integrated Circuits: A Design Perspective*, 2nd Ed., Prentice Hall
3. **Tanner EDA Documentation** — S-Edit User Guide, T-Spice Reference Manual
4. **TSMC 180nm PDK** — Process Design Kit for 0.18µm technology
5. **MOSFET Operation** — *Sedra/Smith: Microelectronic Circuits*, 7th Ed.

---

## 👤 Author

> **[Bibek Das ]**
> B.Tech/M.Tech Student — Electronics & Communication / VLSI Design
> Institution: [GNIT]
> Date: April 2026

---

## 📝 License

This project is released for **educational purposes**. Feel free to use, reference, and build upon this work for your own learning.

---

<div align="center">

**⭐ If this project helped you understand CMOS inverter design, please star the repository!**

*Built with ❤️ using Tanner EDA Tools & 180nm CMOS Technology*



