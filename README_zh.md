# Pico

[English](README.md) | [中文](README_zh.md)

Pico 是由 Pcodcsja 独立维护的中英文 2:1 等宽衍生字体，基于 JetBrains Mono Nerd Fonts、霞鹜文楷和霞鹜臻楷制作，包含字符宽度调整、中文斜体处理和网页字体分包。Pico 非上述原作者或项目的官方发行版。

## 特性

- 英文字符来自 JetBrains Mono NerdFont
- 中日韩 (CJK) 字符来自霞鹜文楷屏幕阅读版等宽 GB (Regular/Medium) 和霞鹜臻楷 GB (Bold)
- 保留 NerdFont 图标并缩放至与中文等宽
  - Powerline 符号 (U+E0A0-U+E0DF) 保持原始垂直边界, 确保终端中正确对齐
  - 普通图标缩放 1.4 倍并垂直居中
- 完美 2:1 宽度比例 (中文 1200, 英文 600 FUnit)
- 字重: Regular, Medium, Italic, MediumItalic, Bold, BoldItalic
- 支持 YAML 配置文件, 可通过命令行覆盖
- 支持多字重中文字体映射 (可选)

## 1.8 更新 (2026-10-23)

- 修正传统 Windows 四样式分组：常规、斜体、粗体、粗斜体归入 `Pico`，中等和中等斜体归入 `Pico Medium`；支持现代字体分组的软件仍统一显示为 `Pico`。
- 为六款字体补全简体中文完整名称和样式名称，包括“Pico 粗体”“Pico 斜体”“Pico 粗斜体”。
- 同步名称和 Windows/macOS 粗体、斜体、常规标记，避免中等字重与常规字重冲突。

Windows 字体预览中的完整名称分别为：`Pico 常规`、`Pico 中等`、`Pico 粗体`、`Pico 斜体`、`Pico 中等斜体`、`Pico 粗斜体`。英文完整名称仍保留对应的 Regular、Medium、Bold、Italic 等样式名称。部分软件按字体家族分组时显示 `Pico`，具体字重和斜体在样式栏中选择。

## 1.7 更新 (2026-10-23)

- 成品字体独立命名为 **Pico**；同步更新内部名称、TTF 文件名、WOFF2 字体族、预览页和打包示例。
- 保留两套源字体的版权、商标声明与设计者署名，将修改版维护者单独标注。
- 桌面和网页输出自动附带 OFL、来源说明及适用的组件许可证。
- 原仓库地址保持不变；旧字体文件及 CSS 引用需要改为 `Pico`。

## 1.6 更新 (2026-10-21)

- 修复 Italic、MediumItalic、BoldItalic 的中文未倾斜问题：按英文源字体的倾角变换中文轮廓，当前为向右 9°，并保持 2:1 字宽。
- 中文使用轮廓倾斜生成；若中文源字体已有倾角，只补偿与英文的倾角差。

## 1.5 更新 (2026-10-21)

- 修复全角大括号、半角片假名字宽，并将零宽字符的占位宽度归零。
- 合入源字体已有的假名、韩文、兼容汉字及汉字扩展 H/I；不同字重使用不同源字体，字符覆盖可能有差别。
- 合并时独立处理复合字形与同名字形，并按 Unicode 字符类别校验字宽。
- 分包从字体元数据读取名称和字重；空输入或构建失败会返回错误。
- 通过 npm 锁文件与 WASM 核心 SHA-256 固定分包环境。执行 `uv run python scripts/install_split.py --split` 可安装后自动生成 Web 字体。

## 下载

### 快速选择

| 使用场景 | 下载文件 |
|---------|---------|
| 💻 **本地安装** (编辑器/IDE/终端) | `Pico.zip` |
| 🌐 **网页使用** (Web Fonts) | `Pico-split-woff2.zip` |
| 📄 **只需单个字重** | 选择对应的 `.ttf` 单文件 |

### 文件说明

#### `Pico.zip`
> **推荐大多数用户下载**

包含 6 个字重的完整 TTF 字体文件, 适用于:
- ✅ VSCode / JetBrains IDE / Sublime Text 等编辑器
- ✅ Windows Terminal / iTerm2 / Alacritty 等终端
- ✅ 系统全局安装

包含字重: Regular, Medium, Italic, MediumItalic, Bold, BoldItalic

#### `Pico-split-woff2.zip`
> **Web 开发者专用**

经过 [cn-font-split](https://github.com/KonghaYao/cn-font-split) 分包优化的 WOFF2 格式, 适用于:
- ✅ 网站/博客的 `@font-face` 引用
- ✅ 需要按需加载中文字符子集的场景
- ✅ 追求极致加载性能的 Web 项目

包含 `all.css` 可直接引用全部字重

#### 单字体文件 (`.ttf`)

如果你只需要特定字重, 可直接下载对应文件:

| 文件名 | 字重 | 适用场景 |
|-------|------|---------|
| `Pico-Regular.ttf` | 常规 | 日常编码 (推荐) |
| `Pico-Medium.ttf` | 中等 | 偏好稍粗字体 |
| `Pico-Bold.ttf` | 粗体 | 标题/强调 |
| `Pico-Italic.ttf` | 斜体 | 注释/变量 |
| `Pico-MediumItalic.ttf` | 中等斜体 | - |
| `Pico-BoldItalic.ttf` | 粗斜体 | - |

## 快速开始

### 使用 uv (推荐)

```bash
# 安装依赖
uv sync

# 构建所有字重
uv run python build.py

# 安装固定版本的分包工具并生成 Web 字体（需要 Node.js）
uv run python scripts/install_split.py --split
```

### 使用 Docker

```bash
# 构建镜像
docker build -t pico-mono .

# 运行构建
docker run --rm \
    -v $(pwd)/fonts:/app/fonts \
    -v $(pwd)/output:/app/output \
    pico-mono

# 构建指定字重
docker run --rm \
    -v $(pwd)/fonts:/app/fonts \
    -v $(pwd)/output:/app/output \
    pico-mono --styles Regular,Medium
```

## 源字体

请将以下字体文件放置在 `fonts/` 目录:

### JetBrains Mono NerdFont (v3.5.1)

从 [Nerd Fonts 发布页面](https://github.com/ryanoasis/nerd-fonts/releases/download/v3.5.1/JetBrainsMono.zip) 下载,解压后放置以下文件:

- `JetBrainsMonoNLNerdFontMono-Regular.ttf`
- `JetBrainsMonoNLNerdFontMono-Medium.ttf`
- `JetBrainsMonoNLNerdFontMono-Italic.ttf`
- `JetBrainsMonoNLNerdFontMono-MediumItalic.ttf`
- `JetBrainsMonoNLNerdFontMono-Bold.ttf`
- `JetBrainsMonoNLNerdFontMono-BoldItalic.ttf`

### 霞鹜文楷屏幕阅读版等宽 GB (v1.530)

直接下载: [LXGWWenKaiMonoGBScreen.ttf](https://github.com/lxgw/LxgwWenKai-Screen/releases/download/v1.530/LXGWWenKaiMonoGBScreen.ttf)

- `LXGWWenKaiMonoGBScreen.ttf` - 用于 Regular/Italic/Medium/MediumItalic 字重

### 霞鹜臻楷 GB (v0.825, 用于 Bold 字重)

直接下载: [LXGWZhenKaiGB-Regular.ttf](https://github.com/lxgw/LxgwZhenKai/releases/download/v0.825/LXGWZhenKaiGB-Regular.ttf)

- `LXGWZhenKaiGB-Regular.ttf` - 用于 Bold/BoldItalic 字重, 提供更粗的中文笔画

## 输出

- 生成的字体文件保存在 `output/fonts/` 目录。
- 分包后的 Web 字体保存在 `output/split/` 目录。

## 字体分包 (Web 字体)

项目包含一个 `split.py` 脚本, 使用 [cn-font-split](https://github.com/KonghaYao/cn-font-split) 将字体分割为 woff2 子集, 用于 Web 分发:

```bash
# 安装 cn-font-split (需要 Node.js)
uv run python scripts/install_split.py

# 运行分包脚本 (自动处理 output/fonts 下的所有字体)
uv run python split.py

# 自定义目录
uv run python split.py --input-dir my_fonts --output-dir my_split_fonts
```

输出结构:

```
output/split/
├── all.css                  # 合并所有字体的 CSS 引用
├── Pico-Regular/
│   ├── result.css           # 单个字体的 CSS
│   ├── index.html           # 测试页面 (包含分包验证报告)
│   └── *.woff2              # 字体子集
└── ...
```

分包完成后，您可以直接打开 `output/split/<FontName>/index.html` 查看该字体的分包验证报告和预览效果。

> **注意**: 由于浏览器跨域安全策略 (CORS)，直接双击打开 `index.html` 可能无法正常加载字体文件或 JSON 报告。请使用本地 HTTP 服务器查看:
>
> ```bash
> uv run python -m http.server 8000
> # 访问 http://localhost:8000/output/split/<FontName>/index.html
> ```

## 2:1 比例验证

验证中英文字符的完美 2:1 宽度比例:

```bash
# 启动本地 HTTP 服务器打开验证页面
uv run python -m http.server 8000
# 然后访问 http://localhost:8000/verify-2-1.html
```

验证页面现已支持通过下拉菜单切换不同的字重。

对于分包后的 Web 字体，请访问 `http://localhost:8000/verify-2-1-split.html` 进行验证。

或者构建字体后直接在浏览器中打开 `verify-2-1.html`。

![2:1 比例验证](resources/2-1.png)

竖线 (`|`) 应该在所有行之间完美对齐,展示每个中文字符的宽度恰好是英文字符的两倍。

## 命令行选项

### 构建脚本 (build.py)

```
用法: build.py [-h] [--config CONFIG] [--styles STYLES] [--fonts-dir FONTS_DIR]
                [--output-dir OUTPUT_DIR] [--parallel PARALLEL]

选项:
  --config CONFIG         配置文件路径 (默认: config.yaml)
  --styles STYLES         逗号分隔的字重列表 (默认: 从配置文件读取)
  --fonts-dir FONTS_DIR   源字体目录 (默认: fonts/)
  --output-dir OUTPUT_DIR 输出目录 (默认: output/fonts/)
  --parallel PARALLEL     并行工作进程数 (默认: 1)
```

配置优先级: 命令行参数 > config.yaml > 默认值

## 配置文件

`config.yaml` 文件提供集中式的构建配置:

```yaml
# 字体元数据
font:
  family_name: "Pico"
  version: "1.8"
  author: "Pcodcsja (Pico derivative maintainer)"
  copyright: "Copyright (c) 2026 Pcodcsja (Pico modifications). Source font copyright notices are retained."
  description: "Pico, an independently maintained 2:1 CJK monospace derivative. Not an official release of the source projects."
  url: "https://github.com/Pcodcsja/PicoMono"
  license: "This font is licensed under the SIL Open Font License, Version 1.1."
  license_url: "https://openfontlicense.org"

# 源字体目录
fonts_dir: "fonts"

# 字重配置
styles:
  Regular:
    en_font: "JetBrainsMonoNLNerdFontMono-Regular.ttf"
    cn_font: "LXGWWenKaiMonoGBScreen.ttf"
    display_name: "Regular"
  # ... 其他字重

# 构建选项
build:
  styles: "Regular,Medium,Italic,MediumItalic,Bold,BoldItalic"
  output_dir: "output/fonts"
  parallel: 6

# 字形宽度配置 (2:1 比例)
width:
  en_width: 600
  cn_width: 1200
  # CJK 视觉缩放因子 (1.0 = 无缩放, 1.08 = 放大 8%)
  visual_scale: 1.08
```

### 多字重中文字体示例

如果中文字体有多个字重, 为每个样式指定不同的 `cn_font`:

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
    cn_font: "LXGWWenKaiMonoGBScreen-Medium.ttf"  # 回退到 Medium
    display_name: "Bold"
```

### 分包脚本 (split.py)

```
用法: split.py [-h] [--input-dir INPUT_DIR] [--output-dir OUTPUT_DIR]

选项:
  --input-dir INPUT_DIR   包含字体文件的输入目录 (默认: output/fonts)
  --output-dir OUTPUT_DIR 分包字体的输出目录 (默认: output/split)
```

## 项目结构

```
.
├── fonts/                  # 源字体
├── output/                 # 输出目录
│   ├── fonts/              # 生成的 TTF 字体
│   │   └── fonts-manifest.json  # 字体元数据(用于验证页面)
│   └── split/              # 生成的 Web 字体 (WOFF2)
├── src/
│   ├── __init__.py
│   ├── config.py           # 字体配置
│   ├── merge.py            # 核心合并逻辑
│   └── utils.py            # 工具函数
├── build.py                # 主构建脚本
├── split.py                # 字体分包脚本
├── config.yaml             # 构建配置
├── pyproject.toml          # Python 项目配置
├── Dockerfile              # Docker 构建
└── README.md
```

## 致谢

- [maple-font](https://github.com/subframe7536/maple-font): 本项目的实现方案参考来源
- [Nerd Fonts](https://github.com/ryanoasis/nerd-fonts): 提供了丰富的开发者图标
- [霞鹜文楷](https://github.com/lxgw/LxgwWenKai): 优秀的开源中文字体
- [霞鹜臻楷](https://github.com/lxgw/LxgwZhenKai): 霞鹜文楷的粗体版本
- [JetBrains Mono](https://github.com/JetBrains/JetBrainsMono): 优秀的编程等宽字体
- [cn-font-split](https://github.com/KonghaYao/cn-font-split): 强大的 Web 字体分包工具

## 许可证

生成的 Pico 字体按 [SIL Open Font License 1.1](OFL.txt) 分发，保留原字体版权和设计者署名。分发 TTF 或 WOFF2 时，请保留 `OFL.txt`、[NOTICE.md](NOTICE.md) 和 `licenses/`；构建脚本会自动复制这些文件。

- JetBrains Mono、霞鹜文楷、霞鹜臻楷：OFL-1.1，详见 `licenses/` 中的原始许可证和源字体声明。
- Nerd Fonts：字体、图标组件和工具代码应分别说明许可证，不能统一写成 MIT。适用的来源声明和组件许可证随包附带。
- 合并项目参考自 [lvbibir/JetBrainsLxgwNerdMono](https://github.com/lvbibir/JetBrainsLxgwNerdMono)，保留其代码贡献署名。字体 OFL 声明不代表对上游脚本或第三方工具重新授权。
- Pico 为独立维护的衍生版，未声明获得原作者背书。来源名称仅用于版权、来源和致谢说明。
