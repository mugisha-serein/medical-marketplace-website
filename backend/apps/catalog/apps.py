from django.apps import AppConfig


class CatalogConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.catalog'
    label = 'catalog'

    def ready(self):
        from django.db.models.signals import post_save
        from django.dispatch import receiver
        from .models import Product

        @receiver(post_save, sender=Product)
        def on_product_save(sender, instance, created, **kwargs):
            """
            After a product is saved:
            1. Rebuild its full-text search vector.
            2. Create a StockRecord if this is a new product (async via Celery).
            """
            # Update search vector (direct DB update, no re-save loop)
            instance.update_search_vector()

            if created:
                from apps.inventory.tasks import create_stock_record
                create_stock_record.delay(str(instance.pk), initial_quantity=0)