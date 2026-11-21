# Hyproled image-based exposure tests

This suite is a deterministic software model of the image signal produced by the current Hyproled shader. It is designed to stay in the repository and run in CI; it does not require a display server, OLED hardware, NumPy, Pillow, or other third-party Python packages.

## Run it

Run the complete test suite from the repository root:

```bash
python3 -m unittest discover -s tests -v
```

Generate a machine-readable report and a readable summary:

```bash
python3 tests/image_metrics.py \
  --json-report /tmp/hyproled-image-metrics.json \
  --markdown-report /tmp/hyproled-image-metrics.md
```

Validate that the checked-in PGM stimuli still match their deterministic generator:

```bash
python3 tests/fixtures/generate_images.py --check
```

The normal unittest discovery already executes this fixture check. The existing GitHub Actions workflow runs unittest discovery, so `test_image_metrics.py` is included automatically; no separate CI dependency is needed.

## What is measured

The test set contains nine small, deterministic grayscale PGM images: an isolated bright pixel, one-pixel horizontal and vertical lines, text-like glyphs, a geometric logo, a uniform bright rectangle, edge markers, a synthetic desktop UI, and a gradient scene.

For every fixture, the report measures:

- no-effect baseline;
- mask-only for `OFF_PIXELS=1,2,3`;
- Pixel Shift only for Fixed, Linear Horizontal, Linear Vertical, Orbit 2x2, and Orbit 3x3;
- combined Pixel Shift + mask for every mode and all three mask densities.

The model reads the actual `pixel_shift_mode_count()`, `pixel_shift_position()`, and `advance_active_effects()` Bash functions from `hyproled`. The test therefore exercises the production offset table and production combined-step schedule instead of maintaining a second copy of either. It also checks that the production GLSL still contains the sampling and mask expressions expected by the model.

## Metrics

- **Peak / source peak** — largest per-panel-pixel time-averaged grayscale signal divided by the source image peak. Lower means the brightest local signal is spread over more panel pixels or attenuated by the mask.
- **Effective pixels** — inverse concentration, `(sum(E)^2 / sum(E^2))`, over the full per-pixel average-exposure map. It estimates how many equally loaded pixels would produce the same total signal and concentration.
- **Support pixels** — number of physical output pixels receiving non-zero average signal during the simulated cycle.
- **Energy retained** — emitted grayscale signal divided by source grayscale signal, averaged over all states. It includes both mask attenuation and black out-of-bounds sampling.
- **Shift energy retained** — signal retained after Pixel Shift sampling but before applying the mask.
- **Mask energy retained** — emitted signal divided by the unmasked shifted signal. For a full four-phase cycle on even-sized fixtures it should be `1 - OFF_PIXELS/4`.
- **Edge loss** — signal lost to the current black out-of-bounds behavior before the mask is applied.
- **Support CV / Gini** — dispersion of average signal among pixels with non-zero average exposure. These complement peak and effective-area measurements; they are not burn-in scores.

Every scheduled state is weighted equally, corresponding to the current timer's equal dwell time. The combined schedule comes from the production shell function, including the adaptive mask-phase increments introduced in stage 5.

## Coordinate and mask contract

The shader evaluates `gl_FragCoord` at pixel centres. The model therefore uses `(x + 0.5, y + 0.5)` with the default OpenGL lower-left window origin. The mask's `2x2` bit mapping is derived from that exact expression. The `--status` mask class must use the same mapping so the Waybar SVG depicts the actual physical phase. The tests pin this contract and fail if the status mapping drifts away from the shader.

PGM rows are stored top-to-bottom by the file format; the loader reverses them into lower-left OpenGL coordinates before simulation. Pixel Shift sampling follows the production shader: output `(x,y)` samples input `(x-dx,y-dy)`, and out-of-bounds samples are black.

## Limits — important

These are signal-distribution metrics, **not measurements or predictions of OLED lifetime**. The model does not know the panel's subpixel current, spectral efficiency, temperature, compensation circuitry, local dimming behavior, automatic brightness limiting, or degradation chemistry. It also excludes the optional brightness-compensation setting. A grayscale PGM value is only a normalized input signal, not a calibrated current measurement.

The fixtures are deliberately synthetic and small. They cover geometries that expose algorithmic properties and regressions; they are not a representative sample of every desktop workload or a substitute for visual testing on the actual 3840x2160 panel. The report should be used to compare implementation behavior and catch regressions, not to claim a percentage increase in panel lifetime.

A change to the shader's sampling, mask formula, coordinate convention, state scheduler, or edge behavior must update or deliberately preserve these tests. Do not weaken the tests merely to make a changed result pass; explain the new behavior and revise the metric contract explicitly.
