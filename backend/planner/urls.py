from rest_framework.routers import DefaultRouter

from .views import DailyGoalViewSet, RecommendationViewSet, RevisionTaskViewSet

router = DefaultRouter()
router.register("recommendations", RecommendationViewSet, basename="recommendation")
router.register("revision-tasks", RevisionTaskViewSet, basename="revisiontask")
router.register("daily-goals", DailyGoalViewSet, basename="dailygoal")

urlpatterns = router.urls
