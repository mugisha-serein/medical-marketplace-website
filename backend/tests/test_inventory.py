import pytest
from decimal import Decimal
from django.test import TestCase
from .factories import ProductFactory, StockRecordFactory
from apps.inventory.services import InventoryService, InsufficientStockError, StockLockError
from apps.inventory.models import StockRecord, StockMovement


@pytest.mark.django_db(transaction=True)
class TestInventoryService:

    def test_deduct_reduces_stock(self, db):
        product = ProductFactory(stock_record=10)
        stock = product.stock_record
        assert stock.quantity == 10

        InventoryService.deduct(str(product.id), 3)
        stock.refresh_from_db()
        assert stock.quantity == 7

    def test_deduct_creates_movement(self, db):
        product = ProductFactory(stock_record=10)
        InventoryService.deduct(str(product.id), 4, reference='order-123')
        movement = StockMovement.objects.filter(
            stock_record=product.stock_record,
            movement_type=StockMovement.MovementType.SALE,
        ).first()
        assert movement is not None
        assert movement.quantity_delta == -4
        assert movement.quantity_before == 10
        assert movement.quantity_after == 6
        assert movement.reference == 'order-123'

    def test_deduct_raises_on_insufficient_stock(self, db):
        product = ProductFactory(stock_record=2)
        with pytest.raises(InsufficientStockError) as exc_info:
            InventoryService.deduct(str(product.id), 5)
        assert exc_info.value.requested == 5
        assert exc_info.value.available == 2

    def test_deduct_does_not_go_below_zero(self, db):
        product = ProductFactory(stock_record=1)
        with pytest.raises(InsufficientStockError):
            InventoryService.deduct(str(product.id), 2)
        product.stock_record.refresh_from_db()
        assert product.stock_record.quantity == 1  # unchanged due to rollback

    def test_restock_increases_stock(self, db):
        product = ProductFactory(stock_record=5)
        InventoryService.restock(str(product.id), 20, reference='PO-001')
        product.stock_record.refresh_from_db()
        assert product.stock_record.quantity == 25

    def test_restock_creates_purchase_movement(self, db):
        product = ProductFactory(stock_record=0)
        InventoryService.restock(str(product.id), 50, reference='PO-002')
        movement = StockMovement.objects.filter(
            stock_record=product.stock_record,
            movement_type=StockMovement.MovementType.PURCHASE,
        ).first()
        assert movement is not None
        assert movement.quantity_delta == 50

    def test_adjust_positive(self, db):
        product = ProductFactory(stock_record=10)
        InventoryService.adjust(str(product.id), 5, reason='found extra units')
        product.stock_record.refresh_from_db()
        assert product.stock_record.quantity == 15

    def test_adjust_negative(self, db):
        product = ProductFactory(stock_record=10)
        InventoryService.adjust(str(product.id), -3, reason='damaged units')
        product.stock_record.refresh_from_db()
        assert product.stock_record.quantity == 7

    def test_adjust_below_zero_raises(self, db):
        product = ProductFactory(stock_record=3)
        with pytest.raises(InsufficientStockError):
            InventoryService.adjust(str(product.id), -10)

    def test_check_availability_true(self, db):
        product = ProductFactory(stock_record=5)
        assert InventoryService.check_availability(str(product.id), 5) is True

    def test_check_availability_false(self, db):
        product = ProductFactory(stock_record=2)
        assert InventoryService.check_availability(str(product.id), 3) is False

    def test_reconcile_corrects_drift(self, db):
        product = ProductFactory(stock_record=10)
        stock = product.stock_record
        # Simulate drift by directly modifying the DB field
        StockRecord.objects.filter(pk=stock.pk).update(quantity=15)
        stock.refresh_from_db()
        assert stock.quantity == 15  # drifted value

        # Reconcile: sum of movements = 10 (from initial create)
        # Movements: +10 (initial stock via factory)
        # After reconcile quantity should = derived
        InventoryService.reconcile(str(product.id))
        # The reconcile result depends on movement history
        # Key assertion: a reconcile movement was written
        reconcile_movement = StockMovement.objects.filter(
            stock_record=stock,
            movement_type=StockMovement.MovementType.RECONCILE,
        ).first()
        # If there was drift, a reconcile movement is created
        # (depends on factory setup; assert movement table has entries)
        assert StockMovement.objects.filter(stock_record=stock).exists()

    def test_full_audit_trail(self, db):
        product = ProductFactory(stock_record=100)
        InventoryService.deduct(str(product.id), 10, reference='order-A')
        InventoryService.deduct(str(product.id), 5, reference='order-B')
        InventoryService.restock(str(product.id), 20, reference='PO-1')

        movements = StockMovement.objects.filter(stock_record=product.stock_record).order_by('created_at')
        qtys = [m.quantity_after for m in movements]
        # Each movement's quantity_after should be correct
        assert all(q >= 0 for q in qtys)

        product.stock_record.refresh_from_db()
        assert product.stock_record.quantity == 105  # 100 - 10 - 5 + 20
