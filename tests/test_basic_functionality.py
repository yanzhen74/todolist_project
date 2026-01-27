# pylint: disable=locally-disabled,broad-exception-caught,useless-suppression,suppressed-message
"""
Basic functionality tests for the TodoList application.
These tests verify that core components load and function correctly.
"""

import pytest

from app import app
from todolist.config import load_config
from todolist.db import DatabaseConnection, DatabaseInitializer


def test_config_load():
    """Test that configuration loads correctly"""
    # 创建一个新的app实例以避免变量重定义
    from flask import Flask
    test_app = Flask(__name__)
    config, db_path = load_config(test_app, 'test')
    assert config is not None
    assert db_path is not None
    assert config.DEBUG is True
    assert config.HOST == '127.0.0.1'
    assert config.PORT == 5000
    assert db_path == 'todolist_test.db'


def test_database_initialization():
    """Test that database initializes correctly"""
    # 直接使用测试数据库路径，不通过 parse_args
    db_path = 'todolist_test.db'
    db_connection = DatabaseConnection(db_path)
    db_initializer = DatabaseInitializer(db_connection)
    db_initializer.init_db()
    # If we get here without exceptions, the test passes
    assert True


def test_app_import():
    """Test that app can be imported"""
    assert app is not None
    # 检查模板过滤器是否已注册的正确方式
    assert 'fromjson' in app.jinja_env.filters


def test_home_page_loads():
    """Test that home page loads correctly"""
    import os
    import tempfile

    from todolist.db import TodoRepository
    from todolist.routes import RoutesManager

    # 使用临时文件数据库，这样连接关闭后数据会被保存
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        temp_db_path = tmp.name

    try:
        # 初始化数据库连接
        db_connection = DatabaseConnection(temp_db_path)
        db_initializer = DatabaseInitializer(db_connection)
        db_initializer.init_db()

        # 初始化TodoRepository和RoutesManager，这会注册所有路由
        todo_repository = TodoRepository(db_connection)
        RoutesManager(app, todo_repository)

        # 使用Flask测试客户端进行测试
        with app.test_client() as client:
            response = client.get('/')
            # 检查响应状态码
            assert response.status_code == 200, \
                f"Expected status code 200, got {response.status_code}"
            # 检查响应内容是否包含预期文本
            response_data = response.data.decode('utf-8')
            assert 'TodoList' in response_data, "Response should contain 'TodoList'"
            assert 'add-form' in response_data, "Response should contain add-form class"
    finally:
        # 清理临时文件
        if os.path.exists(temp_db_path):
            try:
                os.remove(temp_db_path)
            except OSError as e:
                print(f"Warning: Could not remove temporary database file: {e}")


if __name__ == '__main__':
    # Run tests
    pytest.main(['-v', __file__])