from flask import Flask

from todolist.config import load_config, parse_args
from todolist.db import DatabaseConnection, DatabaseInitializer, TodoRepository
from todolist.routes import RoutesManager
from todolist.utils import fromjson_filter

# Create Flask application instance
app = Flask(__name__)

# Register template filters
app.template_filter('fromjson')(fromjson_filter)


def main():
    """Main entry point for the TodoList application"""
    # Parse command line arguments
    args = parse_args()

    # Load configuration
    config, db_path = load_config(app, args.env)

    # Initialize database
    db_connection = DatabaseConnection(db_path)
    db_initializer = DatabaseInitializer(db_connection)
    db_initializer.init_db()

    # Initialize repository
    todo_repository = TodoRepository(db_connection)

    # Register routes
    RoutesManager(app, todo_repository)

    # Start application
    app.run(
        debug=config.DEBUG,
        host=config.HOST,
        port=config.PORT
    )


if __name__ == '__main__':
    main()
