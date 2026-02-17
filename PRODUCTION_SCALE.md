# Production Configuration for 30,000+ students

## Database (PostgreSQL RDS)
- Connection Pool: 10-100 (ThreadedConnectionPool)
- Max Connections: 100
- Timeout: 10s

## Server Requirements
- RAM: 16GB+ (แนะนำ 32GB)
- CPU: 8 cores+
- Storage: 500GB+ SSD

## Gunicorn Configuration
```bash
gunicorn -w 8 -b 0.0.0.0:5000 --timeout 120 --max-requests 1000 --max-requests-jitter 50 local_app:app
```

## Nginx Configuration
```nginx
upstream backend {
    least_conn;
    server 127.0.0.1:5000;
    server 127.0.0.1:5001;
    server 127.0.0.1:5002;
    server 127.0.0.1:5003;
}

server {
    client_max_body_size 50M;
    proxy_connect_timeout 120s;
    proxy_send_timeout 120s;
    proxy_read_timeout 120s;
}
```

## PostgreSQL RDS Settings
```sql
max_connections = 200
shared_buffers = 4GB
effective_cache_size = 12GB
work_mem = 64MB
maintenance_work_mem = 1GB
```

## Redis Cache (แนะนำ)
- ใช้ Redis สำหรับ session และ cache
- TTL: 1 hour

## CDN
- ใช้ CloudFront สำหรับ static files
- ใช้ S3 สำหรับเก็บรูปนักเรียน

## Monitoring
- CloudWatch Alarms
- Database connection pool monitoring
- Memory usage alerts
