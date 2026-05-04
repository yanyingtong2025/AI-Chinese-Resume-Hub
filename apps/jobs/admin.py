from django.contrib import admin
from .models import Job, MatchResult, MatchWeightConfig, MatchingSession


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['title', 'hr_user', 'location', 'education_required', 'work_years_required', 'is_active', 'created_at']
    list_filter = ['is_active', 'education_required', 'created_at']
    search_fields = ['title', 'department', 'location']


@admin.register(MatchResult)
class MatchResultAdmin(admin.ModelAdmin):
    list_display = ['job', 'resume', 'match_score', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['job__title', 'resume__name']
    readonly_fields = ['match_score', 'match_analysis', 'education_score', 'experience_score', 'skills_score', 'created_at']


@admin.register(MatchWeightConfig)
class MatchWeightConfigAdmin(admin.ModelAdmin):
    list_display = ['job', 'education_weight', 'experience_weight', 'skills_weight', 'updated_at']
    list_filter = ['updated_at']


@admin.register(MatchingSession)
class MatchingSessionAdmin(admin.ModelAdmin):
    list_display = ['job', 'hr_user', 'total_resumes', 'matched_count', 'avg_score', 'created_at']
    list_filter = ['created_at']
    readonly_fields = ['created_at']