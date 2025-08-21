# Gunicorn configuration file for development

# Server socket
bind = "0.0.0.0:5000"

# Worker processes (fewer for development)
workers = 2
worker_class = "sync"
timeout = 30

# Logging (stdout/stderr for development)
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Development settings
reload = True
preload_app = False