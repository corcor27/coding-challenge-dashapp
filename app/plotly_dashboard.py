import numpy as np
import os
import pandas as pd

import dash
import plotly.graph_objects as go # or plotly.express as px
import dash_auth
from dash import Dash, html, dcc, callback, Input, Output, State, callback, ctx
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
import io
from googleapiclient.http import MediaIoBaseDownload
from datetime import date


Title = "CDT AIMLAC Presents: The Fuel Feud Competition"

def download_table_file():
    ###script uses ssh key to access google drive and download file as id as below
    SCOPES = ['https://www.googleapis.com/auth/drive']
    SERVICE_ACCOUNT_FILE = "/app/gdrive_key.json"
    credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('drive', 'v3', credentials=credentials)
    file_id = "1ZKtf2456yjtGPND7qpQxpoNSbvp9R809Y6Zpbz5-ApE"
    request = service.files().export_media(fileId=file_id,
                                           mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    file = io.BytesIO()
    downloader = MediaIoBaseDownload(file, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print(F'Download {int(status.progress() * 100)}.')
    file_retrieved: str = file.getvalue()
    data = pd.read_excel(io.BytesIO(file_retrieved))
    return data

def download_history_file():
    ###script uses ssh key to access google drive and download file as id as below
    SCOPES = ['https://www.googleapis.com/auth/drive']
    SERVICE_ACCOUNT_FILE = "/app/gdrive_key.json"
    credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('drive', 'v3', credentials=credentials)
    file_id = "10nSK75_co2upSvGez3FXdzJwxvZWciKZKFq7tCsdOLM"
    request = service.files().export_media(fileId=file_id,
                                           mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    file = io.BytesIO()
    downloader = MediaIoBaseDownload(file, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print(F'Download {int(status.progress() * 100)}.')
    file_retrieved: str = file.getvalue()
    data = pd.read_excel(io.BytesIO(file_retrieved))
    return data


def create_history_plot(data, teams):
    ### create history chart that displays the balance history of the team
    fig = go.Figure()
    dashing_options = ["dash", "dot", "dashdot"]
    colour_options = ["green", "blue", "purple"]
    fig.add_trace(go.Scatter(x=data["Time"], y=data[teams[0]], name=teams[0], line=dict(color='firebrick', width=4)))
    teams.pop(0)
    for num in range(0, len(teams)):
        fig.add_trace(go.Scatter(x=data["Time"], y=data[teams[num]], name=teams[num], line=dict(color=colour_options[num-2], width=4, dash = dashing_options[num-2])))
    fig.update_layout(title='Profit/Loss Team Record',
                   xaxis_title='Profit/Loss (Pounds)',
                   yaxis_title='Time (Days)')
    return fig


fake_history = download_history_file()
df = download_table_file()
teams = list(fake_history.columns)[1:]

### create app layout: title, leaderboard tile, leaderboard table of performence that pulls from the history data, table of teams history, then weather
app = dash.Dash(__name__)

VALID_USERNAME_PASSWORD_PAIRS = {
    "CDT": "CCV5",
}
auth = dash_auth.BasicAuth(
    app,
    VALID_USERNAME_PASSWORD_PAIRS
)


app.layout = dash.html.Div([
    dash.html.H1(Title, style={'text-align':'center'}),
    dash.html.Button('Update', id='btn-nclicks', n_clicks=0, style={'font-size': '16px', 'width': '240px', 'display': 'inline-block', 'margin-bottom': '10px', 'margin-right': '5px', 'height':'50px'}),
    dash.html.Div(children = [dash.html.Div(id='save_stamp')]),
    dash.html.Div([dash.html.H1("Leaderboard Results", style={'text-align':'center'})]),
    dash.html.Div([dash.dash_table.DataTable(id='score_table', data = df.to_dict('records'),columns = [{"name": i, "id": i} for i in df.columns], editable=True,
                                                 style_data_conditional=[{'if': {'filter_query': "{24hr change} > 0",'column_id': '24hr change'},'backgroundColor': 'green','color': 'white'},
                                                                         {'if': {'filter_query': "{24hr change} < 0",'column_id': '24hr change'},'backgroundColor': 'red','color': 'white'},
                                                                         {'if': {'filter_query': "{history change} > 0",'column_id': 'history change'},'backgroundColor': 'green','color': 'white'},
                                                                         {'if': {'filter_query': "{history change} < 0",'column_id': 'history change'},'backgroundColor': 'red','color': 'white'}])]),
    
    dash.html.Div([dash.dcc.Graph(id='results_figure', figure=create_history_plot(fake_history, teams), style={'text-align':'center'})]),
    ])

@app.callback(Output('score_table','data'),
              Output('results_figure','figure'),
              Output('btn-nclicks', 'n_clicks'),
              Output('save_stamp', 'children'),
              Input('btn-nclicks', 'n_clicks'),)

def update_output(btn):

    fake_history = download_history_file()
    df = download_table_file()
    teams = list(fake_history.columns)[1:]
    results_figure = create_history_plot(fake_history, teams)
    today = date.today()

    return df.to_dict('records'), results_figure, 0, "last updated:{}".format(today)
    

if __name__ == '__main__':
    app.run_server(debug=True,  host='0.0.0.0', port=8050, use_reloader=False)

        
    
