import pandas as pd
import numpy as np
import time
import streamlit as st
from datetime import date

import subprocess
import sys


import folium
from streamlit_folium import folium_static

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

#install("streamlit_folium")


# SETTING PAGE CONFIG TO WIDE MODE
st.set_page_config(layout="wide")


#@st.cache(persist=True)
def load_data(df, decimal="."):
    data = pd.read_csv(df,  sep=";")
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis="columns", inplace=True)
    data["date"] = pd.to_datetime(data["date"])
    return data


df = load_data("dataset3.csv")

df = df[(df["nom region"] != "Mayotte") &
        (df["nom region"] !="Guadeloupe") &
        (df["nom region"] !="Martinique") &
        (df["nom region"] !="Guyane") &
        (df["nom region"] !="La Réunion") &
        (df["nom region"].notnull())]

# ------------ Data Cleansing ----------------

actual_year = date.today().year

#Dataset cleaned
cleaned_data = df.copy()
cleaned_data = cleaned_data[cleaned_data['date'].notna()]
cleaned_data = cleaned_data.drop(columns=['adr lb add1', 'adr lb add2', 'adr lb add3', 'adr lb lieu','sup id','coord','coordonnees','id','nat id','tpo id', 'adr nm cp','sup nm haut', 'year'])
cleaned_data["année"]= cleaned_data["date"].dt.year


#---------------- Map Data ----------------

#Create a new dataframe with a column "Count" to count the number of installations
#map_data = df.copy()

map_data = df["nom region"].value_counts().rename_axis('nom region').reset_index(name='count')
#map_data["count"] =1

region_json = f"regions.geojson"


#Preparing metrics

#Total installations
total = len(df)

#Total 5G installations
total_5G = len(df.loc[df['generation'] == "5G"])
data_5G = df.loc[df['generation'] == "5G"]

#Age of installations
cleaned_data["age"] = actual_year - (cleaned_data["année"])

#------------ Data Overview ----------------

st.markdown("<h1 style='text-align: center; '>Dashboard on Mobile Telecom Network installations in France</h1>", unsafe_allow_html=True)


with st.sidebar:
    st.header('Kabirou Kanlanfeyi')

    with st.expander("About Me"):
        st.write(
            """
            I am a currently working as Data Analyst in insurance field at Groupe Covéa.My areas of interest are: Insurance, Finance and GIS.

            Want to connect with me? Follow these links : [LinkedIn] (https://www.linkedin.com/in/kabirou-kanlanfeyi/) , [GitHub] (https://github.com/kabirou7)

            """
        )



#--------------Functions ---------------

def ranking_chart(dataset,column, title):

    col_label = column
    col_values = "Count"

    v = dataset[column].value_counts()
    new = pd.DataFrame({
    col_label: v.index,
    col_values: v.values
    })
    new = new.sort_values(by=col_values, ascending=True)

    fig = px.bar(new, x = col_values, y = col_label, color = col_values, title = title, orientation='h')
    #fig.update_layout(xaxis={col_label:'total descending'} )

    st.plotly_chart(fig)

    return fig

# -----------------Data Presentation -----------

# Menu

select = st.sidebar.selectbox(
    "Select the page:",
    ("Data Presentation",
     "Statistics",
     "Department View",
     "Map View",
     "Samples of Code"))

if select == "Data Presentation":
    st.markdown("<h2 style='text-align: center; '>Data Presentation</h2>", unsafe_allow_html=True)

    st.info("""
             The dataset used is from the [ANFR OPEN DATA] (https://data.anfr.fr/anfr/portail) which provides information about all installations of telecom networks such as 2G,
             3G, 4G and 5G antennas and the different frequencies related to them. We only focus on the Metropolitan France so data related to DOM-TOM are removed. """)


    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.empty()
    with col2:
        st.empty()
    with col3:
        st.image("ANFR.png")
    with col4:
        st.empty()
    with col5:
        st.empty()


    with st.expander("What is ANFR"):
        st.write("""
             The National Frequency Agency is a public administrative establishment created by the telecommunications regulatory law of July 26, 1996, 
             with the mission of managing the radio spectrum in France.     """)

    #with st.expander("Raw Data"):
    st.markdown("<h3 style='text-align: center; '>Raw Data</h3>", unsafe_allow_html=True)
    st.write("This dataset is composed of", len(df), " rows and ", len(df.columns), "columns")
    st.dataframe(df.head(1000))

    #with st.expander("Cleaned Data"):
    st.markdown("<h3 style='text-align: center; '>Cleaned Data</h3>", unsafe_allow_html=True)
    st.write("After cleansing, we ended up with", len(cleaned_data), " rows and ", len(cleaned_data.columns), "columns")
    st.dataframe(cleaned_data.head(1000))
        


elif select =="Statistics":
    st.markdown("<h3 style='text-align: center; '>Data Analysis</h3>", unsafe_allow_html=True)

    #Display metrics

    min_year = min(cleaned_data["année"])
    max_year = max(cleaned_data["année"])
    avg_age = round(cleaned_data["age"].mean(),2)


    #------------ Statistcis ----------------

    st.subheader("Overall Statistics")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total installations", total)
    col2.metric("Number d'installations 5G", total_5G, "+ 12%")
    col3.metric("Average age of installations (years)", avg_age)

    # Data Repartition
    st.subheader("Detailed Statistics")

    # Affichage des graphes
    operators = df["operateur"].value_counts()
    date = cleaned_data["année"].value_counts()


    ranking_chart(df,"operateur", "Distribution by mobile operator")
    #st.write("""Orange is the top mobile operator more than 33 percent the total of the total installations in France.""")   


    st.markdown("<h3 style='text-align: center; '>Number of installations over the time </h3>", unsafe_allow_html=True)
    fig = px.line(cleaned_data, x="année", y="année", color='generation')


    st.caption("Evolution of the number of installations")
    st.line_chart(date)

    st.markdown("<h3 style='text-align: center; '>Ranking by Network Generation (2G,3G, 4G and 5G) </h3>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        ranking_chart(df,"nom region", "Distribution by Region (all Generations)")
    with col2:
        ranking_chart(data_5G, "nom region","Distribution by Region (5G only)")
    #ranking_chart(df,"nom departement","Distribution by Department")

    generation_fig = px.pie(
        hole = 0.6,
        labels = df["generation"],
        names = df["generation"],
        title='Repartition by network generation'
    )

    freq_fig = px.pie(
        hole = 0.6,
        labels = df["frequence"],
        names = df["frequence"],
        title='Repartition by frequency of generations'
    )

    statut_fig = px.pie(
        hole = 0.6,
        labels = df["statut"],
        names = df["statut"],
    )


    col1.plotly_chart(generation_fig, use_column_width=True)
    col2.plotly_chart(freq_fig, use_column_width=True)


elif select =="Department View":
    st.markdown("<h3 style='text-align: center; '>Department View</h3>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    col1.info("You can search the departement you want to show by typing its name and filter all the different graphs and KPIs bellow.")

    with col2:
        department = st.selectbox('Select the departement', df["nom departement"].unique())

    filtered_data = df[(df['nom departement'] == department)]

    metric_total = len(filtered_data)
    metric_5G = len(filtered_data.loc[filtered_data['generation'] == "5G"])

    col1, col2= st.columns(2)
    #col1.markdown("<h3 style='text-align: center; '>metric_total</h3>", unsafe_allow_html=True)
    with col1:
        st.caption("Total Number of installations")
        st.markdown("# "+str(metric_total))
    with col2:
        st.caption("Number of 5G installations")
        st.markdown("# "+str(metric_5G))


    col1, col2 = st.columns(2)
    with col1:
        ranking_chart(filtered_data,"operateur", "Ranking of Operators")

    generation_fig = px.pie(
        hole = 0.6,
        labels = filtered_data["generation"],
        names = filtered_data["generation"],
        title='Repartition by network generation'
    )

    with col2:
        st.plotly_chart(generation_fig, use_column_width=True)


elif select =="Map View":
    select_code = st.sidebar.selectbox(
    "Select the code to display:",
    ("Density Map",
    "Shape Map"))


    if select_code == "Density Map":

        st.markdown("<h3 style='text-align: center; '>Density Map</h3>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)

        with col1:
            region = st.selectbox('Select the region', df["nom region"].unique())
        with col2:
            operateurs = st.selectbox('Select the Mobile Operator', df["operateur"].unique())

        with col1:
            statut = st.selectbox('Select the Statut', df["statut"].unique())
        with col2:
            generations = st.selectbox('Select the Generation', df["generation"].unique())

        filtered_data = df[(df['nom region'] == region) & (df['operateur'] == operateurs) & (df['statut'] == statut) & (df['generation'] == generations) ]

        metric_total = len(filtered_data)
        metric_5G = len(filtered_data.loc[filtered_data['generation'] == "5G"])



        st.caption("Total Number of installations")
        st.markdown("# "+str(metric_total))


        col1, col2 = st.columns(2)
        with col1:
            st.map(filtered_data)
        with col2:
            ranking_chart(filtered_data,"nom departement", "Ranking by Department")

    elif select_code == ("Shape Map"):

        st.info(""" This map is created by combining our original dataset to a Spatial File with the shapes of the region in France in a GeoJson format. We used [Folium] (https://python-visualization.github.io/folium/quickstart.html) and Choropleth for this task.""")


        st.markdown("<h3 style='text-align: center; '>Shape Map</h3>", unsafe_allow_html=True)


        col1, col2 = st.columns(2)
        with col1:

            m = folium.Map(location=[46.7111,1.7191], tiles='CartoDB positron', name="Light Map",
                       zoom_start=5, attr="My Data attribution")

            folium.Choropleth(
            geo_data=region_json,
            name="choropleth",
            data=map_data,
            columns=["nom region", "count"],
            key_on="feature.properties.nom",
            fill_color="YlOrRd",
            fill_opacity=0.7,
            line_opacity=0.2,
            legend_name="Number of installations"
            ).add_to(m)

            folium.features.GeoJson('regions.json',name="States", popup=folium.features.GeoJsonPopup(fields=["nom"]), zoom_on_click = True).add_to(m)

            folium_static(m, width=500, height=400)


elif select == "Samples of Code":

    select_code = st.sidebar.selectbox(
    "Select the code to display:",
    ("Dynamic Metrics Code",
    "Charts Code",
     "Mapping with Folium"))
    if select_code == "Dynamic Metrics Code":
        st.subheader("Metrics Code")
        code = '''

        #Filtered Data
        filtered_data = df[(df['nom region'] == region) & (df['operateur'] == operateurs) & (df['statut'] == statut) & (df['generation'] == generations) ]

        #Create metrics variable
        metric_total = len(filtered_data)
        metric_5G = len(filtered_data.loc[filtered_data['generation'] == "5G"])

        #Display the metric with st.markdown()
        st.caption("Total Number of installations")
        st.markdown("# "+str(metric_total))
        '''
        st.code(code, language ='python')

    elif select_code == "Charts Code":
        st.subheader("Display the Map")
        code = '''

        def ranking_chart(dataset,column, title):

        col_label = column
        col_values = "Count"

        v = dataset[column].value_counts()
        new = pd.DataFrame({
        col_label: v.index,
        col_values: v.values
        })
        new = new.sort_values(by=col_values, ascending=True)

        fig = px.bar(new, x = col_values, y = col_label, color = col_values, title = title, orientation='h')

        st.plotly_chart(fig)

        '''

        st.code(code, language ='python')

    elif select_code == "Mapping with Folium":
        st.subheader("Mapping with Folium and Choropleth")
        code = '''

        folium.Choropleth(
        geo_data=region_json,
        name="choropleth",
        data=map_data,
        columns=["nom region", "count"],
        key_on="feature.properties.nom",
        fill_color="YlOrRd",
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name="Number of installations"
        ).add_to(m)

        folium.features.GeoJson('regions.json',name="States", popup=folium.features.GeoJsonPopup(fields=["nom"]), zoom_on_click = True).add_to(m)

        folium_static(m, width=450, height=300)

        '''

        st.code(code, language ='python')

