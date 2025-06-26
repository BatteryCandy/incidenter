#!/usr/bin/env python3
"""
Production Web Server Configuration for Incidenter

This script provides a production-ready configuration using Gunicorn.
"""
import os
import sys
from pathlib import Path
from server.app import app

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def create_gunicorn_config():
    """Create a Gunicorn configuration file."""
    config_content = """
# Gunicorn configuration for Incidenter web interface
import multiprocessing

# Server socket
bind = "0.0.0.0:5003"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Restart workers after this many requests, to prevent memory leaks
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = "incidenter-web"

# Server mechanics
preload_app = True
pidfile = "/tmp/incidenter.pid"
user = None
group = None
tmp_upload_dir = None

# SSL (uncomment and configure for HTTPS)
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"
"""

    config_path = project_root / "gunicorn.conf.py"
    config_path.write_text(config_content.strip())
    return config_path


def main():
    """Main production server launcher."""
    print("🚀 Starting Incidenter Production Web Server")

    # Create Gunicorn config if it doesn't exist
    config_path = create_gunicorn_config()
    print(f"📝 Gunicorn config created at: {config_path}")

    # Set production environment variables
    os.environ.setdefault("FLASK_ENV", "production")
    os.environ.setdefault("FLASK_DEBUG", "False")

    # Generate a secret key if not set
    if not os.environ.get("FLASK_SECRET_KEY"):
        import secrets

        os.environ["FLASK_SECRET_KEY"] = secrets.token_hex(32)
        print("🔐 Generated Flask secret key")

    print("🌐 Starting server on http://0.0.0.0:5003")
    print("📊 Workers: CPU cores * 2 + 1")
    print("🛠️  Press Ctrl+C to stop")

    try:
        # Start Gunicorn
        import subprocess

        subprocess.run(
            ["gunicorn", "--config", str(config_path), "server.app:app"],
            cwd=project_root,
        )
    except KeyboardInterrupt:
        print("\n👋 Shutting down production server...")
    except FileNotFoundError:
        print("❌ Gunicorn not found. Install with: pip install gunicorn")
        print("Falling back to development server...")
        app.run(host="0.0.0.0", port=5003)


if __name__ == "__main__":
    main()
