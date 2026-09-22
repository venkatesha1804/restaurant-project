# Base_App/management/commands/backup_db.py
import shutil
from pathlib import Path
from datetime import datetime
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Creates a timestamped backup of the SQLite database'

    def handle(self, *args, **options):
        db_path = settings.BASE_DIR / 'db.sqlite3'
        if not db_path.exists():
            self.stdout.write(self.style.ERROR('db.sqlite3 not found — are you using SQLite?'))
            return

        backup_dir = settings.BASE_DIR / 'backups'
        backup_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime('%Y-%m-%d_%H%M%S')
        backup_path = backup_dir / f'backup_{timestamp}.sqlite3'

        shutil.copy2(db_path, backup_path)
        self.stdout.write(self.style.SUCCESS(f'✓ Backup created: {backup_path}'))

        # keep only the last 10 backups
        backups = sorted(backup_dir.glob('backup_*.sqlite3'), key=lambda p: p.stat().st_mtime)
        for old_backup in backups[:-10]:
            old_backup.unlink()
            self.stdout.write(f'Removed old backup: {old_backup.name}')