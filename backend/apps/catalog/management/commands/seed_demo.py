from django.core.management.base import BaseCommand

from apps.catalog.models import Category, Product
from apps.catalog.services import ProductService


class Command(BaseCommand):
    help = 'Seed the SQLite MVP with demo medical marketplace data.'

    def handle(self, *args, **options):
        product_count_before = Product.objects.count()
        category_count_before = Category.objects.count()

        ProductService.ensure_demo_data()

        product_count_after = Product.objects.count()
        category_count_after = Category.objects.count()

        created_products = product_count_after - product_count_before
        created_categories = category_count_after - category_count_before

        self.stdout.write(
            self.style.SUCCESS(
                'Demo data ready. '
                f'Products: {product_count_after} ({created_products:+d}), '
                f'Categories: {category_count_after} ({created_categories:+d}).'
            )
        )
