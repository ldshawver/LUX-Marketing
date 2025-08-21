# Email Marketing App - VPS Deployment Guide

This guide will help you deploy the Email Marketing Automation App on a Debian 12 VPS.

## Prerequisites

- Debian 12 VPS with root access
- Domain name pointing to your VPS (optional but recommended)
- Microsoft Graph API credentials (for email sending)
- OpenAI API key (optional, for AI features)

## Quick Deployment

1. **Upload files to your VPS:**
   ```bash
   # Copy all files to your VPS
   scp -r * root@your-vps-ip:/root/email-marketing-deploy/
   ```

2. **Run the deployment script:**
   ```bash
   ssh root@your-vps-ip
   cd /root/email-marketing-deploy/
   chmod +x deploy.sh
   ./deploy.sh
   ```

3. **Configure your credentials:**
   ```bash
   nano /opt/email-marketing/.env
   ```
   Update the following values:
   - `MS_CLIENT_ID` - Your Microsoft Graph Client ID
   - `MS_CLIENT_SECRET` - Your Microsoft Graph Client Secret  
   - `MS_TENANT_ID` - Your Microsoft Tenant ID
   - `OPENAI_API_KEY` - Your OpenAI API key (optional)
   - Change the PostgreSQL password

4. **Update domain configuration:**
   ```bash
   nano /etc/nginx/sites-available/email-marketing
   ```
   Replace `your_domain.com` with your actual domain

5. **Restart services:**
   ```bash
   systemctl restart email-marketing nginx
   ```

## SSL Certificate Setup

After configuring your domain:

```bash
chmod +x ssl-setup.sh
./ssl-setup.sh your-domain.com
```

## Application Management

### Service Commands
```bash
# Start the application
systemctl start email-marketing

# Stop the application
systemctl stop email-marketing

# Restart the application
systemctl restart email-marketing

# Check status
systemctl status email-marketing

# View logs
journalctl -u email-marketing -f
```

### Application Logs
- Application logs: `/var/log/email-marketing/`
- Nginx logs: `/var/log/nginx/`
- System logs: `journalctl -u email-marketing`

## Backup and Maintenance

### Create Backup
```bash
chmod +x backup.sh
./backup.sh
```

### Update Application
```bash
chmod +x update.sh
./update.sh
```

### Monitor Health
```bash
chmod +x monitoring.sh
./monitoring.sh
```

### Set up automated monitoring (optional)
```bash
# Add to crontab to run every 5 minutes
crontab -e
# Add this line:
# */5 * * * * /opt/email-marketing/monitoring.sh
```

## Database Access

### Connect to PostgreSQL
```bash
sudo -u postgres psql email-marketing_db
```

### Common Database Commands
```sql
-- List all tables
\dt

-- View users
SELECT * FROM user;

-- View contacts
SELECT * FROM contact;

-- View campaigns
SELECT * FROM campaign;
```

## Troubleshooting

### Application won't start
```bash
# Check logs
journalctl -u email-marketing -n 50

# Check configuration
source /opt/email-marketing/.env
echo $DATABASE_URL

# Test database connection
sudo -u email-marketing psql $DATABASE_URL -c "SELECT 1;"
```

### Database issues
```bash
# Restart PostgreSQL
systemctl restart postgresql

# Check PostgreSQL status
systemctl status postgresql

# Reset database (WARNING: This will delete all data)
sudo -u postgres dropdb email-marketing_db
sudo -u postgres createdb email-marketing_db -O email-marketing
```

### Permission issues
```bash
# Fix file permissions
chown -R email-marketing:email-marketing /opt/email-marketing
chmod 600 /opt/email-marketing/.env
```

## Security Recommendations

1. **Change default passwords:**
   - PostgreSQL password in `.env`
   - Admin user password (login as admin, change in app)

2. **Configure firewall:**
   ```bash
   ufw enable
   ufw allow 22/tcp
   ufw allow 80/tcp
   ufw allow 443/tcp
   ```

3. **Set up fail2ban (optional):**
   ```bash
   apt install fail2ban
   systemctl enable fail2ban
   ```

4. **Regular updates:**
   ```bash
   apt update && apt upgrade -y
   ```

## Default Login

After deployment, you can access the application at:
- HTTP: `http://your-domain.com`
- HTTPS: `https://your-domain.com` (after SSL setup)

**Default admin credentials:**
- Username: `admin`
- Password: `admin123`

**⚠️ Important: Change the default password immediately after first login!**

## Support

If you encounter issues:
1. Check the logs: `journalctl -u email-marketing -f`
2. Verify configuration: `cat /opt/email-marketing/.env`
3. Test health endpoint: `curl http://localhost:5000/health`
4. Check service status: `systemctl status email-marketing`

For production use, consider:
- Setting up automated backups
- Implementing log rotation
- Configuring email alerts for system issues
- Using a CDN for static assets
- Setting up monitoring with tools like Prometheus/Grafana