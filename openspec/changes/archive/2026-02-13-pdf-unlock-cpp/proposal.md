## Why

现有 PDF 权限密码移除工具基于 Python (pikepdf/qpdf CLI) 实现。需要提供一个纯 C++ 版本，直接链接 libqpdf 库，具备更好的性能和可独立部署能力（无需 Python 运行时）。测试样张 `/Users/lengzhifeng/Documents/加密测试.pdf` 证实了 RC4 加密 + Owner Password 的典型场景。

## What Changes

- 新增 C++ 命令行工具 `pdf_unlock`，功能对齐现有 Python 版
- 使用 libqpdf C++ API 作为唯一引擎（不再需要双引擎备选）
- 支持：查看加密信息 (`--info`)、单文件解密、批量/递归解密、指定输出路径、提供已知密码
- 输出命名规则保持一致：`原文件名_已解锁.pdf`

## Capabilities

### New Capabilities
- `encryption-info`: 读取并展示 PDF 加密状态、加密版本、权限限制列表
- `single-unlock`: 单文件权限密码移除，支持自定义输出路径和已知密码
- `batch-unlock`: 批量/递归解密目录下所有 PDF 文件
- `result-verify`: 解密后自动验证输出文件完整性和加密状态

### Modified Capabilities

（无，本次为全新 C++ 实现）

## Impact

- **新增文件**: `skills/pdf-password-remover/cpp/` 目录（CMakeLists.txt + 源码 + 测试）
- **依赖**: libqpdf (brew install qpdf)，CMake >= 3.16，C++17
- **不影响**: 现有 Python 版本 `scripts/pdf_unlock.py` 保持不变
