# conda activate py39test, 3dpy310

# conda create -n ENV tensorflow numpy==1.23.4 python=3.9 -y
# pip install open3d laspy

import numpy as np
import laspy
import open3d as o3d

las = laspy.read('D:\\Projects\\Data\\3D_Point_clouds_python_DATA\\NZ19_Wellington.las')
list(las.point_format.dimension_names)
set(list(las.classification))

point_data = np.stack([las.X, las.Y, las.Z], axis=0).transpose((1, 0))
geom = o3d.geometry.PointCloud()
geom.points = o3d.utility.Vector3dVector(point_data)
o3d.visualization.draw_geometries([geom])