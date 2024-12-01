from pymongo.mongo_client import MongoClient
import json
import streamlit as st
import folium
from streamlit_folium import folium_static
from folium.plugins import FastMarkerCluster
import pandas as pd
import pytz
from datetime import datetime, timedelta
import plotly.express as px
from db_methods import *
from misc import *


def taskMapPlot(data: pd.DataFrame):
    m = folium.Map(location=[data['lat'].mean(), data['lon'].mean()], zoom_start=9, width='100%')
    for idx, row in data.iterrows():
        folium.Marker([ row['lat'], row['lon']], 
                        popup=f"{row['info'].split(' | ')[1]}\n",
                        #icon=folium.Icon(color=colors[row['type']])).add_to(m)
                        icon=folium.Icon(icon=type_icons[row['type']], color=type_colors[row['type']])
                    ).add_to(m)
    folium_static(m, width=None)




def activeTaskTable(activeData: pd.DataFrame):
    activeData = activeData.copy()
    activeData['sub_info'] = activeData['info'].apply(lambda x: x.split(' | ')[1])
    activeData['date'] = activeData['date'].apply(lambda x: x.strftime("%d.%m.%Y %H:%M"))
    activeData['cnt_fire_dep'] = activeData['cnt_fire_dep'].apply(lambda x: str(x) + ' 🚒')
    activeData = activeData[['symbol_type', 'date', 'sub_info', 'cnt_fire_dep', 'city', 'district_long']].copy()
    activeData.rename(columns={
        'symbol_type': 'Einsatzart',
        'date': 'Datum', 
        'sub_info': 'Info',
        'cnt_fire_dep': 'im Einsatz',
        'city': 'Ortschaft',
        'district_long': 'Bezirk'
    }, inplace=True)
    
    st.dataframe(
        activeData,
        hide_index=True,
        column_config={
            "Einsatzart": st.column_config.Column(width="small"),
            "Datum": st.column_config.Column(width="medium"),
            "Info": st.column_config.Column(width="large"),
            "im Einsatz": st.column_config.Column(width="medium"),
            "Ortschaft": st.column_config.Column(width="large"), 
            "Bezirk": st.column_config.Column(width="medium")
        }
    )