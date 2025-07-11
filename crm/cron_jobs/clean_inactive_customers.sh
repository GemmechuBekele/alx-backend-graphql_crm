#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/../.." || {
    echo "Failed to change directory to project root"
    exit 1
}

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

if [ $? -eq 0 ]; then
    echo \"[$(date)] Deleted $deleted_count inactive customers\" >> /tmp/customer_cleanup_log.txt
else
    echo \"[$(date)] Error running cleanup\" >> /tmp/customer_cleanup_log.txt
fi
