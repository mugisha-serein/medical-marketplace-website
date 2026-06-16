import json
import logging
from decimal import Decimal
from django.core.cache import cache
from django.conf import settings
from apps.inventory.services import InventoryService

logger = logging.getLogger(__name__)

CART_TTL = getattr(settings, 'CART_TTL_SECONDS', 86400)


def _cart_key(user_id: str) -> str:
    return f'cart:{user_id}'


class CartValidationError(Exception):
    def __init__(self, message, errors=None):
        self.errors = errors or []
        super().__init__(message)


class CartService:
    """
    Cart state is stored entirely in Redis as JSON.
    Schema: { "items": { "<product_id>": { "qty": int, "price_snapshot": str, "name": str, "sku": str } } }
    TTL resets on every mutation (sliding expiry).
    """

    @staticmethod
    def _load(user_id: str) -> dict:
        raw = cache.get(_cart_key(user_id))
        if raw is None:
            return {'items': {}}
        if isinstance(raw, dict):
            return raw
        try:
            return json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return {'items': {}}

    @staticmethod
    def _save(user_id: str, cart: dict):
        cache.set(_cart_key(user_id), cart, CART_TTL)

    @staticmethod
    def get_cart(user_id: str) -> dict:
        cart = CartService._load(user_id)
        return CartService._enrich_cart(cart)

    @staticmethod
    def _enrich_cart(cart: dict) -> dict:
        """Annotate cart with computed totals."""
        total = Decimal('0.00')
        item_count = 0
        for item in cart['items'].values():
            qty = item.get('qty', 0)
            price = Decimal(str(item.get('price_snapshot', '0')))
            item['subtotal'] = str(price * qty)
            total += price * qty
            item_count += qty
        cart['total'] = str(total)
        cart['item_count'] = item_count
        return cart

    @staticmethod
    def add_item(user_id: str, product_id: str, quantity: int) -> dict:
        """
        Add or increment item in cart.
        Validates:
          1. Product exists and is active
          2. Sufficient stock
          3. Price snapshot captured at add time
        """
        from apps.catalog.models import Product
        try:
            product = Product.objects.select_related('stock_record').get(
                pk=product_id, is_active=True
            )
        except Product.DoesNotExist:
            raise CartValidationError(f'Product {product_id} not found or unavailable.')

        cart = CartService._load(user_id)
        existing_qty = cart['items'].get(str(product_id), {}).get('qty', 0)
        new_total_qty = existing_qty + quantity

        if not InventoryService.check_availability(product_id, new_total_qty):
            stock = InventoryService.get_stock(product_id)
            available = stock.quantity if stock else 0
            raise CartValidationError(
                f'Insufficient stock. Requested {new_total_qty}, available {available}.',
                errors=[{'product_id': str(product_id), 'available': available}]
            )

        cart['items'][str(product_id)] = {
            'qty': new_total_qty,
            'price_snapshot': str(product.price),
            'name': product.name,
            'sku': product.sku,
            'product_id': str(product_id),
        }
        CartService._save(user_id, cart)
        logger.info('Cart item added', extra={'user_id': user_id, 'product_id': product_id, 'qty': new_total_qty})
        return CartService._enrich_cart(cart)

    @staticmethod
    def update_item(user_id: str, product_id: str, quantity: int) -> dict:
        """Set item quantity. quantity=0 removes the item."""
        if quantity == 0:
            return CartService.remove_item(user_id, product_id)

        cart = CartService._load(user_id)
        if str(product_id) not in cart['items']:
            raise CartValidationError(f'Product {product_id} not in cart.')

        if not InventoryService.check_availability(product_id, quantity):
            stock = InventoryService.get_stock(product_id)
            available = stock.quantity if stock else 0
            raise CartValidationError(
                f'Insufficient stock. Requested {quantity}, available {available}.'
            )

        # Refresh price snapshot on update
        from apps.catalog.models import Product
        try:
            product = Product.objects.get(pk=product_id, is_active=True)
        except Product.DoesNotExist:
            raise CartValidationError(f'Product {product_id} no longer available.')

        cart['items'][str(product_id)]['qty'] = quantity
        cart['items'][str(product_id)]['price_snapshot'] = str(product.price)
        CartService._save(user_id, cart)
        return CartService._enrich_cart(cart)

    @staticmethod
    def remove_item(user_id: str, product_id: str) -> dict:
        cart = CartService._load(user_id)
        cart['items'].pop(str(product_id), None)
        CartService._save(user_id, cart)
        return CartService._enrich_cart(cart)

    @staticmethod
    def clear(user_id: str):
        cache.delete(_cart_key(user_id))
        logger.info('Cart cleared', extra={'user_id': user_id})

    @staticmethod
    def validate_for_checkout(user_id: str) -> dict:
        """
        Full validation before order placement.
        Checks stock and price for every item.
        Returns validated cart or raises CartValidationError with all errors.
        """
        cart = CartService._load(user_id)
        if not cart['items']:
            raise CartValidationError('Cart is empty.')

        from apps.catalog.models import Product
        errors = []
        validated_items = {}

        for product_id, item in cart['items'].items():
            qty = item['qty']
            try:
                product = Product.objects.select_related('stock_record').get(
                    pk=product_id, is_active=True
                )
            except Product.DoesNotExist:
                errors.append({'product_id': product_id, 'error': 'Product no longer available.'})
                continue

            if not InventoryService.check_availability(product_id, qty):
                stock = InventoryService.get_stock(product_id)
                available = stock.quantity if stock else 0
                errors.append({
                    'product_id': product_id,
                    'name': product.name,
                    'error': f'Insufficient stock. Requested {qty}, available {available}.',
                    'available': available,
                })
                continue

            live_price = product.price
            snapshot_price = Decimal(str(item['price_snapshot']))
            if live_price != snapshot_price:
                # Price changed — update snapshot, surface to caller
                item['price_snapshot'] = str(live_price)
                item['price_changed'] = True
                item['old_price'] = str(snapshot_price)

            validated_items[product_id] = {**item, 'product': product, 'qty': qty}

        if errors:
            raise CartValidationError('Cart validation failed.', errors=errors)

        cart['items'] = {k: {kk: vv for kk, vv in v.items() if kk != 'product'} for k, v in validated_items.items()}
        CartService._save(user_id, cart)

        return {'items': validated_items, 'raw_cart': cart}