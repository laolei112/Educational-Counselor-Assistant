# 并行工作进程数
workers = 4
# 指定每个工作者的线程数
threads = 16

bind = '0.0.0.0:8080'
daemon = 'false'
# 工作模式协程
worker_class = 'gevent'
# 最大并发量
worker_connections = 1024
