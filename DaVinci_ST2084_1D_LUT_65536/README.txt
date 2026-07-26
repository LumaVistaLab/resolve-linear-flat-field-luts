DaVinci Resolve ST 2084 PQ / Linear 1D LUT package

FILES
- ST2084_PQ_to_Linear_1D_65536.cube
- Linear_to_ST2084_PQ_1D_65536.cube

DESIGN
- 65,536 uniformly spaced samples over 0..1.
- One entry for every point of an unsigned 16-bit grid.
- Identical R/G/B columns; channels remain independent.
- Generated directly from the ST 2084 equations in float64.
- Each value is serialized with 17 digits after the decimal point.
- Linear quantity: Y=L/10000.
- No gamut conversion, RGB matrix, white-point conversion, tone mapping,
  OOTF, luma calculation, channel mixing, or creative grading.

The 0..1 DOMAIN_MIN/DOMAIN_MAX values define the table sampling interval.
They do not define the general numeric range of DaVinci Resolve Color nodes.

See validation_report.txt and validation_report.json for interpolation and
round-trip measurements.
