# -*- coding: utf-8 -*-
"""
Created on Sun Jun  7 14:01:31 2020

@author: tsen6
"""

import streamlit as st
import geopandas as gpd
import pandas as pd
import plotly.express as px
import fiona
import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
from urllib.request import urlopen
import geojson
import datetime

# st.title("My Streamlit App")

# clicked = st.button("Click Me")

# if clicked:
#     st.balloons()
    
# url_maryland = "https://github.com/trisha-sen/Streamlit_test/raw/master/tl_2019_24_tract.zip"
# maryland = gpd.read_file(url_maryland)
# maryland['COUNTYFP'] = maryland['COUNTYFP'].astype(str).astype(int)
# baltimore_counties = [510] #[163] #[87,93,99,125,147,163]

# baltimore = gpd.GeoDataFrame()
# for county in baltimore_counties:
#     #print(county)
#     temp = maryland[maryland['COUNTYFP']==county]
#     #print(temp)
#     baltimore = baltimore.append(temp)
'''
# Baltimore city police districts
'''
@st.cache(persist=True)
def load_data():
    url_dataframe = "https://github.com/trisha-sen/Streamlit_test/raw/master/Baltimore_city_details.csv"
    dBalt = pd.read_csv(url_dataframe)
# dBalt
    
    url_baltimore_map = "https://github.com/trisha-sen/Streamlit_test/raw/master/baltimore.geojson"
    with urlopen(url_baltimore_map) as response:
        baltimore_map = geojson.load(response)
    return(dBalt, baltimore_map)

def plot_baltimore(dBalt, baltimore_map):   
    fig = px.choropleth(dBalt, geojson=baltimore_map, 
                        locations='NAME', featureidkey="properties.NAME",
                        color='Police_district_x', #color_continuous_scale="Viridis",
                        # scope="usa",
                        labels={'Police_district_x':'Police District'}    
                        )
    fig.update_geos(fitbounds="locations", visible=False)
    # fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    return(fig)

dBalt, baltiomore_map = load_data()
# fig = plot_baltimore()
# st.plotly_chart(fig)

districts = dBalt.Police_district_x.unique()

police_district = st.radio(
    "Select a district to zoom into", 
    districts )

d = st.date_input(
    "Pick a date",
    datetime.date(2019, 7, 6))




