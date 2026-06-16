from django.contrib import admin
from .models import KPISnapshot


@admin.register(KPISnapshot)
class KPISnapshotAdmin(admin.ModelAdmin):
    list_display = ['period_start', 'period_type', 'dimension', 'dimension_value', 'metric', 'value', 'computed_at']
    list_filter = ['period_type', 'dimension', 'metric']
    ordering = ['-period_start']
    readonly_fields = ['computed_at']