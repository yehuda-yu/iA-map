import streamlit as st
import pandas as pd
import plotly.express as px

# Load your dataset
@st.cache
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
parameter = st.sidebar.selectbox("Select a Parameter to Visualize", data.columns[2:])
threshold_value = st.sidebar.slider("Set Threshold Value", min_value=data[parameter].min(),
                                    max_value=data[parameter].max(), value=data[parameter].median())
units = st.sidebar.text_input("Enter Unit (e.g., mg/L, °C)", "mg/L")

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
st.header(f"Distribution of {parameter}")
st.plotly_chart(px.histogram(data, x=parameter, color='Color', nbins=20, opacity=0.7))

# Provide instructions to users
st.sidebar.header("Instructions")
st.sidebar.markdown(
    "1. Use the sidebar to customize the visualization."
    "2. Select a parameter to visualize from the dropdown menu."
    "3. Adjust the threshold value using the slider."
    "4. Enter the unit (e.g., mg/L) for the selected parameter."
)
