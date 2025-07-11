import datetime
import requests
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

def log_crm_heartbeat():
    now = datetime.datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    message = f"{now} CRM is alive"

    # Setup GraphQL client
    transport = RequestsHTTPTransport(
        url="http://localhost:8000/graphql",
        verify=False,
        retries=3,
    )
    client = Client(transport=transport, fetch_schema_from_transport=False)

    # Query hello field to verify endpoint is responsive
    query = gql("{ hello }")
    try:
        response = client.execute(query)
        status = "GraphQL OK" if "hello" in response else "GraphQL FAIL"
    except Exception as e:
        status = f"GraphQL ERROR: {e}"

    message += f" - {status}"

    # Write the heartbeat message to the log file (append mode)
    with open("/tmp/crm_heartbeat_log.txt", "a") as f:
        f.write(message + "\n")
