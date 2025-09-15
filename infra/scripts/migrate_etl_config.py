#!/usr/bin/env python3
"""
ETL配置迁移脚本
Issue #278: 从分散的配置文件迁移到集中化的etl_loader

功能：
1. 将旧的三维配置目录迁移到扁平化ETL配置
2. 更新所有代码中的配置读取调用
3. 验证迁移的正确性
4. 可选择回滚到旧配置

使用：
    python scripts/migrate_etl_config.py --migrate    # 执行迁移
    python scripts/migrate_etl_config.py --validate   # 验证迁移
    python scripts/migrate_etl_config.py --rollback   # 回滚迁移
"""

import argparse
import os
import shutil
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import yaml
except ImportError:
    print("❌ PyYAML not available. Please install: pip install pyyaml")
    sys.exit(1)


class ETLConfigMigrator:
    """ETL配置迁移器"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.old_config_dirs = {
            'stock_lists': self.project_root / 'common/config/stock_lists',
            'data_sources': self.project_root / 'common/config/data_sources',
            'scenarios': self.project_root / 'common/config/scenarios'
        }
        self.new_config_dir = self.project_root / 'common/config/etl'
        self.backup_dir = self.project_root / 'common/config/etl_migration_backup'

        # 文件映射关系
        self.file_mappings = {
            # Stock Lists
            'common/config/stock_lists/f2.yml': 'common/config/etl/stock_f2.yml',
            'common/config/stock_lists/m7.yml': 'common/config/etl/stock_m7.yml',
            'common/config/stock_lists/n100.yml': 'common/config/etl/stock_n100.yml',
            'common/config/stock_lists/v3k.yml': 'common/config/etl/stock_v3k.yml',

            # Data Sources
            'common/config/data_sources/yfinance.yml': 'common/config/etl/source_yfinance.yml',
            'common/config/data_sources/sec_edgar.yml': 'common/config/etl/source_sec_edgar.yml',

            # Scenarios
            'common/config/scenarios/development.yml': 'common/config/etl/scenario_dev.yml',
            'common/config/scenarios/production.yml': 'common/config/etl/scenario_prod.yml'
        }

        # 需要更新的代码文件模式
        self.code_update_patterns = [
            {
                'pattern': r'from common\.orthogonal_config import orthogonal_config',
                'replacement': 'from common.etl_loader import etl_loader'
            },
            {
                'pattern': r'orthogonal_config\.load_stock_list\(',
                'replacement': 'etl_loader.load_stock_list('
            },
            {
                'pattern': r'orthogonal_config\.load_data_source\(',
                'replacement': 'etl_loader.load_data_source('
            },
            {
                'pattern': r'orthogonal_config\.load_scenario\(',
                'replacement': 'etl_loader.load_scenario('
            },
            {
                'pattern': r'orthogonal_config\.build_runtime_config\(',
                'replacement': 'etl_loader.build_runtime_config('
            },
            # 直接读取配置文件的模式
            {
                'pattern': r'common/config/stock_lists/(\w+)\.yml',
                'replacement': r'common/config/etl/stock_\1.yml'
            },
            {
                'pattern': r'common/config/data_sources/(\w+)\.yml',
                'replacement': r'common/config/etl/source_\1.yml'
            },
            {
                'pattern': r'common/config/scenarios/(\w+)\.yml',
                'replacement': r'common/config/etl/scenario_\1.yml'
            }
        ]

    def create_backup(self):
        """创建配置文件备份"""
        print("📦 创建配置文件备份...")

        if self.backup_dir.exists():
            shutil.rmtree(self.backup_dir)

        self.backup_dir.mkdir(parents=True)

        # 备份旧配置目录
        for name, old_dir in self.old_config_dirs.items():
            if old_dir.exists():
                backup_subdir = self.backup_dir / name
                shutil.copytree(old_dir, backup_subdir)
                print(f"   ✅ 已备份 {name} -> {backup_subdir}")

        # 备份ETL配置目录（如果存在）
        if self.new_config_dir.exists():
            backup_etl = self.backup_dir / 'etl'
            shutil.copytree(self.new_config_dir, backup_etl)
            print(f"   ✅ 已备份 etl -> {backup_etl}")

        print(f"✅ 配置备份完成: {self.backup_dir}")

    def migrate_config_files(self):
        """迁移配置文件到新的扁平结构"""
        print("🔄 迁移配置文件...")

        self.new_config_dir.mkdir(exist_ok=True)

        for old_path_str, new_path_str in self.file_mappings.items():
            old_path = self.project_root / old_path_str
            new_path = self.project_root / new_path_str

            if old_path.exists():
                shutil.copy2(old_path, new_path)
                print(f"   ✅ {old_path.name} -> {new_path.name}")
            else:
                print(f"   ⚠️  源文件不存在: {old_path}")

        print("✅ 配置文件迁移完成")

    def find_files_to_update(self) -> List[Path]:
        """找到需要更新配置读取的代码文件"""
        files_to_update = []

        # 搜索Python文件
        for py_file in self.project_root.rglob('*.py'):
            # 跳过测试文件和备份目录
            if ('.git' in str(py_file) or
                'test' in str(py_file) or
                'backup' in str(py_file) or
                '__pycache__' in str(py_file)):
                continue

            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # 检查是否包含需要更新的模式
                    if any(pattern in content for pattern in [
                        'orthogonal_config',
                        'stock_lists/',
                        'data_sources/',
                        'scenarios/'
                    ]):
                        files_to_update.append(py_file)
            except Exception:
                continue

        return files_to_update

    def update_code_files(self):
        """更新代码文件中的配置读取"""
        print("🔧 更新代码文件中的配置读取...")

        files_to_update = self.find_files_to_update()
        updated_files = []

        for file_path in files_to_update:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    original_content = f.read()

                updated_content = original_content
                file_changed = False

                # 应用所有更新模式
                import re
                for pattern_info in self.code_update_patterns:
                    pattern = pattern_info['pattern']
                    replacement = pattern_info['replacement']

                    new_content = re.sub(pattern, replacement, updated_content)
                    if new_content != updated_content:
                        updated_content = new_content
                        file_changed = True

                # 如果文件有变化，写入更新
                if file_changed:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(updated_content)

                    updated_files.append(file_path)
                    print(f"   ✅ 已更新: {file_path.relative_to(self.project_root)}")

            except Exception as e:
                print(f"   ❌ 更新失败 {file_path}: {e}")

        print(f"✅ 代码更新完成，共更新 {len(updated_files)} 个文件")
        return updated_files

    def validate_migration(self) -> bool:
        """验证迁移结果"""
        print("🔍 验证迁移结果...")

        errors = []

        # 1. 检查新配置文件是否存在
        for new_path_str in self.file_mappings.values():
            new_path = self.project_root / new_path_str
            if not new_path.exists():
                errors.append(f"新配置文件不存在: {new_path}")

        # 2. 检查新配置文件格式是否正确
        for new_path_str in self.file_mappings.values():
            new_path = self.project_root / new_path_str
            if new_path.exists():
                try:
                    with open(new_path, 'r', encoding='utf-8') as f:
                        yaml.safe_load(f)
                except Exception as e:
                    errors.append(f"配置文件格式错误 {new_path}: {e}")

        # 3. 检查etl_loader是否可以导入
        try:
            from common.etl_loader import etl_loader
            print("   ✅ etl_loader模块导入成功")
        except Exception as e:
            errors.append(f"etl_loader模块导入失败: {e}")

        if errors:
            print("❌ 验证发现问题:")
            for error in errors:
                print(f"   • {error}")
            return False
        else:
            print("✅ 迁移验证通过")
            return True

    def rollback_migration(self):
        """回滚迁移"""
        print("↩️  回滚配置迁移...")

        if not self.backup_dir.exists():
            print("❌ 没有找到备份文件，无法回滚")
            return False

        # 恢复旧配置目录
        for name, old_dir in self.old_config_dirs.items():
            backup_subdir = self.backup_dir / name
            if backup_subdir.exists():
                if old_dir.exists():
                    shutil.rmtree(old_dir)
                shutil.copytree(backup_subdir, old_dir)
                print(f"   ✅ 已恢复 {name}")

        # 删除新的ETL配置目录
        if self.new_config_dir.exists():
            shutil.rmtree(self.new_config_dir)
            print("   ✅ 已删除新的ETL配置目录")

        print("✅ 回滚完成")
        return True

    def run_migration(self):
        """执行完整迁移流程"""
        print("🚀 开始ETL配置迁移...")

        # 1. 创建备份
        self.create_backup()

        # 2. 迁移配置文件
        self.migrate_config_files()

        # 3. 更新代码文件
        updated_files = self.update_code_files()

        # 4. 验证迁移
        is_valid = self.validate_migration()

        if is_valid:
            print("🎉 ETL配置迁移完成！")
            print("\n📋 迁移总结:")
            print(f"   • 配置文件: {len(self.file_mappings)} 个")
            print(f"   • 代码文件: {len(updated_files)} 个")
            print(f"   • 备份位置: {self.backup_dir}")
            print("\n📌 下一步:")
            print("   1. 运行测试确保功能正常")
            print("   2. 如有问题可使用 --rollback 回滚")
            print("   3. 确认无误后可删除旧配置目录和备份")
        else:
            print("❌ 迁移验证失败，请检查错误信息")
            return False

        return True


def main():
    parser = argparse.ArgumentParser(description='ETL配置迁移脚本')
    parser.add_argument('--migrate', action='store_true', help='执行配置迁移')
    parser.add_argument('--validate', action='store_true', help='验证迁移结果')
    parser.add_argument('--rollback', action='store_true', help='回滚迁移')
    parser.add_argument('--dry-run', action='store_true', help='预览迁移操作')

    args = parser.parse_args()

    if not any([args.migrate, args.validate, args.rollback, args.dry_run]):
        print("请指定操作: --migrate, --validate, --rollback, 或 --dry-run")
        parser.print_help()
        return

    migrator = ETLConfigMigrator()

    try:
        if args.dry_run:
            print("🔍 预览迁移操作...")
            files_to_update = migrator.find_files_to_update()
            print(f"将要更新的文件 ({len(files_to_update)}):")
            for file_path in files_to_update:
                print(f"   • {file_path.relative_to(migrator.project_root)}")

        elif args.migrate:
            success = migrator.run_migration()
            sys.exit(0 if success else 1)

        elif args.validate:
            success = migrator.validate_migration()
            sys.exit(0 if success else 1)

        elif args.rollback:
            success = migrator.rollback_migration()
            sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print("\n⏹️  操作被用户取消")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 迁移失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()