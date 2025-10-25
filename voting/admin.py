from django.contrib import admin
from .models import Voter, Vote

@admin.register(Voter)
class VoterAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'student_name', 'student_class', 'house', 'has_voted')
    list_filter = ('student_class', 'house', 'has_voted')
    search_fields = ('student_name', 'student_id')


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('voter', 'candidate', 'timestamp')
    list_filter = ('candidate',)
    search_fields = ('voter__student_name', 'candidate__name')
