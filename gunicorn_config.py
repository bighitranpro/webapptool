"""
Gunicorn Configuration File
Production-ready settings for BI GHI TOOL MMO
"""

import multiprocessing

# Server Socket
bind = "0.0.0.0:5003"
backlog = 2048

# Worker Processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 30
keepalive = 2

# Logging
accesslog = "/home/user/webapp/logs/access.log"
errorlog = "/home/user/webapp/logs/error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process Naming
proc_name = "bighi-tool-mmo"

# Server Mechanics
daemon = False
pidfile = "/home/user/webapp/gunicorn.pid"
user = None
group = None
tmp_upload_dir = None

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190
