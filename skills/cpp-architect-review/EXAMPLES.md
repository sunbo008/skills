# 审查示例

本文档提供实际的审查案例,展示如何应用审查清单。

## 示例1: 审查类设计

### 待审查代码

```cpp
// css_parser.h
#pragma once
#include <string>
#include <vector>
#include <map>
#include "style_sheet.h"

class CssParser {
public:
    CssParser();
    ~CssParser();
    
    bool parse(std::string css);
    StyleSheet* getResult();
    std::string getError();
    
    void setDebugMode(bool debug);
    bool isDebugMode();
    
    void reset();
    
private:
    StyleSheet* result;
    std::string error;
    bool debug;
    std::map<std::string, std::string> cache;
};
```

### 审查报告

#### 严重问题 🔴

**问题1: 使用裸指针管理资源**
- **位置**: `StyleSheet* result`
- **问题**: 裸指针管理动态分配的资源,容易内存泄漏
- **修复**:
```cpp
std::unique_ptr<StyleSheet> m_result;
```

**问题2: 命名不符合规范**
- **位置**: 函数名`parse`、`getResult`等
- **问题**: 应使用PascalCase(Google风格)
- **修复**:
```cpp
bool Parse(std::string_view css);
const StyleSheet* GetResult() const;
std::string GetError() const;
```

**问题3: 缺少文件编码标记**
- **问题**: 文件应使用UTF-8 BOM编码
- **修复**: 在编辑器中转换为UTF-8 BOM

#### 重要建议 🟡

**建议1: 使用string_view避免拷贝**
```cpp
// 修改前
bool parse(std::string css);

// 修改后
bool Parse(std::string_view css);
```

**建议2: 使用optional返回结果**
```cpp
// 修改前
StyleSheet* getResult();
std::string getError();

// 修改后
std::optional<StyleSheet> GetResult() const;
// 或使用Expected类型
Expected<StyleSheet, ParseError> Parse(std::string_view css);
```

**建议3: 成员变量命名加前缀**
```cpp
// 修改前
StyleSheet* result;
std::string error;
bool debug;

// 修改后
std::unique_ptr<StyleSheet> m_result;
std::string m_error;
bool m_debug = false;
```

### 修复后的代码

```cpp
// css_parser.h
#pragma once
#include <string>
#include <string_view>
#include <optional>
#include <memory>
#include <map>

// 前向声明,减少编译依赖
struct StyleSheet;
struct ParseError;

/**
 * @class CKSPAICE_CssParser
 * @brief CSS样式表解析器
 */
class CKSPAICE_CssParser {
public:
    CKSPAICE_CssParser();
    ~CKSPAICE_CssParser() = default;
    
    // 禁止拷贝,允许移动
    CKSPAICE_CssParser(const CKSPAICE_CssParser&) = delete;
    CKSPAICE_CssParser& operator=(const CKSPAICE_CssParser&) = delete;
    CKSPAICE_CssParser(CKSPAICE_CssParser&&) noexcept = default;
    CKSPAICE_CssParser& operator=(CKSPAICE_CssParser&&) noexcept = default;
    
    /**
     * @brief 解析CSS文本
     * @param css CSS文本内容
     * @return 解析结果或错误信息
     */
    Expected<StyleSheet, ParseError> Parse(std::string_view css);
    
    /**
     * @brief 设置调试模式
     */
    void SetDebugMode(bool debug) { m_debug = debug; }
    
    /**
     * @brief 获取调试模式状态
     */
    [[nodiscard]] bool IsDebugMode() const { return m_debug; }
    
    /**
     * @brief 重置解析器状态
     */
    void Reset();
    
private:
    bool m_debug = false;
    std::map<std::string, std::string> m_cache;
};
```

## 示例2: 审查函数实现

### 待审查代码

```cpp
// table_parser.cpp
void TableParser::parseTable(const std::string& html) {
    // 解析HTML
    std::vector<std::string> rows;
    std::string current = "";
    bool inTag = false;
    for (int i = 0; i < html.length(); i++) {
        char c = html[i];
        if (c == '<') {
            inTag = true;
            if (current.length() > 0) {
                rows.push_back(current);
                current = "";
            }
        } else if (c == '>') {
            inTag = false;
        } else if (!inTag) {
            current += c;
        }
    }
    
    // 解析每一行
    std::vector<std::vector<std::string>> table;
    for (int i = 0; i < rows.size(); i++) {
        std::vector<std::string> cells;
        std::string cell = "";
        for (int j = 0; j < rows[i].length(); j++) {
            if (rows[i][j] == '|') {
                cells.push_back(cell);
                cell = "";
            } else {
                cell += rows[i][j];
            }
        }
        if (cell.length() > 0) {
            cells.push_back(cell);
        }
        table.push_back(cells);
    }
    
    // 构建表格对象
    m_table = new Table();
    for (int i = 0; i < table.size(); i++) {
        Row* row = new Row();
        for (int j = 0; j < table[i].size(); j++) {
            Cell* cell = new Cell();
            cell->setText(table[i][j]);
            row->addCell(cell);
        }
        m_table->addRow(row);
    }
}
```

### 审查报告

#### 严重问题 🔴

**问题1: 函数过长,做太多事**
- **位置**: `parseTable`函数(50+行)
- **问题**: 一个函数包含HTML解析、行列分割、对象构建三个职责
- **修复**: 拆分成多个小函数

**问题2: 使用裸指针和new**
- **位置**: `m_table = new Table()`等
- **问题**: 手动内存管理,容易泄漏
- **修复**: 使用智能指针

**问题3: 命名不符合规范**
- **位置**: 函数名`parseTable`
- **问题**: 应使用PascalCase
- **修复**: `ParseTable`

**问题4: 使用int作为循环索引**
- **位置**: `for (int i = 0; i < html.length(); i++)`
- **问题**: 应使用size_t,或使用范围for
- **修复**: 使用范围for循环

#### 重要建议 🟡

**建议1: 使用string_view避免拷贝**
```cpp
void ParseTable(std::string_view html);
```

**建议2: 使用现代C++特性**
```cpp
// 使用范围for
for (const auto& row : rows) {
    // ...
}

// 使用emplace_back
cells.emplace_back(cell);
```

**建议3: 错误处理不完善**
- 缺少输入验证
- 没有处理解析失败的情况

### 修复后的代码

```cpp
// table_parser.cpp

Expected<Table, ParseError> CKSPAICE_TableParser::ParseTable(std::string_view html) {
    // 输入验证
    if (html.empty()) {
        return Unexpected(ParseError::EmptyInput);
    }
    
    // 步骤1: 解析HTML提取文本
    auto rows_result = ExtractRows(html);
    if (!rows_result) {
        return Unexpected(rows_result.error());
    }
    
    // 步骤2: 分割单元格
    auto cells_result = SplitCells(rows_result.value());
    if (!cells_result) {
        return Unexpected(cells_result.error());
    }
    
    // 步骤3: 构建表格对象
    return BuildTable(cells_result.value());
}

Expected<std::vector<std::string>, ParseError> 
CKSPAICE_TableParser::ExtractRows(std::string_view html) {
    std::vector<std::string> rows;
    std::string current;
    bool in_tag = false;
    
    for (char c : html) {
        if (c == '<') {
            in_tag = true;
            if (!current.empty()) {
                rows.push_back(std::move(current));
                current.clear();
            }
        } else if (c == '>') {
            in_tag = false;
        } else if (!in_tag) {
            current += c;
        }
    }
    
    if (!current.empty()) {
        rows.push_back(std::move(current));
    }
    
    return rows;
}

Expected<std::vector<std::vector<std::string>>, ParseError>
CKSPAICE_TableParser::SplitCells(const std::vector<std::string>& rows) {
    std::vector<std::vector<std::string>> table;
    table.reserve(rows.size());
    
    for (const auto& row : rows) {
        std::vector<std::string> cells;
        std::string cell;
        
        for (char c : row) {
            if (c == '|') {
                cells.push_back(std::move(cell));
                cell.clear();
            } else {
                cell += c;
            }
        }
        
        if (!cell.empty()) {
            cells.push_back(std::move(cell));
        }
        
        table.push_back(std::move(cells));
    }
    
    return table;
}

Expected<Table, ParseError>
CKSPAICE_TableParser::BuildTable(const std::vector<std::vector<std::string>>& data) {
    auto table = std::make_unique<Table>();
    
    for (const auto& row_data : data) {
        auto row = std::make_unique<Row>();
        
        for (const auto& cell_text : row_data) {
            auto cell = std::make_unique<Cell>();
            cell->SetText(cell_text);
            row->AddCell(std::move(cell));
        }
        
        table->AddRow(std::move(row));
    }
    
    return Table(std::move(table));
}
```

## 示例3: 审查性能问题

### 待审查代码

```cpp
// style_matcher.cpp
std::vector<Style> StyleMatcher::matchStyles(const Element& element) {
    std::vector<Style> result;
    
    // 遍历所有样式规则
    for (int i = 0; i < m_rules.size(); i++) {
        Rule rule = m_rules[i];  // 拷贝
        
        // 检查选择器是否匹配
        for (int j = 0; j < rule.selectors.size(); j++) {
            Selector sel = rule.selectors[j];  // 拷贝
            
            if (matches(element, sel)) {
                // 应用样式
                for (int k = 0; k < rule.declarations.size(); k++) {
                    Declaration decl = rule.declarations[k];  // 拷贝
                    
                    Style style;
                    style.property = decl.property;
                    style.value = decl.value;
                    result.push_back(style);
                }
            }
        }
    }
    
    return result;
}
```

### 审查报告

#### 严重问题 🔴

**问题1: 大量不必要的拷贝**
- **位置**: 循环中的`Rule rule = m_rules[i]`等
- **问题**: 每次循环都拷贝对象,性能损失严重
- **影响**: 对于大型样式表,性能可能下降10倍以上
- **修复**: 使用const引用

**问题2: 容器未预留空间**
- **位置**: `std::vector<Style> result`
- **问题**: 多次push_back可能触发多次重新分配
- **修复**: 使用reserve预留空间

#### 重要建议 🟡

**建议1: 使用范围for循环**
```cpp
// 修改前
for (int i = 0; i < m_rules.size(); i++) {
    Rule rule = m_rules[i];
}

// 修改后
for (const auto& rule : m_rules) {
}
```

**建议2: 使用emplace_back就地构造**
```cpp
// 修改前
Style style;
style.property = decl.property;
style.value = decl.value;
result.push_back(style);

// 修改后
result.emplace_back(decl.property, decl.value);
```

### 修复后的代码

```cpp
// style_matcher.cpp
std::vector<Style> CKSPAICE_StyleMatcher::MatchStyles(const Element& element) {
    std::vector<Style> result;
    result.reserve(EstimateStyleCount());  // 预留空间
    
    // 使用范围for和const引用
    for (const auto& rule : m_rules) {
        for (const auto& selector : rule.selectors) {
            if (Matches(element, selector)) {
                // 应用样式
                for (const auto& decl : rule.declarations) {
                    result.emplace_back(decl.property, decl.value);
                }
            }
        }
    }
    
    return result;
}

size_t CKSPAICE_StyleMatcher::EstimateStyleCount() const {
    // 估算结果大小,避免多次重新分配
    size_t count = 0;
    for (const auto& rule : m_rules) {
        count += rule.declarations.size();
    }
    return count;
}
```

**性能改进**:
- 消除了所有不必要的拷贝
- 使用reserve减少内存重新分配
- 使用emplace_back就地构造
- 预期性能提升: 5-10倍

## 示例4: 审查线程安全问题

### 待审查代码

```cpp
// cache_manager.h
class CacheManager {
public:
    void put(const std::string& key, const std::string& value) {
        m_cache[key] = value;
    }
    
    std::string get(const std::string& key) {
        if (m_cache.find(key) != m_cache.end()) {
            return m_cache[key];
        }
        return "";
    }
    
    void clear() {
        m_cache.clear();
    }
    
private:
    std::map<std::string, std::string> m_cache;
};
```

### 审查报告

#### 严重问题 🔴

**问题1: 缺少线程同步**
- **位置**: 所有公共方法
- **问题**: 多线程访问m_cache会导致数据竞争
- **影响**: 可能导致程序崩溃或数据损坏
- **修复**: 添加互斥锁保护

**问题2: get方法查找两次**
- **位置**: `get`方法
- **问题**: find和[]操作符查找两次,效率低
- **修复**: 只查找一次

#### 重要建议 🟡

**建议1: 使用string_view作为参数**
```cpp
void Put(std::string_view key, std::string_view value);
std::optional<std::string> Get(std::string_view key) const;
```

**建议2: 使用optional表示可能不存在**
```cpp
std::optional<std::string> Get(std::string_view key) const;
```

### 修复后的代码

```cpp
// cache_manager.h
#pragma once
#include <string>
#include <string_view>
#include <map>
#include <mutex>
#include <optional>
#include <shared_mutex>

/**
 * @class CKSPAICE_CacheManager
 * @brief 线程安全的缓存管理器
 */
class CKSPAICE_CacheManager {
public:
    /**
     * @brief 存储键值对
     * @param key 键
     * @param value 值
     */
    void Put(std::string_view key, std::string_view value) {
        std::unique_lock lock(m_mutex);
        m_cache[std::string(key)] = value;
    }
    
    /**
     * @brief 获取值
     * @param key 键
     * @return 值,如果不存在返回nullopt
     */
    [[nodiscard]] std::optional<std::string> Get(std::string_view key) const {
        std::shared_lock lock(m_mutex);
        
        if (auto it = m_cache.find(std::string(key)); it != m_cache.end()) {
            return it->second;
        }
        return std::nullopt;
    }
    
    /**
     * @brief 清空缓存
     */
    void Clear() {
        std::unique_lock lock(m_mutex);
        m_cache.clear();
    }
    
    /**
     * @brief 获取缓存大小
     */
    [[nodiscard]] size_t Size() const {
        std::shared_lock lock(m_mutex);
        return m_cache.size();
    }
    
private:
    mutable std::shared_mutex m_mutex;  // 读写锁
    std::map<std::string, std::string> m_cache;
};
```

**改进说明**:
1. 使用`std::shared_mutex`支持多读单写
2. Get方法使用`shared_lock`,允许并发读取
3. Put和Clear使用`unique_lock`,独占写入
4. 使用`std::optional`表示可能不存在的值
5. 只查找一次,避免重复查找

## 示例5: 审查WPS构建配置

### 待审查代码

```cmake
# CMakeLists.txt
add_library(kspaice_json STATIC
    src/json_reader.cpp
    src/json_writer.cpp
)

target_include_directories(kspaice_json PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/include
    ${CMAKE_CURRENT_SOURCE_DIR}/third_party/rapidjson/include
)

# 链接tinyxml2
find_package(tinyxml2 REQUIRED)
target_link_libraries(kspaice_json tinyxml2::tinyxml2)

# 添加测试
add_executable(json_test tests/json_test.cpp)
target_link_libraries(json_test kspaice_json GTest::gtest_main)
```

### 审查报告

#### 严重问题 🔴

**问题1: 未使用WPS构建宏**
- **位置**: 整个CMakeLists.txt
- **问题**: 直接使用CMake命令,不符合WPS构建规范
- **影响**: 无法与WPS构建系统集成
- **修复**: 使用wps_package等宏

**问题2: 未使用WPS提供的第三方库**
- **位置**: `find_package(tinyxml2 REQUIRED)`
- **问题**: 应使用WPS预编译的tinyxml2
- **修复**: 使用wps_use_packages

### 修复后的代码

```cmake
# CMakeLists.txt

# 定义JSON库
wps_package(kspaice_json STATIC)
    # 添加源文件
    wps_add_sources(
        src/json_reader.cpp
        src/json_writer.cpp
    )
    
    # 添加头文件路径
    wps_include_directories(
        ${CMAKE_CURRENT_SOURCE_DIR}/include
        # RapidJSON是header-only库,直接引用
        ${CMAKE_CURRENT_SOURCE_DIR}/third_party/rapidjson/include
        # 使用WPS提供的tinyxml2头文件
        ${WPS_THIRD_DEFAULT_INCLUDE_DIR}/kspdf_tinyxml2
    )
    
    # 链接WPS提供的第三方库(仅Windows平台)
    wps_use_packages(WIN(tinyxml2-kspdf))
wps_end_package()

# 定义测试(仅在测试模式下编译)
wps_test_package(json_test GTest::gmock_main CONSOLE)
    wps_add_sources(
        tests/json_test.cpp
    )
    
    # 链接被测试的库
    wps_link_packages(kspaice_json)
wps_end_package()

# 仅在测试时添加tests子目录
wps_add_subdirectory_on_test(tests)
```

**改进说明**:
1. 使用`wps_package`定义包
2. 使用`wps_add_sources`添加源文件
3. 使用`wps_include_directories`添加头文件路径
4. 使用`wps_use_packages`链接WPS第三方库
5. 使用`wps_test_package`定义测试
6. 使用平台条件`WIN()`处理平台差异
7. Header-only库(RapidJSON)只添加头文件路径
8. 需要链接的库(tinyxml2)使用WPS预编译版本

## 总结

通过这些示例可以看到:

1. **架构问题**: 循环依赖、职责不清、耦合过紧
2. **代码质量**: 命名不规范、函数过长、错误处理不完善
3. **性能问题**: 不必要的拷贝、缺少优化、资源管理不当
4. **安全问题**: 线程不安全、输入未验证、内存管理问题
5. **规范问题**: 未使用现代C++、未遵循项目规范

审查时要:
- 系统性地检查各个维度
- 提供具体的修复方案
- 说明问题的影响和修复的收益
- 给出可执行的改进建议
