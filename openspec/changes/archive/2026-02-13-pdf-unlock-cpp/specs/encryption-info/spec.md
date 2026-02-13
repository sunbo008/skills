## ADDED Requirements

### Requirement: 读取 PDF 加密状态
系统 SHALL 读取并报告 PDF 文件的加密状态（已加密/未加密）。

#### Scenario: 未加密文件
- **WHEN** 输入一个未加密的 PDF 文件
- **THEN** 显示"加密: 否"并提示"该文件未加密，无需处理"

#### Scenario: 仅有权限密码的文件
- **WHEN** 输入一个仅有 Owner Password 的 PDF 文件
- **THEN** 显示"加密: 是"、"打开密码(User): 无"、"权限密码(Owner): 有"
- **AND** 提示"该文件仅有权限密码，可直接移除"

#### Scenario: 有打开密码的文件
- **WHEN** 输入一个有 User Password 的 PDF 文件且未提供密码
- **THEN** 显示"加密: 是"、"打开密码(User): 有"
- **AND** 提示"该文件有打开密码，需要提供正确密码才能解密"

### Requirement: 显示加密详细信息
系统 SHALL 展示加密版本 (R/V/P)、加密方法（流/字符串/文件）和受限操作列表。

#### Scenario: 显示加密版本和方法
- **WHEN** 输入一个 RC4 加密 (R=4) 的 PDF 文件并使用 `--info` 参数
- **THEN** 显示加密版本 R=4、V=4 和加密方法 RC4

#### Scenario: 显示受限操作列表
- **WHEN** 输入一个限制了打印和内容提取的 PDF 文件
- **THEN** 列出所有受限操作，包括"低分辨率打印"、"高分辨率打印"、"内容提取"等
