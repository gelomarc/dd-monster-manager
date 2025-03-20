import multiprocessing

# Gunicorn configuration
bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() * 2 + 1
threads = 2
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Process naming
proc_name = "ddmonsters"

# SSL (if using)
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190 