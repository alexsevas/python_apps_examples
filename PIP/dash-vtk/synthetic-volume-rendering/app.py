# conda activate allpy311
# pip install dash-vtk

# This example aims to show how do volume rendering of a synthetic image data by only providing the grid information and values.
import random

import dash
import dash_vtk
from dash import html

random.seed(42)

app = dash.Dash(__name__)
server = app.server

volume_view = dash_vtk.View(
    children=dash_vtk.VolumeDataRepresentation(
        spacing=[1, 1, 1],
        dimensions=[10, 10, 10],
        origin=[0, 0, 0],
        scalars=[random.random() for _ in range(1000)],
        rescaleColorMap=False,
    )
)

app.layout = html.Div(
    style={"height": "calc(100vh - 16px)"},
    children=[
        html.Div(children=volume_view, style={"height": "100%", "width": "100%"})
    ],
)

if __name__ == "__main__":
    app.run(debug=True)
