from django.contrib.auth.models import User
from django.db import models


class Recommendation(models.Model):
    """A deterministic, rule-based suggestion stored as history."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="recommendations"
    )
    topic = models.CharField(max_length=100)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username}: {self.topic}"


class RevisionTask(models.Model):
    class Priority(models.TextChoices):
        LOW = "LOW", "Low"
        MEDIUM = "MEDIUM", "Medium"
        HIGH = "HIGH", "High"

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        COMPLETED = "COMPLETED", "Completed"

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="revision_tasks"
    )
    topic = models.CharField(max_length=100)
    priority = models.CharField(
        max_length=10, choices=Priority.choices, default=Priority.MEDIUM
    )
    target_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=12, choices=Status.choices, default=Status.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["target_date", "-priority"]

    def __str__(self):
        return f"{self.topic} ({self.status})"


class DailyGoal(models.Model):
    class GoalType(models.TextChoices):
        SOLVE_PROBLEMS = "SOLVE_PROBLEMS", "Solve Problems"
        CONTEST = "CONTEST", "Participate in Contest"

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="daily_goals"
    )
    description = models.CharField(max_length=255)
    goal_type = models.CharField(
        max_length=20, choices=GoalType.choices, default=GoalType.SOLVE_PROBLEMS
    )
    topic = models.CharField(max_length=100, blank=True)
    target_count = models.IntegerField(default=1)
    completed_count = models.IntegerField(default=0)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date"]

    @property
    def completion_percentage(self):
        if self.target_count <= 0:
            return 0
        return min(100, round(self.completed_count / self.target_count * 100))

    @property
    def is_complete(self):
        return self.completed_count >= self.target_count

    def __str__(self):
        return f"{self.description} ({self.completed_count}/{self.target_count})"
