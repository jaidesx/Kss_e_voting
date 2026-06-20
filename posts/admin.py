from django.contrib import admin
from .models import Post, EligibleHouse, Election
from voting.models import Vote


class EligibleHouseInline(admin.TabularInline):
    model = EligibleHouse
    extra = 1
    verbose_name = 'Eligible House'
    verbose_name_plural = 'Eligible Houses (leave empty = open to all)'


@admin.register(Election)
class ElectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'is_demo', 'created_at')
    list_filter = ('is_active', 'is_demo')
    search_fields = ('title',)
    actions = ['reset_election_votes']

    @admin.action(description="Reset selected elections (delete all cast votes)")
    def reset_election_votes(self, request, queryset):
        deleted_count = 0
        for election in queryset:
            # Delete all votes associated with this election
            votes = Vote.objects.filter(post__election=election)
            count = votes.count()
            votes.delete()
            deleted_count += count
        self.message_user(request, f"Successfully reset {queryset.count()} election(s). Deleted {deleted_count} vote(s).")


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'election', 'description', 'eligible_houses_display')
    list_filter = ('election',)
    search_fields = ('title', 'description')
    inlines = [EligibleHouseInline]

    def eligible_houses_display(self, obj):
        houses = obj.eligible_houses.all()
        if not houses:
            return 'All Houses'
        return ', '.join(h.get_house_display() for h in houses)
    eligible_houses_display.short_description = 'Eligible Houses'

