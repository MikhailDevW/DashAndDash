import os
from datetime import datetime
from pathlib import Path

from pandas.core.frame import DataFrame
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sqlite3

from templates import timeline_template


BASE_DIR = Path(__file__).resolve().parent.parent
DB_NAME = 'testDB.db'


def get_data_frame() -> DataFrame:
    """
    Получение датафрейм из базы данных SQLite.
    """
    try:
        con = sqlite3.connect(os.path.join(BASE_DIR, DB_NAME))

        with con:
            df = pd.read_sql('SELECT * FROM sources', con)
    except sqlite3.OperationalError as error:
        print(error)
        exit()
    except Exception as e:
        print(e)
        exit()
    else:
        return df


def get_period(df: DataFrame) -> set[str]:
    """
    Функция получения времени и даты начала и заврешения периода работы.
    """
    start_period = datetime.strptime(
        min(df['state_begin']), '%Y-%m-%d %H:%M:%S.%f'
    )
    end_period = datetime.strptime(
        max(df['state_end']), '%Y-%m-%d %H:%M:%S.%f'
    )
    str_start = (
        f'{start_period.time()} ({start_period.day}.{start_period.month})')
    str_end = f'{end_period.time()} ({end_period.day}.{end_period.month})'
    return str_start, str_end


def get_base_info(df: DataFrame) -> set:
    return (
        f'Клиента: {df["client_name"][0]}',
        f'Сменный день: {df["shift_day"][0]}',
        f'Точка учета: {df["endpoint_name"][0]}',
        f'Начало периода: {get_period(df)[0]}',
        f'Конец периода: {get_period(df)[1]}',

        get_pie_figure(df),
        get_timeline_figure(df)
    )


def get_pie_figure(df: DataFrame) -> go.Figure:
    """
    Построение круговой диаграммы на основе водного датафрейма (df).
    """
    pie_figure = go.Figure(
        data=[
            go.Pie(
                labels=df['reason'],
                values=df['duration_min'],
                hole=.2
            )
        ],
    )
    pie_figure.update_traces(
        hoverinfo='label+percent',
        textinfo='percent',
        marker=dict(colors=df['color'], )
    )
    return pie_figure


def get_timeline_figure(df: DataFrame):
    timeline = px.timeline(
        df,
        x_start='state_begin',
        x_end='state_end',
        y='endpoint_name',
        color='reason',
        color_discrete_map=dict(
            zip(df['reason'].unique(), df['color'].unique())),
        custom_data=df[
            [
                'state', 'reason', 'state_begin',
                'duration_min', 'shift_day', 'operator'
            ]
        ],
    )
    timeline.update_layout(
        xaxis={
            'side': 'top',
            'dtick': 3.6e+6,
            'tickangle': 0,
        },
        yaxis={
            'dtick': 3.6e+6,
        },
        showlegend=False,
    )
    timeline.update_traces(
        hovertemplate=timeline_template,
    )
    timeline.layout.yaxis.visible = False
    return timeline
