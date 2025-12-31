#!/usr/bin/env python3
"""
SymptoMap Database Backup System
Automated backup with rotation - keeps last 30 backups
Run manually or schedule via cron/Task Scheduler

Usage:
    python scripts/backup.py

Scheduling:
    # Mac/Linux (crontab -e):
    0 */6 * * * /usr/bin/python3 /path/to/scripts/backup.py

    # Windows Task Scheduler:
    schtasks /create /tn "SymptoMap Backup" /tr "python C:\path\to\scripts\backup.py" /sc hourly /mo 6
"""

import shutil
import os
from datetime import datetime
from pathlib import Path
import sys

# Configuration
BACKUP_DIR = Path("backups")
DATABASE_FILE = "symptomap.db"
KEEP_BACKUPS = 30  # Number of backups to retain
LOG_FILE = "logs/backup.log"

def log_message(message):
    """Log message to file and console"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] {message}"
    
    print(log_entry)
    
    # Ensure logs directory exists
    Path("logs").mkdir(exist_ok=True)
    
    with open(LOG_FILE, 'a') as f:
        f.write(log_entry + '\n')

def check_database_exists():
    """Verify database file exists"""
    if not Path(DATABASE_FILE).exists():
        log_message(f"❌ ERROR: Database file not found: {DATABASE_FILE}")
        return False
    return True

def create_backup():
    """Create timestamped backup of database"""
    try:
        # Create backup directory if it doesn't exist
        BACKUP_DIR.mkdir(exist_ok=True)
        
        # Generate timestamp for backup filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"symptomap_backup_{timestamp}.db"
        backup_path = BACKUP_DIR / backup_filename
        
        # Get database size
        db_size = Path(DATABASE_FILE).stat().st_size
        db_size_mb = db_size / (1024 * 1024)
        
        # Copy database file
        shutil.copy2(DATABASE_FILE, backup_path)
        
        # Verify backup was created successfully
        if backup_path.exists():
            backup_size = backup_path.stat().st_size
            if backup_size == db_size:
                log_message(f"✅ Backup created successfully: {backup_filename}")
                log_message(f"   Size: {db_size_mb:.2f} MB")
                return backup_path
            else:
                log_message(f"❌ ERROR: Backup size mismatch!")
                backup_path.unlink()  # Delete corrupted backup
                return None
        else:
            log_message(f"❌ ERROR: Backup file was not created")
            return None
            
    except Exception as e:
        log_message(f"❌ ERROR creating backup: {e}")
        return None

def cleanup_old_backups():
    """Remove old backups, keeping only the last N"""
    try:
        # Get all backup files, sorted by modification time (oldest first)
        backups = sorted(
            BACKUP_DIR.glob("symptomap_backup_*.db"),
            key=lambda p: p.stat().st_mtime
        )
        
        total_backups = len(backups)
        
        if total_backups > KEEP_BACKUPS:
            # Calculate how many to delete
            to_delete = total_backups - KEEP_BACKUPS
            
            # Delete oldest backups
            for old_backup in backups[:to_delete]:
                old_backup.unlink()
                log_message(f"🗑️  Removed old backup: {old_backup.name}")
            
            log_message(f"   Kept {KEEP_BACKUPS} most recent backups")
        else:
            log_message(f"   Total backups: {total_backups} (within limit of {KEEP_BACKUPS})")
            
    except Exception as e:
        log_message(f"⚠️  WARNING: Error during cleanup: {e}")

def get_backup_statistics():
    """Display backup statistics"""
    try:
        backups = list(BACKUP_DIR.glob("symptomap_backup_*.db"))
        
        if not backups:
            log_message("   No previous backups found")
            return
        
        total_size = sum(b.stat().st_size for b in backups)
        total_size_mb = total_size / (1024 * 1024)
        
        # Get oldest and newest
        backups_sorted = sorted(backups, key=lambda p: p.stat().st_mtime)
        oldest = backups_sorted[0]
        newest = backups_sorted[-1]
        
        oldest_date = datetime.fromtimestamp(oldest.stat().st_mtime)
        newest_date = datetime.fromtimestamp(newest.stat().st_mtime)
        
        log_message(f"")
        log_message(f"📊 Backup Statistics:")
        log_message(f"   Total backups: {len(backups)}")
        log_message(f"   Total size: {total_size_mb:.2f} MB")
        log_message(f"   Oldest: {oldest_date.strftime('%Y-%m-%d %H:%M:%S')}")
        log_message(f"   Newest: {newest_date.strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Exception as e:
        log_message(f"⚠️  WARNING: Error getting statistics: {e}")

def main():
    """Main backup execution"""
    log_message("=" * 60)
    log_message("🔄 Starting SymptoMap Database Backup")
    log_message("=" * 60)
    
    # Check if database exists
    if not check_database_exists():
        sys.exit(1)
    
    # Create backup
    backup_path = create_backup()
    
    if backup_path:
        # Cleanup old backups
        cleanup_old_backups()
        
        # Show statistics
        get_backup_statistics()
        
        log_message("=" * 60)
        log_message("✅ Backup process completed successfully")
        log_message("=" * 60)
        return 0
    else:
        log_message("=" * 60)
        log_message("❌ Backup process failed")
        log_message("=" * 60)
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
