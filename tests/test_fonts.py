import math
import tempfile
import unittest
from pathlib import Path

from fontTools.ttLib import TTFont

from build import load_config
from src.config import FontConfig
from src.merge import merge_fonts, center_cjk_glyphs
from src.utils import normalize_zero_width_glyphs, verify_glyph_width, update_font_names
from tests.font_fixtures import source_pair


class FontRegressionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.base, self.cn = source_pair(self.root)
        self.config = FontConfig(visual_scale=1.0)

    def merge(self):
        font = merge_fonts(str(self.base), str(self.cn), self.config)
        self.addCleanup(font.close)
        return font

    def test_unicode_overrides_do_not_replace_latin_outline(self):
        font = self.merge()
        cmap = font.getBestCmap()
        self.assertNotEqual(cmap[0x41], cmap[0xFF5B])
        self.assertEqual(font["hmtx"][cmap[0x41]][0], 600)
        self.assertEqual(font["hmtx"][cmap[0xFF5B]][0], 1200)
        self.assertEqual(font["glyf"][cmap[0x41]].xMax, 500)

    def test_halfwidth_marks_and_new_unicode_ranges(self):
        font = self.merge()
        cmap = font.getBestCmap()
        self.assertEqual(font["hmtx"][cmap[0xFF71]][0], 600)
        self.assertEqual(font["hmtx"][cmap[0x3099]][0], 0)
        for cp in (0x3042, 0xAC00, 0xFA0C, 0x31350, 0x2EBF0):
            self.assertEqual(font["hmtx"][cmap[cp]][0], 1200)

    def test_composites_flatten_and_scale_component_offsets(self):
        font = self.merge()
        glyph = font["glyf"][font.getBestCmap()[0x4E8C]]
        self.assertFalse(glyph.isComposite())
        self.assertEqual((glyph.xMin, glyph.yMin, glyph.xMax, glyph.yMax), (250, 100, 500, 350))
        output = self.root / "saved.ttf"
        font.save(output)
        with TTFont(output) as saved:
            self.assertIn(0x4E8C, saved.getBestCmap())

    def test_zero_width_alias_does_not_change_space_width(self):
        font = self.merge()
        normalize_zero_width_glyphs(font)
        cmap = font.getBestCmap()
        self.assertEqual(font["hmtx"][cmap[0x20]][0], 600)
        for cp in (0x200B, 0xFEFF):
            self.assertEqual(font["hmtx"][cmap[cp]][0], 0)
        output = self.root / "zero-width.ttf"
        font.save(output)
        with TTFont(output) as saved:
            self.assertEqual(saved["hmtx"][saved.getBestCmap()[0x20]][0], 600)
            self.assertEqual(saved["hmtx"][saved.getBestCmap()[0x200B]][0], 0)

    def test_cjk_slant_matches_italic_base_without_tilting_latin(self):
        with TTFont(self.base) as base:
            base["post"].italicAngle = -9
            base["OS/2"].fsSelection = 1
            base["head"].macStyle = 2
            latin_before = list(base["glyf"][base.getBestCmap()[0x41]].coordinates)
            base.save(self.base)
        font = self.merge()
        cmap = font.getBestCmap()
        shear = math.tan(math.radians(9))
        # The source composite offset is flattened and scaled before slanting.
        composite = font["glyf"][cmap[0x4E8C]]
        points = list(composite.coordinates)
        self.assertAlmostEqual(points[0][0], 250 + 100 * shear)
        self.assertAlmostEqual(points[3][0], 250 + 350 * shear)
        self.assertEqual([y for x, y in points], [100, 100, 350, 350])
        self.assertEqual(list(font["glyf"][cmap[0x41]].coordinates), latin_before)
        center_cjk_glyphs(font, self.config)
        normalize_zero_width_glyphs(font)
        verify_glyph_width(font, [0, 600, 1200], config=self.config)
        output = self.root / "italic.ttf"
        font.save(output)
        with TTFont(output) as saved:
            points = list(saved["glyf"][saved.getBestCmap()[0x4E8C]].coordinates)
            self.assertAlmostEqual(points[3][0] - points[0][0], 250 * shear, delta=1)
            self.assertEqual(saved["hmtx"][saved.getBestCmap()[0x4E8C]][0], 1200)

    def test_matching_source_slant_is_not_applied_twice(self):
        for path in (self.base, self.cn):
            with TTFont(path) as font:
                font["post"].italicAngle = -9
                font["OS/2"].fsSelection = 1
                font["head"].macStyle = 2
                if path == self.cn:
                    # A source with an existing rightward slant.
                    font["glyf"]["collision"].coordinates.transform(
                        ((1, 0), (math.tan(math.radians(9)), 1)))
                font.save(path)
        with TTFont(self.cn) as source:
            expected = [(x * .5, y * .5)
                        for x, y in source["glyf"]["collision"].coordinates]
        merged = self.merge()
        actual = list(merged["glyf"][merged.getBestCmap()[0x4E00]].coordinates)
        self.assertEqual(actual, expected)

    def test_width_validator_rejects_wrong_character_class(self):
        font = self.merge()
        center_cjk_glyphs(font, self.config)
        normalize_zero_width_glyphs(font)
        verify_glyph_width(font, [0, 600, 1200], config=self.config)
        glyph = font.getBestCmap()[0xFF5B]
        font["hmtx"][glyph] = (600, 0)
        with self.assertRaisesRegex(ValueError, "U\\+FF5B"):
            verify_glyph_width(font, [0, 600, 1200], config=self.config)

    def test_revision_matches_version_name(self):
        font = self.merge()
        update_font_names(font, "Example", "Regular", "Example Regular",
                          "Example-Regular", "Version 1.5")
        self.assertEqual(font["head"].fontRevision, 1.5)
        self.assertEqual(font["name"].getDebugName(5), "Version 1.5")

    def test_invalid_width_config_and_missing_config_fail(self):
        with self.assertRaises(ValueError):
            FontConfig(en_width=600, cn_width=1000)
        with self.assertRaises(ValueError):
            FontConfig(visual_scale=float("nan"))
        with self.assertRaises(FileNotFoundError):
            load_config(self.root / "absent.yaml")


if __name__ == "__main__":
    unittest.main()
