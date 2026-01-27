# pylint: disable=locally-disabled,broad-exception-caught,useless-suppression,suppressed-message
"""
Database migration tests for the TodoList application.
These tests verify that database schema updates work correctly.
"""

import os
import sqlite3
import tempfile

from todolist.db import DatabaseConnection, DatabaseInitializer


class TestDatabaseMigration:
    """测试数据库迁移功能"""

    def test_init_db_adds_deadline_column(self):
        """测试init_db函数能正确添加deadline列"""
        # 使用临时文件来避免文件锁定问题
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            test_db_path = tmp.name

        try:
            # 创建只有id、title和completed列的表
            conn = sqlite3.connect(test_db_path)
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE todos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    completed INTEGER DEFAULT 0
                )
            ''')
            conn.commit()
            conn.close()

            # 使用DatabaseInitializer初始化数据库
            db_connection = DatabaseConnection(test_db_path)
            db_initializer = DatabaseInitializer(db_connection)
            db_initializer.init_db()
            # DatabaseInitializer已经在内部使用with语句关闭了连接

            # 检查deadline列是否被添加
            conn = sqlite3.connect(test_db_path)
            cursor = conn.cursor()

            # 检查表结构
            cursor.execute("PRAGMA table_info(todos)")
            columns = [row[1] for row in cursor.fetchall()]

            # 验证deadline列已添加
            assert 'deadline' in columns, "deadline列没有被添加到数据库表中"

            conn.close()
        finally:
            # 清理测试数据库
            if os.path.exists(test_db_path):
                try:
                    os.remove(test_db_path)
                except OSError as e:
                    # 如果删除失败，记录日志但不影响测试结果
                    print(f"警告：无法删除测试数据库文件 {test_db_path}: {e}")

    def test_init_db_works_with_existing_deadline_column(self):
        """测试init_db函数在deadline列已存在时能正常工作"""
        # 使用临时文件来避免文件锁定问题
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            test_db_path = tmp.name

        try:
            # 创建包含deadline列的完整表
            conn = sqlite3.connect(test_db_path)
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE todos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    completed INTEGER DEFAULT 0,
                    deadline DATETIME DEFAULT (DATETIME('now', '+24 hours'))
                )
            ''')
            conn.commit()
            conn.close()

            # 使用DatabaseInitializer初始化数据库
            db_connection = DatabaseConnection(test_db_path)
            db_initializer = DatabaseInitializer(db_connection)
            db_initializer.init_db()
            # DatabaseInitializer已经在内部使用with语句关闭了连接

            # 验证表仍然存在且结构正确
            conn = sqlite3.connect(test_db_path)
            cursor = conn.cursor()

            cursor.execute("PRAGMA table_info(todos)")
            columns = [row[1] for row in cursor.fetchall()]

            # 只检查我们关心的列是否存在，不检查列的总数，因为数据库结构可能会变化
            assert 'deadline' in columns, "deadline列应该存在"
            assert 'id' in columns, "id列应该存在"
            assert 'title' in columns, "title列应该存在"
            assert 'completed' in columns, "completed列应该存在"

            conn.close()
        finally:
            # 清理测试数据库
            if os.path.exists(test_db_path):
                try:
                    os.remove(test_db_path)
                except OSError as e:
                    # 如果删除失败，记录日志但不影响测试结果
                    print(f"警告：无法删除测试数据库文件 {test_db_path}: {e}")