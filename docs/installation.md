# Installation

## Requirements

- Linux with a running Hyprland session and `hyprctl` available in that session.
- Bash, `jq`, and `flock` from util-linux. The Nix package supplies these runtime tools.
- `brightnessctl` only when brightness compensation is enabled.

The flake package is built and tested on `x86_64-linux` and `aarch64-linux`.

## Nix flake

Try the CLI without installing it:

```bash
nix run github:Atiumtea/hyproled/v0.4.0#hyproled -- --help
```

Install the stable release into the current Nix profile:

```bash
nix profile install github:Atiumtea/hyproled/v0.4.0#hyproled
```

For a flake-based system configuration, pin the release and follow your existing nixpkgs input:

```nix
inputs.hyproled = {
  url = "github:Atiumtea/hyproled/v0.4.0";
  inputs.nixpkgs.follows = "nixpkgs";
};
```

### NixOS module

Import the module and enable the program:

```nix
{ inputs, ... }: {
  imports = [ inputs.hyproled.nixosModules.default ];
  programs.hyproled.enable = true;
}
```

The module adds the flake package to `environment.systemPackages`. It does not create a hyproled configuration file or configure Hyprland autostart. Pass `inputs` to the module through `specialArgs = { inherit inputs; };` in your `nixosSystem` definition.

### Home Manager

There is no dedicated Home Manager module. Install the flake package through `home.packages`:

```nix
{ inputs, pkgs, ... }: {
  home.packages = [
    inputs.hyproled.packages.${pkgs.system}.default
  ];
}
```

Pass `inputs` to your Home Manager modules using `extraSpecialArgs` if it is not already available there.

### Non-flake Nix

A standalone `default.nix` or `package.nix` is not provided. Direct `nix-build`/`nix-env -f` packaging without flakes is therefore not supported yet. The current Nix interface is the flake package and its NixOS module.

## First configuration

The installed package includes `config.example.json` and `config.schema.json` under `share/hyproled`. Copy the example into the user configuration directory:

```bash
hyproled_bin="$(readlink -f "$(command -v hyproled)")"
hyproled_share="${hyproled_bin%/bin/hyproled}/share/hyproled"
install -Dm600 "$hyproled_share/config.example.json" \
  "${XDG_CONFIG_HOME:-$HOME/.config}/hyproled/config.json"
```

Validate it before enabling effects:

```bash
hyproled --check-config
```

To restore saved preferences when Hyprland starts, add this to `hyprland.conf`:

```ini
exec-once = hyproled --restore
```

See [configuration](configuration.md) and [usage](usage.md) for the available options.
