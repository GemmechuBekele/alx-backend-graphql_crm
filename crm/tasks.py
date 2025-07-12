import datetime
import logging
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

logger = logging.getLogger(__name__)

def get_gql_client():
    transport = RequestsHTTPTransport(
        url='http://localhost:8000/graphql',
        verify=False,
        retries=3,
    )
    return Client(transport=transport, fetch_schema_from_transport=False)

from celery import shared_task

@shared_task
def generate_crm_report():
    client = get_gql_client()
    query = gql('''
        query {
            totalCustomers: allCustomers {
                totalCount
            }
            totalOrders: allOrders {
                totalCount
                edges {
                    node {
                        totalAmount
                    }
                }
            }
        }
    ''')

    try:
        result = client.execute(query)

        total_customers = result['totalCustomers']['totalCount']
        total_orders = result['totalOrders']['totalCount']
        orders_edges = result['totalOrders'].get('edges', [])

        total_revenue = 0
        for edge in orders_edges:
            total_revenue += float(edge['node']['totalAmount'])

        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_line = f"{now} - Report: {total_customers} customers, {total_orders} orders, {total_revenue:.2f} revenue\n"

        with open('/tmp/crm_report_log.txt', 'a') as f:
            f.write(log_line)

        return log_line

    except Exception as e:
        error_line = f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - ERROR generating report: {e}\n"
        with open('/tmp/crm_report_log.txt', 'a') as f:
            f.write(error_line)
        logger.error(error_line)
        raise e
