/**
 * PDF 权限密码移除工具 (C++ 版本)
 *
 * 使用 libqpdf 移除 PDF 文件的 owner/permission 密码，
 * 解锁打印、复制、编辑等受限操作。
 * 不处理 user/open 密码（即需要密码才能打开的 PDF）。
 *
 * 用法:
 *   pdf_unlock input.pdf                         # 解密单个文件
 *   pdf_unlock input.pdf -o output.pdf           # 指定输出路径
 *   pdf_unlock input.pdf --info                  # 仅查看加密信息
 *   pdf_unlock input.pdf -p "password"           # 提供已知密码
 *   pdf_unlock /path/to/pdfs/ --batch            # 批量解密
 *   pdf_unlock /path/to/pdfs/ --batch -r         # 递归批量解密
 *
 * 依赖: libqpdf (brew install qpdf)
 */

#include <qpdf/QPDF.hh>
#include <qpdf/QPDFExc.hh>
#include <qpdf/QPDFPageDocumentHelper.hh>
#include <qpdf/QPDFWriter.hh>

#include <algorithm>
#include <cstring>
#include <filesystem>
#include <iostream>
#include <string>
#include <vector>

namespace fs = std::filesystem;

// ──────────────────────────────────────────────────────────────
// 终端颜色输出
// ──────────────────────────────────────────────────────────────

struct Colors {
    static bool enabled;
    static const char* red()    { return enabled ? "\033[91m" : ""; }
    static const char* green()  { return enabled ? "\033[92m" : ""; }
    static const char* yellow() { return enabled ? "\033[93m" : ""; }
    static const char* blue()   { return enabled ? "\033[94m" : ""; }
    static const char* cyan()   { return enabled ? "\033[96m" : ""; }
    static const char* bold()   { return enabled ? "\033[1m"  : ""; }
    static const char* reset()  { return enabled ? "\033[0m"  : ""; }
};

bool Colors::enabled = true;

static void print_info(const std::string& msg) {
    std::cout << Colors::blue() << "i" << Colors::reset() << " " << msg << "\n";
}

static void print_success(const std::string& msg) {
    std::cout << Colors::green() << "+" << Colors::reset() << " " << msg << "\n";
}

static void print_warning(const std::string& msg) {
    std::cout << Colors::yellow() << "!" << Colors::reset() << " " << msg << "\n";
}

static void print_error(const std::string& msg) {
    std::cerr << Colors::red() << "x" << Colors::reset() << " " << msg << "\n";
}

static void print_header(const std::string& msg) {
    std::cout << "\n" << Colors::bold() << Colors::cyan() << msg
              << Colors::reset() << "\n";
    for (int i = 0; i < 50; ++i) std::cout << "-";
    std::cout << "\n";
}

// ──────────────────────────────────────────────────────────────
// 加密方法名称映射
// ──────────────────────────────────────────────────────────────

static const char* encryption_method_name(QPDF::encryption_method_e method) {
    switch (method) {
        case QPDF::e_none:    return "None";
        case QPDF::e_unknown: return "Unknown";
        case QPDF::e_rc4:     return "RC4";
        case QPDF::e_aes:     return "AES";
        case QPDF::e_aesv3:   return "AES-256";
        default:               return "Unknown";
    }
}

// ──────────────────────────────────────────────────────────────
// Task 2.1: EncryptionInfo + get_encryption_info()
// ──────────────────────────────────────────────────────────────

struct EncryptionInfo {
    std::string file;
    bool encrypted          = false;
    bool has_user_password   = false;
    bool has_owner_password  = false;
    int R = 0;
    int P = 0;
    int V = 0;
    QPDF::encryption_method_e stream_method = QPDF::e_none;
    QPDF::encryption_method_e string_method = QPDF::e_none;
    QPDF::encryption_method_e file_method   = QPDF::e_none;
    std::vector<std::string> restrictions;
};

static EncryptionInfo get_encryption_info(const std::string& pdf_path,
                                          const std::string& password = "") {
    EncryptionInfo info;
    info.file = pdf_path;

    try {
        QPDF qpdf;
        if (password.empty()) {
            qpdf.processFile(pdf_path.c_str());
        } else {
            qpdf.processFile(pdf_path.c_str(), password.c_str());
        }

        if (!qpdf.isEncrypted()) {
            return info;
        }

        info.encrypted = true;
        qpdf.isEncrypted(info.R, info.P, info.V,
                          info.stream_method, info.string_method, info.file_method);

        // 能用空密码打开 → 无 user password, 有 owner password
        if (password.empty()) {
            info.has_user_password = false;
            info.has_owner_password = true;
        } else {
            info.has_user_password = !qpdf.userPasswordMatched();
            info.has_owner_password = true;
        }

        // 收集受限操作
        if (!qpdf.allowAccessibility())
            info.restrictions.emplace_back("辅助功能提取");
        if (!qpdf.allowExtractAll())
            info.restrictions.emplace_back("内容提取");
        if (!qpdf.allowPrintLowRes())
            info.restrictions.emplace_back("低分辨率打印");
        if (!qpdf.allowPrintHighRes())
            info.restrictions.emplace_back("高分辨率打印");
        if (!qpdf.allowModifyAssembly())
            info.restrictions.emplace_back("文档组装");
        if (!qpdf.allowModifyForm())
            info.restrictions.emplace_back("表单填写");
        if (!qpdf.allowModifyAnnotation())
            info.restrictions.emplace_back("修改注释");
        if (!qpdf.allowModifyOther())
            info.restrictions.emplace_back("其他修改");

    } catch (const QPDFExc& e) {
        if (e.getErrorCode() == qpdf_e_password) {
            info.encrypted = true;
            info.has_user_password = true;
        } else {
            print_error(std::string("读取文件失败: ") + e.what());
        }
    } catch (const std::exception& e) {
        print_error(std::string("读取文件失败: ") + e.what());
    }

    return info;
}

// ──────────────────────────────────────────────────────────────
// Task 2.2: display_encryption_info()
// ──────────────────────────────────────────────────────────────

static void display_encryption_info(const EncryptionInfo& info) {
    if (info.file.empty()) return;

    print_header("PDF 加密信息");
    std::cout << "  文件: " << info.file << "\n";
    std::cout << "  加密: " << (info.encrypted ? "是" : "否") << "\n";

    if (!info.encrypted) {
        print_success("该文件未加密，无需处理");
        return;
    }

    std::cout << "  打开密码(User): "
              << (info.has_user_password ? "有" : "无") << "\n";
    std::cout << "  权限密码(Owner): "
              << (info.has_owner_password ? "有" : "无") << "\n";
    std::cout << "  加密版本: R=" << info.R << " V=" << info.V
              << " P=" << info.P << "\n";
    std::cout << "  流加密: " << encryption_method_name(info.stream_method) << "\n";
    std::cout << "  字符串加密: " << encryption_method_name(info.string_method) << "\n";
    std::cout << "  文件加密: " << encryption_method_name(info.file_method) << "\n";

    if (!info.restrictions.empty()) {
        std::cout << "\n  " << Colors::yellow() << "受限操作:"
                  << Colors::reset() << "\n";
        for (const auto& r : info.restrictions) {
            std::cout << "    [x] " << r << "\n";
        }
    }

    if (info.has_user_password) {
        print_warning("该文件有打开密码，需要提供正确密码才能解密");
    } else if (info.has_owner_password) {
        print_info("该文件仅有权限密码，可直接移除");
    }
}

// ──────────────────────────────────────────────────────────────
// Task 3.1: generate_output_path()
// ──────────────────────────────────────────────────────────────

static std::string generate_output_path(const std::string& input_path,
                                        const std::string& output_path = "") {
    if (!output_path.empty()) return output_path;

    fs::path p(input_path);
    std::string stem = p.stem().string();
    std::string ext  = p.extension().string();
    return (p.parent_path() / (stem + "_已解锁" + ext)).string();
}

// ──────────────────────────────────────────────────────────────
// Task 3.2 - 3.4 + 4.1: unlock_pdf() (解密 + 安全校验 + 密码 + 验证)
// ──────────────────────────────────────────────────────────────

static bool unlock_pdf(const std::string& input_path,
                       const std::string& output_path_arg = "",
                       const std::string& password = "") {
    std::string abs_input = fs::absolute(input_path).string();
    std::string abs_output = generate_output_path(abs_input, output_path_arg);

    // Task 3.3: 安全校验 - 文件存在性
    if (!fs::exists(abs_input)) {
        print_error("文件不存在: " + abs_input);
        return false;
    }

    // Task 3.3: 安全校验 - 防止覆盖输入
    if (fs::exists(abs_output) && fs::equivalent(abs_input, abs_output)) {
        print_error("输出路径不能与输入路径相同");
        return false;
    }
    if (abs_input == abs_output) {
        print_error("输出路径不能与输入路径相同");
        return false;
    }

    print_info("输入: " + abs_input);
    print_info("输出: " + abs_output);

    try {
        QPDF qpdf;

        // Task 3.4: 密码支持
        if (password.empty()) {
            qpdf.processFile(abs_input.c_str());
        } else {
            qpdf.processFile(abs_input.c_str(), password.c_str());
        }

        if (!qpdf.isEncrypted()) {
            print_warning("文件未加密，直接复制");
            fs::copy_file(abs_input, abs_output,
                          fs::copy_options::overwrite_existing);
            return true;
        }

        // Task 3.2: 核心解密 - 写出时不保留加密
        QPDFWriter writer(qpdf, abs_output.c_str());
        writer.setPreserveEncryption(false);
        writer.setStaticID(false);
        writer.write();

        // Task 4.1: 解密后自动验证
        try {
            QPDF verify_pdf;
            verify_pdf.processFile(abs_output.c_str());

            if (verify_pdf.isEncrypted()) {
                print_error("解密结果验证失败，输出文件可能仍有加密");
                return false;
            }

            // 验证页面完整性
            QPDFPageDocumentHelper helper(verify_pdf);
            auto pages = helper.getAllPages();
            auto file_size = fs::file_size(abs_output);

            print_success("解密成功! 输出文件: " + abs_output +
                          " (" + std::to_string(file_size) + " 字节, " +
                          std::to_string(pages.size()) + " 页)");
            return true;

        } catch (const std::exception& e) {
            print_error(std::string("验证失败: ") + e.what());
            return false;
        }

    } catch (const QPDFExc& e) {
        if (e.getErrorCode() == qpdf_e_password) {
            print_error("密码错误或该文件需要打开密码(User Password)");
            if (password.empty()) {
                print_info("提示: 使用 -p 参数提供密码");
            }
        } else {
            print_error(std::string("解密失败: ") + e.what());
        }
        return false;
    } catch (const std::exception& e) {
        print_error(std::string("解密失败: ") + e.what());
        return false;
    }
}

// ──────────────────────────────────────────────────────────────
// Task 5.1 + 5.2: batch_unlock()
// ──────────────────────────────────────────────────────────────

struct BatchResult {
    int success = 0;
    int fail    = 0;
    int skip    = 0;
};

static BatchResult batch_unlock(const std::string& directory,
                                const std::string& password = "",
                                bool recursive = false) {
    BatchResult result;
    std::string abs_dir = fs::absolute(directory).string();

    if (!fs::is_directory(abs_dir)) {
        print_error("目录不存在: " + abs_dir);
        return result;
    }

    // 收集 PDF 文件
    std::vector<fs::path> pdf_files;

    // Task 5.2: 递归 vs 非递归
    if (recursive) {
        for (const auto& entry : fs::recursive_directory_iterator(abs_dir)) {
            if (entry.is_regular_file() && entry.path().extension() == ".pdf") {
                pdf_files.push_back(entry.path());
            }
        }
    } else {
        for (const auto& entry : fs::directory_iterator(abs_dir)) {
            if (entry.is_regular_file() && entry.path().extension() == ".pdf") {
                pdf_files.push_back(entry.path());
            }
        }
    }

    std::sort(pdf_files.begin(), pdf_files.end());

    if (pdf_files.empty()) {
        print_warning("目录中未找到 PDF 文件: " + abs_dir);
        return result;
    }

    print_header("批量解密 - 共 " + std::to_string(pdf_files.size()) + " 个 PDF 文件");

    int total = static_cast<int>(pdf_files.size());
    for (int i = 0; i < total; ++i) {
        const auto& pdf_path = pdf_files[i];

        // Task 5.1: 跳过已解锁文件
        if (pdf_path.stem().string().find("_已解锁") != std::string::npos) {
            result.skip++;
            continue;
        }

        std::cout << "\n[" << (i + 1) << "/" << total << "] "
                  << pdf_path.filename().string() << "\n";

        if (unlock_pdf(pdf_path.string(), "", password)) {
            result.success++;
        } else {
            result.fail++;
        }
    }

    print_header("批量处理完成");
    std::cout << "  成功: " << Colors::green()  << result.success << Colors::reset() << "\n";
    std::cout << "  失败: " << Colors::red()    << result.fail    << Colors::reset() << "\n";
    std::cout << "  跳过: " << Colors::yellow() << result.skip    << Colors::reset() << "\n";

    return result;
}

// ──────────────────────────────────────────────────────────────
// Task 1.2: 命令行参数解析
// ──────────────────────────────────────────────────────────────

struct Options {
    std::string input;
    std::string output;
    std::string password;
    bool batch     = false;
    bool recursive = false;
    bool info_only = false;
    bool no_color  = false;
    bool help      = false;
};

static void print_usage(const char* prog) {
    std::cout << R"(
PDF 权限密码移除工具 (C++ 版本) - 解锁打印、复制、编辑等受限操作

用法:
  )" << prog << R"( <input> [选项]

参数:
  input                    PDF 文件路径或目录路径（批量模式）

选项:
  -o, --output <path>      输出文件路径（默认: 原文件名_已解锁.pdf）
  -p, --password <pwd>     已知的密码（如有）
  --batch                  批量处理目录下所有 PDF 文件
  -r, --recursive          递归处理子目录（与 --batch 配合使用）
  --info                   仅显示 PDF 加密信息，不进行解密
  --no-color               禁用颜色输出
  -h, --help               显示帮助信息

示例:
  )" << prog << R"( input.pdf                         # 解密单个文件
  )" << prog << R"( input.pdf -o unlocked.pdf         # 指定输出路径
  )" << prog << R"( /path/to/pdfs/ --batch            # 批量解密
  )" << prog << R"( /path/to/pdfs/ --batch -r         # 递归批量解密
  )" << prog << R"( input.pdf -p "abc123"             # 提供已知密码
  )" << prog << R"( input.pdf --info                  # 仅查看加密信息

注意:
  本工具仅处理权限密码(Owner Password)，不处理打开密码(User Password)。
  请仅对您拥有或有权修改的 PDF 文件使用此工具。
)";
}

static Options parse_args(int argc, char* argv[]) {
    Options opts;

    for (int i = 1; i < argc; ++i) {
        std::string arg = argv[i];

        if (arg == "-h" || arg == "--help") {
            opts.help = true;
        } else if (arg == "-o" || arg == "--output") {
            if (i + 1 < argc) opts.output = argv[++i];
        } else if (arg == "-p" || arg == "--password") {
            if (i + 1 < argc) opts.password = argv[++i];
        } else if (arg == "--batch") {
            opts.batch = true;
        } else if (arg == "-r" || arg == "--recursive") {
            opts.recursive = true;
        } else if (arg == "--info") {
            opts.info_only = true;
        } else if (arg == "--no-color") {
            opts.no_color = true;
        } else if (opts.input.empty()) {
            opts.input = arg;
        } else {
            print_error("未知参数: " + arg);
        }
    }

    return opts;
}

// ──────────────────────────────────────────────────────────────
// main
// ──────────────────────────────────────────────────────────────

int main(int argc, char* argv[]) {
    Options opts = parse_args(argc, argv);

    if (opts.help || opts.input.empty()) {
        print_usage(argv[0]);
        return opts.help ? 0 : 1;
    }

    if (opts.no_color) {
        Colors::enabled = false;
    }

    print_header("PDF 权限密码移除工具");

    // --info: 仅查看加密信息
    if (opts.info_only) {
        auto info = get_encryption_info(opts.input, opts.password);
        display_encryption_info(info);
        return 0;
    }

    // --batch: 批量模式
    if (opts.batch) {
        auto result = batch_unlock(opts.input, opts.password, opts.recursive);
        return result.fail > 0 ? 1 : 0;
    }

    // 单文件模式
    bool success = unlock_pdf(opts.input, opts.output, opts.password);
    return success ? 0 : 1;
}
