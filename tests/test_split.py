import subprocess
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.config import FontConfig
from split import enhance_local_font_matching, split_all_fonts, split_font
from tests.font_fixtures import empty, make_font


class SplitRegressionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_local_matching_never_uses_generic_family(self):
        css = self.root / "result.css"
        css.write_text('src:local("Example"),url("./0.woff2");', encoding="utf-8")
        enhance_local_font_matching(css, "Example", "Bold")
        result = css.read_text("utf-8")
        self.assertIn('local("Example-Bold")', result)
        self.assertNotIn('local("Example")', result)
        enhance_local_font_matching(css, "Example", "Bold")
        self.assertEqual(css.read_text("utf-8"), result)

    def test_missing_and_empty_input_fail(self):
        with self.assertRaises(FileNotFoundError):
            split_all_fonts(self.root / "absent", self.root / "out", FontConfig())
        with self.assertRaises(ValueError):
            split_all_fonts(self.root, self.root / "out", FontConfig())

    @patch("split.copy_font_licenses")
    @patch("split.generate_merged_css")
    @patch("split.split_font")
    def test_manifest_excludes_old_font_names(self, split, css, licenses):
        for name in ("Pico-Regular.ttf", "OldBrand-Regular.ttf"):
            (self.root / name).touch()
        manifest = {"family_name": "Pico", "fonts": [{"filename": "Pico-Regular.ttf"}]}
        (self.root / "fonts-manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        split_all_fonts(self.root, self.root / "out", FontConfig())
        self.assertEqual(split.call_count, 1)
        self.assertEqual(split.call_args.args[0].name, "Pico-Regular.ttf")

    def test_manifest_cannot_read_fonts_outside_input(self):
        manifest = {"fonts": [{"filename": "../outside.ttf"}]}
        (self.root / "fonts-manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        with self.assertRaises(ValueError):
            split_all_fonts(self.root, self.root / "out", FontConfig())

    @patch("split.get_cn_font_split_command", return_value=["fake-tool"])
    def test_metadata_overrides_default_family_and_filename_guessing(self, command):
        font = self.root / "MyBoldFamily-Regular.ttf"
        make_font(font, 1000, {"space": empty()}, {0x20: "space"}, 600,
                  family="MyBoldFamily", weight=400)
        output = self.root / "out"
        old = output / font.stem
        old.mkdir(parents=True)
        (old / "obsolete.woff2").write_bytes(b"old")

        def fake_run(args, **kwargs):
            self.assertEqual(args[args.index("--css.fontFamily") + 1], "MyBoldFamily")
            self.assertEqual(args[args.index("--css.fontWeight") + 1], "400")
            folder = Path(args[args.index("-o") + 1])
            folder.mkdir()
            (folder / "result.css").write_text('src:local("MyBoldFamily"),url("./0.woff2");')
            (folder / "0.woff2").write_bytes(b"wOF2")
            (folder / "index.html").write_text("preview")
        with patch("split.subprocess.run", side_effect=fake_run):
            result = split_font(font, output, FontConfig())
        self.assertEqual(result, old)
        self.assertFalse((old / "obsolete.woff2").exists())

    @patch("split.get_cn_font_split_command", return_value=["fake-tool"])
    def test_failed_split_preserves_existing_output(self, command):
        font = self.root / "Example-Regular.ttf"
        make_font(font, 1000, {"space": empty()}, {0x20: "space"}, 600)
        output = self.root / "out"
        old = output / font.stem
        old.mkdir(parents=True)
        (old / "result.css").write_text("previous")
        with patch("split.subprocess.run", side_effect=subprocess.CalledProcessError(1, "fake", stderr="failed")):
            with self.assertRaises(subprocess.CalledProcessError):
                split_font(font, output, FontConfig())
        self.assertEqual((old / "result.css").read_text(), "previous")


if __name__ == "__main__":
    unittest.main()
