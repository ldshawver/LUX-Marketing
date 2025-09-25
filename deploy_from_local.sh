# SSH into your VPS
ssh root@194.195.92.52

# Install dependencies
apt update
apt install -y python3 python3-pip python3-venv nginx postgresql postgresql-contrib

# Create application user and directories
useradd -m -s /bin/bash luxapp
mkdir -p /var/log/lux-marketing
chown -R luxapp:www-data /var/www/lux-marketing
chown luxapp:www-data /var/log/lux-marketing`