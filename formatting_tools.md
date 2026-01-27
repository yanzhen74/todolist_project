# 代码格式化工具使用指南

本项目使用以下代码格式化和检查工具来维护代码质量：

## 工具列表

1. **isort** - 自动整理import语句顺序
2. **black** - 自动格式化Python代码风格
3. **flake8** - 检查代码风格和错误
4. **pylint** - 详细代码分析和潜在错误检查

## 安装

```bash
pip install -r requirements.txt
```

## 使用方法

### 1. 自动整理import语句

```bash
# 格式化单个文件
python -m isort your_file.py

# 格式化整个目录
python -m isort todolist/
python -m isort tests/

# 根据pyproject.toml配置文件格式化
python -m isort .
```

### 2. 使用Black格式化代码

```bash
# 格式化单个文件
python -m black your_file.py

# 格式化整个目录
python -m black todolist/ tests/
```

### 3. 检查代码风格

```bash
# 使用flake8检查
flake8 todolist/ tests/

# 使用pylint检查
pylint todolist/ tests/
```

## 配置文件

- `pyproject.toml` - 包含isort的配置
- `.pylintrc` - 包含pylint的配置

## 最佳实践

1. 在提交代码前运行 `isort` 和 `black` 来格式化代码
2. 定期运行 `flake8` 和 `pylint` 来检查代码质量
3. 遵循项目的编码规范和风格指南