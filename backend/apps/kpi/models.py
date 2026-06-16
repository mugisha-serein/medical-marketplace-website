import uuid
from django.db import models


class KPISnapshot(models.Model):
    """
    Denormalized time-series table.
    Each row = one KPI metric for one time period and one dimension value.
    e.g. period_type='daily', dimension='category', dimension_value='imaging', metric='revenue', value=150000.00
    """
    class PeriodType(models.TextChoices):
        FIFTEEN_MIN = '15min', '15 Minutes'
        HOURLY = 'hourly', 'Hourly'
        DAILY = 'daily', 'Daily'
        WEEKLY = 'weekly', 'Weekly'
        MONTHLY = 'monthly', 'Monthly'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    period_start = models.DateTimeField(db_index=True)
    period_type = models.CharField(max_length=10, choices=PeriodType.choices, db_index=True)
    dimension = models.CharField(max_length=50, db_index=True,
                                  help_text='e.g. overall, category, vendor, product')
    dimension_value = models.CharField(max_length=255, db_index=True,
                                        help_text='e.g. imaging, vendor-uuid, product-uuid, ALL')
    metric = models.CharField(max_length=50, db_index=True,
                               help_text='e.g. revenue, orders, units_sold, avg_order_value')
    value = models.DecimalField(max_digits=20, decimal_places=4)
    computed_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'kpi_snapshot'
        unique_together = [('period_start', 'period_type', 'dimension', 'dimension_value', 'metric')]
        indexes = [
            models.Index(
                fields=['period_start', 'period_type', 'dimension', 'dimension_value'],
                name='kpi_snapshot_lookup',
            ),
        ]

    def __str__(self):
        return f'{self.period_type} | {self.dimension}:{self.dimension_value} | {self.metric}={self.value}'