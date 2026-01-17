# TodoList Application

A simple and elegant TodoList web application built with Flask, featuring SQLite storage and a clean, responsive design.

## Features

- ✅ Add new todo items with deadline support
- ✅ Set default deadline (current time + 24 hours)
- ✅ Deadline status display (overdue, upcoming, normal)
- ✅ Mark items as completed/pending
- ✅ Delete todo items
- ✅ Responsive web design
- ✅ Real-time updates
- ✅ SQLite database storage with automatic migration
- ✅ Multi-environment configuration support (local/stage/live/test)
- ✅ Command-line parameterized startup
- ✅ Environment variable configuration
- ✅ Comprehensive error handling
- ✅ Production-ready setup
- ✅ Comprehensive end-to-end testing
- ✅ Security-enhanced HTTP methods (POST for delete/toggle operations)
- ✅ Periodic todo items with customizable recurrence
- ✅ Multiple recurrence types: daily, weekly, monthly, yearly, hourly, minutely
- ✅ Weekly recurrence with specific day selection
- ✅ Automatic next occurrence calculation when marking as complete
- ✅ Visible recurrence information in todo list
- ✅ Batch operations: select all todo items
- ✅ Batch operations: select completed todo items
- ✅ Batch operations: delete selected todo items
- ✅ Support for deleting periodic todos with batch operations

## Tech Stack

- **Backend**: Python 3, Flask framework
- **Database**: SQLite
- **Frontend**: HTML, CSS, JavaScript (no external dependencies)
- **Deployment**: Gunicorn (WSGI), Nginx (reverse proxy)

## Getting Started

### Prerequisites

- Python 3.7 or higher
- pip package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd todolist_project
   ```

2. **Create and activate a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install flask gunicorn
   ```

### Running the Application

#### Basic Usage

```bash
# Default to local environment
python app.py

# Specify environment explicitly
python app.py -e local
python app.py -e stage
python app.py -e live

# Show help message
python app.py --help
```

#### Environment-specific Startup

##### Local Development
```bash
python app.py -e local
# or simply
python app.py
```

The application will be available at `http://127.0.0.1:5000`

##### Stage/Test Environment
```bash
python app.py -e stage
```

The application will be available at `http://0.0.0.0:8000`

##### Production Environment
```bash
python app.py -e live
```

The application will be available at `http://0.0.0.0:8000`

#### Using Gunicorn (Production)

```bash
# Basic usage with default environment
gunicorn -w 4 app:app

# Specify environment using environment variable
export FLASK_ENV=production
gunicorn -w 4 -b 0.0.0.0:8000 app:app

# For specific environments
# Local
gunicorn -w 4 -b 127.0.0.1:5000 app:app

# Stage/Live
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

## Project Structure

```
todolist_project/
├── app.py                 # Main Flask application
├── README.md              # This file
├── requirements.txt       # Dependencies list
├── config/                # Environment configuration
│   ├── local/             # Local development configuration
│   │   └── config.py
│   ├── stage/             # Stage/test configuration
│   │   └── config.py
│   └── live/              # Production configuration
│       └── config.py
├── templates/
│   └── index.html         # Frontend template
└── todolist_local.db      # SQLite database (auto-generated, environment-specific)
```

## Configuration

The application supports multiple environments with different configurations. You can specify the environment using the `-e/--env` command-line parameter.

### Environment Types

| Environment | Description | Debug Mode | Default Port | Database Path |
|-------------|-------------|------------|--------------|---------------|
| `local`     | Local development | True | 5000 | `todolist_local.db` |
| `stage`     | Stage/test environment | False | 8000 | `todolist_stage.db` |
| `live`      | Production environment | False | 8000 | `/var/lib/todolist/todolist_live.db` |

### Command-line Parameters

| Parameter | Short | Description | Choices | Default |
|-----------|-------|-------------|---------|---------|
| `--env` | `-e` | Environment to run the application in | `local`, `stage`, `live` | `local` |

### Configuration Files

Configuration is stored in the `config/` directory, with separate files for each environment:

- `config/local/config.py` - Local development configuration
- `config/stage/config.py` - Stage/test configuration
- `config/live/config.py` - Production configuration

Each configuration file contains settings for:
- Debug mode
- Server host and port
- Database path
- Secret key

### Environment Variables

You can still override configuration using environment variables, which take precedence over the configuration files:

| Variable          | Description                |
|-------------------|----------------------------|
| `DEBUG`           | Enable debug mode          |
| `DATABASE_PATH`   | Path to SQLite database    |
| `PORT`            | Server listening port      |

## Usage

1. **Add a regular todo item with deadline**
   - Enter the task in the input field
   - Set a deadline using the datetime picker (default: current time + 24 hours)
   - Click "Add" button

2. **Add a periodic todo item**
   - Enter the task in the input field
   - Set a deadline using the datetime picker (default: current time + 24 hours)
   - Check the "周期" (Periodic) checkbox to enable recurrence settings
   - Select the recurrence type from the dropdown menu:
     - **每n年** (Every n years)
     - **每n月** (Every n months)
     - **每n周** (Every n weeks) - select specific days of the week
     - **每n日** (Every n days)
     - **每n小时** (Every n hours)
     - **每n分钟** (Every n minutes)
   - Set the recurrence interval (number of units between occurrences)
   - Click "Add" button

3. **Mark as completed/pending**
   - For regular todos: Click the checkbox to toggle between completed and pending
   - For periodic todos: Click the checkbox to mark the current occurrence as completed; the todo will automatically update to the next occurrence

4. **Delete a todo item**
   - Click the "Delete" button next to the todo item

5. **Deadline status indicators**
   - 🟢 **Normal**: Deadline is more than 24 hours away
   - 🟠 **Upcoming**: Deadline is within the next 24 hours
   - 🔴 **Overdue**: Deadline has passed

6. **Periodic todo indicators**
   - Periodic todos display their recurrence pattern next to the deadline
   - Example: "每3天" (Every 3 days), "每2周 一、三、五" (Every 2 weeks on Monday, Wednesday, Friday)

7. **Batch operations**
   - **Select All**: Click the checkbox at the top of the todo list to select all todo items
   - **Select Completed**: Click the "选中已完成" (Select Completed) button to select only completed todo items
   - **Delete Selected**: Click the "删除选中" (Delete Selected) button to delete all selected todo items
   - Batch operations work for both regular and periodic todos
   - When deleting periodic todos, the entire periodic todo is removed, not just the current occurrence

## Testing

### Running Tests

The application includes comprehensive end-to-end tests. To run the tests:

```bash
# Run all tests
python run_tests.py

# Run only end-to-end tests
python run_tests.py --marker e2e

# Run a specific test
python run_tests.py --test TestTodoListE2E::test_add_todo_item
```

### Test Coverage

The test suite covers:
- ✅ Home page loading
- ✅ Adding todo items with and without deadlines
- ✅ Marking items as completed/pending
- ✅ Deleting todo items
- ✅ Empty state display
- ✅ Deadline default value
- ✅ Deadline status display
- ✅ Periodic settings UI interaction
- ✅ Adding daily periodic todos
- ✅ Adding weekly periodic todos
- ✅ Adding monthly periodic todos
- ✅ Marking periodic todos complete and verifying automatic update to next occurrence
- ✅ Batch operations: Select all functionality
- ✅ Batch operations: Select completed functionality
- ✅ Batch operations: Delete selected functionality
- ✅ Batch operations: Delete selected periodic todos

## Database Migration

The application automatically handles database migrations:

- When starting the application, it checks if all required columns exist in the `todos` table
- If the `deadline` column is missing, it automatically adds it with a default value of current time + 24 hours
- If periodic-related columns (`is_recurring`, `recurrence_type`, `recurrence_interval`, `recurrence_days`) are missing, they are automatically added with default values
- This ensures backward compatibility with existing databases
- No manual database migration steps are required

## Database Schema

```sql
CREATE TABLE IF NOT EXISTS todos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    completed INTEGER DEFAULT 0,
    deadline DATETIME DEFAULT (DATETIME('now', '+24 hours')),
    is_recurring INTEGER DEFAULT 0,
    recurrence_type TEXT DEFAULT '',
    recurrence_interval INTEGER DEFAULT 1,
    recurrence_days TEXT DEFAULT '[]',
    next_occurrence DATETIME DEFAULT NULL
);
```

## Deployment

### Deploying to Ubuntu Server

1. **Update system packages**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. **Install required packages**
   ```bash
   sudo apt install python3 python3-pip python3-venv nginx git -y
   ```

3. **Clone the repository**
   ```bash
   cd /var/www
   sudo git clone <repository-url> todolist
   sudo chown -R www-data:www-data todolist
   ```

4. **Set up virtual environment**
   ```bash
   cd todolist
   python3 -m venv venv
   source venv/bin/activate
   pip install flask gunicorn
   ```

5. **Create systemd service**
   ```bash
   sudo nano /etc/systemd/system/todolist.service
   ```

   Add the following content:
   ```ini
   [Unit]
   Description=Gunicorn instance to serve TodoList
   After=network.target

   [Service]
   User=www-data
   Group=www-data
   WorkingDirectory=/var/www/todolist
   Environment="PATH=/var/www/todolist/venv/bin"
   ExecStart=/var/www/todolist/venv/bin/gunicorn --workers 3 --bind unix:todolist.sock -m 007 app:app

   [Install]
   WantedBy=multi-user.target
   ```

6. **Configure Nginx**
   ```bash
   sudo nano /etc/nginx/sites-available/todolist
   ```

   Add the following content:
   ```nginx
   server {
       listen 80;
       server_name your_domain.com;

       location / {
           proxy_pass http://unix:/var/www/todolist/todolist.sock;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

7. **Enable the application**
   ```bash
   sudo ln -s /etc/nginx/sites-available/todolist /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   sudo systemctl start todolist
   sudo systemctl enable todolist
   ```

## Security Considerations

- ✅ The application uses parameterized queries to prevent SQL injection
- ✅ Debug mode is disabled by default in production
- ✅ All database connections are properly managed and closed
- ✅ Input validation is implemented for all user inputs
- ✅ DELETE and TOGGLE operations use POST requests instead of GET requests to prevent CSRF attacks
- ✅ Database migrations are handled automatically to maintain schema integrity
- ✅ Comprehensive error handling prevents sensitive information leakage

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Changelog

See the [CHANGELOG](CHANGELOG.md) file for a detailed history of changes.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Flask documentation and community
- SQLite for lightweight database storage
- GitHub for version control and collaboration

## Contact

For any questions or suggestions, please open an issue on GitHub.

---

Built with ❤️ using Flask and Python
