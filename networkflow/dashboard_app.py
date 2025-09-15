import dash
from dash import dcc, html
import pandas as pd
import plotly.express as px

def create_dash_app(data_loader):
    df = data_loader()
    app = dash.Dash(__name__)

    app.layout = html.Div([
        html.H1("Network Flow Dashboard"),
        dcc.Graph(
            id="example-graph",
            figure=px.histogram(df, x="src_ip") if not df.empty else {}
        )
    ])
    return app

