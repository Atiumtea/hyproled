# Known Issues and Compatibility Notes

This document describes confirmed issues and relevant compatibility
limitations affecting hyproled.

It is intended to document reproducible behavior and platform-specific
constraints, not development plans or environment-specific configuration.

## 1. Pixel Shift and Hyprland damage tracking

**Status:** Confirmed  
**Affected component:** Pixel Shift  
**Platform:** Hyprland screen shader

Pixel Shift modifies texture sampling coordinates to shift the rendered
image. Hyprland's partial damage tracking does not account for this
coordinate offset when restricting the final screen shader pass.

As a result, some output pixels may remain stale after partial redraws.
This can appear as thin vertical seams through which previously rendered
framebuffer content becomes visible.

The issue was reproduced on Hyprland 0.53.3 with Pixel Shift enabled.

### Workaround

Use monitor-wide damage tracking:

```ini
debug {
    damage_tracking = 1
}
````

This causes the entire monitor to be invalidated whenever a frame needs to be rendered, while retaining the ability to skip rendering when nothing has changed.

This increases rendering workload compared with partial damage tracking. The setting is global to Hyprland and may affect all connected monitors.

Values `0` and `1` are not equivalent:

- `0`: disables damage tracking and may cause continuous full redraws.
- `1`: uses monitor-wide invalidation when rendering is required.
- `2`: uses partial damage regions and can cause artifacts with Pixel Shift.

Compatibility should be rechecked when changing Hyprland versions.

## 2. Single screen shader limitation

Status: Platform limitation\
Affected component: Shader management\
Platform: Hyprland

Hyprland exposes a single `decoration:screen_shader` option.

hyproled combines its own effects into one shader, but cannot automatically compose arbitrary third-party screen shaders.

The utility preserves the previously configured shader and restores it when disabled.

If another application changes the active screen shader while hyproled is running, hyproled will not overwrite that external shader blindly.

Running multiple independent applications that modify the screen shader is therefore not supported.

## 3. Waybar status icon coverage

Status: Known limitation Affected component: Optional Waybar integration

The existing SVG icon set represents the 2x2 pixel mask and its phases.

It does not yet provide complete visual representation of all runtime effect combinations, particularly Pixel Shift-only operation.

The textual status and tooltip provide additional information and should be used when the icon alone does not accurately describe the active effects.

## 4. Brightness compensation calibration

Status: Hardware-dependent limitation\
Affected component: Brightness compensation

Brightness compensation currently uses values exposed through the\
Linux backlight interface.

These values are not direct measurements of physical display luminance and cannot be interpreted as nits.

The compensation percentages are configurable heuristics, not photometrically calibrated values for individual OLED panels.

Actual luminance preservation and any reduction in differential OLED aging have not been established through measurements.

## 5. Effectiveness model limitations

**Status:** Known limitation  
**Affected component:** Image-based effectiveness tests  
**Platform:** CPU-side simulation and synthetic grayscale fixtures

The image-based tests evaluate the spatial distribution of normalized grayscale input signal across Pixel Shift and mask states. They are useful for comparing algorithmic behavior and detecting regressions, but they are not a physical OLED aging model.

The tests obtain Pixel Shift offsets and combined phase/index transitions from the production Bash functions. However, image sampling and exposure accumulation are performed by a separate Python CPU model. The production GLSL is checked for expected expressions, but the shader is not executed on a GPU.

### Scope and limitations

- The fixtures are nine small synthetic grayscale PGM images. They cover selected geometric patterns and UI-like content, but are not a representative sample of desktop workloads or a substitute for testing on the actual 3840×2160 panel.
- The model evaluates integer texel translation, the current black out-of-bounds behavior, and the mask formula. It does not model area/invert clipping or the optional brightness-compensation setting.
- RGB subpixel structure, subpixel current, electrical charge, calibrated luminance, gamma/transfer characteristics, temperature, automatic brightness limiting, panel compensation circuitry, and OLED degradation chemistry are not represented.
- Edge-loss measurements are affected by the deliberately small fixture dimensions and must not be directly extrapolated to the full panel.
- Metrics such as peak exposure, effective pixels, support, and energy retention describe simulated signal distribution. They are not calibrated burn-in scores or measurements of OLED lifetime improvement.

## 6. Pixel Shift scheduling interval validation

**Status:** Not empirically validated  
**Affected component:** Automatic Pixel Shift scheduler  
**Platform:** systemd user timer

The effectiveness model assigns equal dwell time to every scheduled state and evaluates complete state cycles. It does not model the temporal behavior of OLED degradation or determine how the actual interval between state transitions affects panel aging.

Consequently, the model cannot establish an optimal timer interval or quantify the effect of changing it. The current 15-minute interval is an operational configuration, not an experimentally established optimum for the ThinkPad OLED panel or OLED displays in general.

No interval recommendation should be treated as a conclusion of the current effectiveness tests.