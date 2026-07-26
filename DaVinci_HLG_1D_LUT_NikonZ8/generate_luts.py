#!/usr/bin/env python3
from pathlib import Path
import csv
import json
import math
import numpy as np
from scipy.interpolate import PchipInterpolator

ROOT = Path(__file__).resolve().parent
SIZE = 65536
A = 0.17883277
B = 1.0 - 4.0 * A
C = 0.5 - A * math.log(4.0 * A)

def hlg_oetf(E):
    E = np.asarray(E, dtype=np.float64)
    out = np.empty_like(E)
    low = E <= (1.0 / 12.0)
    out[low] = np.sqrt(3.0 * E[low])
    out[~low] = A * np.log(12.0 * E[~low] - B) + C
    return out

params = json.loads(
    (ROOT / "curve_model_parameters.json").read_text(encoding="utf-8")
)
E0 = params["linear_scale"]["E0"]
shadow_join_stop = params["regions"]["shadow_linear_connection_end_stop"]
rolloff_start_stop = params["regions"]["exact_HLG_theory_end_stop"]
measured_max_stop = params["regions"]["measured_rolloff_end_stop"]
measured_max_code = params["regions"]["measured_maximum_code"]
E_bypass_max = params["linear_scale"]["E_bypass_max"]
anchor_stops = np.asarray(params["rolloff_anchor_stops"])
anchor_codes = np.asarray(params["rolloff_anchor_codes"])
pchip = PchipInterpolator(anchor_stops, anchor_codes, extrapolate=False)

E_shadow = E0 * 2.0**shadow_join_stop
code_shadow = float(hlg_oetf(np.array([E_shadow]))[0])
E_measured_max = E0 * 2.0**measured_max_stop

def theory_from_stop(stops):
    return hlg_oetf(E0 * np.power(2.0, stops))

def code_from_stop(stops):
    stops = np.asarray(stops, dtype=np.float64)
    output = np.empty_like(stops)
    shadow = stops < shadow_join_stop
    output[shadow] = (
        code_shadow * np.power(2.0, stops[shadow] - shadow_join_stop)
    )
    theory = (
        (stops >= shadow_join_stop) & (stops <= rolloff_start_stop)
    )
    output[theory] = theory_from_stop(stops[theory])
    rolloff = (
        (stops > rolloff_start_stop) & (stops < measured_max_stop)
    )
    output[rolloff] = pchip(stops[rolloff])
    output[stops >= measured_max_stop] = measured_max_code
    return output

def linear_to_hlg(E):
    E = np.asarray(E, dtype=np.float64)
    output = np.empty_like(E)
    output[E <= 0.0] = 0.0
    shadow = (E > 0.0) & (E < E_shadow)
    output[shadow] = code_shadow * E[shadow] / E_shadow
    camera = (E >= E_shadow) & (E <= E_measured_max)
    output[camera] = code_from_stop(np.log2(E[camera] / E0))
    bypass = E > E_measured_max
    output[bypass] = (
        measured_max_code
        + (E[bypass] - E_measured_max)
        * (1.0 - measured_max_code)
        / (E_bypass_max - E_measured_max)
    )
    return output

def write_cube(path, title, domain_min, domain_max, values):
    with Path(path).open("w", encoding="ascii", newline="\n") as file:
        file.write(f'TITLE "{title}"\n')
        file.write(f"LUT_1D_SIZE {len(values)}\n")
        file.write(
            "LUT_1D_INPUT_RANGE "
            f"{domain_min:.17f} {domain_max:.17f}\n\n"
        )
        for value in values:
            text = f"{float(value):.17f}"
            file.write(f"{text} {text} {text}\n")

reverse_domain = np.linspace(0.0, E_bypass_max, SIZE)
reverse_table = linear_to_hlg(reverse_domain)
forward_domain = np.linspace(0.0, 1.0, SIZE)
indices = np.searchsorted(reverse_table, forward_domain, side="right") - 1
indices = np.clip(indices, 0, SIZE - 2)
fraction = (
    (forward_domain - reverse_table[indices])
    / (reverse_table[indices + 1] - reverse_table[indices])
)
forward_table = (
    reverse_domain[indices]
    + fraction * (reverse_domain[indices + 1] - reverse_domain[indices])
)
forward_table[0] = 0.0
forward_table[-1] = E_bypass_max

write_cube(
    ROOT / "HLG_to_Linear_1D_65536_LinToe_NikonZ8.cube",
    "Nikon Z8 HLG to Linear - 1D 65536 LinToe",
    0.0, 1.0, forward_table,
)
write_cube(
    ROOT / "Linear_to_HLG_1D_65536_NikonZ8.cube",
    "Linear to Nikon Z8 HLG - 1D 65536",
    0.0, E_bypass_max, reverse_table,
)
