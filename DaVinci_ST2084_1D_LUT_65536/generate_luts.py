#!/usr/bin/env python3
from pathlib import Path
import numpy as np

SIZE=65536
m1=2610.0/16384.0
m2=2523.0/32.0
c1=3424.0/4096.0
c2=2413.0/128.0
c3=2392.0/128.0

def eotf(x):
    p=np.power(x,1.0/m2)
    return np.power(np.maximum(p-c1,0.0)/(c2-c3*p),1.0/m1)

def inv_eotf(y):
    p=np.power(y,m1)
    return np.power((c1+c2*p)/(1.0+c3*p),m2)

def write_cube(path,title,values):
    with Path(path).open("w",encoding="ascii",newline="\n") as f:
        f.write(f'TITLE "{title}"\nLUT_1D_SIZE {len(values)}\n')
        f.write("DOMAIN_MIN 0.00000000000000000 0.00000000000000000 0.00000000000000000\n")
        f.write("DOMAIN_MAX 1.00000000000000000 1.00000000000000000 1.00000000000000000\n\n")
        for v in values:
            s=f"{float(v):.17f}"
            f.write(f"{s} {s} {s}\n")

x=np.linspace(0.0,1.0,SIZE,dtype=np.float64)
write_cube("ST2084_PQ_to_Linear_1D_65536.cube","ST2084 PQ to Linear Y=L/10000 - 1D 65536",eotf(x))
write_cube("Linear_to_ST2084_PQ_1D_65536.cube","Linear Y=L/10000 to ST2084 PQ - 1D 65536",inv_eotf(x))
