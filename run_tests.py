#!/usr/bin/env python3
"""
TodoList测试运行脚本

Usage:
    python run_tests.py [--marker MARKER] [--test TEST_NAME]
    python run_tests.py --help

Options:
    --marker MARKER   Run tests with specific marker (e2e, smoke, regression, test_env)
    --test TEST_NAME  Run specific test function or class
    --help            Show this help message
"""

import os
import sys
import subprocess
import argparse

# 测试数据库文件
TEST_DB_FILE = 'todolist_test.db'

# 清理测试环境
def clean_test_env():
    """清理测试环境"""
    print("\n=== 清理测试环境 ===")

    # 删除测试数据库文件
    if os.path.exists(TEST_DB_FILE):
        try:
            os.remove(TEST_DB_FILE)
            print(f"✓ 删除测试数据库文件: {TEST_DB_FILE}")
        except Exception as e:
            print(f"✗ 删除测试数据库文件失败: {e}")
    else:
        print(f"✓ 测试数据库文件不存在: {TEST_DB_FILE}")

# 运行测试
def run_tests(marker=None, test_name=None):
    """运行测试"""
    print("\n=== 运行测试 ===")

    # 构建测试命令
    cmd = [sys.executable, '-m', 'pytest']

    if marker:
        cmd.extend(['-m', marker])
        print(f"测试标记: {marker}")

    if test_name:
        cmd.append(test_name)
        print(f"测试名称: {test_name}")

    # 添加测试目录
    cmd.append('tests/')

    print(f"测试命令: {' '.join(cmd)}")

    # 运行测试
    result = subprocess.run(cmd, check=False)

    return result.returncode

# 主函数
def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='TodoList测试运行脚本')
    parser.add_argument('--marker',
                       choices=['e2e', 'smoke', 'regression', 'test_env'],
                       help='Run tests with specific marker')
    parser.add_argument('--test', help='Run specific test function or class')

    args = parser.parse_args()

    # 清理测试环境
    clean_test_env()

    # 运行测试
    returncode = run_tests(args.marker, args.test)

    # 再次清理测试环境
    clean_test_env()

    # 输出结果
    print("\n=== 测试结果 ===")
    if returncode == 0:
        print("🎉 所有测试通过!")
    else:
        print(f"❌ 测试失败，返回码: {returncode}")

    return returncode

if __name__ == '__main__':
    sys.exit(main())