from flask import render_template, request, redirect, url_for
from datetime import datetime, timedelta
import json
from todolist.db import TodoRepository
from todolist.utils import calculate_next_occurrence, generate_all_occurrences


class RoutesManager:
    """Routes manager for TodoList application"""

    def __init__(self, app, todo_repository):
        """Initialize routes manager

        Args:
            app: Flask application instance
            todo_repository: TodoRepository instance
        """
        self.app = app
        self.todo_repository = todo_repository
        self.register_routes()

    def register_routes(self):
        """Register all routes with the Flask application"""
        self.app.add_url_rule('/', view_func=self.index, methods=['GET'])
        self.app.add_url_rule('/add', view_func=self.add_todo, methods=['POST'])
        self.app.add_url_rule('/delete/<int:todo_id>', view_func=self.delete_todo, methods=['POST'])
        self.app.add_url_rule('/toggle/<int:todo_id>', view_func=self.toggle_todo, methods=['POST'])
        self.app.add_url_rule('/batch-delete', view_func=self.batch_delete, methods=['POST'])

    def index(self):
        """Home page route"""
        try:
            print("Index route: Getting all todos...")
            todos = self.todo_repository.get_all_todos()
            print(f"Index route: Got {len(todos)} todos")
            
            # Process recurring todos to show all occurrences from creation to next occurrence after now
            processed_todos = []
            now = datetime.now()
            
            for todo in todos:
                # 确保元组包含completed_occurrences字段
                if len(todo) == 11:
                    todo_id, title, completed, deadline, is_recurring, recurrence_type, recurrence_interval, recurrence_days, next_occurrence_from_db, deleted_occurrences, completed_occurrences = todo
                else:
                    # 兼容旧版本
                    todo_id, title, completed, deadline, is_recurring, recurrence_type, recurrence_interval, recurrence_days, next_occurrence_from_db, deleted_occurrences = todo
                    completed_occurrences = None
                
                if is_recurring:
                    try:
                        # Parse deleted occurrences from database
                        deleted_occurrences_list = []
                        if deleted_occurrences:
                            try:
                                deleted_occurrences_list = json.loads(deleted_occurrences)
                            except (json.JSONDecodeError, TypeError):
                                deleted_occurrences_list = []
                        
                        # Parse completed occurrences from database
                        completed_occurrences_list = []
                        if completed_occurrences:
                            try:
                                completed_occurrences_list = json.loads(completed_occurrences)
                            except (json.JSONDecodeError, TypeError, ValueError, Exception):
                                completed_occurrences_list = []
                        
                        # Generate all possible occurrences
                        all_possible_occurrences = []
                        current_deadline = deadline
                        
                        # 生成初始实例
                        initial_occurrences = generate_all_occurrences(
                            deadline, recurrence_type, recurrence_interval, recurrence_days,
                            logger=self.app.logger
                        )
                        
                        # 添加初始实例到所有可能实例列表
                        all_possible_occurrences.extend(initial_occurrences)
                        
                        # 确保我们有足够多的实例来过滤
                        if all_possible_occurrences:
                            last_occurrence = all_possible_occurrences[-1]
                            # 再生成一些额外的实例，确保我们有足够的实例来显示4个未删除的
                            for _ in range(10):
                                next_occurrence_val = calculate_next_occurrence(
                                    last_occurrence, recurrence_type, recurrence_interval, recurrence_days,
                                    logger=self.app.logger
                                )
                                
                                if next_occurrence_val and next_occurrence_val not in all_possible_occurrences:
                                    all_possible_occurrences.append(next_occurrence_val)
                                    last_occurrence = next_occurrence_val
                                else:
                                    break
                        
                        # 过滤掉已删除的实例，但保留已完成的实例
                        filtered_occurrences = [occurrence for occurrence in all_possible_occurrences 
                                                if occurrence not in deleted_occurrences_list]
                        
                        # 确保始终显示4个实例
                        while len(filtered_occurrences) < 4 and filtered_occurrences:
                            # 获取当前最后一个实例
                            last_occurrence = filtered_occurrences[-1]
                            # 生成下一个实例
                            next_occurrence = calculate_next_occurrence(
                                last_occurrence, recurrence_type, recurrence_interval, recurrence_days,
                                logger=self.app.logger
                            )
                            
                            if next_occurrence and next_occurrence not in filtered_occurrences:
                                filtered_occurrences.append(next_occurrence)
                            else:
                                break
                        
                        # 如果过滤后没有实例，生成新的实例
                        if not filtered_occurrences:
                            next_occurrence = calculate_next_occurrence(
                                deadline, recurrence_type, recurrence_interval, recurrence_days,
                                logger=self.app.logger
                            )
                            
                            if next_occurrence:
                                filtered_occurrences.append(next_occurrence)
                                # 继续生成更多实例，直到达到4个
                                while len(filtered_occurrences) < 4:
                                    last_occurrence = filtered_occurrences[-1]
                                    next_occurrence = calculate_next_occurrence(
                                        last_occurrence, recurrence_type, recurrence_interval, recurrence_days,
                                        logger=self.app.logger
                                    )
                                    
                                    if next_occurrence and next_occurrence not in filtered_occurrences:
                                        filtered_occurrences.append(next_occurrence)
                                    else:
                                        break
                        
                        # 只保留前4个实例
                        filtered_occurrences = filtered_occurrences[:4]
                        
                        # Add all non-deleted occurrences as individual todos
                        for i, occurrence in enumerate(filtered_occurrences):
                            # Create a unique ID for each occurrence
                            # 使用日期字符串生成唯一ID，避免索引变化导致的ID冲突
                            # 将日期转换为数字格式作为ID的一部分
                            # 解析日期字符串为datetime对象
                            occ_datetime = datetime.strptime(occurrence, '%Y-%m-%d %H:%M:%S')
                            # 使用时间戳的后6位作为唯一标识
                            occ_timestamp = int(occ_datetime.timestamp())
                            unique_part = occ_timestamp % 1000000
                            occurrence_id = todo_id * 1000000 + unique_part  # 确保ID唯一且为正数
                            
                            # Check if this occurrence is completed
                            is_occurrence_completed = 1 if occurrence in completed_occurrences_list else 0
                            
                            # Create a new todo instance for each occurrence
                            occurrence_todo = (
                                occurrence_id,  # Unique ID for this occurrence
                                title,  # Same title as original
                                is_occurrence_completed,  # Completed status
                                occurrence,  # Use occurrence as deadline
                                True,  # Mark as recurring
                                recurrence_type,
                                recurrence_interval,
                                recurrence_days,
                                occurrence,
                                None,  # No deleted occurrences for individual instances
                                None  # No completed occurrences for individual instances
                            )
                            processed_todos.append(occurrence_todo)
                    except ValueError as e:
                        print(f"Error processing recurring todo {todo_id}: {e}")
                        continue
                else:
                    # Add non-recurring todos normally
                    processed_todos.append(todo)
            
            print(f"Index route: Processed to {len(processed_todos)} todos")
            return render_template('index.html', todos=processed_todos)
        except Exception as e:
            # Print detailed error information
            print(f"Index route error: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            return f"An error occurred while loading todos: {type(e).__name__}: {str(e)}", 500

    def add_todo(self):
        """Add todo route"""
        try:
            title = request.form['title']
            deadline = request.form.get('deadline')

            # Get recurrence-related parameters
            is_recurring = request.form.get('is_recurring') == 'on'
            recurrence_type = request.form.get('recurrence_type')
            recurrence_interval = int(request.form.get('recurrence_interval', 1))
            recurrence_days = request.form.get('recurrence_days')

            # Calculate next occurrence if needed
            next_occurrence = None
            if is_recurring and deadline:
                next_occurrence = calculate_next_occurrence(
                    deadline, recurrence_type, recurrence_interval, recurrence_days,
                    logger=self.app.logger
                )

            # Add todo to database
            self.todo_repository.add_todo(
                title, deadline, is_recurring, recurrence_type, recurrence_interval,
                recurrence_days, next_occurrence
            )

            return redirect(url_for('index'))
        except Exception as e:
            self.app.logger.error(f"Error adding todo: {e}")
            return "An error occurred while adding todo", 500

    def delete_todo(self, todo_id):
        """Delete todo route"""
        try:
            self.todo_repository.delete_todo(todo_id)
            return redirect(url_for('index'))
        except Exception as e:
            self.app.logger.error(f"Error deleting todo: {e}")
            return "An error occurred while deleting todo", 500

    def toggle_todo(self, todo_id):
        """Toggle todo completion status route"""
        try:
            # Get all todos to check which ones exist in the database
            all_todos = self.todo_repository.get_all_todos()
            existing_ids = [t[0] for t in all_todos]
            
            is_generated_id = todo_id not in existing_ids
            original_id = todo_id // 1000000 if is_generated_id else todo_id
            
            # Get original todo details
            original_todo = self.todo_repository.get_todo(original_id)

            if original_todo:
                # For generated occurrence IDs (recurring todo instances)
                if is_generated_id:
                    # Parse original todo tuple
                    if len(original_todo) == 10:
                        id_in_db, title, completed, deadline, is_recurring, recurrence_type, recurrence_interval, recurrence_days, next_occurrence_from_db, deleted_occurrences_json = original_todo
                        completed_occurrences_json = None
                    else:
                        id_in_db, title, completed, deadline, is_recurring, recurrence_type, recurrence_interval, recurrence_days, next_occurrence_from_db, deleted_occurrences_json, completed_occurrences_json = original_todo
                    
                    if is_recurring:
                        # Parse deleted occurrences
                        deleted_occurrences = []
                        if deleted_occurrences_json:
                            try:
                                deleted_occurrences = json.loads(deleted_occurrences_json)
                            except (json.JSONDecodeError, TypeError):
                                deleted_occurrences = []
                        
                        # Parse completed occurrences
                        completed_occurrences = []
                        if completed_occurrences_json:
                            try:
                                completed_occurrences = json.loads(completed_occurrences_json)
                            except (json.JSONDecodeError, TypeError):
                                completed_occurrences = []
                        
                        # Generate all occurrences to find which one we're toggling
                        from todolist.utils import generate_all_occurrences, calculate_next_occurrence
                        all_occurrences = generate_all_occurrences(deadline, recurrence_type, recurrence_interval, recurrence_days)
                        
                        # Ensure we have enough occurrences
                        if all_occurrences:
                            # Generate more occurrences to find the correct one
                            for _ in range(20):  # 生成足够多的实例
                                last_occurrence = all_occurrences[-1]
                                next_occurrence_val = calculate_next_occurrence(last_occurrence, recurrence_type, recurrence_interval, recurrence_days)
                                if next_occurrence_val and next_occurrence_val not in all_occurrences:
                                    all_occurrences.append(next_occurrence_val)
                                else:
                                    break
                            
                            # 生成所有实例，然后找出与当前ID匹配的实例
                            matching_occurrence = None
                            for occurrence in all_occurrences:
                                # 使用相同的ID生成逻辑来匹配实例
                                from datetime import datetime
                                occ_datetime = datetime.strptime(occurrence, '%Y-%m-%d %H:%M:%S')
                                occ_timestamp = int(occ_datetime.timestamp())
                                unique_part = occ_timestamp % 1000000
                                generated_id = original_id * 1000000 + unique_part
                                
                                if generated_id == todo_id:
                                    matching_occurrence = occurrence
                                    break
                            
                            if matching_occurrence:
                                
                                # Check if this occurrence is already completed
                                is_completed = matching_occurrence in completed_occurrences
                                
                                if is_completed:
                                    # Remove from completed list (toggle off)
                                    completed_occurrences.remove(matching_occurrence)
                                else:
                                    # Add to completed list (toggle on)
                                    completed_occurrences.append(matching_occurrence)
                                
                                # Update the original todo with new completed occurrences
                                update_data = {
                                    'completed_occurrences': json.dumps(completed_occurrences)
                                }
                                
                                # Update the database
                                self.todo_repository.update_todo(original_id, **update_data)
                else:
                    # Regular todo (non-generated ID)
                    # Toggle completion status
                    if len(original_todo) == 10:
                        id_in_db, title, completed, deadline, is_recurring, recurrence_type, recurrence_interval, recurrence_days, next_occurrence_from_db, deleted_occurrences_json = original_todo
                        completed_occurrences_json = None
                    else:
                        id_in_db, title, completed, deadline, is_recurring, recurrence_type, recurrence_interval, recurrence_days, next_occurrence_from_db, deleted_occurrences_json, completed_occurrences_json = original_todo
                    
                    new_completed = 1 - completed
                    self.todo_repository.update_todo(original_id, completed=new_completed)

            return redirect(url_for('index'))
        except Exception as e:
            # Print detailed error information for debugging
            print(f"Toggle todo error: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            self.app.logger.error(f"Error toggling todo: {e}")
            return f"An error occurred while updating todo: {type(e).__name__}: {str(e)}", 500

    def batch_delete(self):
        """Batch delete todos route"""
        try:
            # Get the todo_ids from the form data
            todo_ids_json = request.form.get('todo_ids')
            if not todo_ids_json:
                return redirect(url_for('index'))

            # Parse the JSON string to get the list of todo ids and delete_all flag
            delete_data = json.loads(todo_ids_json)
            todo_ids = delete_data.get('todo_ids', [])
            delete_all = delete_data.get('delete_all', False)
            
            # Convert to integers
            todo_ids = [int(id) for id in todo_ids]

            # Call batch_delete_todos with delete_all parameter
            self.todo_repository.batch_delete_todos(todo_ids, delete_all)

            return redirect(url_for('index'))
        except Exception as e:
            self.app.logger.error(f'Error batch deleting todos: {e}')
            return "An error occurred while deleting todos", 500
