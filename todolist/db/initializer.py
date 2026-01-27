class DatabaseInitializer:
    """Database initializer and migration manager"""

    def __init__(self, db_connection):
        """Initialize database initializer

        Args:
            db_connection: DatabaseConnection instance
        """
        self.db_connection = db_connection

    def init_db(self):
        """Initialize database, create tables and add missing columns"""
        try:
            conn = self.db_connection.get_connection()
            cursor = conn.cursor()

            # Create table if not exists
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
                    next_occurrence DATETIME DEFAULT NULL,
                    deleted_occurrences TEXT DEFAULT NULL
                )
            ''')

            # Check and add missing columns
            cursor.execute("PRAGMA table_info(todos)")
            columns = [row[1] for row in cursor.fetchall()]

            # If deadline column doesn't exist, add it
            if 'deadline' not in columns:
                cursor.execute('''
                    ALTER TABLE todos ADD COLUMN deadline DATETIME DEFAULT (DATETIME('now', '+24 hours'))
                ''')

            # Add recurrence-related columns if missing
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

            # Add deleted_occurrences column if missing
            if 'deleted_occurrences' not in columns:
                cursor.execute('''
                    ALTER TABLE todos ADD COLUMN deleted_occurrences TEXT DEFAULT NULL
                ''')

            # Add completed_occurrences column if missing
            if 'completed_occurrences' not in columns:
                cursor.execute('''
                    ALTER TABLE todos ADD COLUMN completed_occurrences TEXT DEFAULT NULL
                ''')

            conn.commit()
        except Exception as e:
            print(f"Error initializing database: {e}")
            raise
        finally:
            conn.close()
