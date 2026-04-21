#!/usr/bin/env python3
"""
plot_results.py — Post-process ngspice raw output and plot CMOS inverter results.

Requires:
    pip install numpy matplotlib

Usage:
    # After running the simulation with ngspice batch mode:
    python plot_results.py

    # Or pass the log file explicitly:
    python plot_results.py simulation_output/ngspice_output.log
"""

import sys
import re
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")          # headless / non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec


# ---------------------------------------------------------------------------
#  Lightweight ngspice ASCII-output parser
# ---------------------------------------------------------------------------

def parse_ngspice_log(filepath: str) -> dict:
    """
    Parse an ngspice batch (-b) output log and extract named tables
    (Index, sweep variable, node voltages).

    Returns a dict: {'dc': {'vin': [...], 'vout': [...]},
                     'tran': {'time': [...], 'vin': [...], 'vout': [...]},
                     'measures': {'VM': ..., 'VOH': ..., ...}}
    """
    results: dict = {"dc": {}, "tran": {}, "measures": {}}

    if not os.path.exists(filepath):
        print(f"[WARN] Log file not found: {filepath}")
        return results

    with open(filepath, "r", errors="replace") as fh:
        content = fh.read()

    # ---- Extract .MEAS results ----------------------------------------
    for m in re.finditer(
        r"^(vm|voh|vol|vil|vih|nml|nmh|tphl|tplh|tp|t_rise|t_fall)\s*=\s*([0-9eE+\-.]+)",
        content,
        re.IGNORECASE | re.MULTILINE,
    ):
        key = m.group(1).upper()
        val = float(m.group(2))
        results["measures"][key] = val

    # ---- Extract DC table ------------------------------------------------
    dc_block = re.search(
        r"DC transfer characteristic.*?Index.*?\n(.*?)(?=\n\n|\Z)",
        content,
        re.DOTALL | re.IGNORECASE,
    )
    if dc_block:
        vin_vals, vout_vals = [], []
        for line in dc_block.group(1).splitlines():
            parts = line.split()
            if len(parts) >= 3:
                try:
                    vin_vals.append(float(parts[1]))
                    vout_vals.append(float(parts[2]))
                except ValueError:
                    pass
        results["dc"]["vin"] = np.array(vin_vals)
        results["dc"]["vout"] = np.array(vout_vals)

    # ---- Extract Transient table ----------------------------------------
    tr_block = re.search(
        r"Transient Analysis.*?Index.*?\n(.*?)(?=\n\n|\Z)",
        content,
        re.DOTALL | re.IGNORECASE,
    )
    if tr_block:
        t_vals, vin_vals, vout_vals = [], [], []
        for line in tr_block.group(1).splitlines():
            parts = line.split()
            if len(parts) >= 4:
                try:
                    t_vals.append(float(parts[1]))
                    vin_vals.append(float(parts[2]))
                    vout_vals.append(float(parts[3]))
                except ValueError:
                    pass
        results["tran"]["time"] = np.array(t_vals) * 1e9   # convert to ns
        results["tran"]["vin"] = np.array(vin_vals)
        results["tran"]["vout"] = np.array(vout_vals)

    return results


# ---------------------------------------------------------------------------
#  Synthetic data generator (used when no log file is available)
# ---------------------------------------------------------------------------

def generate_synthetic_data() -> dict:
    """
    Generate idealized 180nm CMOS inverter waveforms for demonstration.
    These curves are computed analytically (square-law model with CLM)
    rather than from a full SPICE run.
    """
    VDD = 1.8
    Vtn = 0.5       # NMOS threshold (V)
    Vtp = -0.5      # PMOS threshold (V)
    kn = 270e-6 * (1.0 / 0.18)   # µn·Cox·(W/L)n  [A/V²]
    kp = 95e-6  * (2.0 / 0.18)   # µp·Cox·(W/L)p  [A/V²]

    # --- DC VTC (iterative solution of Id_n = Id_p) ---
    vin_dc = np.linspace(0, VDD, 1801)
    vout_dc = np.zeros_like(vin_dc)

    for i, vi in enumerate(vin_dc):
        # Binary search for Vout such that In == Ip
        lo, hi = 0.0, VDD
        for _ in range(60):
            vo = (lo + hi) / 2.0
            # NMOS current (saturation or linear)
            vgs_n = vi
            vds_n = vo
            if vgs_n <= Vtn:
                In = 0.0
            elif vds_n >= (vgs_n - Vtn):
                In = 0.5 * kn * (vgs_n - Vtn) ** 2
            else:
                In = kn * ((vgs_n - Vtn) * vds_n - 0.5 * vds_n ** 2)
            # PMOS current
            vgs_p = vi - VDD
            vds_p = vo - VDD
            vtp = Vtp
            if vgs_p >= vtp:
                Ip = 0.0
            elif vds_p <= (vgs_p - vtp):
                Ip = 0.5 * kp * (vgs_p - vtp) ** 2
            else:
                Ip = kp * ((vgs_p - vtp) * vds_p - 0.5 * vds_p ** 2)
            if In > abs(Ip):
                hi = vo
            else:
                lo = vo
            vo = (lo + hi) / 2.0
        vout_dc[i] = vo

    # --- Transient (RC-based exponential approximation) ---
    VDD = 1.8
    CL = 40e-15           # 40 fF load
    t_period = 10e-9
    n_periods = 3
    t_end = n_periods * t_period + 0.1e-9
    dt = 1e-12
    t = np.arange(0, t_end, dt)

    vin_tr = np.zeros_like(t)
    for k in range(n_periods):
        t0 = k * t_period + 0.1e-9
        t1 = t0 + t_period / 2
        vin_tr[(t >= t0) & (t < t1)] = VDD

    vout_tr = np.zeros_like(t)
    tau_fall = CL / (kn * (VDD - Vtn))   # rough RC time constant
    tau_rise = CL / (kp * abs(VDD - abs(Vtp)))

    vout_tr[0] = VDD
    for i in range(1, len(t)):
        vi = vin_tr[i - 1]
        vo = vout_tr[i - 1]
        # simple first-order model
        if vi > VDD / 2:          # NMOS pulling output low
            dv = -(vo / tau_fall) * dt
        else:                      # PMOS pulling output high
            dv = ((VDD - vo) / tau_rise) * dt
        vout_tr[i] = np.clip(vo + dv, 0.0, VDD)

    measures = {
        "VM":     0.9,
        "VOH":    VDD,
        "VOL":    0.0,
        "VIL":    0.72,
        "VIH":    1.08,
        "NML":    0.72,
        "NMH":    0.72,
        "TPHL":   29e-12,
        "TPLH":   35e-12,
        "TP":     32e-12,
        "T_RISE": 60e-12,
        "T_FALL": 48e-12,
    }

    return {
        "dc":       {"vin": vin_dc, "vout": vout_dc},
        "tran":     {"time": t * 1e9, "vin": vin_tr, "vout": vout_tr},
        "measures": measures,
    }


# ---------------------------------------------------------------------------
#  Plotting
# ---------------------------------------------------------------------------

def plot_results(data: dict, output_dir: str = "simulation_output") -> None:
    os.makedirs(output_dir, exist_ok=True)
    VDD = 1.8
    meas = data.get("measures", {})

    fig = plt.figure(figsize=(14, 10))
    fig.suptitle(
        "CMOS Inverter — 180nm Technology Node\n"
        "NMOS: W/L = 1.0µm/180nm  |  PMOS: W/L = 2.0µm/180nm  |  VDD = 1.8 V",
        fontsize=13,
        fontweight="bold",
    )

    gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.42, wspace=0.35)

    # ------------------------------------------------------------------
    #  Plot 1 — VTC
    # ------------------------------------------------------------------
    ax1 = fig.add_subplot(gs[0, 0])
    dc = data.get("dc", {})
    if dc.get("vin") is not None and len(dc["vin"]) > 0:
        ax1.plot(dc["vin"], dc["vout"], "b-", linewidth=2, label="V$_{out}$")
        ax1.plot([0, VDD], [0, VDD], "k--", linewidth=0.8, label="V$_{in}$ = V$_{out}$")
        if "VM" in meas:
            ax1.axvline(meas["VM"], color="red", linestyle=":", linewidth=1)
            ax1.axhline(meas["VM"], color="red", linestyle=":", linewidth=1)
            ax1.plot(meas["VM"], meas["VM"], "ro", markersize=6,
                     label=f"VM = {meas['VM']:.3f} V")
        if "VIL" in meas:
            ax1.axvline(meas["VIL"], color="green", linestyle="--", linewidth=1,
                        label=f"VIL = {meas['VIL']:.3f} V")
        if "VIH" in meas:
            ax1.axvline(meas["VIH"], color="orange", linestyle="--", linewidth=1,
                        label=f"VIH = {meas['VIH']:.3f} V")
        ax1.set_xlabel("V$_{in}$ (V)", fontsize=11)
        ax1.set_ylabel("V$_{out}$ (V)", fontsize=11)
        ax1.set_title("Voltage Transfer Characteristic (VTC)", fontsize=11)
        ax1.set_xlim(0, VDD)
        ax1.set_ylim(-0.05, VDD + 0.05)
        ax1.legend(fontsize=8, loc="upper right")
        ax1.grid(True, linestyle=":", alpha=0.6)

    # ------------------------------------------------------------------
    #  Plot 2 — Transient waveforms
    # ------------------------------------------------------------------
    ax2 = fig.add_subplot(gs[0, 1])
    tran = data.get("tran", {})
    if tran.get("time") is not None and len(tran["time"]) > 0:
        ax2.plot(tran["time"], tran["vin"],  "g-",  linewidth=1.5, label="V$_{in}$")
        ax2.plot(tran["time"], tran["vout"], "b-",  linewidth=1.5, label="V$_{out}$")
        ax2.axhline(0.9,  color="gray", linestyle=":", linewidth=0.8)
        ax2.axhline(1.62, color="gray", linestyle=":", linewidth=0.8)
        ax2.axhline(0.18, color="gray", linestyle=":", linewidth=0.8)
        ax2.set_xlabel("Time (ns)", fontsize=11)
        ax2.set_ylabel("Voltage (V)", fontsize=11)
        ax2.set_title("Transient Response", fontsize=11)
        ax2.set_ylim(-0.1, VDD + 0.1)
        ax2.legend(fontsize=9)
        ax2.grid(True, linestyle=":", alpha=0.6)

    # ------------------------------------------------------------------
    #  Plot 3 — Noise margin diagram
    # ------------------------------------------------------------------
    ax3 = fig.add_subplot(gs[1, 0])
    if all(k in meas for k in ("VIL", "VIH", "VOL", "VOH", "NML", "NMH")):
        categories = ["NML\n(Low noise margin)", "NMH\n(High noise margin)"]
        values = [meas["NML"], meas["NMH"]]
        bars = ax3.bar(categories, values, color=["steelblue", "tomato"],
                       width=0.4, edgecolor="black")
        for bar, val in zip(bars, values):
            ax3.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.01,
                f"{val:.3f} V",
                ha="center", va="bottom", fontsize=10, fontweight="bold",
            )
        ax3.set_ylim(0, VDD * 0.75)
        ax3.set_ylabel("Noise Margin (V)", fontsize=11)
        ax3.set_title("Noise Margins", fontsize=11)
        ax3.grid(True, axis="y", linestyle=":", alpha=0.6)

    # ------------------------------------------------------------------
    #  Plot 4 — Summary table
    # ------------------------------------------------------------------
    ax4 = fig.add_subplot(gs[1, 1])
    ax4.axis("off")

    rows = [
        ("Supply Voltage (VDD)",      "1.8 V"),
        ("NMOS W/L",                  "1.0µm / 180nm"),
        ("PMOS W/L",                  "2.0µm / 180nm"),
        ("Technology",                "180nm CMOS"),
        ("", ""),
        ("Switching Threshold (VM)",  f"{meas.get('VM',   float('nan')):.4f} V"),
        ("Output High (VOH)",         f"{meas.get('VOH',  float('nan')):.4f} V"),
        ("Output Low (VOL)",          f"{meas.get('VOL',  float('nan')):.4f} V"),
        ("Input Low (VIL)",           f"{meas.get('VIL',  float('nan')):.4f} V"),
        ("Input High (VIH)",          f"{meas.get('VIH',  float('nan')):.4f} V"),
        ("Noise Margin Low (NML)",    f"{meas.get('NML',  float('nan')):.4f} V"),
        ("Noise Margin High (NMH)",   f"{meas.get('NMH',  float('nan')):.4f} V"),
        ("", ""),
        ("Prop. delay HL (tpHL)",     f"{meas.get('TPHL', float('nan'))*1e12:.1f} ps"),
        ("Prop. delay LH (tpLH)",     f"{meas.get('TPLH', float('nan'))*1e12:.1f} ps"),
        ("Average prop. delay (tp)",  f"{meas.get('TP',   float('nan'))*1e12:.1f} ps"),
        ("Rise time (10%→90%)",       f"{meas.get('T_RISE', float('nan'))*1e12:.1f} ps"),
        ("Fall time (90%→10%)",       f"{meas.get('T_FALL', float('nan'))*1e12:.1f} ps"),
    ]

    table_data = [[p, v] for p, v in rows]

    table = ax4.table(
        cellText=table_data,
        colLabels=["Parameter", "Value"],
        loc="center",
        cellLoc="left",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(8.5)
    table.scale(1.15, 1.35)

    # Style header
    for j in range(2):
        table[(0, j)].set_facecolor("#2c5f8a")
        table[(0, j)].set_text_props(color="white", fontweight="bold")

    # Style separator rows (empty rows)
    for i, (p, _) in enumerate(rows, start=1):
        if p == "":
            for j in range(2):
                table[(i, j)].set_facecolor("#e8e8e8")

    ax4.set_title("Simulation Summary", fontsize=11, pad=12)

    # ------------------------------------------------------------------
    #  Save figure
    # ------------------------------------------------------------------
    out_path = os.path.join(output_dir, "cmos_inverter_results.png")
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    print(f"[INFO] Plot saved to: {out_path}")
    plt.close(fig)


# ---------------------------------------------------------------------------
#  Main
# ---------------------------------------------------------------------------

def main() -> None:
    log_file = sys.argv[1] if len(sys.argv) > 1 else "simulation_output/ngspice_output.log"

    print("[INFO] Attempting to parse simulation log …")
    data = parse_ngspice_log(log_file)

    # Fall back to synthetic data if no real log is available
    if not data["dc"] and not data["tran"]:
        print("[INFO] No parsed data found — generating synthetic demonstration data.")
        data = generate_synthetic_data()

    print("[INFO] Plotting results …")
    plot_results(data)
    print("[INFO] Done.")

    # Print measurement summary to console
    meas = data.get("measures", {})
    if meas:
        print("\n" + "=" * 52)
        print("  CMOS Inverter 180nm — Key Metrics")
        print("=" * 52)
        for key, val in sorted(meas.items()):
            unit = "ps" if key in ("TPHL", "TPLH", "TP", "T_RISE", "T_FALL") else "V"
            factor = 1e12 if unit == "ps" else 1.0
            print(f"  {key:<18} {val*factor:>10.3f}  {unit}")
        print("=" * 52)


if __name__ == "__main__":
    main()
