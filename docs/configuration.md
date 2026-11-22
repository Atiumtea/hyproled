# Configuration

The user configuration file is read from:

```text
${XDG_CONFIG_HOME:-~/.config}/hyproled/config.json
```

Set `HYPROLED_CONFIG` to use another path. The package installs `config.example.json` and `config.schema.json` under `share/hyproled`.

## Create and validate

Copy `config.example.json` from the installed package as described in [installation](installation.md), then validate it:

```bash
hyproled --check-config
```

The schema uses configuration format version `1`. Use `config.schema.json` as the editor schema; `--check-config` performs runtime validation through `jq`.

## Fields

| Path | Meaning |
| --- | --- |
| `defaults.disabledPixels` | Number of Mask pixels disabled in each 2×2 block; integer 1–3. |
| `defaults.monitor` | Hyprland monitor ID; non-negative integer. |
| `defaults.area` | `null` for the full output, or `x:y:w:h` for a Mask rectangle. |
| `defaults.invert` | Apply Mask outside the selected area. |
| `defaults.maskEnabled` | Enable Mask by default. |
| `defaults.pixelShift` | Enable Pixel Shift by default. |
| `defaults.pixelShiftMode` | `fixed`, `linear-horizontal`, `linear-vertical`, `orbit-2x2`, or `orbit-3x3`. |
| `defaults.pixelShiftIndex` | Initial position; valid range depends on the selected mode. |
| `defaults.phase` | Initial Mask phase, 0–3. |
| `brightness.enabled` | Enable optional Mask brightness compensation. |
| `brightness.device` | Device name accepted by `brightnessctl`. |
| `brightness.compensationPercentOfMaxByPixelCount` | Compensation percentage of the device maximum for 1, 2, or 3 disabled pixels. |

The shipped example enables both effects, selects `orbit-2x2`, and leaves brightness compensation disabled. Its compensation table is 10%, 20%, and 30% for 1, 2, and 3 disabled pixels respectively.

## Saved state

CLI selections are saved as user preferences in:

```text
${XDG_STATE_HOME:-~/.local/state}/hyproled/preferences.json
```

The active session and recovery information live in the runtime directory:

```text
$XDG_RUNTIME_DIR/hyproled/state.json
```

The runtime state is transient; preferences survive logouts and reboots. `hyproled off` disables the current session while keeping the saved preferences available for the next restore.

## Brightness compensation

Compensation is optional and applies only while Mask is enabled. Pixel Shift-only operation does not read or change brightness. The configured values are percentages of the backlight device's maximum, not percentages of measured panel luminance. They are heuristics and are not calibrated in nits; see [known issues](known-issues.md#brightness-compensation).
