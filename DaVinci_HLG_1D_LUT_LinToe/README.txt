DaVinci Resolve HLG 1D LUT Linear-Toe package

FILES
- HLG_to_Linear_1D_65536_LinToe.cube
- Linear_to_HLG_1D_65536.cube
- validation_report.txt
- validation_report.json
- generate_luts.py
- SHA256SUMS.txt

TRANSFER FUNCTIONS
This package uses only the ITU-R BT.2100-3 HLG reference OETF and its inverse:
- Linear_to_HLG: relative scene-linear E -> non-linear HLG E'
- HLG_to_Linear: non-linear HLG E' -> relative scene-linear E

It does not include:
- HLG display EOTF
- OOTF
- system gamma
- display peak luminance scaling
- black-level lift
- gamut conversion
- RGB matrix operations
- white-point conversion
- tone mapping
- luma calculation
- channel mixing

DESIGN
Linear_to_HLG_1D_65536.cube is the standard HLG OETF sampled uniformly over
relative scene-linear E in the interval 0..1.

HLG_to_Linear_1D_65536_LinToe.cube is not sampled directly from the analytical
inverse OETF. It is sampled from the mathematical inverse of the reverse LUT's
piecewise-linear interpolation curve. This creates a linear toe corresponding
to the reverse LUT's first interval and makes the LUT pair as nearly inverse as
uniform 1D tables permit.

TOE RANGE
- Linear E: 0 .. 1.52590218966964218e-05
- HLG E':   0.00000000000000000e+00 .. 6.76587508679322731e-03

IMPORTANT CONSEQUENCE
Within the toe, the modified HLG-to-Linear LUT deliberately differs from the
standard analytical inverse OETF. Its purpose is pairwise round-trip consistency,
not exact scene-linear photometry in that very small interval.

Both LUTs:
- use LUT_1D_SIZE 65536
- use DOMAIN_MIN 0 and DOMAIN_MAX 1
- have identical R/G/B columns
- are generated in IEEE-754 float64
- serialize each table value with 17 digits after the decimal point.
