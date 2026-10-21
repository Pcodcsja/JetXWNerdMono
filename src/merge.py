"""Core font merging logic for JetBrainsLxgwNerdMono."""

import math
from typing import Set

from fontTools.ttLib import TTFont

from .config import FontConfig
from .utils import is_cjk_codepoint, merge_os2_ranges


def get_cjk_glyphs(font: TTFont, config: FontConfig) -> Set[str]:
    """Get all CJK glyph names from a font.

    Args:
        font: TTFont object
        config: FontConfig with CJK ranges

    Returns:
        Set of glyph names that are CJK characters
    """
    cjk_glyphs = set()
    cmap = font["cmap"].getBestCmap()

    if cmap:
        for codepoint, glyph_name in cmap.items():
            if is_cjk_codepoint(codepoint, config.cjk_ranges):
                cjk_glyphs.add(glyph_name)

    return cjk_glyphs


def get_cjk_cmap_entries(font: TTFont, config: FontConfig) -> dict:
    """Get cmap entries for CJK codepoints.

    Args:
        font: TTFont object
        config: FontConfig with CJK ranges

    Returns:
        Dict mapping codepoint -> glyph_name for CJK characters
    """
    entries = {}
    cmap = font["cmap"].getBestCmap()

    if cmap:
        for codepoint, glyph_name in cmap.items():
            if is_cjk_codepoint(codepoint, config.cjk_ranges):
                entries[codepoint] = glyph_name

    return entries


def merge_fonts(
    base_font_path: str,
    cn_font_path: str,
    config: FontConfig,
) -> TTFont:
    """Import CJK outlines by codepoint, preserving unrelated base glyphs.

    Flatten source composites before scaling so references, component offsets,
    and glyph-name collisions cannot depend on the destination glyph table.
    """
    import copy
    from fontTools.ttLib.tables._g_l_y_f import Glyph
    from fontTools.ttLib.tables._c_m_a_p import CmapSubtable
    from fontTools.ttLib.tables.ttProgram import Program

    print(f"  Loading base font: {base_font_path}")
    base_font = TTFont(base_font_path)
    try:
        with TTFont(cn_font_path) as cn_font:
            base_cmap = dict(base_font.getBestCmap() or {})
            space = base_cmap.get(0x20)
            if not space or base_font["hmtx"][space][0] != config.en_width:
                raise ValueError("en_width must match the English source font's space advance")
            source_entries = get_cjk_cmap_entries(cn_font, config)
            if not source_entries:
                raise ValueError("The CJK source font has no supported CJK codepoints")
            base_glyf = base_font["glyf"]
            source_glyf = cn_font["glyf"]
            order = list(base_font.getGlyphOrder())
            used_names = set(order)
            imported = {}
            scale = base_font["head"].unitsPerEm / cn_font["head"].unitsPerEm * config.visual_scale
            # OpenType uses negative angles for a rightward slant. Apply only
            # the difference so an already slanted CJK source is not tilted twice.
            target_angle = base_font["post"].italicAngle
            source_angle = cn_font["post"].italicAngle
            shear = math.tan(math.radians(source_angle)) - math.tan(math.radians(target_angle))
            print(f"  Importing {len(source_entries)} CJK mappings at {scale:.4f}x")
            if shear:
                print(f"  Matching CJK slant: {source_angle:g} to {target_angle:g} degrees")
            for cp, source_name in sorted(source_entries.items()):
                width = config.codepoint_width(cp)
                key = (source_name, width)
                if key not in imported:
                    name = source_name
                    if name in used_names:
                        name = f"{source_name}.cjk"
                    while name in used_names:
                        name += ".cjk"
                    source = source_glyf[source_name]
                    glyph = Glyph()
                    if source.numberOfContours:
                        coords, ends, flags = source.getCoordinates(source_glyf)
                        glyph.coordinates = copy.deepcopy(coords)
                        glyph.endPtsOfContours = list(ends)
                        glyph.flags = copy.copy(flags)
                        glyph.numberOfContours = len(ends)
                        glyph.coordinates.scale((scale, scale))
                        if shear:
                            glyph.coordinates.transform(((1, 0), (shear, 1)))
                        glyph.program = Program()
                        glyph.program.fromBytecode(b"")
                        glyph.recalcBounds(base_glyf)
                        lsb = glyph.xMin
                    else:
                        glyph.numberOfContours = 0
                        lsb = 0
                    base_glyf[name] = glyph
                    base_font["hmtx"][name] = (width, lsb)
                    order.append(name)
                    used_names.add(name)
                    imported[key] = name
                base_cmap[cp] = imported[key]

            if len(order) > 65535:
                raise ValueError(f"Too many TrueType glyphs: {len(order)} (maximum 65535)")
            base_font.setGlyphOrder(order)
            base_font["maxp"].numGlyphs = len(order)
            # All Unicode consumers must see the same mapping. Do not alter
            # legacy Mac encodings or format-14 variation-selector tables.
            tables = base_font["cmap"].tables
            if not any(t.format == 12 and t.isUnicode() for t in tables):
                table = CmapSubtable.newSubtable(12)
                table.platformID, table.platEncID, table.language = 3, 10, 0
                table.cmap = {}
                tables.append(table)
            if not any(t.format == 4 and t.isUnicode() for t in tables):
                table = CmapSubtable.newSubtable(4)
                table.platformID, table.platEncID, table.language = 3, 1, 0
                table.cmap = {}
                tables.append(table)
            for table in tables:
                if table.isUnicode() and table.format in (4, 12):
                    table.cmap = {cp: name for cp, name in base_cmap.items()
                                  if table.format == 12 or cp < 0xFFFF}
            base_font["hhea"].advanceWidthMax = max(w for w, _ in base_font["hmtx"].metrics.values())
            merge_os2_ranges(base_font, cn_font)
            base_font["OS/2"].recalcUnicodeRanges(base_font)
            base_font["OS/2"].recalcCodePageRanges(base_font)
            print(f"  Added {len(imported)} outlines ({len(order)} glyphs total)")
        return base_font
    except Exception:
        base_font.close()
        raise


def scale_nerd_icons(font: TTFont, config: FontConfig) -> None:
    """Scale NerdFont icons to occupy 2x English character width (same as CJK).

    NerdFont icons are in Private Use Area:
    - U+E000-U+F8FF (BMP Private Use Area)
    - U+F0000-U+FFFFD (Supplementary Private Use Area-A)

    Powerline symbols (U+E0A0-U+E0DF) are handled specially:
    - They must maintain their original vertical bounds to align with text
    - Only horizontal width adjustment is applied, no scaling or vertical shift

    Args:
        font: TTFont object
        config: FontConfig object
    """
    glyf = font["glyf"]
    hmtx = font["hmtx"]
    cmap = font["cmap"].getBestCmap()

    # NerdFont icon Unicode ranges
    nerd_ranges = [
        (0xE000, 0xF8FF),      # Private Use Area
        (0xF0000, 0xFFFFD),    # Supplementary Private Use Area-A
    ]

    # Powerline symbols range - these need special handling
    # They must span the full line height and not be scaled
    powerline_range = (0xE0A0, 0xE0DF)

    # Build mapping: codepoint -> glyph_name for nerd icons
    nerd_glyph_map = {}  # glyph_name -> codepoint
    for codepoint, glyph_name in cmap.items():
        for start, end in nerd_ranges:
            if start <= codepoint <= end:
                nerd_glyph_map[glyph_name] = codepoint
                break

    if not nerd_glyph_map:
        return

    print(f"  Processing {len(nerd_glyph_map)} NerdFont icons...")

    # Target: scale icons to ~70% of 1200 = 840 units (similar to CJK fill ratio)
    # Original icon width is ~600, so scale factor = 840 / 600 = 1.4
    scale_factor = 1.4

    powerline_count = 0
    scaled_count = 0

    for glyph_name, codepoint in nerd_glyph_map.items():
        if glyph_name not in glyf.glyphs:
            continue

        glyph = glyf[glyph_name]
        if glyph.numberOfContours <= 0:
            continue

        # Get current metrics
        width, lsb = hmtx[glyph_name]
        if width != config.en_width:
            continue  # Skip if not standard English width

        # Check if this is a Powerline symbol
        is_powerline = powerline_range[0] <= codepoint <= powerline_range[1]

        if is_powerline:
            # Powerline symbols: only adjust width, no scaling or vertical shift
            # These symbols need to maintain their original vertical bounds
            if hasattr(glyph, "coordinates"):
                if not hasattr(glyph, 'xMin') or glyph.xMin is None:
                    glyph.recalcBounds(glyf)

                # Only center horizontally, keep vertical position
                if hasattr(glyph, 'xMin') and glyph.xMin is not None:
                    glyph_width = glyph.xMax - glyph.xMin
                    ideal_lsb = (config.cn_width - glyph_width) // 2
                    delta_x = ideal_lsb - glyph.xMin

                    if abs(delta_x) > 1:
                        glyph.coordinates.translate((delta_x, 0))
                        glyph.recalcBounds(glyf)

                    hmtx[glyph_name] = (config.cn_width, ideal_lsb)
                else:
                    hmtx[glyph_name] = (config.cn_width, 0)

            powerline_count += 1
        else:
            # Regular icons: scale and center both horizontally and vertically
            if hasattr(glyph, "coordinates"):
                # Ensure bounds are calculated
                if not hasattr(glyph, 'xMin') or glyph.xMin is None:
                    glyph.recalcBounds(glyf)

                # Scale to 2x size
                glyph.coordinates.scale((scale_factor, scale_factor))
                glyph.recalcBounds(glyf)

            # Update advance width to CJK width (1200)
            # Center the glyph horizontally and vertically
            if hasattr(glyph, 'xMin') and glyph.xMin is not None:
                glyph_width = glyph.xMax - glyph.xMin
                ideal_lsb = (config.cn_width - glyph_width) // 2
                delta_x = ideal_lsb - glyph.xMin

                # Vertical centering: align icon center with CJK center (~360)
                glyph_center_y = (glyph.yMin + glyph.yMax) / 2
                target_center_y = 360  # Similar to CJK vertical center
                delta_y = target_center_y - glyph_center_y

                if abs(delta_x) > 1 or abs(delta_y) > 1:
                    glyph.coordinates.translate((delta_x, delta_y))
                    glyph.recalcBounds(glyf)

                hmtx[glyph_name] = (config.cn_width, ideal_lsb)
            else:
                hmtx[glyph_name] = (config.cn_width, 0)

            scaled_count += 1

    print(f"    Powerline symbols (no scaling): {powerline_count}")
    print(f"    Regular icons (scaled 1.4x): {scaled_count}")


def center_cjk_glyphs(font: TTFont, config: FontConfig) -> None:
    """Center CJK glyphs within their advance width.

    Only centers glyphs that occupy more than half the advance width.
    Narrow glyphs (like punctuation) keep their original position,
    except for paired punctuation (brackets, quotes) which are aligned
    to their respective sides.

    Args:
        font: TTFont object
        config: FontConfig object
    """
    glyf = font["glyf"]
    hmtx = font["hmtx"]
    cmap = font["cmap"].getBestCmap()
    cjk_glyphs = get_cjk_glyphs(font, config)

    # Paired punctuation: left-side chars should align right, right-side should align left
    # These are codepoints for opening/closing brackets and quotes
    left_punctuation = {
        0x3010,  # 【
        0x300A,  # 《
        0x3008,  # 〈
        0x300C,  # 「
        0x300E,  # 『
        0x3014,  # 〔
        0x3016,  # 〖
        0x3018,  # 〘
        0x301A,  # 〚
        0xFF08,  # （
        0xFF3B,  # ［
        0xFF5B,  # ｛
        0x2018,  # '
        0x201C,  # "
    }
    right_punctuation = {
        0x3011,  # 】
        0x300B,  # 》
        0x3009,  # 〉
        0x300D,  # 」
        0x300F,  # 』
        0x3015,  # 〕
        0x3017,  # 〗
        0x3019,  # 〙
        0x301B,  # 〛
        0xFF09,  # ）
        0xFF3D,  # ］
        0xFF5D,  # ｝
        0x2019,  # '
        0x201D,  # "
    }

    # Build reverse cmap: glyph_name -> codepoint
    glyph_to_codepoint = {}
    if cmap:
        for cp, gn in cmap.items():
            glyph_to_codepoint[gn] = cp

    centered_count = 0
    skipped_count = 0
    paired_count = 0

    for glyph_name in sorted(cjk_glyphs):
        if glyph_name not in glyf.glyphs:
            continue

        glyph = glyf[glyph_name]
        if glyph.numberOfContours <= 0:
            continue

        width, lsb = hmtx[glyph_name]
        if width != config.cn_width:
            continue

        # Calculate glyph bounds
        if not hasattr(glyph, "xMin") or glyph.xMin is None:
            glyph.recalcBounds(glyf)

        if glyph.xMin is None or glyph.xMax is None:
            continue

        glyph_width = glyph.xMax - glyph.xMin
        codepoint = glyph_to_codepoint.get(glyph_name, 0)

        # Handle paired punctuation specially
        if codepoint in left_punctuation:
            # Left punctuation (opening): align to right side
            ideal_lsb = config.cn_width - glyph_width
            delta = ideal_lsb - glyph.xMin
            if abs(delta) > 1:
                glyph.coordinates.translate((delta, 0))
                glyph.recalcBounds(glyf)
                hmtx[glyph_name] = (config.cn_width, ideal_lsb)
            paired_count += 1
            continue

        if codepoint in right_punctuation:
            # Right punctuation (closing): align to left side
            ideal_lsb = 0
            delta = ideal_lsb - glyph.xMin
            if abs(delta) > 1:
                glyph.coordinates.translate((delta, 0))
                glyph.recalcBounds(glyf)
                hmtx[glyph_name] = (config.cn_width, ideal_lsb)
            paired_count += 1
            continue

        # Only center glyphs that occupy more than half the advance width
        # Narrow glyphs (like punctuation) keep their original position
        if glyph_width <= config.cn_width // 2:
            skipped_count += 1
            continue

        # Calculate centering offset
        ideal_lsb = (config.cn_width - glyph_width) // 2
        delta = ideal_lsb - glyph.xMin

        if abs(delta) > 1:  # Only adjust if significant
            glyph.coordinates.translate((delta, 0))
            glyph.recalcBounds(glyf)
            hmtx[glyph_name] = (config.cn_width, ideal_lsb)
            centered_count += 1

    print(f"    Centered: {centered_count}, Paired punctuation: {paired_count}, Skipped (narrow): {skipped_count}")
