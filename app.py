import streamlit as st
from pyproj import CRS
import pandas as pd
import geopandas as gpd
from shapely.geometry import LineString, Point
import folium
from streamlit_folium import st_folium

import os, sys
import traceback

def catch_errors():
    try:
        yield
    except Exception:
        st.error("Error en la aplicación:")
        st.code(traceback.format_exc())

with catch_errors():
print(">>> Ejecutando archivo:", os.path.abspath(__file__))
print("Python ejecutado:", sys.executable)

# Cargar shapes.txt manteniendo la precisión
shapes = pd.read_csv('shapes.txt')
routes = pd.read_csv('routes.txt')
stops = pd.read_csv('stops.txt')
stop_times = pd.read_csv('stop_times.txt')
trips = pd.read_csv('trips.txt')

# Convertir puntos a geometría
shapes_gdf = (
    shapes.sort_values(["shape_id", "shape_pt_sequence"])
    .groupby("shape_id")
    .apply(lambda x: LineString(zip(x.shape_pt_lon, x.shape_pt_lat)))
    .reset_index()
)

shapes_gdf.columns = ["shape_id", "geometry"]
crs_obj = CRS.from_epsg(4326)  # Crea el objeto CRS correctamente
shapes_gdf = gpd.GeoDataFrame(shapes_gdf, geometry="geometry", crs=crs_obj)

# =========================
#   UI
# =========================
st.title("🚍 Planificador inteligente — TransMilenio")

st.write("Esta app detecta si la ruta **en la que ya vas** te sirve para llegar al destino.")


# =========================
#   INPUTS DEL USUARIO
# =========================

st.header("1️⃣ ¿En qué ruta vas?")
ruta_seleccionada = st.selectbox(
    "Selecciona tu ruta",
    routes.route_short_name.unique(),
)

st.header("2️⃣ ¿Dónde estás?")
col1, col2 = st.columns(2)
with col1:
    modo_origen = st.radio("Selecciona cómo indicar dónde estás:", ["Parada", "Coordenadas"])

if modo_origen == "Parada":
    parada_origen = st.selectbox("Selecciona tu parada actual", stops.stop_name.unique())
    stop_actual = stops[stops.stop_name == parada_origen].iloc[0]

else:
    lat = st.number_input("Latitud", value=4.65)
    lon = st.number_input("Longitud", value=-74.1)
    stop_actual = {"stop_lat": lat, "stop_lon": lon}


st.header("3️⃣ ¿A dónde vas?")
destino = st.text_input("Escribe la parada o dirección de destino")

calcular = st.button("Calcular ruta")

# =========================
#   PROCESAMIENTO
# =========================

if calcular:

    # ---- 1. Filtrar rutas por route_short_name ----
    route_id = routes.loc[routes.route_short_name == ruta_seleccionada, "route_id"].iloc[0]
    trips_ruta = trips[trips.route_id == route_id]

    if trips_ruta.empty:
        st.error("No se encontraron viajes para esta ruta.")
        st.stop()

    # ---- 2. Seleccionar un trip (en GTFS cada ruta tiene varios) ----
    trip_id = trips_ruta.iloc[0].trip_id
    st.write(f"Usando trip: `{trip_id}`")

    stops_trip = stop_times[stop_times.trip_id == trip_id].merge(stops, on="stop_id")

    # ---- 3. Buscar destino por nombre aproximado ----
    destino_results = stops_trip[stops_trip.stop_name.str.contains(destino, case=False, na=False)]

    if not destino_results.empty:
        parada_destino = destino_results.iloc[0]
        st.success(f"Esta ruta **SÍ** te sirve. Debes bajarte en: **{parada_destino.stop_name}**")
    else:
        st.warning("Esta ruta NO te lleva directamente al destino. (Transbordos: próximo paso)")
        parada_destino = None

    # =========================
    #   MAPA
    # =========================

    st.header("🗺️ Mapa de tu ruta y posición")

    # Crear mapa centrado en la posición actual
    m = folium.Map(location=[stop_actual["stop_lat"], stop_actual["stop_lon"]], zoom_start=13)

    # ---- Marcar posición actual ----
    folium.Marker(
        [stop_actual["stop_lat"], stop_actual["stop_lon"]],
        tooltip="Estás aquí",
        icon=folium.Icon(color="blue")
    ).add_to(m)

    # ---- Dibujar route shape ----
    # Buscar shape_id asociado
    shape_id = trips_ruta.iloc[0].shape_id
    shape_geom = shapes_gdf[shapes_gdf.shape_id == shape_id].geometry.iloc[0]

    folium.PolyLine(
        locations=[(lat, lon) for lon, lat in zip(shape_geom.coords.xy[0], shape_geom.coords.xy[1])],
        weight=5,
        color="red",
        tooltip=f"Ruta {ruta_seleccionada}"
    ).add_to(m)

    # ---- Marcar destino si existe----
    if parada_destino is not None:
        folium.Marker(
            [parada_destino.stop_lat, parada_destino.stop_lon],
            tooltip=f"Destino: {parada_destino.stop_name}",
            icon=folium.Icon(color="green")
        ).add_to(m)

    st_folium(m, width=700, height=500)