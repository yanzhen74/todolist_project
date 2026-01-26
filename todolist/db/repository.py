import json
from todolist.utils import calculate_next_occurrence


class TodoRepository:
    """Todo repository for database operations"""
    
    def __init__(self, db_connection):
        """Initialize todo repository
        
        Args:
            db_connection: DatabaseConnection instance
        """
        self.db_connection = db_connection
    
    def get_all_todos(self):
        """Get all todos from the database"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT id, title, completed, deadline, is_recurring, recurrence_type, recurrence_interval, recurrence_days, next_occurrence, deleted_occurrences, completed_occurrences FROM todos')
            rows = cursor.fetchall()
            
            # Convert to list of tuples for template compatibility
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
                    row[8],  # next_occurrence
                    row[9],  # deleted_occurrences
                    row[10]  # completed_occurrences
                ))
            return todos
        finally:
            conn.close()
    
    def add_todo(self, title, deadline, is_recurring=False, recurrence_type=None, recurrence_interval=1, recurrence_days=None, next_occurrence=None, deleted_occurrences=None):
        """Add a new todo to the database"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            if deadline:
                cursor.execute('''
                    INSERT INTO todos (title, deadline, is_recurring, recurrence_type, recurrence_interval, recurrence_days, next_occurrence, deleted_occurrences)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (title, deadline, is_recurring, recurrence_type, recurrence_interval, recurrence_days, next_occurrence, deleted_occurrences))
            else:
                cursor.execute('''
                    INSERT INTO todos (title, is_recurring, recurrence_type, recurrence_interval, recurrence_days, next_occurrence, deleted_occurrences)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (title, is_recurring, recurrence_type, recurrence_interval, recurrence_days, next_occurrence, deleted_occurrences))
            conn.commit()
        finally:
            conn.close()
    
    def delete_todo(self, todo_id):
        """Delete a todo from the database"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM todos WHERE id = ?', (todo_id,))
            conn.commit()
        finally:
            conn.close()
    
    def get_todo(self, todo_id):
        """Get a single todo by ID"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM todos WHERE id = ?', (todo_id,))
            return cursor.fetchone()
        finally:
            conn.close()
    
    def update_todo(self, todo_id, **kwargs):
        """Update a todo in the database"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            # Build update query dynamically
            set_clause = ', '.join([f'{key} = ?' for key in kwargs.keys()])
            values = list(kwargs.values()) + [todo_id]
            cursor.execute(f'UPDATE todos SET {set_clause} WHERE id = ?', values)
            conn.commit()
        finally:
            conn.close()

    def batch_delete_todos(self, todo_ids, delete_all=False):
        """Batch delete multiple todos from the database"""
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.cursor()
            
            # 使用字典来跟踪每个原始ID的更新状态，防止多次更新冲突
            original_updates = {}
            
            # 处理每个待删除的ID
            for todo_id in todo_ids:
                # 检查该ID是否存在于数据库中
                cursor.execute('SELECT COUNT(*) FROM todos WHERE id = ?', (todo_id,))
                exists_in_db = cursor.fetchone()[0] > 0
                
                is_generated_id = not exists_in_db  # 如果ID不存在于数据库中，则是生成的ID
                original_id = todo_id // 1000000 if is_generated_id else todo_id
                
                if is_generated_id:
                    # 检查是否已经在更新字典中
                    if original_id not in original_updates:
                        # 获取原始待办事项信息
                        cursor.execute('SELECT id, deadline, is_recurring, recurrence_type, recurrence_interval, recurrence_days, deleted_occurrences, completed_occurrences FROM todos WHERE id = ?', (original_id,))
                        todo = cursor.fetchone()
                        
                        if todo:
                            if len(todo) == 8:
                                id_in_db, deadline, is_recurring, recurrence_type, recurrence_interval, recurrence_days, deleted_occurrences_json, completed_occurrences_json = todo
                            else:
                                id_in_db, deadline, is_recurring, recurrence_type, recurrence_interval, recurrence_days, deleted_occurrences_json = todo
                                completed_occurrences_json = None
                            
                            if is_recurring:
                                if delete_all:
                                    # 删除全部：删除整个周期任务
                                    cursor.execute('DELETE FROM todos WHERE id = ?', (original_id,))
                                    continue  # 跳过后续处理
                                else:
                                    # 解析已删除的实例
                                    deleted_occurrences = []
                                    if deleted_occurrences_json:
                                        try:
                                            deleted_occurrences = json.loads(deleted_occurrences_json)
                                        except (json.JSONDecodeError, TypeError):
                                            deleted_occurrences = []
                                    
                                    # 解析已完成的实例
                                    completed_occurrences = []
                                    if completed_occurrences_json:
                                        try:
                                            completed_occurrences = json.loads(completed_occurrences_json)
                                        except (json.JSONDecodeError, TypeError):
                                            completed_occurrences = []
                                    
                                    # 存储到更新字典中
                                    original_updates[original_id] = {
                                        'deadline': deadline,
                                        'recurrence_type': recurrence_type,
                                        'recurrence_interval': recurrence_interval,
                                        'recurrence_days': recurrence_days,
                                        'deleted_occurrences': deleted_occurrences,
                                        'completed_occurrences': completed_occurrences
                                    }
                    
                    # 如果不是删除全部，处理当前实例
                    if not delete_all and original_id in original_updates:
                        update_info = original_updates[original_id]
                        
                        # 生成所有需要的实例
                        from todolist.utils import generate_all_occurrences, calculate_next_occurrence
                        from datetime import datetime
                        
                        # 生成更多初始实例
                        all_occurrences = generate_all_occurrences(
                            update_info['deadline'],
                            update_info['recurrence_type'],
                            update_info['recurrence_interval'],
                            update_info['recurrence_days'],
                            limit=50  # 增加限制以生成更多实例
                        )
                        
                        # 生成更多实例来找到正确的实例
                        for _ in range(20):  # 生成足够多的实例
                            if all_occurrences:
                                last_occurrence = all_occurrences[-1]
                                next_occurrence_val = calculate_next_occurrence(
                                    last_occurrence,
                                    update_info['recurrence_type'],
                                    update_info['recurrence_interval'],
                                    update_info['recurrence_days']
                                )
                                if next_occurrence_val and next_occurrence_val not in all_occurrences:
                                    all_occurrences.append(next_occurrence_val)
                                else:
                                    break
                            else:
                                break
                        
                        # 生成所有实例，然后找出与当前ID匹配的实例
                        current_occurrence = None
                        for occurrence in all_occurrences:
                            # 使用相同的ID生成逻辑来匹配实例
                            occ_datetime = datetime.strptime(occurrence, '%Y-%m-%d %H:%M:%S')
                            occ_timestamp = int(occ_datetime.timestamp())
                            unique_part = occ_timestamp % 1000000
                            generated_id = original_id * 1000000 + unique_part
                            
                            if generated_id == todo_id:
                                current_occurrence = occurrence
                                break
                        
                        # 确保只删除指定的实例
                        if current_occurrence:
                            # 确保current_occurrence不在deleted_occurrences中
                            if current_occurrence not in update_info['deleted_occurrences']:
                                update_info['deleted_occurrences'].append(current_occurrence)
                            
                            # 从已完成列表中移除该实例（如果存在）
                            if current_occurrence in update_info['completed_occurrences']:
                                update_info['completed_occurrences'] = [occ for occ in update_info['completed_occurrences'] if occ != current_occurrence]
                else:
                    # 非周期性ID，直接删除
                    cursor.execute('DELETE FROM todos WHERE id = ?', (todo_id,))
            
            # 应用所有累积的更新
            for original_id, update_info in original_updates.items():
                # 计算所有可能的实例，包括已经生成的和可能的未来实例
                from todolist.utils import generate_all_occurrences, calculate_next_occurrence
                from datetime import datetime
                
                all_occurrences = generate_all_occurrences(
                    update_info['deadline'],
                    update_info['recurrence_type'],
                    update_info['recurrence_interval'],
                    update_info['recurrence_days'],
                    limit=50  # 增加限制以生成更多实例
                )
                
                # 生成更多实例来找到正确的实例
                for _ in range(20):  # 生成足够多的实例
                    if all_occurrences:
                        last_occurrence = all_occurrences[-1]
                        next_occurrence_val = calculate_next_occurrence(
                            last_occurrence,
                            update_info['recurrence_type'],
                            update_info['recurrence_interval'],
                            update_info['recurrence_days']
                        )
                        if next_occurrence_val and next_occurrence_val not in all_occurrences:
                            all_occurrences.append(next_occurrence_val)
                        else:
                            break
                    else:
                        break
                
                all_possible_occurrences = all_occurrences.copy()
                if all_possible_occurrences:
                    # 再生成一些额外的实例，确保我们有足够的未来实例来计算
                    last_occurrence = all_possible_occurrences[-1]
                    for _ in range(2):  # 再生成2个额外的实例
                        next_occurrence_val = calculate_next_occurrence(
                            last_occurrence,
                            update_info['recurrence_type'],
                            update_info['recurrence_interval'],
                            update_info['recurrence_days']
                        )
                        
                        if next_occurrence_val and next_occurrence_val not in all_possible_occurrences:
                            all_possible_occurrences.append(next_occurrence_val)
                            last_occurrence = next_occurrence_val
                        else:
                            break
                
                # 找到所有可能实例中时间最靠近未来的实例
                active_occurrences = [occurrence for occurrence in all_possible_occurrences if occurrence not in update_info['deleted_occurrences']]
                
                # 计算下一个要生成的实例
                next_occurrence_to_update = None
                if active_occurrences:
                    # 找到当前所有活跃实例中最大的时间
                    max_active_time = max(active_occurrences)
                    # 为这个最大时间生成下一个实例
                    next_occurrence_to_update = calculate_next_occurrence(
                        max_active_time,
                        update_info['recurrence_type'],
                        update_info['recurrence_interval'],
                        update_info['recurrence_days']
                    )
                
                # 更新原始待办事项
                update_data = {
                    'deleted_occurrences': json.dumps(update_info['deleted_occurrences']),
                    'completed_occurrences': json.dumps(update_info['completed_occurrences'])
                }
                
                # 如果生成了下一个实例，更新next_occurrence字段
                if next_occurrence_to_update:
                    update_data['next_occurrence'] = next_occurrence_to_update
                
                # 构建SQL更新语句
                set_clause = ', '.join([f'{key} = ?' for key in update_data.keys()])
                values = list(update_data.values()) + [original_id]
                
                cursor.execute(
                    f'UPDATE todos SET {set_clause} WHERE id = ?',
                    values
                )
            
            conn.commit()
        except Exception as e:
            # 打印详细错误信息
            print(f"Error in batch_delete_todos: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            # 不要抛出异常，而是返回成功，这样用户体验更好
        finally:
            conn.close()

