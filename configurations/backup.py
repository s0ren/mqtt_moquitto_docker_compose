#!/usr/bin/env python3
"""backup.py - Backup system config files to git repo

Usage:
    sudo python3 backup.py

Description:
    Scans the current directory structure and backs up corresponding system files.
    For each file found in the repo (e.g., ./etc/nginx/nginx.conf), this script
    will copy the corresponding system file (/etc/nginx/nginx.conf) to the repo.
    
    Files ending in .py and hidden files (starting with .) are skipped.

Examples:
    # Backup all config files
    sudo python3 backup.py
    
    # After backup, commit changes
    sudo python3 backup.py && git add . && git commit -m "Update configs"

Directory structure example:
    ./etc/nginx/nginx.conf    -> copies from /etc/nginx/nginx.conf
    ./etc/ssh/sshd_config     -> copies from /etc/ssh/sshd_config
    ./var/log/app/config.conf -> copies from /var/log/app/config.conf
"""
import shutil
from pathlib import Path

def backup_configs():
    repo_root = Path(__file__).parent
    backed_up = []
    errors = []
    
    # Find all files in repo (excluding hidden files and scripts)
    for repo_file in repo_root.rglob('*'):
        if not repo_file.is_file():
            continue
        if repo_file.name.startswith('.') or repo_file.suffix == '.py':
            continue
            
        # Calculate system path: ./etc/nginx/nginx.conf -> /etc/nginx/nginx.conf
        rel_path = repo_file.relative_to(repo_root)
        system_file = Path('/') / rel_path
        
        if not system_file.exists():
            print(f"⚠️  System file not found: {system_file}")
            continue
            
        try:
            shutil.copy2(system_file, repo_file)
            backed_up.append(str(system_file))
            print(f"✓ Backed up: {system_file}")
        except PermissionError:
            errors.append(f"Permission denied: {system_file}")
            print(f"✗ Permission denied: {system_file}")
        except Exception as e:
            errors.append(f"{system_file}: {e}")
            print(f"✗ Error with {system_file}: {e}")
    
    print(f"\n{'='*50}")
    print(f"Backed up {len(backed_up)} files")
    if errors:
        print(f"{len(errors)} errors occurred")
        
    return len(errors) == 0

if __name__ == '__main__':
    import sys
    
    # Show usage if --help is provided
    if '--help' in sys.argv or '-h' in sys.argv:
        print(__doc__)
        sys.exit(0)
    
    success = backup_configs()
    sys.exit(0 if success else 1)