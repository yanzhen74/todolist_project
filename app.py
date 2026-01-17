import os
import sys
import argparse
import sqlite3
from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for

# 创建Flask应用实例
app = Flask(__name__)

# 全局配置变量
db_path = None
config = None

# 解析命令行参数
def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='TodoList Application')
    parser.add_argument('-e', '--env', 
                      choices=['local', 'stage', 'live', 'test'], 
                      default='local',
                      help='Environment to run the application in (default: local)')
    return parser.parse_args()

# 加载配置
def load_config(env):
    """Load configuration based on environment"""
    global config, db_path
    
    try:
        # 动态导入配置模块
        config_module = f'config.{env}.config'
        __import__(config_module)
        config = sys.modules[config_module].Config
        
        # 设置全局配置变量
        db_path = config.DATABASE_PATH
        app.config.from_object(config)
        
        # 设置Flask配置
        app.config['SECRET_KEY'] = config.SECRET_KEY
        
        print(f"Loaded {env} environment configuration:")
        print(f"  DEBUG: {config.DEBUG}")
        print(f"  HOST: {config.HOST}")
        print(f"  PORT: {config.PORT}")
        print(f"  DATABASE_PATH: {config.DATABASE_PATH}")
        
    except Exception as e:
        print(f"Error loading {env} configuration: {e}")
        sys.exit(1)

# 获取数据库连接
def get_db_connection():
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

# 初始化数据库
def init_db():
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # 创建表（如果不存在）
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS todos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    completed INTEGER DEFAULT 0,
                    deadline DATETIME DEFAULT (DATETIME('now', '+24 hours'))
                )
            ''')
            
            # 检查 deadline 列是否存在
            cursor.execute("PRAGMA table_info(todos)")
            columns = [row[1] for row in cursor.fetchall()]
            
            # 如果 deadline 列不存在，添加它
            if 'deadline' not in columns:
                cursor.execute('''
                    ALTER TABLE todos ADD COLUMN deadline DATETIME DEFAULT (DATETIME('now', '+24 hours'))
                ''')
            
            conn.commit()
    except Exception as e:
        app.logger.error(f"Error initializing database: {e}")

# 首页路由
@app.route('/')
def index():
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, title, completed, deadline FROM todos')
            todos = cursor.fetchall()
        return render_template('index.html', todos=todos)
    except Exception as e:
        app.logger.error(f"Error in index route: {e}")
        return "An error occurred while loading todos", 500

@app.route('/add', methods=['POST'])
def add_todo():
    try:
        title = request.form['title']
        deadline = request.form.get('deadline')
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            if deadline:
                cursor.execute('INSERT INTO todos (title, deadline) VALUES (?, ?)', (title, deadline))
            else:
                cursor.execute('INSERT INTO todos (title) VALUES (?)', (title,))
            conn.commit()
        return redirect(url_for('index'))
    except Exception as e:
        app.logger.error(f"Error adding todo: {e}")
        return "An error occurred while adding todo", 500

@app.route('/delete/<int:todo_id>')
def delete_todo(todo_id):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM todos WHERE id = ?', (todo_id,))
            conn.commit()
        return redirect(url_for('index'))
    except Exception as e:
        app.logger.error(f"Error deleting todo: {e}")
        return "An error occurred while deleting todo", 500

@app.route('/toggle/<int:todo_id>')
def toggle_todo(todo_id):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT completed FROM todos WHERE id = ?', (todo_id,))
            result = cursor.fetchone()
            if result:
                completed = result['completed']
                new_completed = 1 - completed
                cursor.execute('UPDATE todos SET completed = ? WHERE id = ?', (new_completed, todo_id))
                conn.commit()
        return redirect(url_for('index'))
    except Exception as e:
        app.logger.error(f"Error toggling todo: {e}")
        return "An error occurred while updating todo", 500

# 主入口
def main():
    """Main entry point"""
    # 解析命令行参数
    args = parse_args()
    
    # 加载配置
    load_config(args.env)
    
    # 初始化数据库
    init_db()
    
    # 启动应用
    app.run(
        debug=config.DEBUG,
        host=config.HOST,
        port=config.PORT
    )

if __name__ == '__main__':
    main()
