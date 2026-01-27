import sys


def load_config(app, env):
    """Load configuration based on environment

    Args:
        app: Flask application instance
        env: Environment name (local, stage, live, test)

    Returns:
        tuple: (config, db_path) - Configuration object and database path
    """
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

        return config, db_path

    except Exception as e:
        print(f"Error loading {env} configuration: {e}")
        sys.exit(1)
