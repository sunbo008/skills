## Context

现有 Python 版本 (`scripts/pdf_unlock.py`) 使用 pikepdf + qpdf CLI 双引擎策略。C++ 版本直接链接 libqpdf C++ API，不需要双引擎。目标环境为 macOS (Homebrew 安装的 qpdf 12.x)，使用 CMake 构建，C++17 标准。

测试样张特征: RC4 加密, R=4, V=4, P=-3392, 仅 Owner Password (空 User Password), 7项操作受限。

## Goals / Non-Goals

**Goals:**
- 功能完全对齐 Python 版 (info / 单文件 / 批量 / 递归 / 密码 / 输出路径)
- 使用 libqpdf C++ API 直接操作，零外部进程调用
- 解密后自动验证输出文件完整性
- 清晰的终端彩色输出

**Non-Goals:**
- 不处理 User Password (打开密码) 的暴力破解
- 不支持 GUI 界面
- 不支持 Windows/Linux 构建 (仅 macOS Homebrew)
- 不实现 PDF 内容修改或重加密功能

## Decisions

### Decision 1: 单文件架构 (不拆分头文件)

**选择**: 所有代码放在一个 `pdf_unlock.cpp` 文件中
**理由**: 这是一个功能明确的 CLI 工具，总代码量预计 400-500 行，拆分头文件增加不必要的复杂性。如果未来需要作为库使用，再重构提取。
**替代方案**: 拆分为 `pdf_info.h/cpp` + `pdf_unlock.h/cpp` + `main.cpp` — 过度设计。

### Decision 2: libqpdf 单引擎

**选择**: 仅使用 libqpdf C++ API (QPDF + QPDFWriter)
**理由**: C++ 版本直接链接 libqpdf，不再需要 qpdf CLI 作为备选引擎。pikepdf 底层也是 qpdf。
**核心 API**:
- `QPDF::processFile()` — 打开 PDF
- `QPDF::isEncrypted()` — 检测加密
- `QPDF::allowXxx()` — 查询权限限制
- `QPDFWriter::setPreserveEncryption(false)` — 写出时移除加密
- `QPDFPageDocumentHelper::getAllPages()` — 验证页面完整性

### Decision 3: 手工参数解析 (不引入第三方库)

**选择**: 自定义 `parse_args()` 函数，逐个匹配参数
**理由**: 参数数量少 (7个选项)，不值得引入 CLI 框架。保持零额外依赖。
**替代方案**: 使用 CLI11 / cxxopts — 引入额外依赖不值得。

### Decision 4: std::filesystem 管理路径

**选择**: 使用 C++17 `<filesystem>` 处理所有路径操作
**理由**: 标准库原生支持，处理中文路径、路径拼接、目录遍历均可靠。

### Decision 5: 错误处理策略

**选择**: 异常捕获 (try/catch QPDFExc) + 返回 bool 表示成功/失败
**理由**: libqpdf 本身使用异常机制 (QPDFExc)，顺其自然。bool 返回值用于批量模式统计成功/失败数。
**密码错误识别**: 通过 `QPDFExc::getErrorCode() == qpdf_e_password` 区分密码错误和其他错误。

### Decision 6: 终端彩色输出

**选择**: ANSI 转义序列，通过静态 `Colors::enabled` 全局开关控制
**理由**: macOS 终端原生支持 ANSI。提供 `--no-color` 参数禁用。

## Risks / Trade-offs

- **[仅 macOS]** → CMakeLists.txt 硬编码 Homebrew 路径。Mitigation: 优先用 pkg-config，Homebrew 路径仅作 fallback。
- **[中文路径]** → macOS 默认 UTF-8，std::filesystem 处理中文路径可靠。Mitigation: 测试样张名含中文。
- **[libqpdf 版本]** → API 可能在大版本变更。Mitigation: 使用稳定的核心 API (QPDF/QPDFWriter)，不使用实验性接口。

## Open Questions

（无，需求和技术方案均明确）
