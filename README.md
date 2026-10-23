# Pico

[English](README.md) | [中文](README_zh.md)

Pico is an independently maintained 2:1 CJK monospace derivative by Pcodcsja, based on JetBrains Mono Nerd Fonts, LXGW WenKai Mono and LXGW ZhenKai. It includes character-width adjustments, CJK obliques and web subsets. Pico is not an official release of the source projects.

## Features

- English characters from JetBrains Mono NerdFont
- CJK characters from LXGW WenKai Mono GB Screen (Regular/Medium) and LXGW ZhenKai GB (Bold)
- NerdFont icons preserved and scaled to match CJK width
  - Powerline symbols (U+E0A0-U+E0DF) maintain original vertical bounds for proper terminal alignment
  - Regular icons scaled 1.4x and vertically centered
- Perfect 2:1 width ratio (CJK 1200, English 600 FUnit)
- Styles: Regular, Medium, Italic, MediumItalic, Bold, BoldItalic
- YAML configuration support with CLI override
- Multi-weight Chinese font mapping (optional)

## Version 1.8 (2026-10-23)

- Fix legacy Windows style linking: four RIBBI faces use `Pico`; Medium and Medium Italic use `Pico Medium`. Typographic family names remain `Pico` for all six faces.
- Add distinct Simplified Chinese full names and style names for all six faces.
- Synchronize Windows/macOS bold, italic and regular flags with the legacy grouping.

Each face has a distinct English full name (for example `Pico Bold Italic`) and a Simplified Chinese full name for Windows preview. Applications that group by typographic family may show `Pico` as the family and expose the weight and italic face in a separate style selector.

## Version 1.7 (2026-10-23)

- Rename the derivative to **Pico**, including internal names, TTF filenames, WOFF2 families, previews and packaging examples.
- Preserve both source fonts' copyright, trademark and designer attribution; identify the derivative maintainer separately.
- Bundle OFL, attribution and component license notices with desktop and web output.
- Keep the repository URL; update old font filenames and CSS references to `Pico`.

## Version 1.6 (2026-10-21)

- Fix upright CJK outlines in Italic, MediumItalic and BoldItalic by matching the English source slant (currently 9° to the right), preserving the 2:1 advance widths.
- Generate CJK obliques by shearing the outlines; compensate only for the angle difference when the CJK source already has a slant.

## Version 1.5 (2026-10-21)

- Correct fullwidth braces and halfwidth kana advances; normalize zero-width characters.
- Import kana, Hangul, compatibility ideographs and CJK extensions H/I where the source font contains them. Coverage can differ between weights because they use different source fonts.
- Merge composites independently of source glyph names and validate widths by Unicode character class.
- Read Web font names and weights from built font metadata; empty inputs and failed builds return errors.
- Pin the Web tooling with an npm lockfile and a SHA-256-verified WASM core. Run `uv run python scripts/install_split.py --split` to install and generate Web fonts.

## Download

### Quick Selection

| Use Case | Download |
|----------|----------|
| 💻 **Local Install** (Editor/IDE/Terminal) | `Pico.zip` |
| 🌐 **Web Usage** (Web Fonts) | `Pico-split-woff2.zip` |
| 📄 **Single Weight Only** | Choose the corresponding `.ttf` file |

### File Description

#### `Pico.zip`
> **Recommended for most users**

Contains 6 complete TTF font files with all weights, suitable for:
- ✅ VSCode / JetBrains IDE / Sublime Text and other editors
- ✅ Windows Terminal / iTerm2 / Alacritty and other terminals
- ✅ System-wide installation

Included weights: Regular, Medium, Italic, MediumItalic, Bold, BoldItalic

#### `Pico-split-woff2.zip`
> **For Web developers**

WOFF2 format optimized with [cn-font-split](https://github.com/KonghaYao/cn-font-split), suitable for:
- ✅ Website/blog `@font-face` references
- ✅ On-demand loading of CJK character subsets
- ✅ Web projects requiring optimal loading performance

Includes `all.css` for importing all weights at once

#### Single Font Files (`.ttf`)

If you only need a specific weight, download the corresponding file directly:

| File | Weight | Use Case |
|------|--------|----------|
| `Pico-Regular.ttf` | Regular | Daily coding (Recommended) |
| `Pico-Medium.ttf` | Medium | Prefer slightly bolder font |
| `Pico-Bold.ttf` | Bold | Headings/emphasis |
| `Pico-Italic.ttf` | Italic | Comments/variables |
| `Pico-MediumItalic.ttf` | Medium Italic | - |
| `Pico-BoldItalic.ttf` | Bold Italic | - |

## Quick Start

### Using uv (Recommended)

```bash
# Install dependencies
uv sync

# Build all styles
uv run python build.py

# Install the locked Web font tooling and generate subsets (requires Node.js)
uv run python scripts/install_split.py --split
```

### Using Docker

```bash
# Build image
docker build -t pico-mono .

# Run build
docker run --rm \
    -v $(pwd)/fonts:/app/fonts \
    -v $(pwd)/output:/app/output \
    pico-mono

# Build specific styles
docker run --rm \
    -v $(pwd)/fonts:/app/fonts \
    -v $(pwd)/output:/app/output \
    pico-mono --styles Regular,Medium
```

## Source Fonts

Place the following fonts in the `fonts/` directory:

### JetBrains Mono NerdFont (v3.5.1)

Download from [Nerd Fonts release](https://github.com/ryanoasis/nerd-fonts/releases/download/v3.5.1/JetBrainsMono.zip), extract and place these files:

- `JetBrainsMonoNLNerdFontMono-Regular.ttf`
- `JetBrainsMonoNLNerdFontMono-Medium.ttf`
- `JetBrainsMonoNLNerdFontMono-Italic.ttf`
- `JetBrainsMonoNLNerdFontMono-MediumItalic.ttf`
- `JetBrainsMonoNLNerdFontMono-Bold.ttf`
- `JetBrainsMonoNLNerdFontMono-BoldItalic.ttf`

### LXGW WenKai Mono GB Screen (v1.530)

Download directly: [LXGWWenKaiMonoGBScreen.ttf](https://github.com/lxgw/LxgwWenKai-Screen/releases/download/v1.530/LXGWWenKaiMonoGBScreen.ttf)

- `LXGWWenKaiMonoGBScreen.ttf` - Used for Regular/Italic/Medium/MediumItalic styles

### LXGW ZhenKai GB (v0.825, for Bold weights)

Download directly: [LXGWZhenKaiGB-Regular.ttf](https://github.com/lxgw/LxgwZhenKai/releases/download/v0.825/LXGWZhenKaiGB-Regular.ttf)

- `LXGWZhenKaiGB-Regular.ttf` - Used for Bold/BoldItalic styles to provide heavier CJK strokes

## Output

- Generated fonts are saved to `output/fonts/`.
- Split web fonts are saved to `output/split/`.

## Font Splitting (Web Fonts)

The project includes a `split.py` script that uses [cn-font-split](https://github.com/KonghaYao/cn-font-split) to split fonts into woff2 subsets for web delivery:

```bash
# Install cn-font-split (requires Node.js)
uv run python scripts/install_split.py

# Run split script (processes all fonts in output/fonts)
uv run python split.py

# Custom directories
uv run python split.py --input-dir my_fonts --output-dir my_split_fonts
```

Output structure:

```
output/split/
├── all.css                  # Merged CSS importing all fonts
├── Pico-Regular/
│   ├── result.css           # Single font CSS
│   ├── index.html           # Test page (contains splitting report)
│   └── *.woff2              # Font subsets
└── ...
```

After splitting, you can open `output/split/<FontName>/index.html` to view the splitting report and preview the font.

> **Note**: Due to browser CORS policies, directly opening `index.html` may fail to load font files or JSON reports. Please use a local HTTP server:
>
> ```bash
> uv run python -m http.server 8000
> # Visit http://localhost:8000/output/split/<FontName>/index.html
> ```

## 2:1 Ratio Verification

To verify the perfect 2:1 width ratio between CJK and English characters:

```bash
# Open verification page in browser
uv run python -m http.server 8000
# Then visit http://localhost:8000/verify-2-1.html
```

The verification page supports switching between different font weights using the dropdown menu.

For split web fonts, please visit `http://localhost:8000/verify-2-1-split.html`.

Or simply open `verify-2-1.html` directly in your browser after building the fonts.

![2:1 Ratio Verification](resources/2-1.png)

The vertical bars (`|`) should align perfectly across all lines, demonstrating that each CJK character occupies exactly twice the width of an English character.

## Command Line Options

### Build Script (build.py)

```
usage: build.py [-h] [--config CONFIG] [--styles STYLES] [--fonts-dir FONTS_DIR]
                [--output-dir OUTPUT_DIR] [--parallel PARALLEL]

options:
  --config CONFIG         Path to config.yaml (default: config.yaml)
  --styles STYLES         Comma-separated styles (default: from config)
  --fonts-dir FONTS_DIR   Source fonts directory (default: fonts/)
  --output-dir OUTPUT_DIR Output directory (default: output/fonts/)
  --parallel PARALLEL     Parallel workers (default: 1)
```

Configuration priority: CLI args > config.yaml > defaults

## Configuration

The `config.yaml` file provides centralized configuration for the build process:

```yaml
# Font metadata
font:
  family_name: "Pico"
  version: "1.8"
  author: "Pcodcsja (Pico derivative maintainer)"
  copyright: "Copyright (c) 2026 Pcodcsja (Pico modifications). Source font copyright notices are retained."
  description: "Pico, an independently maintained 2:1 CJK monospace derivative. Not an official release of the source projects."
  url: "https://github.com/Pcodcsja/PicoMono"
  license: "This font is licensed under the SIL Open Font License, Version 1.1."
  license_url: "https://openfontlicense.org"

# Source fonts directory
fonts_dir: "fonts"

# Styles configuration
styles:
  Regular:
    en_font: "JetBrainsMonoNLNerdFontMono-Regular.ttf"
    cn_font: "LXGWWenKaiMonoGBScreen.ttf"
    display_name: "Regular"
  # ... other styles

# Build options
build:
  styles: "Regular,Medium,Italic,MediumItalic,Bold,BoldItalic"
  output_dir: "output/fonts"
  parallel: 6

# Glyph width configuration (2:1 ratio)
width:
  en_width: 600
  cn_width: 1200
  # CJK visual scale factor (1.0 = no extra scaling, 1.08 = 8% larger)
  visual_scale: 1.08
```

### Multi-Weight Chinese Font Example

For Chinese fonts with multiple weights, specify different `cn_font` for each style:

```yaml
styles:
  Regular:
    en_font: "JetBrainsMonoNLNerdFontMono-Regular.ttf"
    cn_font: "LXGWWenKaiMonoGBScreen-Regular.ttf"
    display_name: "Regular"
  Medium:
    en_font: "JetBrainsMonoNLNerdFontMono-Medium.ttf"
    cn_font: "LXGWWenKaiMonoGBScreen-Medium.ttf"
    display_name: "Medium"
  Bold:
    en_font: "JetBrainsMonoNLNerdFontMono-Bold.ttf"
    cn_font: "LXGWWenKaiMonoGBScreen-Medium.ttf"  # Fallback to Medium
    display_name: "Bold"
```

### Split Script (split.py)

```
usage: split.py [-h] [--input-dir INPUT_DIR] [--output-dir OUTPUT_DIR]

options:
  --input-dir INPUT_DIR   Input directory containing font files (default: output/fonts)
  --output-dir OUTPUT_DIR Output directory for split fonts (default: output/split)
```

## Project Structure

```
.
├── fonts/                  # Source fonts
├── output/                 # Output directory
│   ├── fonts/              # Generated TTF fonts
│   │   └── fonts-manifest.json  # Font metadata for verification pages
│   └── split/              # Generated Web fonts (WOFF2)
├── src/
│   ├── __init__.py
│   ├── config.py           # Font configuration
│   ├── merge.py            # Core merge logic
│   └── utils.py            # Utility functions
├── build.py                # Main build script
├── split.py                # Font splitting script
├── config.yaml             # Build configuration
├── pyproject.toml          # Python project config
├── Dockerfile              # Docker build
└── README.md
```

## Acknowledgments

- [maple-font](https://github.com/subframe7536/maple-font): Implementation reference and inspiration
- [Nerd Fonts](https://github.com/ryanoasis/nerd-fonts): Developer icons
- [LXGW WenKai](https://github.com/lxgw/LxgwWenKai): Source CJK font for Regular/Medium weights
- [LXGW ZhenKai](https://github.com/lxgw/LxgwZhenKai): Source CJK font for Bold weights
- [JetBrains Mono](https://github.com/JetBrains/JetBrainsMono): Source English font
- [cn-font-split](https://github.com/KonghaYao/cn-font-split): Web font splitting tool

## License

Generated Pico fonts are distributed under the [SIL Open Font License 1.1](OFL.txt), retaining original copyright and designer attribution. Include `OFL.txt`, [NOTICE.md](NOTICE.md) and `licenses/` with TTF files and WOFF2 subsets; the build scripts copy these automatically.

- JetBrains Mono, LXGW WenKai and LXGW ZhenKai: OFL-1.1; original license text and source notices are in `licenses/`.
- Nerd Fonts: fonts, icon components and tool code have distinct licensing. They must not be collectively labeled MIT; applicable notices and component licenses are bundled.
- The merge implementation derives from [lvbibir/JetBrainsLxgwNerdMono](https://github.com/lvbibir/JetBrainsLxgwNerdMono), whose contribution credit is retained. The font OFL declaration does not relicense inherited scripts or third-party tools.
- Pico is an independent derivative without a claim of endorsement. Source names identify origin and attribution only.
