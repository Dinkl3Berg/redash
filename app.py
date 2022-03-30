import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash_html_components.Div import Div
import plotly.express as px
import pandas as pd
import requests
import html as ht
import plotly.graph_objects as go
import json
from dash.dependencies import Input, Output
api_ip = "http://192.168.178.51:5000"
#api_ip = "http://127.0.0.1:5000"
db_tables = ['sale_flat', 'sale_house', 'rent_flat', 'rent_house']
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])



# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options
@app.callback(Output('recent-entries-fig', 'figure'), Input('interval-component', 'n_intervals'))
def recent_entries_fig(n):
    alldf = pd.DataFrame()
    for table in db_tables:
        ds = pd.read_json(requests.get(f'{api_ip}/stats/entries-recent/{table}').text, typ="series")
        ds = ds.rename("data")
        alldf[table] = ds

    fig=px.line(alldf, labels={'index':'Einträge in den letzten 10 Tagen', 'value':'Anzahl'})
    fig.update_layout(legend_title="Tabelle")
    return fig

def total_entries_fig():
    totalentriesdf = pd.read_json(requests.get(f'{api_ip}/stats/entries-all/').text, typ="series")
    fig = px.bar(totalentriesdf, labels={'index':'Alle Einträge pro Kategorie', 'value':'Anzahl'})
    fig.update_traces(texttemplate='%{value:,}', textposition='outside')
    fig.update_layout(showlegend=False)

    graph = dbc.Card(
                    dbc.CardBody([html.Div(className="shadow p-3 mb-5 bg-body rounded",  children=[
                                dcc.Graph(
                                    figure=fig
                    )])]),
                    className="mt-3",
                    )
    return graph

def unscraped_entries_fig():
    entriesunscrapeddf =  pd.read_json(requests.get(f'{api_ip}/stats/entries-unscraped/').text, typ="series")
    fig = px.bar(entriesunscrapeddf, labels={'index':'Ungescrapte Einträge pro Kategorie', 'value':'Anzahl'})
    fig.update_traces(texttemplate='%{value:,}', textposition='outside')
    fig.update_layout(showlegend=False)

    graph = dbc.Card(
                    dbc.CardBody([html.Div(className="shadow p-3 mb-5 bg-body rounded",  children=[
                        dcc.Graph(
                            figure=fig
                    )])]),
                    className="mt-3",
                    )
    return graph

@app.callback(Output('graph-tabs', 'children'), Input('interval-component', 'n_intervals'))
def graph_tabs(n):
    graph_tabs = dbc.Tabs(
        [
            dbc.Tab(total_entries_fig(), label="Total Entries"),
            dbc.Tab(unscraped_entries_fig(), label="Unscraped Entries"),
        ]
    	)
    return graph_tabs

@app.callback(Output('logs-text', 'children'), Input('interval-component', 'n_intervals'))
def logs_text(n):
    logs = requests.get(f'{api_ip}/stats/recent-err').text
    logs = logs.replace("\\n", "\n").replace("\\t", "\t")
    return logs

@app.callback(Output('running-nodes-tab', 'figure'), Input('interval-component', 'n_intervals'))
def running_nodes_tab(n):
    nodes = json.loads(requests.get(f'{api_ip}/stats/current-nodes/').text)
    running_nodes_table = go.Figure(data=[go.Table(header=dict(values=['Table', 'Nodes']),
                        cells=dict(values=[list(nodes.keys()), list(nodes.values())]))
                             ])
    return running_nodes_table

@app.callback(Output('bad-proxies-tab', 'figure'), Input('interval-component', 'n_intervals'))
def bad_proxies_tab(n):                         
    #requests.get(f'{api_ip}/stats/current-nodes/'
    bad_proxies = json.loads(requests.get(f'{api_ip}/stats/bad-proxy/').text)
    bad_proxy_table = go.Figure(data=[go.Table(header=dict(values=['proxy', 'number of failures']),
                        cells=dict(values=[list(bad_proxies.keys()),list(bad_proxies.values())]))
                         ])
    return bad_proxy_table

app.layout = html.Div(className="container-fluid", children=[
     dcc.Interval(
            id='interval-component',
            interval=60*60*1000, # in milliseconds
            n_intervals=0
        ),
    html.Div(className="row", children=[
        html.Div(className="col-6", children=[
            html.Div(className="shadow p-3 mb-5 bg-body rounded overflow-auto", id='logs-text',
                    style={"white-space": "pre","height": "50vh"}),
            dcc.Graph(id='bad-proxies-tab'),
            dcc.Graph(id='running-nodes-tab'),

        ]),
        
        html.Div(className="col-6", children=[
            html.Div(className="shadow p-3 mb-5 bg-body rounded", children=[
                dcc.Graph(
                    id='recent-entries-fig'
                )
            ]),
            html.Div(id='graph-tabs')
        ])
    ])
])

if __name__ == '__main__':
    #app.run_server(port=8050, host='0.0.0.0')
    app.run_server(port=8050, debug=True)