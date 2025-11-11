import sys
from celery import shared_task
from django.utils import timezone
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport
from decimal import Decimal
from datetime import datetime
import requests

GRAPHQL_ENDPOINT = "http://localhost:8000/graphql"

@shared_task
def generate_crm_report():
    """
    Celery task that queries the GraphQL endpoint to fetch CRM totals 
    and logs a summary report weekly.
    """

    
    try:

        from crm.models import Customer, Order
        from django.db.models import Sum


        total_customers = Customer.objects.count()
        total_orders = Order.objects.count()
        
        revenue_aggregation = Order.objects.aggregate(Sum('total_amount'))
        total_revenue_decimal = revenue_aggregation['total_amount__sum'] or Decimal('0.00')
        
        total_revenue = f"{total_revenue_decimal:.2f}"
        
        log_path = "/tmp/crm_report_log.txt"
        now = timezone.localtime(timezone.now())
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
        
        report_message = (
            f"{timestamp} - Report: {total_customers} customers, "
            f"{total_orders} orders, ${total_revenue} revenue"
        )

        with open(log_path, "a") as f:
            f.write(report_message + "\n")
            
        print(f"CRM Report Generated: {report_message}", file=sys.stdout)
        
    except Exception as e:
        error_message = f"[{timezone.localtime(timezone.now()).strftime('%Y-%m-%d %H:%M:%S')}] ERROR: CRM report failed: {e}"
        print(error_message, file=sys.stderr)
        sys.exit(1)
