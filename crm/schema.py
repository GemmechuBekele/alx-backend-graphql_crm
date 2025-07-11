import re
import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from django.core.validators import validate_email
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from decimal import Decimal
from .models import Customer, Product, Order
from .filters import CustomerFilter, ProductFilter, OrderFilter

# ---------------- GraphQL Types ----------------
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ("id", "name", "stock")

class OrderType(DjangoObjectType):
    class Meta:
        model = Order

class CustomerNode(DjangoObjectType):
    class Meta:
        model = Customer
        filterset_class = CustomerFilter
        interfaces = (graphene.relay.Node,)

class ProductNode(DjangoObjectType):
    class Meta:
        model = Product
        filterset_class = ProductFilter
        interfaces = (graphene.relay.Node,)

class OrderNode(DjangoObjectType):
    class Meta:
        model = Order
        filterset_class = OrderFilter
        interfaces = (graphene.relay.Node,)

# ---------------- Helper Functions ----------------
def is_valid_phone(phone):
    pattern = r'^(\+\d{10,15}|\d{3}-\d{3}-\d{4})$'
    return re.match(pattern, phone)

# ---------------- Mutations ----------------
class CreateCustomer(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        email = graphene.String(required=True)
        phone = graphene.String()

    customer = graphene.Field(CustomerType)
    message = graphene.String()

    def mutate(self, info, name, email, phone=None):
        try:
            validate_email(email)
        except ValidationError:
            raise Exception("Invalid email format")

        if Customer.objects.filter(email=email).exists():
            raise Exception("Email already exists")

        if phone and not is_valid_phone(phone):
            raise Exception("Invalid phone format")

        customer = Customer(name=name, email=email, phone=phone)
        customer.save()
        return CreateCustomer(customer=customer, message="Customer created successfully.")

class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(graphene.JSONString, required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    def mutate(self, info, input):
        customers = []
        errors = []

        for i, data in enumerate(input):
            try:
                name = data['name']
                email = data['email']
                phone = data.get('phone')

                validate_email(email)
                if Customer.objects.filter(email=email).exists():
                    raise Exception(f"[{i}] Email already exists")

                if phone and not is_valid_phone(phone):
                    raise Exception(f"[{i}] Invalid phone format")

                customer = Customer(name=name, email=email, phone=phone)
                customer.save()
                customers.append(customer)
            except Exception as e:
                errors.append(str(e))

        return BulkCreateCustomers(customers=customers, errors=errors)

class CreateProduct(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        price = graphene.Decimal(required=True)
        stock = graphene.Int(default_value=0)

    product = graphene.Field(ProductType)

    def mutate(self, info, name, price, stock=0):
        if price <= 0:
            raise Exception("Price must be positive")
        if stock < 0:
            raise Exception("Stock cannot be negative")

        product = Product(name=name, price=price, stock=stock)
        product.save()
        return CreateProduct(product=product)

class CreateOrder(graphene.Mutation):
    class Arguments:
        customer_id = graphene.ID(required=True)
        product_ids = graphene.List(graphene.ID, required=True)
        order_date = graphene.DateTime()

    order = graphene.Field(OrderType)

    def mutate(self, info, customer_id, product_ids, order_date=None):
        try:
            customer = Customer.objects.get(pk=customer_id)
        except ObjectDoesNotExist:
            raise Exception("Invalid customer ID")

        if not product_ids:
            raise Exception("At least one product must be selected")

        products = Product.objects.filter(pk__in=product_ids)
        if products.count() != len(product_ids):
            raise Exception("One or more invalid product IDs")

        total = sum([product.price for product in products])
        order = Order(customer=customer, total_amount=total)
        if order_date:
            order.order_date = order_date
        order.save()
        order.products.set(products)
        return CreateOrder(order=order)

class UpdateLowStockProducts(graphene.Mutation):
    updated_products = graphene.List(ProductType)
    message = graphene.String()

    @classmethod
    def mutate(cls, root, info):
        low_stock_products = Product.objects.filter(stock__lt=10)
        for product in low_stock_products:
            product.stock += 10
            product.save()

        return UpdateLowStockProducts(
            updated_products=low_stock_products,
            message=f"Restocked {low_stock_products.count()} products."
        )

# ---------------- Root Query ----------------
class Query(graphene.ObjectType):
    all_customers = DjangoFilterConnectionField(CustomerNode, order_by=graphene.List(of_type=graphene.String))
    all_products = DjangoFilterConnectionField(ProductNode, order_by=graphene.List(of_type=graphene.String))
    all_orders = DjangoFilterConnectionField(OrderNode, order_by=graphene.List(of_type=graphene.String))

    def resolve_all_customers(self, info, **kwargs):
        order_by = kwargs.get("order_by")
        qs = Customer.objects.all()
        return qs.order_by(*order_by) if order_by else qs

    def resolve_all_products(self, info, **kwargs):
        order_by = kwargs.get("order_by")
        qs = Product.objects.all()
        return qs.order_by(*order_by) if order_by else qs

    def resolve_all_orders(self, info, **kwargs):
        order_by = kwargs.get("order_by")
        qs = Order.objects.all()
        return qs.order_by(*order_by) if order_by else qs

# ---------------- Root Mutation ----------------
class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
    updateLowStockProducts = UpdateLowStockProducts.Field()
