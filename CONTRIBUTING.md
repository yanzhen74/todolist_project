# 贡献指南

感谢您有兴趣为 TodoList 项目做贡献！我们欢迎各种形式的贡献，包括但不限于错误修复、新功能开发、文档改进和测试用例编写。

## 开发环境设置

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd todolist_project
   ```

2. **创建虚拟环境**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

4. **运行应用**
   ```bash
   python app.py
   ```

## 代码风格

- 遵循 PEP 8 Python 代码风格指南
- 使用有意义的变量和函数命名
- 编写清晰的注释和文档字符串
- 确保代码具有良好的可读性

## 提交规范

请遵循项目的 [Git Commit 规范](GIT_COMMIT_SPEC.md)：

- 格式：`<type>: <title>`
- 类型包括：`feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `enhance`, `perf`, `deploy`
- 标题首字母大写，结尾不使用句号
- 内容列表使用数字序号，清晰描述具体变更

## 测试

在提交代码之前，请确保：
1. 所有现有测试通过
2. 为新功能编写适当的测试
3. 运行测试套件：`python -m pytest tests/`

## Pull Request 流程

1. Fork 项目仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'feat: Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 报告问题

当报告问题时，请包含：
- 问题的详细描述
- 重现步骤
- 预期行为
- 实际行为
- 系统环境信息

## 联系方式

如有疑问，请在 GitHub 上创建 Issue 或联系项目维护者。