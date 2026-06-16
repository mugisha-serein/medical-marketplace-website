from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from apps.accounts import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='auth-register'),
    path('token/', views.LoginView.as_view(), name='auth-token'),
    path('token/refresh/', TokenRefreshView.as_view(), name='auth-token-refresh'),
    path('logout/', views.LogoutView.as_view(), name='auth-logout'),
    path('me/', views.MeView.as_view(), name='auth-me'),
    path('me/change-password/', views.ChangePasswordView.as_view(), name='auth-change-password'),
    path('me/vendor-profile/', views.VendorProfileView.as_view(), name='auth-vendor-profile'),
    path('me/customer-profile/', views.CustomerProfileView.as_view(), name='auth-customer-profile'),
]
