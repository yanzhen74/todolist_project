import os
import sqlite3
import pytest
from app import init_db

class TestDatabaseMigration:
    """测试数据库迁移功能"""
    
    def test_init_db_adds_deadline_column(self, monkeypatch):
        """测试init_db函数能正确添加deadline列"""
        test_db_path = "test_migration_add.db"
        
        # 删除可能存在的旧测试数据库
        if os.path.exists(test_db_path):
            os.remove(test_db_path)
        
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
        
        # 模拟全局db_path变量
        monkeypatch.setattr('app.db_path', test_db_path)
        
        # 调用init_db函数
        init_db()
        
        # 检查deadline列是否被添加
        conn = sqlite3.connect(test_db_path)
        cursor = conn.cursor()
        
        # 检查表结构
        cursor.execute("PRAGMA table_info(todos)")
        columns = [row[1] for row in cursor.fetchall()]
        
        # 验证deadline列已添加
        assert 'deadline' in columns, "deadline列没有被添加到数据库表中"
        
        conn.close()
        
        # 清理测试数据库
        if os.path.exists(test_db_path):
            os.remove(test_db_path)
    
    def test_init_db_works_with_existing_deadline_column(self, monkeypatch):
        """测试init_db函数在deadline列已存在时能正常工作"""
        test_db_path = "test_migration_existing.db"
        
        # 删除可能存在的旧测试数据库
        if os.path.exists(test_db_path):
            os.remove(test_db_path)
        
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
        
        # 模拟全局db_path变量
        monkeypatch.setattr('app.db_path', test_db_path)
        
        # 调用init_db函数（应该不会出错）
        init_db()
        
        # 验证表仍然存在且结构正确
        conn = sqlite3.connect(test_db_path)
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA table_info(todos)")
        columns = [row[1] for row in cursor.fetchall()]
        
        assert 'deadline' in columns, "deadline列应该存在"
        assert len(columns) == 4, "表应该有4列"
        
        conn.close()
        
        # 清理测试数据库
        if os.path.exists(test_db_path):
            os.remove(test_db_path)