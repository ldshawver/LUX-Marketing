# Deploy to lux.lucifercruz.com - Complete Guide

## 🚀 Quick Deployment (Automated)

I've created an automated deployment script for your VPS. Here's how to deploy your email marketing app to **lux.lucifercruz.com**:

### Option 1: Automated Deployment

```bash
# Run this from your local machine where you have the files
./deploy-to-vps.sh
```

This script will:
- Upload files to your VPS (194.195.92.52)
- Extract and install everything automatically
- Configure nginx for lux.lucifercruz.com
- Set up the database and services

### Option 2: Manual Step-by-Step

If you prefer manual control:

```bash
# 1. Upload the package
scp email-marketing-app-*.tar.gz root@194.195.92.52:/root/

# 2. Connect to your VPS
ssh root@194.195.92.52

# 3. Extract and deploy
cd /root
tar -xzf email-marketing-app-*.tar.gz
cd email-marketing-app-*
chmod +x deploy.sh
./deploy.sh

# 4. Configure your domain
nano /etc/nginx/sites-available/email-marketing
# Change "your_domain.com" to "lux.lucifercruz.com"

# 5. Restart services
systemctl restart email-marketing nginx
```

## 🔧 Post-Deployment Configuration

### 1. Configure API Credentials

```bash
ssh root@194.195.92.52
nano /opt/email-marketing/.env
```

Update these values:
```env
# Microsoft Graph API (required for email sending)
MS_CLIENT_ID=your_microsoft_client_id
MS_CLIENT_SECRET=your_microsoft_client_secret
MS_TENANT_ID=your_microsoft_tenant_id

# OpenAI API (optional, for LUX AI features)
OPENAI_API_KEY=your_openai_api_key

# Database (already configured, but you can change the password)
DATABASE_URL=postgresql://email-marketing:your_password@localhost/email-marketing_db
```

### 2. Set Up SSL Certificate

```bash
ssh root@194.195.92.52
cd /root/email-marketing-app-*
./ssl-setup.sh lux.lucifercruz.com
```

### 3. Restart Services After Configuration

```bash
systemctl restart email-marketing nginx
```

## 🌐 Access Your Application

**After deployment:**
- HTTP: http://lux.lucifercruz.com
- HTTPS: https://lux.lucifercruz.com (after SSL setup)

**Default login:**
- Username: `admin`
- Password: `admin123`

## 📊 Service Management

```bash
# Check application status
systemctl status email-marketing

# View application logs
journalctl -u email-marketing -f

# Restart application
systemctl restart email-marketing

# Check nginx status
systemctl status nginx

# View nginx logs
tail -f /var/log/nginx/error.log
```

## 🔒 Security Notes

1. **Change default password** immediately after first login
2. **Update API credentials** in the .env file
3. **Set up SSL certificate** for HTTPS
4. **Configure firewall** if needed:
   ```bash
   ufw enable
   ufw allow 22/tcp    # SSH
   ufw allow 80/tcp    # HTTP
   ufw allow 443/tcp   # HTTPS
   ```

## 🔧 Troubleshooting

### Application won't start
```bash
# Check logs
journalctl -u email-marketing -n 50

# Check if port is in use
netstat -tlnp | grep :5000

# Restart the service
systemctl restart email-marketing
```

### Database connection issues
```bash
# Check PostgreSQL
systemctl status postgresql

# Test database connection
sudo -u postgres psql -c "SELECT 1;"

# Connect to app database
sudo -u postgres psql email-marketing_db
```

### Nginx issues
```bash
# Test configuration
nginx -t

# Check error logs
tail -f /var/log/nginx/error.log

# Restart nginx
systemctl restart nginx
```

## 📧 Email Configuration Requirements

To send emails, you need Microsoft Graph API credentials:

1. **Register an app** in Azure AD
2. **Add permissions:** Mail.Send (Application permission)
3. **Get admin consent** for the tenant
4. **Copy credentials** to your .env file

Without these credentials, the app will work but email sending will fail.

## 🔄 Updates and Maintenance

### Backup your data
```bash
./backup.sh
```

### Update the application
```bash
./update.sh
```

### Monitor health
```bash
./monitoring.sh
```

## 📞 Support

If you encounter issues:

1. **Check service status:** `systemctl status email-marketing`
2. **View logs:** `journalctl -u email-marketing -f`
3. **Test health:** `curl http://localhost:5000/health`
4. **Verify configuration:** `cat /opt/email-marketing/.env`

Your email marketing app will be fully functional once deployed and configured!