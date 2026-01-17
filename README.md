# TodoList Application

A simple and elegant TodoList web application built with Flask, featuring SQLite storage and a clean, responsive design.

## Features

- ✅ Add new todo items
- ✅ Mark items as completed/pending
- ✅ Delete todo items
- ✅ Responsive web design
- ✅ Real-time updates
- ✅ SQLite database storage
- ✅ Multi-environment configuration support (local/stage/live)
- ✅ Command-line parameterized startup
- ✅ Environment variable configuration
- ✅ Comprehensive error handling
- ✅ Production-ready setup

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

1. **Add a todo item**
   - Enter the task in the input field
   - Click "Add" button

2. **Mark as completed/pending**
   - Click the checkbox next to the todo item

3. **Delete a todo item**
   - Click the "Delete" button next to the todo item

## Database Schema

```sql
CREATE TABLE IF NOT EXISTS todos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    completed INTEGER DEFAULT 0
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

- The application uses parameterized queries to prevent SQL injection
- Debug mode is disabled by default in production
- All database connections are properly managed and closed
- Input validation is implemented for all user inputs

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

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
