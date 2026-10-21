from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen


def rectangle(x=100, y=100, size=400):
    pen = TTGlyphPen(None)
    pen.moveTo((x, y))
    pen.lineTo((x + size, y))
    pen.lineTo((x + size, y + size))
    pen.lineTo((x, y + size))
    pen.closePath()
    return pen.glyph()


def empty():
    return TTGlyphPen(None).glyph()


def make_font(path, upm, glyphs, cmap, width, family="Example", style="Regular", weight=400):
    builder = FontBuilder(upm, isTTF=True)
    glyphs = {".notdef": empty(), **glyphs}
    builder.setupGlyphOrder(list(glyphs))
    builder.setupCharacterMap(cmap)
    builder.setupGlyf(glyphs)
    builder.setupHorizontalMetrics({name: (width, glyph.xMin if glyph.numberOfContours else 0)
                                    for name, glyph in glyphs.items()})
    builder.setupHorizontalHeader(ascent=upm, descent=-upm // 4)
    builder.setupNameTable({"familyName": family, "styleName": style,
                            "fullName": f"{family} {style}",
                            "psName": family.replace(" ", "") + "-" + style.replace(" ", ""),
                            "version": "Version 1.0"})
    builder.setupOS2(sTypoAscender=upm, sTypoDescender=-upm // 4,
                     usWinAscent=upm, usWinDescent=upm // 4,
                     usWeightClass=weight, fsSelection=1 if "Italic" in style else 0x40)
    builder.setupPost()
    builder.setupMaxp()
    builder.save(path)


def source_pair(root):
    base = root / "base.ttf"
    cn = root / "cn.ttf"
    make_font(base, 1000, {"space": empty(), "collision": rectangle()},
              {0x20: "space", 0x41: "collision", 0xFF5B: "collision",
               0x200B: "space", 0xFEFF: "space"}, 600)
    part = rectangle(0, 0, 500)
    pen = TTGlyphPen({"part": part})
    pen.addComponent("part", (1, 0, 0, 1, 500, 200))
    glyphs = {"collision": rectangle(100, 100, 1800), "half": rectangle(),
              "mark": rectangle(), "part": part, "composite": pen.glyph()}
    cmap = {cp: "collision" for cp in (0x4E00, 0xFF5B, 0x3042, 0xAC00,
                                       0xFA0C, 0x31350, 0x2EBF0)}
    cmap.update({0x4E8C: "composite", 0xFF71: "half", 0x3099: "mark"})
    make_font(cn, 2000, glyphs, cmap, 2000)
    return base, cn
