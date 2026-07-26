#!/usr/bin/env python3
from pathlib import Path
import csv
import json
import numpy as np
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
CSV_PATH = ROOT / "digitized_curve.csv"
PARAM_PATH = ROOT / "curve_model_parameters.json"
LUT_PATH = ROOT / "Linear_to_HLG_1D_65536_NikonZ8.cube"
OUTPUT_PATH = ROOT / "NikonZ8_reverse_LUT_fit_check.png"

def read_cube(path):
    input_min = None
    input_max = None
    declared_size = None
    values = []

    with path.open("r", encoding="ascii") as file:
        for raw_line in file:
            line = raw_line.strip()
            if not line or line.startswith("#") or line.startswith("TITLE"):
                continue
            if line.startswith("LUT_1D_SIZE"):
                declared_size = int(line.split()[1])
                continue
            if line.startswith("LUT_1D_INPUT_RANGE"):
                parts = line.split()
                input_min = float(parts[1])
                input_max = float(parts[2])
                continue
            if line.startswith(("DOMAIN_MIN", "DOMAIN_MAX")):
                raise ValueError(
                    f"Unsupported legacy domain tag remains in {path.name}: {line}"
                )
            values.append(float(line.split()[0]))

    if input_min is None or input_max is None:
        raise ValueError(f"LUT_1D_INPUT_RANGE missing from {path.name}")
    if declared_size != len(values):
        raise ValueError(
            f"{path.name}: declared {declared_size}, parsed {len(values)}"
        )

    return input_min, input_max, np.asarray(values, dtype=np.float64)

def interpolate_table(x, input_min, input_max, table):
    x = np.asarray(x, dtype=np.float64)
    position = (
        (x - input_min)
        / (input_max - input_min)
        * (len(table) - 1)
    )
    position = np.clip(position, 0.0, len(table) - 1)
    i0 = np.floor(position).astype(np.int64)
    i0 = np.minimum(i0, len(table) - 2)
    fraction = position - i0
    result = table[i0] * (1.0 - fraction) + table[i0 + 1] * fraction
    result[x >= input_max] = table[-1]
    result[x <= input_min] = table[0]
    return result

with CSV_PATH.open("r", encoding="utf-8") as file:
    rows = list(csv.DictReader(file))

stops = np.array([float(row["stops"]) for row in rows])
measurement = np.array(
    [float(row["measured_Z8_HLG_IRE"]) for row in rows]
)
theory = np.array(
    [float(row["calibrated_BT2100_HLG_IRE"]) for row in rows]
)

params = json.loads(PARAM_PATH.read_text(encoding="utf-8"))
E0 = params["linear_scale"]["E0"]
shadow_join = params["regions"]["shadow_linear_connection_end_stop"]
rolloff_start = params["regions"]["exact_HLG_theory_end_stop"]
measured_max_stop = params["regions"]["measured_rolloff_end_stop"]

input_min, input_max, table = read_cube(LUT_PATH)
plot_stops = np.linspace(-10.0, measured_max_stop, 3000)
linear_E = E0 * np.power(2.0, plot_stops)
lut_output = interpolate_table(
    linear_E, input_min, input_max, table
)

plt.figure(figsize=(12, 7))
plt.plot(
    stops,
    measurement,
    linewidth=1.5,
    label="Digitized Nikon Z8 / HLG measurement",
)
plt.plot(
    stops,
    theory,
    linewidth=1.3,
    label="Calibrated analytical HLG theory",
)
plt.plot(
    plot_stops,
    lut_output * 100.0,
    linewidth=2.0,
    label=LUT_PATH.name,
)
plt.axvline(
    shadow_join,
    linestyle="--",
    linewidth=1.0,
    label="Shadow/theory join",
)
plt.axvline(
    rolloff_start,
    linestyle="--",
    linewidth=1.0,
    label="Theory/rolloff join",
)
plt.axvline(
    measured_max_stop,
    linestyle="--",
    linewidth=1.0,
    label="Measured maximum",
)
plt.xlabel("Exposure relative to chart Stop 0 (stops)")
plt.ylabel("HLG signal / IRE (%)")
plt.title("Nikon Z8 HLG reverse-LUT fit check")
plt.xlim(-10.0, 6.0)
plt.ylim(0.0, 100.0)
plt.grid(True, alpha=0.3)
plt.legend(loc="upper left")
plt.tight_layout()
plt.savefig(OUTPUT_PATH, dpi=200)
plt.close()
print(OUTPUT_PATH)
