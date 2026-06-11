from rest_framework import serializers

from .models import DailyGoal, Recommendation, RevisionTask


class RecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recommendation
        fields = ("id", "topic", "message", "created_at")
        read_only_fields = fields


class RevisionTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = RevisionTask
        fields = (
            "id", "topic", "priority", "target_date",
            "status", "created_at", "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class DailyGoalSerializer(serializers.ModelSerializer):
    completion_percentage = serializers.IntegerField(read_only=True)
    is_complete = serializers.BooleanField(read_only=True)

    class Meta:
        model = DailyGoal
        fields = (
            "id", "description", "goal_type", "topic",
            "target_count", "completed_count", "date",
            "completion_percentage", "is_complete", "created_at",
        )
        read_only_fields = ("id", "created_at")
