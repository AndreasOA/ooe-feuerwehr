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


def taskMapPlot(data: pd.DataFrame, legend: bool = True):
    m = folium.Map(location=[data['lat'].mean(), data['lon'].mean()], zoom_start=9)
    for idx, row in data.iterrows():
        folium.Marker([ row['lat'], row['lon']], 
                        popup=f"{row['info'].split(' | ')[1]}\n",
                        #icon=folium.Icon(color=colors[row['type']])).add_to(m)
                        icon=folium.Icon(icon=type_icons[row['type']], color=type_colors[row['type']])
                    ).add_to(m)
    folium_static(m)
    if legend:
        st.subheader("Legende")
        legend_html = "<div style='display: flex; flex-wrap: wrap; justify-content: space-between;'>"
        count = 0
        for task_type, color in type_colors.items():
            legend_html += f"<div style='flex: 0 0 calc(50% - 10px); display: flex; align-items: center; margin-bottom: 5px;'>"
            legend_html += f"<span style='background-color: {color}; display: inline-block; height: 20px; width: 20px; margin-right: 5px;'></span>{task_type}"
            legend_html += "</div>"
            count += 1
            if count % 2 == 0:  # after every two items, add a separation
                legend_html += "<div style='flex-basis: 100%; height: 10px;'></div>"
        # Close the main container
        legend_html += "</div>"

        st.markdown(legend_html, unsafe_allow_html=True)



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
    html = activeData.to_html(index=False, classes='styled-table')
    # CSS styles for the HTML table: making header background grey
    html_style = """
    <style>
        .styled-table {
            font-size: 0.9em;  /* reduce text size */
            margin-bottom: 20px;  /* add margin at the bottom */
            width: 100%;  /* make table full-width */
        }
        .styled-table thead th {
            background-color: grey;
            opacity: 0.8;
            color: white;
            text-align: left;
        }
    </style>
    """

    # Display the styled HTML table in Streamlit
    st.write(html_style, unsafe_allow_html=True)
    st.write(html, unsafe_allow_html=True)