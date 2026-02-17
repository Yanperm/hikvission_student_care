#!/bin/bash
# Health Check Script - ตรวจสอบระบบทุก 1 นาที

LOG_FILE="/home/ubuntu/hikvission_student_care/logs/health_check.log"
APP_URL="http://localhost:5000"
MAX_RETRIES=3

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

check_health() {
    response=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "$APP_URL")
    
    if [ "$response" = "200" ]; then
        log "✅ System OK (HTTP $response)"
        return 0
    else
        log "❌ System DOWN (HTTP $response)"
        return 1
    fi
}

restart_app() {
    log "🔄 Restarting application..."
    sudo systemctl restart student-care-production
    sleep 10
    
    if check_health; then
        log "✅ Restart successful"
        # แจ้งเตือน LINE/Email (optional)
    else
        log "❌ Restart failed - Manual intervention required"
        # แจ้งเตือนด่วน
    fi
}

# Main
retry_count=0
while [ $retry_count -lt $MAX_RETRIES ]; do
    if check_health; then
        exit 0
    fi
    
    retry_count=$((retry_count + 1))
    log "⚠️ Retry $retry_count/$MAX_RETRIES"
    sleep 5
done

# ถ้าล้มเหลว 3 ครั้ง ให้ restart
log "🚨 Health check failed $MAX_RETRIES times - Initiating restart"
restart_app
