from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from config.permission import IsVendorOrAdmin
from .services import KPIService
from .models import KPISnapshot


class KPIDashboardView(APIView):
    """
    Returns pre-computed KPI summary. Zero live aggregation.
    Vendors see their own data; admins see global data.
    """
    permission_classes = [IsVendorOrAdmin]

    def get(self, request):
        if request.user.is_staff:
            vendor_id = request.query_params.get('vendor_id')
        else:
            vendor = getattr(request.user, 'vendor_profile', None)
            vendor_id = str(vendor.id) if vendor else None

        data = KPIService.get_dashboard_summary(vendor_id=vendor_id)
        return Response(data)


class KPITimeSeriesView(APIView):
    """Returns raw snapshot rows for charting."""
    permission_classes = [IsVendorOrAdmin]

    def get(self, request):
        period_type = request.query_params.get('period_type', 'daily')
        metric = request.query_params.get('metric', 'revenue')
        dimension = request.query_params.get('dimension', 'overall')
        limit = min(int(request.query_params.get('limit', 30)), 365)

        qs = KPISnapshot.objects.filter(
            period_type=period_type,
            metric=metric,
            dimension=dimension,
        )

        if request.user.is_staff:
            dim_value = request.query_params.get('dimension_value', 'ALL')
        elif request.user.is_vendor:
            vendor = getattr(request.user, 'vendor_profile', None)
            dim_value = str(vendor.id) if vendor else 'ALL'
            qs = qs.filter(dimension='vendor')
        else:
            return Response({'error': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)

        qs = qs.filter(dimension_value=dim_value).order_by('-period_start')[:limit]

        data = [
            {
                'period_start': row.period_start.isoformat(),
                'value': str(row.value),
            }
            for row in reversed(list(qs))
        ]
        return Response({'results': data, 'metric': metric, 'period_type': period_type})