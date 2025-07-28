from django.contrib import admin
from .models import MLApp, PredictionLog

@admin.register(MLApp)
class MLAppAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(PredictionLog)
class PredictionLogAdmin(admin.ModelAdmin):
    list_display = ('ml_app', 'processing_time', 'created_at')
    list_filter = ('ml_app', 'created_at')
    readonly_fields = ('created_at',)
    list_per_page = 20
