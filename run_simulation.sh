#!/usr/bin/env bash
# =============================================================
#  run_simulation.sh — CMOS Inverter 180nm SPICE Simulation
#
#  Supported simulators (tried in order):
#    1. ngspice  (open-source, most widely available)
#    2. hspice   (commercial, Synopsys)
#    3. spectre  (commercial, Cadence)
#
#  Usage:
#    chmod +x run_simulation.sh
#    ./run_simulation.sh            # auto-detect simulator
#    ./run_simulation.sh ngspice    # force ngspice
#    ./run_simulation.sh hspice     # force hspice
# =============================================================

set -euo pipefail

NETLIST="cmos_inverter.sp"
OUTPUT_DIR="simulation_output"

# -------------------------------------------------------
#  Helper functions
# -------------------------------------------------------
info()  { echo "[INFO]  $*"; }
error() { echo "[ERROR] $*" >&2; exit 1; }

check_file() {
    [[ -f "$1" ]] || error "Required file not found: $1"
}

# -------------------------------------------------------
#  Detect or override simulator
# -------------------------------------------------------
detect_simulator() {
    if   command -v ngspice  &>/dev/null; then echo "ngspice"
    elif command -v hspice   &>/dev/null; then echo "hspice"
    elif command -v spectre  &>/dev/null; then echo "spectre"
    else
        error "No supported SPICE simulator found. Install ngspice:
    Ubuntu/Debian : sudo apt-get install ngspice
    Fedora/RHEL   : sudo dnf install ngspice
    macOS (brew)  : brew install ngspice
    Windows (WSL) : sudo apt-get install ngspice"
    fi
}

SIMULATOR="${1:-$(detect_simulator)}"

# -------------------------------------------------------
#  Validate inputs
# -------------------------------------------------------
check_file "$NETLIST"
check_file "180nm_models.lib"

mkdir -p "$OUTPUT_DIR"

info "Simulator  : $SIMULATOR"
info "Netlist    : $NETLIST"
info "Output dir : $OUTPUT_DIR"
echo ""

# -------------------------------------------------------
#  Run simulation
# -------------------------------------------------------
case "$SIMULATOR" in

  ngspice)
    info "Running ngspice …"
    ngspice -b "$NETLIST" \
            -o "$OUTPUT_DIR/ngspice_output.log" \
            2>&1 | tee "$OUTPUT_DIR/ngspice_console.log"
    info "Raw output : $OUTPUT_DIR/ngspice_output.log"
    ;;

  hspice)
    info "Running HSPICE …"
    hspice "$NETLIST" -o "$OUTPUT_DIR/hspice_output" \
           | tee "$OUTPUT_DIR/hspice_console.log"
    info "HSPICE data files written to $OUTPUT_DIR/"
    ;;

  spectre)
    info "Running Spectre (via HSPICE-compatibility mode) …"
    spectre +compat hspice "$NETLIST" \
            -raw "$OUTPUT_DIR/spectre_raw" \
            | tee "$OUTPUT_DIR/spectre_console.log"
    info "Spectre data written to $OUTPUT_DIR/spectre_raw"
    ;;

  *)
    error "Unknown simulator '$SIMULATOR'. Use: ngspice | hspice | spectre"
    ;;
esac

echo ""
info "Simulation complete."
echo ""
echo "====================================================================="
echo "  POST-PROCESSING HINTS"
echo "====================================================================="
echo ""
echo "  ngspice interactive plot (DC VTC):"
echo "    ngspice cmos_inverter.sp"
echo "    ngspice> plot v(vout_dc) vs v(vin_dc)"
echo ""
echo "  ngspice interactive plot (Transient):"
echo "    ngspice> plot v(vin_tr) v(vout_tr)"
echo ""
echo "  Python / numpy post-processing:"
echo "    See plot_results.py for automated waveform plots."
echo ""
echo "====================================================================="
