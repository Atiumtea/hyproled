# Waybar

`hyproled --status` prints JSON for a Waybar custom module. The module can poll the state and receive an update signal after a successful change.

## Module

Add this to the Waybar configuration:

```json
"custom/hyproled": {
  "exec": "hyproled --status",
  "return-type": "json",
  "interval": 1,
  "signal": 10,
  "format": " ",
  "tooltip": true
}
```

`signal: 10` registers Waybar for `SIGRTMIN+10`, which hyproled uses to notify the module after changing its state. The one-second interval also refreshes status if another process changes the runtime state.

## Icons and CSS

The package installs the generated icons and `waybar-icons.css` under `share/hyproled`. The CSS contains the placeholder `@HYPROLED_ICON_DIR@`; replace it with the absolute installed icon directory before importing the stylesheet.

For a Nix profile installation:

```bash
config_home="${XDG_CONFIG_HOME:-$HOME/.config}"
mkdir -p "$config_home/waybar"
hyproled_bin="$(readlink -f "$(command -v hyproled)")"
hyproled_share="${hyproled_bin%/bin/hyproled}/share/hyproled"
sed "s|@HYPROLED_ICON_DIR@|${hyproled_share}/icons|g" \
  "$hyproled_share/waybar-icons.css" \
  > "$config_home/waybar/hyproled-icons.css"
```

Import the resulting file from your Waybar stylesheet:

```css
@import "hyproled-icons.css";
```

The module name `custom/hyproled` matches the CSS selector `#custom-hyproled`. The generated CSS and SVGs are build assets; do not edit them by hand. Regenerate them with `python3 scripts/generate-icons.py` and verify with `python3 scripts/generate-icons.py --check`.

The icon set shows the current Mask pattern and Pixel Shift direction. Physical direction was checked on one OLED panel; other displays may have a different apparent orientation. See [known issues](known-issues.md#waybar-icon-orientation).
