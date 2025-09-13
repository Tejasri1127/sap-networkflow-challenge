import click
from .parsers import get_container_client, iter_csv_dfs_from_container
from .dashboard_app import create_dash_app
import pandas as pd

@click.group()
def cli():
    pass

@cli.command('dashboard')
@click.option('--storage-account', required=True)
@click.option('--container', required=True)
@click.option('--sas-token', default=None)
@click.option('--host', default='0.0.0.0')
@click.option('--port', default=8050)
def dashboard(storage_account, container, sas_token, host, port):
    """Launch dashboard using data from Azure Blob storage."""
    cc = get_container_client(storage_account, container, sas_token)
    dfs = []
    for df in iter_csv_dfs_from_container(cc):
        dfs.append(df)
    if not dfs:
        click.echo('No CSV logs found in container.')
        return
    full = pd.concat(dfs, ignore_index=True)
    app = create_dash_app(lambda: full)
    app.run_server(host=host, port=port, debug=False)

if __name__ == '__main__':
    cli()

