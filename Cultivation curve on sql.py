import pandas as pd
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_daq as daq
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from sqlalchemy import create_engine
import config
import function

# -----------------------------------------------------------------------------
# guidebook = pd.DataFrame(function.get_query(function.sql_query.format("series, vessel")), columns=['series', 'vessel'])
guidebook = pd.DataFrame(function.get_query(function.sql_query),
                         columns=['file_time', 'series', 'series_code', 'vessel', 'name_medicinal_product'])
guidebook = guidebook.fillna('-')
df = pd.DataFrame()
seria = function.unique(guidebook['series'].values)
list_seria = list({'label': sr, 'value': sr} for sr in seria)
name = function.unique(guidebook['name_medicinal_product'].values)
list_name = list({'label': _, 'value': _} for _ in name)
# -----------------------------------------------------------------------------
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.H1(children='SPC: Cultivation curve', style={'textAlign': 'center'}),

    html.Div(children='''
        Cultivation curve: A web application for monitoring cultivation parameter.
    ''', style={'textAlign': 'center'}),
    html.Label('Select name product'),
    dcc.Dropdown(id='select_name',
                 options=list_name,
                 multi=True,
                 value=["БЕВАЦИЗУМАБ, субстанция"]),
    html.Br(),
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
    dash_table.DataTable(
        id="table",
        columns=[{"name": i, "id": i} for i in df.columns],
        data=df.to_dict("records"),
        export_format="xlsx",
    )
], style={'columnCount': 1})


@app.callback(
    Output('select_seria', 'options'),
    Output('select_procedure', 'options'),
    Output('subplot', 'figure'),
    Output('table', 'data'),
    Output('table', 'columns'),
    Input('select_name', 'value'),
    Input('select_seria', 'value'),
    Input('select_procedure', 'value'),
    Input('select_parameter', 'value'),
    Input('submit_button', 'n_clicks'),
    Input('boolean_switch', 'value'))
def update_layout(name, series, vessel, parameter, click, switch):
    seria = set(guidebook[guidebook['name_medicinal_product'].isin(list(name))]['series'].values)
    list_seria = list({'label': sr, 'value': sr} for sr in seria)
    procedure = set(guidebook[guidebook['series'].isin(list(series))]['vessel'].values)
    list_procedure = list({'label': proc, 'value': proc} for proc in procedure)

    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'submit_button' in changed_id:
        df = function.get_df(series, vessel, parameter)
        if switch:
            fig = function.plot_graph_on_one(series, vessel, parameter, df)
        else:
            fig = function.plot_graph_on_sub(series, vessel, parameter, df)
    else:
        df = pd.DataFrame()
        fig = {}
    data = df.to_dict("records")
    columns = [{"name": i, "id": i} for i in df.columns]
    return list_seria, list_procedure, fig, data, columns


if __name__ == '__main__':
    app.run_server(debug=True)
