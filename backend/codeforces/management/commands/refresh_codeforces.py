"""
Periodic refresh: re-sync every profile that has a Codeforces handle.

Run manually:        python manage.py refresh_codeforces
Schedule (cron):     0 */6 * * *  python manage.py refresh_codeforces
(or use Windows Task Scheduler). Keeps stored analytics reasonably fresh
without any always-on background worker.
"""
import time

from django.core.management.base import BaseCommand

from accounts.models import Profile
from codeforces.services import CodeforcesError, sync_user


class Command(BaseCommand):
    help = "Re-sync Codeforces data for all users with a saved handle."

    def handle(self, *args, **options):
        profiles = Profile.objects.exclude(codeforces_handle="")
        self.stdout.write(f"Refreshing {profiles.count()} profile(s)...")
        for profile in profiles:
            handle = profile.codeforces_handle
            try:
                summary = sync_user(profile.user, handle)
                self.stdout.write(self.style.SUCCESS(
                    f"  {handle}: {summary['problems_synced']} problems"))
            except CodeforcesError as exc:
                self.stdout.write(self.style.ERROR(f"  {handle}: {exc}"))
            time.sleep(1)  # be polite to the public API
        self.stdout.write(self.style.SUCCESS("Done."))
