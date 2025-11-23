"""
Gunicorn configuration file for BiTool application
"""

import multiprocessing
import os

# Server Socket
bind = "0.0.0.0:5003"
backlog = 2048

# Worker Processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "gevent"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 120
keepalive = 5

# Server Mechanics
daemon = False
pidfile = "/home/root/webapp/gunicorn.pid"
umask = 0
user = None
group = None
tmp_upload_dir = None

# Logging
accesslog = "/home/root/webapp/logs/access.log"
errorlog = "/home/root/webapp/logs/error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process Naming
proc_name = "bitool_app"

# Server Hooks
def on_starting(server):
    """Called just before the master process is initialized."""
    print("=" * 80)
    print("🚀 BiTool Application Starting...")
    print("=" * 80)

def when_ready(server):
    """Called just after the server is started."""
    print("✅ BiTool is ready to handle requests!")
    print(f"🌐 Server: {bind}")
    print(f"👷 Workers: {workers}")
    print("=" * 80)

def on_exit(server):
    """Called just before exiting Gunicorn."""
    print("=" * 80)
    print("🛑 BiTool Application Shutting Down...")
    print("=" * 80)

# SSL (if needed in future)
# keyfile = None
# certfile = None
