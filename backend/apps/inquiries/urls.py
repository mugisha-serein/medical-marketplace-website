from django.urls import path
from .views import InquiryListCreateView

urlpatterns = [
    path('', InquiryListCreateView.as_view(), name='inquiry-list-create'),
]
