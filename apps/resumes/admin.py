from django.contrib import admin
from .models import Resume


@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'file_name', 'status', 'education', 'work_years', 'created_at']
    list_filter = ['status', 'education', 'created_at']
    search_fields = ['name', 'email', 'phone', 'school', 'major']
    readonly_fields = ['raw_text', 'parsed_data', 'created_at', 'updated_at']