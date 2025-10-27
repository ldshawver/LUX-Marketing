import tarfile
import os

# Create comprehensive deployment package
files_and_dirs = []

# Python files at root
for f in os.listdir('.'):
    if f.endswith('.py') and os.path.isfile(f):
        files_and_dirs.append(f)

# Requirements
if os.path.exists('deploy_requirements.txt'):
    files_and_dirs.append('deploy_requirements.txt')

# Complete lux/ package directory
if os.path.exists('lux'):
    for root, dirs, files in os.walk('lux'):
        for file in files:
            path = os.path.join(root, file)
            files_and_dirs.append(path)

# Templates directory at root
if os.path.exists('templates'):
    for root, dirs, files in os.walk('templates'):
        for file in files:
            path = os.path.join(root, file)
            files_and_dirs.append(path)

# Static directory at root
if os.path.exists('static'):
    for root, dirs, files in os.walk('static'):
        for file in files:
            if not file.endswith('.tar.gz'):  # Skip old packages
                path = os.path.join(root, file)
                files_and_dirs.append(path)

# Create tarball
print("Creating complete deployment package...")
with tarfile.open('lux-complete-deploy.tar.gz', 'w:gz') as tar:
    for item in files_and_dirs:
        if os.path.exists(item):
            tar.add(item)
            print(f"Added: {item}")

size = os.path.getsize('lux-complete-deploy.tar.gz')
print(f"\n{'='*50}")
print(f"Package created: lux-complete-deploy.tar.gz")
print(f"Total items: {len(files_and_dirs)}")
print(f"Size: {size:,} bytes ({size/1024:.1f} KB)")
print(f"{'='*50}")
