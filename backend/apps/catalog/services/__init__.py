import hashlib
import json
import logging
from django.core.cache import cache
from django.contrib.postgres.search import SearchQuery, SearchRank, TrigramSimilarity
from django.db.models import Q, F
from django.conf import settings
from django.utils.text import slugify
from apps.catalog.models import Product, Category

logger = logging.getLogger(__name__)

SEARCH_CACHE_TTL = getattr(settings, 'SEARCH_CACHE_TTL', 300)
PRODUCT_CACHE_TTL = getattr(settings, 'PRODUCT_CACHE_TTL', 600)


def _search_cache_key(params: dict) -> str:
    raw = json.dumps(params, sort_keys=True)
    h = hashlib.md5(raw.encode()).hexdigest()
    return f'catalog:search:{h}'


def _product_cache_key(product_id: str) -> str:
    return f'catalog:product:{product_id}'


class SearchService:
    """
    Executes full-text search via PostgreSQL tsvector with trigram fallback.
    All results come from cache if available; cache-aside pattern.
    """

    @staticmethod
    def search(params: dict):
        """
        params keys: q, category_slug, min_price, max_price, condition,
                     vendor_id, is_featured, ordering, page_size
        Returns QuerySet (not yet evaluated — view handles pagination).
        """
        cache_key = _search_cache_key(params)
        # Return cached queryset IDs if available; rebuild QS from IDs
        cached_ids = cache.get(cache_key)
        if cached_ids is not None:
            preserved_order = {pk: idx for idx, pk in enumerate(cached_ids)}
            qs = Product.objects.filter(pk__in=cached_ids, is_active=True).select_related(
                'vendor', 'category'
            ).prefetch_related('images', 'tags')
            # Re-apply order from cached list
            qs = sorted(qs, key=lambda p: preserved_order.get(str(p.pk), 999))
            return qs

        qs = Product.objects.filter(is_active=True).select_related(
            'vendor', 'category'
        ).prefetch_related('images', 'tags')

        # Full-text search
        q = params.get('q', '').strip()
        if q:
            search_query = SearchQuery(q, search_type='websearch')
            qs = qs.filter(search_vector=search_query).annotate(
                rank=SearchRank(F('search_vector'), search_query)
            ).order_by('-rank')
        else:
            qs = qs.order_by('-created_at')

        # Filters
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

        if params.get('tag_slugs'):
            qs = qs.filter(tags__slug__in=params['tag_slugs']).distinct()

        # Explicit ordering (overrides search rank)
        ordering = params.get('ordering')
        if ordering in ('price', '-price', 'name', '-name', 'created_at', '-created_at') and not q:
            qs = qs.order_by(ordering)

        # Cache the list of PKs (not the full objects)
        ids = list(qs.values_list('pk', flat=True)[:500])
        cache.set(cache_key, [str(i) for i in ids], SEARCH_CACHE_TTL)

        return qs


class ProductService:
    @staticmethod
    def get_product(product_id: str):
        cache_key = _product_cache_key(product_id)
        cached = cache.get(cache_key)
        if cached:
            return cached

        try:
            product = Product.objects.select_related('vendor', 'category').prefetch_related(
                'images', 'tags'
            ).get(pk=product_id, is_active=True)
            cache.set(cache_key, product, PRODUCT_CACHE_TTL)
            return product
        except Product.DoesNotExist:
            return None

    @staticmethod
    def invalidate_product_cache(product_id: str):
        cache.delete(_product_cache_key(str(product_id)))
        # Also invalidate search caches (broad invalidation - all search results)
        cache.delete_pattern('medequip:catalog:search:*')

    @staticmethod
    def generate_unique_slug(name: str, instance_id=None) -> str:
        base_slug = slugify(name)[:470]
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
        cache_key = 'catalog:category_tree'
        cached = cache.get(cache_key)
        if cached:
            return cached
        categories = list(Category.objects.filter(is_active=True).order_by('name'))
        cache.set(cache_key, categories, 1800)
        return categories
