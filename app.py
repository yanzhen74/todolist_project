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

# 注册fromjson过滤器
import json
@app.template_filter('fromjson')
def fromjson_filter(value):
    if value:
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return []
    return []

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
                    deadline DATETIME DEFAULT (DATETIME('now', '+24 hours')),
                    is_recurring BOOLEAN DEFAULT 0,
                    recurrence_type TEXT DEFAULT NULL,
                    recurrence_interval INTEGER DEFAULT 1,
                    recurrence_days TEXT DEFAULT NULL,
                    next_occurrence DATETIME DEFAULT NULL
                )
            ''')
            
            # 检查并添加缺失的列
            cursor.execute("PRAGMA table_info(todos)")
            columns = [row[1] for row in cursor.fetchall()]
            
            # 如果 deadline 列不存在，添加它
            if 'deadline' not in columns:
                cursor.execute('''
                    ALTER TABLE todos ADD COLUMN deadline DATETIME DEFAULT (DATETIME('now', '+24 hours'))
                ''')
            
            # 添加周期相关列
            if 'is_recurring' not in columns:
                cursor.execute('''
                    ALTER TABLE todos ADD COLUMN is_recurring BOOLEAN DEFAULT 0
                ''')
            
            if 'recurrence_type' not in columns:
                cursor.execute('''
                    ALTER TABLE todos ADD COLUMN recurrence_type TEXT DEFAULT NULL
                ''')
            
            if 'recurrence_interval' not in columns:
                cursor.execute('''
                    ALTER TABLE todos ADD COLUMN recurrence_interval INTEGER DEFAULT 1
                ''')
            
            if 'recurrence_days' not in columns:
                cursor.execute('''
                    ALTER TABLE todos ADD COLUMN recurrence_days TEXT DEFAULT NULL
                ''')
            
            if 'next_occurrence' not in columns:
                cursor.execute('''
                    ALTER TABLE todos ADD COLUMN next_occurrence DATETIME DEFAULT NULL
                ''')
            
            conn.commit()
    except Exception as e:
        app.logger.error(f"Error initializing database: {e}")

# 计算下一次出现时间
def calculate_next_occurrence(deadline, recurrence_type, recurrence_interval, recurrence_days):
    """
    根据周期类型计算下一次出现时间
    
    Args:
        deadline: 当前截止时间
        recurrence_type: 周期类型 (yearly, monthly, daily, hourly, minutely, weekly)
        recurrence_interval: 周期间隔
        recurrence_days: 每周特定天数，JSON格式字符串
        
    Returns:
        下一次出现时间（ISO格式字符串）
    """
    import json
    from datetime import datetime, timedelta
    
    try:
        # 解析截止时间，处理多种格式
        try:
            # 尝试解析 YYYY-MM-DD HH:MM:SS 格式
            current_time = datetime.strptime(deadline, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            try:
                # 尝试解析 YYYY-MM-DDTHH:MM 格式（datetime-local输入格式）
                current_time = datetime.strptime(deadline, "%Y-%m-%dT%H:%M")
            except ValueError:
                # 尝试解析 YYYY-MM-DDTHH:MM:SS 格式
                current_time = datetime.strptime(deadline, "%Y-%m-%dT%H:%M:%S")
        
        next_time = current_time
        
        # 根据周期类型计算下一次时间
        if recurrence_type == 'yearly':
            next_time = current_time.replace(year=current_time.year + recurrence_interval)
        elif recurrence_type == 'monthly':
            # 处理月份边界情况
            next_month = current_time.month + recurrence_interval
            year_increment = next_month // 12
            month = next_month % 12 if next_month % 12 != 0 else 12
            year = current_time.year + year_increment
            
            # 处理月末情况
            try:
                next_time = current_time.replace(year=year, month=month)
            except ValueError:
                # 日期无效（如31日在小月），调整到月末
                if month == 2:
                    # 处理2月特殊情况
                    is_leap = (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)
                    day = 29 if is_leap else 28
                    next_time = current_time.replace(year=year, month=month, day=day)
                else:
                    # 其他小月，调整到月末
                    days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
                    # 计算实际的月份索引（1月为0）
                    month_idx = month - 1
                    day = days_in_month[month_idx]
                    next_time = current_time.replace(year=year, month=month, day=day)
        elif recurrence_type == 'daily':
            next_time = current_time + timedelta(days=recurrence_interval)
        elif recurrence_type == 'hourly':
            next_time = current_time + timedelta(hours=recurrence_interval)
        elif recurrence_type == 'minutely':
            next_time = current_time + timedelta(minutes=recurrence_interval)
        elif recurrence_type == 'weekly':
            try:
                # 解析每周特定天数
                if recurrence_days:
                    days_of_week = json.loads(recurrence_days)
                    if days_of_week:
                        # 获取当前是周几（0-6，周一为0，周日为6）
                        current_weekday = current_time.weekday()
                        
                        # 找到下一个匹配的星期几
                        found = False
                        for day in days_of_week:
                            if day > current_weekday:
                                # 本周内找到
                                next_time = current_time + timedelta(days=(day - current_weekday))
                                found = True
                                break
                        
                        if not found:
                            # 本周内没有找到，找下周第一个匹配的
                            next_time = current_time + timedelta(days=(7 - current_weekday + days_of_week[0]))
                    else:
                        # 默认每周
                        next_time = current_time + timedelta(weeks=recurrence_interval)
            except (json.JSONDecodeError, Exception) as e:
                app.logger.error(f"Error parsing recurrence_days: {e}")
                next_time = current_time + timedelta(weeks=recurrence_interval)
        else:
            # 默认每周
            next_time = current_time + timedelta(weeks=recurrence_interval)
        
        # 格式化返回
        return next_time.strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        app.logger.error(f"Error calculating next occurrence: {e}")
        return None

# 首页路由
@app.route('/')
def index():
    try:
        # 使用try-except来捕获具体的数据库错误
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, title, completed, deadline, is_recurring, recurrence_type, recurrence_interval, recurrence_days, next_occurrence FROM todos')
        rows = cursor.fetchall()
        
        # 转换为元组列表，因为模板使用索引访问
        todos = []
        for row in rows:
            todos.append((
                row[0],  # id
                row[1],  # title
                row[2],  # completed
                row[3],  # deadline
                row[4],  # is_recurring
                row[5],  # recurrence_type
                row[6],  # recurrence_interval
                row[7],  # recurrence_days
                row[8]   # next_occurrence
            ))
        conn.close()
        return render_template('index.html', todos=todos)
    except Exception as e:
        # 打印详细错误信息
        print(f"Index route error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return "An error occurred while loading todos", 500

@app.route('/add', methods=['POST'])
def add_todo():
    try:
        title = request.form['title']
        deadline = request.form.get('deadline')
        
        # 获取周期相关参数
        is_recurring = request.form.get('is_recurring') == 'on'
        recurrence_type = request.form.get('recurrence_type')
        recurrence_interval = int(request.form.get('recurrence_interval', 1))
        recurrence_days = request.form.get('recurrence_days')
        
        # 计算下一次出现时间
        next_occurrence = None
        if is_recurring and deadline:
            next_occurrence = calculate_next_occurrence(deadline, recurrence_type, recurrence_interval, recurrence_days)
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            if deadline:
                cursor.execute('''
                    INSERT INTO todos (title, deadline, is_recurring, recurrence_type, recurrence_interval, recurrence_days, next_occurrence)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (title, deadline, is_recurring, recurrence_type, recurrence_interval, recurrence_days, next_occurrence))
            else:
                cursor.execute('''
                    INSERT INTO todos (title, is_recurring, recurrence_type, recurrence_interval, recurrence_days, next_occurrence)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (title, is_recurring, recurrence_type, recurrence_interval, recurrence_days, next_occurrence))
            conn.commit()
        return redirect(url_for('index'))
    except Exception as e:
        app.logger.error(f"Error adding todo: {e}")
        return "An error occurred while adding todo", 500

@app.route('/delete/<int:todo_id>', methods=['POST'])
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

@app.route('/toggle/<int:todo_id>', methods=['POST'])
def toggle_todo(todo_id):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            # 获取todo的完整信息，包括周期相关字段
            cursor.execute('SELECT * FROM todos WHERE id = ?', (todo_id,))
            result = cursor.fetchone()
            
            if result:
                # 转换为字典以便访问
                todo = dict(result)
                completed = todo['completed']
                
                # 检查是否为周期todo
                is_recurring = todo['is_recurring']
                
                if is_recurring:
                    # 周期todo：不真正标记为完成，而是更新为下一次出现
                    current_deadline = todo['deadline']
                    recurrence_type = todo['recurrence_type']
                    recurrence_interval = todo['recurrence_interval']
                    recurrence_days = todo['recurrence_days']
                    
                    # 计算下一次出现时间
                    next_occurrence = calculate_next_occurrence(current_deadline, recurrence_type, recurrence_interval, recurrence_days)
                    
                    if next_occurrence:
                        # 更新todo为下一次出现
                        cursor.execute('''
                            UPDATE todos 
                            SET deadline = ?, next_occurrence = ?, completed = 0
                            WHERE id = ?
                        ''', (next_occurrence, next_occurrence, todo_id))
                else:
                    # 普通todo：正常切换完成状态
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
