# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 19:22:07 2020

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
from shapely.geometry import Polygon
# from shapely.geometry.polygon import Polygon
from urllib.request import urlopen
import geojson
import datetime
from math import radians, cos, sin, asin, sqrt
import plotly.graph_objs as go

#%%
def distance_calculations(df1, df2):  
    lat1 = df1['latitude']
    lon1 = df1['longitude']
    lat2 = df2['latitude']
    lon2 = df2['longitude']
    
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 3956 # Radius of earth in kilometers. Use 6371 for km
    return c * r

dist = ['Central','Eastern','Northeastern', 'Northern', 'Northwestern', 
'Southeastern', 'Southern', 'Southwestern','Western']         
hours_month = [25.146,25.626,24.914,23.4368,24.4976,23.0048,24.622,24.1336,25.7448]
dHours = pd.DataFrame({'District': dist, 'hours_month': hours_month})
dHours['hours_month'] = dHours['hours_month'].astype(float)*4.28
dHours = dHours.set_index(['District'])

#%%
Officers = [94,98,83,85,76,95,109,78,91]
Districts = ['Western', 'Southwestern', 'Southern', 'Northwestern', 'Central',
       'Southeastern', 'Northeastern', 'Northern', 'Eastern']
Short = ['W','SW','S','NW','C','SE','NE','N','E']
d = {'District':Districts,
     'Officers':Officers,
     'short': Short}
dfOfficers = pd.DataFrame(data = d)

#%%
# base.legend(loc='upper left')
url_stations = 'https://github.com/trisha-sen/Streamlit_test/raw/master/Police_Stations.csv'
Stations = pd.read_csv(url_stations)
# ('C:/Users/tsen6/Desktop/Python/Analysis911/Police_Stations.csv').drop(columns=['Unnamed: 0'])
Stations = Stations.set_index('name')
# Stations = gpd.GeoDataFrame(
#     Stations, geometry=gpd.points_from_xy(Stations.longitude, Stations.latitude))

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
                        color_continuous_scale="RdYlGn_r", 
                        range_color = [0,800], 
                        # title = 'Geo-spatial distribution of 911 calls in Baltimore'
                        # cmax =400
                        )
    fig.update_geos(fitbounds="locations", visible=False)
    # fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    return(fig)

url_count = "https://github.com/trisha-sen/Streamlit_test/raw/master/MedHighWeeklyCount.csv"

#%%
# @st.cache(persist=True)
def District_counts(month, year):
    avg_CFS_hours = 1.3*48/60
    url_MonthlyDist = 'https://github.com/trisha-sen/Streamlit_test/raw/master/MonthlyDist.csv'
    df = pd.read_csv(url_MonthlyDist) #('MonthlyDist.csv')           
    df['Date'] = pd.to_datetime(df['Date'])
    dfMonthDistrict = df[(df['Date'].dt.year==year) &
                              (df['Date'].dt.month==month)]
    dfMonthDistrict = dfMonthDistrict.drop(columns=['Date']).\
                      sort_values(by=['Count'])    
    dfMonthDistrict['Workload'] = dfMonthDistrict['Count']*avg_CFS_hours
    dfMonthDistrict['%911 calls'] = dfMonthDistrict['Count']/dfMonthDistrict['Count'].sum()*100
    dfMonthDistrict = dfMonthDistrict.join(dfOfficers.set_index('District'), on='District')
    dfMonthDistrict['% Workforce'] = dfMonthDistrict['Officers']/dfMonthDistrict['Officers'].sum()*100

    return(dfMonthDistrict)

#%%
'''
## Predictions of monthly emergency workforce demand for Baltimore City.
Select a month and year to view analysis.
'''
year = st.selectbox('Year',[2020,2021])
if year == 2020:
    Months = pd.DataFrame(data = {'months':['June',
                                  'Jul','Aug','Sept','Oct','Nov','Dec'],
                                  'numer':np.arange(6,13)})
    
    month0 = st.selectbox('Month',Months['months'])
                         # range(7, 13))

    month = Months[Months.months
                   ==month0].reset_index(drop=True).numer[0]
else:
    Months = pd.DataFrame(data = {'months':['Jan','Feb'],
                                  'numer':np.arange(1,3)})
    
    month0 = st.selectbox('Month',Months['months'])
                         # range(7, 13))

    month = Months[Months.months
                   ==month0].reset_index(drop=True).numer[0]
    
#%% Geo-spatial Distribution
@st.cache(persist=True)
def Monthly_rate(year,month):
    url_monthlyPred = 'https://github.com/trisha-sen/Streamlit_test/raw/master/MonthlyPred.csv'
    df = pd.read_csv(url_monthlyPred) #('MonthlyPred.csv') #(url_count)        
    df['Date'] = pd.to_datetime(df['Date'])
    Temp = df[(df['Date'].dt.year==year) & 
              (df['Date'].dt.month==month)]
    return(Temp)

'''
To view high resolution predictions of 911 call volumes for Baltimore,
 hover over this map. Each zone represents a census tract.
'''
dfMonth = Monthly_rate(year,month)

fig = plot_baltimore(dfMonth)
st.plotly_chart(fig)
#%%
'Knowledge of predicted emergency call volumes has been used to estimate monthly workforce needs. Baltimore is organized into 9 districts. Following is an analysis of predicted needs and available workforce for',month0, str(year),'in each district.'
'A red bar indicates shortage, a green bar indicates excess.'

dfMonthDistrict = District_counts(month, year)
dfMonthDistrict = dfMonthDistrict.set_index('District')
dfMonthDistrict['Per Officer'] = dHours
dfMonthDistrict['Officers Needed'] = (dfMonthDistrict['Workload']
                                      /dfMonthDistrict['Per Officer'])/0.6
dfMonthDistrict = dfMonthDistrict.reset_index()

dfPlot = pd.DataFrame()
dfPlot['Gap'] = (dfMonthDistrict['Officers Needed']
                 -dfMonthDistrict['Officers']).astype(int)
dfPlot['District']=dfMonthDistrict['District']
dfPlot['short'] = dfMonthDistrict['short']
dfPlot = dfPlot.set_index('short')


#----------Plotting Bar Chart-------------------------------------
fig, ax = plt.subplots()
colors = tuple(np.where(dfPlot["Gap"]<0, 'g', 'r'))

dfPlot['Gap'].plot(kind='bar', color=colors,
                   figsize=(10,5))

# ax.set_xlabel('District', fontsize=20)
ax.set_ylabel('Shortage', fontsize=20)
ax.tick_params(axis='x', labelsize=18)
ax.tick_params(axis='y', labelsize=18)
# ax.set_title("Trend for " + str(police_district) + " police district" , fontsize=16)
st.pyplot(fig)
    
if dfPlot['Gap'].sum() < 0:
    'There is a predicted overall excess of', str(
        abs(int(dfPlot['Gap'].sum()))), 'emergency personnel in Baltimore for',month0, str(year) 
else:
    'There is a predicted overall deficit of', str(
        abs(int(dfPlot['Gap'].sum()))), 'emergency personnel in Baltimore for',month0, str(year)

dfPlot = dfPlot.set_index('District')   

#%%
'Select a deficient district to find recommendations for 2 closest locations to transfer excess workforce from'
Deficit = dfPlot[dfPlot['Gap']>0]
Excess = dfPlot[dfPlot['Gap']<0]
dist_list = st.selectbox("",Deficit.index)

dExcess = pd.DataFrame(columns = ['district','distance','excess'])
district, distance, gap = [], [], []
for location in Excess.index:
    Temp = pd.DataFrame()
    d1 = Stations.loc[dist_list]
    d2 = Stations.loc[location]    
    district.append(location)
    distance.append(round((distance_calculations(d1, d2)),1))
    gap.append(abs(Excess[Excess.index==location]['Gap'].values[0]))

dExcess['district']=district
dExcess['distance']=distance
dExcess['excess']=gap

req = abs(Deficit[Deficit.index == dist_list]['Gap'].values[0])
'Deficit in', dist_list, 'district for', month0, str(year),'is',str(req),'. Closest districts with atleast', str(max(int(0.25*req),3)), 'excess personnel are:'

dExcessUse = dExcess[dExcess['excess']>max(int(0.25*req),3)]
dExcessUse = dExcessUse.sort_values('distance').reset_index(drop=True)
for i in dExcessUse.index[:2]:
    data = dExcessUse.iloc[i]
    str(data['excess']), 'personnel', 'in' ,data['district'], 'district,', str(data['distance']), 'miles away' 

displayTable = st.checkbox('Display Data Table')
if displayTable:
    dExcess

# #%%
# url = 'https://github.com/trisha-sen/Streamlit_test/raw/master/DistrictBorders.json'
# DistrictBorders = gpd.read_file(url)

# HQLocations = DistrictBorders[10:].reset_index(drop=True)
# DistrictBorders = DistrictBorders[0:10].drop([2]).reset_index(drop=True)

# def split_name(df):
#     Name = df.Name.split()[0]
#     return Name

# DistrictBorders['Name']= DistrictBorders.apply(lambda x: split_name(x),axis=1)
# DistrictBorders = DistrictBorders.set_index('Name')

# Dist2 = DistrictBorders
# for i in range(0,9):
#     new = Polygon(Dist2.iloc[i].geometry)
#     Dist2.geometry[i] = new
    
# Dist2['Color'] =  'white'
# Dist2.loc['Central','Color'] = '#C62828'
# Dist2.loc['Eastern','Color'] = 'green'
    
# base = Dist2.plot(color = Dist2['Color'],edgecolor='black')
# HQLocations.plot(ax=base, marker='o', color='black', markersize=30)
# base.axis('off')