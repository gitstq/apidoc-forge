<div align="center">

# 🚀 APIDoc Forge

**Intelligent API Documentation Generator & Sync Engine**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-black)](https://github.com/psf/black)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

[English](#english) | [简体中文](#简体中文) | [繁體中文](#繁體中文)

</div>

---

<a name="english"></a>
## 🇺🇸 English

### 🎉 Introduction

APIDoc Forge is a **lightweight, zero-dependency** Python CLI tool that automatically generates beautiful API documentation from your Python source code. It parses docstrings, type hints, and code structure to produce comprehensive documentation in multiple formats.

**Key Differentiators:**
- 🎯 **Zero Dependencies** - Pure Python standard library, no external packages required
- 🚀 **Multiple Output Formats** - Markdown, HTML, JSON, and OpenAPI/Swagger
- 🧠 **Intelligent Parsing** - Supports Google-style, NumPy-style, and reStructuredText docstrings
- ⚡ **AST-Based Analysis** - Accurate code parsing using Python's Abstract Syntax Tree
- 🔄 **Sync Ready** - Built for CI/CD integration with watch mode support

### ✨ Core Features

| Feature | Description |
|---------|-------------|
| 📖 **Smart Docstring Parsing** | Extracts parameters, return types, raises, and examples from docstrings |
| 🎨 **Beautiful HTML Output** | Syntax-highlighted, responsive documentation with dark mode code blocks |
| 📝 **Markdown Generation** | GitHub-flavored Markdown perfect for README files |
| 🔌 **OpenAPI Support** | Generate Swagger-compatible specifications for REST APIs |
| 📊 **JSON Export** | Machine-readable documentation for further processing |
| 🏷️ **Type Hint Recognition** | Full support for Python 3.8+ type annotations |
| 🎯 **Async Function Support** | Properly documents async/await functions |
| 🔍 **Class & Method Analysis** | Comprehensive OOP documentation including inheritance |

### 🚀 Quick Start

#### Installation

```bash
# Clone the repository
git clone https://github.com/gitstq/apidoc-forge.git
cd apidoc-forge

# Or install directly
pip install -e .
```

#### Usage

```bash
# Generate Markdown documentation
python apidoc_forge.py analyze ./src -o ./docs -f markdown

# Generate HTML documentation
python apidoc_forge.py analyze ./src -o ./docs -f html

# Generate OpenAPI specification
python apidoc_forge.py analyze ./src -o ./docs -f openapi --title "My API"

# Analyze a single file
python apidoc_forge.py analyze my_module.py -o ./docs -f markdown
```

### 📖 Detailed Usage

#### Command Line Options

```bash
apidoc-forge analyze [PATH] [OPTIONS]

Arguments:
  PATH                    Path to Python file or directory

Options:
  -o, --output DIR        Output directory (default: ./docs)
  -f, --format FORMAT     Output format: markdown, html, json, openapi
  --title TITLE          Documentation title
  --pattern PATTERN      File pattern for directories (default: *.py)
  -v, --verbose          Enable verbose output
  -h, --help             Show help message
```

#### Example Output

**Input Python Code:**
```python
class UserManager:
    """Manages user operations and data persistence.
    
    Args:
        auto_save: Whether to automatically save changes.
    """
    
    def create_user(self, name: str, email: str) -> User:
        """Create a new user in the system.
        
        Args:
            name: Full name of the user.
            email: Valid email address.
        
        Returns:
            The newly created User object.
        
        Raises:
            ValueError: If email is invalid.
        """
        pass
```

**Generated Markdown:**
```markdown
### create_user

```python
def create_user(self, name: str, email: str) -> User
```

Create a new user in the system.

**Parameters:**
- `name` (*str*) - Full name of the user.
- `email` (*str*) - Valid email address.

**Returns:**
*User*
The newly created User object.

**Raises:**
- ValueError: If email is invalid.
```

### 💡 Design Philosophy

APIDoc Forge was designed with these principles:

1. **Zero Dependencies** - No pip install hell, works out of the box
2. **Pythonic** - Leverages AST for accurate parsing, not regex hacks
3. **Format Agnostic** - Generate once, output anywhere
4. **CI/CD Ready** - Perfect for automated documentation pipelines
5. **Developer Experience** - Clear error messages and verbose mode

### 📦 Supported Docstring Styles

- ✅ **Google Style** (recommended)
- ✅ **NumPy Style**
- ✅ **reStructuredText**
- ✅ **Epytext**

### 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

```bash
# Fork and clone
git clone https://github.com/yourusername/apidoc-forge.git

# Create a branch
git checkout -b feature/amazing-feature

# Make changes and commit
git commit -m "feat: add amazing feature"

# Push and create PR
git push origin feature/amazing-feature
```

### 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

<a name="简体中文"></a>
## 🇨🇳 简体中文

### 🎉 项目介绍

APIDoc Forge 是一款**轻量级、零依赖**的 Python CLI 工具，能够自动从 Python 源代码生成精美的 API 文档。它解析文档字符串、类型提示和代码结构，生成多种格式的综合文档。

**核心差异化优势：**
- 🎯 **零依赖** - 纯 Python 标准库，无需外部包
- 🚀 **多格式输出** - 支持 Markdown、HTML、JSON 和 OpenAPI/Swagger
- 🧠 **智能解析** - 支持 Google 风格、NumPy 风格和 reStructuredText 文档字符串
- ⚡ **基于 AST 分析** - 使用 Python 抽象语法树进行精确代码解析
- 🔄 **同步就绪** - 内置 CI/CD 集成支持，支持监视模式

### ✨ 核心特性

| 特性 | 描述 |
|------|------|
| 📖 **智能文档字符串解析** | 从文档字符串中提取参数、返回类型、异常和示例 |
| 🎨 **精美 HTML 输出** | 语法高亮、响应式设计，支持深色模式代码块 |
| 📝 **Markdown 生成** | 适合 README 文件的 GitHub 风格 Markdown |
| 🔌 **OpenAPI 支持** | 为 REST API 生成 Swagger 兼容规范 |
| 📊 **JSON 导出** | 机器可读的文档格式，便于进一步处理 |
| 🏷️ **类型提示识别** | 完全支持 Python 3.8+ 类型注解 |
| 🎯 **异步函数支持** | 正确文档化 async/await 函数 |
| 🔍 **类和方法分析** | 全面的面向对象文档，包括继承关系 |

### 🚀 快速开始

#### 安装

```bash
# 克隆仓库
git clone https://github.com/gitstq/apidoc-forge.git
cd apidoc-forge

# 或直接安装
pip install -e .
```

#### 使用

```bash
# 生成 Markdown 文档
python apidoc_forge.py analyze ./src -o ./docs -f markdown

# 生成 HTML 文档
python apidoc_forge.py analyze ./src -o ./docs -f html

# 生成 OpenAPI 规范
python apidoc_forge.py analyze ./src -o ./docs -f openapi --title "My API"

# 分析单个文件
python apidoc_forge.py analyze my_module.py -o ./docs -f markdown
```

### 📖 详细使用指南

#### 命令行选项

```bash
apidoc-forge analyze [路径] [选项]

参数:
  路径                    Python 文件或目录路径

选项:
  -o, --output 目录       输出目录 (默认: ./docs)
  -f, --format 格式       输出格式: markdown, html, json, openapi
  --title 标题           文档标题
  --pattern 模式         目录的文件匹配模式 (默认: *.py)
  -v, --verbose          启用详细输出
  -h, --help             显示帮助信息
```

#### 示例输出

**输入 Python 代码：**
```python
class UserManager:
    """管理用户操作和数据持久化。
    
    Args:
        auto_save: 是否自动保存更改。
    """
    
    def create_user(self, name: str, email: str) -> User:
        """在系统中创建新用户。
        
        Args:
            name: 用户的全名。
            email: 有效的电子邮件地址。
        
        Returns:
            新创建的 User 对象。
        
        Raises:
            ValueError: 如果电子邮件无效。
        """
        pass
```

**生成的 Markdown：**
```markdown
### create_user

```python
def create_user(self, name: str, email: str) -> User
```

在系统中创建新用户。

**参数：**
- `name` (*str*) - 用户的全名。
- `email` (*str*) - 有效的电子邮件地址。

**返回：**
*User*
新创建的 User 对象。

**异常：**
- ValueError: 如果电子邮件无效。
```

### 💡 设计理念

APIDoc Forge 遵循以下设计原则：

1. **零依赖** - 无需 pip 安装，开箱即用
2. **Pythonic** - 利用 AST 进行精确解析，而非正则表达式
3. **格式无关** - 一次生成，随处输出
4. **CI/CD 就绪** - 完美的自动化文档流水线工具
5. **开发者体验** - 清晰的错误信息和详细模式

### 📦 支持的文档字符串风格

- ✅ **Google 风格**（推荐）
- ✅ **NumPy 风格**
- ✅ **reStructuredText**
- ✅ **Epytext**

### 🤝 贡献指南

我们欢迎贡献！请参阅 [CONTRIBUTING.md](CONTRIBUTING.md) 了解指南。

```bash
# Fork 并克隆
git clone https://github.com/yourusername/apidoc-forge.git

# 创建分支
git checkout -b feature/amazing-feature

# 修改并提交
git commit -m "feat: add amazing feature"

# 推送并创建 PR
git push origin feature/amazing-feature
```

### 📄 开源协议

MIT 许可证 - 详情请参阅 [LICENSE](LICENSE) 文件。

---

<a name="繁體中文"></a>
## 🇹