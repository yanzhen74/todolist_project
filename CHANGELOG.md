# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2026-01-18

### Added
- 增加了周期待办事项功能，支持多种周期类型
- 支持的周期类型：年/月/周/日/小时/分钟
- 每周周期支持特定日期选择
- 标记周期待办事项完成后自动更新到下一次出现时间

### Fixed
- 修复了每周周期待办事项添加报错问题
- 修复了`test_add_monthly_recurring_todo`测试用例
- 修复了`test_deadline_status_display`测试用例的StaleElementReferenceException问题
- 修复了`test_add_todo_item`测试用例，确保能正确找到添加的待办事项
- 修复了`test_mark_todo_complete`测试用例，添加了测试前清空现有待办事项的代码

### Changed
- 更新了数据库架构，添加了周期相关字段
- 完善了README文档，添加了周期功能说明
- 改进了测试覆盖，添加了周期功能相关测试
- 优化了所有测试用例，添加了测试前清空现有待办事项的代码，确保测试环境干净
- 改进了测试用例的稳定性，添加了更详细的调试信息和更可靠的元素查找逻辑

## [1.1.0] - 2026-01-17

### Added
- 增加了待办事项截止日期功能
- 添加了截止日期状态显示（正常、即将过期、已过期）
- 实现了自动数据库迁移，确保向后兼容
- 增加了更详细的测试覆盖

### Changed
- 改进了前端UI，添加了日期时间选择器
- 优化了测试用例，确保覆盖新功能

## [1.0.0] - 2026-01-16

### Added
- 初始版本，实现了基本的待办事项功能
- 支持添加、删除、标记完成待办事项
- 支持本地SQLite存储
- 实现了基本的端到端测试
- 添加了多环境配置支持
- 实现了自动数据库初始化

### Changed
- 完善了README文档
- 优化了项目结构
- 改进了代码质量和安全性
