# alx-backend-graphql_crm/crm/schema.py
import re
import graphene
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from decimal import Decimal
from django.db.models import Sum, F
from crm.models import Product

from graphene_django.types import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from .models import Customer, Product, Order
from .filters import CustomerFilter, ProductFilter, OrderFilter

# --- TYPES & CONNECTIONS ---

class CustomerType(DjangoObjectType):
    created_at = graphene.DateTime()
    
    class Meta:
        model = Customer
        fields = ('id', 'name', 'email', 'phone', 'created_at', 'orders') 
        interfaces = (graphene.Node,)
        filter_fields = ()

class CustomerConnection(graphene.relay.Connection):
    class Meta:
        node = CustomerType

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ('id', 'name', 'price', 'stock')
        interfaces = (graphene.Node,)
        filter_fields = ()

class ProductConnection(graphene.relay.Connection):
    class Meta:
        node = ProductType

class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = ('id', 'customer', 'products', 'total_amount', 'order_date')
        interfaces = (graphene.Node,) # <--- FIX 1: Use graphene.Node directly
        filter_fields = ()

class OrderConnection(graphene.relay.Connection):
    class Meta:
        node = OrderType

# --- QUERY (CRM-specific) ---

class Query(graphene.ObjectType):
    """Defines all CRM-specific root query fields, using connections for filtering/ordering."""
    
    all_customers = DjangoFilterConnectionField(
        CustomerType,
        filterset_class=CustomerFilter,
        description="List of customers with filtering options."
    )

    all_products = DjangoFilterConnectionField(
        ProductType,
        filterset_class=ProductFilter,
        description="List of products with filtering options."
    )

    all_orders = DjangoFilterConnectionField(
        OrderType,
        filterset_class=OrderFilter,
        description="List of orders with filtering options."
    )
    
    # Node field for fetching by global ID
    node = graphene.Node.Field()
    
    # Single object query
    customer = graphene.Field(CustomerType, id=graphene.ID())


    def resolve_customer(root, info, id):
        try:
            return Customer.objects.get(pk=id)
        except Customer.DoesNotExist:
            return None

# --- UTILITY VALIDATION ---

def validate_phone(phone):
    """Validates phone number format."""
    phone_regex = re.compile(r'^\+?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}$')
    if phone and not phone_regex.match(phone):
        raise ValidationError("Invalid phone number format. Please use a valid format (e.g., +1234567890 or 123-456-7890).")


class BulkCustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String(required=False)

class OrderInput(graphene.InputObjectType):
    customer_id = graphene.ID(required=True)
    product_ids = graphene.List(graphene.ID, required=True)


# 1. CreateCustomer
class CreateCustomer(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        email = graphene.String(required=True)
        phone = graphene.String(required=False)

    customer = graphene.Field(CustomerType)
    message = graphene.String()

    @classmethod
    def mutate(cls, root, info, name, email, phone=None):
        try:
            validate_email(email)
            if Customer.objects.filter(email=email).exists():
                raise ValidationError("Email already exists.")
            if phone:
                validate_phone(phone)

        except ValidationError as e:
            raise Exception(f"Validation Error: {e.message}")

        customer = Customer(
            name=name,
            email=email,
            phone=phone
        )
        customer.save()
        
        return CreateCustomer(customer=customer, message="Customer created successfully.")

# 2. BulkCreateCustomers
class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(BulkCustomerInput, required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    @classmethod
    @transaction.atomic
    def mutate(cls, root, info, input):
        successful_customers = []
        validation_errors = []
        emails_in_batch = set(Customer.objects.values_list('email', flat=True))

        for i, customer_data in enumerate(input):
            email = customer_data.get('email')
            phone = customer_data.get('phone')

            try:
                validate_email(email)

                if email in emails_in_batch:
                    db_exists = Customer.objects.filter(email=email).exists()
                    error_msg = "Email already exists in database." if db_exists else "Duplicate email in current batch."
                    raise ValidationError(error_msg)

                if phone:
                    validate_phone(phone)
                
                emails_in_batch.add(email)

                customer = Customer(
                    name=customer_data.get('name'),
                    email=email,
                    phone=phone if phone else None
                )
                customer.save()
                successful_customers.append(customer)

            except ValidationError as e:
                error_message = f"Record {i} (Email: {email}) failed validation: {e.message}"
                validation_errors.append(error_message)

            except Exception as e:
                error_message = f"Record {i} (Email: {email}) failed creation: {str(e)}"
                validation_errors.append(error_message)

        return BulkCreateCustomers(
            customers=successful_customers,
            errors=validation_errors
        )


# 3. CreateProduct
class CreateProduct(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        price = graphene.Float(required=True)
        stock = graphene.Int(required=False, default_value=0)

    product = graphene.Field(ProductType)

    @classmethod
    def mutate(cls, root, info, name, price, stock=0):

        price_decimal = Decimal(str(price))

        if price_decimal <= 0:
            raise Exception("Validation Error: Price must be a positive number.")
        if stock < 0:
            raise Exception("Validation Error: Stock cannot be negative.")

        product = Product(
            name=name,
            price=price_decimal,
            stock=stock
        )
        product.save()
        
        return CreateProduct(product=product)

# 4. CreateOrder
class CreateOrder(graphene.Mutation):
    class Arguments:
        input = OrderInput(required=True)

    order = graphene.Field(OrderType)

    @classmethod
    @transaction.atomic
    def mutate(cls, root, info, input):
        customer_id = input.get('customer_id')
        product_ids = input.get('product_ids')

        if not product_ids:
            raise Exception("Validation Error: An order must contain at least one product.")

        try:
            customer = Customer.objects.get(pk=customer_id)
        except Customer.DoesNotExist:
            raise Exception(f"Validation Error: Invalid customer ID '{customer_id}'.")

        unique_product_ids = set(product_ids)
        products = Product.objects.filter(pk__in=unique_product_ids)

        if products.count() != len(unique_product_ids):
            valid_pks = set(str(p.pk) for p in products)
            invalid_ids = [pid for pid in unique_product_ids if pid not in valid_pks]
            raise Exception(f"Validation Error: Invalid product ID(s) found: {', '.join(invalid_ids)}.")

        total_amount = products.aggregate(Sum('price'))['price__sum']

        order = Order(
            customer=customer,
            total_amount=total_amount
        )
        order.save()

        order.products.set(products)

        return CreateOrder(order=order)
    

class UpdatedProductType(DjangoObjectType):
    """A minimal type for returning updated products."""
    class Meta:
        model = Product
        fields = ('id', 'name', 'stock')
        interfaces = (graphene.Node,)
        filter_fields = ()

class UpdateLowStockProducts(graphene.Mutation):
    """
    Restocks products where stock is less than 10 by incrementing stock by 10.
    """
    updated_products = graphene.List(UpdatedProductType)
    message = graphene.String()

    @classmethod
    @transaction.atomic
    def mutate(cls, root, info):
        LOW_STOCK_THRESHOLD = 10
        RESTOCK_AMOUNT = 10


        low_stock_products_ids = Product.objects.filter(stock__lt=LOW_STOCK_THRESHOLD).values_list('id', flat=True)

        if not low_stock_products_ids:
            return UpdateLowStockProducts(
                updated_products=[], 
                message="No low-stock products found to update."
            )


        Product.objects.filter(id__in=low_stock_products_ids).update(stock=F('stock') + RESTOCK_AMOUNT)

        updated_products = Product.objects.filter(id__in=low_stock_products_ids)
        product_names = ', '.join([p.name for p in updated_products])

        return UpdateLowStockProducts(
            updated_products=updated_products,
            message=f"Successfully restocked {len(updated_products)} products: {product_names} (Stock +{RESTOCK_AMOUNT})."
        )


# --- ROOT MUTATION ---

class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
    update_low_stock_products = UpdateLowStockProducts.Field()