from django.urls import path

from apps.kpi import views

urlpatterns = [
    path('summary/', views.KPIDashboardView.as_view(), name='kpi-dashboard'),
    path('timeseries/', views.KPITimeSeriesView.as_view(), name='kpi-timeseries'),
]
