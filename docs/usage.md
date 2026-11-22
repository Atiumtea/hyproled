# Usage

`hyproled` controls two independent effects in one Hyprland screen shader:

- **Mask** blacks out 1–3 pixels in each 2×2 output-pixel block. It can be limited to an area or inverted.
- **Pixel Shift** offsets the full image by an integer number of output pixels. It does not use the Mask area setting.

The shipped example configuration enables both effects.

## Common commands

| Command | Effect |
| --- | --- |
| `hyproled` | Apply the saved preferences and configured defaults. |
| `hyproled off` | Disable both effects, restore the previous screen shader, and restore the saved brightness baseline when compensation was active. |
| `hyproled --mask` / `--no-mask` | Enable or disable Mask without changing Pixel Shift. |
| `hyproled --pixel-shift` / `--no-pixel-shift` | Enable or disable Pixel Shift without changing Mask. |
| `hyproled --pixel-shift-mode MODE` | Select a Pixel Shift mode. |
| `hyproled --off-pixels N` | Enable Mask and disable N pixels per 2×2 block. |
| `hyproled --disabled-pixels N` | Set the Mask density without enabling Mask. |
| `hyproled --area x:y:w:h` | Restrict Mask to an output-pixel rectangle. |
| `hyproled --invert` / `--no-invert` | Enable or disable area inversion. |
| `hyproled --monitor ID` | Select the Hyprland monitor. |
| `hyproled --full-screen` | Clear the configured Mask area and use the full output. |
| `hyproled --brightness-compensation` / `--no-brightness-compensation` | Enable or disable optional Mask brightness compensation. |
| `hyproled --restore` | Restore saved effects after Hyprland starts. |
| `hyproled --status` | Print Waybar-compatible JSON status. |
| `hyproled --check-config` | Validate the configuration without applying effects. |
| `hyproled --version` | Print the installed version. |

Short aliases: `-a` (`--area`), `-i` (`--invert`), `-o` (`--off-pixels`), `-m` (`--monitor`), and `-s` (`--step`).

The `--monitor ID` option selects the Hyprland monitor. Area coordinates are shader/output-pixel coordinates, not logical layout coordinates.

## Pixel Shift modes

| Mode | Positions | Behaviour |
| --- | ---: | --- |
| `fixed` | 1 | Constant one-pixel offset. |
| `linear-horizontal` | 2 | Alternates horizontally. |
| `linear-vertical` | 2 | Alternates vertically. |
| `orbit-2x2` | 4 | Cycles through a 2×2 offset pattern. |
| `orbit-3x3` | 9 | Cycles through a 3×3 offset pattern. |

## Advancing effects

| Command | Behaviour |
| --- | --- |
| `hyproled --step` | Advance all active dynamic effects. `-s` is an alias. |
| `hyproled --mask-step` | Advance only the Mask phase. |
| `hyproled --shift-step` | Advance only the Pixel Shift position. The `fixed` mode has no next position. |

A timer or event hook is external to hyproled; the package does not install a scheduler. The appropriate interval has not been empirically established. See [known issues](known-issues.md#pixel-shift-scheduling-interval).

## Examples

Change Pixel Shift mode while keeping the current Mask setting:

```bash
hyproled --pixel-shift-mode orbit-3x3
```

Advance only Pixel Shift:

```bash
hyproled --shift-step
```

Run Pixel Shift without Mask:

```bash
hyproled --no-mask --pixel-shift
```

Inspect the current state:

```bash
hyproled --status | jq
```

For configuration fields and persistence paths, see [configuration](configuration.md). For Waybar setup, see [waybar](waybar.md).
