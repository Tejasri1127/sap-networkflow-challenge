from networkflow.dashboard_app import create_dash_app
from networkflow.parsers import load_nsg_flow_logs

# Configure your storage info here
ACCOUNT_URL = "https://<your_storage_account>.blob.core.windows.net"
CONTAINER_NAME = "insights-logs-networksecuritygroupflowevent"
SAS_TOKEN = "<your_sas_token>"

def data_loader():
    return load_nsg_flow_logs(
        account_url=ACCOUNT_URL,
        container_name=CONTAINER_NAME,
        sas_token=SAS_TOKEN,
        prefix=""
    )

if __name__ == "__main__":
    app = create_dash_app(data_loader)
    app.run_server(host="0.0.0.0", port=8050, debug=True)

