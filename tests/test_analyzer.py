import pandas as pd
from networkflow import analyzer


def sample_df():
    return pd.DataFrame(
        {
            "src_ip": ["1.1.1.1", "1.1.1.1", "2.2.2.2", "3.3.3.3", "1.1.1.1"],
            "dst_ip": ["5.5.5.5", "5.5.5.5", "6.6.6.6", "7.7.7.7", "5.5.5.5"],
            "bytes": [100, 50, 300, 200, 50],
            "flow_decision": ["Allow", "Deny", "Allow", "Allow", "Allow"],
            "timestamp": pd.date_range("2025-01-01", periods=5, freq="h"),
        }
    )


def test_top_talkers():
    df = sample_df()
    result = analyzer.top_talkers(df, n=1)
    assert result.iloc[0]["src_ip"] == "2.2.2.2"
    assert result.iloc[0]["bytes"] == 300


def test_denied_flows():
    df = sample_df()
    result = analyzer.denied_flows(df)
    assert len(result) == 1
    assert result.iloc[0]["flow_decision"] == "Deny"


def flows_per_hour(df: pd.DataFrame) -> pd.DataFrame:
    """Return number of flows grouped by hour."""
    if not pd.api.types.is_datetime64_any_dtype(df["timestamp"]):
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce", utc=True)

    return (
        df.set_index("timestamp")
        .resample("1h")  # lowercase 'h' to avoid FutureWarning
        .size()
        .reset_index(name="flow_count")
    )

