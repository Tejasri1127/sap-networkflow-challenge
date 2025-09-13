"""Simple Dash app factory that builds basic charts from a DataFrame loader."""

from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd
from . import analyzer

def create_dash_app(data_loader):
    app = Dash(__name__, suppress_callback_exceptions=True)
    df = data_loader()
    subs = ['All']
    if 'subscription' in df.columns:
        subs = ['All'] + sorted(df['subscription'].dropna().unique().tolist())
    app.layout = html.Div([
        html.H2('Network Flow Dashboard'),
        html.Div([
            dcc.Dropdown(subs, id='subscription-filter', value='All'),
            dcc.DatePickerRange(id='daterange')
        ], style={'display': 'flex', 'gap': '1rem'}),
        dcc.Tabs([
            dcc.Tab(label='Top Talkers', children=[dcc.Graph(id='top-talkers')]),
            dcc.Tab(label='Top Listeners', children=[dcc.Graph(id='top-listeners')]),
            dcc.Tab(label='Denied Flows', children=[dcc.Graph(id='denied-pie')]),
            dcc.Tab(label='Time-series', children=[dcc.Graph(id='flows-timeseries')])
        ]),
        html.Div(id='summary')
    ])

    @app.callback(
        Output('top-talkers', 'figure'),
        Input('subscription-filter', 'value'),
        Input('daterange', 'start_date'),
        Input('daterange', 'end_date'),
    )
    def update_top_talkers(subscription, start, end):
        d = df.copy()
        if subscription and subscription != 'All' and 'subscription' in d.columns:
            d = d[d['subscription'] == subscription]
        if start:
            d = d[pd.to_datetime(d['timestamp']) >= pd.to_datetime(start)]
        if end:
            d = d[pd.to_datetime(d['timestamp']) <= pd.to_datetime(end)]
        top = analyzer.top_talkers(d, by='bytes', n=10)
        if top.empty:
            return px.bar()
        fig = px.bar(top, x='src_ip', y=top.columns[1], labels={'src_ip': 'Source IP', top.columns[1]: 'Bytes'})
        return fig

    @app.callback(Output('top-listeners', 'figure'),
                  Input('subscription-filter', 'value'))
    def update_listeners(subscription):
        d = df.copy()
        if subscription and subscription != 'All' and 'subscription' in d.columns:
            d = d[d['subscription'] == subscription]
        top = analyzer.top_listeners(d, by='bytes', n=10)
        if top.empty:
            return px.bar()
        fig = px.bar(top, x='dst_ip', y=top.columns[1], labels={'dst_ip': 'Dest IP', top.columns[1]: 'Bytes'})
        return fig

    @app.callback(Output('denied-pie', 'figure'), Input('subscription-filter', 'value'))
    def update_denied(subscription):
        d = df.copy()
        if subscription and subscription != 'All' and 'subscription' in d.columns:
            d = d[d['subscription'] == subscription]
        denied = analyzer.denied_flows(d)
        if denied.empty:
            return px.pie()
        counts = denied['flow_decision'].value_counts().reset_index()
        counts.columns = ['decision','count']
        return px.pie(counts, names='decision', values='count', title='Denied / Dropped Flows')

    @app.callback(Output('flows-timeseries', 'figure'), Input('subscription-filter', 'value'))
    def update_timeseries(subscription):
        d = df.copy()
        if subscription and subscription != 'All' and 'subscription' in d.columns:
            d = d[d['subscription'] == subscription]
        ts = analyzer.flows_per_hour(d)
        if ts.empty:
            return px.line()
        fig = px.line(x=ts.index, y=ts.values, labels={'x': 'Hour', 'y': 'Flows'})
        return fig

    return app

