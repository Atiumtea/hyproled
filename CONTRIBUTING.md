# Contributing

Issues and focused pull requests are welcome. For a larger feature or a change to the CLI/configuration contract, open an issue first so the design can be discussed before implementation.

## Before changing code

- Keep each change focused; avoid unrelated refactoring.
- Preserve the separation between Mask and Pixel Shift and the single composed Hyprland screen shader.
- Treat runtime state, persistent preferences, shader restoration, and brightness rollback as safety-critical paths.
- Update user documentation when changing CLI options, configuration, or observable behavior.
- Do not edit generated icons or CSS manually. Change `scripts/generate-icons.py`, regenerate, and commit the outputs.
- Keep JSON Schema and runtime `jq` validation consistent.
- Do not present synthetic image metrics as measurements of OLED aging or panel lifetime.

## Local checks

Enter the development shell to get the project's Nix development tools:

```bash
nix develop
```

Run the same core checks used by CI:

```bash
bash -n ./hyproled
python3 -m unittest discover -s tests -v
python3 scripts/generate-icons.py --check
```

CI also runs ShellCheck, actionlint, workflow security analysis, and Nix package checks on `x86_64-linux` and `aarch64-linux`. ShellCheck can be run locally when installed:

```bash
shellcheck --shell=bash ./hyproled examples/*.sh
```

## Commits and pull requests

Use [Conventional Commits](https://www.conventionalcommits.org/), for example:

```text
feat: add a new Pixel Shift mode
fix: preserve brightness on shader restore
docs: describe the Waybar module
```

Use the usual types (`feat`, `fix`, `perf`, `docs`, `test`, `build`, `ci`, `chore`) and write the subject in the imperative. Mark breaking changes with `!` and/or a `BREAKING CHANGE:` footer.

Use a clear pull-request title. Pull requests are normally squash-merged, and the resulting commit title is consumed by Release Please. Do not edit `CHANGELOG.md`, bump `version.txt`, or create tags as part of an ordinary feature or fix pull request; see the [release process](.github/DEPLOYMENT.md).

A pull request should explain the reason for the change, user-visible behavior, and tests performed. Include relevant issue references and update documentation where needed.

## License

By submitting a contribution, you confirm that you have the right to submit it under the project's [BSD 3-Clause License](LICENSE). Preserve existing copyright and license notices.
