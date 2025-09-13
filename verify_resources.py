import sys
import argparse
from azure.storage.blob import ContainerClient
from azure.identity import DefaultAzureCredential
from azure.mgmt.containerinstance import ContainerInstanceManagementClient
from azure.mgmt.resource import SubscriptionClient

def container_exists(account, container):
    account_url = f"https://{account}.blob.core.windows.net"
    cc = ContainerClient(account_url=account_url, container_name=container, credential=DefaultAzureCredential())
    return cc.exists()

def find_aci(name):
    cred = DefaultAzureCredential()
    sub = next(SubscriptionClient(cred).subscriptions.list()).subscription_id
    client = ContainerInstanceManagementClient(cred, sub)
    for g in client.container_groups.list():
        if g.name == name:
            fqdn = getattr(g.ip_address, 'fqdn', None)
            return True, fqdn
    return False, None

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--storage', required=True)
    p.add_argument('--container', required=True)
    p.add_argument('--aci', required=True)
    args = p.parse_args()
    ok = container_exists(args.storage, args.container)
    ok_aci, fqdn = find_aci(args.aci)
    print('Container exists:', ok)
    print('ACI exists:', ok_aci, 'fqdn:', fqdn)
    sys.exit(0 if ok and ok_aci else 2)

if __name__ == '__main__':
    main()

