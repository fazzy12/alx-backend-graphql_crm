import os
import django
from django.db import transaction
from decimal import Decimal

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_backend_graphql.settings')
django.setup()

from crm.models import Customer, Product, Order

# Define sample data based on the task examples
CUSTOMER_DATA = [
    {"name": "Alice Johnson", "email": "alice@example.com", "phone": "+1234567890"},
    {"name": "Bob Smith", "email": "bob@example.com", "phone": "123-456-7890"},
    {"name": "Carol King", "email": "carol@example.com", "phone": None},
]

PRODUCT_DATA = [
    {"name": "Laptop Pro", "price": 1200.00, "stock": 10},
    {"name": "Mechanical Keyboard", "price": 99.99, "stock": 50},
    {"name": "Wireless Mouse", "price": 25.50, "stock": 100},
]

@transaction.atomic
def run_seed():
    """Seeds the database with sample CRM data."""
    print("Starting database seeding...")

    # Clear existing data for idempotency
    Order.objects.all().delete()
    Product.objects.all().delete()
    Customer.objects.all().delete()
    print("Existing data cleared.")

    # --- 1. Create Customers ---
    customers_map = {}
    for data in CUSTOMER_DATA:
        customer = Customer.objects.create(**data)
        customers_map[data['name']] = customer
        print(f"Created Customer: {customer.name}")

    # --- 2. Create Products ---
    products_map = {}
    for data in PRODUCT_DATA:
        # Ensure Decimal type for price before creation
        data['price'] = Decimal(data['price'])
        product = Product.objects.create(**data)
        products_map[data['name']] = product
        print(f"Created Product: {product.name} (ID: {product.id})")

    # --- 3. Create an Order ---
    
    # Get objects for the order
    alice = customers_map['Alice Johnson']
    laptop = products_map['Laptop Pro']
    mouse = products_map['Wireless Mouse']
    
    # Calculate total amount (mimics the mutation logic)
    products_for_order = [laptop, mouse]
    total_amount = sum(p.price for p in products_for_order)
    
    # Create the Order
    order = Order.objects.create(
        customer=alice,
        total_amount=total_amount
    )
    
    # Associate products
    order.products.set(products_for_order)
    
    print(f"\nCreated Order {order.id} for {alice.name}.")
    print(f"Products: {', '.join([p.name for p in products_for_order])}")
    print(f"Total Amount: {order.total_amount}")
    
    print("\nDatabase seeding complete.")

if __name__ == '__main__':
    run_seed()