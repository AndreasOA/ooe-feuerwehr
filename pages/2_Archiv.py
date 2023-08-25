from pymongo.mongo_client import MongoClient
import json
import streamlit as st
import folium
from streamlit_folium import folium_static
from folium.plugins import FastMarkerCluster
import pandas as pd
import pytz
from datetime import datetime, timedelta, date
import plotly.express as px
from db_methods import *
from misc import *
from st_plots import *


# Sidebar
st.sidebar.header("Filter")
st.sidebar.subheader("Datumsbereich")
min_date = date.today() - timedelta(days=1)
max_date = date.today()
min_date = st.sidebar.date_input('Start Datum', min_date)
max_date = st.sidebar.date_input('End Datum', max_date)
min_date = datetime.combine(min_date, datetime.min.time())
max_date = datetime.combine(max_date, datetime.max.time())
timezone = pytz.FixedOffset(120)
min_date = min_date.replace(tzinfo=timezone)
max_date = max_date.replace(tzinfo=timezone)
task_types = st.sidebar.multiselect('Einsatzart', list(type_colors.keys()), default='Brand')
districts = st.sidebar.multiselect('Bezirk', ['N/A'] + list(district_abr_full.keys()), default=['N/A'] + list(district_abr_full.keys()))
# Filter Data
data_filter = st.session_state.dataframe.copy()
data_filter = data_filter[(data_filter['date'] >= min_date) & (data_filter['date'] <= max_date)]
data_filter = data_filter[data_filter['type'].isin(task_types)]
if 'N/A' in districts:
    districts.remove('N/A')
    districts.append('')
data_filter = data_filter[data_filter['district'].isin(districts)]
st.title("OÖ Feuerwehr Einsatz Tracker")
st.subheader("Einsatz Archiv")
if len(data_filter) == 0:
    st.warning("Keine Daten gefunden")
else:

    # 1. Map Plot
    taskMapPlot(data_filter)
    st.divider()
    # 2. Pie Plot
    st.subheader("Verteilung der Einsatzarten")
    pie_data = data_filter['type'].value_counts().reset_index()
    pie_data.columns = ['type', 'count']
    fig_pie = px.pie(pie_data, values='count', names='type')
    st.plotly_chart(fig_pie)
    st.divider()
    # 2. Pie Plot
    st.subheader("Zeitverteilung der Einsätze")
    # Extract the hour from the 'date' column
    data_filter['date_hour'] = data_filter['date'].dt.floor('H')

    # Group by 'date_hour' and count occurrences
    timeline_data = data_filter.groupby('date_hour').size().reset_index(name='count')

    # Create a complete range of hours between the minimum and maximum dates
    all_hours = pd.date_range(start=timeline_data['date_hour'].min(), 
                            end=timeline_data['date_hour'].max(), 
                            freq='H').to_frame(name='date_hour')

    # Merge the complete range with the timeline_data
    timeline_data = pd.merge(all_hours, timeline_data, on='date_hour', how='left')

    # Fill NaN values with 0
    timeline_data['count'].fillna(0, inplace=True)

    # Convert the count column to integer type
    timeline_data['count'] = timeline_data['count'].astype(int)

    # Plot using Plotly
    fig_timeline = px.line(timeline_data, x='date_hour', y='count', labels={'date_hour': 'Datum', 'count': 'Anzahl Einsätze'})
    st.plotly_chart(fig_timeline)
    # 3. Table with current tasks
    st.divider()
    st.subheader("Einsatz Tabelle")
    activeTaskTable(data_filter)
    
