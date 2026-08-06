# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-08-06

### Added

- 初始发布版本
- 支持 8 种编程语言：Python、JavaScript、TypeScript、Go、Rust、Java、Ruby、PHP
- 自动生成 6 种配置文件：AGENTS.md、CLAUDE.md、.cursorrules、Copilot 指令、MCP 配置、Skill 文件
- 项目分析功能：语言检测、框架检测、依赖解析、命令提取
- 代码质量分析：代码统计、质量评分、工具检测
- 健康报告：Agent 就绪度评分、代码质量评分
- 增量更新：保留手写内容，只更新生成区间
- JSON 输出：支持 Schema 校验
- 敏感环境变量自动过滤
- 并行工具检测优化性能
- 完整的测试覆盖（62 个测试）
