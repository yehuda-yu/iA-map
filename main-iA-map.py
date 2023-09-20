import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

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

# Define lists of columns
categorical_cols = ['Village','District','Date_Completed', 'BH Depth_1', 'BH Depth_2', 'BH Depth_3', 'BH Depth_4', 'Lithology_1', 'Lithology_2']
numerical_cols = ['Depth_of_overburden', 'Total_Depth', 'Depth_drilled_in_bedrock', 'Yield_L/s_1', 'Yield_L/s_2', 'Yield_L/s_3', 'Yield_L/s_4', 'Static_Water_Level', 'Stabilized_discharge(L/s)', 'Altitude_(m)',]
threshold_cols = ['Ph', 'Electrical Conductivity (EC)', 'Total dissolved solids',
                       'Turbidity', 'Colour', 'Alkalinity', 'Hardness', 'Chloride', 'Nitrate', 'Nitrite',
                       'Iron', 'Copper', 'Flouride', 'Sulphate', 'E.coli', 'Suspended solids (total)',
                       'Manganese', 'Total Coliforms']

# Define all available columns in your dataset
all_columns = categorical_cols + numerical_cols + threshold_cols

# Allow the user to select a single column as the parameter to show
parameter = st.sidebar.selectbox("Select a Parameter to Visualize", all_columns)

# Check if the selected column belongs to categorical, numerical, or threshold columns
if parameter in categorical_cols:
    
    # Create the map for categorical columns
    fig = px.scatter_mapbox(
        data.dropna(subset=[parameter]),
        lat='lat',
        lon='long',
        color=parameter,
        hover_data=[parameter, 'Village', 'District'],
        color_discrete_map="Set1",  # Use a categorical color map
        size_max=15,
        zoom=8
    )
    units = ""
    threshold_value = None
    pass
    
elif parameter in numerical_cols:

    # Create the map for numerical columns without a threshold
    fig = px.scatter_mapbox(
        data.dropna(subset=[parameter]),
        lat='lat',
        lon='long',
        color=parameter,
        size=parameter,
        hover_data=[parameter, 'Village', 'District'],
        color_continuous_scale='Viridis',  # Replace with your desired color scale
        size_max=15,
        zoom=8
    )
    units = st.sidebar.text_input("Enter Unit (e.g., mg/L, °C)", "mg/L")
    threshold_value = None
    pass
    
elif parameter in threshold_cols:

        # Use predefined dictionaries for threshold columns
    threshold_dict = {
        'Threshold_Column_1': 10.0,
        'Threshold_Column_2': 20.0
    }
    color_dict = {
        'Threshold_Column_1': {'Red': 'red', 'Green': 'green'},
        'Threshold_Column_2': {'Red': 'red', 'Green': 'green'}
    }
    # Set threshold value and color dictionary based on the selected column
    threshold_value = threshold_dict.get(parameter, 0.0)
    color_map = color_dict.get(parameter, {'Red': 'red', 'Green': 'green'})
    # Create the map for threshold columns
    fig = px.scatter_mapbox(
        data.dropna(subset=[parameter]),
        lat='lat',
        lon='long',
        color=parameter,
        size=10,  # Set a default size for threshold columns
        hover_data=[parameter, 'Village', 'District'],
        color_discrete_map=color_map,
        size_max=15,
        zoom=8
    )
    units = st.sidebar.text_input("Enter Unit (e.g., mg/L, °C)", "mg/L")
    pass

# Set the minimum size of points
fig.update_traces(marker=dict(sizemin=5))

# Add a custom legend label with the threshold value if applicable
if threshold_value is not None:
    fig.update_layout(legend_title_text=f"Threshold ({threshold_value} {units})")

fig.update_layout(mapbox_style="carto-positron")
fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

# Show the map
st.plotly_chart(fig)

# Create a histogram below the map
fig_histogram = px.histogram(data, x=parameter, color=parameter, nbins=20, opacity=0.7)
fig_histogram.update_layout(title=f"Distribution of {parameter}")

# Customize the legend of the histogram
if threshold_value is not None:
    fig_histogram.update_layout(
        legend_title_text=f"Threshold ({threshold_value} {units})",
        showlegend=True,
        coloraxis_colorbar=dict(title="", tickvals=[0, 1], ticktext=["Below", "Above"])
    )
else:
    fig_histogram.update_layout(
        legend_title_text=f"Units: {units}",
        showlegend=False
    )

st.plotly_chart(fig_histogram)

# Provide instructions to users
st.sidebar.header("Instructions")
st.sidebar.markdown("1. Use the sidebar to customize the visualization.")
st.sidebar.markdown("2. Select a column group: Categorical, Numerical, or Threshold.")
st.sidebar.markdown("3. Select a parameter to visualize from the dropdown menu.")
st.sidebar.markdown("4. Enter the unit (e.g., mg/L) for the selected parameter if applicable.")
