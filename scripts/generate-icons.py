#!/usr/bin/env python3
"""Generate symbolic 2x2 status icons for hyproled."""

from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "assets" / "icons"

# Exact layout produced by the GLSL expression in make_shader():
#
#   top:    GLSL positions 2 3
#   bottom: GLSL positions 0 1
#
# A mask is printed MSB-first (bits 3..0).
# Bit N represents GLSL position N.

PIXEL_PATHS = {
    0: "M12 12 L12 21.2 A9.2 9.2 0 0 1 2.8 12 Z",   # bottom-left
    1: "M12 12 L21.2 12 A9.2 9.2 0 0 1 12 21.2 Z",  # bottom-right
    2: "M12 12 L2.8 12 A9.2 9.2 0 0 1 12 2.8 Z",    # top-left
    3: "M12 12 L12 2.8 A9.2 9.2 0 0 1 21.2 12 Z",   # top-right
}

# Outer circular border. The inner subpath is cut out with even-odd fill.
OUTER_RING = (
    '<path id="outer-ring" class="foreground" fill-rule="evenodd" '
    'd="M12 1.5 A10.5 10.5 0 1 1 12 22.5 '
    'A10.5 10.5 0 1 1 12 1.5 Z '
    'M12 3 A9 9 0 1 0 12 21 A9 9 0 1 0 12 3 Z" />'
)

GRID_VERTICAL = (
    '<path id="grid-vertical" class="foreground" '
    'd="M11.35 3 H12.65 V21 H11.35 Z" />'
)

GRID_HORIZONTAL = (
    '<path id="grid-horizontal" class="foreground" '
    'd="M3 11.35 H21 V12.65 H3 Z" />'
)

ERROR_MARK = (
    '<path id="error-mark" class="foreground" '
    'd="M7.1 5.9 L12 10.8 L16.9 5.9 L18.1 7.1 '
    'L13.2 12 L18.1 16.9 L16.9 18.1 L12 13.2 '
    'L7.1 18.1 L5.9 16.9 L10.8 12 L5.9 7.1 Z" />'
)


def mask_for_state(phase: int, off_pixels: int) -> str:
    """Return the 4-bit mask for the shader's exact off-pixel predicate."""

    if phase not in range(4):
        raise ValueError("phase must be between 0 and 3")

    if off_pixels not in (1, 2, 3):
        raise ValueError("off_pixels must be between 1 and 3")

    bits = 0

    for pos in range(4):
        if (pos - phase) % 4 < off_pixels:
            bits |= 1 << pos

    return f"{bits:04b}"


def active_masks() -> list[str]:
    return sorted({
        mask_for_state(phase, off_pixels)
        for phase in range(4)
        for off_pixels in (1, 2, 3)
    })


def svg_document(mask: str | None = None, *, error: bool = False) -> str:
    nodes: list[str] = []

    if error:
        nodes.extend((OUTER_RING, ERROR_MARK))
    else:
        bits = int(mask, 2) if mask is not None else 0

        for pos, path_data in PIXEL_PATHS.items():
            if bits & (1 << pos):
                nodes.append(
                    f'<path id="pixel-{pos}" '
                    f'class="foreground" d="{path_data}" />'
                )

        nodes.extend((
            OUTER_RING,
            GRID_VERTICAL,
            GRID_HORIZONTAL,
        ))

    body = "\n  ".join(nodes)

    return (
        '<svg xmlns="http://www.w3.org/2000/svg" '
        'width="24" height="24" viewBox="0 0 24 24">\n'
        f'  {body}\n'
        '</svg>\n'
    )


def expected_files() -> dict[str, str]:
    files = {
        "hyproled-off.svg": svg_document(),
        "hyproled-error.svg": svg_document(error=True),
    }

    for mask in active_masks():
        files[f"hyproled-{mask}.svg"] = svg_document(mask)

    return dict(sorted(files.items()))


def check_files(files: dict[str, str]) -> bool:
    expected_names = set(files)
    actual_names = {
        path.name
        for path in OUTPUT_DIR.glob("hyproled-*.svg")
    }

    ok = True

    for name in sorted(expected_names - actual_names):
        print(f"missing: {OUTPUT_DIR / name}")
        ok = False

    for name in sorted(actual_names - expected_names):
        print(f"unexpected: {OUTPUT_DIR / name}")
        ok = False

    for name in sorted(expected_names & actual_names):
        actual = (OUTPUT_DIR / name).read_text(encoding="utf-8")

        if actual != files[name]:
            print(f"out of date: {OUTPUT_DIR / name}")
            ok = False

    if ok:
        print(f"OK: {len(files)} SVG icons match the generator")

    return ok


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument(
        "--check",
        action="store_true",
        help="verify generated icons without modifying files",
    )

    args = parser.parse_args()
    files = expected_files()

    if args.check:
        return 0 if check_files(files) else 1

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for name, content in files.items():
        (OUTPUT_DIR / name).write_text(content, encoding="utf-8")

    print(f"Generated {len(files)} SVG icons in {OUTPUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
