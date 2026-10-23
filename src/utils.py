"""Utility functions for font manipulation."""

from typing import List, Tuple

from fontTools.ttLib import TTFont
from .config import FontConfig, is_zero_width


def set_font_name(
    font: TTFont,
    name: str,
    name_id: int,
    mac: bool = True,
    lang_id: int = 0x409
) -> None:
    """Set font name entry.

    Args:
        font: TTFont object
        name: Name string to set
        name_id: Name table ID
        mac: Whether to also set Mac platform entry (default True for macOS compatibility)
        lang_id: Language ID (default 0x409 for US English)
    """
    name_table = font["name"]

    # Only remove existing entries if we are setting English (default)
    # This allows adding multiple languages for the same NameID
    if lang_id == 0x409:
        name_table.removeNames(nameID=name_id)

    # Windows platform (platformID=3, platEncID=1 = Unicode BMP)
    name_table.setName(
        name, nameID=name_id, platformID=3, platEncID=1, langID=lang_id
    )

    # Mac platform (platformID=1, platEncID=0 = Roman, langID=0 = English)
    # Only set for English
    if mac and lang_id == 0x409:
        name_table.setName(
            name, nameID=name_id, platformID=1, platEncID=0, langID=0x0
        )


def font_notice_values(font: TTFont, name_id: int) -> List[str]:
    """Read every localized notice, preserving its original text."""
    return list(dict.fromkeys(
        record.toUnicode() for record in font["name"].names
        if record.nameID == name_id and record.toUnicode().strip()
    ))


def merge_font_notices(target_font: TTFont, source_font: TTFont) -> None:
    """Keep both sources' copyright, trademark and designer attribution."""
    for name_id in (0, 7, 8, 9):
        notices = list(dict.fromkeys(
            font_notice_values(target_font, name_id)
            + font_notice_values(source_font, name_id)
        ))
        if notices:
            # Use Unicode records: Mac Roman cannot encode localized notices.
            set_font_name(target_font, "\n\n".join(notices), name_id, mac=False)


def update_font_names(
    font: TTFont,
    family_name: str,
    style_name: str,
    full_name: str,
    postscript_name: str,
    version_str: str,
    author: str = "",
    copyright_str: str = "",
    description: str = "",
    url: str = "",
    license_desc: str = "",
    license_url: str = "",
) -> None:
    """Update font metadata names.

    Args:
        font: TTFont object
        family_name: Typographic family (NameID 16); legacy families are derived
        style_name: Typographic style (NameID 17); legacy styles are derived
        full_name: Full font name (NameID 4)
        postscript_name: PostScript name (NameID 6)
        version_str: Version string (NameID 5)
        author: Derivative maintainer, appended to manufacturer attribution
        copyright_str: Additional copyright notice, appended to source notices
        description: Font description (NameID 10)
        url: Derivative project URL (NameID 11); original designer URL is retained
        license_desc: License description (NameID 13)
        license_url: License URL (NameID 14)
    """
    unique_id = f"{version_str};{postscript_name}"
    font["head"].fontRevision = float(version_str.removeprefix("Version ").strip())

    # English names (Language ID 0x409)
    # NameID 0: Copyright
    notices = font_notice_values(font, 0)
    if copyright_str and not any(copyright_str in notice for notice in notices):
        notices.append(copyright_str)
    if notices:
        set_font_name(font, "\n\n".join(notices), 0, mac=False)
    # Legacy Windows families have at most four style-linked faces. Medium
    # belongs to its own legacy family, while IDs 16/17 keep all faces under Pico.
    styles = {
        "regular": (family_name, "Regular", False, False, "常规"),
        "italic": (family_name, "Italic", False, True, "斜体"),
        "medium": (f"{family_name} Medium", "Regular", False, False, "中等"),
        "mediumitalic": (f"{family_name} Medium", "Italic", False, True, "中等斜体"),
        "bold": (family_name, "Bold", True, False, "粗体"),
        "bolditalic": (family_name, "Bold Italic", True, True, "粗斜体"),
    }
    existing_bold = bool(font["OS/2"].fsSelection & 0x20 or font["head"].macStyle & 0x01)
    existing_italic = bool(font["OS/2"].fsSelection & 0x01 or font["head"].macStyle & 0x02)
    legacy_family, legacy_style, bold, italic, chinese_style = styles.get(
        style_name.replace(" ", "").casefold(),
        (family_name, style_name, existing_bold, existing_italic, style_name),
    )
    set_font_name(font, legacy_family, 1)
    set_font_name(font, legacy_style, 2)
    # Keep both Windows and macOS style flags consistent with legacy names.
    font["OS/2"].fsSelection = (
        (font["OS/2"].fsSelection & ~0x61)
        | (0x20 if bold else 0)
        | (0x01 if italic else 0)
        | (0x40 if not (bold or italic) else 0)
    )
    font["head"].macStyle = (font["head"].macStyle & ~0x03) | int(bold) | (int(italic) << 1)
    # NameID 3: Unique ID
    set_font_name(font, unique_id, 3)
    # NameID 4: Full name
    set_font_name(font, full_name, 4)
    # NameID 5: Version string
    set_font_name(font, version_str, 5)
    # NameID 6: PostScript name
    set_font_name(font, postscript_name, 6)
    # Trademark and original designer notices are attribution, not face names.
    # NameID 8: Original manufacturers plus the derivative maintainer.
    if author:
        manufacturers = font_notice_values(font, 8)
        if not any(author in notice for notice in manufacturers):
            manufacturers.append(author)
        set_font_name(font, "\n\n".join(manufacturers), 8, mac=False)
    # NameID 10: Description
    if description:
        set_font_name(font, description, 10)
    # NameID 11: Vendor URL
    if url:
        set_font_name(font, url, 11)
    # NameID 12 is the original designer URL; do not impersonate the designer.
    # NameID 13: License description
    if license_desc:
        set_font_name(font, license_desc, 13)
    # NameID 14: License URL
    if license_url:
        set_font_name(font, license_url, 14)

    # Set Preferred family/style (NameID 16, 17) for better Windows compatibility
    set_font_name(font, family_name, 16)  # Preferred Family
    set_font_name(font, style_name, 17)  # Preferred Subfamily

    # Optional legacy family names must not retain a source project's branding.
    optional_names = {18: full_name, 21: family_name, 22: style_name}
    for name_id, value in optional_names.items():
        if any(record.nameID == name_id for record in font["name"].names):
            set_font_name(font, value, name_id)
    if "fvar" not in font:
        font["name"].removeNames(nameID=25)

    # Add Chinese names (Language ID 0x804) for better Windows CJK compatibility
    # Localized full names expose the face style in Chinese font previews.
    # Keep the family and legacy style-linking names stable across locales.
    cn_lang_id = 0x804
    set_font_name(font, legacy_family, 1, mac=False, lang_id=cn_lang_id)
    set_font_name(font, legacy_style, 2, mac=False, lang_id=cn_lang_id)
    set_font_name(font, f"{family_name} {chinese_style}", 4, mac=False, lang_id=cn_lang_id)
    set_font_name(font, family_name, 16, mac=False, lang_id=cn_lang_id)
    set_font_name(font, chinese_style, 17, mac=False, lang_id=cn_lang_id)


def merge_os2_ranges(target_font: TTFont, source_font: TTFont) -> None:
    """Merge OS/2 table ranges (Unicode ranges and Code Page ranges).

    This is critical for Windows applications (like Excel) to recognize
    Chinese character support.

    Args:
        target_font: The font to update
        source_font: The source font (usually the CJK font)
    """
    if "OS/2" not in target_font or "OS/2" not in source_font:
        return

    target_os2 = target_font["OS/2"]
    source_os2 = source_font["OS/2"]

    # Merge Unicode Ranges (ulUnicodeRange1-4)
    # These are bit fields indicating supported Unicode blocks
    if hasattr(target_os2, "ulUnicodeRange1") and hasattr(source_os2, "ulUnicodeRange1"):
        target_os2.ulUnicodeRange1 |= source_os2.ulUnicodeRange1
        target_os2.ulUnicodeRange2 |= source_os2.ulUnicodeRange2
        target_os2.ulUnicodeRange3 |= source_os2.ulUnicodeRange3
        target_os2.ulUnicodeRange4 |= source_os2.ulUnicodeRange4
        print("  Merged OS/2 Unicode Ranges")

    # Merge Code Page Ranges (ulCodePageRange1-2)
    # These are bit fields indicating supported code pages (e.g. 936 for GBK)
    if hasattr(target_os2, "ulCodePageRange1") and hasattr(source_os2, "ulCodePageRange1"):
        target_os2.ulCodePageRange1 |= source_os2.ulCodePageRange1
        target_os2.ulCodePageRange2 |= source_os2.ulCodePageRange2
        print("  Merged OS/2 Code Page Ranges")


def is_cjk_codepoint(
    codepoint: int, cjk_ranges: Tuple[Tuple[int, int], ...]
) -> bool:
    """Check if a Unicode codepoint is in CJK ranges.

    Args:
        codepoint: Unicode codepoint
        cjk_ranges: Tuple of (start, end) ranges

    Returns:
        True if codepoint is in CJK ranges
    """
    for start, end in cjk_ranges:
        if start <= codepoint <= end:
            return True
    return False


def verify_glyph_width(
    font: TTFont, expected_widths: List[int], file_name: str | None = None,
    config: FontConfig | None = None,
) -> None:
    """Verify all glyph widths are in expected values.

    Args:
        font: TTFont object
        expected_widths: List of valid advance widths
        file_name: Optional file name for error messages

    Raises:
        ValueError: If glyphs with unexpected widths are found
    """
    unexpected = []
    hmtx = font["hmtx"]

    for name in font.getGlyphOrder():
        width, _ = hmtx[name]
        if width not in expected_widths and width != 0:
            unexpected.append((name, width))

    if config is not None:
        for cp, name in (font.getBestCmap() or {}).items():
            expected = config.codepoint_width(cp)
            if expected is not None and hmtx[name][0] != expected:
                unexpected.append((f"U+{cp:04X} {name} (expected {expected})", hmtx[name][0]))

    if not unexpected:
        print(f"Verified glyph widths in {file_name or 'font'}")
        return

    # Show first 10 unexpected glyphs
    sample = unexpected[:10]
    sample_str = "\n".join(f"  {name}: {width}" for name, width in sample)
    raise ValueError(
        f"Found {len(unexpected)} glyphs with unexpected widths "
        f"(expected {expected_widths}):\n{sample_str}"
    )


def normalize_zero_width_glyphs(font: TTFont) -> None:
    """Separate zero-width aliases from visible glyphs before setting metrics."""
    import copy
    cmap = font.getBestCmap() or {}
    visible = {gn for cp, gn in cmap.items() if not is_zero_width(cp)}
    remapped = {}
    # glyf.__setitem__ also appends to its live glyph order. Work on a copy
    # so cloned aliases occur only once when the order is installed below.
    order = list(font.getGlyphOrder())
    for cp, name in sorted(cmap.items()):
        if not is_zero_width(cp):
            continue
        target = name
        if name in visible:
            target = remapped.get(name)
            if target is None:
                target = f"{name}.zero"
                while target in font["glyf"].glyphs:
                    target += ".zero"
                font["glyf"][target] = copy.deepcopy(font["glyf"][name])
                order.append(target)
                remapped[name] = target
            for table in font["cmap"].tables:
                if table.isUnicode() and hasattr(table, "cmap") and cp in table.cmap:
                    table.cmap[cp] = target
        glyph = font["glyf"][target]
        font["hmtx"][target] = (0, glyph.xMin if glyph.numberOfContours else 0)
    font.setGlyphOrder(order)
