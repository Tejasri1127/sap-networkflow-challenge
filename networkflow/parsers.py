"""
parsers.py
Functions to read and decompress zipped CSV NSG logs from Azure Blob Storage.
Supports .zip, .gz, and plain .csv blobs. Uses retry/backoff for blob downloads.
"""
import io
import zipfile
import gzip
import logging
from typing import Iterator, Optional
import pandas as pd
from azure.storage.blob import ContainerClient
from tenacity import retry, wait_exponential, stop_after_attempt

logger = logging.getLogger(__name__)

def get_container_client(account_name: str, container: str, sas_token: Optional[str] = None) -> ContainerClient:
    account_url = f"https://{account_name}.blob.core.windows.net"
    if sas_token:
        return ContainerClient(account_url=account_url, container_name=container, credential=sas_token)
    # If no SAS token, ContainerClient will use environment/default credentials if present
    return ContainerClient(account_url=account_url, container_name=container)

@retry(wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(3))
def download_blob_bytes(container_client: ContainerClient, blob_name: str) -> bytes:
    blob = container_client.get_blob_client(blob_name)
    stream = blob.download_blob()
    return stream.readall()

def iter_csv_dfs_from_container(container_client: ContainerClient, prefix: Optional[str] = None) -> Iterator[pd.DataFrame]:
    """Yield pandas DataFrames for each CSV found inside blobs (.zip, .gz, .csv)."""
    for blob in container_client.list_blobs(name_starts_with=prefix):
        name = blob.name.lower()
        if not (name.endswith('.zip') or name.endswith('.gz') or name.endswith('.csv')):
            continue
        logger.info('Processing blob: %s', blob.name)
        raw = download_blob_bytes(container_client, blob.name)
        if name.endswith('.zip'):
            with zipfile.ZipFile(io.BytesIO(raw)) as z:
                for member in z.namelist():
                    if member.lower().endswith('.csv'):
                        with z.open(member) as fh:
                            df = pd.read_csv(fh)
                            yield normalize_df_columns(df)
        elif name.endswith('.gz'):
            with gzip.GzipFile(fileobj=io.BytesIO(raw)) as gz:
                df = pd.read_csv(gz)
                yield normalize_df_columns(df)
        else:
            df = pd.read_csv(io.BytesIO(raw))
            yield normalize_df_columns(df)

def normalize_df_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize likely column names to canonical set used by analyzer/dashboard."""
    mapping = {}
    low = {c.lower(): c for c in df.columns}
    def pick(*candidates):
        for c in candidates:
            k = c.lower()
            if k in low:
                return low[k]
        return None
    # common picks
    mapping['src_ip'] = pick('src_ip', 'sourceip', 'src', 'source_ip', 'srcip') or 'src_ip'
    mapping['dst_ip'] = pick('dst_ip', 'destinationip', 'dst', 'destination_ip', 'dstip') or 'dst_ip'
    mapping['src_port'] = pick('src_port', 'sourceport', 'sport') or 'src_port'
    mapping['dst_port'] = pick('dst_port', 'destinationport', 'dport') or 'dst_port'
    mapping['protocol'] = pick('protocol', 'proto') or 'protocol'
    mapping['flow_decision'] = pick('flow_decision', 'decision', 'action') or 'flow_decision'
    mapping['flow_state'] = pick('flow_state', 'state') or 'flow_state'
    mapping['packets'] = pick('packets', 'packet_count', 'pkt') or 'packets'
    mapping['bytes'] = pick('bytes', 'byte_count', 'octets') or 'bytes'
    mapping['timestamp'] = pick('timestamp', 'time', 'time_generated') or 'timestamp'
    # build rename map
    rename = {}
    for canon, orig in mapping.items():
        if orig in df.columns and orig != canon:
            rename[orig] = canon
    df = df.rename(columns=rename)
    # ensure timestamp is datetime
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    return df

