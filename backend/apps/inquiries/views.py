from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Inquiry
from .serializers import InquirySerializer
from apps.catalog.services import ProductService


class InquiryListCreateView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        inquiries = Inquiry.objects.select_related('product')[:50]
        return Response(InquirySerializer(inquiries, many=True).data)

    def post(self, request):
        ProductService.ensure_demo_data()
        serializer = InquirySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        inquiry = serializer.save()
        return Response(
            {
                'success': True,
                'message': 'Inquiry received. The vendor can now follow up with the buyer.',
                'data': InquirySerializer(inquiry).data,
            },
            status=status.HTTP_201_CREATED,
        )
