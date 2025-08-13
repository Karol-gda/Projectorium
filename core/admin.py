from django.contrib import admin
from .models import Project, Milestone, SubTask


# Register your models here.
@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'end_date', 'budget_total', 'project_support')
    list_filter = ('project_support',)
    search_fields = ('title', 'description')

@admin.register(Milestone)
class MilestoneAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'status','start_date', 'due_date')
    list_filter = ('status', 'project')
    search_fields = ('title', 'description')
    filter_horizontal = ('responsible',)

@admin.register(SubTask)
class SubTaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'milestone', 'start_date', 'due_date')
    list_filter = ('milestone',)
    search_fields = ('title', 'description')
    filter_horizontal = ('assigned_to',)

