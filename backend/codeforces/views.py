from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView

from planner.models import Recommendation

from . import analytics
from .serializers import SyncRequestSerializer
from .services import CodeforcesError, sync_user


class SyncView(APIView):
    """Fetch fresh data from Codeforces for the given handle and store it."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = SyncRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        handle = serializer.validated_data["handle"].strip()
        try:
            summary = sync_user(request.user, handle)
        except CodeforcesError as exc:
            return Response(
                {"detail": str(exc)}, status=status.HTTP_502_BAD_GATEWAY
            )
        return Response(summary, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def overview(request):
    return Response(analytics.overview_stats(request.user))


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def rating(request):
    return Response(analytics.rating_analytics(request.user))


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def contests(request):
    return Response(analytics.contest_analytics(request.user))


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def topics(request):
    return Response(analytics.topic_analysis(request.user))


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def weaknesses(request):
    return Response(analytics.detect_weaknesses(request.user))


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def recommend(request):
    """Generate recommendations from current weaknesses and store history."""
    recs = analytics.generate_recommendations(request.user)
    for r in recs:
        Recommendation.objects.create(
            user=request.user, topic=r["topic"], message=r["message"]
        )
    return Response(recs, status=status.HTTP_201_CREATED)
