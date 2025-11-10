#!/bin/bash

# Define the project root by navigating up two directories from this script's location
PROJECT_ROOT=$(dirname "$(dirname "$(dirname "$(readlink -f "$0")")")")

# Change to the project root directory so manage.py can find the settings and apps
cd "$PROJECT_ROOT" || { echo "Failed to change directory to $PROJECT_ROOT" >&2; exit 1; }

# The Python code to be executed via manage.py shell
PYTHON_CODE='
from django.db.models import Q, Max
from django.utils import timezone
from datetime import timedelta
from crm.models import Customer
import sys

try:
    # 1. Define the cutoff date (1 year ago)
    one_year_ago = timezone.now() - timedelta(days=365)

    # 2. Find customers to delete:
    #    - Annotate each customer with their latest order date.
    #    - Filter for customers where the latest order date is:
    #      a) Older than one year ago (latest_order_date < one_year_ago)
    #      b) Non-existent (latest_order_date is null, i.e., no orders at all)
    customers_to_delete = Customer.objects.annotate(
        latest_order_date=Max("orders__order_date")
    ).filter(
        Q(latest_order_date__lt=one_year_ago) | Q(latest_order_date__isnull=True)
    )

    # 3. Execute deletion and get the count
    deleted_count, _ = customers_to_delete.delete()

    # 4. Log the result to /tmp/customer_cleanup_log.txt with a timestamp
    timestamp = timezone.now().isoformat()
    log_entry = f"[{timestamp}] Deleted {deleted_count} inactive customers."

    with open("/tmp/customer_cleanup_log.txt", "a") as f:
        f.write(log_entry + "\n")
    
except Exception as e:
    # Log the error to stderr, which cron job runner will capture
    print(f"ERROR: Customer cleanup failed: {e}", file=sys.stderr)
    sys.exit(1)
'

# Execute the Python code using manage.py shell
# Note: Ensure python3 is the correct interpreter for your environment
/usr/bin/env python3 manage.py shell --command "$PYTHON_CODE"