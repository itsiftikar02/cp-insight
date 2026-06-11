from django.contrib.auth.models import User
from django.db import models


class CodeforcesContest(models.Model):
    """A user's participation in one Codeforces contest (from user.rating)."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="contests"
    )
    contest_id = models.IntegerField()
    contest_name = models.CharField(max_length=255)
    rank = models.IntegerField()
    old_rating = models.IntegerField()
    new_rating = models.IntegerField()
    rating_update_time = models.DateTimeField()

    class Meta:
        unique_together = ("user", "contest_id")
        ordering = ["rating_update_time"]

    @property
    def rating_change(self):
        return self.new_rating - self.old_rating

    def __str__(self):
        return f"{self.user.username} @ {self.contest_name}"


class CodeforcesProblem(models.Model):
    """Global catalog of problems. Shared across all users."""

    contest_id = models.IntegerField(null=True, blank=True)
    index = models.CharField(max_length=10)
    name = models.CharField(max_length=255)
    rating = models.IntegerField(null=True, blank=True)
    tags = models.JSONField(default=list)  # e.g. ["dp", "greedy"]

    class Meta:
        unique_together = ("contest_id", "index")

    @property
    def problem_key(self):
        return f"{self.contest_id}{self.index}"

    def __str__(self):
        return f"{self.problem_key} - {self.name}"


class UserSolvedProblem(models.Model):
    """Links a user to a problem they solved (from user.status, verdict OK)."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="solved_problems"
    )
    problem = models.ForeignKey(
        CodeforcesProblem, on_delete=models.CASCADE, related_name="solvers"
    )
    solved_at = models.DateTimeField()

    class Meta:
        unique_together = ("user", "problem")
        ordering = ["-solved_at"]

    def __str__(self):
        return f"{self.user.username} solved {self.problem.problem_key}"


class TopicStatistics(models.Model):
    """Derived count of solved problems per tag, per user."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="topic_stats"
    )
    tag = models.CharField(max_length=100)
    solved_count = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "tag")
        ordering = ["-solved_count"]

    def __str__(self):
        return f"{self.user.username} - {self.tag}: {self.solved_count}"
