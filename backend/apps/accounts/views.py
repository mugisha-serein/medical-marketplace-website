import secrets
from django.contrib.auth import get_user_model
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.throttling import ScopedRateThrottle

from .serializers import (
    RegisterSerializer, UserSerializer, ChangePasswordSerializer,
    UpdateProfileSerializer, VendorProfileSerializer, CustomerProfileSerializer,
    CustomTokenObtainPairSerializer,
)
from .models import VendorProfile, CustomerProfile
from apps.notification.tasks import send_welcome_email

User = get_user_model()


class AuthThrottle(ScopedRateThrottle):
    scope = 'auth'


class RegisterView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AuthThrottle]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        # Dispatch welcome email async
        send_welcome_email.delay(str(user.id))
        return Response(
            {'message': 'Account created successfully. Please check your email.', 'user_id': str(user.id)},
            status=status.HTTP_201_CREATED,
        )


class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]
    throttle_classes = [AuthThrottle]
    serializer_class = CustomTokenObtainPairSerializer


class TokenRefreshView(TokenRefreshView):
    permission_classes = [AllowAny]


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({'error': 'Refresh token required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': 'Logged out successfully.'}, status=status.HTTP_200_OK)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        serializer = UpdateProfileSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserSerializer(request.user).data)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save(update_fields=['password'])
        return Response({'message': 'Password changed successfully.'})


class VendorProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get_profile(self, user):
        try:
            return user.vendor_profile
        except VendorProfile.DoesNotExist:
            return None

    def get(self, request):
        profile = self.get_profile(request.user)
        if not profile:
            return Response({'error': 'Vendor profile not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(VendorProfileSerializer(profile).data)

    def patch(self, request):
        profile = self.get_profile(request.user)
        if not profile:
            return Response({'error': 'Vendor profile not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = VendorProfileSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class CustomerProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get_profile(self, user):
        try:
            return user.customer_profile
        except CustomerProfile.DoesNotExist:
            return None

    def get(self, request):
        profile = self.get_profile(request.user)
        if not profile:
            return Response({'error': 'Customer profile not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(CustomerProfileSerializer(profile).data)

    def patch(self, request):
        profile = self.get_profile(request.user)
        if not profile:
            return Response({'error': 'Customer profile not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = CustomerProfileSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
