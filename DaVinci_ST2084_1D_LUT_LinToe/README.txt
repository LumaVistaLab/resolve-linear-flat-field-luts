DaVinci Resolve ST 2084 1D LUT Linear-Toe package

FILES
- ST2084_PQ_to_Linear_1D_65536_LinToe.cube
- Linear_to_ST2084_PQ_1D_65536.cube
- validation_report.txt
- validation_report.json
- generate_luts.py
- SHA256SUMS.txt

DESIGN
The reverse LUT remains the 65,536-point uniformly sampled ST 2084 inverse EOTF.
The forward LUT is sampled from the mathematical inverse of the reverse LUT's
piecewise-linear interpolation curve. This creates a linear toe matching the
reverse LUT's first interval and improves pairwise round-trip consistency.

TOE RANGE
- Linear Y: 0 .. 1.52590218966964218e-05
- Luminance: 0 .. 0.152590218967 cd/m^2
- PQ N: 7.30955902578396646e-07 .. 7.42876811192939718e-02

IMPORTANT
Below the toe boundary, the modified forward LUT intentionally departs from the
standard ST 2084 EOTF. It is optimized for mutual inversion with the reverse LUT,
not for photometrically exact intermediate linear-light values.

Both LUTs use LUT_1D_SIZE 65536, DOMAIN_MIN 0, DOMAIN_MAX 1, and identical
R/G/B columns. No gamut conversion, matrix, white-point conversion, tone mapping,
OOTF, luma calculation, or channel mixing is included.
