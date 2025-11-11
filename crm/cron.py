import sys
from datetime import datetime
from django.utils import timezone
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport

# Optional GraphQL check dependencies
try:
    from gql import Client, gql
    from gql.transport.requests import RequestsHTTPTransport
except ImportError:
    pass 

def log_crm_heartbeat():
    """
    Logs a heartbeat message to a file every 5 minutes.
    Optionally queries the GraphQL 'hello' field to check server health.
    """
    now = timezone.localtime(timezone.now())
    timestamp = now.strftime("%d/%m/%Y-%H:%M:%S")
    log_message = f"{timestamp} CRM is alive"
    
    graphql_status = ""
    try:
        HELLO_QUERY = gql("{ hello }")

        transport = RequestsHTTPTransport(
            url="http://localhost:8000/graphql",
            verify=True,
            timeout=5,
        )
        client = Client(transport=transport, fetch_schema_from_transport=False)
        result = client.execute(HELLO_QUERY)
        
        if result.get('hello') == "Hello, GraphQL!":
            graphql_status = " | GraphQL: OK"
        else:
            graphql_status = f" | GraphQL: Warning (Response: {result.get('hello')})"
            
    except NameError:
        graphql_status = " | GraphQL Check: Skipped (gql library not found)"
    except Exception as e:
        graphql_status = f" | GraphQL: FAILED ({type(e).__name__})"

    log_entry = log_message + graphql_status
    log_path = "/tmp/crm_heartbeat_log.txt"
    
    try:
        with open(log_path, "a") as f:
            f.write(log_entry + "\n")
            
        print(f"Heartbeat logged: {log_entry}", file=sys.stdout)
    except Exception as e:
        print(f"ERROR: Failed to write heartbeat log: {e}", file=sys.stderr)
        

def update_low_stock():
    """
    Executes a GraphQL mutation to restock products with low inventory (stock < 10).
    Logs the updated product names and new stock levels to /tmp/low_stock_updates_log.txt.
    """
    # 1. Define the GraphQL Mutation to call
    MUTATION = gql(
        """
        mutation RestockProducts {
          updateLowStockProducts {
            message
            updatedProducts {
              name
              stock
            }
          }
        }
        """
    )
    
    log_path = "/tmp/low_stock_updates_log.txt"

    try:
        # 2. Setup the GraphQL client transport
        transport = RequestsHTTPTransport(
            url="http://localhost:8000/graphql",
            verify=True,
            retries=3,
            timeout=10,
        )

        # 3. Execute the mutation
        client = Client(transport=transport, fetch_schema_from_transport=False)
        result = client.execute(MUTATION)
        
        # 4. Extract and log results
        data = result.get('updateLowStockProducts', {})
        message = data.get('message', 'Mutation failed or returned no message.')
        updated_products = data.get('updatedProducts', [])
        
        timestamp = timezone.localtime(timezone.now()).strftime("%d/%m/%Y-%H:%M:%S")

        with open(log_path, "a") as f:
            if updated_products:
                f.write(f"[{timestamp}] Restock SUCCESS: {message}\n")
                for product in updated_products:
                    f.write(f"  - Product: {product['name']} | New Stock: {product['stock']}\n")
            else:
                 f.write(f"[{timestamp}] Restock INFO: {message}\n")

        print(f"Low stock update logged: {message}", file=sys.stdout)
        
    except Exception as e:
        error_message = f"[{timezone.localtime(timezone.now()).strftime('%d/%m/%Y-%H:%M:%S')}] ERROR: Low stock update failed: {e}"
        print(error_message, file=sys.stderr)
        # Log error to file as well for visibility
        with open(log_path, "a") as f:
            f.write(error_message + "\n")
        sys.exit(1)


if __name__ == '__main__':
    log_crm_heartbeat()
    update_low_stock()