# Worktree Python Environment Isolation

## 🎯 设计目标

完全基于repo内部、使用pixi/Python管理的worktree级别Python环境完全隔离方案。

### 核心特性
- ✅ **零配置**：进入worktree自动激活隔离环境
- ✅ **完全隔离**：每个worktree的Python环境完全独立  
- ✅ **pixi为核心**：所有环境管理都通过pixi
- ✅ **工作流简单**：`python p3.py <command>` 自动工作
- ✅ **全局工具复用**：ansible/docker等通过pixi task复用
- ✅ **完全repo内部**：无外部文件依赖

## 🚀 使用方法

### 基本工作流（零配置）
```bash
# 1. 进入worktree目录
cd /path/to/worktree

# 2. 直接使用 - 自动环境隔离
python p3.py version-info          # 自动切换到worktree Python
python p3.py build f2              # 使用隔离环境构建
python p3.py e2e                   # 使用隔离环境测试
```

### pixi命令（推荐）
```bash
# 环境管理
pixi run worktree-status            # 查看环境状态
pixi run worktree-verify            # 验证环境和包
pixi run worktree-init              # 初始化环境（如需要）

# 全局基础设施复用
pixi run global-setup               # 设置全局工具配置
pixi run docker-status              # 查看Docker状态
pixi run ansible-setup              # 运行ansible设置
```

## 🏗️ 架构设计

### 环境隔离层级
```
Repository Root/
├── .pixi/                          # 主仓库pixi环境
├── infra/                          # 全局基础设施(ansible/docker)
│   ├── ansible/                    # 全局复用
│   └── docker/                     # 全局复用  
├── scripts/                        # 全局脚本
│   └── worktree_isolation.py       # 核心隔离管理器
└── worktrees/
    └── feature-branch/
        ├── .pixi/                  # 隔离的Python环境
        ├── .worktree_config.json   # 全局工具配置
        ├── p3.py                   # 自动环境切换集成
        └── scripts/ -> ../scripts  # 复用脚本
```

### 自动环境切换机制
1. **p3.py启动时检测**：自动检测当前是否在worktree
2. **Python环境验证**：检查是否使用worktree隔离的Python
3. **自动切换**：如果环境不匹配，自动切换到正确Python
4. **透明执行**：用户无感知，命令正常执行

## 📋 验证环境隔离

### 验证命令
```bash
# 完整验证
pixi run worktree-verify

# 手动验证
python scripts/worktree_isolation.py status
python scripts/worktree_isolation.py verify
```

### 期望输出
```
🔍 Worktree Environment Status
========================================
Repository: my_finance
Worktree: feature-branch
Is Worktree: True
Python: 3.12.11 at /path/to/.pixi/envs/default/bin/python
✅ Python environment isolated

🔍 Package Availability Check
------------------------------
✅ Available: pandas, numpy, requests, neo4j, yfinance
🎉 All core packages available!
```

## 🔧 故障排除

### 常见问题

**Q: Python环境没有隔离？**
```bash
# 确保pixi环境已安装
pixi install

# 重新初始化
pixi run worktree-init

# 手动验证
python scripts/worktree_isolation.py status
```

**Q: 包导入失败？**
```bash
# 检查pixi环境
pixi run check-env

# 重新安装依赖
pixi install

# 验证包可用性
pixi run worktree-verify
```

**Q: 全局工具配置问题？**
```bash
# 重新设置全局配置
pixi run global-setup

# 检查配置文件
cat .worktree_config.json
```

## 💡 最佳实践

### 开发工作流
1. **进入worktree**: `cd /path/to/worktree`
2. **验证环境**: `pixi run worktree-verify`
3. **正常开发**: `python p3.py <commands>`
4. **测试**: `python p3.py e2e`
5. **提交**: `python p3.py create-pr`

### 环境管理
- **定期验证**: 使用 `pixi run worktree-verify` 检查环境
- **包管理**: 通过 `pixi.toml` 统一管理依赖
- **全局工具**: 通过 `pixi run` 使用ansible/docker命令

### 性能优化
- **pixi缓存**: pixi自动缓存依赖，跨worktree共享
- **基础设施复用**: ansible/docker配置全局共享
- **脚本复用**: 通过符号链接复用scripts目录

## 🎉 优势总结

- **完全隔离**: 不同worktree的Python环境零污染
- **零配置**: 无需记住复杂命令，自动激活
- **高性能**: pixi缓存机制，基础设施复用
- **易维护**: 完全在git repo内管理，版本控制
- **兼容性**: 与现有p3工作流完全兼容