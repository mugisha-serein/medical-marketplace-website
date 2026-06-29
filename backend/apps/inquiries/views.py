from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from config.permission import IsVendorOrAdmin
from .models import Inquiry
from .serializers import InquirySerializer


class InquiryListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == 'POST':
            return [AllowAny()]
        return [IsVendorOrAdmin()]

    def get(self, request):
        queryset = Inquiry.objects.select_related('product')[:50]
        serializer = InquirySerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = InquirySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=201)
