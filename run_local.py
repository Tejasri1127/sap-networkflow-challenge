# run_local.py (quick test)
import pandas as pd
from networkflow.dashboard_app import create_dash_app

df = pd.read_csv("sample_logs/sample_nsg_log.csv")
app = create_dash_app(lambda: df)
app.run_server(port=8050, debug=True)

