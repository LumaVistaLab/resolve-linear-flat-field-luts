#!/usr/bin/env python3
from pathlib import Path
import math
import numpy as np

SIZE = 65536
a = 0.17883277
b = 1.0 - 4.0 * a
c = 0.5 - a * math.log(4.0 * a)

def hlg_oetf(E):
    E = np.asarray(E, dtype=np.float64)
    out = np.empty_like(E)
    low = E <= (1.0 / 12.0)
    out[low] = np.sqrt(3.0 * E[low])
    out[~low] = a * np.log(12.0 * E[~low] - b) + c
    return out

def write_cube(path, title, values):
    with Path(path).open("w", encoding="ascii", newline="\n") as f:
        f.write(f'TITLE "{title}"\n')
        f.write(f"LUT_1D_SIZE {len(values)}\n")
        f.write("DOMAIN_MIN 0.00000000000000000 0.00000000000000000 0.00000000000000000\n")
        f.write("DOMAIN_MAX 1.00000000000000000 1.00000000000000000 1.00000000000000000\n\n")
        for value in values:
            s = f"{float(value):.17f}"
            f.write(f"{s} {s} {s}\n")

grid = np.linspace(0.0, 1.0, SIZE, dtype=np.float64)
reverse = hlg_oetf(grid)

forward = np.empty_like(grid)
below = grid <= reverse[0]
forward[below] = 0.0
indices = np.searchsorted(reverse, grid[~below], side="right") - 1
indices = np.clip(indices, 0, SIZE - 2)
fraction = (
    (grid[~below] - reverse[indices])
    / (reverse[indices + 1] - reverse[indices])
)
forward[~below] = (
    indices.astype(np.float64) + fraction
) / (SIZE - 1)
forward[-1] = 1.0

write_cube(
    "HLG_to_Linear_1D_65536_LinToe.cube",
    "HLG to Linear Scene E - 1D 65536 LinToe",
    forward,
)
write_cube(
    "Linear_to_HLG_1D_65536.cube",
    "Linear Scene E to HLG - 1D 65536",
    reverse,
)
