import streamlit as st
import folium
from folium import plugins
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import Point

# Load your dataset
# @st.cache_data
def load_data(path):
        
    # load the data
    csv_file = "dataset.csv"
    data = pd.read_csv(csv_file)

    # drop geometry column
    data.drop(columns=['geometry'], inplace=True)

    # Convert the columns to numeric
    data['Grid_N'] = pd.to_numeric(data['Grid_N'])
    data['Grid_E'] = pd.to_numeric(data['Grid_E'])

    # convert all water parameter columns to numeric
    water_columns = [ 'Ph',
        'Electrical Conductivity (EC)', 'Total dissolved solids', 'Turbidity',
        'Colour', 'Alkalinity', 'Hardness', 'Chloride', 'Nitrate', 'Nitrite',
        'Iron', 'Copper', 'Flouride', 'Sulphate', 'E.coli',
        'Suspended solids (total)', 'Manganese', 'Total Coliforms',]
    for column in water_columns:
        data[column] = pd.to_numeric(data[column], errors='coerce')

    # Create a GeoDataFrame with Point geometry
    geometry = [Point(x, y) for x, y in zip(data['Grid_E'], data['Grid_N'])]
    gdf = gpd.GeoDataFrame(data, geometry=geometry)

    # Filter out rows with 0 values in coordinates
    gdf = gdf.query("Grid_N != 0 and Grid_E != 0")

    # Define the coordinate reference system (CRS) for Africa
    gdf.crs = {'init': 'epsg:32636'}

    # drop 	field_1 column
    gdf.drop(columns=['field_1'], inplace=True)

    return gdf

# Function to create a map with Folium
# @st.cache(allow_output_mutation=True)
def create_base_map():
    """
    Creates a Folium Map instance.
    """
    # Create a Folium Map instance
    m = folium.Map(location=[1.373333, 32.290275], zoom_start=6)

    # Add Esri Satellite tile layer
    esri_tile = folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri',
        name='Esri Satellite',
        overlay=False,
        control=True
    )
    esri_tile.add_to(m)

    # Add Stamen Terrain map layer
    terrain_tile = folium.TileLayer(
        tiles='https://stamen-tiles-{s}.a.ssl.fastly.net/terrain/{z}/{x}/{y}.png',
        attr='Stamen Terrain',
        name='Stamen Terrain',
        overlay=False,
        control=True,
    )
    terrain_tile.add_to(m)

    # Add LayerControl to the map
    folium.LayerControl().add_to(m)

    return m

# Function to display points on the map with dynamic threshold columns
def display_points_on_map(m, gdf, column, threshold_value):
    # Create threshold columns dynamically based on user input
    below_threshold_col = f'{column}_below_threshold'
    above_threshold_col = f'{column}_above_threshold'

    gdf[below_threshold_col] = gdf[column].apply(lambda x: x if x < threshold_value else None)
    gdf[above_threshold_col] = gdf[column].apply(lambda x: x if x >= threshold_value else None)

    # Define marker options
    marker_kwds = {
        'radius': 6,
    }

    # Plot points below threshold with green color
    below_threshold = gdf[~gdf[below_threshold_col].isnull()]
    below_threshold.explore(
        m=m,
        column=below_threshold_col,
        legend=False,
        zoom_start=6,
        name=f"{column} < {threshold_value}",
        cmap='Greens',  # Use a green colormap
        vmax=-1,       # Set the maximum value of the colormap
        marker_kwds=marker_kwds,
    )

    # Plot points above threshold with red color
    above_threshold = gdf[~gdf[above_threshold_col].isnull()]
    above_threshold.explore(
        m=m,
        column=above_threshold_col,
        legend=False,
        zoom_start=6,
        name=f"{column} >= {threshold_value}",
        cmap='Reds',  # Use a red colormap
        vmax=0.91,     # Set the minimum value of the colormap
        marker_kwds=marker_kwds,
    )

    return m

# App UI

st.title("Water Drilling Points in Uganda")

# Load the data
path = "dataset.shp"
data = load_data(path)


st.table(data.head())
"""
# Parameter selection dropdown
selected_parameter = st.selectbox("Select Parameter to Visualize", data.columns)

# Threshold value input
threshold_value = st.number_input("Enter Threshold Value", min_value=0.0, max_value=100.0)

# Create and display the map
st.subheader("Map Visualization")

 # Create a base map (cached)
base_map = create_base_map()

# Display points on the map based on the user's input
m = display_points_on_map(base_map, data, selected_parameter, threshold_value)

# Display the map using Streamlit
st.subheader("Map Visualization")
st.write(m)
"""
