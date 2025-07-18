# conda activate allpy311
# pip install dash-vtk dash numpy vtk

# This example aims to show how to load a vtkImageData using VTK and push it to the dash-vtk components for doing Volume rendering.

import os
import dash
from dash import html

import dash_vtk
from dash_vtk.utils import to_volume_state

import vtk

# Data file path
demo_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
head_vti = os.path.join(demo_dir, "data", "head.vti")

# Load dataset from dist
reader = vtk.vtkXMLImageDataReader()
reader.SetFileName(head_vti)
reader.Update()

volume_state = to_volume_state(reader.GetOutput())

vtk_view = dash_vtk.View(
    dash_vtk.VolumeRepresentation(
        children=[
            dash_vtk.VolumeController(),
            dash_vtk.Volume(state=volume_state),
        ]
    )
)

app = dash.Dash(__name__)
server = app.server

app.layout = html.Div(
    style={"height": "calc(100vh - 16px)", "width": "100%"},
    children=[html.Div(vtk_view, style={"height": "100%", "width": "100%"})],
)

if __name__ == "__main__":
    app.run(debug=True)
