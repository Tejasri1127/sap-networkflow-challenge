# networkflow/parsers.py
import io, zipfile, gzip, tempfile, logging
from typing import Iterator
import pandas as pd
from azure.storage.blob import ContainerClient
from azure.identity import DefaultAzureCredential
from tenacity import retry, wait_exponential, stop_after_attempt

logger = logging.getLogger(__name__)

def get_container_client(account_name: str, container: str, sas_token: str = None) -> ContainerClient:
    account_url = f"https://{account_name}.blob.core.windows.net"
    if sas_token:
        return ContainerClient(account_url=account_url, container_name=container, credential=sas_token)
    credential = DefaultAzureCredential()
    return ContainerClient(account_url=account_url, container_name=container, credential=credential)

@retry(wait=wait_exponential(multiplier=1, min=2, max=30), stop=stop_after_attempt(4))
def download_blob_to_bytes(container_client: ContainerClient, blob_name: str) -> bytes:
    blob = container_client.get_blob_client(blob_name)
    stream = blob.download_blob()
    data = stream.readall()
    return data

def iter_csv_dfs_from_container(container_client: ContainerClient, prefix: str = None) -> Iterator[pd.DataFrame]:
    """
    Yields DataFrames for every CSV found inside zipped blobs (.zip or .gz) in the container.
    """
    for blob_props in container_client.list_blobs(name_starts_with=prefix):
        name = blob_props.name.lower()
        if not (name.endswith('.zip') or name.endswith('.gz') or name.endswith('.csv')):
            continue
        logger.info("Processing blob: %s", blob_props.name)
        raw = download_blob_to_bytes(container_client, blob_props.name)
        if name.endswith('.zip'):
            z = zipfile.ZipFile(io.BytesIO(raw))
            for member in z.namelist():
                if member.lower().endswith('.csv'):
                    with z.open(member) as fh:
                        df = pd.read_csv(fh)
                        yield normalize_df_columns(df)
        elif name.endswith('.gz'):
            with gzip.GzipFile(fileobj=io.BytesIO(raw)) as gz:
                df = pd.read_csv(gz)
                yield normalize_df_columns(df)
        else:  # plain CSV
            df = pd.read_csv(io.BytesIO(raw))
            yield normalize_df_columns(df)

def normalize_df_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Map likely column names to canonical names used by analyzer/dashboard.
    Canonical columns: subscription, resource_group, nsg_name, src_ip, src_port,
    dst_ip, dst_port, protocol, flow_decision, flow_state, packets, bytes, timestamp
    """
    mapping = {}
    low_to_col = {c.lower(): c for c in df.columns}
    def pick(*candidates):
        for c in candidates:
            k = c.lower()
            if k in low_to_col:
                return low_to_col[k]
        return None

    mapping_src = pick('src', 'src_ip', 'sourceip', 'source_ip', 'srcip')
    mapping_dst = pick('dst', 'dst_ip', 'destinationip', 'destination_ip', 'dstip')
    # ... add more picks
    mapping['src_ip'] = mapping_src or 'src_ip'
    mapping['dst_ip'] = mapping_dst or 'dst_ip'
    # Map other fields; if not found leave them as-is so downstream can handle
    col_map = {}
    for canon, original in mapping.items():
        if original in df.columns:
            col_map[original] = canon
    df = df.rename(columns=col_map)
    # Ensure timestamp exists and is datetime
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    return df

