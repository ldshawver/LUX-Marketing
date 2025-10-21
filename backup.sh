#!/bin/bash

# Backup script for Email Marketing App
# Creates backups of database and application files

APP_NAME="email-marketing"
APP_DIR="/opt/$APP_NAME"
BACKUP_DIR="/var/backups/$APP_NAME"
DATE=$(date +%Y%m%d_%H%M%S)

echo "=== Email Marketing App Backup Script ==="

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Backup database
echo "Backing up database..."
sudo -u postgres pg_dump "${APP_NAME}_db" > "$BACKUP_DIR/database_$DATE.sql"

# Backup application files
echo "Backing up application files..."
tar -czf "$BACKUP_DIR/app_files_$DATE.tar.gz" -C "$APP_DIR" .

# Backup environment configuration
echo "Backing up configuration..."
cp "$APP_DIR/.env" "$BACKUP_DIR/env_$DATE.backup"

# Clean old backups (keep last 7 days)
echo "Cleaning old backups..."
find "$BACKUP_DIR" -type f -mtime +7 -delete

# Set permissions
chown -R root:root "$BACKUP_DIR"
chmod 600 "$BACKUP_DIR"/*

echo "Backup completed successfully!"
echo "Files saved to: $BACKUP_DIR"
echo ""
echo "Latest backups:"
ls -la "$BACKUP_DIR" | tail -5