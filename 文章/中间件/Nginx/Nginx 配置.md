# Nginx 配置

````xml
# 定义工作进程数，通常设置为CPU核心数  
worker_processes auto;  
  
# 设置错误日志的路径和级别  
error_log /var/log/nginx/error.log warn;  
  
# 设置进程PID文件的位置  
pid /var/run/nginx.pid;  
  
# 定义事件处理模型  
events {  
    # 设置每个worker进程的最大连接数  
    worker_connections 1024;  
    # 使用epoll事件驱动模型  
    use epoll;  
    # 多路复用连接进行复用  
    multi_accept on;  
}  
  
http {  
    # 设置日志格式  
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '  
                    '$status $body_bytes_sent "$http_referer" '  
                    '"$http_user_agent" "$http_x_forwarded_for"';  
  
    # 访问日志的路径和格式  
    access_log /var/log/nginx/access.log main;  
  
    # 发送文件  
    sendfile on;  
    # tcp_nopush on;  
  
    # 保持连接  
    keepalive_timeout 65;  
  
    # 开启gzip压缩  
    gzip on;  
    gzip_disable "msie6";  
  
    # 定义包含其他location配置文件的目录  
    include /etc/nginx/conf.d/*.conf;  
  
    # 设置服务器级别的配置  
    server {  
        # 监听端口  
        listen 80;  
        server_name localhost;  
  
        # 访问控制，允许所有来源  
        allow all;  
  
        # 定义location来处理静态文件请求  
        location /static/ {  
            root /path/to/static/files;  
            index index.html index.htm;  
        }  
  
        # 定义location来处理动态请求，通过代理转发到后端服务器  
        location / {  
            proxy_pass http://backend_server;  
            proxy_set_header Host $host;  
            proxy_set_header X-Real-IP $remote_addr;  
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;  
            proxy_set_header X-Forwarded-Proto $scheme;  
        }  
  
        # 错误页面配置  
        error_page 500 502 503 504 /50x.html;  
        location = /50x.html {  
            root /path/to/error/pages;  
        }  
    }  
  
    # 配置SSL/TLS，如果需要的话  
    # ...  
}
````