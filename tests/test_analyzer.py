import pandas as pd
from networkflow import analyzer

def sample_df():
    return pd.DataFrame({
        'src_ip': ['1.1.1.1','1.1.1.2','1.1.1.1'],
        'dst_ip': ['2.2.2.2','2.2.2.3','2.2.2.2'],
        'bytes': [100,200,300],
        'flow_decision': ['Allow','Deny','Allow'],
        'timestamp': ['2025-01-01T00:00:00Z','2025-01-01T01:00:00Z','2025-01-01T02:00:00Z']
    })

def test_top_talkers():
    df = sample_df()
    res = analyzer.top_talkers(df, by='bytes', n=2)
    assert res.iloc[0]['src_ip'] == '1.1.1.1'

def test_denied_flows():
    df = sample_df()
    denied = analyzer.denied_flows(df)
    assert not denied.empty

