from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    """Extra information attached one-to-one to Django's built-in User."""

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="profile"
    )
    name = models.CharField(max_length=150, blank=True)
    codeforces_handle = models.CharField(max_length=100, blank=True, db_index=True)
    current_rating = models.IntegerField(null=True, blank=True)
    max_rating = models.IntegerField(null=True, blank=True)

    last_synced_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile<{self.user.username}>"
