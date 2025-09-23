# conda activate hydro_env
# python 3.9.23

from vispy import app, visuals, scene
import numpy as np

canvas = scene.SceneCanvas(keys='interactive')
view = canvas.central_widget.add_view()
points = np.random.rand(10000, 3)
scatter = scene.visuals.Markers()
scatter.set_data(points, edge_color=None, face_color='white', size=7)
view.add(scatter)
view.camera = 'turntable'
canvas.show()
app.run()