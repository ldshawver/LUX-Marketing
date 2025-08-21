#!/bin/bash

# Monitoring script for Email Marketing App
# Can be run as a cron job to monitor application health

APP_NAME="email-marketing"
LOG_FILE="/var/log/$APP_NAME/monitoring.log"
HEALTH_URL="http://localhost:5000/health"

# Function to log with timestamp
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

# Check if application is running
if ! systemctl is-active --quiet "$APP_NAME"; then
    log_message "ERROR: Application service is not running"
    echo "Application is down. Attempting to restart..."
    systemctl restart "$APP_NAME"
    sleep 10
    
    if systemctl is-active --quiet "$APP_NAME"; then
        log_message "INFO: Successfully restarted application"
    else
        log_message "CRITICAL: Failed to restart application"
        exit 1
    fi
fi

# Check application health endpoint
if curl -f -s "$HEALTH_URL" > /dev/null; then
    log_message "INFO: Health check passed"
else
    log_message "WARNING: Health check failed"
    echo "Health check failed. Restarting application..."
    systemctl restart "$APP_NAME"
fi

# Check disk space (alert if over 85%)
DISK_USAGE=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -gt 85 ]; then
    log_message "WARNING: Disk usage is ${DISK_USAGE}%"
fi

# Check memory usage (alert if over 90%)
MEMORY_USAGE=$(free | grep Mem | awk '{printf("%.0f", $3/$2 * 100.0)}')
if [ "$MEMORY_USAGE" -gt 90 ]; then
    log_message "WARNING: Memory usage is ${MEMORY_USAGE}%"
fi

log_message "INFO: Monitoring check completed"