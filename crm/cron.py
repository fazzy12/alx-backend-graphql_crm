import sys
from datetime import datetime
from django.utils import timezone

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


if __name__ == '__main__':
    log_crm_heartbeat()