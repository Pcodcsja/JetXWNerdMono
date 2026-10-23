import tempfile
import unittest
from pathlib import Path

from fontTools.ttLib import TTFont

from src.config import FontConfig
from src.licensing import copy_font_licenses, write_source_font_notices
from src.merge import merge_fonts
from src.utils import set_font_name, update_font_names
from tests.font_fixtures import source_pair


class MetadataTests(unittest.TestCase):
    def test_all_six_faces_have_distinct_full_names_and_consistent_legacy_groups(self):
        faces = [
            ("Regular", "Pico", "Regular", False, False, "常规"),
            ("Italic", "Pico", "Italic", False, True, "斜体"),
            ("Medium", "Pico Medium", "Regular", False, False, "中等"),
            ("Medium Italic", "Pico Medium", "Italic", False, True, "中等斜体"),
            ("Bold", "Pico", "Bold", True, False, "粗体"),
            ("Bold Italic", "Pico", "Bold Italic", True, True, "粗斜体"),
        ]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            base, _ = source_pair(root)
            families = {}
            localized_full_names = set()
            for style, legacy_family, legacy_style, bold, italic, chinese in faces:
                with self.subTest(style=style), TTFont(base) as font:
                    # Seed incorrect source flags to verify normalization.
                    font["OS/2"].fsSelection |= 0x61
                    font["head"].macStyle |= 0x03
                    update_font_names(font, "Pico", style, f"Pico {style}",
                                      "Pico-" + style.replace(" ", ""), "Version 1.8")
                    output = root / (style.replace(" ", "") + ".ttf")
                    font.save(output)
                with TTFont(output) as saved:
                    names = saved["name"]
                    self.assertEqual(names.getDebugName(1), legacy_family)
                    self.assertEqual(names.getDebugName(2), legacy_style)
                    self.assertEqual(names.getDebugName(16), "Pico")
                    for name_id, expected in ((1, legacy_family), (2, legacy_style),
                                              (4, "Pico " + chinese), (16, "Pico"), (17, chinese)):
                        self.assertEqual(names.getName(name_id, 3, 1, 0x804).toUnicode(), expected)
                    self.assertEqual(bool(saved["OS/2"].fsSelection & 0x20), bold)
                    self.assertEqual(bool(saved["OS/2"].fsSelection & 0x01), italic)
                    self.assertEqual(bool(saved["OS/2"].fsSelection & 0x40), not (bold or italic))
                    self.assertEqual(saved["head"].macStyle & 0x03, int(bold) | (int(italic) << 1))
                    families.setdefault(legacy_family, set()).add(legacy_style)
                    localized_full_names.add(names.getName(4, 3, 1, 0x804).toUnicode())
            self.assertEqual(len(localized_full_names), 6)
            self.assertEqual(families["Pico"], {"Regular", "Italic", "Bold", "Bold Italic"})
            self.assertEqual(families["Pico Medium"], {"Regular", "Italic"})

    def test_pico_names_preserve_both_sources_notices_after_save(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            base, cn = source_pair(root)
            for path, prefix in ((base, "English"), (cn, "CJK")):
                with TTFont(path) as font:
                    for name_id, text in {0: "copyright", 7: "trademark", 8: "manufacturer", 9: "designer"}.items():
                        set_font_name(font, f"{prefix} {text}", name_id)
                    if path == cn:
                        set_font_name(font, "Original Chinese copyright", 0, mac=False, lang_id=0x804)
                    set_font_name(font, "https://example.org/designer", 12)
                    for name_id in (18, 21, 22, 25):
                        set_font_name(font, "OldBrand", name_id)
                    font.save(path)
            with merge_fonts(str(base), str(cn), FontConfig(visual_scale=1)) as font:
                for _ in range(2):
                    update_font_names(font, "Pico", "Regular", "Pico Regular", "Pico-Regular", "Version 1.7",
                                      author="Pcodcsja (Pico derivative maintainer)",
                                      copyright_str="Pico modifications copyright",
                                      url="https://github.com/Pcodcsja/PicoMono")
                font.save(root / "Pico-Regular.ttf")
            with TTFont(root / "Pico-Regular.ttf") as font:
                names = font["name"]
                for name_id, suffix in ((0, "copyright"), (7, "trademark"), (8, "manufacturer"), (9, "designer")):
                    value = names.getDebugName(name_id)
                    for prefix in ("English", "CJK"):
                        self.assertIn(f"{prefix} {suffix}", value)
                self.assertIn("Original Chinese copyright", names.getDebugName(0))
                self.assertEqual(names.getDebugName(0).count("Pico modifications copyright"), 1)
                self.assertNotIn("Pcodcsja", names.getDebugName(9))
                self.assertEqual(names.getDebugName(12), "https://example.org/designer")
                for name_id in (1, 3, 4, 6, 16, 18, 21):
                    self.assertIn("Pico", names.getDebugName(name_id))
                    self.assertNotIn("OldBrand", names.getDebugName(name_id))
                self.assertIsNone(names.getDebugName(25))
                self.assertEqual(names.getDebugName(5), "Version 1.7")
                self.assertAlmostEqual(font["head"].fontRevision, 1.7, places=4)

    def test_release_contains_font_and_component_licenses(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            copy_font_licenses(output)
            self.assertIn("SIL OPEN FONT LICENSE", (output / "OFL.txt").read_text("utf-8"))
            self.assertTrue((output / "NOTICE.md").is_file())
            self.assertTrue((output / "licenses/LXGWWenKaiMonoGBScreen-OFL.txt").is_file())
            self.assertTrue((output / "licenses/NerdFonts-LICENSE.txt").is_file())

    def test_source_notices_describe_actual_inputs_and_survive_web_packaging(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            base, cn = source_pair(root)
            with TTFont(cn) as font:
                set_font_name(font, "Custom source copyright", 0)
                font.save(cn)
            desktop = root / "desktop"
            web = root / "web"
            copy_font_licenses(desktop)
            notices = desktop / "licenses/SOURCE-FONT-NOTICES.txt"
            write_source_font_notices([base, cn, base], notices)
            text = notices.read_text("utf-8")
            self.assertEqual(text.count("File: base.ttf"), 1)
            self.assertIn("Custom source copyright", text)
            copy_font_licenses(web, source_root=desktop)
            self.assertEqual((web / "licenses/SOURCE-FONT-NOTICES.txt").read_text("utf-8"), text)


if __name__ == "__main__":
    unittest.main()
