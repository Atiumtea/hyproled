from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ICONS = ROOT / "assets" / "icons"
HYPROLED = ROOT / "hyproled"
GENERATOR = ROOT / "scripts" / "generate-icons.py"
SVG_NS = "{http://www.w3.org/2000/svg}"

# Position-to-geometry mapping. This is deliberately independent
# of the generator implementation.
EXPECTED_SECTOR_PREFIX = {
    0: "M12 12 L12 21.2",  # bottom-left, GLSL pos 0
    1: "M12 12 L21.2 12",  # bottom-right, GLSL pos 1
    2: "M12 12 L2.8 12",   # top-left, GLSL pos 2
    3: "M12 12 L12 2.8",  # top-right, GLSL pos 3
}


def mask_from_positions(positions: set[int]) -> str:
    bits = sum(1 << pos for pos in positions)
    return f"{bits:04b}"


def shader_mask(phase: int, off_pixels: int) -> str:
    disabled = {
        pos
        for pos in range(4)
        if (pos - phase) % 4 < off_pixels
    }

    return mask_from_positions(disabled)


def read_svg(name: str):
    return ET.parse(ICONS / name).getroot()


class IconGenerationTests(unittest.TestCase):
    def test_main_shader_formula_is_the_expected_source_of_truth(self):
        source = HYPROLED.read_text(encoding="utf-8")

        self.assertIn(
            "float pos = mod(fc.x, 2.0) + 2.0 * mod(fc.y, 2.0);",
            source,
        )

        self.assertIn(
            "bool off = mod(pos - float(${PHASE}), 4.0) < float(${OFF_PIXELS});",
            source,
        )

    def test_binary_bit_order(self):
        self.assertEqual(mask_from_positions({0}), "0001")
        self.assertEqual(mask_from_positions({0, 2}), "0101")
        self.assertEqual(mask_from_positions({3}), "1000")

    def test_exact_shader_table(self):
        expected = [
            ["0001", "0011", "0111"],
            ["0010", "0110", "1110"],
            ["0100", "1100", "1101"],
            ["1000", "1001", "1011"],
        ]

        actual = [
            [shader_mask(phase, count) for count in (1, 2, 3)]
            for phase in range(4)
        ]

        self.assertEqual(actual, expected)

    def test_exact_12_shader_masks_are_generated(self):
        expected = {
            shader_mask(phase, count)
            for phase in range(4)
            for count in (1, 2, 3)
        }

        self.assertEqual(len(expected), 12)

        actual = {
            path.stem.removeprefix("hyproled-")
            for path in ICONS.glob("hyproled-*.svg")
            if path.stem not in ("hyproled-off", "hyproled-error")
        }

        self.assertEqual(actual, expected)

    def test_each_svg_sector_matches_its_glsl_position(self):
        for phase in range(4):
            for count in (1, 2, 3):
                mask = shader_mask(phase, count)
                root = read_svg(f"hyproled-{mask}.svg")

                self.assertEqual(
                    root.attrib.get("viewBox"),
                    "0 0 24 24",
                )

                paths = {
                    element.attrib.get("id"): element
                    for element in root.iter(f"{SVG_NS}path")
                }

                bits = int(mask, 2)

                self.assertIn("outer-ring", paths)
                self.assertIn("grid-vertical", paths)
                self.assertIn("grid-horizontal", paths)

                for element in paths.values():
                    self.assertEqual(
                        element.attrib.get("class"),
                        "success",
                    )

                for pos, expected_prefix in EXPECTED_SECTOR_PREFIX.items():
                    path = paths.get(f"pixel-{pos}")
                    should_be_filled = bool(bits & (1 << pos))

                    self.assertEqual(
                        path is not None,
                        should_be_filled,
                        (mask, pos),
                    )

                    if path is not None:
                        self.assertTrue(
                            path.attrib["d"].startswith(expected_prefix),
                            (mask, pos, path.attrib["d"]),
                        )

    def test_off_and_error_icons(self):
        off_root = read_svg("hyproled-off.svg")
        error_root = read_svg("hyproled-error.svg")

        off = {
            element.attrib.get("id")
            for element in off_root.iter(f"{SVG_NS}path")
        }

        error = {
            element.attrib.get("id")
            for element in error_root.iter(f"{SVG_NS}path")
        }

        self.assertEqual(
            off,
            {"outer-ring", "grid-vertical", "grid-horizontal"},
        )

        self.assertEqual(
            error,
            {"outer-ring", "error-mark"},
        )

        self.assertEqual(
            {element.attrib.get("class")
             for element in off_root.iter(f"{SVG_NS}path")},
            {"warning"},
        )

        self.assertEqual(
            {element.attrib.get("class")
             for element in error_root.iter(f"{SVG_NS}path")},
            {"error"},
        )

    def test_generator_check_mode(self):
        result = subprocess.run(
            [sys.executable, str(GENERATOR), "--check"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )

        self.assertEqual(
            result.returncode,
            0,
            result.stdout + result.stderr,
        )


@unittest.skipUnless(
    shutil.which("jq"),
    "jq is required for hyproled --status tests",
)
class StatusMaskTests(unittest.TestCase):
    def test_status_mask_class_matches_shader_and_svg_names(self):
        with tempfile.TemporaryDirectory() as runtime_dir:
            state_dir = Path(runtime_dir) / "hyproled"
            state_dir.mkdir()

            state_path = state_dir / "state.json"

            env = os.environ.copy()
            env["XDG_RUNTIME_DIR"] = runtime_dir

            state = {
                "version": 2,
                "status": "active",
                "phase": 0,
                "offPixels": 1,
                "monitor": 0,
                "area": None,
                "invert": False,
                "brightnessOriginal": 100,
                "brightnessMax": 528,
                "brightnessApplied": 110,
                "brightnessDevice": "intel_backlight",
                "activeShader": "/tmp/hyproled-test.glsl",
                "previousShader": "",
                "compensationPercent": 10,
                "brightnessEnabled": True,
                "compensationPercentOfMaxByPixelCount": {
                    "1": 10,
                    "2": 20,
                    "3": 30,
                },
            }

            for phase in range(4):
                for count in (1, 2, 3):
                    state["phase"] = phase
                    state["offPixels"] = count

                    state_path.write_text(
                        json.dumps(state),
                        encoding="utf-8",
                    )

                    result = subprocess.run(
                        [str(HYPROLED), "--status"],
                        cwd=ROOT,
                        env=env,
                        text=True,
                        capture_output=True,
                    )

                    self.assertEqual(result.returncode, 0, result.stderr)

                    payload = json.loads(result.stdout)
                    expected_mask = shader_mask(phase, count)

                    self.assertIn(
                        f"mask-{expected_mask}",
                        payload["class"],
                    )

                    self.assertTrue(
                        (ICONS / f"hyproled-{expected_mask}.svg").is_file()
                    )


if __name__ == "__main__":
    unittest.main()
