"""Bundle font licenses with both desktop and web output."""

import shutil
import hashlib
from pathlib import Path
from typing import Iterable

from fontTools.ttLib import TTFont


def copy_font_licenses(output_dir: Path, source_root: Path | None = None) -> None:
    """Keep required notices alongside generated font distributions."""
    root = source_root if source_root is not None else Path(__file__).resolve().parents[1]
    source_dir = root / "licenses"
    required = [root / "OFL.txt", root / "NOTICE.md"]
    for path in required:
        if not path.is_file():
            raise FileNotFoundError(f"Missing font license notice: {path}")
    if not source_dir.is_dir() or not any(source_dir.iterdir()):
        raise FileNotFoundError(f"Missing source font licenses: {source_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)
    for path in required:
        shutil.copy2(path, output_dir / path.name)
    shutil.copytree(source_dir, output_dir / "licenses", dirs_exist_ok=True)


def write_source_font_notices(source_fonts: Iterable[Path], output_file: Path) -> None:
    """Record the actual build inputs rather than a fixed template's metadata."""
    sections = []
    labels = {0: "Copyright", 5: "Version", 7: "Trademark", 8: "Manufacturer",
              9: "Designer", 13: "License", 14: "License URL"}
    for path in sorted(set(source_fonts)):
        lines = [f"File: {path.name}", f"SHA-256: {hashlib.sha256(path.read_bytes()).hexdigest()}"]
        with TTFont(path, lazy=True) as font:
            for name_id, label in labels.items():
                values = list(dict.fromkeys(record.toUnicode() for record in font["name"].names
                                           if record.nameID == name_id and record.toUnicode().strip()))
                if values:
                    lines.append(label + ":\n" + "\n\n".join(values))
        sections.append("\n\n".join(lines))
    output_file.write_text(("\n\n" + "=" * 72 + "\n\n").join(sections) + "\n", encoding="utf-8")
