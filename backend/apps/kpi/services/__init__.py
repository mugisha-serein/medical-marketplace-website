import logging
from decimal import Decimal
from datetime import datetime, timedelta, date
from django.core.cache import cache
from django.db.models import Sum, Count, Avg
from django.utils import timezone
from django.conf import settings

from apps.kpi.models import KPISnapshot

logger = logging.getLogger(__name__)
KPI_CACHE_TTL = getattr(settings, 'KPI_SNAPSHOT_CACHE_TTL', 300)

# Redis key patterns for real-time counters (incremented on order.placed)
RT_ORDERS_KEY = 'kpi:rt:orders:{date}'
RT_REVENUE_KEY = 'kpi:rt:revenue:{date}'


class KPIService:

    @staticmethod
    def get_dashboard_summary(vendor_id: str = None) -> dict:
        """
        Returns combined snapshot + real-time data for the KPI dashboard.
        Zero aggregation queries in the request cycle — reads from KPISnapshot + Redis.
        """
        today_str = date.today().isoformat()
        cache_key = f'kpi:summary:{vendor_id or "global"}:{today_str}'
        cached = cache.get(cache_key)
        if cached:
            return cached

        data = {}

        # Real-time today counters from Redis
        rt_orders = cache.get(RT_ORDERS_KEY.format(date=today_str)) or 0
        rt_revenue = cache.get(RT_REVENUE_KEY.format(date=today_str)) or '0'
        data['today'] = {
            'orders': int(rt_orders),
            'revenue': str(rt_revenue),
        }

        # Recent snapshot data
        now = timezone.now()
        thirty_days_ago = now - timedelta(days=30)

        base_qs = KPISnapshot.objects.filter(
            period_type=KPISnapshot.PeriodType.DAILY,
            period_start__gte=thirty_days_ago,
        )
        if vendor_id:
            vendor_qs = base_qs.filter(dimension='vendor', dimension_value=str(vendor_id))
        else:
            vendor_qs = base_qs.filter(dimension='overall', dimension_value='ALL')

        # Last 30 days totals
        totals = vendor_qs.values('metric').annotate(total=Sum('value'))
        totals_map = {row['metric']: row['total'] for row in totals}

        data['last_30_days'] = {
            'revenue': str(totals_map.get('revenue', 0)),
            'orders': int(totals_map.get('orders', 0) or 0),
            'units_sold': int(totals_map.get('units_sold', 0) or 0),
            'avg_order_value': str(totals_map.get('avg_order_value', 0) or 0),
        }

        # Top products by units sold (last 30 days)
        top_products_qs = base_qs.filter(
            dimension='product', metric='units_sold'
        ).order_by('-value')[:10]

        data['top_products'] = [
            {'product_id': row.dimension_value, 'units_sold': int(row.value)}
            for row in top_products_qs
        ]

        # Revenue by category (last 30 days)
        by_category_qs = base_qs.filter(
            dimension='category', metric='revenue'
        ).values('dimension_value').annotate(total=Sum('value')).order_by('-total')[:10]

        data['revenue_by_category'] = [
            {'category': row['dimension_value'], 'revenue': str(row['total'])}
            for row in by_category_qs
        ]

        cache.set(cache_key, data, KPI_CACHE_TTL)
        return data

    @staticmethod
    def increment_realtime(order_total: Decimal, order_date: str):
        """Called from Celery task after order placement. Increments Redis counters."""
        orders_key = RT_ORDERS_KEY.format(date=order_date)
        revenue_key = RT_REVENUE_KEY.format(date=order_date)

        cache.incr(orders_key)  # atomic INCR
        # Redis doesn't natively support decimal INCR; store as string and accumulate
        current = Decimal(str(cache.get(revenue_key) or '0'))
        cache.set(revenue_key, str(current + order_total), 86400 * 2)  # 2-day TTL
        # Set TTL on orders key if first order of the day
        cache.expire(orders_key, 86400 * 2)

    @staticmethod
    def compute_snapshot(period_type: str, period_start: datetime):
        """
        Computes and upserts KPISnapshot rows for the given period.
        Called by Celery beat tasks.
        """
        from apps.orders.models import Order, OrderItem
        from apps.catalog.models import Category

        period_end = period_start + KPIService._period_delta(period_type)
        orders = Order.objects.filter(
            created_at__gte=period_start,
            created_at__lt=period_end,
            status__in=[
                Order.Status.CONFIRMED,
                Order.Status.PROCESSING,
                Order.Status.SHIPPED,
                Order.Status.DELIVERED,
            ],
        )

        # -- Overall metrics
        agg = orders.aggregate(
            total_revenue=Sum('total_amount'),
            total_orders=Count('id'),
            avg_order_value=Avg('total_amount'),
        )
        units = OrderItem.objects.filter(order__in=orders).aggregate(
            total_units=Sum('quantity')
        )

        KPIService._upsert(period_start, period_type, 'overall', 'ALL', 'revenue',
                           agg['total_revenue'] or 0)
        KPIService._upsert(period_start, period_type, 'overall', 'ALL', 'orders',
                           agg['total_orders'] or 0)
        KPIService._upsert(period_start, period_type, 'overall', 'ALL', 'units_sold',
                           units['total_units'] or 0)
        KPIService._upsert(period_start, period_type, 'overall', 'ALL', 'avg_order_value',
                           agg['avg_order_value'] or 0)

        # -- Per-vendor metrics
        vendor_agg = orders.values('items__vendor_id').annotate(
            revenue=Sum('items__subtotal'),
            order_count=Count('id', distinct=True),
            units=Sum('items__quantity'),
        )
        for row in vendor_agg:
            vid = str(row['items__vendor_id'] or 'unknown')
            KPIService._upsert(period_start, period_type, 'vendor', vid, 'revenue', row['revenue'] or 0)
            KPIService._upsert(period_start, period_type, 'vendor', vid, 'orders', row['order_count'] or 0)
            KPIService._upsert(period_start, period_type, 'vendor', vid, 'units_sold', row['units'] or 0)

        # -- Per-category metrics
        cat_agg = OrderItem.objects.filter(order__in=orders).values(
            'product__category__name'
        ).annotate(revenue=Sum('subtotal'), units=Sum('quantity'))
        for row in cat_agg:
            cat = row['product__category__name'] or 'unknown'
            KPIService._upsert(period_start, period_type, 'category', cat, 'revenue', row['revenue'] or 0)
            KPIService._upsert(period_start, period_type, 'category', cat, 'units_sold', row['units'] or 0)

        # -- Per-product metrics
        prod_agg = OrderItem.objects.filter(order__in=orders).values(
            'product_id'
        ).annotate(units=Sum('quantity'), revenue=Sum('subtotal'))
        for row in prod_agg:
            pid = str(row['product_id'] or 'unknown')
            KPIService._upsert(period_start, period_type, 'product', pid, 'units_sold', row['units'] or 0)
            KPIService._upsert(period_start, period_type, 'product', pid, 'revenue', row['revenue'] or 0)

        # Invalidate dashboard cache
        cache.delete_pattern('medequip:kpi:summary:*')
        logger.info('KPI snapshot computed', extra={'period_type': period_type, 'period_start': str(period_start)})

    @staticmethod
    def _upsert(period_start, period_type, dimension, dimension_value, metric, value):
        KPISnapshot.objects.update_or_create(
            period_start=period_start,
            period_type=period_type,
            dimension=dimension,
            dimension_value=str(dimension_value),
            metric=metric,
            defaults={'value': Decimal(str(value))},
        )

    @staticmethod
    def _period_delta(period_type: str) -> timedelta:
        return {
            '15min': timedelta(minutes=15),
            'hourly': timedelta(hours=1),
            'daily': timedelta(days=1),
            'weekly': timedelta(weeks=1),
            'monthly': timedelta(days=30),
        }.get(period_type, timedelta(hours=1))
