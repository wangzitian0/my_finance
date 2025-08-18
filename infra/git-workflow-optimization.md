# Git Workflow Optimization

## 概述

本文档描述了项目的Git工作流程优化措施，包括自动分支清理、Git hooks和最佳实践。

## 核心原则

1. **及时清理**: MR合并后立即清理相关分支
2. **自动化**: 使用脚本和hooks自动执行常见任务
3. **一致性**: 统一的commit格式和PR流程
4. **安全性**: 防止意外的数据丢失或错误提交

## 分支清理系统

### 自动分支清理脚本

位置: `scripts/cleanup_merged_branches.py`

功能:
- 自动识别已合并的PR分支
- 清理本地和远程的过时分支
- 修剪远程引用
- 支持交互式和自动模式

### 使用方法

```bash
# 查看会被清理的分支 (安全)
p3 cleanup-branches --dry-run

# 交互式清理 (推荐)
p3 cleanup-branches

# 自动清理 (适用于CI或定期维护)
p3 cleanup-branches --auto
```

### 清理规则

- **自动清理**: 最近30天内合并的PR分支
- **保护分支**: main, master, develop, staging, production 永不删除
- **安全检查**: 验证分支确实已合并才删除
- **远程优先**: 先删除远程分支，再删除本地分支

## Git Hooks 系统

### 自动安装

```bash
pixi run install-git-hooks
```

### Hook 功能

#### 1. Post-merge Hook
- **触发时机**: git merge 或 git pull 成功后
- **功能**: 
  - 检测是否在main分支
  - 自动清理合并的分支 (7天内)
  - 修剪远程引用
- **位置**: `.git/hooks/post-merge`

#### 2. Pre-push Hook  
- **触发时机**: git push 之前
- **功能**:
  - 检查分支是否落后main
  - 警告未提交的更改
  - 用户确认继续
- **位置**: `.git/hooks/pre-push`

#### 3. Commit-msg Hook
- **触发时机**: git commit 之前
- **功能**:
  - 验证commit格式 (type: description)
  - 检查issue引用
  - 跳过Claude Code签名的commit
- **位置**: `.git/hooks/commit-msg`

## 完整工作流程

### 1. 开始新功能

```bash
# 确保在最新的main分支
git checkout main
git pull origin main

# 创建feature分支
git checkout -b feature/description-fixes-ISSUE_NUMBER

# 开发功能...
```

### 2. 提交和推送

```bash
# 添加更改
git add .

# 提交 (commit-msg hook会验证格式)
git commit -m "feat: Add new functionality

Fixes #123

PR: https://github.com/wangzitian0/my_finance/pull/PLACEHOLDER

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# 推送 (pre-push hook会检查状态)
git push -u origin feature/description-fixes-123
```

### 3. 创建和管理PR

```bash
# 创建PR
gh pr create --title "feat: Add new functionality" --body "..."

# 更新commit with actual PR URL
git commit --amend -m "feat: Add new functionality

Fixes #123

PR: https://github.com/wangzitian0/my_finance/pull/456

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"

git push --force-with-lease
```

### 4. MR合并后清理

```bash
# 检查PR状态
gh pr view 456

# 如果已合并，自动清理分支
p3 cleanup-branches --auto

# 或手动清理
git push origin --delete feature/description-fixes-123
git branch -D feature/description-fixes-123
```

## 维护命令

### 定期维护

```bash
# 每周运行一次，清理过时分支
p3 cleanup-branches --auto

# 更新Git hooks
pixi run install-git-hooks

# 检查仓库健康状况
git fsck
git gc --prune=now
```

### 紧急清理

```bash
# 强制删除本地分支
git branch -D branch-name

# 删除远程分支
git push origin --delete branch-name

# 修剪所有远程引用
git remote prune origin

# 清理未跟踪的文件
git clean -fd
```

## 最佳实践

### Commit 格式

遵循约定式提交格式:
```
type(scope): description

Fixes #issue-number

PR: https://github.com/owner/repo/pull/number

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

**Type类型**:
- `feat`: 新功能
- `fix`: 错误修复
- `docs`: 文档更改
- `style`: 格式更改
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 构建/工具更改

### 分支命名

```
feature/description-fixes-ISSUE_NUMBER
bugfix/description-fixes-ISSUE_NUMBER
hotfix/description-fixes-ISSUE_NUMBER
```

### PR 最佳实践

1. **一个PR一个功能**: 保持PR专注和可审查
2. **详细描述**: 包含功能说明、测试结果、截图等
3. **及时合并**: 避免long-running分支
4. **合并后清理**: 立即删除feature分支

## 故障排除

### 常见问题

1. **分支无法删除**
   ```bash
   # 如果分支有未合并的更改，使用force删除
   git branch -D branch-name
   ```

2. **Hook 不执行**
   ```bash
   # 检查hook文件权限
   ls -la .git/hooks/
   chmod +x .git/hooks/*
   ```

3. **远程分支删除失败**
   ```bash
   # 检查是否有权限删除远程分支
   git push origin --delete branch-name
   ```

### 调试模式

```bash
# 启用详细输出
GIT_TRACE=1 git push origin branch-name

# 检查hook执行
echo "test" | .git/hooks/commit-msg /tmp/test-msg
```

## 配置选项

### 自定义清理规则

编辑 `scripts/cleanup_merged_branches.py`:
```python
# 修改天数阈值
days_back = 14  # 默认30天

# 修改保护分支列表
protected_branches = {'main', 'master', 'develop', 'custom-branch'}
```

### Hook 配置

编辑相应的hook文件在 `.git/hooks/` 目录中以自定义行为。

## 安全注意事项

1. **备份重要分支**: 删除前确认分支已正确合并
2. **测试先行**: 使用 `--dry-run` 参数测试清理操作
3. **权限控制**: 确保只有授权用户能删除远程分支
4. **监控日志**: 定期检查hook和清理脚本的日志输出

---

*通过这些优化措施，项目的Git工作流程将更加高效、一致和安全。*