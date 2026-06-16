from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from django.db import transaction
from .models import VendorProfile, CustomerProfile

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Add role and name to JWT payload."""
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.get_role()
        token['email'] = user.email
        token['full_name'] = user.full_name
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['role'] = self.user.get_role()
        data['email'] = self.user.email
        data['full_name'] = self.user.full_name
        return data


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(min_length=8, write_only=True)
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    role = serializers.ChoiceField(choices=['customer', 'vendor'])
    # Vendor-specific
    company_name = serializers.CharField(max_length=255, required=False)
    company_registration = serializers.CharField(max_length=100, required=False, allow_blank=True)
    phone = serializers.CharField(max_length=30, required=False, allow_blank=True)

    def validate_email(self, value):
        if User.objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError('An account with this email already exists.')
        return value.lower()

    def validate(self, attrs):
        if attrs['role'] == 'vendor' and not attrs.get('company_name'):
            raise serializers.ValidationError({'company_name': 'Company name is required for vendor accounts.'})
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        role = validated_data.pop('role')
        company_name = validated_data.pop('company_name', '')
        company_registration = validated_data.pop('company_registration', '')
        phone = validated_data.pop('phone', '')

        is_vendor = role == 'vendor'
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            is_vendor=is_vendor,
            is_active=True,  # set to False + verify email in production
        )

        if is_vendor:
            VendorProfile.objects.create(
                user=user,
                company_name=company_name,
                company_registration=company_registration,
                phone=phone,
            )
        else:
            CustomerProfile.objects.create(user=user, phone=phone)

        return user


class UserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    vendor_profile = serializers.SerializerMethodField()
    customer_profile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'role', 'is_active', 'email_verified', 'date_joined',
            'vendor_profile', 'customer_profile',
        ]
        read_only_fields = fields

    def get_role(self, obj):
        return obj.get_role()

    def get_vendor_profile(self, obj):
        if hasattr(obj, 'vendor_profile'):
            vp = obj.vendor_profile
            return {
                'id': str(vp.id),
                'company_name': vp.company_name,
                'is_verified': vp.is_verified,
                'phone': vp.phone,
            }
        return None

    def get_customer_profile(self, obj):
        if hasattr(obj, 'customer_profile'):
            cp = obj.customer_profile
            return {
                'id': str(cp.id),
                'organization': cp.organization,
                'phone': cp.phone,
            }
        return None


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(min_length=8, write_only=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Current password is incorrect.')
        return value


class UpdateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name']


class VendorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorProfile
        exclude = ['user']
        read_only_fields = ['id', 'is_verified', 'created_at', 'updated_at']


class CustomerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerProfile
        exclude = ['user']
        read_only_fields = ['id', 'created_at', 'updated_at']