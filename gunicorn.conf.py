workers = 1
worker_class = 'sync'
bind = '0.0.0.0:$PORT'
timeout = 300
max_requests = 1000
max_requests_jitter = 50
preload_app = True
