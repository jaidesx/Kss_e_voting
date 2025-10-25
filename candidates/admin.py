from django.contrib import admin
from .models import Candidate

@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ("name", "post", "_class", "stream")
    list_filter = ("post", "stream")
    search_fields = ("name", "slogan")
