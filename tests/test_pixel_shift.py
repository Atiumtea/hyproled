from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HYPROLED = ROOT / "hyproled"
SOURCE = HYPROLED.read_text(encoding="utf-8")


class CompositeShaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        match = re.search(
            r"(?ms)^make_shader\(\) \{\n.*?^\}",
            SOURCE,
        )
        if match is None:
            raise AssertionError("make_shader() was not found")
        cls.function = match.group(0)

    def generate(self, mask, shift, path, dx=1, dy=0):
        script = (
            self.function
            + "\nMONITOR=0\n"
            + "PHASE=0\n"
            + "OFF_PIXELS=1\n"
            + f"MASK_ENABLED={'true' if mask else 'false'}\n"
            + f"PIXEL_SHIFT={'true' if shift else 'false'}\n"
            + f"PIXEL_SHIFT_DX={dx}\n"
            + f"PIXEL_SHIFT_DY={dy}\n"
            + 'AREA=""\n'
            + "INVERT=false\n"
            + 'make_shader "$1"\n'
        )

        result = subprocess.run(
            ["bash", "-c", script, "hyproled-test", str(path)],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return path.read_text(encoding="utf-8")

    def test_mask_only(self):
        with tempfile.TemporaryDirectory() as directory:
            shader = self.generate(
                True, False, Path(directory) / "mask.frag"
            )

        self.assertIn("vec4 orig = texture(tex, v_texcoord);", shader)
        self.assertIn("bool off =", shader)
        self.assertNotIn("texelFetch(tex, sourceTexel, 0)", shader)

    def test_pixel_shift_only(self):
        with tempfile.TemporaryDirectory() as directory:
            shader = self.generate(
                False, True, Path(directory) / "shift.frag"
            )

        self.assertIn("texelFetch(tex, sourceTexel, 0)", shader)
        self.assertIn("sourceTexel.x < 0", shader)
        self.assertIn("sourceTexel.y < 0", shader)
        self.assertIn("orig = vec4(0.0, 0.0, 0.0, 1.0);", shader)
        self.assertNotIn("bool off =", shader)
        self.assertIn("fragColor = orig;", shader)

    def test_combined_effects(self):
        with tempfile.TemporaryDirectory() as directory:
            shader = self.generate(
                True, True, Path(directory) / "combined.frag"
            )

        self.assertIn("texelFetch(tex, sourceTexel, 0)", shader)
        self.assertIn("bool off =", shader)

    def test_mask_uses_output_coordinates(self):
        with tempfile.TemporaryDirectory() as directory:
            shader = self.generate(
                True, True, Path(directory) / "combined.frag"
            )

        self.assertIn("vec2 fc = gl_FragCoord.xy;", shader)
        self.assertIn(
            "float pos = mod(fc.x, 2.0) + 2.0 * mod(fc.y, 2.0);",
            shader,
        )

    def test_fixed_shift_uses_one_physical_texel(self):
        with tempfile.TemporaryDirectory() as directory:
            shader = self.generate(
                False, True, Path(directory) / "shift.frag", dx=1, dy=0
            )

        self.assertIn("textureSize(tex, 0)", shader)
        self.assertIn(
            "ivec2 sourceTexel = texel - ivec2(1, 0);",
            shader,
        )

    def test_zero_offset_keeps_the_original_sampling_path(self):
        with tempfile.TemporaryDirectory() as directory:
            shader = self.generate(
                False, True, Path(directory) / "zero.frag", dx=0, dy=0
            )

        self.assertIn("vec4 orig = texture(tex, v_texcoord);", shader)
        self.assertNotIn("texelFetch", shader)

    def test_cli_help_documents_both_options(self):
        result = subprocess.run(
            ["bash", str(HYPROLED), "-h"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("--pixel-shift", result.stdout)
        self.assertIn("--no-pixel-shift", result.stdout)
        self.assertIn("--pixel-shift-mode", result.stdout)
        self.assertIn("--shift-step", result.stdout)

        # The parser must preserve ordinary options after consuming a mode value.
        parser_regression = subprocess.run(
            ["bash", str(HYPROLED), "--pixel-shift-mode", "orbit-3x3", "-z"],
            cwd=ROOT, text=True, capture_output=True,
        )
        self.assertNotEqual(parser_regression.returncode, 0)
        self.assertIn("unknown option: -z", parser_regression.stderr)

        invalid = subprocess.run(
            ["bash", str(HYPROLED), "--pixel-shift-mode", "unknown"],
            cwd=ROOT, text=True, capture_output=True,
        )
        self.assertNotEqual(invalid.returncode, 0)
        self.assertIn("invalid Pixel Shift mode", invalid.stderr)

    def test_all_pixel_shift_positions_compile(self):
        validator = shutil.which("glslangValidator")
        if validator is None:
            self.skipTest("glslangValidator is not installed or not on PATH")
        modes = {
            "fixed": [(1, 0)],
            "linear-horizontal": [(0, 0), (1, 0)],
            "linear-vertical": [(0, 0), (0, 1)],
            "orbit-2x2": [(0, 0), (1, 0), (1, 1), (0, 1)],
            "orbit-3x3": [
                (0, 0), (1, 0), (1, 1), (0, 1), (-1, 1),
                (-1, 0), (-1, -1), (0, -1), (1, -1),
            ],
        }

        with tempfile.TemporaryDirectory() as directory:
            mask_path = Path(directory) / "mask-only.frag"
            self.generate(True, False, mask_path, dx=0, dy=0)
            cases = [(True, False, 0, 0, "mask-only")]
            for mode, offsets in modes.items():
                for index, (dx, dy) in enumerate(offsets):
                    cases.append((False, True, dx, dy, f"{mode}-{index}-shift"))
                    cases.append((True, True, dx, dy, f"{mode}-{index}-combined"))

            for mask, shift, dx, dy, name in cases:
                path = Path(directory) / f"{name}.frag"
                if name == "mask-only":
                    path = mask_path
                else:
                    self.generate(mask, shift, path, dx=dx, dy=dy)
                result = subprocess.run(
                    [validator, "-S", "frag", str(path)],
                    text=True,
                    capture_output=True,
                )
                self.assertEqual(
                    result.returncode,
                    0,
                    f"{name}: {result.stdout}{result.stderr}",
                )


class PixelShiftModeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        functions = []
        for name in ("pixel_shift_mode_count", "pixel_shift_position",
                     "select_pixel_shift_mode", "advance_pixel_shift"):
            match = re.search(rf"(?ms)^{name}\(\) \{{\n.*?^\}}", SOURCE)
            if match is None:
                raise AssertionError(f"{name}() was not found")
            functions.append(match.group(0))
        cls.functions = "\n\n".join(functions)

    def run_bash(self, command):
        result = subprocess.run(
            ["bash", "-c", self.functions + "\n" + command],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result.stdout.strip()

    def test_mode_lengths_and_positions(self):
        expected = {
            "fixed": [(1, 0)],
            "linear-horizontal": [(0, 0), (1, 0)],
            "linear-vertical": [(0, 0), (0, 1)],
            "orbit-2x2": [(0, 0), (1, 0), (1, 1), (0, 1)],
            "orbit-3x3": [
                (0, 0), (1, 0), (1, 1), (0, 1), (-1, 1),
                (-1, 0), (-1, -1), (0, -1), (1, -1),
            ],
        }
        for mode, offsets in expected.items():
            count = int(self.run_bash(f'pixel_shift_mode_count "{mode}"'))
            self.assertEqual(count, len(offsets), mode)
            for index, offset in enumerate(offsets):
                actual = tuple(map(int, self.run_bash(
                    f'pixel_shift_position "{mode}" "{index}"'
                ).split()))
                self.assertEqual(actual, offset, f"{mode}[{index}]")

    def test_mode_selection_preserves_or_resets_position(self):
        script = (
            self.functions
            + '\nPIXEL_SHIFT=true PIXEL_SHIFT_MODE=orbit-2x2 PIXEL_SHIFT_INDEX=2\n'
            + 'select_pixel_shift_mode orbit-2x2\nprintf "%s %s\\n" "$PIXEL_SHIFT_MODE" "$PIXEL_SHIFT_INDEX"\n'
            + 'select_pixel_shift_mode orbit-3x3\nprintf "%s %s\\n" "$PIXEL_SHIFT_MODE" "$PIXEL_SHIFT_INDEX"\n'
        )
        result = subprocess.run(["bash", "-c", script], cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stdout.splitlines(), ["orbit-2x2 2", "orbit-3x3 0"])

    def test_shift_step_wraps_and_fixed_mode_has_no_next_position(self):
        script = (
            self.functions
            + '\nPIXEL_SHIFT_MODE=orbit-3x3 PIXEL_SHIFT_INDEX=8\n'
            + 'advance_pixel_shift\nprintf "%s\\n" "$PIXEL_SHIFT_INDEX"\n'
        )
        result = subprocess.run(["bash", "-c", script], cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stdout.strip(), "0")

        fixed = subprocess.run(
            ["bash", "-c", self.functions + '\nPIXEL_SHIFT_MODE=fixed PIXEL_SHIFT_INDEX=0\nadvance_pixel_shift'],
            cwd=ROOT, text=True, capture_output=True,
        )
        self.assertEqual(fixed.returncode, 2)

    def test_invalid_mode_position_is_rejected(self):
        result = subprocess.run(
            ["bash", "-c", self.functions + '\npixel_shift_position orbit-2x2 4'],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertNotEqual(result.returncode, 0)


@unittest.skipUnless(shutil.which("jq"), "jq is not installed")
class RuntimeStatusTests(unittest.TestCase):
    def create_state(self, version, mask_enabled=True, pixel_shift=False,
                     pixel_shift_mode="fixed", pixel_shift_index=0):
        state = {
            "version": version,
            "status": "active",
            "phase": 0,
            "offPixels": 1,
            "monitor": 0,
            "area": None,
            "invert": False,
            "brightnessOriginal": 100,
            "brightnessMax": 528,
            "brightnessApplied": 100,
            "brightnessDevice": "intel_backlight",
            "activeShader": "/tmp/hyproled-test.glsl",
            "previousShader": "",
            "compensationPercent": 0,
            "brightnessEnabled": False,
            "compensationPercentOfMaxByPixelCount": {
                "1": 10, "2": 20, "3": 30
            },
        }

        if version >= 3:
            state["pixelShift"] = pixel_shift

        if version >= 4:
            state["maskEnabled"] = mask_enabled

        if version >= 5:
            state["pixelShiftMode"] = pixel_shift_mode
            state["pixelShiftIndex"] = pixel_shift_index

        if version == 1:
            state.pop("brightnessEnabled")

        return state

    def run_status(self, state, runtime_dir):
        state_dir = Path(runtime_dir) / "hyproled"
        state_dir.mkdir(exist_ok=True)
        (state_dir / "state.json").write_text(
            json.dumps(state), encoding="utf-8"
        )

        env = os.environ.copy()
        env["XDG_RUNTIME_DIR"] = str(runtime_dir)

        result = subprocess.run(
            [str(HYPROLED), "--status"],
            cwd=ROOT,
            env=env,
            text=True,
            capture_output=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def assert_brightness_disabled(self, payload):
        self.assertIn("brightness-disabled", payload["class"])
        self.assertNotIn("brightness-enabled", payload["class"])
        self.assertIn("Brightness compensation: disabled", payload["tooltip"])
        self.assertIn("Brightness: unchanged", payload["tooltip"])

    def test_v1_migration_defaults_to_brightness_enabled(self):
        with tempfile.TemporaryDirectory() as directory:
            state = self.create_state(1)
            payload = self.run_status(state, directory)

        self.assertIn("brightness-enabled", payload["class"])
        self.assertNotIn("brightness-disabled", payload["class"])
        self.assertIn("Brightness compensation: enabled", payload["tooltip"])

    def test_v4_pixel_shift_only(self):
        with tempfile.TemporaryDirectory() as directory:
            state = self.create_state(4, False, True)
            payload = self.run_status(state, directory)

        self.assertIn("pixel-shift-enabled", payload["class"])
        self.assertNotIn("mask-0001", payload["class"])
        self.assertIn("Mask: disabled", payload["tooltip"])
        self.assertIn("Pixel shift: enabled", payload["tooltip"])
        self.assert_brightness_disabled(payload)

    def test_v4_mask_only(self):
        with tempfile.TemporaryDirectory() as directory:
            state = self.create_state(4, True, False)
            payload = self.run_status(state, directory)

        self.assertIn("mask-0001", payload["class"])
        self.assertIn("pixel-shift-disabled", payload["class"])
        self.assert_brightness_disabled(payload)

    def test_v4_combined(self):
        with tempfile.TemporaryDirectory() as directory:
            state = self.create_state(4, True, True)
            payload = self.run_status(state, directory)

        self.assertIn("mask-0001", payload["class"])
        self.assertIn("pixel-shift-enabled", payload["class"])
        self.assert_brightness_disabled(payload)

    def test_v5_orbit_3x3_position(self):
        with tempfile.TemporaryDirectory() as directory:
            state = self.create_state(5, True, True, "orbit-3x3", 8)
            payload = self.run_status(state, directory)

        self.assertIn("pixel-shift-mode-orbit-3x3", payload["class"])
        self.assertIn("Pixel Shift mode: orbit-3x3", payload["tooltip"])
        self.assertIn("Pixel Shift position: 9/9", payload["tooltip"])

    def test_v5_invalid_position_is_reported_as_error(self):
        with tempfile.TemporaryDirectory() as directory:
            state = self.create_state(5, True, True, "orbit-2x2", 4)
            payload = self.run_status(state, directory)

        self.assertEqual(payload["alt"], "error")
        self.assertIn("error", payload["class"])

    def test_v3_migration_defaults_to_mask_enabled(self):
        with tempfile.TemporaryDirectory() as directory:
            state = self.create_state(3, True, True)
            payload = self.run_status(state, directory)

        self.assertIn("mask-0001", payload["class"])
        self.assertIn("pixel-shift-enabled", payload["class"])

    def test_v2_migration_defaults_to_mask_only(self):
        with tempfile.TemporaryDirectory() as directory:
            state = self.create_state(2)
            payload = self.run_status(state, directory)

        self.assertIn("mask-0001", payload["class"])
        self.assertIn("pixel-shift-disabled", payload["class"])


@unittest.skipUnless(shutil.which("jq"), "jq is not installed")
class RuntimeStateLoadingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        match = re.search(
            r"(?ms)^load_state\(\) \{\n.*?^\}",
            SOURCE,
        )
        if match is None:
            raise AssertionError("load_state() was not found")
        cls.load_state_function = match.group(0)

        match = re.search(
            r"(?ms)^is_pixel_shift_only_session\(\) \{\n.*?^\}",
            SOURCE,
        )
        if match is None:
            raise AssertionError("is_pixel_shift_only_session() was not found")
        cls.predicate_function = match.group(0)

        match = re.search(
            r"(?ms)^save_state\(\) \{\n.*?^\}",
            SOURCE,
        )
        if match is None:
            raise AssertionError("save_state() was not found")
        cls.save_state_function = match.group(0)

    def run_load_state(self, state):
        with tempfile.TemporaryDirectory() as directory:
            state_path = Path(directory) / "state.json"
            state_path.write_text(json.dumps(state), encoding="utf-8")

            script = (
                'die() { printf "%s\\n" "$*" >&2; exit 1; }\n'
                'STATE_FILE="$1"\n'
                "COMPENSATION_MAP='{}'\n"
                + self.load_state_function
                + '\nload_state\nprintf "%s\\n" '
                  '"$MASK_ENABLED" "$PIXEL_SHIFT" "$BRIGHTNESS_ENABLED" '
                  '"$PIXEL_SHIFT_MODE" "$PIXEL_SHIFT_INDEX"\n'
            )

            result = subprocess.run(
                ["bash", "-c", script, "hyproled-test", str(state_path)],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result.stdout.splitlines()

    def run_pixel_shift_only_predicate(self, state):
        with tempfile.TemporaryDirectory() as directory:
            state_path = Path(directory) / "state.json"
            state_path.write_text(json.dumps(state), encoding="utf-8")

            script = (
                'STATE_FILE="$1"\n'
                + self.predicate_function
                + '\nis_pixel_shift_only_session\n'
            )

            result = subprocess.run(
                ["bash", "-c", script, "hyproled-test", str(state_path)],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )

        return result.returncode == 0

    def test_v4_preserves_explicit_false_values(self):
        state = RuntimeStatusTests().create_state(4, False, True)

        self.assertEqual(
            self.run_load_state(state),
            ["false", "true", "false", "fixed", "0"],
        )

    def test_v5_loads_selected_mode_and_position(self):
        state = RuntimeStatusTests().create_state(
            5, False, True, "orbit-3x3", 7
        )
        self.assertEqual(
            self.run_load_state(state),
            ["false", "true", "false", "orbit-3x3", "7"],
        )

    def test_v3_defaults_to_mask_enabled(self):
        state = RuntimeStatusTests().create_state(3, True, True)

        self.assertEqual(
            self.run_load_state(state),
            ["true", "true", "false", "fixed", "0"],
        )

    def test_v1_uses_legacy_defaults(self):
        state = RuntimeStatusTests().create_state(1)

        self.assertEqual(
            self.run_load_state(state),
            ["true", "false", "true", "fixed", "0"],
        )

    def test_save_state_persists_v5_mode_and_index(self):
        with tempfile.TemporaryDirectory() as directory:
            script = (
                'STATE_DIR="$1"\n'
                'STATE_FILE="$STATE_DIR/state.json"\n'
                'TEMP_STATE_FILE=""\n'
                'STATUS="active" AREA="" BRIGHTNESS_DEVICE="intel_backlight"\n'
                'PREVIOUS_SHADER="" ACTIVE_SHADER="/tmp/hyproled-test.glsl" RESTORE_TARGET=""\n'
                'PIXEL_SHIFT_MODE="orbit-3x3" PIXEL_SHIFT_INDEX=6\n'
                'PHASE=0 OFF_PIXELS=1 MONITOR=0 INVERT=false MASK_ENABLED=false PIXEL_SHIFT=true\n'
                'BRIGHTNESS_ORIGINAL=0 BRIGHTNESS_MAX=1 BRIGHTNESS_APPLIED=0\n'
                'COMPENSATION_PERCENT=0 BRIGHTNESS_ENABLED=false COMPENSATION_MAP="{}"\n'
                + self.save_state_function
                + '\nsave_state && cat "$STATE_FILE"\n'
            )
            result = subprocess.run(
                ["bash", "-c", script, "hyproled-test", directory],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        state = json.loads(result.stdout)
        self.assertEqual(state["version"], 5)
        self.assertEqual(state["pixelShiftMode"], "orbit-3x3")
        self.assertEqual(state["pixelShiftIndex"], 6)

    def test_pixel_shift_only_predicate(self):
        state = RuntimeStatusTests().create_state(4, False, True)
        self.assertTrue(self.run_pixel_shift_only_predicate(state))

        state["maskEnabled"] = True
        self.assertFalse(self.run_pixel_shift_only_predicate(state))

        state_v5 = RuntimeStatusTests().create_state(
            5, False, True, "linear-vertical", 1
        )
        self.assertTrue(self.run_pixel_shift_only_predicate(state_v5))

        legacy_state = RuntimeStatusTests().create_state(3, True, True)
        self.assertFalse(self.run_pixel_shift_only_predicate(legacy_state))

if __name__ == "__main__":
    unittest.main()
