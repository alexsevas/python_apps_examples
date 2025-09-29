# conda activate allpy311

# pip install dash

# Пример показывает, как меняется синусоида в зависимости от частоты, которую выбирает пользователь

import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import numpy as np
import plotly.graph_objs as go

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Dynamic Sine Wave Plot"),
    dcc.Slider(
        id='frequency-slider',
        min=1,
        max=10,
        step=0.5,
        value=1,
        marks={i: str(i) for i in range(1, 11)}
    ),
    dcc.Graph(id='sine-graph')
])

@app.callback(
    Output('sine-graph', 'figure'),
    Input('frequency-slider', 'value')
)
def update_graph(frequency):
    x_vals = np.linspace(0, 2 * np.pi, 500)
    y_vals = np.sin(frequency * x_vals)
    figure = go.Figure(
        data=[
            go.Scatter(x=x_vals, y=y_vals, mode='lines', name='Sine Wave')
        ],
        layout=go.Layout(
            title=f"Sine Wave with Frequency {frequency}",
            xaxis={'title': 'x'},
            yaxis={'title': 'sin(f*x)'}
        )
    )
    return figure

if __name__ == '__main__':
    app.run_server(debug=True)
