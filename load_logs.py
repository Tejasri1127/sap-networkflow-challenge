from networkflow.parsers import load_nsg_flow_logs

# Replace these with your actual Azure Storage details
account_url = "https://mynsglogs123.blob.core.windows.net"
container_name = "insights-logs-networksecuritygroupflowevent"
sas_token = "se=2025-09-20T23%3A59%3A00Z&sp=rlc&spr=https&sv=2022-11-02&ss=b&srt=sco&sig=iBmB%2BYIBDnldKQsQcctwJrIa9Wu4gY/93JieLpNeRS4%3D"

# Load NSG flow logs into a DataFrame
df = load_nsg_flow_logs(account_url, container_name, prefix="", sas_token=sas_token)

# Print first few rows
print(df.head())

