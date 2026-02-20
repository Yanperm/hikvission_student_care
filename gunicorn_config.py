import multiprocessing

# Server socket
bind = "0.0.0.0:8080"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "gevent"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 120
keepalive = 5

# Logging
accesslog = "/home/ubuntu/hikvission_student_care/logs/access.log"
errorlog = "/home/ubuntu/hikvission_student_care/logs/error.log"
loglevel = "info"

# Process naming
proc_name = "student_care"

# Server mechanics
daemon = False
pidfile = "/home/ubuntu/hikvission_student_care/gunicorn.pid"
user = "ubuntu"
group = "ubuntu"
tmp_upload_dir = None

# SSL (if needed)
# keyfile = "/path/to/key.pem"
# certfile = "/path/to/cert.pem"
