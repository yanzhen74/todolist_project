import json


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
            cursor.execute('SELECT id, title, completed, deadline, is_recurring, recurrence_type, recurrence_interval, recurrence_days, next_occurrence FROM todos')
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
                    row[8]   # next_occurrence
                ))
            return todos
        finally:
            conn.close()
    
    def add_todo(self, title, deadline, is_recurring=False, recurrence_type=None, recurrence_interval=1, recurrence_days=None, next_occurrence=None):
        """Add a new todo to the database"""
        conn = self.db_connection.get_connection()
        try:
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
