from dash import html, Output, Input, State, dcc, Patch
from dash_extensions.enrich import (DashProxy,
                                    ServersideOutputTransform,
                                    MultiplexerTransform)
import dash_mantine_components as dmc
from dash.exceptions import PreventUpdate

from utils import get_data_frame, get_base_info


CARD_STYLE = dict(
    withBorder=True,
    shadow="sm",
    radius="md",
    style={
        'height': '400px',
        'padding': '0px',
        'margin': '0px',
    }
)


class EncostDash(DashProxy):
    def __init__(self, **kwargs):
        self.app_container = None
        super().__init__(
            transforms=[ServersideOutputTransform(), MultiplexerTransform()],
            **kwargs
        )


df = get_data_frame()
app = EncostDash(name=__name__)


def get_layout():
    return html.Div([
        dmc.Paper([
            dmc.Grid([
                dmc.Col([
                    dmc.Card([
                        html.H3(
                            'Клиент: ',
                            id='client',),
                        html.P(
                            'Сменный день: ',
                            id='shift_day'),
                        html.P(
                            'Точка учета: ',
                            id='endpoint_name'),
                        html.P(
                            'Начало периода: ',
                            id='start_period'),
                        html.P(
                            'Конец периода: ',
                            id='end_period'),
                        dmc.Button(
                            'Показать информацию.',
                            id='show_info'),
                        dcc.Dropdown(
                            id='dropdown-filter',
                            options=[
                                {
                                    'label': x, 'value': x
                                } for x in df['reason'].unique()],
                            multi=True,
                        ),
                        dmc.Button(
                            'Выберите фильтр',
                            id='filter'),
                        html.Div(
                            id='output')],
                        **CARD_STYLE)
                ], span=6),
                dmc.Col([
                    dmc.Card([
                        dcc.Graph(
                            id='chart',
                            responsive='auto',
                            config=dict(
                                displaylogo=False, displayModeBar=False,),
                            style={
                                'height': '450px',
                                'margin': '-50px',
                            }
                        )],
                        **CARD_STYLE)
                ], span=6),
                dmc.Col([
                    dmc.Card([
                        dcc.Graph(
                            id='timeline',
                            responsive='auto',
                            config=dict(
                                displaylogo=False, displayModeBar=False,
                            ),
                            style={
                                'height': '250px',
                            })],
                        **CARD_STYLE)
                ], span=12),
            ], gutter="xl",)
        ])
    ])


app.layout = get_layout()


@app.callback(
    Output('client', 'children'),
    Output('shift_day', 'children'),
    Output('endpoint_name', 'children'),
    Output('start_period', 'children'),
    Output('end_period', 'children'),

    Output('chart', 'figure'),
    Output('timeline', 'figure'),
    State('filter', 'value'),
    Input('show_info', 'n_clicks'),
    prevent_initial_call=True,
)
def update_base_info(value, click):
    """
    Показываем базовую информацию по фрейму.
    """
    if click is None:
        raise PreventUpdate
    return get_base_info(df)


@app.callback(
    Output('timeline', 'figure'),
    Input('filter', 'n_clicks'),
    State('dropdown-filter', 'value'),
    State('timeline', 'figure'),
    prevent_initial_call=True,
)
def graph_filtering(click, reason, fig):
    """
    Фильтрация мульти-выбор по состояниям.
    """
    if not reason:
        raise PreventUpdate
    filtered_traces = [
        index
        for index, _ in enumerate(fig['data'])
        if fig['data'][index]['name'] in reason
    ]
    updated_figure = Patch()
    for index, _ in enumerate(fig['data']):
        updated_figure['data'][index]['opacity'] = 1 if index in filtered_traces else 0.2
    return updated_figure


if __name__ == '__main__':
    app.run_server(debug=True)
