import os
import sys
from datetime import datetime, timedelta, timezone

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(PROJECT_ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_backend_graphql.settings')


try:
    from django.utils import timezone
    from gql import Client, gql
    from gql.transport.requests import RequestsHTTPTransport
except ImportError:
    print("ERROR: Required libraries 'gql' are not installed. Please run 'pip install gql'")
    sys.exit(1)


def send_order_reminders():
    """
    Queries the GraphQL endpoint for recent orders and logs them as reminders.
    """
    try:
        one_week_ago = timezone.now() - timedelta(days=7)
        start_date = one_week_ago.isoformat() 

        QUERY = gql(
            """
            query RecentOrders($startDate: DateTime) {
              allOrders(orderDateGte: $startDate) {
                edges {
                  node {
                    id
                    orderDate
                    customer {
                      email
                    }
                  }
                }
              }
            }
            """
        )

        transport = RequestsHTTPTransport(
            url="http://localhost:8000/graphql",
            verify=True,
            retries=3,
        )

        client = Client(transport=transport, fetch_schema_from_transport=True)

        result = client.execute(
            QUERY, 
            variable_values={"startDate": start_date}
        )
        
        log_entries = []
        
        orders = result.get('allOrders', {}).get('edges', [])
        
        for edge in orders:
            order = edge.get('node', {})
            order_id = order.get('id')
            customer_email = order.get('customer', {}).get('email', 'N/A')
            
            timestamp = timezone.now().isoformat()
            log_entry = f"[{timestamp}] REMINDER: Order ID {order_id} (Customer: {customer_email})"
            log_entries.append(log_entry)

        log_path = "/tmp/order_reminders_log.txt"
        with open(log_path, "a") as f:
            for entry in log_entries:
                f.write(entry + "\n")
        
        print("Order reminders processed!")
        
    except Exception as e:
        print(f"ERROR: Order reminders script failed: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    send_order_reminders()