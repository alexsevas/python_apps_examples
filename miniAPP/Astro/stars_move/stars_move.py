



import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from mpl_toolkits.mplot3d import Axes3D

# Константы
num_stars = 10  # Количество звезд
semi_major_axes = np.linspace(1, 3, num_stars)  # Большие полуоси орбит
orbital_periods = semi_major_axes ** 1.5  # Закон Кеплера T^2 ~ a^3
colors = plt.cm.viridis(np.linspace(0, 1, num_stars))  # Разные цвета звезд

# Генерация случайных параметров орбит
excentricities = np.random.uniform(0.5, 0.9, num_stars)  # Высокий эксцентриситет
inclinations = np.random.uniform(0, np.pi, num_stars)  # Разные наклоны орбит

theta = np.linspace(0, 2 * np.pi, 300)  # Углы для траекторий
orbits_x, orbits_y, orbits_z = [], [], []
for i in range(num_stars):
    r = semi_major_axes[i] * (1 - excentricities[i] ** 2) / (1 + excentricities[i] * np.cos(theta))
    x = r * np.cos(theta)
    y = r * np.sin(theta)
    z = y * np.tan(inclinations[i])
    orbits_x.append(x)
    orbits_y.append(y)
    orbits_z.append(z)

# Фигуры и оси
fig = plt.figure(figsize=(8, 8))
ax = fig.add_subplot(111, projection='3d')
ax.set_xlim(-3.5, 3.5)
ax.set_ylim(-3.5, 3.5)
ax.set_zlim(-3.5, 3.5)
ax.set_xticks([])
ax.set_yticks([])
ax.set_zticks([])
ax.set_title("Stars Orbiting a Black Hole")

# Черная дыра
ax.scatter(0, 0, 0, color='black', s=100, label='Black Hole')

# Линии орбит
for i in range(num_stars):
    ax.plot(orbits_x[i], orbits_y[i], orbits_z[i], linestyle='dashed', color=colors[i], alpha=0.5)

# Звезды и их траектории
stars = [ax.plot([], [], [], 'o', color=colors[i])[0] for i in range(num_stars)]
trajectories = [ax.plot([], [], [], '-', color=colors[i], alpha=0.6)[0] for i in range(num_stars)]
traces_x = [[] for _ in range(num_stars)]
traces_y = [[] for _ in range(num_stars)]
traces_z = [[] for _ in range(num_stars)]

# Функция анимации
def update(frame):
    for i in range(num_stars):
        angle = 2 * np.pi * frame / (100 * orbital_periods[i])  # Угловая скорость
        r = semi_major_axes[i] * (1 - excentricities[i] ** 2) / (1 + excentricities[i] * np.cos(angle))
        x = r * np.cos(angle)
        y = r * np.sin(angle)
        z = y * np.tan(inclinations[i])
        stars[i].set_data([x], [y])
        stars[i].set_3d_properties([z])
        traces_x[i].append(x)
        traces_y[i].append(y)
        traces_z[i].append(z)
        trajectories[i].set_data(traces_x[i], traces_y[i])
        trajectories[i].set_3d_properties(traces_z[i])
    return stars + trajectories

ani = animation.FuncAnimation(fig, update, frames=500, interval=20, blit=True)
plt.show()
