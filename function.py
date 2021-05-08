import pandas as pd
import numpy as np
from plotly.subplots import make_subplots
from sqlalchemy import create_engine
import plotly.graph_objs as go
import config

list_parametr = [{'label': 'Total cells', 'value': 'total_cells'},
                 {'label': 'Total cells per ml', 'value': 'total_cells_per_ml'},
                 {'label': 'Average circularity', 'value': 'average_circularity'},
                 {'label': 'Average diameter', 'value': 'average_diameter'},
                 {'label': 'Viability', 'value': 'viability'},
                 {'label': 'Viable cells', 'value': 'viable_cells'},
                 {'label': 'Viable cells per ml', 'value': 'viable_cells_per_ml'}]

sql_query = "Some select sql were we take all data"
sql_query_where = "Some select sql where we choose data"
str_col = 'file_time,timediff,sample_id,series,vessel,seriavessel,numbers'

def unique(sequence):
    """
    Функция для создания множества с сохранением порядка элементов
    """
    seen = set()
    return [x for x in sequence if not (x in seen or seen.add(x))]

def get_query(sql):
    """
    Функция для осуществления SQL запроса
    """
    alchemy_engine = create_engine(config.sql_db, pool_recycle=3600)
    cluster_connection = alchemy_engine.connect()
    result = cluster_connection.execute(sql)
    cluster_connection.close()
    return result


def get_df(series, vessel, parameter):
    str_param = str_col + ',' + ','.join(parameter)
    tp_series = tuple(series)
    tp_vessel = tuple(vessel)
    if len(series) < 2:
        if len(vessel) < 2:
            df = pd.DataFrame(get_query(
                sql_query_where.format(str_param, '(\'' + str(series[0]) + '\')', '(\'' + str(vessel[0]) + '\')')),
                columns=list(str_param.split(',')))
        else:
            df = pd.DataFrame(get_query(
                sql_query_where.format(str_param, '(\'' + str(series[0]) + '\')', tp_vessel)),
                columns=list(str_param.split(',')))
    elif len(series) >= 2:
        if len(vessel) < 2:
            df = pd.DataFrame(get_query(
                sql_query_where.format(str_param, tp_series, '(\'' + str(vessel[0]) + '\')')),
                columns=list(str_param.split(',')))
        else:
            df = pd.DataFrame(get_query(sql_query_where.format(str_param, tp_series, tp_vessel)),
                              columns=list(str_param.split(',')))
    df = df.sort_values(by=['timediff'])
    return df


def plot_graph_on_sub(series, vessel, parameter, df):
    splot_title = list((val.replace('_', ' ').capitalize()) for val in parameter)
    fig = make_subplots(rows=len(parameter), cols=1, subplot_titles=['Subplot graph'], vertical_spacing=0.1,
                        x_title='Время от начала процесса (часы)', )
    for graph in range(1, len(parameter) + 1):
        param = parameter[graph - 1]
        for ser in series:
            for ves in vessel:
                fig.append_trace(
                    go.Scatter(x=df[(df['vessel'] == ves) & (df['series'] == ser)]['timediff'],
                               y=df[(df['vessel'] == ves) & (df['series'] == ser)][param],
                               mode='lines+markers',
                               hovertemplate=
                               "Sample Name: %{text[0]}<extra></extra>" +
                               "<br>Sample Time: %{text[1]}" +
                               "<br>Sample Value: %{text[2]}",
                               text=df[(df['vessel'] == ves) & (df['series'] == ser)][
                                   ['sample_id', 'file_time', param]],
                               name=str(ser + '-' + ves)),
                    row=graph, col=1)
        fig.update_yaxes(title_text=splot_title[graph - 1], row=graph, col=1)
    fig.update_layout(height=400 * len(parameter) + 1)

    return fig


def plot_graph_on_one(series, vessel, parameter, df):
    i = 0
    for ser in series:
        temp_df = df[df['series'] == ser]
        start_time = pd.to_datetime(temp_df['file_time']).min()
        temp_df['one_timediff'] = pd.to_datetime(temp_df['file_time']) - start_time
        temp_df['one_timediff'] = temp_df['one_timediff'] / np.timedelta64(1, 'h')
        if i == 0:
            new_df = temp_df
            i += 1
        else:
            new_df = new_df.append(temp_df)
    df = new_df
    splot_title = list((val.replace('_', ' ').capitalize()) for val in parameter)
    index_axes_position = list(range(len(splot_title)))
    index_axes = list(str(i + 1) for i in list(range(len(splot_title))))

    fig = make_subplots(specs=[[{"secondary_y": True}]], subplot_titles=['Multiple-axes graph'])

    for graph in range(1, len(parameter) + 1):
        param = parameter[graph - 1]
        for ser in series:
            for ves in vessel:
                fig.add_trace(go.Scatter(x=df[(df['vessel'] == ves) & (df['series'] == ser)]['one_timediff'],
                                         y=df[(df['vessel'] == ves) & (df['series'] == ser)][param],
                                         mode='lines+markers',
                                         hovertemplate=
                                         "Sample Name: %{text[0]}<extra></extra>" +
                                         "<br>Sample Time: %{text[1]}" +
                                         "<br>Sample Value: %{text[2]}",
                                         text=df[(df['vessel'] == ves) & (df['series'] == ser)][
                                             ['sample_id', 'file_time', param]],
                                         name=str(ser + '-' + ves),
                                         yaxis="y" + str(graph))

                              )

    fig.update_layout(
        xaxis=dict(
            domain=[len(splot_title) * 0.05, 1]
        ),
        yaxis1=dict(
            title=splot_title[0],
            side="left",
            position=0.0,

        ))
    for i in list(range(len(splot_title))):
        if index_axes[i] != '1':
            fig.layout['yaxis' + index_axes[i]] = {
                'overlaying': 'y',
                'position': 0.05 * (index_axes_position[i] + 0.01),
                'side': 'left',
                'title': {'text': splot_title[i]},
            }

    fig.update_layout(
        height=700)
    fig.update_xaxes(title_text="Время от начала самого раннего процесса (часы)")

    return fig
