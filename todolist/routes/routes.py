from flask import render_template, request, redirect, url_for
from datetime import datetime, timedelta
from todolist.db import TodoRepository
from todolist.utils import calculate_next_occurrence


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
            
            # Process recurring todos to show upcoming occurrences
            processed_todos = []
            now = datetime.now()
            one_day_later = now + timedelta(days=1)
            
            for todo in todos:
                todo_id, title, completed, deadline, is_recurring, recurrence_type, recurrence_interval, recurrence_days, next_occurrence = todo
                
                # Add the original todo
                processed_todos.append(todo)
                
                # If it's a recurring todo and next_occurrence is set
                if is_recurring and next_occurrence:
                    try:
                        # Parse next occurrence time
                        next_occurrence_dt = datetime.strptime(next_occurrence, "%Y-%m-%d %H:%M:%S")
                        
                        # Check if next occurrence is within the next day
                        if now <= next_occurrence_dt <= one_day_later:
                            # Create a new todo instance for the upcoming occurrence
                            # Use a negative ID to indicate it's a generated occurrence
                            upcoming_todo = (
                                -todo_id,  # Negative ID to distinguish from actual todos
                                f"{title} (即将到来)",  # Indicate it's upcoming
                                0,  # Not completed
                                next_occurrence,  # Use next occurrence as deadline
                                True,  # Mark as recurring
                                recurrence_type,
                                recurrence_interval,
                                recurrence_days,
                                next_occurrence
                            )
                            processed_todos.append(upcoming_todo)
                    except ValueError as e:
                        print(f"Error parsing next_occurrence {next_occurrence} for todo {todo_id}: {e}")
                        continue
            
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
            # Skip negative IDs (generated upcoming occurrences)
            if todo_id < 0:
                return redirect(url_for('index'))
                
            # Get todo details
            todo = self.todo_repository.get_todo(todo_id)

            if todo:
                # Convert to dictionary for easier access
                todo_dict = dict(todo)
                completed = todo_dict['completed']

                # Check if it's a recurring todo
                is_recurring = todo_dict['is_recurring']

                if is_recurring:
                    # Recurring todo: update to next occurrence instead of marking as complete
                    current_deadline = todo_dict['deadline']
                    recurrence_type = todo_dict['recurrence_type']
                    recurrence_interval = todo_dict['recurrence_interval']
                    recurrence_days = todo_dict['recurrence_days']

                    # Calculate next occurrence
                    next_occurrence = calculate_next_occurrence(
                        current_deadline, recurrence_type, recurrence_interval, recurrence_days,
                        logger=self.app.logger
                    )

                    if next_occurrence:
                        # Update todo to next occurrence
                        self.todo_repository.update_todo(
                            todo_id,
                            deadline=next_occurrence,
                            next_occurrence=next_occurrence,
                            completed=0
                        )
                else:
                    # Regular todo: toggle completion status normally
                    new_completed = 1 - completed
                    self.todo_repository.update_todo(todo_id, completed=new_completed)

            return redirect(url_for('index'))
        except Exception as e:
            self.app.logger.error(f"Error toggling todo: {e}")
            return "An error occurred while updating todo", 500

    def batch_delete(self):
        """Batch delete todos route"""
        try:
            # Get the todo_ids from the form data
            todo_ids_json = request.form.get('todo_ids')
            if not todo_ids_json:
                return redirect(url_for('index'))

            # Parse the JSON string to get the list of todo ids
            import json
            todo_ids = json.loads(todo_ids_json)
            # Convert to integers
            todo_ids = [int(id) for id in todo_ids]

            # Batch delete the todos
            self.todo_repository.batch_delete_todos(todo_ids)

            return redirect(url_for('index'))
        except Exception as e:
            self.app.logger.error(f'Error batch deleting todos: {e}')
            return "An error occurred while deleting todos", 500
