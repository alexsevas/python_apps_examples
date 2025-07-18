# conda activate allpy311

# pip install dash-vtk dash

from dash import Dash, html

import dash_vtk
from dash_vtk.utils import to_mesh_state

try:
    # VTK 9+
    from vtkmodules.vtkImagingCore import vtkRTAnalyticSource
except ImportError:
    # VTK =< 8
    from vtk.vtkImagingCore import vtkRTAnalyticSource

# Use VTK to get some data
data_source = vtkRTAnalyticSource()
data_source.Update()  # <= Execute source to produce an output
dataset = data_source.GetOutput()

# Use helper to get a mesh structure that can be passed as-is to a Mesh
# RTData is the name of the field
mesh_state = to_mesh_state(dataset)

content = dash_vtk.View([
    dash_vtk.GeometryRepresentation([
        dash_vtk.Mesh(state=mesh_state)
    ]),
])

# Dash setup
app = Dash()
server = app.server

app.layout = html.Div(
    style={"width": "100%", "height": "800px"},
    children=[content],
)

if __name__ == "__main__":
    app.run(debug=True)
