import sqlite3


class DatabaseConnection:
    """Database connection manager"""

    def __init__(self, db_path):
        """Initialize database connection manager

        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path

    def get_connection(self):
        """Get a database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
