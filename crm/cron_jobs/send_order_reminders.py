#!/usr/bin/env python3

import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

# Setup GraphQL transport
transport = RequestsHTTPTransport(
    url="http://localhost:8000/graphql",
    verify=False,
    retries=3,
)

client = Client(transport=transport, fetch_schema_from_transport=False)

# Calculate date range
today = datetime.date.today()
seven_days_ago = today - datetime.timedelta(days=7)

# Define GraphQL query
query = gql("""
query {
  orders(orderDate_Gte: "%s") {
    id
    customer {
      email
    }
  }
}
""" % seven_days_ago.isoformat())

try:
    result = client.execute(query)
    orders = result.get("orders", [])

    # Log file path
    with open("/tmp/order_reminders_log.txt", "a") as log_file:
        for order in orders:
            order_id = order["id"]
            email = order["customer"]["email"]
            timestamp = datetime.datetime.now().isoformat()
            log_file.write(f"[{timestamp}] Reminder for Order ID: {order_id}, Email: {email}\n")

    print("Order reminders processed!")

except Exception as e:
    print(f"Error querying orders: {e}")
