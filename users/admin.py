from django.contrib import admin

from .models import Viewer


@admin.register(Viewer)
class ViewerAdmin(admin.ModelAdmin):
    list_display = ('user',)
    search_fields = ('user__username',)