# hyproled

[![CI](https://github.com/Atiumtea/hyproled/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/Atiumtea/hyproled/actions/workflows/ci.yml) [![Release](https://img.shields.io/github/v/release/Atiumtea/hyproled?display_name=tag&label=latest%20release)](https://github.com/Atiumtea/hyproled/releases/latest) [![License](https://img.shields.io/github/license/Atiumtea/hyproled)](LICENSE)

A Hyprland screen-shader utility for experimental OLED burn-in mitigation. `hyproled` combines two independent effects in one shader: a configurable 2×2 pixel **Mask** and full-frame **Pixel Shift**.

It can preserve effect preferences, restore the previously active screen shader, optionally compensate brightness, and expose its state to Waybar. It does not guarantee burn-in prevention or a measurable increase in panel lifetime.

## Releases and support

| Track | Status |
| --- | --- |
| [Latest stable release](https://github.com/Atiumtea/hyproled/releases/latest) · [![Latest release](https://img.shields.io/github/v/release/Atiumtea/hyproled?display_name=tag&label=stable)](https://github.com/Atiumtea/hyproled/releases/latest) | Supported |
| [`main`](https://github.com/Atiumtea/hyproled/tree/main) | Development; may change without notice |
| Previous release tags | Available, but not maintained |

Only the latest stable release receives fixes. Release notes are in the [changelog](CHANGELOG.md) and [GitHub Releases](https://github.com/Atiumtea/hyproled/releases).

## Install with Nix

The flake provides packages for `x86_64-linux` and `aarch64-linux`, plus a NixOS module.

```bash
nix profile install github:Atiumtea/hyproled/v0.4.0#hyproled
```

See [installation](docs/installation.md) for NixOS, Home Manager, and current non-flake limitations.

## Quick start

Create `config.json` from the shipped `config.example.json`, validate it, then run:

```bash
hyproled --check-config
hyproled
hyproled --step
hyproled off
```

To restore saved preferences after Hyprland starts, add `exec-once = hyproled --restore` to your Hyprland configuration.

## Documentation

- [Installation and Nix integration](docs/installation.md)
- [CLI and effects](docs/usage.md)
- [Configuration](docs/configuration.md)
- [Waybar](docs/waybar.md)
- [Known issues](docs/known-issues.md)
- [Image-test methodology and limits](tests/IMAGE_METRICS.md)
- [Contributing](CONTRIBUTING.md)
- [Release process](.github/DEPLOYMENT.md)
- [Recording demos](docs/demo-recording.md)

## Support

Report bugs and request features in [GitHub Issues](https://github.com/Atiumtea/hyproled/issues). Include the hyproled version, Hyprland version, steps to reproduce, relevant logs, and a sanitized configuration.

## Attributions

This project began as a fork of [mklan/hyproled](https://github.com/mklan/hyproled). The original implementation and its contributions remain credited to mklan. This fork extends that work; it is not affiliated with or endorsed by the original author.

Licensed under the [BSD 3-Clause License](LICENSE).
