import click
import pandas as pd
from networkflow.parsers import get_container_client, iter_csv_dfs_from_container, normalize_df_columns
from networkflow.dashboard_app import create_dash_app

# 1️⃣ Define the CLI group first
@click.group()
def cli():
    """Network Flow CLI"""
    pass

# 2️⃣ Add commands AFTER cli() is defined
@cli.command()
@click.option("--storage-account", required=True)
@click.option("--container", required=True)
@click.option("--sas-token", default=None)
def dashboard(storage_account, container, sas_token):
    """Run the Dash dashboard."""
    container_client = get_container_client(storage_account, container, sas_token)
    dfs = [normalize_df_columns(df) for df in iter_csv_dfs_from_container(container_client)]
    data = pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()
    app = create_dash_app(lambda: data)
    app.run(host="0.0.0.0", port=8050, debug=True)

# 3️⃣ Main entry point
if __name__ == "__main__":
    cli()

