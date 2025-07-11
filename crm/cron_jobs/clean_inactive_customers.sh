#!/bin/bash

# Activate virtual environment if needed (uncomment and modify below if applicable)
# source /path/to/venv/bin/activate

# Navigate to project directory
cd "$(dirname "$0")"/../.. || exit 1

# Run Django command to delete inactive customers and capture output
deleted_count=$(python3 manage.py shell -c "
import datetime
from crm.models import Customer
from django.utils.timezone import now

cutoff_date = now() - datetime.timedelta(days=365)
inactive_customers = Customer.objects.filter(order__isnull=True, created_at__lt=cutoff_date).distinct()
count = inactive_customers.count()
inactive_customers.delete()
print(count)
")

# Log the result with timestamp
echo \"[$(date)] Deleted $deleted_count inactive customers\" >> /tmp/customer_cleanup_log.txt
