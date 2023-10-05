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

    # Rename columns
    column_mapping = {
        "Depth_of_overburden": "Overburden Thickness (m)",
        "Depth_drilled_in_bedrock": "Depth Drilled in Bedrock (m)",
        "Static_Water_Level": "Static Water Level (m)",
        "Stabilized_discharge(L/s)": "Borehole Yield (L/s)",
        "Altitude_(m)": "Elevation (m)",
        "Ph": "pH",
        "Electrical Conductivity (EC)": "Electrical Conductivity (μS/cm)",
        "Total dissolved solids": "Total Dissolved Solids (mg/L)",
        "Turbidity": "Turbidity (NTU)",
        "Hardness": "Hardness (mg/L)",
        "Chloride": "Chloride (mg/L)",
        "Nitrate": "Nitrate as N (mg/L)",
        "Nitrite": "Nitrite (mg/L)",
        "Iron": "Iron (mg/L)",
        "Copper": "Copper (mg/L)",
        "Flouride": "Flouride (mg/L)",
        "Sulphate": "Sulfate (mg/L)",
        "Manganese": "Manganese (mg/L)"
    }
    data.rename(columns=column_mapping, inplace=True)

    # Drop columns
    columns_to_drop = ["Colour", "Alkalinity", "E.coli", "Suspended solids (total)"]
    data.drop(columns=columns_to_drop, inplace=True)

    return data

# Define the units and thresholds dictionary
units_and_thresholds = {
    "pH": ("", (9.5, 5.5)),
    "Electrical Conductivity (μS/cm)": ("μS/cm", (2500,)),
    "Total Dissolved Solids (mg/L)": ("mg/L", (1500,)),
    "Turbidity (NTU)": ("NTU", (25,)),
    "Hardness (mg/L)": ("mg/L", (600,)),
    "Chloride (mg/L)": ("mg/L", (250,)),
    "Nitrate as N (mg/L)": ("mg/L", (10,)),
    "Sulfate (mg/L)": ("mg/L", (400,)),
    "Manganese (mg/L)": ("mg/L", (0.1,)),
    "Total Coliforms (CFU/100 ml)": ("CFU/100 ml", (0.0001,))
}

# App UI
st.title("Water Drilling Points in Uganda")

# Provide instructions to users
st.sidebar.header("Instructions")
st.sidebar.markdown("Select parameters to visualize from the dropdown menus.")

# Load the data
data = load_data()

# Sidebar for user input
st.sidebar.header("Customize Visualization")

# Define lists of columns
categorical_cols = ['Village', 'District', 'Date_Completed', 'First Water Strike Depth (m)', 'Second Water Strike Depth (m)',
                   'Third Water Strike Depth (m)', 'Fourth Water Strike Depth (m)', 'Lithology_1', 'Lithology_2']
numerical_cols = ['Overburden Thickness (m)', 'Total_Depth', 'Depth Drilled in Bedrock (m)', 'First Water Strike Yield (L/s)',
                 'Second Water Strike Yield (L/s)', 'Third Water Strike Yield (L/s)', 'Fourth Water Strike Yield (L/s)',
                 'Static Water Level (m)', 'Borehole Yield (L/s)', 'Elevation (m)']
threshold_cols = ['pH', 'Electrical Conductivity (μS/cm)', 'Total Dissolved Solids (mg/L)',
                 'Turbidity (NTU)', 'Hardness (mg/L)', 'Chloride (mg/L)', 'Nitrate as N (mg/L)', 'Sulfate (mg/L)',
                 'Manganese (mg/L)', 'Total Coliforms (CFU/100 ml)']

# Define all available columns in your dataset
all_columns = categorical_cols + numerical_cols + threshold_cols

# Allow the user to select two columns as parameters to show
selected_columns = st.sidebar.columns(2)
parameter1 = selected_columns[0].selectbox("Select Parameter 1", all_columns)
parameter2 = selected_columns[1].selectbox("Select Parameter 2", all_columns)

# Helper function to create a map for a single parameter
def create_map(parameter, data):
    try:
        if parameter in categorical_cols:
            # Create the map for categorical columns
            fig = px.scatter_mapbox(
                data.dropna(subset=[parameter]),
                lat='lat',
                lon='long',
                color=parameter,
                hover_data=[parameter, 'Village', 'Borehole Yeild (L/s)', 'Nitrate as N (mg/L)', 'Total Dissolved Solids (mg/L)', 'Elevation (m)'],
                color_discrete_sequence=px.colors.qualitative.G10,
                zoom=8
            )
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
                hover_data=[parameter, 'Village', 'Borehole Yeild (L/s)', 'Nitrate as N (mg/L)', 'Total Dissolved Solids (mg/L)', 'Elevation (m)'],
                hover_name="Village",
                color_continuous_scale='plasma',  # Replace with your desired color scale
                size_max=15,
                zoom=8
            )
            units = 'm'
            threshold_value = None

        elif parameter in threshold_cols:
            # Set threshold value and color dictionary based on the selected column and dictionary
            threshold_value = float(units_and_thresholds[parameter][1])

            # create column of color
            data['Color'] = data[parameter].apply(lambda x: 'Red' if x >= threshold_value else 'Green')
            # Create the map for threshold columns
            fig = px.scatter_mapbox(
                data.dropna(subset=[parameter]),
                lat='lat',
                lon='long',
                color='Color',
                size=parameter,
                hover_data=[parameter, 'Village', 'Borehole Yeild (L/s)', 'Nitrate as N (mg/L)', 'Total Dissolved Solids (mg/L)', 'Elevation (m)'],
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
                hover_data=[parameter, 'Village', 'Borehole Yeild (L/s)', 'Nitrate as N (mg/L)', 'Total Dissolved Solids (mg/L)', 'Elevation (m)'],
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

# Create maps for the selected parameters
create_map(parameter1, data)
create_map(parameter2, data)
