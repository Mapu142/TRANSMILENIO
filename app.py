import pandas as pd # para leer *.txt
import geopandas as gpd
from shapely.geometry import LineString



# Cargar shapes.txt manteniendo la precisión
shapes = pd.read_csv('shapes.txt')
routes = pd.read_csv('routes.txt')
stops = pd.read_csv('stops.txt')
stops_times = pd.read_csv('stop_times.txt')
trips = pd.read_csv('trips.txt')

# Convertir puntos a geometría
shapes_gdf = (
    shapes.sort_values(["shape_id", "shape_pt_sequence"])
    .groupby("shape_id")
    .apply(lambda x: LineString(zip(x.shape_pt_lon, x.shape_pt_lat)))
    .reset_index()
)

shapes_gdf.columns = ["shape_id", "geometry"]
shapes_gdf = gpd.GeoDataFrame(shapes_gdf, geometry="geometry", crs="EPSG:4326")

trips_shapes = trips.merge(shapes_gdf, on="shape_id")
trips_routes = trips_shapes.merge(routes, on="route_id")

# Ahora tienes cada ruta con su polilínea real
trips_routes.head()

trips_shapes = trips.merge(shapes_gdf, on="shape_id")
trips_routes = trips_shapes.merge(routes, on="route_id")

# Ahora tienes cada ruta con su polilínea real
trips_routes.head()

from mappymatch import map_match
from mappymatch.constructs.geometries import Point
from mappymatch.maps.nx.nx_map import NXMap
from mappymatch.matcher.lcss.lcss_map_matcher import LCSSMapMatcher
# Punto del usuario
pt = Point(user_lon, user_lat)

# Map matching → encontrar shape más probable
matched = matcher.match_point(pt)
matched

