#!/usr/bin/env python3
"""restore.py - Restore config files from git repo to system

Usage:
    sudo python3 restore.py [OPTIONS]

Options:
    --dry-run    Show what would be restored without making changes
    -h, --help   Show this help message

Description:
    Restores system config files from the git repo structure. For each file
    found in the repo (e.g., ./etc/nginx/nginx.conf), this script will copy
    it to the corresponding system location (/etc/nginx/nginx.conf).
    
    Before overwriting, existing system files are backed up with a .bak extension.
    A confirmation prompt is shown before making changes (unless --dry-run).
    
    Files ending in .py and hidden files (starting with .) are skipped.

Examples:
    # Preview what would be restored (recommended first step)
    sudo python3 restore.py --dry-run
    
    # Actually restore the files
    sudo python3 restore.py
    
    # Restore without this script's backup (not recommended)
    # Note: Original files are still backed up as .bak

Safety:
    - Shows confirmation prompt before restoring
    - Creates .bak files before overwriting existing files
    - Use --dry-run to preview changes first

Directory structure example:
    ./etc/nginx/nginx.conf    -> restores to /etc/nginx/nginx.conf
    ./etc/ssh/sshd_config     -> restores to /etc/ssh/sshd_config
    ./var/log/app/config.conf -> restores to /var/log/app/config.conf
"""
import shutil
from pathlib import Path

def restore_configs(dry_run=False):
    repo_root = Path(__file__).parent
    restored = []
    errors = []
    
    # Find all files in repo
    for repo_file in repo_root.rglob('*'):
        if not repo_file.is_file():
            continue
        if repo_file.name.startswith('.') or repo_file.suffix == '.py':
            continue
            
        # Calculate system path
        rel_path = repo_file.relative_to(repo_root)
        system_file = Path('/') / rel_path
        
        if dry_run:
            print(f"Would restore: {repo_file} -> {system_file}")
            continue
        
        try:
            # Create parent directories if needed
            system_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Backup existing file before overwriting
            if system_file.exists():
                backup = system_file.with_suffix(system_file.suffix + '.bak')
                shutil.copy2(system_file, backup)
                print(f"  Backed up existing to: {backup}")
            
            # Restore the file
            shutil.copy2(repo_file, system_file)
            restored.append(str(system_file))
            print(f"✓ Restored: {system_file}")
            
        except PermissionError:
            errors.append(f"Permission denied: {system_file}")
            print(f"✗ Permission denied: {system_file}")
        except Exception as e:
            errors.append(f"{system_file}: {e}")
            print(f"✗ Error with {system_file}: {e}")
    
    print(f"\n{'='*50}")
    if dry_run:
        print("DRY RUN - no changes made")
    else:
        print(f"Restored {len(restored)} files")
        if errors:
            print(f"{len(errors)} errors occurred")
        
    return len(errors) == 0

if __name__ == '__main__':
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Restore config files from git repo to system',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument('--dry-run', action='store_true', 
                       help='Show what would be restored without making changes')
    args = parser.parse_args()
    
    if not args.dry_run:
        response = input("This will overwrite system files. Continue? [y/N] ")
        if response.lower() != 'y':
            print("Aborted.")
            sys.exit(1)
    
    success = restore_configs(dry_run=args.dry_run)
    sys.exit(0 if success else 1)