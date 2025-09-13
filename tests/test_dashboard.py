# Simple smoke test for dashboard app factory
import pandas as pd
from networkflow.dashboard_app import create_dash_app

def test_dashboard_factory():
    df = pd.DataFrame({'src_ip':[], 'dst_ip':[], 'bytes':[], 'timestamp':[]})
    app = create_dash_app(lambda: df)
    assert app is not None

