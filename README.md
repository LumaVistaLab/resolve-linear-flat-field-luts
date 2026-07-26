# Resolve Linear Flat-Field LUTs

Language: English | [简体中文](README_zh-CN.md)

High-precision 1D transfer-function LUTs for converting PQ/HLG signals to and from linear light in DaVinci Resolve, intended for linear flat-field dust removal in video and time-lapse photography.

## Scope

Each LUT applies the same one-dimensional transfer function independently to the R, G, and B channels. The delivered tables have three identical, monotonic columns; they do not mix channels.

These LUTs perform only the documented transfer-function conversion:

- PQ/ST 2084 code values ↔ normalized linear light;
- standard HLG signal ↔ relative scene-linear light; or
- the repository's Nikon Z8 HLG model ↔ its paired linear representation.

They do **not** perform gamut conversion, RGB matrixing, white-point conversion, tone mapping, display transformation, HLG system-gamma/OOTF processing, white balance, exposure compensation, luma calculation, or creative grading.

The intended setup is an explicit node-based workflow in DaVinci Resolve with **Resolve Color Management (RCM) disabled**. These are not general-purpose creative LUTs and are not designed to turn camera material directly into a final display image.

Terminology used below:

- **PQ/ST 2084 code value** is the nonlinear signal defined by the ST 2084 transfer function.
- **HLG signal** is the nonlinear $E'$ signal associated with the documented HLG camera-side OETF model.
- **Linear light** is proportional to optical or scene-light quantity. Its normalization differs by package and must not be mixed.
- **Flat field** is a spatial map of the dust transmission, not a display-ready image.
- **Local Replacement** means the DaVinci Resolve tool used to reconstruct the dust-free reference area.
- **Round trip** means forward LUT → linear processing → matching reverse LUT.

## Core principle

Let:

- $S_t(x)$ be the ideal dust-free linear image at frame $t$;
- $T(x)$ be the transmission of dust fixed on the sensor or optical path; and
- $I_t(x)$ be the observed linear image.

The model is:

```math
I_t(x) = S_t(x)\,T(x)
```

In unaffected regions, $T(x)$ is close to $1$. In a dust-attenuated region:

```math
0 < T(x) < 1
```

For a reference frame, let $I_r(x)$ be the original dusty image and let the image reconstructed with Local Replacement approximate $S_r(x)$. Build the flat in linear light:

```math
F(x) = \frac{I_r(x)}{S_r(x)} \approx T(x)
```

Then correct any frame with:

```math
\begin{aligned}
\frac{I_t(x)}{F(x)}
&\approx \frac{S_t(x)\,T(x)}{T(x)} \\
&\approx S_t(x)
\end{aligned}
```

### What “fully adaptive” means

The flat-field image itself may be static. The correction nevertheless changes naturally with the current frame's linear brightness because it is a division by the multiplicative transmission map. No per-frame ROI statistics, brightness estimate, strength curve, or extra adaptive factor is required.

An alternative design that builds the flat in PQ code-value space and then adds a per-frame adaptive adjustment factor is **not** the workflow recommended by this repository.

## Why the flat must be made in linear light

Dust attenuation is modeled as multiplication in linear light. For a nonlinear encoding function `g`, in general:

```math
\frac{g(S\,T)}{g(S)} \ne T
```

Dividing PQ or HLG code values therefore does not reliably isolate the dust transmission. Both the dusty reference and the reconstructed reference must first use the same forward LUT and the same linear definition. The resulting flat must remain in that linear representation until it is used as the divisor.

The Local Replacement operation itself may still run on PQ/HLG code values in the proposed node order. In high-contrast regions, that nonlinear-domain reconstruction can introduce small differences; inspect the reference and final result.

## DaVinci Resolve workflow

The instructions below describe the required signal path. DaVinci Resolve's layer order and the precise definition of the **Divide** composite mode must be verified with the result; the labels “upper” and “lower” alone do not prove which image is the numerator.

### Stage A — Create the linear flat field

1. Create a flat-field timeline with Resolve Color Management disabled.
2. Stack the same PQ or HLG clip on two tracks.
3. Select a reference frame that can be reconstructed cleanly with Local Replacement.
4. On the Color page, use Local Replacement on the upper clip to remove the dust.
5. Immediately after that replacement node, apply the matching forward LUT:
   - PQ → Linear,
   - HLG → Linear, or
   - Nikon Z8 HLG → its paired Linear.
6. Apply the same forward LUT to the untouched reference on the lower track, so both layers use exactly the same linear representation.
7. On the Edit page, set the upper clip's composite mode to **Divide**.
8. Verify with scopes, known pixels, or a controlled test that the actual operation is the original dusty linear reference divided by the reconstructed dust-free linear reference, $\frac{I_r(x)}{S_r(x)}$.

   The expected flat is close to `1` in clean areas and typically below `1` in attenuated dust areas. If the reciprocal is produced, correct the layer/order setup before continuing.
9. On the Color page, grab a still of the verified flat.
10. Export the result as a high-precision TIFF. This TIFF is the linear flat field.

Do not apply the reverse LUT before exporting the flat.

### Stage B — Apply the linear flat field

1. Create the dust-removal timeline with Resolve Color Management disabled.
2. Put the original PQ or HLG material on the lower track.
3. Put the linear flat-field TIFF on the upper track and extend it over the full required duration.
4. On the Color page, apply the same package's forward LUT to the original material, converting it to linear light. The TIFF is already linear and must not receive this LUT again.
5. On the Edit page, set the flat-field layer's composite mode to **Divide**.
6. Verify that the effective calculation is the current dusty linear frame divided by the linear flat field, $\frac{I_t(x)}{F(x)}$.

7. At the timeline output, apply the matching reverse LUT to return the composite result to PQ or HLG.
8. Check final code values, black level, highlights, color, noise, and residual dust.

### Signal-path requirements

- Flat creation and flat application must use the **same linear definition**.
- Forward and reverse LUTs must come from the same package.
- Do not let the TIFF pass through an input color space, RCM, automatic color management, or another implicit transform.
- The flat and source must have identical resolution, crop, scaling, rotation, stabilization, and pixel registration.
- If the source undergoes a geometric operation, apply the exact same operation to the flat in the same coordinate system.
- Confirm the clip's data-level interpretation and the LUT placement with scopes before relying on the result.

## LUT versions

All eight delivered `.cube` files declare and contain 65,536 entries. Every entry has identical R/G/B values, so the LUTs are per-channel transfer functions rather than gamut transforms.

| Directory | Signal and linear definition | Delivered pair | Structure / dark strategy | Intended use and caution |
| --- | --- | --- | --- | --- |
| `DaVinci_ST2084_1D_LUT_65536` | PQ ↔ $Y=L/10{,}000$ | `ST2084_PQ_to_Linear_1D_65536.cube` + `Linear_to_ST2084_PQ_1D_65536.cube` | Uniform 65,536-point standard formula tables; input domain $[0,1]$ | Baseline choice when adherence to the sampled ST 2084 formula is preferred; finite-table interpolation causes a larger near-black round-trip deviation. |
| `DaVinci_ST2084_1D_LUT_LinToe` | PQ ↔ $Y=L/10{,}000$ | `ST2084_PQ_to_Linear_1D_65536_LinToe.cube` + `Linear_to_ST2084_PQ_1D_65536.cube` | Matched linear toe in the forward LUT; input domain $[0,1]$ | Better pairwise round-trip consistency through a full PQ → Linear → PQ chain; the toe intentionally differs from the continuous ST 2084 EOTF. |
| `DaVinci_HLG_1D_LUT_LinToe` | HLG $E'$ ↔ relative scene-linear $E$ | `HLG_to_Linear_1D_65536_LinToe.cube` + `Linear_to_HLG_1D_65536.cube` | BT.2100-3 reference OETF pair with a matched linear toe; input domain $[0,1]$ | General HLG source-side transfer workflow; not a display EOTF, OOTF, system-gamma transform, or HDR-to-SDR conversion. |
| `DaVinci_HLG_1D_LUT_NikonZ8` | Nikon Z8 HLG model ↔ package-specific linear $E$ | `HLG_to_Linear_1D_65536_LinToe_NikonZ8.cube` + `Linear_to_HLG_1D_65536_NikonZ8.cube` | Measured-chart-derived highlight model, matched inverse, and Resolve-specific input-range metadata | Use only with Nikon Z8 HLG material matching the model; it is not interchangeable with the general HLG package. |

### 1. ST 2084 / PQ — 65,536-point baseline

`DaVinci_ST2084_1D_LUT_65536` is generated directly from the ST 2084 EOTF and inverse EOTF in float64. Values are serialized with 17 digits after the decimal point.

- LUT size: `65536`
- Sampling: uniform over `0..1`
- Linear quantity: $Y=L/10{,}000$
- Forward range: PQ $N\in[0,1]$ → linear $Y\in[0,1]$
- Reverse range: linear $Y\in[0,1]$ → PQ, with the formula's first table value approximately $7.3095590258\times10^{-7}$
- Metadata: `DOMAIN_MIN 0 0 0` and `DOMAIN_MAX 1 1 1`

No additional extended range or clamping behavior is encoded. Host behavior outside the declared domain is not specified by the LUT.

The dense table reduces interpolation error over most of the range, but density alone does not make the two uniformly sampled nonlinear tables exact inverses near black. This package is the appropriate baseline when the sampled standard curve definition takes priority over the round-trip optimization described below.

### 2. ST 2084 / PQ — LinToe

`DaVinci_ST2084_1D_LUT_LinToe` retains the same reverse LUT as the baseline package; the two reverse files are byte-identical according to their SHA-256 manifests. Its forward LUT is sampled from the mathematical inverse of the reverse LUT's piecewise-linear interpolation curve.

The repository records the matched toe as:

- linear $Y$: $0\le Y\le1.5259021896696422\times10^{-5}$;
- equivalent luminance: $0\le L\le0.15259021896696423\ \mathrm{cd/m^2}$; and
- PQ $N$: approximately $7.3095590258\times10^{-7}\le N\le0.074287681119294$.

This improves `PQ → Linear → PQ` mutual inversion for the finite table. Inside the toe, however, the forward result is intentionally not point-for-point equal to the ideal continuous ST 2084 EOTF. “LinToe” means near-black inverse-pair optimization; it is not a creative contrast curve or a film-style toe.

### 3. General HLG — LinToe

`DaVinci_HLG_1D_LUT_LinToe` uses the ITU-R BT.2100-3 HLG reference OETF and its inverse only:

```math
E \longleftrightarrow E'
```

Both files use a `0..1` input domain. The reverse LUT is the standard OETF uniformly sampled over relative scene-linear `E`; the forward LUT is the inverse of that table's piecewise-linear interpolation. The documented toe corresponds to:

- linear $E$: $0\le E\le1.5259021896696422\times10^{-5}$;
- HLG $E'$: $0\le E'\le0.006765875086793227$.

This package deliberately excludes the display EOTF, OOTF, HLG system gamma, display peak-luminance scaling, black lift, gamut conversion, and tone mapping. It must not be described or used as a complete HLG display transform or HDR-to-SDR LUT.

### 4. Nikon Z8 HLG

`DaVinci_HLG_1D_LUT_NikonZ8` is a dedicated model for matching Nikon Z8 HLG material. It is not the default choice for general HLG footage.

The repository's reproducible model contains four regions:

1. A linear shadow connection from black to the theoretical HLG point at `-7.00` stops. The chart's approximately `2–3 IRE` floor is treated as a measurement/noise limit.
2. The analytical BT.2100 HLG OETF from `-7.00` to `+2.50` stops.
3. A monotonic PCHIP fit to the digitized Nikon Z8 highlight roll-off from `+2.50` to `+5.75` stops, ending at a modeled measured maximum of `97.00 IRE`.
4. A synthetic reversible bypass from HLG `0.97` to `1.00`. This preserves code values through the pair but is not claimed to represent camera exposure response above clipping.

The package defines:

```math
\begin{aligned}
E &= E_0\,2^{\mathrm{stops}}, \\
E_0 &= 0.04328874613391145
\end{aligned}
```

Its delivered metadata is intentionally different from the other packages:

- `HLG_to_Linear_1D_65536_LinToe_NikonZ8.cube` uses `LUT_1D_INPUT_RANGE 0 1` and outputs linear $E$ up to $2.4017386520303$.
- `Linear_to_HLG_1D_65536_NikonZ8.cube` uses `LUT_1D_INPUT_RANGE 0 2.4017386520303` and outputs HLG in $[0,1]$.
- Neither file contains `DOMAIN_MIN` or `DOMAIN_MAX`.

This is the corrected Resolve input-range form. The repository records that the earlier domain-tag form caused visible round-trip brightening, while the corrected pair has been concatenated and tested in DaVinci Resolve with the observed material code values unchanged. This test does not establish compatibility with every Nikon Z8 firmware, every HLG recording mode, other Nikon cameras, or arbitrary standard-HLG media.

The digitized source has 851 rows and comes from a raster chart rather than an original numerical measurement table. Fit accuracy is therefore limited by chart calibration, line thickness, resolution, and anti-aliasing. Thanks to **zxi / Huahua's Tech Road** for publishing the Nikon Z8 HLG measured response curve used as the source for this model; see [References](#references).

![Nikon Z8 HLG reverse-LUT fit check](DaVinci_HLG_1D_LUT_NikonZ8/NikonZ8_reverse_LUT_fit_check.png)

*Repository-generated comparison of the digitized Nikon Z8 measurement, calibrated analytical HLG theory, and the delivered reverse LUT. It documents the implemented fit; it is not an independent camera certification.*

## How to choose a version

```text
Input is PQ / ST 2084:
├─ Prefer the sampled standard curve definition → ST2084 65536
└─ Prefer stronger LUT-pair round-trip consistency → ST2084 LinToe

Input is HLG:
├─ General HLG material → HLG LinToe
└─ Matching Nikon Z8 HLG material → HLG NikonZ8
```

Never:

- mix the forward LUT from one directory with the reverse LUT from another;
- use the Nikon Z8 pair on unconfirmed general HLG material;
- use an HLG LUT on PQ material; or
- use a PQ LUT on HLG material.

## Installation

The most reliable installation path is the one DaVinci Resolve opens for the current installation:

1. Open DaVinci Resolve.
2. Open **Preferences** or **Project Settings**, then locate the **Color Management / Lookup Tables** controls. The exact location and label may vary by Resolve version.
3. Click **Open LUT Folder**.
4. Copy the required LUT directory, or keep and copy its two `.cube` files as a pair, into the opened user/system LUT location.
5. Return to Resolve and choose **Update Lists** / refresh the LUT list.
6. Confirm both directions appear in the Color page LUT browser.

OS paths are intentionally not hard-coded because they vary by Resolve version, installation method, and user configuration. Do not treat Resolve's hidden `.LUT` cache as the normal user installation folder.

## Usage notes

- Keep the pair together even where an identically named reverse LUT appears in another package.
- Verify the forward/reverse direction from the full filename; do not infer it from folder order.
- Preserve sufficient precision in the TIFF and throughout the node/composite path.
- Inspect the flat before use. Clean regions should be near `1`, not near `0`.
- Reject or repair a flat that contains zero, negative, NaN, infinite, or abnormal per-channel values. Division by a very small value can amplify noise dramatically.
- Test the actual Divide direction with a controlled image before processing a long timeline.
- Rebuild the flat when dust position, focal length, aperture, lens, sensor-cleaning state, or geometry changes.
- Keep color transforms and spatial processing in a deliberate order. A transform hidden in clip metadata, an input color space, RCM, or output setup can invalidate the assumed signal path.

## Limitations and known error sources

The method assumes that dust behaves approximately as a fixed spatial multiplicative attenuation. It can substantially reduce fixed sensor dust, but it cannot guarantee complete removal for every lens, scene, or processing chain.

The assumption can be weakened or broken by:

- local tone mapping;
- clarity, texture, or dehaze processing;
- sharpening and edge enhancement;
- spatial noise reduction;
- content-dependent demosaicing;
- highlight reconstruction;
- lens-vignetting correction;
- local exposure adjustment;
- stabilization, resampling, scaling, cropping, rotation, or other geometric changes;
- local nonlinear errors introduced by compression;
- complex nonlinear or spatial processing interpolated between time-lapse grading keyframes; and
- Local Replacement performed in PQ/HLG code-value space, especially across high-contrast edges.

Residual error generally comes from nonlinear or spatial processing that occurs after the dust attenuation is formed, imperfect reconstruction of the reference, flat-field noise, or loss of pixel registration. Very small flat values amplify noise and artifacts during division.

## Validation status

The following categories are intentionally separate:

| Category | Evidence in this repository | Status and limits |
| --- | --- | --- |
| Mathematical model | The multiplicative equations in this README | Valid under the fixed spatial transmission assumption; it is not proof that every real dust artifact follows the model exactly. |
| LUT file structure | Direct parsing of all 8 delivered `.cube` files | Confirmed: 65,536 declared and actual entries each, identical R/G/B columns, monotonic values, and the domains described above. |
| Numerical interpolation checks | Per-package `validation_report.txt` and `validation_report.json` | Reproducible repository checks using piecewise-linear LUT interpolation; they are not independent certification or blanket host-compatibility tests. |
| Practical flat-field workflow | Reported use of linear flat creation and application with PQ/HLG video and time-lapse material | Reported to provide substantially adaptive correction of fixed dust; complete removal is not guaranteed. |
| DaVinci Resolve round trip | Corrected Nikon Z8 forward/reverse pair | Tested in DaVinci Resolve; the tested material's code values were observed unchanged after the pair. |
| Broader Resolve/camera coverage | Other Resolve versions, GPUs, Nikon Z8 firmware/modes, other cameras, and out-of-domain values | Not verified by the included evidence. |

The repository's own interpolation reports record these maximum absolute round-trip errors:

| Package | Reported round trip | Maximum absolute error |
| --- | --- | ---: |
| ST2084 65536 | PQ → Linear → PQ | `2.2232094594546482e-2` PQ |
| ST2084 LinToe | PQ → Linear → PQ | `3.6975259488924994e-6` PQ |
| HLG LinToe | HLG → Linear → HLG | `2.8087143122178596e-6` HLG |
| Nikon Z8 | HLG → Linear → HLG, parsing delivered files with declared input ranges | `1.1309335427034384e-6` HLG |

These figures describe the repository's stated interpolation model. They should not be substituted for validation of a specific DaVinci Resolve version, GPU path, media data-level interpretation, or export codec.

## Repository layout

```text
.
├── DaVinci_HLG_1D_LUT_LinToe/
│   ├── HLG_to_Linear_1D_65536_LinToe.cube
│   ├── Linear_to_HLG_1D_65536.cube
│   ├── README.txt
│   ├── SHA256SUMS.txt
│   ├── generate_luts.py
│   ├── validation_report.json
│   └── validation_report.txt
├── DaVinci_HLG_1D_LUT_NikonZ8/
│   ├── HLG_to_Linear_1D_65536_LinToe_NikonZ8.cube
│   ├── Linear_to_HLG_1D_65536_NikonZ8.cube
│   ├── NikonZ8_reverse_LUT_fit_check.png
│   ├── README.txt
│   ├── SHA256SUMS.txt
│   ├── curve_model_parameters.json
│   ├── digitized_curve.csv
│   ├── generate_luts.py
│   ├── plot_reverse_lut_fit_check.py
│   ├── validation_report.json
│   └── validation_report.txt
├── DaVinci_ST2084_1D_LUT_65536/
│   ├── Linear_to_ST2084_PQ_1D_65536.cube
│   ├── ST2084_PQ_to_Linear_1D_65536.cube
│   ├── README.txt
│   ├── SHA256SUMS.txt
│   ├── generate_luts.py
│   ├── validation_report.json
│   └── validation_report.txt
├── DaVinci_ST2084_1D_LUT_LinToe/
│   ├── Linear_to_ST2084_PQ_1D_65536.cube
│   ├── ST2084_PQ_to_Linear_1D_65536_LinToe.cube
│   ├── README.txt
│   ├── SHA256SUMS.txt
│   ├── generate_luts.py
│   ├── validation_report.json
│   └── validation_report.txt
├── .gitignore
├── LICENSE
├── README.md
└── README_zh-CN.md
```

## References

1. [SMPTE ST 2084:2014 — High Dynamic Range Electro-Optical Transfer Function of Mastering Reference Displays](https://pub.smpte.org/latest/st2084/st2084-2014.pdf)
2. [ITU-R BT.2100-3 — Image parameter values for high dynamic range television](https://www.itu.int/rec/R-REC-BT.2100-3-202502-I/en)
3. zxi, Huahua's Tech Road: [Nikon Z8/Z9 HLG Deepdive | HLG 详解 VS N-LOG](https://zxi.mytechroad.com/blog/photography/nikon-z8-z9-hlg-deepdive-hlg-%E8%AF%A6%E8%A7%A3-vs-n-log/) — source of the Nikon Z8 measured response chart digitized for the package.

## License

This repository is distributed under the **GNU General Public License, Version 3**. See [LICENSE](LICENSE); the full license text is not duplicated here.

## Disclaimer

This is an independent project and is not an official Blackmagic Design, Nikon, Dolby, ITU, or SMPTE product. Product names and trademarks belong to their respective owners.

The LUTs and workflow are provided without a guarantee of lossless conversion, absolute accuracy, universal compatibility, or complete dust removal. Validate the full signal path on representative copies of your own media before production use.
