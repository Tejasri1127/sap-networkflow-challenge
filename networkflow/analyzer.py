"""
analyzer.py
Aggregation and basic anomaly detection helpers.
"""
import pandas as pd
import numpy as np

def top_talkers(df: pd.DataFrame, by: str = 'bytes', n: int = 10) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=['src_ip', by])
    col = by if by in df.columns else df.columns[0]
    res = df.groupby('src_ip', dropna=False)[col].sum().reset_index().sort_values(col, ascending=False).head(n)
    return res

def top_listeners(df: pd.DataFrame, by: str = 'bytes', n: int = 10) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=['dst_ip', by])
    col = by if by in df.columns else df.columns[0]
    res = df.groupby('dst_ip', dropna=False)[col].sum().reset_index().sort_values(col, ascending=False).head(n)
    return res

def denied_flows(df: pd.DataFrame) -> pd.DataFrame:
    if 'flow_decision' not in df.columns:
        return df.iloc[0:0]
    mask = df['flow_decision'].astype(str).str.lower().str.contains('deny|drop|dropped')
    return df[mask].copy()

def flows_per_hour(df: pd.DataFrame) -> pd.Series:
    if 'timestamp' not in df.columns:
        return pd.Series(dtype=int)
    s = df.copy()
    s['hour'] = pd.to_datetime(s['timestamp']).dt.floor('H')
    return s.groupby('hour').size().sort_index()

def detect_spikes(ts: pd.Series, window: int = 24, z_thresh: float = 3.0):
    if ts.empty:
        return pd.DatetimeIndex([])
    rmean = ts.rolling(window=window, min_periods=1).mean()
    rstd = ts.rolling(window=window, min_periods=1).std().replace(0, np.nan)
    z = (ts - rmean) / rstd
    return z[z > z_thresh].index

def persistent_connections(df: pd.DataFrame, min_occurrences: int = 20, window_hours: int = 1) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()
    s = df.copy()
    s['timestamp'] = pd.to_datetime(s['timestamp'])
    s['hour_bucket'] = s['timestamp'].dt.floor(f"{window_hours}H")
    key_cols = ['src_ip','dst_ip','src_port','dst_port','protocol','hour_bucket']
    counts = s.groupby(key_cols).size().reset_index(name='occurrences')
    return counts[counts['occurrences'] >= min_occurrences]

