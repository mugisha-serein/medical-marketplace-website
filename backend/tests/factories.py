import factory
import factory.django
from decimal import Decimal
from django.utils.text import slugify
from faker import Faker

fake = Faker()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'accounts.User'
        django_get_or_create = ('email',)

    email = factory.LazyAttribute(lambda _: fake.unique.email())
    first_name = factory.LazyAttribute(lambda _: fake.first_name())
    last_name = factory.LazyAttribute(lambda _: fake.last_name())
    password = factory.PostGenerationMethodCall('set_password', 'testpass123')
    is_active = True
    is_vendor = False


class VendorUserFactory(UserFactory):
    is_vendor = True

    @factory.post_generation
    def vendor_profile(obj, create, extracted, **kwargs):
        if not create:
            return
        VendorProfileFactory(user=obj)


class VendorProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'accounts.VendorProfile'

    user = factory.SubFactory(VendorUserFactory, vendor_profile=None)
    company_name = factory.LazyAttribute(lambda _: fake.company())
    is_verified = True


class CustomerProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'accounts.CustomerProfile'

    user = factory.SubFactory(UserFactory)
    organization = factory.LazyAttribute(lambda _: fake.company())


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'catalog.Category'
        django_get_or_create = ('slug',)

    name = factory.LazyAttribute(lambda _: fake.unique.word().title())
    slug = factory.LazyAttribute(lambda obj: slugify(obj.name))
    is_active = True


class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'catalog.Product'

    vendor = factory.SubFactory(VendorProfileFactory)
    category = factory.SubFactory(CategoryFactory)
    name = factory.LazyAttribute(lambda _: f'{fake.word().title()} Medical Equipment')
    slug = factory.LazyAttribute(lambda obj: slugify(obj.name) + f'-{fake.uuid4()[:8]}')
    sku = factory.LazyAttribute(lambda _: f'SKU-{fake.unique.bothify("????-####")}')
    description = factory.LazyAttribute(lambda _: fake.paragraph())
    short_description = factory.LazyAttribute(lambda _: fake.sentence())
    price = factory.LazyAttribute(lambda _: Decimal(str(round(fake.pyfloat(min_value=100, max_value=50000, right_digits=2), 2))))
    is_active = True
    condition = 'new'

    @factory.post_generation
    def stock_record(obj, create, extracted, **kwargs):
        if not create:
            return
        from apps.inventory.models import StockRecord
        quantity = extracted if extracted is not None else 10
        StockRecord.objects.get_or_create(product=obj, defaults={'quantity': quantity})


class StockRecordFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'inventory.StockRecord'
        django_get_or_create = ('product',)

    product = factory.SubFactory(ProductFactory, stock_record=None)
    quantity = 10


class OrderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'orders.Order'

    user = factory.SubFactory(UserFactory)
    order_number = factory.LazyAttribute(lambda _: f'ME{fake.bothify("########")}')
    status = 'pending'
    shipping_address = factory.LazyAttribute(lambda _: fake.address())
    billing_address = factory.LazyAttribute(lambda _: fake.address())
    subtotal = Decimal('1000.00')
    shipping_cost = Decimal('0.00')
    tax_amount = Decimal('0.00')
    total_amount = Decimal('1000.00')


class OrderItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'orders.OrderItem'

    order = factory.SubFactory(OrderFactory)
    product = factory.SubFactory(ProductFactory)
    vendor = factory.LazyAttribute(lambda obj: obj.product.vendor)
    product_name_snapshot = factory.LazyAttribute(lambda obj: obj.product.name)
    product_sku_snapshot = factory.LazyAttribute(lambda obj: obj.product.sku)
    unit_price_snapshot = Decimal('500.00')
    quantity = 2
