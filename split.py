import argparse
import re
import sys
import json
import shutil
import subprocess
import logging
import tempfile

from fontTools.ttLib import TTFont
from pathlib import Path
from typing import List

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from src.config import FontConfig
from src.licensing import copy_font_licenses

logger = logging.getLogger(__name__)

# Mapping from style key to display name for local() matching
STYLE_DISPLAY_NAMES = {
    "Regular": "Regular",
    "Medium": "Medium",
    "Italic": "Italic",
    "MediumItalic": "Medium Italic",
    "Bold": "Bold",
    "BoldItalic": "Bold Italic",
}

def check_cn_font_split_installed() -> bool:
    """Check if cn-font-split is installed."""
    return bool(get_cn_font_split_command())


def get_cn_font_split_command() -> List[str]:
    """Resolve the project-local tool or an installed command.

    Prefer the pinned project-local WASM core, avoiding native FFI crashes.
    """
    root = Path(__file__).parent
    wasm_core = root / "_tools/node_modules/cn-font-split/dist/libffi-wasm32-wasip1.wasm"
    if wasm_core.is_file() and shutil.which("node"):
        return [shutil.which("node"), str(root / "src/split_wasm.cjs")]
    executable = shutil.which("cn-font-split")
    if not executable:
        local_tool = root / "_tools" / ("cn-font-split.cmd" if sys.platform == "win32" else "bin/cn-font-split")
        if local_tool.is_file():
            executable = str(local_tool)
    return [executable] if executable else []


def enhance_local_font_matching(
    css_path: Path, family_name: str, style_key: str,
    full_name: str | None = None, postscript_name: str | None = None,
) -> None:
    """Use exact face names only; a family name can select the wrong weight."""
    if not css_path.is_file():
        raise FileNotFoundError(f"CSS file not found: {css_path}")
    full_name = full_name or f"{family_name} {STYLE_DISPLAY_NAMES.get(style_key, style_key)}"
    postscript_name = postscript_name or f"{family_name}-{style_key}"
    local_values = ",".join(f"local({json.dumps(name, ensure_ascii=False)})"
                            for name in dict.fromkeys((postscript_name, full_name)))
    content = css_path.read_text(encoding="utf-8")
    pattern = r"(?:local\((?:[^)]+)\)\s*,\s*)+(?=url\()"
    content = re.sub(pattern, lambda match: local_values + ",", content)
    css_path.write_text(content, encoding="utf-8")


def read_font_metadata(font_path: Path) -> dict:
    """Use the built face's names, weight and style instead of guessing filenames."""
    with TTFont(font_path) as font:
        names = font["name"]
        family = names.getDebugName(16) or names.getDebugName(1)
        style = names.getDebugName(17) or names.getDebugName(2) or "Regular"
        full_name = names.getDebugName(4)
        postscript_name = names.getDebugName(6)
        if not all((family, full_name, postscript_name)):
            raise ValueError(f"Missing font names in {font_path}")
        italic = bool(font["OS/2"].fsSelection & 1 or font["head"].macStyle & 2)
        return {"family": family, "style": style, "full_name": full_name,
                "postscript_name": postscript_name,
                "weight": str(font["OS/2"].usWeightClass),
                "css_style": "italic" if italic else "normal"}


def split_font(
    font_path: Path, output_base_dir: Path, config: FontConfig,
    test_html: bool = True,
) -> Path:
    """Generate and validate a face in a temporary directory before publishing."""
    command = get_cn_font_split_command()
    if not command:
        raise RuntimeError("cn-font-split is not installed. Run 'uv run python scripts/install_split.py'.")
    metadata = read_font_metadata(font_path)
    output_base_dir.mkdir(parents=True, exist_ok=True)
    output_base_dir = output_base_dir.resolve()
    output_dir = output_base_dir / font_path.stem
    # Refuse an existing symlink/junction pointing outside the intended output.
    if output_dir.resolve().parent != output_base_dir:
        raise ValueError(f"Output is outside the split directory: {output_dir}")
    logger.info(f"Splitting font: {font_path}")
    with tempfile.TemporaryDirectory(prefix=".font-split-", dir=output_base_dir) as temp_dir:
        staging = Path(temp_dir) / font_path.stem
        cmd = command + [
            "run", "-i", str(font_path.resolve()), "-o", str(staging),
            "--css.fontFamily", metadata["family"],
            "--css.fontWeight", metadata["weight"],
            "--css.fontStyle", metadata["css_style"],
            "--css.fontDisplay", "swap", "--renameOutputFont", "[index].[ext]",
            "--testHtml", str(test_html).lower(),
        ]
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to split {font_path.stem}: {e.stderr or e.stdout}")
            raise
        css_path = staging / "result.css"
        enhance_local_font_matching(css_path, metadata["family"], metadata["style"],
                                    metadata["full_name"], metadata["postscript_name"])
        subsets = list(staging.glob("*.woff2"))
        if not subsets:
            raise RuntimeError(f"No WOFF2 files generated for {font_path.name}")
        for subset in subsets:
            with subset.open("rb") as stream:
                if stream.read(4) != b"wOF2":
                    raise ValueError(f"Invalid WOFF2 file: {subset.name}")
        if test_html and not (staging / "index.html").is_file():
            raise RuntimeError(f"No preview generated for {font_path.name}")
        # Only replace this known generated face directory after a successful run.
        if output_dir.exists():
            shutil.rmtree(output_dir)
        staging.rename(output_dir)
    logger.info(f"Successfully split {font_path.stem} ({len(subsets)} subsets)")
    return output_dir


def generate_merged_css(split_dirs: List[Path], output_file: Path) -> None:
    """Generate a merged CSS file that imports all font subsets.

    This function reads the result.css from each split directory and creates a new
    CSS file that imports them.
    """
    logger.info(f"Generating merged CSS: {output_file}")

    import_statements = []

    for split_dir in split_dirs:
        css_file = split_dir / "result.css"
        if not css_file.exists():
            raise FileNotFoundError(f"CSS file not found: {css_file}")

        font_name = split_dir.name
        # Use relative path for import
        import_path = f"./{font_name}/result.css"
        import_statements.append(f'@import "{import_path}";')

    output_file.write_text("\n".join(import_statements), encoding="utf-8")
    logger.info("Merged CSS generated successfully")


def split_all_fonts(
    input_dir: Path,
    output_dir: Path,
    config: FontConfig,
) -> None:
    """Split all fonts in the input directory.

    Args:
        input_dir: Directory containing font files (e.g., output/)
        output_dir: Base directory for split output (e.g., output/split/)
        config: FontConfig object
    """
    if not input_dir.is_dir():
        raise FileNotFoundError(f"Input directory not found: {input_dir}")
    manifest_path = input_dir / "fonts-manifest.json"
    if manifest_path.is_file():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        filenames = [face["filename"] for face in manifest["fonts"]]
        font_files = []
        for filename in dict.fromkeys(filenames):
            if not isinstance(filename, str) or Path(filename).name != filename or not filename.lower().endswith(".ttf"):
                raise ValueError("Manifest font filenames must be local .ttf filenames")
            path = input_dir / filename
            if path.resolve().parent != input_dir.resolve() or not path.is_file():
                raise ValueError(f"Missing or external manifest font: {filename}")
            font_files.append(path)
    else:
        font_files = sorted(input_dir.glob("*.ttf"))
    if not font_files:
        raise ValueError(f"No .ttf files found in {input_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)

    split_dirs = []
    failures = []
    for font_file in font_files:
        try:
            split_dir = split_font(font_file, output_dir, config)
            split_dirs.append(split_dir)
        except Exception as e:
            logger.error(f"Error processing {font_file}: {e}")
            failures.append(font_file.name)

    # Generate merged CSS
    if failures:
        raise RuntimeError(f"Failed to split {len(failures)} font(s): {', '.join(failures)}")
    generate_merged_css(split_dirs, output_dir / "all.css")
    # Prefer the notices from the actual TTF build, including custom source fonts.
    notice_root = input_dir if (input_dir / "OFL.txt").is_file() else None
    copy_font_licenses(output_dir, source_root=notice_root)


def main():
    parser = argparse.ArgumentParser(
        description="Split fonts for web use using cn-font-split",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=Path(__file__).parent / "output/fonts",
        help="Input directory containing built fonts (default: output/fonts/)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).parent / "output/split",
        help="Output directory for split fonts (default: output/split/)",
    )

    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    # Initialize config
    config = FontConfig()

    print("\nSplitting fonts for web use...")
    try:
        split_all_fonts(args.input_dir, args.output_dir, config)
        print(f"Fonts split successfully! Output: {args.output_dir}")
    except Exception as e:
        print(f"Error splitting fonts: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
