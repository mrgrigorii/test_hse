# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate

import numpy as np
import pandas as pd
import plotly.express as px


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

DATASET = 'Введение в историю искусства.csv'


def load_dataset(dataset):
    with open(dataset, 'r', encoding='utf-8') as fin:
        df = pd.read_csv(fin, parse_dates=['date_created', 'date_modified'])

        df = df.drop(
            columns=['email_address', 'first_name', 'last_name', 'custom_1']
        )
        df = df.iloc[1:]
        df['respondent_id'] = df['respondent_id'].astype(np.int64)
        df['collector_id'] = df['collector_id'].astype(np.int64)

        df_response_questions = df.columns[[5, 6, 8, 9, 10, 13]]
        # 14 - user_id actualy
        df_open_ended_response_questions = df.columns[[7, 11, 12]]

        return df, df_response_questions, df_open_ended_response_questions


def get_pie_figure(dataset, column):
    data = dataset.loc[:, ['user_id', column]]
    data = data.drop_duplicates()
    data = data.dropna()

    fig = px.pie(data, names=column, title=column)
    return fig

df, df_q, df_open_ended_q = load_dataset(DATASET)
fig = get_pie_figure(df, df_q[0])

app.layout = html.Div(
    children=[
        html.H1(
            children='Введение в историю искусства'
        ),
        html.Label('Выберите вопрос'),
        dcc.Dropdown(
            id='questions',
            options=[
                {'label': question, 'value': question} for question in df_q
            ],
            value=df_q[0],
        ),
        dcc.Graph(id='graph-pie'),

        dcc.Dropdown(
            id='open-questions',
            options=[
                {'label': question, 'value': question} for question in df_open_ended_q
            ],
            value=df_open_ended_q[0],
        ),
        dash_table.DataTable(
            id='table',
            style_cell={
                'whiteSpace': 'normal',
                'height': 'auto',
                'textAlign': 'left',
                'minWidth': '180px', 'width': '180px', 'maxWidth': '180px',
            },
            style_data={
                'height': 'auto',
                'textAlign': 'left',
                'minWidth': '180px', 'width': '180px', 'maxWidth': '180px',
            },

            style_data_conditional=[{
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(248, 248, 248)'
            }],
            style_header={
                'backgroundColor': 'rgb(230, 230, 230)',
                'fontWeight': 'bold',
                'minWidth': '180px', 'width': '180px', 'maxWidth': '180px',
            },
            style_table={'height': '500px', 'overflowY': 'auto'}
        )
    ],
    style={'textAlign': 'center', 'width': '80%', 'margin-left': '10%', },
)


@app.callback(
    Output('graph-pie', 'figure'),
    [Input('questions', 'value')])
def update_figure(question):
    data = df.loc[:, ['user_id', question]]
    data = data.drop_duplicates()
    data = data.dropna()
    fig = px.pie(data, names=question)

    fig.update_layout(transition_duration=500)
    return fig


@app.callback(
    [
        Output('table', 'columns'),
        Output('table', 'data'),
    ],
    [Input('open-questions', 'value')])
def update_table(question):
    if question is None:
        raise PreventUpdate
    data = df.loc[:, ['user_id', question]]
    data = data.drop_duplicates()
    data = data.dropna()

    columns = [{"name": question, "id": question}, ]
    data = data.to_dict('records')
    return columns, data


if __name__ == '__main__':
    app.run_server(debug=True)
