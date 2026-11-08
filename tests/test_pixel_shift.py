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

    def generate(self, mask, shift, path):
        script = (
            self.function
            + "\nMONITOR=0\n"
            + "PHASE=0\n"
            + "OFF_PIXELS=1\n"
            + f"MASK_ENABLED={'true' if mask else 'false'}\n"
            + f"PIXEL_SHIFT={'true' if shift else 'false'}\n"
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

        self.assertIn("orig = texture(tex, v_texcoord);", shader)
        self.assertIn("bool off =", shader)
        # Both GLSL branches are present; the false condition disables Pixel Shift.
        self.assertIn("if (false) {", shader)
        self.assertIn("texelFetch(tex, sourceTexel, 0)", shader)
        self.assertIn("orig = texture(tex, v_texcoord);", shader)

    def test_pixel_shift_only(self):
        with tempfile.TemporaryDirectory() as directory:
            shader = self.generate(
                False, True, Path(directory) / "shift.frag"
            )

        self.assertIn("if (true) {", shader)
        self.assertIn("texelFetch(tex, sourceTexel, 0)", shader)
        self.assertIn("sourceTexel.x < 0", shader)
        self.assertIn("orig = vec4(0.0, 0.0, 0.0, 1.0);", shader)
        self.assertNotIn("bool off =", shader)
        self.assertIn("fragColor = orig;", shader)

    def test_combined_effects(self):
        with tempfile.TemporaryDirectory() as directory:
            shader = self.generate(
                True, True, Path(directory) / "combined.frag"
            )

        self.assertIn("if (true) {", shader)
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
                False, True, Path(directory) / "shift.frag"
            )

        self.assertIn("textureSize(tex, 0)", shader)
        self.assertIn(
            "ivec2 sourceTexel = texel - ivec2(1, 0);",
            shader,
        )

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

    @unittest.skipUnless(
        shutil.which("glslangValidator"),
        "glslangValidator is not installed",
    )
    def test_three_shader_modes_compile(self):
        validator = shutil.which("glslangValidator")

        with tempfile.TemporaryDirectory() as directory:
            for mask, shift, name in (
                (True, False, "mask"),
                (False, True, "shift"),
                (True, True, "combined"),
            ):
                path = Path(directory) / f"{name}.frag"
                self.generate(mask, shift, path)

                result = subprocess.run(
                    [validator, "-S", "frag", str(path)],
                    text=True,
                    capture_output=True,
                )
                self.assertEqual(
                    result.returncode,
                    0,
                    result.stdout + result.stderr,
                )


@unittest.skipUnless(shutil.which("jq"), "jq is not installed")
class RuntimeStatusTests(unittest.TestCase):
    def create_state(self, version, mask_enabled=True, pixel_shift=False):
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
                  '"$MASK_ENABLED" "$PIXEL_SHIFT" "$BRIGHTNESS_ENABLED"\n'
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
            ["false", "true", "false"],
        )

    def test_v3_defaults_to_mask_enabled(self):
        state = RuntimeStatusTests().create_state(3, True, True)

        self.assertEqual(
            self.run_load_state(state),
            ["true", "true", "false"],
        )

    def test_v1_uses_legacy_defaults(self):
        state = RuntimeStatusTests().create_state(1)

        self.assertEqual(
            self.run_load_state(state),
            ["true", "false", "true"],
        )

    def test_pixel_shift_only_predicate(self):
        state = RuntimeStatusTests().create_state(4, False, True)
        self.assertTrue(self.run_pixel_shift_only_predicate(state))

        state["maskEnabled"] = True
        self.assertFalse(self.run_pixel_shift_only_predicate(state))

        legacy_state = RuntimeStatusTests().create_state(3, True, True)
        self.assertFalse(self.run_pixel_shift_only_predicate(legacy_state))


if __name__ == "__main__":
    unittest.main()
