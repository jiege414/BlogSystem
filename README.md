# BlogSystem（Flask 博客系统｜软件测试实践项目）

一个基于 Flask 的简易博客系统，用于练习 Web 应用的功能测试、权限测试与安全测试（CSRF），并沉淀测试文档与缺陷修复记录。

## 测试设计理念

基于风险优先级对测试用例进行分层设计（P0/P1/P2），优先覆盖权限控制、状态跳转与安全相关场景，形成可复用的 Web 应用测试模板。

## 功能概览
- 用户注册 / 登录 / 登出（支持 next 重定向）
- 文章发布 / 编辑 / 删除（仅作者可操作）
- 文章列表与详情展示
- 文章搜索（根据标题模糊搜索）
- 日志记录（关键操作记录 INFO 级别日志，支持双环境配置）

## 技术栈
- 后端：Flask
- 数据库：SQLite + SQLAlchemy
- 认证：Flask-Login
- 表单与 CSRF：Flask-WTF

## 数据库说明
- **类型**：SQLite（文件型数据库，无需单独安装）
- **位置**：`instance/blog.db`（应用首次运行时自动创建）
- **查看方式**：1、使用 DB Browser for SQLite 等工具打开 `instance/blog.db`
              2、或者在命令行中执行 `python scripts/show_form_content.py` 查看所有表数据；执行 `python scripts/show_schema.py` 查看数据库建表语句。

## 初次运行（环境配置）

如果是第一次运行本项目，请按以下步骤配置环境：

```bash
# 1. 克隆或下载项目后，进入项目目录
cd BlogSystem

# 2. 创建虚拟环境
python -m venv .venv

# 3. 激活虚拟环境
# Windows:
.\.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# 4. 安装依赖
pip install -r requirements.txt

# 5. 初始化数据库（可选，应用首次运行时会自动创建）
flask --app app init-db
```

完成以上步骤后，即可使用下方的启动方式运行项目。

## 快速开始（本地运行）

### 方式 1：Windows 一键启动（推荐）
双击运行：
- `run.bat`

或在 PowerShell / CMD 中执行：
.\run.bat
### 方式 2：命令行启动（.venv）
在项目根目录执行：
```bash
.\.venv\Scripts\python.exe run_app.py
```
或使用 Flask 命令：
```bash
set FLASK_APP=app:create_app
flask run --debug
```
启动后访问：
- http://127.0.0.1:5000

> 依赖安装（首次运行前执行）：
```bash
python -m pip install -r requirements.txt
```
### 方式 3：Linux/macOS 启动
```bash
# 进入项目目录
cd BlogSystem

# 创建并激活虚拟环境
python3 -m venv .venv
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 启动应用
python run_app.py
# 或使用 Flask 命令
export FLASK_APP=app:create_app
flask run --debug
```
> 启动后访问：http://127.0.0.1:5000  
> 退出虚拟环境：`deactivate`

## 测试与文档
本项目包含测试计划、测试用例、缺陷报告与执行截图，见：
- `docs/TESTPLAN.md`（测试计划）
- `docs/TESTCASES.md`（测试用例）
- `docs/MANUAL_TESTING.md`（手工测试记录）
- `docs/BUG_REPORTS.md`（缺陷报告）
- `docs/screenshots/`（用例执行与缺陷截图）

## 测试覆盖与产出
- 用例规模：手工测试用例 **63 条**（含搜索 4 条、日志 3 条），覆盖认证、文章、搜索、权限、日志、异常流与安全场景
- 覆盖模块：
  - 认证与重定向：登录 next 参数处理与站内跳转校验（防开放重定向）
  - 文章管理：创建、查看、编辑、删除、搜索（模糊匹配）
  - 权限控制：仅作者可编辑/删除文章（403/404 等异常流验证）
  - 安全测试（CSRF）：覆盖创建/修改/删除等关键操作的 CSRF 校验与回归验证
  - 日志验证：关键操作日志记录与级别验证
- 缺陷与改进：
  - 发现并推动修复 **3 个问题/风险点**（含 CSRF 相关安全语义优化与回归验证）
  - 通过文档化（测试计划/用例/缺陷/截图）形成可追溯的测试闭环

## 自动化测试（pytest）
- 安装（首次运行前执行）
python -m pip install pytest
- 运行：
python -m pytest -q

## 目录结构
```
BlogSystem/
├── app/                    # 应用核心代码
│   ├── __init__.py        # 应用工厂
│   ├── auth.py            # 认证蓝图（注册/登录/登出）
│   ├── blog.py            # 博客蓝图（文章CRUD/搜索）
│   ├── models.py          # 数据模型（User/Post）
│   ├── forms.py           # 表单定义
│   └── extensions.py      # Flask扩展初始化
├── scripts/               # 工具脚本
│   ├── run_app.py         # Python启动脚本
│   ├── check_user.py      # 用户信息检查
│   ├── show_schema.py     # 数据库结构查看
│   └── show_form_content.py  # 数据库内容查看
├── tests/                 # 自动化测试
│   ├── conftest.py        # pytest配置
│   ├── test_regression.py # 回归测试
│   ├── test_permissions.py # 权限测试
│   └── test_security_csrf.py # CSRF安全测试
├── templates/             # HTML模板
├── docs/                  # 测试文档与截图
├── run.bat                # Windows一键启动
├── run_app.py             # 根目录启动入口
├── requirements.txt       # 依赖列表
└── README.md              # 项目说明
```

## 免责声明
该项目用于学习与测试实践，当前以开发环境方式运行（Flask Debug），不建议直接用于生产环境。
