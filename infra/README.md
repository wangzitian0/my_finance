# Infra - 基础设施

全局性基础设施管理，专注于环境、部署、监控和开发工具链。

## 组件结构

### 环境管理
- `env_status.py` - 环境状态检查
- `shutdown_all.py` - 服务关闭

### 部署配置
- `ansible/` - 自动化部署配置
- `k8s/` - Kubernetes部署配置
- `deployment.md` - 部署指南

### 开发工具
- `cleanup_merged_branches.py` - Git分支清理
- `install_git_hooks.py` - Git hooks安装
- `commit_data_changes.py` - 数据子模块提交
- `cleanup_obsolete_files.py` - 文件清理
- `git-workflow-optimization.md` - Git工作流文档

### 监控运维
- `monitoring.md` - 监控架构文档

## 使用方式

```bash
# 环境管理
pixi run env-status
pixi run shutdown-all

# Git工作流
pixi run cleanup-branches
pixi run install-git-hooks
pixi run commit-data-changes

# 部署
ansible-playbook infra/ansible/setup.yml
kubectl apply -f infra/k8s/
```

## 职责边界

- **全局环境**: Docker、K8s、数据库等基础服务
- **部署自动化**: CI/CD、配置管理
- **开发工具**: Git工具、代码质量检查
- **监控运维**: 系统监控、日志管理