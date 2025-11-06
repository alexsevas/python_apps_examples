import json
import os
from concurrent.futures import ProcessPoolExecutor
import requests
from pytopojson.feature import Feature
import detroit as d3

# URLs
WORLD_URL = "https://cdn.jsdelivr.net/npm/world-atlas@2/land-50m.json"
US_URL = "https://cdn.jsdelivr.net/npm/us-atlas@3/counties-10m.json"

# Theme
theme = "light"
color = "white" if theme == "dark" else "black"

width = 688

# --- Projection helpers (must be defined at module level) ---
def cylindrical_projection(projection, width, height):
    return (
        projection.rotate([0, 0])
        .fit_extent([[1, 1], [width - 1, height - 1]], {"type": "Sphere"})
        .set_precision(0.2)
    )

def azimuthal_projection1(projection, width, height):
    return (
        projection.rotate([110, -40])
        .fit_extent([[1, 1], [width - 1, height - 1]], {"type": "Sphere"})
        .set_precision(0.2)
    )

def azimuthal_projection2(projection, width, height):
    return (
        projection.scale(width / 6)
        .translate([width / 2, height / 2])
        .set_clip_angle(74 - 1e-4)
        .set_clip_extent([[-1, -1], [width + 1, height + 1]])
        .set_precision(0.2)
    )

def azimuthal_projection3(projection, width, height):
    return (
        projection.rotate([110, -40])
        .fit_extent([[1, 1], [width - 1, height - 1]], {"type": "Sphere"})
        .set_precision(0.2)
    )

def azimuthal_projection4(projection, width, height):
    return (
        projection.scale(width / 4)
        .translate([width / 2, height / 2])
        .rotate([-27, 0])
        .set_clip_angle(135 - 1e-4)
        .set_clip_extent([[-1, -1], [width + 1, height + 1]])
        .set_precision(0.2)
    )

def conic_projection1(projection, width, height):
    return (
        projection.parallels([35, 65])
        .rotate([-20, 0])
        .scale(width * 0.55)
        .set_center([0, 52])
        .translate([width / 2, height / 2])
        .set_clip_extent([[-1, -1], [width + 1, height + 1]])
        .set_precision(0.2)
    )

def conic_projection2(projection, width, height):
    return projection.scale(1300 / 975 * width * 0.8).translate([width / 2, height / 2])


# --- Worker function (must be picklable) ---
def generate_svg(args):
    name, proj_name, height, transform_name, is_world = args

    # Reconstruct projection object
    projection = getattr(d3, f"geo_{proj_name}")()
    transform = globals()[transform_name]

    if is_world:
        _generate_world(name, projection, height, transform)
    else:
        _generate_us(name, projection, height, transform)


def _generate_world(name, projection, height, transform):
    # Load world data inside the function (spawn-safe)
    world_resp = requests.get(WORLD_URL)
    world = json.loads(world_resp.content)
    feature = Feature()(world, world["objects"]["land"])
    graticule = d3.geo_graticule_10()
    outline = {"type": "Sphere"}

    projection = transform(projection, width, height)
    path = d3.geo_path(projection)

    svg = (
        d3.create("svg")
        .attr("width", width)
        .attr("height", height)
        .attr("viewBox", f"0 0 {width} {height}")
    )
    (
        svg.append("path")
        .attr("name", "graticule")
        .attr("d", path(graticule))
        .attr("stroke", color)
        .attr("stroke-opacity", 0.2)
        .attr("fill", "none")
    )
    (
        svg.append("path")
        .attr("name", "feature")
        .attr("d", path(feature))
        .attr("fill", color)
    )
    (
        svg.append("path")
        .attr("name", "outline")
        .attr("d", path(outline))
        .attr("stroke", color)
        .attr("fill", "none")
    )

    with open(f"result/{theme}-projection-{name}.svg", "w") as file:
        file.write(str(svg))


def _generate_us(name, projection, height, transform):
    # Load US data inside the function (spawn-safe)
    us_resp = requests.get(US_URL)
    us = json.loads(us_resp.content)
    nation = Feature()(us, us["objects"]["nation"])
    statemesh = json.load(open("data/statemesh.json"))
    countymesh = json.load(open("data/countymesh.json"))

    projection = transform(projection, width, height)
    path = d3.geo_path(projection)

    svg = (
        d3.create("svg")
        .attr("width", width)
        .attr("height", height)
        .attr("viewBox", f"0 0 {width} {height}")
    )
    (
        svg.append("path")
        .attr("name", "nation")
        .attr("d", path(nation))
        .attr("stroke", color)
        .attr("fill", "none")
    )
    (
        svg.append("path")
        .attr("name", "statemesh")
        .attr("d", path(statemesh))
        .attr("fill", "none")
        .attr("stroke", color)
        .attr("stroke-width", 0.5)
    )
    (
        svg.append("path")
        .attr("name", "countymesh")
        .attr("d", path(countymesh))
        .attr("stroke", color)
        .attr("stroke-width", 0.5)
        .attr("stroke-opacity", 0.5)
        .attr("fill", "none")
    )

    os.makedirs("result", exist_ok=True)
    with open(f"result/{theme}-projection-{name}.svg", "w") as file:
        file.write(str(svg))


# --- Projection list using STRINGS (picklable) ---
projections = [
    ("equirectangular", "equirectangular", width / 2, "cylindrical_projection", True),
    ("mercator", "mercator", width, "cylindrical_projection", True),
    ("transverse_mercator", "transverse_mercator", width, "cylindrical_projection", True),
    ("equal_earth", "equal_earth", width * 0.49, "cylindrical_projection", True),
    ("natural_earth_1", "natural_earth_1", width * 0.5, "cylindrical_projection", True),
    ("azimuthal_equal_area", "azimuthal_equal_area", 400, "azimuthal_projection1", True),
    ("azimuthal_equidistant", "azimuthal_equidistant", 400, "azimuthal_projection1", True),
    ("gnomonic", "gnomonic", 400, "azimuthal_projection2", True),
    ("orthographic", "orthographic", 400, "azimuthal_projection3", True),
    ("stereographic", "stereographic", 400, "azimuthal_projection4", True),
    ("conic_conformal", "conic_conformal", 400, "conic_projection1", True),
    ("conic_equal_area", "conic_equal_area", 400, "conic_projection1", True),
    ("conic_equidistant", "conic_equidistant", 400, "conic_projection1", True),
    ("albers", "albers", 400, "conic_projection2", False),
    ("albers_usa", "albers_usa", 400, "conic_projection2", False),
]


# --- Main execution guard ---
if __name__ == '__main__':
    with ProcessPoolExecutor() as pool:
        list(pool.map(generate_svg, projections))