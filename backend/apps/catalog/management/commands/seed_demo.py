import os

from django.core.management.base import BaseCommand

from apps.accounts.models import User, VendorProfile
from apps.catalog.models import Category, Product
from apps.catalog.services import ProductService


class Command(BaseCommand):
    help = 'Seed the SQLite MVP with demo-only medical marketplace data.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--vendor-email',
            default=os.getenv('DEMO_VENDOR_EMAIL', 'vendor@medequip.local'),
            help='Demo-only vendor email. Override with DEMO_VENDOR_EMAIL or this option.',
        )
        parser.add_argument(
            '--vendor-password',
            default=os.getenv('DEMO_VENDOR_PASSWORD'),
            help=(
                'Optional demo-only vendor password. Override with DEMO_VENDOR_PASSWORD '
                'or this option. If omitted, the demo vendor cannot log in.'
            ),
        )

    def handle(self, *args, **options):
        vendor_email = options['vendor_email']
        vendor_password = options.get('vendor_password')

        self.stdout.write(self.style.WARNING('Seeding DEMO-ONLY vendor account and catalog data.'))

        vendor_user, _ = User.objects.get_or_create(
            email=vendor_email,
            defaults={
                'first_name': 'Demo',
                'last_name': 'Vendor',
                'is_active': True,
                'is_vendor': True,
                'email_verified': True,
            },
        )
        vendor_user.first_name = vendor_user.first_name or 'Demo'
        vendor_user.last_name = vendor_user.last_name or 'Vendor'
        vendor_user.is_active = True
        vendor_user.is_vendor = True
        vendor_user.email_verified = True

        if vendor_password:
            vendor_user.set_password(vendor_password)
            password_message = 'Demo vendor password was set from DEMO_VENDOR_PASSWORD/--vendor-password.'
        elif not vendor_user.has_usable_password():
            vendor_user.set_unusable_password()
            password_message = 'No demo vendor password was set; pass DEMO_VENDOR_PASSWORD or --vendor-password to enable login.'
        else:
            password_message = 'Existing demo vendor password was preserved.'
        vendor_user.save()

        vendor, _ = VendorProfile.objects.get_or_create(
            user=vendor_user,
            defaults={
                'company_name': 'Kigali MedSupply Co.',
                'description': 'Trusted supplier of clinic-ready medical equipment for hospitals and private practices.',
                'phone': '+250 788 000 111',
                'address': 'Kigali, Rwanda',
                'website': 'https://example.com',
                'is_verified': True,
            },
        )

        product_count_before = Product.objects.count()
        category_count_before = Category.objects.count()

        ProductService.ensure_demo_data(vendor)

        product_count_after = Product.objects.count()
        category_count_after = Category.objects.count()

        created_products = product_count_after - product_count_before
        created_categories = category_count_after - category_count_before

        self.stdout.write(self.style.WARNING(password_message))
        self.stdout.write(
            self.style.SUCCESS(
                'Demo data ready. '
                f'Vendor: {vendor_email}. '
                f'Products: {product_count_after} ({created_products:+d}), '
                f'Categories: {category_count_after} ({created_categories:+d}).'
            )
        )
