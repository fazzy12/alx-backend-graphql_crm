# alx-backend-graphql_crm/crm/filters.py (NEW FILE)
import django_filters
from django.db.models import Q

from .models import Customer, Product, Order

# --- FilterSets ---

class CustomerFilter(django_filters.FilterSet):
    # Case-insensitive partial matches (icontains)
    name = django_filters.CharFilter(lookup_expr='icontains')
    email = django_filters.CharFilter(lookup_expr='icontains')
    
    # Date range filters (explicit GTE/LTE lookups)
    created_at_gte = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_at_lte = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')

    # Challenge: Custom filter for phone pattern (e.g., starts with +1)
    phone_pattern = django_filters.CharFilter(
        method='filter_phone_pattern', 
        label='Filter by phone number starting with pattern (e.g., +1)'
    )

    class Meta:
        model = Customer
        fields = ['name', 'email', 'created_at']

    def filter_phone_pattern(self, queryset, name, value):
        if value:
            return queryset.filter(phone__startswith=value)
        return queryset


class ProductFilter(django_filters.FilterSet):
    # Case-insensitive partial match
    name = django_filters.CharFilter(lookup_expr='icontains')
    
    # Range filters for price
    price_gte = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    price_lte = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    
    # Range filters for stock
    stock_gte = django_filters.NumberFilter(field_name='stock', lookup_expr='gte')
    stock_lte = django_filters.NumberFilter(field_name='stock', lookup_expr='lte')
    
    class Meta:
        model = Product
        fields = ['name', 'price', 'stock']


class OrderFilter(django_filters.FilterSet):
    # Range filters for amount and date
    total_amount_gte = django_filters.NumberFilter(field_name='total_amount', lookup_expr='gte')
    total_amount_lte = django_filters.NumberFilter(field_name='total_amount', lookup_expr='lte')
    order_date_gte = django_filters.DateTimeFilter(field_name='order_date', lookup_expr='gte')
    order_date_lte = django_filters.DateTimeFilter(field_name='order_date', lookup_expr='lte')

    # Related field lookups (customer name, product name)
    customer_name = django_filters.CharFilter(field_name='customer__name', lookup_expr='icontains')
    product_name = django_filters.CharFilter(field_name='products__name', lookup_expr='icontains')

    # Challenge: Filter by specific product ID
    product_id = django_filters.NumberFilter(
        method='filter_products_by_id', 
        label='Orders containing specific Product ID'
    )

    class Meta:
        model = Order
        fields = ['total_amount', 'order_date']

    def filter_products_by_id(self, queryset, name, value):
        # Use .distinct() to avoid duplicate orders if multiple products match
        if value:
            return queryset.filter(products__id=value).distinct()
        return queryset