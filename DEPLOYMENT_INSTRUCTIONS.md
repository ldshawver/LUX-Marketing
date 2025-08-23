# LUX Email Marketing Bot - VPS Deployment Fix

## Quick Fix for Your VPS Issue

Your VPS is failing because of a corrupted `routes.py` file with duplicate route definitions. This package contains the fixed files.

## Files to Download from Replit:

1. **lux-email-app-fixed.tar.gz** - Complete fixed application package  
2. **vps-fix-deployment.sh** - Automated deployment script  

## Step-by-Step Fix:

### 1. Download Files
- In Replit file browser, right-click each file → Download
- Save both files to the same folder on your computer

### 2. Run Deployment Script
```bash
chmod +x vps-fix-deployment.sh
./vps-fix-deployment.sh
```

### 3. What the Script Does:
- Connects to your VPS at 194.195.92.52
- Backs up your current installation  
- Replaces corrupted files with fixed versions
- Restarts the service properly
- Tests both backend (port 5000) and domain (HTTPS)

### 4. Expected Result:
```
✅ Backend is responding!
✅ Domain is accessible via HTTPS!
```

## After Successful Deployment:

🌐 **Access your app:** https://lux.lucifercruz.com  
🔐 **Login:** admin / admin123  
🔧 **Configure:** Add Microsoft Graph API and OpenAI keys  

## If You Need Help:

Check service status:
```bash
ssh root@194.195.92.52 'systemctl status lux'
```

View logs:
```bash  
ssh root@194.195.92.52 'journalctl -u lux -f'
```

The deployment script will automatically fix the route conflict error that's preventing your app from starting.