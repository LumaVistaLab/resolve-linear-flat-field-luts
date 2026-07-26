DaVinci Resolve Nikon Z8/Z-system HLG 1D LUT package

LUT FILES
- HLG_to_Linear_1D_65536_LinToe_NikonZ8.cube
- Linear_to_HLG_1D_65536_NikonZ8.cube

CHECK AND REPRODUCTION FILES
- NikonZ8_reverse_LUT_fit_check.png
- plot_reverse_lut_fit_check.py
- digitized_curve.csv
- curve_model_parameters.json
- validation_report.txt
- validation_report.json
- generate_luts.py
- SHA256SUMS.txt

SOURCE CURVE
https://zxi.mytechroad.com/blog/photography/nikon-z8-z9-hlg-deepdive-hlg-%E8%AF%A6%E8%A7%A3-vs-n-log/

SCOPE
Only the camera-side HLG transfer is represented.
No display EOTF, OOTF, system gamma, display luminance scaling, gamut
conversion, RGB matrix, white-point conversion, tone mapping, luma
calculation, or channel mixing is included.

MODEL
1. Black to -7.00 stops:
   Linear connection to the theoretical HLG point. The chart's approximately
   2-3 IRE shadow floor is treated as a measurement/noise limit.

2. -7.00 to 2.50 stops:
   Exact analytical BT.2100 HLG OETF. The blue raster line is not fitted here.

3. 2.50 to 5.75 stops:
   Strictly monotonic PCHIP fit to the digitized Nikon Z8 highlight rolloff.
   Theory support anchors immediately before the handoff keep the transition
   smooth.

4. Measured maximum:
   97.00 IRE at approximately
   5.75 stops.

5. HLG 0.97 to 1.00:
   Compact synthetic reversible bypass. It preserves existing code values but
   is not claimed to represent Nikon exposure response above clipping.

LINEAR SCALE
E = E0 * 2^stops
E0 = 0.04328874613391145

HLG_to_Linear LUT domain: HLG 0..1
Linear_to_HLG LUT domain: E 0..2.40173865203029990

LUT PAIR CONSTRUCTION
Linear_to_HLG_1D_65536_NikonZ8.cube samples the composite curve uniformly in
its declared linear input domain.

HLG_to_Linear_1D_65536_LinToe_NikonZ8.cube is sampled from the inverse of the
reverse LUT's actual piecewise-linear interpolation curve. This maximizes
pairwise round-trip consistency.

LIMITATION
The source is a 1024x688 raster chart rather than an original numerical
measurement table. Highlight fit accuracy is limited by chart calibration,
line thickness, resolution, and anti-aliasing. The CSV, parameter JSON,
validation report, plotting script, and generated fit-check image expose the
assumptions for inspection.


RESOLVE INPUT-RANGE FIX
The original package used DOMAIN_MIN / DOMAIN_MAX tags. DaVinci Resolve did
not apply the extended reverse-LUT input domain as intended, causing the
NikonZ8 pair to brighten on round-trip.

This revision uses:

  HLG_to_Linear_1D_65536_LinToe_NikonZ8.cube
  LUT_1D_INPUT_RANGE 0.00000000000000000 1.00000000000000000

  Linear_to_HLG_1D_65536_NikonZ8.cube
  LUT_1D_INPUT_RANGE 0.00000000000000000 2.40173865203029990

The LUT table values, Nikon Z8 highlight fit, shadow policy, LinToe inverse,
and 0.97..1.00 bypass model are otherwise unchanged.
