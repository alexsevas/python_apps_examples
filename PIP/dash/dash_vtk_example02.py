# conda activate allpy311

# pip install dash-vtk dash

from dash import Dash, html

import dash_vtk
from dash_vtk.utils import to_volume_state

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

# Use helper to get a volume structure that can be passed as-is to a Volume
volume_state = to_volume_state(dataset)  # No need to select field

content = dash_vtk.View([
    dash_vtk.VolumeRepresentation([
        # GUI to control Volume Rendering
        # + Setup good default at startup
        dash_vtk.VolumeController(),
        # Actual volume
        dash_vtk.Volume(state=volume_state),
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
