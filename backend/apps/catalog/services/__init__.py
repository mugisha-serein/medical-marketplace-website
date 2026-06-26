from django.core.cache import cache
from django.db.models import Q
from django.utils.text import slugify
from apps.accounts.models import User, VendorProfile
from apps.catalog.models import Product, Category


class SearchService:
    @staticmethod
    def search(params: dict):
        qs = Product.objects.filter(is_active=True).select_related('vendor', 'category').prefetch_related('images', 'tags')
        q = (params.get('q') or '').strip()
        if q:
            qs = qs.filter(
                Q(name__icontains=q)
                | Q(short_description__icontains=q)
                | Q(description__icontains=q)
                | Q(manufacturer__icontains=q)
                | Q(model_number__icontains=q)
            )
        if params.get('category_slug'):
            qs = qs.filter(category__slug=params['category_slug'])
        if params.get('min_price') is not None:
            qs = qs.filter(price__gte=params['min_price'])
        if params.get('max_price') is not None:
            qs = qs.filter(price__lte=params['max_price'])
        if params.get('condition'):
            qs = qs.filter(condition=params['condition'])
        if params.get('vendor_id'):
            qs = qs.filter(vendor_id=params['vendor_id'])
        if params.get('is_featured'):
            qs = qs.filter(is_featured=True)
        ordering = params.get('ordering') or '-created_at'
        if ordering in ('price', '-price', 'name', '-name', 'created_at', '-created_at'):
            qs = qs.order_by(ordering)
        return qs


class ProductService:
    @staticmethod
    def ensure_demo_data():
        if Product.objects.exists():
            return
        vendor_user, _ = User.objects.get_or_create(
            email='vendor@medequip.local',
            defaults={'first_name': 'Demo', 'last_name': 'Vendor', 'is_active': True, 'is_vendor': True, 'email_verified': True},
        )
        if not vendor_user.has_usable_password():
            vendor_user.set_password('DemoVendor123!')
            vendor_user.save(update_fields=['password'])
        vendor, _ = VendorProfile.objects.get_or_create(
            user=vendor_user,
            defaults={'company_name': 'Kigali MedSupply Co.', 'description': 'Trusted supplier of clinic-ready medical equipment.', 'phone': '+250 788 000 111', 'address': 'Kigali, Rwanda', 'website': 'https://example.com', 'is_verified': True},
        )
        categories = {}
        for name, slug, description in [
            ('Diagnostics', 'diagnostics', 'Tools for examination, imaging and diagnosis.'),
            ('Patient Care', 'patient-care', 'Everyday devices for clinical care and monitoring.'),
            ('Surgical Tools', 'surgical-tools', 'Essential equipment for operating rooms and clinics.'),
        ]:
            categories[slug], _ = Category.objects.get_or_create(slug=slug, defaults={'name': name, 'description': description, 'is_active': True})
        for product in [
            {'name': 'Digital Patient Monitor', 'slug': 'digital-patient-monitor', 'sku': 'MVP-MON-001', 'category': categories['patient-care'], 'price': '850.00', 'stock_quantity': 12, 'manufacturer': 'MedCore', 'model_number': 'MC-PM100', 'short_description': 'Portable 5-parameter monitor for clinics and emergency rooms.', 'description': 'A reliable patient monitor for heart rate, SpO2, blood pressure, temperature and respiratory rate.', 'specifications': {'Display': '12 inch', 'Parameters': 'ECG, SpO2, NIBP, TEMP, RESP'}, 'is_featured': True},
            {'name': 'Portable Ultrasound Scanner', 'slug': 'portable-ultrasound-scanner', 'sku': 'MVP-ULT-002', 'category': categories['diagnostics'], 'price': '2450.00', 'stock_quantity': 4, 'manufacturer': 'SonoLite', 'model_number': 'SL-U2', 'short_description': 'Compact ultrasound scanner for point-of-care diagnosis.', 'description': 'Lightweight ultrasound device suitable for maternal care, emergency assessment and mobile clinical teams.', 'specifications': {'Probe': 'Convex', 'Battery': '3 hours', 'Connectivity': 'USB-C'}, 'is_featured': True},
            {'name': 'Sterile Surgical Instrument Set', 'slug': 'sterile-surgical-instrument-set', 'sku': 'MVP-SUR-003', 'category': categories['surgical-tools'], 'price': '320.00', 'stock_quantity': 25, 'manufacturer': 'SafeCut', 'model_number': 'SC-SET20', 'short_description': 'Reusable stainless steel instrument kit for minor procedures.', 'description': 'A practical set of forceps, scissors, clamps and holders for outpatient and theatre preparation.', 'specifications': {'Pieces': '20', 'Material': 'Stainless steel', 'Sterilizable': 'Yes'}, 'is_featured': False},
            {'name': 'Automatic Blood Pressure Machine', 'slug': 'automatic-blood-pressure-machine', 'sku': 'MVP-BP-004', 'category': categories['diagnostics'], 'price': '95.00', 'stock_quantity': 40, 'manufacturer': 'CarePulse', 'model_number': 'CP-BP9', 'short_description': 'Fast digital BP machine for triage and outpatient rooms.', 'description': 'Easy-to-use automatic blood pressure monitor with cuff and memory for repeated checks.', 'specifications': {'Cuff': 'Adult', 'Power': 'Battery/USB', 'Memory': '99 readings'}, 'is_featured': False},
        ]:
            Product.objects.get_or_create(slug=product['slug'], defaults={**product, 'vendor': vendor, 'condition': Product.Condition.NEW, 'is_active': True})

    @staticmethod
    def get_product(product_id: str):
        return Product.objects.select_related('vendor', 'category').prefetch_related('images', 'tags').filter(pk=product_id, is_active=True).first()

    @staticmethod
    def invalidate_product_cache(product_id: str):
        cache.delete(f'catalog:product:{product_id}')

    @staticmethod
    def generate_unique_slug(name: str, instance_id=None) -> str:
        base_slug = slugify(name)[:470] or 'product'
        slug = base_slug
        counter = 1
        while True:
            qs = Product.objects.filter(slug=slug)
            if instance_id:
                qs = qs.exclude(pk=instance_id)
            if not qs.exists():
                return slug
            slug = f'{base_slug}-{counter}'
            counter += 1

    @staticmethod
    def get_category_tree():
        return list(Category.objects.filter(is_active=True).order_by('name'))


__all__ = ['SearchService', 'ProductService']
