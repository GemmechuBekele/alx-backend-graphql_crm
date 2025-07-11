import datetime
import requests

def log_crm_heartbeat():
    now = datetime.datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    message = f"{now} CRM is alive"

    # Optional GraphQL query to hello field
    try:
        response = requests.post(
            "http://localhost:8000/graphql",
            json={'query': '{ hello }'},
            timeout=5
        )
        if response.status_code == 200 and 'data' in response.json():
            message += " - GraphQL OK"
        else:
            message += " - GraphQL FAIL"
    except Exception as e:
        message += f" - GraphQL ERROR: {e}"

    with open("/tmp/crm_heartbeat_log.txt", "a") as f:
        f.write(message + "\n")
