from django.contrib import admin

from .models import DailyGoal, Recommendation, RevisionTask

admin.site.register(DailyGoal)
admin.site.register(Recommendation)
admin.site.register(RevisionTask)
