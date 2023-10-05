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

    # replace 'BH Depth_1', 'BH Depth_2','BH Depth_3', 'BH Depth_4', 'Yield_L/s_1' names to 'First Water Strike Depth (m)'...
    data = data.rename(columns={'BH Depth_1': 'First Water Strike Depth (m)', 'BH Depth_2': 'Second Water Strike Depth (m)', 'BH Depth_3': 'Third Water Strike Depth (m)', 'BH Depth_4': 'Fourth Water Strike Depth (m)', })
    # replace Yield_L/s_1 to First Water Strike Yield (L/s)...
    data = data.rename(columns={'Yield_L/s_1': 'First Water Strike Yield (L/s)', 'Yield_L/s_2': 'Second Water Strike Yield (L/s)', 'Yield_L/s_3': 'Third Water Strike Yield (L/s)', 'Yield_L/s_4': 'Fourth Water Strike Yield (L/s)','Stabilized_discharge(L/s)':'Borehole Yeild (L/s)' })
    
    return data

# Define the units and thresholds dictionary
units_and_thresholds = {
    "Ph": ("", (5.5, 9.5)),
    "Electrical Conductivity (EC)": ("μS/cm", (2500,)),
    "Total dissolved solids": ("mg/L", (1500,)),
    "Colour": ("TCU", (50,)),
    "Turbidity": ("NTU", (25,)),
    "Hardness": ("mg/L", (600,)),
    "Chloride": ("mg/L", (250,)),
    "Cadmium (Cd)": ("mg/L", (0.003,)),
    "Calcium (Ca)": ("mg/L", (150,)),
    "Copper": ("mg/L", (1,)),
    "Flouride": ("mg/L", (1.5,)),
    "Iron": ("mg/L", (0.3,)),
    "Manganese": ("mg/L", (0.1,)),
    "Magneisum (Mg)": ("mg/L", (100,)),
    "Nitrate (as NO3-)": ("mg/L", (45,)),
    "Sodium (Na)": ("mg/L", (200,)),
    "Chlorine Residue": ("mg/L", (0.2, 0.5)),
    "Sulphate": ("mg/L", (400,)),
    "Total Coliforms": ("CFU/100 ml", (0.0001,)),
    "E.coli": ("CFU/100 ml", (0.0001,)),
    "Aluminium (Al)": ("mg/L", (0.2,)),
    "Arsenic (As)": ("mg/L", (0.01,)),
    "Nitrate": ("mg/L", (10,)),
    "Zinc (Zn)": ("mg/L", (3,)),
    "Lead (Pb)": ("mg/L", (0.01,)),
    "Mercury (Hg)": ("mg/L", (0.001,)),
    "Cyanide": ("mg/L", (0.01,)),
    "Selenium (Se)": ("mg/L", (0.01,)),
    "Barium (Ba)": ("mg/L", (0.7,)),
    "Ammonia (NH3)": ("mg/L", (0.5,)),
    "Nickel (Ni)": ("mg/L", (0.02,)),
    "Chromium (Cr)": ("mg/L", (0.05,)),
    "Cobalt (Co)": ("mg/L", ("-")),
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
categorical_cols = ['Village','District','Date_Completed','First Water Strike Depth (m)', 'Second Water Strike Depth (m)',
       'Third Water Strike Depth (m)', 'Fourth Water Strike Depth (m)', 'Lithology_1', 'Lithology_2']
numerical_cols = ['Depth_of_overburden', 'Total_Depth', 'Depth_drilled_in_bedrock','First Water Strike Yield (L/s)', 'Second Water Strike Yield (L/s)',
       'Third Water Strike Yield (L/s)', 'Fourth Water Strike Yield (L/s)', 'Static_Water_Level', 'Borehole Yeild (L/s)', 'Altitude_(m)',]
threshold_cols = ['Ph', 'Electrical Conductivity (EC)', 'Total dissolved solids',
                       'Turbidity', 'Colour', 'Alkalinity', 'Hardness', 'Chloride', 'Nitrate', 'Nitrite',
                       'Iron', 'Copper', 'Flouride', 'Sulphate', 'E.coli', 'Suspended solids (total)',
                       'Manganese', 'Total Coliforms']

# Define all available columns in your dataset
all_columns = categorical_cols + numerical_cols + threshold_cols

# Allow the user to select a single column as the parameter to show
parameter = st.sidebar.selectbox("Select a Parameter to Visualize", all_columns,27)



# Check if the selected column belongs to categorical, numerical, or threshold columns
if parameter in categorical_cols:
    
    # Create the map for categorical columns
    fig = px.scatter_mapbox(
        data.dropna(subset=[parameter]),
        lat='lat',
        lon='long',
        color=parameter,
        hover_data=[parameter, 'Village', 'District'],
        color_discrete_sequence=px.colors.qualitative.G10,
        zoom=8
    )
    # define units and threshold value
    units = ''
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
        hover_name="Village",
        color_continuous_scale='plasma',  # Replace with your desired color scale
        size_max=15,
        zoom=8
    )
    # define units and threshold value by the dictionary
    units = 'm'
    threshold_value = None
    pass
    
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
        hover_data=[parameter, 'Village', 'District'],
        color_discrete_map={'Red': 'red', 'Green': 'green'},
        size_max=15,
        zoom=8
    )
    units = units_and_thresholds[parameter][0]
    pass

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

