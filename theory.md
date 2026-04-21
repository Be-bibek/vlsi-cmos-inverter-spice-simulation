# 📖 CMOS Inverter — Theory & Background

## 1. Introduction to CMOS Technology

CMOS (Complementary Metal-Oxide-Semiconductor) is the dominant technology used in modern digital integrated circuits. The word "complementary" refers to the use of both **n-type (NMOS)** and **p-type (PMOS)** transistors working together in a push-pull configuration.

### Why CMOS?

| Feature | Benefit |
|---------|---------|
| Near-zero static power | Only dynamic power during switching |
| Full voltage swing | Output swings from 0V to VDD |
| High noise margins | Robust against interference |
| Scalability | Works from micron down to nanometer nodes |

---

## 2. MOSFET Basics

A MOSFET (Metal-Oxide-Semiconductor Field-Effect Transistor) has four terminals:
- **Gate (G)** — Controls the channel; voltage here determines on/off state
- **Drain (D)** — Current flows in here (NMOS) or out here (PMOS)
- **Source (S)** — Reference terminal, connected to supply rail
- **Body (B)** — Substrate; tied to Source in most digital designs

### NMOS vs PMOS

| Property | NMOS | PMOS |
|----------|------|------|
| Carrier | Electrons | Holes |
| Turns ON when | VGS > Vth (positive) | VGS < Vth (negative) |
| Source connected to | GND | VDD |
| Mobility (µ) | Higher (~450 cm²/Vs) | Lower (~200 cm²/Vs) |
| Symbol | Arrow pointing in | Arrow pointing out |

---

## 3. CMOS Inverter Operation

### Circuit

```
      VDD
       |
      [PMOS]  ← Gate = In
       |
       +——— Out
       |
      [NMOS]  ← Gate = In
       |
      GND
```

### Truth Table

| Input (Vin) | PMOS State | NMOS State | Output (Vout) |
|-------------|-----------|-----------|--------------|
| LOW (0V) | ON (conducting) | OFF | HIGH (VDD) |
| HIGH (VDD) | OFF | ON (conducting) | LOW (0V) |

### Static Power Dissipation

In steady state, only **one** transistor is ON at any time. Since no direct path exists from VDD to GND, **static current ≈ 0**, giving near-zero static power: `P_static ≈ 0`.

Dynamic power during switching: `P_dynamic = α · C_L · VDD² · f`

---

## 4. Voltage Transfer Characteristic (VTC)

The VTC plots Vout (y-axis) vs. Vin (x-axis) for DC operation. It completely characterizes the inverter's static behavior.

### Five Regions of Operation

**Region A** (Vin < VTn):
- NMOS: OFF, PMOS: Linear
- Vout = VDD (full high output)

**Region B** (VTn < Vin < VM):
- NMOS: Saturation, PMOS: Linear
- Vout begins to drop

**Region C** (Vin ≈ VM):
- Both in Saturation — maximum gain region
- This is the steepest part of the curve

**Region D** (VM < Vin < VDD + VTp):
- NMOS: Linear, PMOS: Saturation
- Vout continues dropping

**Region E** (Vin > VDD + VTp):
- NMOS: Linear, PMOS: OFF
- Vout = 0V (full low output)

---

## 5. Key VTC Parameters

### Switching Threshold (VM)

VM is the input voltage at which Vout = Vin. It represents the midpoint of the transition.

For a symmetric inverter:
```
VM ≈ VDD/2
```

Achieved when: `kn = kp`, i.e., `µn·Wn/Ln = µp·Wp/Lp`

Since `µn ≈ 2µp`: set `Wp = 2·Wn` for VM = VDD/2

### Noise Margins

Noise margins define how much noise the inverter can tolerate on its input without incorrect output.

```
NMH = VOH − VIH    (High-level noise margin)
NML = VIL − VOL    (Low-level noise margin)
```

For an ideal inverter with VDD = 1V:
- VOH = 1V, VOL = 0V → full output swing
- VIH ≈ 0.6V, VIL ≈ 0.4V (approximately)
- NMH ≈ NML ≈ 0.4V

---

## 6. The 180nm Technology Node

The 180nm node (also written as 0.18µm) was a widely produced process from the late 1990s. It remains the most popular node for academic PDK (Process Design Kit) education because:

- Models are publicly available (e.g., BSIM3v3)
- Well-documented transistor characteristics
- Suitable for analog and digital design teaching
- VDD = 1.8V typical (though 1.0V is used in this project for simplicity)

The `180nm_nominal.md` file includes the SPICE model cards for NMOS and PMOS transistors at this node, describing parameters like threshold voltage (Vth), carrier mobility (µ), oxide capacitance (Cox), and many others.

---

## 7. Design Rationale — This Project

### Why W(PMOS) = 800nm, W(NMOS) = 400nm?

At 180nm:
- µn (electron mobility) ≈ 2 × µp (hole mobility)
- To match drive strength: set Wp/Wn = µn/µp ≈ 2
- 800nm / 400nm = **2:1 ratio** → symmetric inverter design

### Why L = 180nm for both?

The minimum gate length equals the technology node (180nm). Using minimum L maximizes speed and minimizes area. For educational purposes, both transistors use minimum L.

### Why VDD = 1.0V?

Standard 180nm VDD is 1.8V, but 1.0V is used here to:
- Simplify analysis (makes VM = 0.5V a clean midpoint)
- Demonstrate near-ideal symmetric behavior
- Reduce simulation complexity

---

*For step-by-step reproduction guide, see [`step_by_step_guide.md`](step_by_step_guide.md)*
