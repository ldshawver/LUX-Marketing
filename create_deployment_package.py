#!/usr/bin/env python3
import tarfile
import os
from datetime import datetime

def create_deployment_package():
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    filename = f'lux-deployment-{timestamp}.tar.gz'
    
    exclude_patterns = [
        '*.tar.gz', 'instance', 'tests', '__pycache__', '*.pyc', 
        '.git', 'attached_assets', 'email_marketing.db', '*.db'
    ]
    
    include_items = [
        'ai_agent.py', 'app.py', 'auth.py', 'email_service.py',
        'main.py', 'models.py', 'routes.py', 'scheduler.py',
        'seo_service.py', 'sms_service.py', 'tracking.py',
        'user_management.py', 'utils.py', 'woocommerce_service.py',
        'wsgi.py', 'gunicorn.conf.py', 'health_check.py',
        'templates', 'static', 'lux', 'scripts',
        'README.md', 'DEPLOYMENT_GUIDE.md', 'WOOCOMMERCE_INTEGRATION.md',
        'requirements.txt', 'deploy_requirements.txt'
    ]
    
    def should_exclude(name):
        for pattern in exclude_patterns:
            if pattern.startswith('*'):
                if name.endswith(pattern[1:]):
                    return True
            elif name == pattern or name.startswith(pattern + '/'):
                return True
        return False
    
    with tarfile.open(filename, 'w:gz') as tar:
        for item in include_items:
            if os.path.exists(item):
                if os.path.isfile(item):
                    tar.add(item)
                    print(f"Added file: {item}")
                elif os.path.isdir(item):
                    for root, dirs, files in os.walk(item):
                        dirs[:] = [d for d in dirs if not should_exclude(d)]
                        
                        for file in files:
                            filepath = os.path.join(root, file)
                            if not should_exclude(file):
                                tar.add(filepath)
                                print(f"Added: {filepath}")
    
    size = os.path.getsize(filename)
    size_mb = size / (1024 * 1024)
    print(f"\n✓ Deployment package created: {filename}")
    print(f"✓ Size: {size_mb:.2f} MB")
    return filename

if __name__ == '__main__':
    create_deployment_package()
