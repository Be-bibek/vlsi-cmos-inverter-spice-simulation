# 🔧 Step-by-Step Reproduction Guide

## Prerequisites

Before you begin, make sure you have:

- [ ] **Tanner S-Edit** installed (licensed copy)
- [ ] **T-Spice** simulator (comes with Tanner suite)
- [ ] **W-Edit** waveform viewer (bundled with Tanner)
- [ ] **180nm PDK** model file (`180nm_nominal.md`) — place it in an accessible path
- [ ] Basic familiarity with MOSFET operation

---

## Part 1: Schematic Design in S-Edit

### Step 1.1 — Create a New Cell

1. Open **Tanner S-Edit**
2. Go to **File → New** or open an existing project
3. Create a new cell named `Cell0`
4. The schematic editor opens with a blank canvas

### Step 1.2 — Set Up Libraries

1. In the **Libraries** panel on the left, ensure these libraries are loaded:
   - `Devices`
   - `SPICE_Elements`
   - `SPICE_Commands`
   - `Generic_250nm_Devices` (or 180nm equivalent)
2. Use the **Filter** dropdown to search for components

### Step 1.3 — Place PMOS Transistor

1. In the Libraries panel, select **Devices** → find `pMesfet` or the PMOS symbol
2. Click **Open** to place it on the schematic
3. Double-click the placed symbol to open its properties
4. Set the following parameters:
   - **W** = `800nm`
   - **L** = `180nm`
   - **M** = `1`
5. Name/Label it `PMOS_1`
6. Place it in the upper portion of your schematic

### Step 1.4 — Place NMOS Transistor

1. In Libraries, select **Devices** → find `nMesfet` or NMOS symbol
2. Place it below the PMOS transistor
3. Set parameters:
   - **W** = `400nm`
   - **L** = `180nm`
   - **M** = `1`
4. Name/Label it `NMOS_1`

### Step 1.5 — Place Voltage Sources

**V1 — Power Supply (VDD):**
1. From **SPICE_Elements** library, select a DC voltage source
2. Place it connected to the **Source** of PMOS_1 (top)
3. Set value to **1.0V**
4. Label it `V1`

**V2 — Input Source (for DC sweep):**
1. Place another voltage source
2. Connect it to the **Input** node (gates of both PMOS and NMOS)
3. Set value to **1.0V** (this will be swept during simulation)
4. Label it `V2`

### Step 1.6 — Add Ports

1. From the toolbar or **Draw** menu, add a **Port**
2. Place an **In** port at the input node (gate connection)
3. Place an **Out** port at the output node (common drain of PMOS and NMOS)

### Step 1.7 — Add Ground

1. From **Devices** or the toolbar, place a **GND** symbol
2. Connect it to:
   - The **Source** of NMOS_1
   - The negative terminal of V1
   - The negative terminal of V2

### Step 1.8 — Add PrintVoltage Probes

1. From **SPICE_Commands** library, find `PrintVoltage`
2. Place one probe on the **In** node
3. Place another probe on the **Out** node
4. These will instruct T-Spice to record and print voltage at these nodes

### Step 1.9 — Wire the Circuit

Connect with wires (press `W` or use **Draw → Wire**):

```
VDD (V1+)
    │
  [PMOS_1 Source]
  [PMOS_1 Gate] ←───── In port ←── V2(+)
  [PMOS_1 Drain]
    │
   Out port
    │
  [NMOS_1 Drain]
  [NMOS_1 Gate] ←───── In port
  [NMOS_1 Source]
    │
   GND ──── V1(−) ──── V2(−)
```

### Step 1.10 — Save the Schematic

- Press **Ctrl+S** or **File → Save**
- Verify no DRC (Design Rule Check) errors in the Command window

---

## Part 2: Simulation Setup

### Step 2.1 — Open Simulation Dialog

1. Go to **Setup → SPICE Simulation** (or press the simulation button)
2. The **"Setup SPICE Simulation of cell 'Cell0'"** dialog opens

### Step 2.2 — Configure General Settings

Click **General** in the left panel:

| Field | Value |
|-------|-------|
| Reference Temperature | 27 (default) |
| Accuracy | Default |
| Show Waveforms | During |
| Include Files | `../../180nm_nominal.md` (adjust path to where your PDK file is located) |
| Simulator | T-Spice |

> ⚠️ **Important:** The path to `180nm_nominal.md` must be correct. If it's wrong, the simulation will fail with "model not found" errors.

### Step 2.3 — Enable DC Sweep Analysis

1. In the left panel, check ✅ **DC Sweep Analysis**
2. Click on **DC Sweep Analysis** to open its settings

### Step 2.4 — Configure DC Sweep Parameters

Under **Source 1** (swept for each value of Source 2):

| Field | Value |
|-------|-------|
| Source or Parameter Name | `vv2` |
| Start Value | `0v` |
| Stop Value | `1v` |
| Step | `0.1v` |
| Sweep Type | `lin` (linear) |

Leave Source 2 and Source 3 disabled (default).

> 💡 The source name `vv2` corresponds to voltage source V2 in the schematic. T-Spice prefixes voltage source names with an extra 'v'.

### Step 2.5 — Run the Simulation

1. Click **Run Simulation** button
2. T-Spice will:
   - Generate the SPICE netlist from schematic
   - Load the 180nm model file
   - Sweep V2 from 0V to 1V in 0.1V steps
   - Record In:V and Out:V at each step
3. W-Edit opens automatically when simulation completes

---

## Part 3: Viewing Results in W-Edit

### Step 3.1 — Set the X-Axis

1. In the **DC Chart Parameters** panel (left side of W-Edit)
2. Under **Independent**, select `vv2` from the dropdown
3. The x-axis now represents input voltage (0 to 1V)

### Step 3.2 — Plot Waveforms

1. Expand the simulation tree to find `In:V` and `Out:V`
2. Click to add them to the plot
3. `In:V` appears as a **straight diagonal line** (red) — this is expected (it equals Vin)
4. `Out:V` appears as the **inverter VTC curve** (green)

### Step 3.3 — Analyze the VTC

Observe and note:
- At Vin = 0V: Vout ≈ 1.0V ✓
- At Vin = 1V: Vout ≈ 0.0V ✓
- The steep transition: approximately between Vin = 0.35V and 0.65V
- The switching threshold VM ≈ 0.45–0.50V (where Out:V crosses In:V)

### Step 3.4 — Export/Screenshot

- Use **File → Export** or take a screenshot of the waveform
- Save to `results/vtc_waveform.png`

---

## Common Errors & Fixes

| Error | Likely Cause | Fix |
|-------|-------------|-----|
| "Model not found" | Wrong path to `180nm_nominal.md` | Check Include Files path in General settings |
| Flat output (no switching) | Wiring error in schematic | Check PMOS/NMOS gate connections to In port |
| Output stuck at 0 or 1 | PMOS/NMOS parameters wrong | Verify W, L values in transistor properties |
| Simulation runs but no waveform | PrintVoltage probes missing | Add PrintVoltage on In and Out nodes |
| W-Edit shows empty chart | Wrong independent variable | Set Independent to `vv2` in DC Chart Parameters |

---

*For theory and background, see [`theory.md`](theory.md)*
