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