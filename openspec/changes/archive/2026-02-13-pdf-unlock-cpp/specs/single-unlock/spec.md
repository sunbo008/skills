## ADDED Requirements

### Requirement: 移除单文件权限密码
系统 SHALL 移除 PDF 文件的 Owner Password，输出无加密的 PDF 文件。

#### Scenario: 默认输出路径
- **WHEN** 输入 `input.pdf` 且未指定 `-o` 参数
- **THEN** 输出文件为 `input_已解锁.pdf`（与输入文件同目录）

#### Scenario: 自定义输出路径
- **WHEN** 输入 `input.pdf` 并指定 `-o output.pdf`
- **THEN** 输出文件为 `output.pdf`

#### Scenario: 未加密文件直接复制
- **WHEN** 输入一个未加密的 PDF 文件
- **THEN** 显示警告"文件未加密，直接复制"并将文件复制到输出路径

### Requirement: 支持已知密码
系统 SHALL 支持通过 `-p` 参数提供已知密码来解密文件。

#### Scenario: 提供正确密码
- **WHEN** 输入一个加密 PDF 并通过 `-p` 提供正确密码
- **THEN** 成功解密并输出无加密文件

#### Scenario: 需要打开密码但未提供
- **WHEN** 输入一个有 User Password 的 PDF 且未提供 `-p` 参数
- **THEN** 显示错误"密码错误或该文件需要打开密码"并提示使用 `-p` 参数

### Requirement: 安全校验
系统 SHALL 防止输出文件覆盖输入文件，并检查输入文件存在性。

#### Scenario: 输入文件不存在
- **WHEN** 提供一个不存在的文件路径
- **THEN** 显示错误"文件不存在: <路径>"并返回非零退出码

#### Scenario: 输出路径与输入相同
- **WHEN** 指定的输出路径与输入路径完全相同
- **THEN** 显示错误"输出路径不能与输入路径相同"并返回非零退出码
