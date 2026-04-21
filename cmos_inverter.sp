* ============================================================
*  CMOS Inverter — 180nm Technology Node SPICE Simulation
*
*  Technology : 180nm CMOS (TSMC-compatible BSIM3v3)
*  Supply     : VDD = 1.8 V
*  NMOS       : W/L = 1.0µm / 180nm
*  PMOS       : W/L = 2.0µm / 180nm  (2× NMOS for β-ratio match)
*
*  Analyses included
*    1. DC sweep  → Voltage Transfer Characteristic (VTC)
*    2. Transient → Propagation delay, rise / fall time
*    3. DC op-pt  → Bias-point summary at Vin = VDD/2
* ============================================================

.TITLE CMOS Inverter 180nm Simulation

* ---- Include technology models ----
.LIB '180nm_models.lib'

* ============================================================
*  Supply and stimulus
* ============================================================
VDD   vdd   0   DC 1.8
VSS   0     0   DC 0

* DC input source — swept in .DC analysis
Vin_dc vin_dc 0 DC 0

* Pulse input for transient analysis
*   Format: PULSE(V_low  V_high  t_delay  t_rise  t_fall  t_pulse  t_period)
Vin_tr vin_tr 0 PULSE(0 1.8 0.1ns 0.05ns 0.05ns 5ns 10ns)

* ============================================================
*  CMOS Inverter Sub-Circuit Definition
* ============================================================
.SUBCKT CMOS_INV  vin vout vdd vss
*            Gate  Drain Source  Bulk   Model         W       L
M_PMOS  vout  vin   vdd   vdd  PMOS_180nm  W=2.0u  L=180n
M_NMOS  vout  vin   vss   vss  NMOS_180nm  W=1.0u  L=180n
.ENDS CMOS_INV

* ============================================================
*  DUT 1 — For DC VTC sweep
* ============================================================
XINV_DC vin_dc vout_dc vdd 0 CMOS_INV

* Load capacitance (fan-out of 4 × gate capacitance ≈ 4 × 10 fF)
CL_DC   vout_dc 0  40f

* ============================================================
*  DUT 2 — For Transient analysis
* ============================================================
XINV_TR vin_tr vout_tr vdd 0 CMOS_INV

* Load capacitance
CL_TR   vout_tr 0  40f

* ============================================================
*  Analysis 1 — DC Sweep (VTC)
*  Sweep Vin from 0 V to 1.8 V in 1 mV steps
* ============================================================
.DC Vin_dc 0 1.8 0.001

* ============================================================
*  Analysis 2 — Transient
*  Simulate 30 ns with 1 ps time step
* ============================================================
.TRAN 1ps 30ns

* ============================================================
*  Analysis 3 — Operating Point at Vin = VDD/2 (0.9 V)
* ============================================================
* (The .OP is evaluated after sweeps; set Vin_dc to 0.9 V manually
*  in a separate run if needed.  Here it is included for reference.)
.OP

* ============================================================
*  Measurements — extracted automatically during simulation
* ============================================================

* --- VTC measurements (from DC sweep) ---
* Switching threshold VM (Vout = Vin crossing)
.MEAS DC  VM     FIND V(vout_dc) WHEN V(vout_dc)=V(vin_dc)

* Output high / low voltages
.MEAS DC  VOH    FIND V(vout_dc) AT=0
.MEAS DC  VOL    FIND V(vout_dc) AT=1.8

* Input low / high threshold (Vout = 90% / 10% of VDD)
.MEAS DC  VIL    FIND V(vin_dc)  WHEN V(vout_dc)=1.62  RISE=1
.MEAS DC  VIH    FIND V(vin_dc)  WHEN V(vout_dc)=0.18  FALL=1

* --- Noise margins (computed from VIL, VIH, VOL, VOH) ---
* NML = VIL - VOL
* NMH = VOH - VIH
.MEAS DC  NML    PARAM='VIL - VOL'
.MEAS DC  NMH    PARAM='VOH - VIH'

* --- Transient measurements ---
* Propagation delay (50% crossing, low-to-high and high-to-low output)
.MEAS TRAN tpHL   TRIG V(vin_tr) VAL=0.9 RISE=1
+                 TARG V(vout_tr) VAL=0.9 FALL=1
.MEAS TRAN tpLH   TRIG V(vin_tr) VAL=0.9 FALL=1
+                 TARG V(vout_tr) VAL=0.9 RISE=1
.MEAS TRAN tp     PARAM='(tpHL + tpLH) / 2'

* Output rise time (10% → 90%)
.MEAS TRAN t_rise TRIG V(vout_tr) VAL=0.18  RISE=1
+                 TARG V(vout_tr) VAL=1.62   RISE=1

* Output fall time (90% → 10%)
.MEAS TRAN t_fall TRIG V(vout_tr) VAL=1.62  FALL=1
+                 TARG V(vout_tr) VAL=0.18   FALL=1

* ============================================================
*  Output — save key node voltages and currents
* ============================================================
.PROBE DC  V(vin_dc) V(vout_dc)
.PROBE TRAN V(vin_tr) V(vout_tr) I(VDD)

* Print all measurement results to output file
.PRINT DC   V(vin_dc) V(vout_dc)
.PRINT TRAN V(vin_tr) V(vout_tr)

.OPTIONS SCALE=1e-6    $ default length unit = µm
.OPTIONS TEMP=27       $ room temperature

.END
