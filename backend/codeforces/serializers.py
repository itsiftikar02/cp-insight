from rest_framework import serializers

from .models import CodeforcesContest, CodeforcesProblem, UserSolvedProblem


class ContestSerializer(serializers.ModelSerializer):
    rating_change = serializers.IntegerField(read_only=True)

    class Meta:
        model = CodeforcesContest
        fields = (
            "contest_id", "contest_name", "rank",
            "old_rating", "new_rating", "rating_change", "rating_update_time",
        )


class ProblemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodeforcesProblem
        fields = ("contest_id", "index", "name", "rating", "tags")


class SolvedProblemSerializer(serializers.ModelSerializer):
    problem = ProblemSerializer(read_only=True)

    class Meta:
        model = UserSolvedProblem
        fields = ("problem", "solved_at")


class SyncRequestSerializer(serializers.Serializer):
    handle = serializers.CharField(max_length=100)
