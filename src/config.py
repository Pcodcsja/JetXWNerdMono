"""Font configuration for JetBrainsLxgwNerdMono."""

from dataclasses import dataclass
from typing import Tuple
import math
import unicodedata


def is_zero_width(codepoint: int) -> bool:
    """Characters which must not consume a text cell."""
    return (
        unicodedata.category(chr(codepoint)) in ("Mn", "Me")
        or codepoint in (0x200B, 0x200C, 0x200D, 0x200E, 0x200F, 0xFEFF)
        or 0x202A <= codepoint <= 0x202E
        or 0x2060 <= codepoint <= 0x206F
        or 0xFE00 <= codepoint <= 0xFE0F
        or 0xE0100 <= codepoint <= 0xE01EF
    )


@dataclass
class FontConfig:
    """Configuration for font building."""

    # Font naming
    family_name: str = "JetBrainsLxgwNerdMono"
    family_name_compact: str = "JetBrainsLxgwNerdMono"
    version: str = "1.6"

    # CJK visual scale factor (1.0 = no extra scaling, 1.08 = 8% larger)
    visual_scale: float = 1.08

    # Glyph width configuration (2:1 ratio)
    en_width: int = 600  # English character width
    cn_width: int = 1200  # CJK character width (2x)

    # CJK Unicode ranges
    cjk_ranges: Tuple[Tuple[int, int], ...] = (
        (0x4E00, 0x9FFF),  # CJK Unified Ideographs
        (0x3400, 0x4DBF),  # CJK Unified Ideographs Extension A
        (0x20000, 0x2A6DF),  # CJK Unified Ideographs Extension B
        (0x2A700, 0x2B73F),  # CJK Unified Ideographs Extension C
        (0x2B740, 0x2B81F),  # CJK Unified Ideographs Extension D
        (0x2B820, 0x2CEAF),  # CJK Unified Ideographs Extension E
        (0x2CEB0, 0x2EBEF),  # CJK Unified Ideographs Extension F
        (0x2EBF0, 0x2EE5F),  # CJK Unified Ideographs Extension I
        (0x30000, 0x3134F),  # CJK Unified Ideographs Extension G
        (0x31350, 0x323AF),  # CJK Unified Ideographs Extension H
        (0xF900, 0xFAFF),  # CJK Compatibility Ideographs
        (0x2F800, 0x2FA1F),  # CJK Compatibility Ideographs Supplement
        (0x3000, 0x303F),  # CJK Symbols and Punctuation
        (0x3040, 0x30FF),  # Hiragana and Katakana
        (0x31F0, 0x31FF),  # Katakana Phonetic Extensions
        (0x1AFF0, 0x1AFFF),  # Kana Extended-B
        (0x1B000, 0x1B16F),  # Kana Supplement, Extended-A, Small Kana
        (0x1100, 0x11FF),  # Hangul Jamo
        (0x3130, 0x318F),  # Hangul Compatibility Jamo
        (0xA960, 0xA97F),  # Hangul Jamo Extended-A
        (0xAC00, 0xD7AF),  # Hangul Syllables
        (0xD7B0, 0xD7FF),  # Hangul Jamo Extended-B
        (0xFF00, 0xFFEF),  # Halfwidth and Fullwidth Forms
        (0x2E80, 0x2EFF),  # CJK Radicals Supplement
        (0x2F00, 0x2FDF),  # Kangxi Radicals
        (0x3100, 0x312F),  # Bopomofo
        (0x31A0, 0x31BF),  # Bopomofo Extended
        (0x31C0, 0x31EF),  # CJK Strokes
        (0x3200, 0x32FF),  # Enclosed CJK Letters and Months
        (0x3300, 0x33FF),  # CJK Compatibility
        (0xFE30, 0xFE4F),  # CJK Compatibility Forms
    )

    def __post_init__(self) -> None:
        if type(self.en_width) is not int or self.en_width <= 0:
            raise ValueError("en_width must be a positive integer")
        if type(self.cn_width) is not int or self.cn_width != 2 * self.en_width:
            raise ValueError("cn_width must be exactly 2 * en_width")
        if not math.isfinite(self.visual_scale) or self.visual_scale <= 0:
            raise ValueError("visual_scale must be positive and finite")

    def codepoint_width(self, codepoint: int) -> int | None:
        """Return a semantic cell width, or None for other characters."""
        if is_zero_width(codepoint):
            return 0
        if any(start <= codepoint <= end for start, end in self.cjk_ranges):
            return self.en_width if unicodedata.east_asian_width(chr(codepoint)) == "H" else self.cn_width
        if 0x20 <= codepoint <= 0x7E:
            return self.en_width
        return None
