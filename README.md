# BlogSystem（Flask 博客系统｜软件测试实践项目）

一个基于 Flask 的简易博客系统，用于练习 Web 应用的功能测试、权限测试与安全测试（CSRF），并沉淀测试文档与缺陷修复记录。

## 功能概览
- 用户注册 / 登录 / 登出（支持 next 重定向）
- 文章发布 / 编辑 / 删除（仅作者可操作）
- 文章列表与详情展示

## 技术栈
- 后端：Flask
- 数据库：SQLite + SQLAlchemy
- 认证：Flask-Login
- 表单与 CSRF：Flask-WTF

## 快速开始（本地运行）
### 方式 1：Windows 一键启动（推荐）
双击运行：
- `run.bat`

或在 PowerShell / CMD 中执行：sh
.\run.bat### 方式 2：命令行启动（.venv）
在项目根目录执行：ash
.\.venv\Scripts\python.exe app.py启动后访问：
- http://127.0.0.1:5000

> 依赖安装：sh
python -m pip install -r requirements.txt## 测试与文档
本项目包含测试计划、测试用例、缺陷报告与执行截图，见：
- `docs/TESTPLAN.md`（测试计划）
- `docs/TESTCASES.md`（测试用例）
- `docs/MANUAL_TESTING.md`（手工测试记录）
- `docs/BUG_REPORTS.md`（缺陷报告）
- `docs/screenshots/`（用例执行与缺陷截图）

## 测试重点
- 认证与重定向：登录 next 参数处理与站内跳转校验
- 权限控制：仅作者可编辑/删除文章（403/404 等异常流验证）
- 安全测试（CSRF）：覆盖创建/修改/删除等关键操作的 CSRF 校验与回归验证
- 工程可复现：requirements + 启动脚本（.venv/run.bat）保证环境一致性

## 目录结构
- `app.py`：应用入口与应用工厂
- `auth.py`：认证相关路由
- `blog.py`：文章相关路由
- `models.py`：数据模型
- `forms.py`：表单定义
- `templates/`：页面模板
- `docs/`：测试文档与截图

## 免责声明
该项目用于学习与测试实践，当前以开发环境方式运行（Flask Debug），不建议直接用于生产环境。
