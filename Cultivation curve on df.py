import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_daq as daq
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import function
import config

# -----------------------------------------------------------------------------
df = pd.read_csv('Cultivation curve.csv')
df.dropna(inplace=True)
df.reset_index(drop=True)
seria = set(df['series'].values)
list_seria = list({'label': sr, 'value': sr} for sr in seria)
# -----------------------------------------------------------------------------
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.H1(children='Cultivation curve', style={'textAlign': 'center'}),

    html.Div(children='''
            Cultivation curve: A web application for monitoring cultivation parameter.
        ''', style={'textAlign': 'center'}),
    html.Label('Select series processes'),
    dcc.Dropdown(id='select_seria',
                 options=list_seria,
                 multi=True,
                 value=["90360920"]),
    html.Br(),
    html.Label('Select series procedure'),
    dcc.Dropdown(id='select_procedure',
                 options=[],
                 multi=True,
                 value=["kolba2000ml"]),
    html.Br(),
    html.Label('Select parameter'),
    dcc.Dropdown(id='select_parameter',
                 options=function.list_parametr,
                 multi=True,
                 value=["total_cells"]),
    html.Br(),
    html.Div(children=[
        html.Label('Switching between plot (left - sub plot, right - multiple-axes plot)'),
        daq.ToggleSwitch(
            id="boolean_switch",
            style={'width': '250px', 'margin': '0'},
            value=False,
        ),
        html.Br(),
        html.Button('Plot graphs', id='submit_button', n_clicks=0)], style={'columnCount': 2}),
    dcc.Graph(id='subplot',
              figure={}),
], style={'columnCount': 1})


@app.callback(
    Output('select_procedure', 'options'),
    Output('subplot', 'figure'),
    Input('select_seria', 'value'),
    Input('select_procedure', 'value'),
    Input('select_parameter', 'value'),
    Input('boolean_switch', 'value'))
def update_layout(series, vessel, parameter, switch):
    procedure = set(df[df['series'].isin(list(series))]['vessel'].values)
    list_procedure = list({'label': proc, 'value': proc} for proc in procedure)

    if len(vessel) > 0:
        target_df = df[(df['series'].isin(list(series))) & (df['vessel'].isin(list(vessel)))].copy()
        if switch:
            fig = function.plot_graph_on_one(series, vessel, parameter, target_df)
        else:
            fig = function.plot_graph_on_sub(series, vessel, parameter, target_df)
    else:
        fig = {}

    return list_procedure, fig


if __name__ == '__main__':
    app.run_server(debug=True)



