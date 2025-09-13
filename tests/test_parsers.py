import pandas as pd
from networkflow.parsers import normalize_df_columns

def test_normalize_columns():
    df = pd.DataFrame({'Src_IP': ['1.1.1.1'], 'Dst_IP': ['2.2.2.2'], 'timestamp': ['2025-01-01T00:00:00Z'], 'bytes': [100]})
    out = normalize_df_columns(df)
    assert 'src_ip' in out.columns
    assert 'dst_ip' in out.columns
    assert out['timestamp'].dtype.kind == 'M'  # datetime

