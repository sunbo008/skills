# Google C++ 架构师审查参考手册

## 详细审查清单

### 架构设计审查清单

#### 模块职责审查

| 检查项 | 说明 | 反例 | 正例 |
|--------|------|------|------|
| 单一职责 | 每个类/模块只做一件事 | 一个类既负责解析又负责渲染 | 解析器类只负责解析,渲染器类负责渲染 |
| 职责明确 | 从名字就能看出职责 | `Manager`、`Helper`、`Util` | `CssParser`、`TableRenderer` |
| 合理粒度 | 不要太大也不要太小 | 1000行的上帝类 | 100-300行的专注类 |

#### 接口设计审查

| 检查项 | 说明 | 反例 | 正例 |
|--------|------|------|------|
| 最小接口 | 只暴露必要的方法 | 暴露所有内部方法 | 只暴露公共API |
| 稳定接口 | 接口不易变化 | 频繁修改接口签名 | 使用配置对象扩展参数 |
| 易用性 | 接口简单直观 | 需要多步初始化 | 提供便捷的工厂方法 |
| 前向声明 | 减少编译依赖 | 头文件include所有依赖 | 使用前向声明+实现文件include |

#### 依赖关系审查

```cpp
// ❌ 错误: 循环依赖
// module_a.h
#include "module_b.h"
class ModuleA {
    ModuleB* m_b;
};

// module_b.h
#include "module_a.h"
class ModuleB {
    ModuleA* m_a;
};

// ✅ 正确: 使用前向声明打破循环
// module_a.h
class ModuleB;  // 前向声明
class ModuleA {
    ModuleB* m_b;
};

// module_b.h
class ModuleA;  // 前向声明
class ModuleB {
    ModuleA* m_a;
};
```

### 代码质量审查清单

#### 命名规范详细检查

```cpp
// ✅ 正确的命名示例
class CKSPAICE_CssParser;           // 类: C前缀 + PascalCase
class IKSPAICE_TableRenderer;       // 接口: I前缀 + PascalCase
struct KSPAICE_BoundingBox;         // 结构体: 无前缀 + PascalCase
enum class EKSPAICE_StyleSource;    // 枚举: E前缀 + PascalCase

void ParseCssText();                // 函数: PascalCase (Google风格)
int GetRowCount() const;            // Getter: Get前缀

int row_count;                      // 变量: snake_case
int m_value;                        // 成员变量: m_前缀
int value_;                         // 成员变量: _后缀 (Google风格)

const int kMaxBufferSize = 1024;    // 常量: k前缀 + PascalCase
constexpr double kPi = 3.14159;

enum class Color {
    kRed,                           // 枚举值: k前缀
    kGreen,
    kBlue
};

#define KSPAICE_LOG_DEBUG(msg)      // 宏: 全大写 + 下划线

// 智能指针类型别名
using KSPAICE_CssParserUP = std::unique_ptr<IKSPAICE_CssParser>;
using KSPAICE_BoundingBoxSP = std::shared_ptr<KSPAICE_BoundingBox>;
```

#### 函数设计详细检查

```cpp
// ❌ 错误: 函数太长,做太多事
void ProcessDocument(const Document& doc) {
    // 100+ 行代码
    // 验证、解析、转换、渲染全在一个函数
}

// ✅ 正确: 拆分成多个小函数
void ProcessDocument(const Document& doc) {
    ValidateDocument(doc);      // 20行
    ParseContent(doc);          // 30行
    TransformData(doc);         // 25行
    RenderOutput(doc);          // 15行
}

// ❌ 错误: 参数传递不当
void Process(std::string text);                    // 大对象传值,拷贝开销大
void GetResult(std::shared_ptr<Result>& out);      // 输出参数用引用,不清晰

// ✅ 正确: 合理的参数传递
void Process(std::string_view text);               // 只读大对象用string_view
std::optional<Result> GetResult();                 // 优先返回值

// ❌ 错误: 输出参数不明确
void Calculate(int input, int* output);

// ✅ 正确: 使用返回值
std::optional<int> Calculate(int input);
Expected<int, Error> Calculate(int input);
```

#### 错误处理详细检查

```cpp
// ❌ 错误: 忽略错误
void OpenFile(const std::string& path) {
    std::ifstream file(path);
    // 没有检查是否打开成功
    file >> data;
}

// ✅ 正确: 使用optional处理可能失败的操作
std::optional<std::string> ReadFile(const std::string& path) {
    std::ifstream file(path);
    if (!file.is_open()) {
        return std::nullopt;
    }
    std::string content;
    // 读取内容...
    return content;
}

// ✅ 正确: 使用Expected类型
Expected<Document, ParseError> ParseDocument(const std::string& json) {
    if (json.empty()) {
        return Unexpected(ParseError::EmptyInput);
    }
    // 解析逻辑...
    return document;
}

// ❌ 错误: 滥用异常
int FindIndex(const std::vector<int>& vec, int value) {
    for (size_t i = 0; i < vec.size(); ++i) {
        if (vec[i] == value) return i;
    }
    throw std::runtime_error("Not found");  // 未找到不是异常情况
}

// ✅ 正确: 使用optional
std::optional<size_t> FindIndex(const std::vector<int>& vec, int value) {
    for (size_t i = 0; i < vec.size(); ++i) {
        if (vec[i] == value) return i;
    }
    return std::nullopt;
}
```

### 性能优化审查清单

#### 内存管理详细检查

```cpp
// ❌ 错误: 手动内存管理
class Parser {
    Resource* m_resource;
public:
    Parser() : m_resource(new Resource()) {}
    ~Parser() { delete m_resource; }  // 容易忘记或出错
};

// ✅ 正确: 使用智能指针(Rule of Zero)
class Parser {
    std::unique_ptr<Resource> m_resource;
public:
    Parser() : m_resource(std::make_unique<Resource>()) {}
    // 不需要手动定义析构函数
};

// ❌ 错误: 容器未预留空间
std::vector<int> numbers;
for (int i = 0; i < 10000; ++i) {
    numbers.push_back(i);  // 多次重新分配
}

// ✅ 正确: 预留空间
std::vector<int> numbers;
numbers.reserve(10000);  // 一次性分配
for (int i = 0; i < 10000; ++i) {
    numbers.push_back(i);
}
```

#### 拷贝优化详细检查

```cpp
// ❌ 错误: 不必要的字符串拷贝
void ProcessText(const std::string& text) {
    // text被拷贝
}
std::string data = "Hello, World!";
ProcessText(data);  // 拷贝整个字符串

// ✅ 正确: 使用string_view避免拷贝
void ProcessText(std::string_view text) {
    // 零拷贝,只是视图
}
ProcessText(data);      // 不拷贝
ProcessText("Literal"); // 不拷贝

// ❌ 错误: 返回值拷贝
std::vector<int> CreateVector() {
    std::vector<int> result;
    // 填充数据...
    return std::move(result);  // 不必要的move,阻碍RVO
}

// ✅ 正确: 依赖RVO/NRVO
std::vector<int> CreateVector() {
    std::vector<int> result;
    // 填充数据...
    return result;  // 编译器会优化,不会拷贝
}

// ❌ 错误: 循环中的拷贝
for (const auto item : container) {  // 拷贝每个元素
    Process(item);
}

// ✅ 正确: 使用引用
for (const auto& item : container) {  // 不拷贝
    Process(item);
}

// ✅ 正确: 移动而非拷贝
std::vector<LargeObject> objects;
for (auto&& obj : source) {
    objects.push_back(std::move(obj));  // 移动
}
```

#### 性能关键路径检查

```cpp
// ❌ 错误: 热路径中的临时对象
for (int i = 0; i < 1000000; ++i) {
    std::string temp = "prefix_" + std::to_string(i);  // 每次循环创建临时对象
    Process(temp);
}

// ✅ 正确: 复用对象
std::string temp;
for (int i = 0; i < 1000000; ++i) {
    temp = "prefix_";
    temp += std::to_string(i);  // 复用string对象
    Process(temp);
}

// ❌ 错误: 不必要的查找
for (const auto& item : items) {
    if (map.find(item.key) != map.end()) {
        Process(map[item.key]);  // 查找两次
    }
}

// ✅ 正确: 只查找一次
for (const auto& item : items) {
    if (auto it = map.find(item.key); it != map.end()) {
        Process(it->second);  // 只查找一次
    }
}
```

### 安全性审查清单

#### 输入验证检查

```cpp
// ❌ 错误: 缺少输入验证
void ProcessArray(const int* arr, size_t size) {
    for (size_t i = 0; i < size; ++i) {
        Process(arr[i]);  // arr可能是nullptr
    }
}

// ✅ 正确: 验证输入
void ProcessArray(const int* arr, size_t size) {
    if (arr == nullptr || size == 0) {
        KSPAICE_LOG_ERROR("Invalid input");
        return;
    }
    for (size_t i = 0; i < size; ++i) {
        Process(arr[i]);
    }
}

// ✅ 更好: 使用span避免指针+长度
void ProcessArray(std::span<const int> arr) {
    if (arr.empty()) {
        KSPAICE_LOG_ERROR("Empty array");
        return;
    }
    for (int value : arr) {
        Process(value);
    }
}
```

#### 内存安全检查

```cpp
// ❌ 错误: 悬垂指针
std::string_view GetName() {
    std::string temp = "John";
    return temp;  // 返回指向临时对象的视图,危险!
}

// ✅ 正确: 返回拥有所有权的对象
std::string GetName() {
    return "John";
}

// ❌ 错误: use-after-free
std::unique_ptr<Resource> res = std::make_unique<Resource>();
Resource* ptr = res.get();
res.reset();  // 释放资源
ptr->Use();   // 使用已释放的内存,危险!

// ✅ 正确: 不保存裸指针
std::unique_ptr<Resource> res = std::make_unique<Resource>();
res->Use();  // 直接使用智能指针
```

#### 线程安全检查

```cpp
// ❌ 错误: 数据竞争
class Counter {
    int m_count = 0;
public:
    void Increment() {
        ++m_count;  // 多线程访问不安全
    }
};

// ✅ 正确: 使用互斥锁
class Counter {
    int m_count = 0;
    std::mutex m_mutex;
public:
    void Increment() {
        std::lock_guard<std::mutex> lock(m_mutex);
        ++m_count;
    }
};

// ✅ 更好: 使用原子变量
class Counter {
    std::atomic<int> m_count{0};
public:
    void Increment() {
        m_count.fetch_add(1, std::memory_order_relaxed);
    }
};

// ❌ 错误: 死锁风险
void Transfer(Account& from, Account& to, int amount) {
    std::lock_guard<std::mutex> lock1(from.mutex);
    std::lock_guard<std::mutex> lock2(to.mutex);  // 可能死锁
    from.balance -= amount;
    to.balance += amount;
}

// ✅ 正确: 使用std::lock避免死锁
void Transfer(Account& from, Account& to, int amount) {
    std::scoped_lock lock(from.mutex, to.mutex);  // 原子地锁定多个互斥锁
    from.balance -= amount;
    to.balance += amount;
}
```

### 现代C++特性检查清单

#### 智能指针使用

```cpp
// ❌ 避免: 裸指针拥有资源
Widget* w = new Widget();
// ... 使用 ...
delete w;  // 容易忘记或异常时泄漏

// ✅ 正确: 使用unique_ptr
auto w = std::make_unique<Widget>();
// 自动释放,异常安全

// ❌ 错误: 不必要的shared_ptr
std::shared_ptr<Widget> w = std::make_shared<Widget>();
// 如果不需要共享所有权,用unique_ptr

// ✅ 正确: 根据所有权选择
std::unique_ptr<Widget> w = std::make_unique<Widget>();  // 独占所有权
std::shared_ptr<Data> data = std::make_shared<Data>();   // 共享所有权
std::weak_ptr<Parent> parent = m_parent;                 // 弱引用,避免循环
```

#### 现代类型使用

```cpp
// ❌ 旧方式: 使用特殊值
int FindIndex(const std::vector<int>& vec, int value) {
    // ...
    return -1;  // -1表示未找到,不清晰
}

// ✅ 现代方式: 使用optional
std::optional<size_t> FindIndex(const std::vector<int>& vec, int value) {
    // ...
    return std::nullopt;  // 明确表示没有值
}

// ❌ 旧方式: 使用union
union Data {
    int i;
    double d;
    char* s;  // 不知道当前类型
};

// ✅ 现代方式: 使用variant
std::variant<int, double, std::string> data;
data = 42;
if (auto* p = std::get_if<int>(&data)) {
    // 类型安全的访问
}

// ❌ 旧方式: 多个返回值用输出参数
void GetUserInfo(std::string* name, int* age);

// ✅ 现代方式: 使用结构化绑定
std::pair<std::string, int> GetUserInfo();
auto [name, age] = GetUserInfo();
```

### WPS构建系统检查清单

```cmake
# ❌ 错误: 直接使用CMake命令
add_library(mylib STATIC src/main.cpp)
target_include_directories(mylib PUBLIC include/)

# ✅ 正确: 使用WPS宏
wps_package(mylib STATIC)
    wps_add_sources(src/main.cpp)
    wps_include_directories(
        ${CMAKE_CURRENT_SOURCE_DIR}/include
    )
wps_end_package()

# ❌ 错误: 未使用WPS提供的第三方库
find_package(tinyxml2 REQUIRED)
target_link_libraries(mylib tinyxml2::tinyxml2)

# ✅ 正确: 使用WPS预编译的第三方库
wps_package(mylib STATIC)
    wps_include_directories(
        ${WPS_THIRD_DEFAULT_INCLUDE_DIR}/kspdf_tinyxml2
    )
    wps_use_packages(WIN(tinyxml2-kspdf))
wps_end_package()

# ❌ 错误: 未使用平台条件
wps_use_packages(some_windows_only_lib)  # 在Linux上会失败

# ✅ 正确: 使用平台条件
wps_use_packages(WIN(some_windows_only_lib))
wps_use_packages(LINUX(some_linux_only_lib))
wps_use_packages(DARWIN(some_macos_only_lib))

# Header-only库的正确处理
# ✅ 正确: 只添加头文件路径
set(RAPIDJSON_INCLUDE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/third_party/rapidjson/include")
wps_include_directories(${RAPIDJSON_INCLUDE_DIR})
# 不需要wps_use_packages
```

## 审查报告模板

### 完整示例

```markdown
# 架构审查报告: CSS解析器模块

## 概述
本次审查CSS解析器模块的设计和实现,包括接口设计、代码质量和性能优化。
整体设计合理,但存在一些需要改进的问题。

## 严重问题 🔴

### 问题1: 文件编码不是UTF-8 BOM
**位置**: `src/core/css/css_parser.cpp`
**问题描述**: 源文件使用UTF-8无BOM编码,不符合项目规范
**影响**: 可能导致中文注释在不同环境下乱码
**修复方案**:
将文件转换为UTF-8 BOM格式。在VS Code中:
1. 点击右下角编码
2. 选择"通过编码保存"
3. 选择"UTF-8 with BOM"

**原因**: 根据《Google-CPP-软件架构师角色定义.md》4.0.1节,所有源文件必须使用UTF-8 BOM编码

### 问题2: 存在循环依赖
**位置**: `core/css/css_parser.h` ↔ `core/css/style_sheet.h`
**问题描述**: CssParser和StyleSheet相互包含头文件
**影响**: 增加编译依赖,可能导致编译错误
**修复方案**:
\`\`\`cpp
// css_parser.h
#pragma once
class StyleSheet;  // 前向声明

class CssParser {
    std::unique_ptr<StyleSheet> Parse(const std::string& css);
};

// css_parser.cpp
#include "style_sheet.h"  // 实现文件中包含
\`\`\`
**原因**: 根据4.3.3节,应优先使用前向声明减少编译依赖

## 重要建议 🟡

### 建议1: 使用string_view避免字符串拷贝
**位置**: `CssParser::Parse(const std::string& cssText)`
**当前做法**: 参数使用const引用,但在只读场景下仍会拷贝
**建议做法**: 使用std::string_view,零拷贝
**改进代码**:
\`\`\`cpp
// 修改前
Expected<StyleSheet, ParseError> Parse(const std::string& cssText);

// 修改后
Expected<StyleSheet, ParseError> Parse(std::string_view cssText);
\`\`\`
**收益**: 
- 避免字符串拷贝,提升性能
- 可以直接传递字面量和子串
- 符合4.8.4节性能优化最佳实践

### 建议2: 函数过长需要拆分
**位置**: `CssParser::ParseRuleSet()` (150行)
**当前做法**: 一个函数处理所有解析逻辑
**建议做法**: 拆分成多个小函数
**改进代码**:
\`\`\`cpp
void ParseRuleSet() {
    ParseSelectors();      // 30行
    ParseDeclarations();   // 40行
    ValidateRules();       // 25行
    BuildRuleSet();        // 20行
}
\`\`\`
**收益**: 提高可读性和可维护性,符合4.5.2节函数长度规范

## 优化建议 🟢

### 优化1: 容器预留空间
**位置**: `CssParser::ParseSelectors()`
**优化方案**:
\`\`\`cpp
std::vector<Selector> selectors;
selectors.reserve(estimatedCount);  // 预留空间
for (...) {
    selectors.push_back(selector);
}
\`\`\`
**预期收益**: 减少动态扩容次数,提升10-20%性能

## 优点总结 ✅

1. 接口设计清晰,职责单一
2. 使用了std::optional处理可能失败的操作
3. 智能指针管理资源,符合RAII原则
4. 注释规范,Doxygen格式完整
5. 单元测试覆盖率高

## 总体评分
- 架构设计: 8/10 (存在循环依赖问题)
- 代码质量: 7/10 (函数过长,需要拆分)
- 性能优化: 6/10 (有优化空间)
- 安全性: 9/10 (输入验证完善)
- 规范遵循: 7/10 (文件编码不符合规范)

## 后续行动
- [ ] 修复文件编码为UTF-8 BOM
- [ ] 打破循环依赖,使用前向声明
- [ ] 将Parse参数改为string_view
- [ ] 拆分ParseRuleSet函数
- [ ] 为容器添加reserve调用
```

## 常见反模式

### 1. 上帝类 (God Class)
一个类做太多事,违反单一职责原则。

### 2. 意大利面代码 (Spaghetti Code)
函数间相互调用混乱,难以理解和维护。

### 3. 魔法数字 (Magic Numbers)
代码中出现没有解释的数字常量。

### 4. 过早优化 (Premature Optimization)
在没有性能问题时过度优化,牺牲可读性。

### 5. 重复代码 (Code Duplication)
相同或相似的代码出现在多处。

### 6. 长参数列表 (Long Parameter List)
函数参数过多,应该封装成对象。

### 7. 不一致的命名 (Inconsistent Naming)
同一概念使用不同的名字。

### 8. 注释过时 (Outdated Comments)
注释与代码不一致,误导读者。
