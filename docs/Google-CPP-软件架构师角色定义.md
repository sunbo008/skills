# Google C++ 软件架构师指南

本文档定义了 C++ 软件架构师的职责、能力标准和编码规范，参考 Google C++ Style Guide 和业界最佳实践。

---

## 第一部分：职责描述

### 1.1 核心职责

#### 系统设计与架构
- **设计可扩展的系统架构**：确保系统能够随业务增长而扩展
- **定义模块边界和接口**：明确各模块的职责和交互方式
- **技术选型决策**：评估和选择合适的技术栈、框架和工具
- **性能架构设计**：设计满足性能要求的系统架构

#### 技术领导
- **代码审查**：审查关键代码，确保符合架构设计和编码规范
- **技术指导**：指导团队成员解决复杂技术问题
- **知识传承**：编写技术文档，组织技术分享
- **标准制定**：制定和维护团队的编码规范和最佳实践

#### 质量保障
- **架构评审**：评审设计方案，识别潜在风险
- **技术债务管理**：识别、记录和规划技术债务的偿还
- **安全架构**：确保系统设计符合安全要求
- **可测试性设计**：确保架构支持有效的测试策略

#### 跨团队协作
- **接口协商**：与其他团队协商 API 和数据格式
- **依赖管理**：管理外部依赖和第三方库
- **技术沟通**：向非技术人员解释技术决策

### 1.2 日常工作内容

| 活动 | 时间占比 | 说明 |
|------|---------|------|
| 系统设计 | 30% | 架构设计、技术方案评审 |
| 代码审查 | 25% | 审查关键代码和设计 |
| 编码实现 | 20% | 核心模块和原型开发 |
| 技术指导 | 15% | 指导团队、解决疑难问题 |
| 文档编写 | 10% | 架构文档、设计文档 |

---

## 第二部分：能力标准

### 2.1 技术能力

#### 2.1.1 C++ 语言精通（必须）

**现代 C++ 特性（C++11/14/17/20）**
- 智能指针：`std::unique_ptr`、`std::shared_ptr`、`std::weak_ptr`
- 移动语义：右值引用、`std::move`、完美转发
- Lambda 表达式和函数式编程
- 变参模板和折叠表达式
- `constexpr` 和编译期计算
- 结构化绑定和 `std::optional`/`std::variant`
- 协程（C++20）

**内存管理**
- RAII 原则的深入理解和应用
- 内存对齐和缓存友好设计
- 自定义分配器
- 内存泄漏检测和预防

**并发编程**
- 线程安全设计模式
- 锁的正确使用和死锁预防
- 无锁数据结构
- `std::atomic` 和内存序

#### 2.1.2 系统设计能力（必须）

**设计原则**
- SOLID 原则的 C++ 实现
- DRY（Don't Repeat Yourself）
- KISS（Keep It Simple, Stupid）
- YAGNI（You Aren't Gonna Need It）

**设计模式**
- 创建型：工厂、单例、Builder
- 结构型：适配器、装饰器、代理、组合
- 行为型：策略、观察者、命令、状态机

**架构模式**
- 分层架构
- 微服务架构
- 事件驱动架构
- 插件架构

#### 2.1.3 工程能力（必须）

**构建系统**
- CMake 高级用法
- 交叉编译配置
- 依赖管理（vcpkg、Conan）

**测试**
- 单元测试（Google Test）
- 集成测试
- 性能测试和基准测试
- 模糊测试

**工具链**
- 静态分析（clang-tidy、cppcheck）
- 动态分析（Valgrind、ASan、TSan）
- 性能分析（perf、VTune）
- 调试技巧（GDB、LLDB）

### 2.2 软技能

#### 2.2.1 沟通能力
- 清晰表达复杂技术概念
- 编写高质量技术文档
- 有效的代码审查反馈
- 跨团队技术协调

#### 2.2.2 决策能力
- 权衡利弊做出技术决策
- 识别和管理技术风险
- 在不确定性中做出判断

#### 2.2.3 领导能力
- 技术方向把控
- 团队成员培养
- 推动技术改进

### 2.3 能力等级标准

| 级别 | 年限参考 | 核心能力要求 |
|------|---------|-------------|
| L5 高级工程师 | 5+ 年 | 独立设计模块，指导初级工程师 |
| L6 Staff 工程师 | 8+ 年 | 设计子系统，跨团队技术协调 |
| L7 高级 Staff | 10+ 年 | 设计大型系统，技术战略规划 |
| L8 首席工程师 | 15+ 年 | 公司级技术决策，行业影响力 |

---

## 第三部分：项目结构

### 3.1 项目目录结构

本项目为 `jsonreader` 模块，位于 `Coding/core_bundle/office/pdf/jsonreader/`，是 PDF JSON 解析和处理的核心库。

```
jsonreader/
├── include/                    # 公共头文件
│   ├── core/                   # 核心模块头文件
│   │   ├── css/                # CSS 解析相关
│   │   ├── html/               # HTML 解析相关
│   │   ├── json/               # JSON 抽象层
│   │   ├── latex/              # LaTeX 解析相关
│   │   └── table/              # 表格处理相关
│   ├── tools/                  # 工具类头文件
│   └── utils/                  # 通用工具头文件
├── src/                        # 源代码实现
│   ├── core/                   # 核心模块实现
│   │   ├── css/                # CSS 解析器实现
│   │   ├── html/               # HTML 解析器实现
│   │   ├── json/               # JSON 后端实现
│   │   ├── latex/              # LaTeX 解析器实现
│   │   └── table/              # 表格解析器实现
│   ├── tools/                  # 工具类实现
│   └── utils/                  # 通用工具实现
├── tests/                      # 测试代码
│   ├── unit/                   # 单元测试
│   ├── integration/            # 集成测试
│   ├── benchmark/              # 性能测试
│   ├── fuzz/                   # 模糊测试
│   └── fixtures/               # 测试数据
├── tools/                      # 命令行工具
│   ├── tree_walker/            # JSON 树遍历工具
│   ├── kspaice_transfer/       # 格式转换工具
│   ├── kspaice_json_generator/ # JSON 生成工具
│   └── roundtrip_validator/    # 往返验证工具
├── third_party/                # 第三方依赖
│   ├── rapidjson/              # RapidJSON (header-only)
│   ├── gumbo-parser/           # HTML 解析器
│   └── microtex/               # LaTeX 渲染库
├── docs/                       # 文档
├── cmake/                      # CMake 配置文件
├── benchmarks/                 # 性能基准测试
├── examples/                   # 示例代码
└── openspec/                   # OpenSpec 变更管理
    ├── specs/                  # 规格说明
    └── changes/                # 变更记录
```

**核心模块说明**：

| 模块 | 路径 | 职责 |
|------|------|------|
| CSS 解析器 | `core/css/` | 解析 CSS 样式，支持选择器匹配和属性应用 |
| HTML 解析器 | `core/html/` | 解析 HTML 内容，提取表格和样式信息 |
| JSON 抽象层 | `core/json/` | 统一的 JSON 读写接口，支持多后端 |
| LaTeX 解析器 | `core/latex/` | 解析 LaTeX 公式，转换为 OMML 格式 |
| 表格解析器 | `core/table/` | 解析 PDF 中的表格结构 |
| 工具库 | `utils/` | 日志、错误处理、平台兼容等通用功能 |

### 3.2 Release 目录

项目的构建和发布目录位于仓库根目录的 `release/` 文件夹：

```
release/
├── wps_build/                  # 构建输出目录
│   ├── *.obj                   # 编译中间文件
│   ├── *.tlog                  # 构建日志
│   └── ...
└── xwares/                     # WPS 第三方库和依赖
    ├── *.hpp                   # 头文件
    ├── *.h
    ├── *.cpp
    └── ...
```

**目录说明**：

| 目录 | 说明 |
|------|------|
| `wps_build/` | 构建产物和中间文件，包含编译生成的 .obj 文件和日志 |
| `xwares/` | WPS 预编译的第三方库和公共依赖 |

> ⚠️ **注意**：`release/` 目录是所有 `krepo-ng` 构建命令的工作目录，必须在此目录下执行构建命令。

### 3.3 构建规范

**构建工具**：本项目基于 WPS 构建规则，使用 `krepo-ng` 进行构建。

**基本构建命令**：

```bash
# 首先切换到 release 目录
cd release

# 构建指定目标
krepo-ng build -t <target_name>

# 示例：构建 jsonreader 模块
krepo-ng build -t jsonreader

# 构建多个目标
krepo-ng build -t target1 -t target2
```

> ⚠️ **重要**：所有 `krepo-ng` 命令必须在 `release` 目录下执行。

**常用构建选项**：

| 选项 | 说明 |
|------|------|
| `-t <target>` | 指定构建目标 |
| `--release` | 构建 Release 版本 |
| `--debug` | 构建 Debug 版本 |
| `--clean` | 清理后重新构建 |

**注意事项**：
- 构建前确保已正确配置 WPS 开发环境
- 首次构建需要完整的依赖同步
- 增量构建时注意检查依赖变更

### 3.4 WPS 第三方库使用规范

WPS 构建系统提供了统一的第三方库管理机制，通过预定义变量和宏简化第三方库的集成。

**核心变量**：

| 变量名 | 说明 |
|--------|------|
| `WPS_THIRD_DEFAULT_INCLUDE_DIR` | WPS 第三方库的默认头文件目录 |

**使用 WPS 预编译的第三方库**：

```cmake
wps_package(my_library STATIC)
    wps_add_sources(
        src/my_source.cpp
    )
    wps_include_directories(
        ${CMAKE_CURRENT_SOURCE_DIR}/include
        # 使用 WPS 提供的第三方库头文件
        ${WPS_THIRD_DEFAULT_INCLUDE_DIR}/kspdf_tinyxml2
    )
    # 链接 WPS 提供的第三方库（平台条件语法）
    wps_use_packages(WIN(tinyxml2-kspdf))
wps_end_package()
```

**平台条件语法说明**：

```cmake
# wps_use_packages 支持平台条件
wps_use_packages(WIN(lib_name))      # 仅 Windows 平台
wps_use_packages(DARWIN(lib_name))   # 仅 macOS 平台
wps_use_packages(LINUX(lib_name))    # 仅 Linux 平台
wps_use_packages(lib_name)           # 所有平台
```

**WPS 构建系统常用宏**：

| 宏名称 | 说明 | 示例 |
|--------|------|------|
| `wps_package(name TYPE)` | 定义包（STATIC/SHARED/EXECUTABLE） | `wps_package(mylib STATIC)` |
| `wps_end_package()` | 结束包定义 | - |
| `wps_add_sources(...)` | 添加源文件 | `wps_add_sources(src/main.cpp)` |
| `wps_include_directories(...)` | 添加头文件路径 | `wps_include_directories(include/)` |
| `wps_link_packages(...)` | 链接内部包 | `wps_link_packages(kspaice_json)` |
| `wps_use_packages(...)` | 使用外部依赖/WPS提供的第三方库 | `wps_use_packages(WIN(tinyxml2-kspdf))` |
| `wps_add_definitions(...)` | 添加宏定义 | `wps_add_definitions(MY_MACRO)` |
| `wps_test_package(...)` | 定义测试包 | `wps_test_package(test GTest::gmock_main CONSOLE)` |
| `wps_add_subdirectory_on_test(...)` | 测试时才添加子目录 | `wps_add_subdirectory_on_test(tests)` |

**Header-only 库 vs WPS 预编译库**：

```cmake
# 方式一：Header-only 库（如 RapidJSON）
# 只需添加头文件路径，不需要链接
set(RAPIDJSON_INCLUDE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/third_party/rapidjson/include")
wps_include_directories(${RAPIDJSON_INCLUDE_DIR})

# 方式二：WPS 预编译库（如 tinyxml2）
# 需要同时添加头文件路径和链接库
wps_include_directories(${WPS_THIRD_DEFAULT_INCLUDE_DIR}/kspdf_tinyxml2)
wps_use_packages(WIN(tinyxml2-kspdf))
```

**最佳实践**：

1. **优先使用 WPS 提供的第三方库**：保持与 WPS 构建系统的一致性
2. **Header-only 库可自行管理**：放在 `third_party/` 目录，通过 `wps_include_directories` 引用
3. **需要编译的第三方库**：优先使用 WPS 预编译版本，避免 ABI 兼容性问题
4. **平台差异处理**：使用 `WIN()`、`DARWIN()` 等条件宏处理平台差异

---

## 第四部分：编码规范

### 4.0 文件规范

#### 4.0.1 文件编码

**强制要求**：所有生成的代码文件必须使用 **UTF-8 BOM** 格式。

```
文件头部必须包含 UTF-8 BOM 字节序标记：
EF BB BF（十六进制）
```

**原因说明**：
- 确保跨平台和跨编辑器的一致性
- 避免中文注释和字符串在不同环境下出现乱码
- 与 Visual Studio 等 IDE 的默认设置保持兼容

**适用范围**：
- `.h` / `.hpp` 头文件
- `.cpp` / `.cc` 源文件
- `.inl` 内联文件

### 4.1 命名规范

#### 4.1.1 通用规则

```cpp
// 类名：PascalCase
class TableStyleManager;
class CssParser;

// 函数名：camelCase 或 PascalCase（Google 风格用 PascalCase）
void ComputeStyle();
int GetRowCount();

// 变量名：snake_case 或 camelCase
int row_count;      // Google 风格
int rowCount;       // 也可接受

// 成员变量：带前缀或后缀
class MyClass {
    int m_value;      // m_ 前缀
    int value_;       // _ 后缀（Google 风格）
};

// 常量：k 前缀 + PascalCase
const int kMaxBufferSize = 1024;
constexpr double kPi = 3.14159;

// 枚举值：k 前缀或全大写
enum class Color {
    kRed,           // Google 风格
    kGreen,
    kBlue
};

// 宏：全大写 + 下划线
#define MAX_BUFFER_SIZE 1024
#define KSPAICE_LOG_DEBUG(msg) ...
```

#### 4.1.2 命名前缀规范（本项目）

```cpp
// 类前缀
class CKSPAICE_CssParser;      // C 前缀：具体类
class IKSPAICE_CssParser;      // I 前缀：接口类
struct KSPAICE_BoundingBox;    // 无前缀：结构体

// 枚举前缀
enum class EKSPAICE_StyleSource;  // E 前缀：枚举

// 智能指针类型别名
using KSPAICE_BoundingBoxSP = std::shared_ptr<KSPAICE_BoundingBox>;
using KSPAICE_CssParserUP = std::unique_ptr<IKSPAICE_CssParser>;
```

### 4.2 格式规范

#### 4.2.1 缩进和空白

```cpp
// 使用 4 空格缩进（或团队约定的 2 空格）
class MyClass {
    void Method() {
        if (condition) {
            DoSomething();
        }
    }
};

// 运算符两侧加空格
int result = a + b * c;
if (x == y && z != w) { }

// 逗号后加空格
void Function(int a, int b, int c);
std::vector<int> v = {1, 2, 3};

// 大括号风格（K&R 或 Allman，保持一致）
// K&R 风格（Google 推荐）
if (condition) {
    DoSomething();
} else {
    DoOther();
}
```

#### 4.2.2 行长度

```cpp
// 每行不超过 80-120 字符（团队约定）
// 长表达式换行
auto result = SomeLongFunctionName(
    first_argument,
    second_argument,
    third_argument);

// 长字符串换行
std::string message = 
    "This is a very long message that "
    "spans multiple lines for readability.";
```

### 4.3 头文件规范

#### 4.3.1 Include 顺序

```cpp
// 1. 对应的头文件（如果是 .cpp）
#include "my_class.h"

// 2. C 系统头文件
#include <cstdint>
#include <cstring>

// 3. C++ 标准库头文件
#include <string>
#include <vector>
#include <memory>

// 4. 第三方库头文件
#include <rapidjson/document.h>

// 5. 项目内部头文件
#include "core/css/css_parser.h"
#include "utils/logger.h"
```

#### 4.3.2 头文件保护

```cpp
// 使用 #pragma once（现代编译器推荐）
#pragma once

// 或使用传统的 include guard
#ifndef KSPAICE_CSS_PARSER_H
#define KSPAICE_CSS_PARSER_H

// 内容...

#endif // KSPAICE_CSS_PARSER_H
```

#### 4.3.3 前向声明

```cpp
// 优先使用前向声明减少编译依赖
// 头文件中：
class CssParser;  // 前向声明
struct BoundingBox;

class MyClass {
    std::unique_ptr<CssParser> m_parser;  // 只需前向声明
};

// 实现文件中再 include
#include "css_parser.h"
```

### 4.4 类设计规范

#### 4.4.1 类结构顺序

```cpp
class MyClass {
public:
    // 1. 类型定义和别名
    using Ptr = std::shared_ptr<MyClass>;
    
    // 2. 静态常量
    static constexpr int kMaxSize = 100;
    
    // 3. 构造函数和析构函数
    MyClass();
    explicit MyClass(int value);
    ~MyClass();
    
    // 4. 拷贝/移动操作（Rule of Five）
    MyClass(const MyClass&) = delete;
    MyClass& operator=(const MyClass&) = delete;
    MyClass(MyClass&&) noexcept = default;
    MyClass& operator=(MyClass&&) noexcept = default;
    
    // 5. 公共方法
    void DoSomething();
    int GetValue() const;
    
protected:
    // 6. 保护方法
    virtual void OnEvent();
    
private:
    // 7. 私有方法
    void Initialize();
    
    // 8. 成员变量（放最后）
    int m_value = 0;
    std::string m_name;
};
```

#### 4.4.2 Rule of Zero/Five

```cpp
// Rule of Zero：优先使用智能指针，不需要手动管理资源
class GoodClass {
    std::unique_ptr<Resource> m_resource;
    std::vector<int> m_data;
    // 不需要定义析构函数、拷贝/移动操作
};

// Rule of Five：如果必须手动管理资源
class ResourceOwner {
public:
    ResourceOwner();
    ~ResourceOwner();
    ResourceOwner(const ResourceOwner&);
    ResourceOwner& operator=(const ResourceOwner&);
    ResourceOwner(ResourceOwner&&) noexcept;
    ResourceOwner& operator=(ResourceOwner&&) noexcept;
};
```

### 4.5 函数设计规范

#### 4.5.1 参数传递

```cpp
// 输入参数：
// - 小类型：传值
void Process(int value);
void Process(double value);

// - 大类型：const 引用
void Process(const std::string& text);
void Process(const std::vector<int>& data);

// - 智能指针（共享所有权）：传值
void Process(std::shared_ptr<Resource> resource);

// - 智能指针（不转移所有权）：const 引用或裸指针
void Process(const std::shared_ptr<Resource>& resource);
void Process(Resource* resource);  // 不拥有

// 输出参数：
// - 优先使用返回值
std::optional<Result> Compute();
Expected<Result, Error> Compute();

// - 必要时使用指针（明确表示可能修改）
void GetResult(Result* out_result);

// 输入输出参数：引用
void Modify(std::string& text);
```

#### 4.5.2 函数长度

```cpp
// 函数应该短小精悍
// - 理想情况：20-40 行
// - 最大不超过：80 行
// - 超过时考虑拆分

// 好的做法：每个函数做一件事
void ProcessDocument(const Document& doc) {
    ValidateDocument(doc);
    ParseContent(doc);
    ApplyStyles(doc);
    RenderOutput(doc);
}

// 避免：一个函数做太多事
void DoEverything() {
    // 200+ 行代码...
}
```

### 4.6 错误处理规范

#### 4.6.1 错误处理策略

```cpp
// 1. 使用 std::optional 表示可能没有值
std::optional<User> FindUser(int id);

// 2. 使用 Expected/Result 类型（推荐）
Expected<Document, Error> ParseDocument(const std::string& json);

// 3. 使用异常（谨慎使用，仅用于真正的异常情况）
void OpenFile(const std::string& path) {
    if (!FileExists(path)) {
        throw FileNotFoundException(path);
    }
}

// 4. 使用错误码（C 风格接口）
ErrorCode ProcessData(const Data* input, Result* output);
```

#### 4.6.2 断言使用

```cpp
// 调试断言：检查编程错误
assert(ptr != nullptr && "Pointer should not be null");

// 运行时检查：检查可恢复的错误
if (index >= size) {
    KSPAICE_LOG_ERROR("Index out of bounds");
    return std::nullopt;
}

// 静态断言：编译期检查
static_assert(sizeof(int) == 4, "int must be 4 bytes");
```

### 4.7 注释规范

#### 4.7.1 文件头注释

```cpp
/**
 * @file css_parser.h
 * @brief CSS 解析器接口定义
 * 
 * @details 本文件定义了 CSS 解析器的接口和相关类型。
 *          支持 CSS3 子集，包括选择器、声明块等。
 * 
 * @author KSPAICE Team
 * @date 2026-01-14
 */
```

#### 4.7.2 类注释

```cpp
/**
 * @class CssParser
 * @brief CSS 样式表解析器
 * 
 * @details 解析 CSS 文本并生成结构化的样式表对象。
 *          支持以下功能：
 *          - 元素选择器、类选择器、ID 选择器
 *          - 伪类选择器（:first-child, :nth-child）
 *          - 后代选择器和子选择器
 * 
 * @example
 * auto parser = createCssParser();
 * auto result = parser->parse("td { color: red; }");
 * if (result) {
 *     // 使用解析结果
 * }
 * 
 * @note 线程安全：解析器实例不是线程安全的
 */
class CssParser { ... };
```

#### 4.7.3 函数注释

```cpp
/**
 * @brief 解析 CSS 文本
 * 
 * @param cssText CSS 文本内容
 * @return 解析结果，失败时返回错误信息
 * 
 * @throws std::invalid_argument 如果 cssText 为空
 * 
 * @note 解析器会尽可能容错，跳过无法识别的规则
 * 
 * @example
 * auto result = parser.Parse("body { margin: 0; }");
 */
Expected<StyleSheet, ParseError> Parse(const std::string& cssText);
```

#### 4.7.4 行内注释

```cpp
void ProcessData() {
    // 步骤 1: 验证输入数据
    if (!ValidateInput()) {
        return;
    }
    
    // 步骤 2: 转换数据格式
    // 注意：这里使用 UTF-8 编码
    auto converted = ConvertToUtf8(data);
    
    // TODO: 添加缓存机制提升性能
    // FIXME: 大文件处理可能导致内存不足
    // HACK: 临时解决方案，等待上游修复
}
```

### 4.8 现代 C++ 最佳实践

#### 4.8.1 智能指针使用

```cpp
// 独占所有权：使用 unique_ptr
auto parser = std::make_unique<CssParser>();

// 共享所有权：使用 shared_ptr
auto doc = std::make_shared<Document>();

// 弱引用（避免循环引用）：使用 weak_ptr
std::weak_ptr<Parent> m_parent;

// 避免裸指针拥有资源
// 错误
Resource* res = new Resource();  // 谁负责删除？

// 正确
auto res = std::make_unique<Resource>();
```

#### 3.8.2 避免的做法

```cpp
// 避免：使用 new/delete
Widget* w = new Widget();
delete w;

// 避免：C 风格数组
int arr[100];

// 避免：C 风格类型转换
int* p = (int*)ptr;

// 避免：using namespace std（在头文件中）
using namespace std;  // 污染命名空间

// 避免：魔法数字
if (status == 42) { }  // 42 是什么？

// 正确做法
constexpr int kStatusSuccess = 42;
if (status == kStatusSuccess) { }
```

#### 4.8.3 推荐的做法

```cpp
// 使用 auto 简化类型声明
auto it = container.begin();
auto result = ComputeValue();

// 使用范围 for 循环
for (const auto& item : items) {
    Process(item);
}

// 使用 nullptr 而非 NULL 或 0
if (ptr == nullptr) { }

// 使用 override 和 final
class Derived : public Base {
    void Method() override;
    void FinalMethod() final;
};

// 使用 [[nodiscard]] 防止忽略返回值
[[nodiscard]] bool IsValid() const;

// 使用 constexpr 进行编译期计算
constexpr int Square(int x) { return x * x; }
```

#### 4.8.4 性能与资源

**性能敏感代码规范**（呼应 5.3 节性能审查）

```cpp
// 1. 使用 std::string_view 避免字符串拷贝
// 错误：每次调用都会拷贝字符串
void ProcessText(const std::string& text) {
    // ...
}

// 正确：只读参数使用 string_view，零拷贝
void ProcessText(std::string_view text) {
    // 注意：不要存储 string_view，它只是视图
    // 不要返回指向临时对象的 string_view
}

// 使用场景示例
std::string data = "Hello, World!";
ProcessText(data);                    // 可以传 string
ProcessText("Literal");               // 可以传字面量
ProcessText(data.substr(0, 5));       // 可以传子串视图

// 2. 使用 std::span 处理数组和缓冲区
// 错误：C 风格指针 + 长度，容易出错
void ProcessBuffer(const uint8_t* data, size_t size);

// 正确：使用 span 提供类型安全的视图
void ProcessBuffer(std::span<const uint8_t> data) {
    // 自动包含大小信息
    for (auto byte : data) {
        // ...
    }
}

// 使用示例
std::vector<uint8_t> buffer = {1, 2, 3, 4};
ProcessBuffer(buffer);                // 自动转换
ProcessBuffer(std::span(buffer.data(), buffer.size()));

// 3. 积极使用移动语义
// 正确：返回局部变量会自动移动（RVO/NRVO）
std::vector<int> CreateLargeVector() {
    std::vector<int> result;
    result.reserve(10000);
    // 填充数据...
    return result;  // 不需要 std::move，编译器会优化
}

// 正确：转移所有权时显式使用 move
void TakeOwnership(std::unique_ptr<Resource> resource) {
    m_resource = std::move(resource);
}

// 正确：容器插入时移动临时对象
std::vector<std::string> names;
std::string temp = "John";
names.push_back(std::move(temp));  // temp 被移动，不再有效

// 避免：不必要的拷贝
std::vector<LargeObject> objects;
for (const auto& obj : source) {
    objects.push_back(obj);  // 拷贝
}

// 正确：移动而非拷贝
for (auto&& obj : source) {
    objects.push_back(std::move(obj));  // 移动
}

// 4. 容器预留空间减少动态扩容
// 错误：多次扩容导致性能损失
std::vector<int> numbers;
for (int i = 0; i < 10000; ++i) {
    numbers.push_back(i);  // 可能触发多次内存重新分配
}

// 正确：预先分配足够空间
std::vector<int> numbers;
numbers.reserve(10000);  // 一次性分配
for (int i = 0; i < 10000; ++i) {
    numbers.push_back(i);  // 不会重新分配
}

// 正确：已知大小时直接构造
std::vector<int> numbers(10000);  // 预分配并初始化
for (int i = 0; i < 10000; ++i) {
    numbers[i] = i;
}

// 5. 其他性能优化技巧
// 使用 emplace 系列方法就地构造
std::vector<std::pair<int, std::string>> pairs;
pairs.emplace_back(1, "one");  // 就地构造，避免临时对象

// 避免不必要的临时对象
// 错误
std::string result = std::string("prefix_") + suffix;

// 正确
std::string result = "prefix_";
result += suffix;

// 使用 const& 捕获 lambda 避免拷贝
auto process = [&data = const_cast<const Data&>(data)]() {
    // 使用 data，不会拷贝
};

// 考虑使用 small string optimization (SSO)
// 短字符串（通常 < 16 字节）不会堆分配
std::string short_str = "hello";  // 栈上存储，无堆分配
```

**性能优化原则**：

1. **测量优先**：使用性能分析工具（perf、VTune）确定瓶颈，不要过早优化
2. **避免拷贝**：优先使用视图类型（`string_view`、`span`）和移动语义
3. **预分配内存**：已知大小时使用 `reserve()` 或直接构造
4. **就地构造**：使用 `emplace` 系列方法减少临时对象
5. **权衡取舍**：可读性和维护性优先，性能关键路径才需要极致优化

**注意事项**：

- `std::string_view` 不拥有数据，注意生命周期管理
- `std::span` 是 C++20 特性，旧编译器需要使用替代方案
- 移动后的对象处于有效但未指定状态，不要继续使用
- `reserve()` 只分配容量，不改变 `size()`，注意区分 `capacity()` 和 `size()`

#### 4.8.5 结构化绑定与现代类型

**1. 结构化绑定（Structured Bindings，C++17）**

结构化绑定允许从元组、数组、结构体等一次性解包多个值。

```cpp
// 传统方式：使用 std::pair/std::tuple
std::pair<std::string, int> GetUserInfo() {
    return {"Alice", 25};
}

// 旧方式：分别获取
auto result = GetUserInfo();
std::string name = result.first;
int age = result.second;

// 现代方式：结构化绑定（C++17）
auto [name, age] = GetUserInfo();
// name 是 std::string，age 是 int

// 使用场景1：遍历 map
std::map<std::string, int> scores = {{"Alice", 90}, {"Bob", 85}};

// 旧方式
for (const auto& pair : scores) {
    std::cout << pair.first << ": " << pair.second << std::endl;
}

// 新方式：更清晰
for (const auto& [name, score] : scores) {
    std::cout << name << ": " << score << std::endl;
}

// 使用场景2：解包自定义结构体
struct Point {
    double x;
    double y;
    double z;
};

Point GetOrigin() {
    return {0.0, 0.0, 0.0};
}

auto [x, y, z] = GetOrigin();

// 使用场景3：解包数组
int arr[3] = {1, 2, 3};
auto [a, b, c] = arr;

// 使用场景4：与 insert/emplace 返回值配合
std::map<std::string, int> data;
auto [iter, inserted] = data.insert({"key", 42});
if (inserted) {
    std::cout << "插入成功: " << iter->first << std::endl;
}
```

**2. std::optional（C++17）**

`std::optional` 表示"可能有值也可能没有值"，替代传统的指针或特殊值（如 -1、nullptr）。

```cpp
// 传统方式：使用特殊值或指针
int FindIndex(const std::vector<int>& vec, int value) {
    for (size_t i = 0; i < vec.size(); ++i) {
        if (vec[i] == value) return i;
    }
    return -1;  // 特殊值表示未找到，容易出错
}

// 现代方式：使用 std::optional
std::optional<size_t> FindIndex(const std::vector<int>& vec, int value) {
    for (size_t i = 0; i < vec.size(); ++i) {
        if (vec[i] == value) return i;
    }
    return std::nullopt;  // 明确表示没有值
}

// 使用方式
std::vector<int> numbers = {1, 2, 3, 4, 5};

// 方式1：检查是否有值
auto result = FindIndex(numbers, 3);
if (result.has_value()) {
    std::cout << "找到了，索引: " << result.value() << std::endl;
}

// 方式2：使用 operator bool
if (result) {
    std::cout << "找到了，索引: " << *result << std::endl;
}

// 方式3：提供默认值
size_t index = result.value_or(0);  // 如果没有值，使用 0

// 方式4：结合结构化绑定
std::optional<std::pair<std::string, int>> GetConfig() {
    // 可能返回配置，也可能没有
    return std::make_pair("setting", 42);
}

if (auto config = GetConfig(); config) {
    auto [key, value] = *config;
    std::cout << key << " = " << value << std::endl;
}

// 实际应用：配置读取
class Config {
public:
    std::optional<std::string> GetString(const std::string& key) const {
        auto it = m_data.find(key);
        if (it != m_data.end()) {
            return it->second;
        }
        return std::nullopt;
    }
    
    std::optional<int> GetInt(const std::string& key) const {
        if (auto str = GetString(key); str) {
            try {
                return std::stoi(*str);
            } catch (...) {
                return std::nullopt;
            }
        }
        return std::nullopt;
    }
    
private:
    std::map<std::string, std::string> m_data;
};

// 使用
Config config;
if (auto timeout = config.GetInt("timeout"); timeout) {
    std::cout << "超时设置: " << *timeout << " 秒" << std::endl;
} else {
    std::cout << "使用默认超时" << std::endl;
}
```

**3. std::variant（C++17）**

`std::variant` 是类型安全的联合体（union），可以存储多种类型中的一种。

```cpp
// 传统方式：使用 union（不安全）
union Data {
    int i;
    double d;
    char* s;  // 危险：不知道当前是哪种类型
};

// 现代方式：使用 std::variant（类型安全）
std::variant<int, double, std::string> data;

// 赋值
data = 42;                    // 现在存储 int
data = 3.14;                  // 现在存储 double
data = "hello";               // 现在存储 string

// 访问方式1：std::get（如果类型不匹配会抛异常）
try {
    int value = std::get<int>(data);
} catch (const std::bad_variant_access&) {
    std::cout << "类型不匹配" << std::endl;
}

// 访问方式2：std::get_if（返回指针，类型不匹配返回 nullptr）
if (auto* ptr = std::get_if<int>(&data)) {
    std::cout << "int 值: " << *ptr << std::endl;
}

// 访问方式3：std::visit（推荐，使用访问者模式）
std::visit([](auto&& arg) {
    using T = std::decay_t<decltype(arg)>;
    if constexpr (std::is_same_v<T, int>) {
        std::cout << "int: " << arg << std::endl;
    } else if constexpr (std::is_same_v<T, double>) {
        std::cout << "double: " << arg << std::endl;
    } else if constexpr (std::is_same_v<T, std::string>) {
        std::cout << "string: " << arg << std::endl;
    }
}, data);

// 实际应用：JSON 值表示
class JsonValue {
public:
    using Value = std::variant<
        std::nullptr_t,           // null
        bool,                     // boolean
        int64_t,                  // integer
        double,                   // number
        std::string,              // string
        std::vector<JsonValue>,   // array
        std::map<std::string, JsonValue>  // object
    >;
    
    JsonValue(Value v) : m_value(std::move(v)) {}
    
    bool IsNull() const { return std::holds_alternative<std::nullptr_t>(m_value); }
    bool IsBool() const { return std::holds_alternative<bool>(m_value); }
    bool IsInt() const { return std::holds_alternative<int64_t>(m_value); }
    bool IsDouble() const { return std::holds_alternative<double>(m_value); }
    bool IsString() const { return std::holds_alternative<std::string>(m_value); }
    
    std::optional<int64_t> AsInt() const {
        if (auto* p = std::get_if<int64_t>(&m_value)) {
            return *p;
        }
        return std::nullopt;
    }
    
    std::string ToString() const {
        return std::visit([](auto&& arg) -> std::string {
            using T = std::decay_t<decltype(arg)>;
            if constexpr (std::is_same_v<T, std::nullptr_t>) {
                return "null";
            } else if constexpr (std::is_same_v<T, bool>) {
                return arg ? "true" : "false";
            } else if constexpr (std::is_same_v<T, int64_t>) {
                return std::to_string(arg);
            } else if constexpr (std::is_same_v<T, double>) {
                return std::to_string(arg);
            } else if constexpr (std::is_same_v<T, std::string>) {
                return "\"" + arg + "\"";
            } else {
                return "complex type";
            }
        }, m_value);
    }
    
private:
    Value m_value;
};

// 使用
JsonValue v1(42);
JsonValue v2(3.14);
JsonValue v3("hello");

std::cout << v1.ToString() << std::endl;  // "42"
std::cout << v2.ToString() << std::endl;  // "3.14"
std::cout << v3.ToString() << std::endl;  // "hello"
```

**4. 组合使用示例**

```cpp
// 结合 optional、variant 和结构化绑定
struct ParseResult {
    std::variant<int, double, std::string> value;
    std::string error;
};

std::optional<ParseResult> ParseValue(const std::string& input) {
    if (input.empty()) {
        return std::nullopt;
    }
    
    // 尝试解析为整数
    try {
        int i = std::stoi(input);
        return ParseResult{i, ""};
    } catch (...) {}
    
    // 尝试解析为浮点数
    try {
        double d = std::stod(input);
        return ParseResult{d, ""};
    } catch (...) {}
    
    // 作为字符串
    return ParseResult{input, ""};
}

// 使用
if (auto result = ParseValue("42"); result) {
    auto& [value, error] = *result;
    
    std::visit([](auto&& v) {
        std::cout << "解析结果: " << v << std::endl;
    }, value);
}
```

**最佳实践**：

1. **结构化绑定**：
   - 优先用于解包 `std::pair`、`std::tuple` 和简单结构体
   - 使用 `const auto&` 避免不必要的拷贝
   - 变量名要有意义，提高可读性

2. **std::optional**：
   - 替代返回指针或特殊值的场景
   - 明确表达"可能没有值"的语义
   - 优先使用 `value_or()` 提供默认值

3. **std::variant**：
   - 替代不安全的 `union`
   - 表示"多种类型之一"的场景
   - 优先使用 `std::visit` 进行类型安全的访问
   - 考虑性能：`variant` 有一定开销，不适合极致性能场景

**注意事项**：

- 这些特性都是 C++17 引入的，确保编译器支持
- `std::optional` 和 `std::variant` 有额外的内存开销
- 结构化绑定的变量不能单独声明为引用，需要整体声明（如 `auto& [a, b]`）
- `std::variant` 的第一个类型必须有默认构造函数

---

## 第五部分：代码审查清单

### 5.1 架构审查

- [ ] 模块职责是否单一明确？
- [ ] 接口设计是否合理？
- [ ] 依赖关系是否正确？
- [ ] 是否存在循环依赖？
- [ ] 扩展性是否足够？

### 5.2 代码质量审查

- [ ] 命名是否清晰准确？
- [ ] 函数是否足够短小？
- [ ] 是否有重复代码？
- [ ] 错误处理是否完善？
- [ ] 边界条件是否处理？

### 5.3 性能审查

- [ ] 是否有不必要的拷贝？
- [ ] 是否有内存泄漏风险？
- [ ] 是否有性能瓶颈？
- [ ] 缓存是否有效利用？

### 5.4 安全审查

- [ ] 输入是否验证？
- [ ] 是否有缓冲区溢出风险？
- [ ] 是否有资源泄漏？
- [ ] 线程安全是否保证？

---

## 参考资料

1. [Google C++ Style Guide](https://google.github.io/styleguide/cppguide.html)
2. [C++ Core Guidelines](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines)
3. [Effective Modern C++](https://www.oreilly.com/library/view/effective-modern-c/9781491908419/)
4. [Clean Code](https://www.oreilly.com/library/view/clean-code-a/9780136083238/)
