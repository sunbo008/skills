## ADDED Requirements

### Requirement: 批量解密目录下 PDF
系统 SHALL 支持 `--batch` 模式，解密指定目录下所有 PDF 文件。

#### Scenario: 非递归批量解密
- **WHEN** 指定一个包含 PDF 文件的目录并使用 `--batch`
- **THEN** 解密该目录下所有 `.pdf` 文件（不含子目录）
- **AND** 显示处理摘要（成功数、失败数、跳过数）

#### Scenario: 递归批量解密
- **WHEN** 指定目录并使用 `--batch -r`
- **THEN** 递归解密该目录及所有子目录下的 `.pdf` 文件

#### Scenario: 跳过已解锁文件
- **WHEN** 目录中存在文件名含 `_已解锁` 的 PDF
- **THEN** 自动跳过这些文件，跳过计数加一

#### Scenario: 空目录
- **WHEN** 指定的目录中没有 PDF 文件
- **THEN** 显示警告"目录中未找到 PDF 文件"

#### Scenario: 目录不存在
- **WHEN** 指定一个不存在的目录路径并使用 `--batch`
- **THEN** 显示错误"目录不存在"并返回非零退出码
