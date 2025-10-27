import tarfile
import os

# List all files to include
files_to_include = []

# Python files
for f in os.listdir('.'):
    if f.endswith('.py') and not f.startswith('create_deployment'):
        files_to_include.append(f)

# Requirements
files_to_include.append('deploy_requirements.txt')

# Templates directory
for root, dirs, files in os.walk('templates'):
    for file in files:
        files_to_include.append(os.path.join(root, file))

# Static directory
for root, dirs, files in os.walk('static'):
    for file in files:
        files_to_include.append(os.path.join(root, file))

# Create tarball
with tarfile.open('lux-complete-deploy.tar.gz', 'w:gz') as tar:
    for f in files_to_include:
        if os.path.exists(f):
            tar.add(f)
            print(f"Added: {f}")

print(f"\nTotal files added: {len(files_to_include)}")
print(f"Package size: {os.path.getsize('lux-complete-deploy.tar.gz')} bytes")
