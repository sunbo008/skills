cmake_minimum_required(VERSION 3.16)
project(pdf_unlock VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# ── 查找 libqpdf ──────────────────────────────────────────────
# 优先 pkg-config，fallback 到 Homebrew 路径
find_package(PkgConfig QUIET)
if(PkgConfig_FOUND)
    pkg_check_modules(QPDF QUIET libqpdf)
endif()

if(NOT QPDF_FOUND)
    # Homebrew 路径 (Apple Silicon / Intel)
    foreach(_prefix /opt/homebrew /usr/local)
        if(EXISTS "${_prefix}/include/qpdf/QPDF.hh")
            set(QPDF_INCLUDE_DIRS "${_prefix}/include")
            set(QPDF_LIBRARY_DIRS "${_prefix}/lib")
            find_library(QPDF_LIB qpdf HINTS "${_prefix}/lib")
            if(QPDF_LIB)
                set(QPDF_LIBRARIES "${QPDF_LIB}")
                set(QPDF_FOUND TRUE)
                message(STATUS "Found qpdf at ${_prefix}")
                break()
            endif()
        endif()
    endforeach()
endif()

if(NOT QPDF_FOUND)
    message(FATAL_ERROR
        "libqpdf not found. Install with: brew install qpdf")
endif()

# ── 可执行文件 ────────────────────────────────────────────────
add_executable(pdf_unlock pdf_unlock.cpp)

target_include_directories(pdf_unlock PRIVATE ${QPDF_INCLUDE_DIRS})
target_link_directories(pdf_unlock PRIVATE ${QPDF_LIBRARY_DIRS})
target_link_libraries(pdf_unlock PRIVATE ${QPDF_LIBRARIES})

# ── 安装 ──────────────────────────────────────────────────────
install(TARGETS pdf_unlock DESTINATION bin)
