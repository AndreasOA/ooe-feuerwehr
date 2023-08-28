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
import requests

def get_external_ip():
    response = requests.get("https://api64.ipify.org?format=json")
    if response.status_code == 200:
        data = response.json()
        return data.get("ip")
    else:
        return "Unknown"

external_ip = get_external_ip()
st.write("External IP:", external_ip)

####################################################################################################
# Load Data
def apply_district_abr_full(x):
    try:
        return district_abr_full[x]
    except:
        return ''

def format_city(x):
    try:
        return city_to_city[keep_only_letters(x)]
    except:
        return '-'

def makeMapsLink(x):
    try:
        return f"https://maps.google.com/?q={x['lat']},{x['lon']}"
    except:
        return ''


url = st.secrets['mongo_db']['url']
dbm = DbMethods(url)
data = dbm.dbGetAll()
data['district_long'] = data['district'].apply(lambda x: apply_district_abr_full(x))
data['date'] = pd.to_datetime(data['date'])
data['map_url'] =  data.apply(lambda row: makeMapsLink(row), axis=1)
data['city'] = data['city'].apply(lambda x: format_city(x))
if 'dataframe' not in st.session_state:
    st.session_state.dataframe = data
####################################################################################################
# Page Layout
st.title("OÖ Feuerwehr Einsatz Tracker")
####################################################################################################
# Sidebar
st.sidebar.header("Live Benachrichtigungen")
telegram_link = "https://t.me/ooefeuerwehr"
st.sidebar.markdown(f"[Telegram Gruppe]({telegram_link})")

# Social Media Links
st.sidebar.header("Kontakt")
socials = {
    "Twitter": "https://twitter.com/heyandio",
    "GitHub ": "https://github.com/AndreasOA",
    "Website": "https://a-o.dev"
}

for social, link in socials.items():
    st.sidebar.markdown(f"[{social}]({link})")
####################################################################################################
# Content
st.divider()
st.subheader("Statistik der letzten 24 Stunden:")
col1, col2, col3 = st.columns([1,1,2])
current_time = datetime.now(pytz.FixedOffset(120))
time_24_hours_ago = current_time - timedelta(days=1)
data_24_hours = data[(data['date'] >= time_24_hours_ago) & (data['date'] <= current_time)]
activeData = data[data['status'] == 'Aktiv']

most_common_task_type = data_24_hours['type'].value_counts().idxmax()
col1.metric("Laufende Einsätze", len(data[data['status'] == 'Aktiv']))
col2.metric("Einsätze insgesamt", len(data_24_hours))
col3.metric("Häufigste Einsatzart", most_common_task_type)
st.divider()
st.title("Aktive Einsätze")
if len(activeData) == 0:
    st.warning("Keine aktiven Einsätze")
else:
    activeTaskTable(activeData)
    taskMapPlot(activeData, legend=False)
st.divider()
st.title("Alle Einsätze der letzten 24 Stunden")
activeTaskTable(data_24_hours)
st.divider()