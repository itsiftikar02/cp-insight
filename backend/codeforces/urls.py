from django.urls import path

from . import views

urlpatterns = [
    path("sync/", views.SyncView.as_view(), name="cf-sync"),
    path("analytics/overview/", views.overview, name="cf-overview"),
    path("analytics/rating/", views.rating, name="cf-rating"),
    path("analytics/contests/", views.contests, name="cf-contests"),
    path("analytics/topics/", views.topics, name="cf-topics"),
    path("analytics/weaknesses/", views.weaknesses, name="cf-weaknesses"),
    path("recommend/", views.recommend, name="cf-recommend"),
]
