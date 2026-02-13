## 1. 项目骨架

- [x] 1.1 创建 `skills/pdf-password-remover/cpp/` 目录和 `CMakeLists.txt`（查找 libqpdf, C++17, 生成 pdf_unlock 可执行文件）
- [x] 1.2 创建 `pdf_unlock.cpp` 基础框架（main + 参数解析 + 颜色输出工具函数）

## 2. encryption-info 能力

- [x] 2.1 实现 `EncryptionInfo` 结构体和 `get_encryption_info()` 函数（QPDF::isEncrypted, allowXxx 系列 API）
- [x] 2.2 实现 `display_encryption_info()` 格式化输出（加密状态、版本、方法、受限操作列表）

## 3. single-unlock 能力

- [x] 3.1 实现 `generate_output_path()` 输出路径生成（默认 `_已解锁` 后缀）
- [x] 3.2 实现 `unlock_pdf()` 核心解密函数（QPDFWriter::setPreserveEncryption(false)）
- [x] 3.3 实现安全校验（文件存在性、路径防覆盖）
- [x] 3.4 实现密码支持（-p 参数传递给 processFile）

## 4. result-verify 能力

- [x] 4.1 在 `unlock_pdf()` 中实现解密后自动验证（重新打开输出文件检查加密状态 + 页面数）

## 5. batch-unlock 能力

- [x] 5.1 实现 `batch_unlock()` 函数（目录遍历 + 跳过已解锁文件 + 统计摘要）
- [x] 5.2 支持递归模式（-r 参数控制 recursive_directory_iterator vs directory_iterator）

## 6. 测试验证

- [x] 6.1 编译通过（cmake + make 无错误无警告）
- [x] 6.2 使用测试样张验证 --info 功能
- [x] 6.3 使用测试样张验证单文件解密功能
- [x] 6.4 使用 qpdf CLI 二次验证解密结果
