from rest_framework import permissions, viewsets

from .models import DailyGoal, Recommendation, RevisionTask
from .serializers import (
    DailyGoalSerializer,
    RecommendationSerializer,
    RevisionTaskSerializer,
)


class OwnedModelViewSet(viewsets.ModelViewSet):
    """Base viewset that scopes every query to the logged-in user."""
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class RecommendationViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only history of generated recommendations."""
    queryset = Recommendation.objects.all()
    serializer_class = RecommendationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


class RevisionTaskViewSet(OwnedModelViewSet):
    queryset = RevisionTask.objects.all()
    serializer_class = RevisionTaskSerializer


class DailyGoalViewSet(OwnedModelViewSet):
    queryset = DailyGoal.objects.all()
    serializer_class = DailyGoalSerializer
