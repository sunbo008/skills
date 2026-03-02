# C++ 审查快速参考卡片

快速查阅最常见的审查要点，适合在审查时对照检查。

---

## 🔴 严重问题（必须修复）

### 文件编码
```
❌ UTF-8 无BOM
✅ UTF-8 with BOM
```

### 资源管理
```cpp
❌ Widget* w = new Widget(); delete w;
✅ auto w = make_unique<Widget>();
```

### 循环依赖
```cpp
❌ A.h includes B.h, B.h includes A.h
✅ 使用前向声明: class B;
```

### 内存安全
```cpp
❌ 裸指针拥有资源
✅ 智能指针管理资源
```

### 线程安全
```cpp
❌ 无锁保护的共享数据
✅ mutex + lock_guard 或 atomic
```

---

## 🟡 重要建议（建议改进）

### 命名规范
```cpp
类名:     PascalCase          class CssParser
函数名:   PascalCase          void ParseCss()
变量名:   snake_case          int row_count
成员变量: m_前缀或_后缀       int m_value; int value_;
常量:     k前缀+PascalCase    const int kMaxSize = 100
枚举值:   k前缀+PascalCase    enum { kRed, kGreen }
宏:       全大写+下划线        #define MAX_SIZE 100
```

### 参数传递
```cpp
小对象:         传值              void f(int x)
大对象只读:     const引用         void f(const string& s)
更好的只读:     string_view       void f(string_view s)
输出参数:       指针              void f(int* out)
输入输出:       引用              void f(string& s)
所有权转移:     unique_ptr        void f(unique_ptr<T> p)
```

### 返回值
```cpp
❌ void GetData(vector<int>* out);
✅ vector<int> GetData();
✅ optional<Data> GetData();  // 可能失败
```

### 错误处理
```cpp
❌ 返回-1表示失败
✅ optional<int> 或 Expected<int, Error>
```

### 函数长度
```
理想: 20-40行
最大: 80行
超过需要拆分
```

---

## 🟢 性能优化（推荐）

### 避免拷贝
```cpp
❌ for (auto item : items)           // 拷贝
✅ for (const auto& item : items)    // 引用

❌ void f(const string& s)           // 可能拷贝
✅ void f(string_view s)             // 零拷贝
```

### 容器优化
```cpp
❌ vector<int> v;
   for (...) v.push_back(x);         // 多次扩容

✅ vector<int> v;
   v.reserve(count);                 // 预留空间
   for (...) v.push_back(x);
```

### 就地构造
```cpp
❌ v.push_back(Widget(a, b));        // 临时对象
✅ v.emplace_back(a, b);             // 就地构造
```

### 移动语义
```cpp
❌ return std::move(local_var);      // 阻碍RVO
✅ return local_var;                 // 编译器优化

✅ vec.push_back(std::move(obj));    // 移动而非拷贝
```

---

## ✅ 现代C++检查

### 智能指针
```cpp
独占: unique_ptr<T> p = make_unique<T>();
共享: shared_ptr<T> p = make_shared<T>();
弱引: weak_ptr<T> w = p;
```

### 类型推导
```cpp
✅ auto it = container.begin();
✅ auto value = compute();
```

### 范围for
```cpp
✅ for (const auto& item : items) { }
```

### nullptr
```cpp
✅ int* ptr = nullptr;
❌ int* ptr = NULL;
```

### override/final
```cpp
✅ void method() override;
✅ void method() final;
```

### [[nodiscard]]
```cpp
✅ [[nodiscard]] bool IsValid() const;
```

### constexpr
```cpp
✅ constexpr int Square(int x) { return x * x; }
```

### 结构化绑定 (C++17)
```cpp
✅ auto [key, value] = map.find(...);
✅ for (const auto& [k, v] : map) { }
```

### optional (C++17)
```cpp
✅ optional<int> Find(const string& key);
   if (auto v = Find("key"); v) { use(*v); }
```

### variant (C++17)
```cpp
✅ variant<int, double, string> data;
   visit([](auto&& arg) { ... }, data);
```

---

## 🔒 安全检查

### 输入验证
```cpp
✅ if (ptr == nullptr) return error;
✅ if (size == 0) return error;
✅ if (index >= size) return error;
```

### 边界检查
```cpp
❌ arr[index]              // 不检查
✅ arr.at(index)           // 检查边界
✅ if (index < size) arr[index]
```

### const正确性
```cpp
✅ void f(const Data& data) const;
✅ const int* const ptr;
```

### noexcept
```cpp
✅ ~Destructor() noexcept;
✅ void swap(T& a, T& b) noexcept;
```

---

## 🔧 WPS构建系统

### 包定义
```cmake
wps_package(mylib STATIC)
    wps_add_sources(src/main.cpp)
    wps_include_directories(include/)
wps_end_package()
```

### 第三方库
```cmake
# Header-only库
wps_include_directories(third_party/rapidjson/include)

# WPS预编译库
wps_include_directories(${WPS_THIRD_DEFAULT_INCLUDE_DIR}/kspdf_tinyxml2)
wps_use_packages(WIN(tinyxml2-kspdf))
```

### 平台条件
```cmake
wps_use_packages(WIN(lib))      # Windows
wps_use_packages(DARWIN(lib))   # macOS
wps_use_packages(LINUX(lib))    # Linux
```

---

## 📋 快速检查清单

### 5秒检查（最关键）
- [ ] 文件是UTF-8 BOM编码
- [ ] 无裸指针拥有资源
- [ ] 无明显内存泄漏

### 30秒检查
- [ ] 命名符合规范
- [ ] 无循环依赖
- [ ] 函数不超过80行
- [ ] 有错误处理
- [ ] 线程安全（如果多线程）

### 5分钟检查
- [ ] 架构设计合理
- [ ] 接口设计清晰
- [ ] 无重复代码
- [ ] 无不必要拷贝
- [ ] 使用现代C++特性
- [ ] 有必要的注释

---

## 🎯 审查优先级

### P0 - 必须修复
- 内存泄漏
- 线程不安全
- 缓冲区溢出
- 循环依赖

### P1 - 强烈建议
- 命名不规范
- 函数过长
- 错误处理缺失
- 资源管理不当

### P2 - 建议改进
- 性能可优化
- 代码可重构
- 注释不完善

### P3 - 可选优化
- 风格细节
- 锦上添花的改进

---

## 📖 常用模式

### RAII模式
```cpp
class FileHandle {
    FILE* file_;
public:
    FileHandle(const char* path) : file_(fopen(path, "r")) {}
    ~FileHandle() { if (file_) fclose(file_); }
};
```

### Rule of Zero
```cpp
class Widget {
    unique_ptr<Impl> pImpl_;
    // 不需要定义析构/拷贝/移动
};
```

### Rule of Five
```cpp
class Resource {
public:
    ~Resource();
    Resource(const Resource&);
    Resource& operator=(const Resource&);
    Resource(Resource&&) noexcept;
    Resource& operator=(Resource&&) noexcept;
};
```

### 工厂模式
```cpp
unique_ptr<Parser> CreateParser(Type type) {
    switch (type) {
        case Type::Css: return make_unique<CssParser>();
        case Type::Html: return make_unique<HtmlParser>();
    }
}
```

---

## 🚫 常见错误

### 1. 忘记const
```cpp
❌ int GetValue() { return value_; }
✅ int GetValue() const { return value_; }
```

### 2. 不必要的move
```cpp
❌ return std::move(local);  // 阻碍RVO
✅ return local;             // 让编译器优化
```

### 3. 拷贝shared_ptr
```cpp
❌ void f(shared_ptr<T> p);        // 拷贝
✅ void f(const shared_ptr<T>& p); // 引用
✅ void f(T* p);                   // 不拥有时用裸指针
```

### 4. 在头文件using namespace
```cpp
❌ using namespace std;  // 污染命名空间
✅ using std::string;    // 或直接std::string
```

### 5. 魔法数字
```cpp
❌ if (status == 42) { }
✅ constexpr int kSuccess = 42;
   if (status == kSuccess) { }
```

---

## 💡 审查技巧

### 从上到下
1. 先看架构（最重要）
2. 再看接口设计
3. 然后看实现细节
4. 最后看格式规范

### 从重到轻
1. 先找严重问题（内存、安全）
2. 再找重要问题（质量、性能）
3. 最后看优化建议

### 从外到内
1. 先看公共接口
2. 再看内部实现
3. 最后看私有细节

---

**提示**: 这是快速参考卡片，详细说明请查看：
- **STANDARDS.md** - 完整的编码规范
- **REFERENCE.md** - 详细的检查清单
- **EXAMPLES.md** - 实际审查案例
