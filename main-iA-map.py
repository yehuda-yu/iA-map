import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Load your dataset
@st.cache_data
def load_data():
    # Load the data from a CSV file
    csv_file = "gdf_84.csv"
    data = pd.read_csv(csv_file)
    
    # Convert relevant columns to numeric
    numeric_columns = ['lat', 'long', 'Ph', 'Electrical Conductivity (EC)', 'Total dissolved solids',
                       'Turbidity', 'Colour', 'Alkalinity', 'Hardness', 'Chloride', 'Nitrate', 'Nitrite',
                       'Iron', 'Copper', 'Flouride', 'Sulphate', 'E.coli', 'Suspended solids (total)',
                       'Manganese', 'Total Coliforms']
    
    data[numeric_columns] = data[numeric_columns].apply(pd.to_numeric, errors='coerce')
    
    return data

# App UI
st.title("Water Drilling Points in Uganda")

# Load the data
data = load_data()

# Sidebar for user input
st.sidebar.header("Customize Visualization")

# define columns to choose from
parameters_cols = ['Depth_of_overburden',
       'Total_Depth', 'Depth_drilled_in_bedrock', 'BH Depth_1', 'BH Depth_2',
       'BH Depth_3', 'BH Depth_4', 'Yield_L/s_1', 'Yield_L/s_2', 'Yield_L/s_3',
       'Yield_L/s_4', 'Lithology_1', 'Lithology_2', 'Static_Water_Level',
       'Stabilized_discharge(L/s)', 'Altitude_(m)', 'Date_Lab', 'Ph',
       'Electrical Conductivity (EC)', 'Total dissolved solids', 'Turbidity',
       'Colour', 'Alkalinity', 'Hardness', 'Chloride', 'Nitrate', 'Nitrite',
       'Iron', 'Copper', 'Flouride', 'Sulphate', 'E.coli', 'Number',
       'Suspended solids (total)', 'Manganese', 'Total Coliforms',]

parameter = st.sidebar.selectbox("Select a Parameter to Visualize", parameters_cols)
threshold_value = st.sidebar.text_input("Enter Threshold Value", data[parameter].median())
units = st.sidebar.text_input("Enter Unit (e.g., mg/L, °C)", "mg/L")

# Convert threshold value to float
try:
    threshold_value = float(threshold_value)
except ValueError:
    st.sidebar.warning("Please enter a valid threshold value.")

# Create a new column for color based on the threshold
data['Color'] = data[parameter].apply(lambda x: 'Red' if x >= threshold_value else 'Green')

# Create the map
fig = px.scatter_mapbox(
    data,
    lat='lat',
    lon='long',
    color='Color',
    size=parameter,
    hover_data=[parameter, 'Village', 'District'],
    color_discrete_map={'Red': 'red', 'Green': 'green'},
    size_max=15,
    zoom=8
)

# Set the minimum size of points
fig.update_traces(marker=dict(sizemin=5))

# Add a custom legend label with the threshold value
fig.update_layout(legend_title_text=f"Threshold ({threshold_value} {units})")

fig.update_layout(mapbox_style="carto-positron")
fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

# Show the map
st.plotly_chart(fig)

# Create a histogram below the map
fig_histogram = px.histogram(data, x=parameter, color='Color', nbins=20, opacity=0.7,
                             color_discrete_map={'Red': 'red', 'Green': 'green'})
fig_histogram.update_layout(title=f"Distribution of {parameter}")

# Customize the legend of the histogram
fig_histogram.update_layout(
    legend_title_text=f"Threshold ({threshold_value} {units})",
    showlegend=True,  # Display the legend
    coloraxis_colorbar=dict(title="", tickvals=[0, 1], ticktext=["Below", "Above"])
)

st.plotly_chart(fig_histogram)

# Provide instructions to users
st.sidebar.header("Instructions")
st.sidebar.markdown(
    "1. Use the sidebar to customize the visualization."(
 st.sidebar.markdown(   
    "2. Select a parameter to visualize from the dropdown menu."(
 st.sidebar.markdown(
    "3. Enter the threshold value manually."(
 st.sidebar.markdown(    
    "4. Enter the unit (e.g., mg/L) for the selected parameter."
)
