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
## Predictions of weekly 911 call volumes for Baltimore City
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

dBalt, baltimore_map = load_data()

districts = dBalt.Police_district_x.unique()

def plot_baltimore(dIn):   
    fig = px.choropleth(dIn, geojson=baltimore_map, 
                        locations='Census_Tracts', featureidkey="properties.NAME",
                        color='Count',
                        color_continuous_scale="Viridis", 
                        range_color = [0,250], title = 'Weekly Distribution of 911 calls in Baltimore'
                        # cmax =400
                        )
    fig.update_geos(fitbounds="locations", visible=False)
    # fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    return(fig)

url_count = "https://github.com/trisha-sen/Streamlit_test/raw/master/MedHighWeeklyCount.csv"

@st.cache(persist=True)
def District_counts(police_district):
    df = pd.read_csv(url_count)        
    df['Date'] = pd.to_datetime(df['Date'])

    Temp = df[(df['PoliceDistrict']==police_district)]
    dfSum = Temp.groupby(pd.Grouper(key='Date', freq='W'))['Count'].sum()
    dfWeekDistrict = pd.DataFrame(dfSum) 
    dfWeekDistrict['Date'] = dfSum.index
    dfWeekDistrict['PoliceDistrict'] = police_district
    dfWeekDistrict = dfWeekDistrict[1:]
    dfWeekDistrict = dfWeekDistrict[0:-2]
    return(dfWeekDistrict)

date = st.date_input(
    "Pick a week between 2013 and 2018",
    datetime.date(2018, 10, 5))

@st.cache(persist=True)
def Weekly_rate(year, week):
    df = pd.read_csv(url_count)        
    df['Date'] = pd.to_datetime(df['Date'])
    Temp = df[(df['Date'].dt.year==year) & 
              (df['Date'].dt.week==week)]
    return(Temp)

week = date.isocalendar()[1]
year = date.year

if (year < 2013) | (year>2018):
    '## That date is not in range'
else:     
    dfWeek = Weekly_rate(year,week)
    
    fig = plot_baltimore(dfWeek)
    st.plotly_chart(fig)
    
    displayTable = st.checkbox('Display Data Table')
    if displayTable:
        dfWeek

police_district = st.sidebar.radio(
    "Select a district to view weekly trend in 911 call volume", 
    districts)

dfWeekDistrict = District_counts(police_district)
fig, ax = plt.subplots()
ax.plot_date(dfWeekDistrict.Date, dfWeekDistrict.Count,
             color = ((0.86,0.078,0.24)),linestyle = '-', marker = '')
ax.set_ylim(0,)
ax.set_xlabel('Date', fontsize=14)
ax.set_ylabel('Medium/High Priority 911 calls', fontsize=14)
ax.set_title("Trend for " + str(police_district) + " police district" , fontsize=16)
st.pyplot(fig)






