from django.contrib import admin

from .models import (
    CodeforcesContest,
    CodeforcesProblem,
    TopicStatistics,
    UserSolvedProblem,
)

admin.site.register(CodeforcesContest)
admin.site.register(CodeforcesProblem)
admin.site.register(UserSolvedProblem)
admin.site.register(TopicStatistics)
