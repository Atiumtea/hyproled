# Recording demos

The README should show short captures of the actual utility, not the inherited upstream animation. Record the desktop on a real Hyprland session; the repository's image fixtures are test data, not demo footage.

## Capture

On Nix, the capture tools can be run without installing them globally:

```bash
nix shell nixpkgs#wl-screenrec nixpkgs#slurp nixpkgs#ffmpeg
```

Select a region and record a short clip:

```bash
wl-screenrec -g "$(slurp)" --max-fps 12 -f /tmp/hyproled-demo.mp4
```

Stop recording with `Ctrl+C`. `wl-screenrec` supports region selection through `slurp` and lists Hyprland among its supported compositors; it requires a compatible Wayland capture protocol and hardware video-encoding support. If it cannot capture on the current setup, use OBS with the Hyprland PipeWire portal.

## Convert to GIF

Create the destination directory, then generate a clip-specific palette before quantizing the video:

```bash
mkdir -p assets/demos
ffmpeg -i /tmp/hyproled-demo.mp4 \
  -filter_complex \
  "[0:v]fps=12,scale=960:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=128[p];[b][p]paletteuse=dither=bayer:bayer_scale=3" \
  -loop 0 assets/demos/hyproled-demo.gif
```

Keep clips short and crop to the relevant UI. A useful pair is one clip showing Mask phase and Pixel Shift movement, and another showing the Waybar icon/tooltip changing with the state. Avoid notifications, private windows, and unnecessary desktop chrome. Check the resulting file size and readability before adding it to the README.

The palette pipeline uses FFmpeg's `palettegen` and `paletteuse` filters; see the [FFmpeg filter documentation](https://ffmpeg.org/ffmpeg-filters.html#palettegen) and [wl-screenrec README](https://github.com/rosalyntg/wl-screenrec).
