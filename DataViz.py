import streamlit as st
import pandas as pd
import altair as alt

# Load the data
file_path = r"All_Attribute_Table.xlsx"
data = pd.read_excel(file_path)
st.markdown("""
    <style>
    .stMarkdown h3 {
        font-family: 'Arial', sans-serif;
        color: #2e4053;
        background-color: #f4f6f7;
        padding: 10px;
        border-radius: 5px;
        box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# Display the column names to identify the correct names
st.header("DATA ANALYSIS DASHBOARD")

st.subheader("Fields in Data")
columns = data.columns
# Create a 3x3 grid layout for column names
num_columns = 2
rows = [columns[i:i + num_columns] for i in range(0, len(columns), num_columns)]

html_string = '<div style="display: flex; flex-wrap: wrap;">'
for row in rows:
    html_string += '<div style="width: 33.33%;">'
    for col in row:
        html_string += f'<span style="display: block; padding: 5px; border: 1px solid #ccc; margin: 2px;">{col}</span>'
    html_string += '</div>'
html_string += '</div>'

st.markdown(html_string, unsafe_allow_html=True)
# Preprocess data
data['Date'] = pd.to_datetime(data['Accident Date'], errors='coerce')
data['Year'] = data['Date'].dt.year
data['Month'] = data['Date'].dt.month_name()
data['Day'] = data['Date'].dt.day_name()


# Title and Description
st.title(' Accident Data Analytics Dashboard')
st.markdown("""
This dashboard provides a comprehensive analysis of accident data, covering all available fields including trends, severity, location, environmental conditions, vehicle involvement, and more.
""")

# Sidebar filters
st.sidebar.header('Filters')

# Identify the correct column names
years = data['Year'].dropna().unique()

# Replace 'Accident_Severity' with the actual column name from your dataset
severity_column = 'Accident_Severity'  # Replace with the actual column name

selected_year = st.sidebar.multiselect('Year', options=years, default=years)

# Ensure the column exists before using it
if severity_column in data.columns:
    severities = data[severity_column].dropna().unique()
    selected_severity = st.sidebar.multiselect('Accident_Severity', options=severities, default=severities)
    filtered_data = data[(data['Year'].isin(selected_year)) & (data[severity_column].isin(selected_severity))]
else:
    st.sidebar.write(f"Column '{severity_column}' not found in the dataset.")
    filtered_data = data[data['Year'].isin(selected_year)]

# Summary Metrics
st.header("Summary Metrics")
total_accidents = filtered_data.shape[0]
total_casualties = filtered_data['Number_of_Casualties'].sum()
total_vehicles = filtered_data['Number_of_Vehicles'].sum()
unique_districts = filtered_data['Local_Authority_(District)'].nunique()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Accidents", total_accidents)
col2.metric("Total Casualties", int(total_casualties))
col3.metric("Total Vehicles Involved", int(total_vehicles))
col4.metric("Unique Districts", unique_districts)

# Time-Based Analysis
st.header("Time-Based Analysis")

st.subheader("Accidents Over Time") 
st.markdown("""
            
**Description**: This line chart shows the number of accidents per month over the selected period. It helps to identify trends and seasonal patterns in accident occurrences.

**Inference**: Look for peaks and troughs to identify high-risk periods. For example, an increase in accidents during winter months might indicate weather-related hazards.

""")
# Add the corresponding chart code here

accidents_over_time = filtered_data.groupby(filtered_data['Date'].dt.to_period("M")).size().reset_index(name='Accidents')
accidents_over_time['Date'] = accidents_over_time['Date'].dt.to_timestamp()

line_chart = alt.Chart(accidents_over_time).mark_line().encode(
    x='Date:T',
    y='Accidents:Q'
).properties(width=800, height=400)
st.altair_chart(line_chart, use_container_width=True)

            
st.subheader("Accidents by Day of the Week:")

st.markdown(""" 
            
**Description**: This bar chart displays the number of accidents occurring on each day of the week.

**Inference**: Identify which days have the highest number of accidents. For instance, weekends might show higher accident rates due to increased travel and leisure activities.

""",unsafe_allow_html=True)

accidents_by_day = filtered_data['Day'].value_counts().reset_index()
accidents_by_day.columns = ['Day', 'Count']
bar_chart_day = alt.Chart(accidents_by_day).mark_bar().encode(
    x=alt.X('Count:Q', title='Number of Accidents'),
    y=alt.Y('Day:N', sort='-x'),
    tooltip=['Day', 'Count']
).properties(width=800, height=400)
st.altair_chart(bar_chart_day, use_container_width=True)

st.subheader("Accidents by Month")
st.markdown("""
**Description**: This bar chart presents the number of accidents for each month.

**Inference**: Seasonal variations in accident rates can be observed. This can help in planning targeted safety campaigns.
            
""")

accidents_by_month = filtered_data['Month'].value_counts().reset_index()
accidents_by_month.columns = ['Month', 'Count']
bar_chart_month = alt.Chart(accidents_by_month).mark_bar().encode(
    x=alt.X('Count:Q', title='Number of Accidents'),
    y=alt.Y('Month:N', sort='-x'),
    tooltip=['Month', 'Count']
).properties(width=800, height=400)
st.altair_chart(bar_chart_month, use_container_width=True)

# Severity Analysis

if severity_column in filtered_data.columns:
    st.header("Severity Analysis")
    severity_count = filtered_data[severity_column].value_counts().reset_index()
    severity_count.columns = [severity_column, 'Count']
    

    st.subheader("Accident Severity Distribution")
    st.markdown('''
        **Description**: This pie chart shows the proportion of accidents by severity (e.g., fatal, serious, slight).

        **Inference**: Assess the distribution of accident severities. A high proportion of serious or fatal accidents may indicate a need for improved safety measures.

    '''
    )
    pie_chart = alt.Chart(severity_count).mark_arc().encode(
        theta=alt.Theta(field="Count", type="quantitative"),
        color=alt.Color(field=severity_column, type="nominal"),
        tooltip=[severity_column, 'Count']
    ).properties(width=400, height=400)
    st.altair_chart(pie_chart, use_container_width=True)

    severity_over_time = filtered_data.groupby([filtered_data['Date'].dt.to_period("M"), severity_column]).size().reset_index(name='Accidents')
    severity_over_time['Date'] = severity_over_time['Date'].dt.to_timestamp()
    
    st.subheader("Accidents by Severity Over Time")
    st.markdown('''
        **Description**: This stacked bar chart shows the number of accidents of different severities over time.

        **Inference**: Observe trends in accident severities over time. Look for periods with increases in severe accidents to identify potential causes.
        
    ''')
    bar_chart_severity_time = alt.Chart(severity_over_time).mark_bar().encode(
        x='Date:T',
        y='Accidents:Q',
        color=f'{severity_column}:N',
        tooltip=['Date:T', severity_column, 'Accidents']
    ).properties(width=800, height=400)
    st.altair_chart(bar_chart_severity_time, use_container_width=True)

# Location Analysis
st.header("Location Analysis")

st.subheader("Accidents by Local Authority (District)")
st.markdown('''
**Description**: This bar chart displays the number of accidents by district.

**Inference**: Identify high-risk areas. Districts with a high number of accidents might require targeted interventions.
            
''')
location_count = filtered_data['Local_Authority_(District)'].value_counts().reset_index()
location_count.columns = ['Local_Authority_(District)', 'Count']

bar_chart_location = alt.Chart(location_count).mark_bar().encode(
    x=alt.X('Count:Q', title='Number of Accidents'),
    y=alt.Y('Local_Authority_(District):N', sort='-x'),
    tooltip=['Local_Authority_(District)', 'Count']
).properties(width=800, height=400)
st.altair_chart(bar_chart_location, use_container_width=True)
st.subheader("Urban or Rural Area")
st.markdown('''

**Description**: This bar chart shows the number of accidents in urban vs. rural areas.

**Inference**: Compare accident rates between urban and rural settings. Urban areas might have higher accident rates due to higher traffic density.
            
''')
urban_rural_count = filtered_data['Urban_or_Rural_Area'].value_counts().reset_index()
urban_rural_count.columns = ['Urban_or_Rural_Area', 'Count']

bar_chart_urban_rural = alt.Chart(urban_rural_count).mark_bar().encode(
    x=alt.X('Count:Q', title='Number of Accidents'),
    y=alt.Y('Urban_or_Rural_Area:N', sort='-x'),
    tooltip=['Urban_or_Rural_Area', 'Count']
).properties(width=800, height=400)
st.altair_chart(bar_chart_urban_rural, use_container_width=True)

# Environmental Conditions
st.header("Environmental Conditions")
light_conditions_count = filtered_data['Light_Conditions'].value_counts().reset_index()
light_conditions_count.columns = ['Light_Conditions', 'Count']

st.subheader("Accidents by Light Conditions")
st.markdown('''
**Description**: This bar chart displays the number of accidents under different light conditions (e.g., daylight, darkness).

**Inference**: Determine if light conditions play a significant role in accident occurrences. For example, a high number of accidents in darkness may suggest the need for better street lighting.
         
''')
bar_chart_light = alt.Chart(light_conditions_count).mark_bar().encode(
    x=alt.X('Count:Q', title='Number of Accidents'),
    y=alt.Y('Light_Conditions:N', sort='-x'),
    tooltip=['Light_Conditions', 'Count']
).properties(width=800, height=400)
st.altair_chart(bar_chart_light, use_container_width=True)

weather_conditions_count = filtered_data['Weather_Conditions'].value_counts().reset_index()
weather_conditions_count.columns = ['Weather_Conditions', 'Count']

st.subheader("Accidents by Weather Conditions")
st.markdown('''
**Description**: This bar chart presents the number of accidents under various weather conditions (e.g., clear, rain, fog).

**Inference**: Identify weather conditions that contribute to higher accident rates. This information can help in issuing weather-related travel advisories.

''')
bar_chart_weather = alt.Chart(weather_conditions_count).mark_bar().encode(
    x=alt.X('Count:Q', title='Number of Accidents'),
    y=alt.Y('Weather_Conditions:N', sort='-x'),
    tooltip=['Weather_Conditions', 'Count']
).properties(width=800, height=400)
st.altair_chart(bar_chart_weather, use_container_width=True)

road_surface_conditions_count = filtered_data['Road_Surface_Conditions'].value_counts().reset_index()
road_surface_conditions_count.columns = ['Road_Surface_Conditions', 'Count']

st.subheader("Accidents by Road Surface Conditions")
st.markdown('''
            
**Description**: This bar chart shows the number of accidents on different road surface conditions (e.g., dry, wet, icy).

**Inference**: Assess the impact of road surface conditions on accident rates. High accident rates on wet or icy roads may indicate the need for better road maintenance or public warnings.
            
''')
bar_chart_road_surface = alt.Chart(road_surface_conditions_count).mark_bar().encode(
    x=alt.X('Count:Q', title='Number of Accidents'),
    y=alt.Y('Road_Surface_Conditions:N', sort='-x'),
    tooltip=['Road_Surface_Conditions', 'Count']
).properties(width=800, height=400)
st.altair_chart(bar_chart_road_surface, use_container_width=True)

# Vehicle and Casualty Analysis
st.header("Vehicle and Casualty Analysis")
vehicle_type_count = filtered_data['Vehicle_Type'].value_counts().reset_index()
vehicle_type_count.columns = ['Vehicle_Type', 'Count']

st.subheader("Accidents by Vehicle Type")
st.markdown('''

**Description**: This bar chart displays the number of accidents involving different types of vehicles (e.g., cars, motorcycles).

**Inference**: Identify which vehicle types are most frequently involved in accidents. This can help in targeting safety measures for specific vehicle users.

         
''')
bar_chart_vehicles = alt.Chart(vehicle_type_count).mark_bar().encode(
    x=alt.X('Count:Q', title='Number of Accidents'),
    y=alt.Y('Vehicle_Type:N', sort='-x'),
    tooltip=['Vehicle_Type', 'Count']
).properties(width=800, height=400)
st.altair_chart(bar_chart_vehicles, use_container_width=True)

casualty_count = filtered_data['Number_of_Casualties'].value_counts().reset_index()
casualty_count.columns = ['Number_of_Casualties', 'Count']

st.subheader("Number of Casualties")
st.markdown('''

**Description**: This histogram shows the distribution of the number of casualties per accident.

**Inference**: Determine how many accidents involve multiple casualties. High casualty accidents may need special attention.
         
''')
histogram_casualties = alt.Chart(casualty_count).mark_bar().encode(
    x=alt.X('Number_of_Casualties:Q', bin=True),
    y=alt.Y('Count:Q', title='Number of Accidents'),
    tooltip=['Number_of_Casualties', 'Count']
).properties(width=800, height=400)
st.altair_chart(histogram_casualties, use_container_width=True)

vehicle_count = filtered_data['Number_of_Vehicles'].value_counts().reset_index()
vehicle_count.columns = ['Number_of_Vehicles', 'Count']


st.subheader("Number of Vehicles Involved")
st.markdown('''
**Description**: This histogram presents the distribution of the number of vehicles involved in accidents.

**Inference**: Assess the typical scale of accidents in terms of vehicle involvement. Multi-vehicle accidents may require different safety interventions compared to single-vehicle accidents.
         
''')
histogram_vehicles = alt.Chart(vehicle_count).mark_bar().encode(
    x=alt.X('Number_of_Vehicles:Q', bin=True),
    y=alt.Y('Count:Q', title='Number of Accidents'),
    tooltip=['Number_of_Vehicles', 'Count']
).properties(width=800, height=400)
st.altair_chart(histogram_vehicles, use_container_width=True)

st.header("Addtional Insights")

junction_control_count = filtered_data['Junction_Control'].value_counts().reset_index()
junction_control_count.columns = ['Junction_Control', 'Count']


st.subheader("Accidents by Junction Control")
st.markdown('''
**Description**: This bar chart displays the number of accidents at different types of junction controls (e.g., traffic signals, roundabouts).

**Inference**: Assess the safety of different junction controls. High accident rates at specific junction types might indicate the need for redesign or additional safety measures.
         
''')
bar_chart_junction_control = alt.Chart(junction_control_count).mark_bar().encode(
    x=alt.X('Count:Q', title='Number of Accidents'),
    y=alt.Y('Junction_Control:N', sort='-x'),
    tooltip=['Junction_Control', 'Count']
).properties(width=800, height=400)
st.altair_chart(bar_chart_junction_control, use_container_width=True)

speed_limit_count = filtered_data['Speed_limit'].value_counts().reset_index()
speed_limit_count.columns = ['Speed_limit', 'Count']

st.subheader("Accidents by Speed Limit:")
st.markdown('''
**Description**: This bar chart shows the number of accidents occurring in areas with different speed limits.

**Inference**: Evaluate the relationship between speed limits and accident rates. Areas with high accident rates might need speed limit adjustments or better enforcement.
         
''')
bar_chart_speed_limit = alt.Chart(speed_limit_count).mark_bar().encode(
    x=alt.X('Count:Q', title='Number of Accidents'),
    y=alt.Y('Speed_limit:N', sort='-x'),
    tooltip=['Speed_limit', 'Count']
).properties(width=800, height=400)
st.altair_chart(bar_chart_speed_limit, use_container_width=True)
