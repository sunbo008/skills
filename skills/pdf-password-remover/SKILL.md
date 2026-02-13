# PDF 权限密码移除工具

移除 PDF 文件的 **owner/permission 密码**，解锁打印、复制、编辑等受限操作。使用 libqpdf C++ API 直接操作 PDF，独立二进制无额外运行时依赖。

## PDF 密码类型说明

| 类型 | 名称 | 效果 | 本工具支持 |
|------|------|------|-----------|
| User Password | 打开密码 | 无密码无法查看 PDF | ❌ 不处理 |
| Owner Password | 权限密码 | 可查看但限制操作 | ✅ 可移除 |

## 目录结构

```
pdf-password-remover/
├── SKILL.md              ← 本文件
└── cpp/
    ├── CMakeLists.txt     ← CMake 构建配置
    ├── pdf_unlock.cpp     ← 源码 (libqpdf 原生 API)
    └── build/
        └── pdf_unlock     ← 编译后可执行文件
```

## 构建

```bash
cd cpp
mkdir -p build && cd build
cmake ..
cmake --build .
```

## 依赖

- **libqpdf**: `brew install qpdf`
- **CMake** >= 3.16
- **C++17** 编译器

## 快速开始

```bash
# 查看 PDF 加密信息
./pdf_unlock input.pdf --info

# 解密单个文件（输出为 input_已解锁.pdf）
./pdf_unlock input.pdf

# 指定输出文件名
./pdf_unlock input.pdf -o output.pdf

# 批量解密目录下所有 PDF
./pdf_unlock /path/to/pdfs/ --batch

# 递归批量解密（含子目录）
./pdf_unlock /path/to/pdfs/ --batch -r
```

## 命令行参数

| 参数 | 说明 |
|------|------|
| `input` | PDF 文件或目录路径 |
| `-o, --output` | 输出路径（默认: 原名_已解锁.pdf） |
| `-p, --password` | 已知密码（可选） |
| `--batch` | 批量处理模式 |
| `-r, --recursive` | 递归子目录（配合 --batch） |
| `--info` | 仅查看加密信息 |
| `--no-color` | 禁用颜色输出 |
| `-h, --help` | 显示帮助信息 |
