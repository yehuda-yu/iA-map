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
    numeric_columns = ['lat', 'long', 'pH', 'Electrical Conductivity (μS/cm)', 'Total Dissolved Solids (mg/L)',
                       'Turbidity (NTU)', 'Alkalinity (mg/L)', 'Hardness (mg/L)', 'Chloride (mg/L)',
                       'Nitrate as N (mg/L)', 'Nitrite (mg/L)', 'Iron (mg/L)', 'Copper (mg/L)',
                       'Flouride (mg/L)', 'Sulfate (mg/L)', 'Suspended solids (mg/L)',
                       'Manganese (mg/L)']
    
    data[numeric_columns] = data[numeric_columns].apply(pd.to_numeric, errors='coerce')

    # Rename columns
    column_rename_dict = {
        "Depth of Overburden": "Overburden Thickness (m)",
        "Depth Drilled in Bedrock (m)": "Depth Drilled in Bedrock (m)",
        "Static Water Level (m)": "Static Water Level (m)",
        "Stabilized Discharge": "Borehole Yield (l/s)",
        "Altitude": "Elevation (m)",
        "pH": "pH",
        "Electrical Conductivity (μS/cm)": "Electrical Conductivity (μS/cm)",
        "Total Dissolved Solids (mg/L)": "Total Dissolved Solids (mg/L)",
        "Turbidity (NTU)": "Turbidity (NTU)",
        "Alkalinity (mg/L)": "Alkalinity (mg/L)",
        "Hardness (mg/L)": "Hardness (mg/L)",
        "Chloride (mg/L)": "Chloride (mg/L)",
        "Nitrate as N (mg/L)": "Nitrate as N (mg/L)",
        "Nitrite (mg/L)": "Nitrite (mg/L)",
        "Iron (mg/L)": "Iron (mg/L)",
        "Copper (mg/L)": "Copper (mg/L)",
        "Flouride (mg/L)": "Flouride (mg/L)",
        "Sulfate (mg/L)": "Sulfate (mg/L)",
        "Suspended solids (mg/L)": "Suspended solids (mg/L)",
        "Manganese (mg/L)": "Manganese (mg/L)"
    }
    
    data = data.rename(columns=column_rename_dict)
    
    # Drop columns to remove
    columns_to_remove = ["Colour", "Alkalinity (mg/L)", "Ecoli", "Suspended solids (mg/L)", "Total Coliforms"]
    data = data.drop(columns=columns_to_remove, errors='ignore')
    
    return data

# Define the units and thresholds dictionary
units_and_thresholds = {
    "pH": ("", (9.5, 5.5)),
    "Electrical Conductivity (μS/cm)": ("μS/cm", (2500,)),
    "Total Dissolved Solids (mg/L)": ("mg/L", (1500,)),
    "Turbidity (NTU)": ("NTU", (25,)),
    "Hardness (mg/L)": ("mg/L", (600,)),
    "Chloride (mg/L)": ("mg/L", (250,)),
    "Copper (mg/L)": ("mg/L", (1,)),
    "Flouride (mg/L)": ("mg/L", (1.5,)),
    "Iron (mg/L)": ("mg/L", (0.3,)),
    "Manganese (mg/L)": ("mg/L", (0.1,)),
    "Nitrate as N (mg/L)": ("mg/L", (45,)),
    "Sulfate (mg/L)": ("mg/L", (400,)),
}

# App UI
st.title("Water Drilling Points in Uganda")

# Provide instructions to users
st.sidebar.header("Instructions")
st.sidebar.markdown("Select a parameter to visualize from the dropdown menu.")

# Load the data
data = load_data()

# Sidebar for user input
st.sidebar.header("Customize Visualization")

# Define lists of columns
categorical_cols = ['Village', 'District', 'Date_Completed', 'Lithology_1', 'Lithology_2']
numerical_cols = ['Overburden Thickness (m)', 'Depth Drilled in Bedrock (m)', 'Static Water Level (m)',
                   'Borehole Yield (l/s)', 'Elevation (m)']
threshold_cols = ['pH', 'Electrical Conductivity (μS/cm)', 'Total Dissolved Solids (mg/L)',
                   'Turbidity (NTU)', 'Hardness (mg/L)', 'Chloride (mg/L)', 'Nitrate as N (mg/L)',
                   'Nitrite (mg/L)', 'Iron (mg/L)', 'Copper (mg/L)', 'Flouride (mg/L)', 'Sulfate (mg/L)',
                   'Manganese (mg/L)']

# Define all available columns in your dataset
all_columns = categorical_cols + numerical_cols + threshold_cols

# Allow the user to select a single column as the parameter to show
parameter = st.sidebar.selectbox("Select a Parameter to Visualize", all_columns, 27)

try:
    # Check if the selected column belongs to categorical, numerical, or threshold columns
    if parameter in categorical_cols:
        
        # Create the map for categorical columns
        fig = px.scatter_mapbox(
            data.dropna(subset=[parameter]),
            lat='lat',
            lon='long',
            color=parameter,
            hover_data=[parameter, 'Village', 'Borehole Yield (l/s)', 'Nitrate as N (mg/L)',
                        'Total Dissolved Solids (mg/L)', 'Elevation (m)'],
            color_discrete_sequence=px.colors.qualitative.G10,
            zoom=8
        )
        # define units and threshold value
        units = ''
        threshold_value = None
    
    elif parameter in numerical_cols:
    
        # Create the map for numerical columns without a threshold
        fig = px.scatter_mapbox(
            data.dropna(subset=[parameter]),
            lat='lat',
            lon='long',
            color=parameter,
            size=parameter,
            hover_data=[parameter, 'Village', 'Borehole Yield (l/s)', 'Nitrate as N (mg/L)',
                        'Total Dissolved Solids (mg/L)', 'Elevation (m)'],
            hover_name="Village",
            color_continuous_scale='plasma',  # Replace with your desired color scale
            size_max=15,
            zoom=8
        )
        # define units and threshold value by the dictionary
        units = 'm'
        threshold_value = None
        
    elif parameter in threshold_cols:
        
        # Set threshold value and color dictionary based on the selected column and dictionary
        threshold_value = float(units_and_thresholds[parameter][1][0])

        # create column of color
        data['Color'] = data[parameter].apply(lambda x: 'Red' if x >= threshold_value else 'Green')
        # Create the map for threshold columns
        fig = px.scatter_mapbox(
            data.dropna(subset=[parameter]),
            lat='lat',
            lon='long',
            color='Color',
            size=parameter,
            hover_data=[parameter, 'Village', 'Borehole Yield (l/s)', 'Nitrate as N (mg/L)',
                        'Total Dissolved Solids (mg/L)', 'Elevation (m)'],
            color_discrete_map={'Red': 'red', 'Green': 'green'},
            size_max=15,
            zoom=8
        )
        units = units_and_thresholds[parameter][0]

    elif parameter == 'pH':
        # Get the lower and upper threshold values for pH
        lower_threshold, upper_threshold = units_and_thresholds[parameter][1]
    
        # Create a column 'Color' based on pH values
        data['Color'] = data['pH'].apply(lambda x: 'Red' if x < lower_threshold or x > upper_threshold else 'Green')
    
        # Create the map for threshold columns
        fig = px.scatter_mapbox(
            data.dropna(subset=[parameter]),
            lat='lat',
            lon='long',
            color='Color',
            size=parameter,
            hover_data=[parameter, 'Village', 'Borehole Yield (l/s)', 'Nitrate as N (mg/L)',
                        'Total Dissolved Solids (mg/L)', 'Elevation (m)'],
            color_discrete_map={'Red': 'red', 'Green': 'green'},
            size_max=15,
            zoom=8
        )
        units = units_and_thresholds[parameter][0]
    

    # Set the minimum size of points
    fig.update_traces(marker=dict(sizemin=5))

    # Add a custom legend label with the threshold value if applicable
    if threshold_value is not None:
        fig.update_layout(legend_title_text=f"Threshold ({threshold_value} {units})")

    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

    # add the subtitle with units
    st.subheader(f"{parameter}: {units}")

    # Show the map
    st.plotly_chart(fig)

except Exception as e:
    st.error(f"An error occurred: {e}")

try:
    # Create a histogram below the map
    if threshold_value is not None:
        # Create a histogram below the map
        fig_histogram = px.histogram(data, x=parameter, color='Color', nbins=20, opacity=0.8,
                                     color_discrete_map={'Red': 'red', 'Green': 'green'})
        fig_histogram.update_layout(title=f"Distribution of {parameter}")
        
        # Customize the legend of the histogram
        fig_histogram.update_layout(
            legend_title_text=f"Threshold ({threshold_value} {units})",
            showlegend=True,  # Display the legend
            coloraxis_colorbar=dict(title="", tickvals=[0, 1], ticktext=["Below", "Above"])
        )

    else:
        fig_histogram = px.histogram(data, x=parameter, nbins=20, opacity=0.8,color_discrete_sequence=['indianred'])
        fig_histogram.update_layout(title=f"Distribution of {parameter}")
        fig_histogram.update_layout(
            legend_title_text=f"Units: {units}",
            showlegend=False
        )

    st.plotly_chart(fig_histogram)

except Exception as e:
    st.error(f"An error occurred: {e}")
