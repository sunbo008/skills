# C++ 编码规范核心要点（本地参考）

本文档提取了Google C++ Style Guide和C++ Core Guidelines中最常用的审查要点，供离线使用。

---

## 一、命名规范 (Google C++ Style Guide)

### 1.1 通用命名规则

**原则**: 名称应该具有描述性，避免缩写

```cpp
// ✅ 好的命名
int num_errors;
int num_completed_connections;

// ❌ 避免
int n;
int nerr;
int n_comp_conns;
```

### 1.2 文件命名

- 文件名全小写，可以包含下划线或连字符
- C++文件以`.cc`或`.cpp`结尾
- 头文件以`.h`或`.hpp`结尾

```
my_useful_class.cc
my_useful_class.h
```

### 1.3 类型命名

类、结构体、类型别名、枚举、模板参数都使用**PascalCase**（每个单词首字母大写）

```cpp
class UrlTable { ... };
struct UrlTableProperties { ... };
typedef hash_map<UrlTableProperties*, string> PropertiesMap;
using PropertiesMap = hash_map<UrlTableProperties*, string>;
enum class UrlTableError { ... };
```

### 1.4 变量命名

变量（包括函数参数）和数据成员使用**snake_case**（全小写加下划线）

```cpp
string table_name;  // 局部变量
string tablename;   // 也可以（但不推荐）

class TableInfo {
  string table_name_;  // 成员变量（下划线后缀）
  string tablename_;   // 也可以
  static Pool<TableInfo>* pool_;  // 静态成员变量
};
```

### 1.5 常量命名

常量使用**k前缀 + PascalCase**

```cpp
const int kDaysInAWeek = 7;
constexpr int kMaxSize = 100;
```

### 1.6 函数命名

普通函数使用**PascalCase**，访问器和修改器可以使用snake_case

```cpp
// 普通函数
void AddTableEntry();
void DeleteUrl();

// 访问器和修改器
class MyClass {
 public:
  int num_entries() const { return num_entries_; }  // getter
  void set_num_entries(int num_entries) { num_entries_ = num_entries; }  // setter
  
 private:
  int num_entries_;
};
```

### 1.7 枚举命名

枚举名使用PascalCase，枚举值使用**k前缀 + PascalCase**

```cpp
enum class UrlTableError {
  kOk = 0,
  kOutOfMemory,
  kMalformedInput,
};
```

### 1.8 宏命名

宏使用**全大写 + 下划线**

```cpp
#define ROUND(x) ...
#define PI_ROUNDED 3.0
```

---

## 二、格式规范 (Google C++ Style Guide)

### 2.1 行长度

每行不超过**80字符**

### 2.2 缩进

使用**2个空格**缩进（注：项目可能使用4个空格）

```cpp
class MyClass {
 public:  // 2空格缩进
  MyClass();
  void Method();
  
 private:
  int value_;
};
```

### 2.3 大括号

函数定义：左大括号在同一行

```cpp
void Function() {
  DoSomething();
}

if (condition) {
  DoSomething();
} else {
  DoSomethingElse();
}
```

### 2.4 空格

```cpp
// 运算符两侧加空格
int x = a + b;
if (x == y) { ... }

// 逗号后加空格
Function(a, b, c);

// 指针和引用：靠近类型
int* ptr;
int& ref;
```

### 2.5 头文件顺序

```cpp
// 1. 相关头文件
#include "foo/bar.h"

// 2. C系统头文件
#include <sys/types.h>

// 3. C++标准库头文件
#include <string>
#include <vector>

// 4. 其他库头文件
#include "base/basictypes.h"

// 5. 本项目头文件
#include "foo/public/fooserver.h"
```

---

## 三、类设计 (C++ Core Guidelines)

### 3.1 C.1: 将相关数据组织成结构体（类）

```cpp
// ❌ 避免
void draw(int x, int y, int width, int height);

// ✅ 推荐
struct Rectangle {
  int x, y;
  int width, height;
};
void draw(const Rectangle& rect);
```

### 3.2 C.2: 如果类有不变式，使用class；如果数据成员可以独立变化，使用struct

```cpp
// struct: 简单数据聚合
struct Point {
  int x;
  int y;
};

// class: 有不变式需要维护
class Date {
 public:
  Date(int year, int month, int day);
  int year() const { return year_; }
  
 private:
  int year_;
  int month_;  // 1-12
  int day_;    // 1-31
  // 不变式: month和day必须有效
};
```

### 3.3 C.21: 如果定义或=delete了任何拷贝、移动或析构函数，定义或=delete所有

**Rule of Zero**: 优先使用智能指针，不需要定义这些函数

```cpp
// ✅ 推荐: Rule of Zero
class Widget {
  std::unique_ptr<Impl> pImpl_;
  // 不需要定义析构函数、拷贝/移动操作
};
```

**Rule of Five**: 如果必须定义，定义全部5个

```cpp
class Resource {
 public:
  Resource();
  ~Resource();
  Resource(const Resource&);
  Resource& operator=(const Resource&);
  Resource(Resource&&) noexcept;
  Resource& operator=(Resource&&) noexcept;
};
```

### 3.4 C.45: 不要定义只初始化数据成员的默认构造函数；使用成员初始化器

```cpp
// ❌ 避免
class Widget {
 public:
  Widget() : x_(0), y_(0) {}
 private:
  int x_;
  int y_;
};

// ✅ 推荐
class Widget {
 private:
  int x_ = 0;
  int y_ = 0;
};
```

---

## 四、函数设计 (C++ Core Guidelines)

### 4.1 F.1: 将有意义的操作"打包"成精心命名的函数

```cpp
// ❌ 避免
void process() {
  // 100行代码做各种事情
}

// ✅ 推荐
void process() {
  validate_input();
  transform_data();
  write_output();
}
```

### 4.2 F.2: 函数应该执行单一逻辑操作

函数应该短小，理想情况下不超过40行

### 4.3 F.15: 优先使用简单和常规的方式传递信息

**参数传递指南**:

```cpp
// 小对象（<= 2-3个字（8-12字节））：传值
void f(int x);
void f(Point p);  // Point是{int x, y;}

// 只读大对象：const引用
void f(const string& s);
void f(const vector<int>& v);

// 只读小对象（可能）：string_view
void f(string_view s);

// 输出参数：指针（明确表示可能修改）
void f(int* out);

// 输入输出参数：引用
void f(string& s);

// 移动语义：右值引用
void f(vector<int>&& v);

// 所有权转移：unique_ptr
void f(unique_ptr<Widget> w);

// 共享所有权：shared_ptr
void f(shared_ptr<Widget> w);
```

### 4.4 F.16: 对于"输入"参数，按值传递廉价拷贝的类型，其他按const引用传递

```cpp
void f1(const string& s);  // ✅ 大对象
void f2(string_view s);    // ✅ 更好：只读视图
void f3(int x);            // ✅ 小对象
void f4(const int& x);     // ❌ 不必要的引用
```

### 4.5 F.20: 对于"输出"值，优先返回值而非输出参数

```cpp
// ❌ 避免
void get_data(vector<int>* out);

// ✅ 推荐
vector<int> get_data();

// ✅ 可能失败时使用optional
optional<Data> get_data();
```

### 4.6 F.21: 要返回多个"输出"值，优先返回结构体或tuple

```cpp
// ❌ 避免
void get_user_info(string* name, int* age);

// ✅ 推荐
struct UserInfo {
  string name;
  int age;
};
UserInfo get_user_info();

// 或使用tuple + 结构化绑定
pair<string, int> get_user_info();
auto [name, age] = get_user_info();
```

---

## 五、资源管理 (C++ Core Guidelines)

### 5.1 R.1: 使用资源句柄和RAII自动管理资源

```cpp
// ❌ 避免
void f() {
  FILE* file = fopen("file.txt", "r");
  // ... 使用file ...
  fclose(file);  // 容易忘记或异常时泄漏
}

// ✅ 推荐
void f() {
  ifstream file("file.txt");
  // ... 使用file ...
  // 自动关闭
}
```

### 5.2 R.3: 裸指针（T*）不拥有所有权

```cpp
// ✅ 明确所有权
unique_ptr<Widget> owner = make_unique<Widget>();
Widget* observer = owner.get();  // 不拥有，只观察
```

### 5.3 R.11: 避免显式调用new和delete

```cpp
// ❌ 避免
Widget* w = new Widget();
delete w;

// ✅ 推荐
auto w = make_unique<Widget>();
```

### 5.4 R.20-R.23: 使用智能指针表示所有权

```cpp
// 独占所有权
unique_ptr<Widget> w = make_unique<Widget>();

// 共享所有权
shared_ptr<Widget> w = make_shared<Widget>();

// 弱引用（不影响生命周期）
weak_ptr<Widget> w_weak = w;
```

---

## 六、错误处理 (C++ Core Guidelines)

### 6.1 E.2: 抛出异常表示无法完成函数的任务

```cpp
// ✅ 使用异常处理真正的错误
void open_file(const string& path) {
  ifstream file(path);
  if (!file.is_open()) {
    throw runtime_error("Cannot open file: " + path);
  }
}
```

### 6.2 E.3: 异常仅用于错误处理

```cpp
// ❌ 避免：用异常控制流程
try {
  int value = find_value(key);
} catch (NotFound&) {
  // 未找到不是异常情况
}

// ✅ 推荐：使用optional
optional<int> value = find_value(key);
if (value) {
  // 使用value
}
```

### 6.3 E.12: 使用noexcept当函数不能或不应该抛出异常

```cpp
void swap(Data& a, Data& b) noexcept {
  // 不会抛出异常
}
```

### 6.4 E.16: 析构函数、释放和swap绝不能失败

```cpp
class Resource {
 public:
  ~Resource() noexcept {  // 析构函数必须noexcept
    // 清理资源
  }
};
```

---

## 七、性能优化 (C++ Core Guidelines)

### 7.1 Per.1: 不要无理由地优化

**原则**: 
1. 先让代码正确
2. 测量性能
3. 优化瓶颈
4. 再次测量

### 7.2 Per.4: 不要假设复杂代码一定比简单代码快

```cpp
// ✅ 简单清晰
for (const auto& item : items) {
  process(item);
}

// ❌ 不必要的复杂优化
for (size_t i = 0, n = items.size(); i < n; ++i) {
  process(items[i]);
}
```

### 7.3 Per.5: 不要假设低级代码一定比高级代码快

现代编译器优化很强大，高级抽象通常不会带来性能损失

### 7.4 Per.7: 设计以支持优化

```cpp
// ✅ 支持移动语义
class Buffer {
 public:
  Buffer(Buffer&&) noexcept = default;
  Buffer& operator=(Buffer&&) noexcept = default;
};

// ✅ 支持RVO
Buffer create_buffer() {
  Buffer buf;
  // 初始化
  return buf;  // 不需要std::move
}
```

### 7.5 Per.10: 依赖静态类型系统

```cpp
// ✅ 使用类型表达意图
void process(span<const int> data);  // 明确：只读数组视图

// ❌ 避免
void process(const int* data, size_t size);  // 容易出错
```

### 7.6 Per.11: 将计算从运行时移到编译时

```cpp
// ✅ 编译期计算
constexpr int square(int x) { return x * x; }
constexpr int result = square(5);  // 编译期计算

// ✅ 编译期检查
static_assert(sizeof(int) == 4, "int must be 4 bytes");
```

### 7.7 Per.19: 可预测的内存访问比不可预测的快

```cpp
// ✅ 顺序访问（缓存友好）
for (size_t i = 0; i < n; ++i) {
  sum += array[i];
}

// ❌ 随机访问（缓存不友好）
for (size_t i = 0; i < n; ++i) {
  sum += array[random_indices[i]];
}
```

---

## 八、并发编程 (C++ Core Guidelines)

### 8.1 CP.1: 假设代码将作为多线程程序的一部分运行

设计时考虑线程安全

### 8.2 CP.2: 避免数据竞争

```cpp
// ❌ 数据竞争
int counter = 0;
void increment() {
  ++counter;  // 不安全
}

// ✅ 使用互斥锁
int counter = 0;
mutex counter_mutex;
void increment() {
  lock_guard<mutex> lock(counter_mutex);
  ++counter;
}

// ✅ 使用原子变量
atomic<int> counter{0};
void increment() {
  counter.fetch_add(1);
}
```

### 8.3 CP.3: 最小化可写数据的显式共享

```cpp
// ✅ 使用const减少共享
void worker(const shared_ptr<const Data>& data) {
  // 只读访问，不需要同步
}
```

### 8.4 CP.20: 使用RAII，绝不要使用裸的lock()/unlock()

```cpp
// ❌ 避免
mutex m;
m.lock();
// ... 危险：异常会导致死锁
m.unlock();

// ✅ 推荐
mutex m;
lock_guard<mutex> lock(m);
// ... 自动解锁
```

### 8.5 CP.22: 绝不要在持有锁时调用未知代码

```cpp
// ❌ 危险
void process() {
  lock_guard<mutex> lock(m);
  callback();  // 可能死锁
}

// ✅ 推荐
void process() {
  Data data;
  {
    lock_guard<mutex> lock(m);
    data = get_data();
  }
  callback(data);  // 锁外调用
}
```

---

## 九、现代C++特性使用

### 9.1 使用auto简化类型声明

```cpp
// ✅ 推荐
auto it = container.begin();
auto value = compute_value();

// ❌ 避免过度使用
auto x = 5;  // int更清晰
```

### 9.2 使用范围for循环

```cpp
// ✅ 推荐
for (const auto& item : items) {
  process(item);
}

// ❌ 避免
for (size_t i = 0; i < items.size(); ++i) {
  process(items[i]);
}
```

### 9.3 使用nullptr替代NULL

```cpp
// ✅ 推荐
int* ptr = nullptr;

// ❌ 避免
int* ptr = NULL;
int* ptr = 0;
```

### 9.4 使用override和final

```cpp
class Derived : public Base {
 public:
  void method() override;  // ✅ 明确覆盖
  void final_method() final;  // ✅ 禁止进一步覆盖
};
```

### 9.5 使用[[nodiscard]]

```cpp
[[nodiscard]] bool is_valid() const;  // ✅ 不应忽略返回值
```

### 9.6 使用constexpr

```cpp
constexpr int factorial(int n) {
  return n <= 1 ? 1 : n * factorial(n - 1);
}
```

### 9.7 使用结构化绑定 (C++17)

```cpp
map<string, int> data;
for (const auto& [key, value] : data) {
  cout << key << ": " << value << endl;
}
```

### 9.8 使用std::optional (C++17)

```cpp
optional<int> find_value(const string& key);

if (auto value = find_value("key"); value) {
  cout << *value << endl;
}
```

### 9.9 使用std::variant (C++17)

```cpp
variant<int, double, string> data;
data = 42;

visit([](auto&& arg) {
  cout << arg << endl;
}, data);
```

---

## 十、避免的做法

### 10.1 避免使用new和delete

```cpp
// ❌ 避免
Widget* w = new Widget();
delete w;

// ✅ 推荐
auto w = make_unique<Widget>();
```

### 10.2 避免C风格类型转换

```cpp
// ❌ 避免
int* p = (int*)ptr;

// ✅ 推荐
int* p = static_cast<int*>(ptr);
int* p = reinterpret_cast<int*>(ptr);
```

### 10.3 避免C风格数组

```cpp
// ❌ 避免
int arr[100];

// ✅ 推荐
array<int, 100> arr;
vector<int> arr(100);
```

### 10.4 避免在头文件中using namespace

```cpp
// ❌ 避免（在头文件中）
using namespace std;

// ✅ 推荐
using std::string;  // 或直接使用std::string
```

### 10.5 避免魔法数字

```cpp
// ❌ 避免
if (status == 42) { }

// ✅ 推荐
constexpr int kStatusSuccess = 42;
if (status == kStatusSuccess) { }
```

---

## 十一、快速检查清单

### 命名检查
- [ ] 类名使用PascalCase
- [ ] 函数名使用PascalCase
- [ ] 变量名使用snake_case
- [ ] 成员变量有_后缀或m_前缀
- [ ] 常量使用k前缀+PascalCase
- [ ] 宏使用全大写+下划线

### 资源管理检查
- [ ] 使用智能指针，避免new/delete
- [ ] 遵循RAII原则
- [ ] 使用Rule of Zero或Rule of Five

### 函数设计检查
- [ ] 函数短小（<40行）
- [ ] 单一职责
- [ ] 参数传递合理（小对象传值，大对象const引用）
- [ ] 优先返回值而非输出参数

### 错误处理检查
- [ ] 使用optional表示可能不存在
- [ ] 使用异常处理真正的错误
- [ ] 析构函数标记noexcept

### 性能检查
- [ ] 避免不必要的拷贝
- [ ] 使用string_view和span
- [ ] 使用移动语义
- [ ] 容器预留空间

### 并发检查
- [ ] 使用RAII管理锁
- [ ] 避免数据竞争
- [ ] 不在锁内调用未知代码

### 现代C++检查
- [ ] 使用auto简化声明
- [ ] 使用范围for循环
- [ ] 使用nullptr
- [ ] 使用override/final
- [ ] 使用constexpr

---

## 参考资料

本文档基于以下标准提取核心要点：

1. **Google C++ Style Guide**
   - 在线版本: https://google.github.io/styleguide/cppguide.html
   - 涵盖：命名、格式、类设计、函数、注释等

2. **C++ Core Guidelines**
   - 在线版本: https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines
   - 涵盖：资源管理、错误处理、性能、并发等

3. **项目特定规范**
   - Google-CPP-软件架构师角色定义.md
   - WPS构建系统规范

---

**注意**: 本文档是精简版本，完整规范请参考原始文档。在实际审查中，应结合项目具体情况灵活应用。
