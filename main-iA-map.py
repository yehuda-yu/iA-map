import streamlit as st
import pandas as pd
import folium
from branca.colormap import LinearColormap
from branca.colormap import linear
from streamlit_folium import st_folium
from folium.plugins import Draw


# Load your dataset
def load_data():
    # Load the data from a CSV file
    csv_file = r"gdf_84.csv"
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

        # Rename columns
    column_mapping = {
        "Depth_of_overburden": "Overburden Thickness (m)",
        "Depth_drilled_in_bedrock": "Depth Drilled in Bedrock (m)",
        'Total_Depth': 'Total_Depth (m)',
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
        "Manganese":"Manganese (mg/L)"
    }
    data.rename(columns=column_mapping, inplace=True)
    
    # Drop columns
    columns_to_drop = ["Colour", "Alkalinity","E.coli", "Suspended solids (total)"]
    data.drop(columns=columns_to_drop, inplace=True)
    
    return data

# Define the units and thresholds dictionary
units_and_thresholds = {
    "pH": ("", (9.5, 5.5)),
    "Electrical Conductivity (μS/cm)": ("μS/cm", (2500,)),
    "Total Dissolved Solids (mg/L)": ("mg/L", (1500,)),
    "Colour": ("TCU", (50,)),
    "Turbidity (NTU)": ("NTU", (25,)),
    "Hardness (mg/L)": ("mg/L", (600,)),
    "Chloride (mg/L)": ("mg/L", (250,)),
    "Cadmium (Cd)": ("mg/L", (0.003,)),
    "Calcium (Ca)": ("mg/L", (150,)),
    "Copper": ("mg/L", (1,)),
    "Flouride": ("mg/L", (1.5,)),
    "Iron": ("mg/L", (0.3,)),
    "Manganese (mg/L)": ("mg/L", (0.1,)),
    "Magneisum (Mg)": ("mg/L", (100,)),
    "Nitrate as N (mg/L)": ("mg/L", (10,)),
    "Sodium (Na)": ("mg/L", (200,)),
    "Chlorine Residue": ("mg/L", (0.2, 0.5)),
    "Sulfate (mg/L)": ("mg/L", (400,)),
    "Total Coliforms": ("CFU/100 ml", (0.0001,)),
    "E.coli": ("CFU/100 ml", (0.0001,)),
    "Aluminium (Al)": ("mg/L", (0.2,)),
    "Arsenic (As)": ("mg/L", (0.01,)),
    "Nitrate as NO3": ("mg/L", (45,)),
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


# Load the data
data = load_data()

# Define lists of columns
categorical_cols = ['Village', 'District', 'Date_Completed', 'First Water Strike Depth (m)', 'Second Water Strike Depth (m)',
            'Third Water Strike Depth (m)', 'Fourth Water Strike Depth (m)', 'Lithology_1', 'Lithology_2']

numerical_cols = ['Overburden Thickness (m)', 'Total_Depth (m)', 'Depth Drilled in Bedrock (m)', 'First Water Strike Yield (L/s)',
                'Second Water Strike Yield (L/s)', 'Third Water Strike Yield (L/s)', 'Fourth Water Strike Yield (L/s)',
                'Static Water Level (m)', 'Borehole Yield (L/s)', 'Elevation (m)']

threshold_cols = ['pH', 'Electrical Conductivity (μS/cm)', 'Total Dissolved Solids (mg/L)',
                'Turbidity (NTU)', 'Hardness (mg/L)', 'Chloride (mg/L)', 'Nitrate as N (mg/L)', 'Sulfate (mg/L)',
                'Manganese (mg/L)', 'Total Coliforms']


def load_map(data,parameter):

    # Check if the selected column belongs to categorical, numerical, or threshold columns
    if parameter in categorical_cols:

        # load tata
        data = load_data()

        # Drop the rows with missing values
        data = data.dropna(subset=[parameter])

        # Create a map object
        m = folium.Map(location=[data['lat'].mean(), data['long'].mean()], zoom_start=9, tiles='openstreetmap')

        # Add Esri Satellite tile layer
        tile = folium.TileLayer(
            tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
            attr='Esri',
            name='Esri Satellite',
            overlay=False,
            control=True
        )
        tile.add_to(m)

        # Add Stamen Terrain map layer
        folium.TileLayer(
            tiles='https://stamen-tiles-{s}.a.ssl.fastly.net/terrain/{z}/{x}/{y}.png',
            attr='Stamen',
            name='Stamen',
            overlay=False,
            control=True,
        ).add_to(m)

        for index, row in data.iterrows():
            loc = (row['lat'], row['long'])
            popup_text = f"""<b>Village: {row['Village']}</b><br>  
                            lat: {row['lat']}<br>
                            long: {row['long']}<br>
                            {parameter}: {row[parameter]}<br>
                            Total_Depth (m): {row['Total_Depth (m)']}<br>
                            Borehole Yeild (L/s): {row['Borehole Yeild (L/s)']}<br>
                            Nitrate as N (mg/L): {row['Nitrate as N (mg/L)']}<br>
                            Electrical Conductivity (μS/cm): {row['Electrical Conductivity (μS/cm)']}<br>
                        """

            # color = categorical_colors(data[parameter].unique().tolist().index(row[parameter]))

            folium.Circle(
                location=loc,
                popup=folium.Popup(popup_text, max_width=450),
                radius=100,
                fill=True,
                color='YlGnBu',
                capacity=.9,
            ).add_to(m)

        # Add legends and layer control
        folium.LayerControl().add_to(m)

    
    elif parameter in threshold_cols:
        
        # Set threshold value and color dictionary based on the selected column and dictionary
        threshold_value = float(units_and_thresholds[parameter][1][0])

        # load tata
        data = load_data()

        # Drop the rows with missing values
        data = data.dropna(subset=[parameter])

        # Function to determine the color based on the threshold
        def get_color(value):
            if value >= threshold_value:
                return 'red'
            else:
                return 'green'

        # Define the colormap
        colormap = LinearColormap(
            colors=['green', 'red'],
            vmin=data[parameter].min(),
            vmax=data[parameter].max()
        )

        # Create a map object
        m = folium.Map(location=[data['lat'].mean(), data['long'].mean()], zoom_start=9, tiles='openstreetmap')

        # Add Esri Satellite tile layer
        tile = folium.TileLayer(
            tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
            attr='Esri',
            name='Esri Satellite',
            overlay=False,
            control=True
        )
        tile.add_to(m)

        # Add Stamen Terrain map layer
        folium.TileLayer(
            tiles='https://stamen-tiles-{s}.a.ssl.fastly.net/terrain/{z}/{x}/{y}.png',
            attr='Stamen',
            name='Stamen',
            overlay=False,
            control=True,
        ).add_to(m)

        for loc, p in zip(zip(data["lat"], data["long"]), data[parameter]):
            # Determine the color based on the threshold
            color = get_color(p)

            # Popup text based on index
            index = data.index[(data['lat'] == loc[0]) & (data['long'] == loc[1])].tolist()

            # Create popup text with Village as the title
            popup_text = f"<b>Village: {data.loc[index[0], 'Village']}</b><br>"  # Village as title
            popup_text += f"lat: {data.loc[index[0], 'lat']}<br>"
            popup_text += f"long: {data.loc[index[0], 'long']}<br>"
            popup_text += f"{parameter}: {data.loc[index[0], parameter]}<br>"
            popup_text += f"Total_Depth (m): {data.loc[index[0], 'Total_Depth (m)']}<br>"
            popup_text += f"Borehole Yeild (L/s): {data.loc[index[0], 'Borehole Yeild (L/s)']}<br>"
            popup_text += f"Nitrate as N (mg/L): {data.loc[index[0], 'Nitrate as N (mg/L)']}<br>"
            popup_text += f"Electrical Conductivity (μS/cm): {data.loc[index[0], 'Electrical Conductivity (μS/cm)']}<br>"

            folium.Circle(
                location=loc,
                popup=folium.Popup(popup_text, max_width=450),
                radius=20,  # yarıçap
                fill=True,
                color=color,  # Use the color determined by the threshold
                capacity=0.9,
            ).add_to(m)

        # Add legends and layer control
        folium.LayerControl().add_to(m)

        # Add the colorbar to the map
        colormap.add_to(m)

    elif parameter in numerical_cols:

        # load tata
        data = load_data()

        # Drop the rows with missing values
        data = data.dropna(subset=[parameter])

        # define popup text
        popup_list = ['Village', 'lat','long',parameter,'Total_Depth (m)', 'Borehole Yeild (L/s)', 'Nitrate as N (mg/L)', 'Electrical Conductivity (μS/cm)']

        # define popup text based on the columns in the popup_list
        # popup_text = '<br>'.join([f'{col}: {data.iloc[i][col]}' for col in popup_list])

        # Define the Viridis color map
        colormap = LinearColormap(colors=['#264653', '#287271', '#2a9d8f', '#8ab17d', '#babb74', '#e9c46a', '#efb366', '#f4a261', '#ee8959', '#e76f51'],
                                    vmin=data[parameter].min(),
                                    vmax=data[parameter].max())


        # plot using folium
        # Create a map object
        m = folium.Map(location=[data['lat'].mean(), data['long'].mean()], zoom_start=9, tiles='openstreetmap')

        # Add Esri Satellite tile layer
        tile = folium.TileLayer(
            tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
            attr='Esri',
            name='Esri Satellite',
            overlay=False,
            control=True
        )
        tile.add_to(m)

        # Add Stamen Terrain map layer
        folium.TileLayer(
            tiles='https://stamen-tiles-{s}.a.ssl.fastly.net/terrain/{z}/{x}/{y}.png',
            attr='Stamen',
            name='Stamen',
            overlay=False,
            control=True,
        ).add_to(m)

        for loc, p in zip(zip(data["lat"],data["long"]),data[parameter]):
            
            # popup text based on index
            index = data.index[(data['lat'] == loc[0]) & (data['long'] == loc[1])].tolist()
            #   add popup text based on list of columns

            popup_text = """<b>Village: {}</b><br>
                            lat: {}<br>
                            long: {}<br>
                            parameter: {}<br>
                            Total_Depth (m): {}<br>
                            Borehole Yeild (L/s): {}<br>
                            Nitrate as N (mg/L): {}<br>
                            Electrical Conductivity (μS/cm): {}<br>
                            """
            
            popup_text = popup_text.format(
                                            data.loc[index[0], "Village"],
                                            data.loc[index[0], "lat"],
                                            data.loc[index[0], "long"],
                                            data.loc[index[0], parameter],
                                            data.loc[index[0], "Total_Depth (m)"],
                                            data.loc[index[0], "Borehole Yeild (L/s)"],
                                            data.loc[index[0], "Nitrate as N (mg/L)"],
                                            data.loc[index[0], "Electrical Conductivity (μS/cm)"]
                                            )

            folium.Circle(
            location=loc,
            popup=folium.Popup(popup_text,max_width=450),
            radius=20, 
            fill=True, 
            color=colormap(p),
            capacity=0.9,
        ).add_to(m)

        # add laegends and layer control
        folium.LayerControl().add_to(m)

        # add colormap to map
        colormap.caption = parameter
        colormap.add_to(m)


    return m 

# App UI
st.title("Water Drilling Points in Uganda")

# Provide instructions to users
st.header("Instructions")
st.markdown("Select a parameter to visualize from the dropdown menu.")

# Define all available columns in your dataset
all_columns = categorical_cols + numerical_cols + threshold_cols

c1, c2 = st.columns(2)


with c1:

    # Allow the user to select a single column as the parameter to show
    parameter1 = st.selectbox("Select a Parameter to Visualize", all_columns, 25)

    # title for map
    st.write(f"Map1: {parameter1}")

    m1 = load_map(data, parameter1) 
    Draw(export=True).add_to(m1)
    st_folium(m1, width=350, height=500)

with c2:

    # Allow the user to select a single column as the parameter to show
    parameter2 = st.selectbox("Select a Parameter to Visualize", all_columns, 20)

    # title for map
    st.write(f"Map2: {parameter2}")

    m2 = load_map(data, parameter2)
    Draw(export=True).add_to(m2)
    st_folium(m2, width=350, height=500)

# m = load_map(data, parameter) 
# Draw(export=True).add_to(m)

# st_folium(m, width=700, height=500)
# m.to_streamlit(width=700, height=500, add_layer_control=True)
