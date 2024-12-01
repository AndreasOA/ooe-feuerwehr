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
from dotenv import load_dotenv
import os

load_dotenv()
# Set page to wide mode
st.set_page_config(
    layout="wide",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)

dbm = DbMethods()

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

@st.cache_data(ttl=600)
def load_data():
    return dbm.dbGetAll()

data = load_data()
data['district_long'] = data['district'].apply(lambda x: apply_district_abr_full(x))
data["lon"] = pd.to_numeric(data["lon"])
data["lat"] = pd.to_numeric(data["lat"])
res = []
for i, elem in data.iterrows():
    res.append(pd.to_datetime(elem['date']))
data['date'] = res
data['date'] = data['date'].apply(lambda x: x.tz_localize('UTC') if x.tzinfo is None else x.tz_convert('UTC'))
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
    "GitHub ": "https://github.com/AndreasOA"
}

for social, link in socials.items():
    st.sidebar.markdown(f"[{social}]({link})")
####################################################################################################
# Content
st.divider()
st.subheader("Statistik:")
col1, col2, col3 = st.columns(3)
current_time = datetime.now(pytz.FixedOffset(120))
time_24_hours_ago = current_time - timedelta(days=1)
# Now you can safely compare because both are offset-naive
data_24_hours = data[((data['date'] >= time_24_hours_ago) & (data['date'] <= current_time))]
activeData = data[data['status'] == 'Aktiv'].sort_values('date', ascending=False)
try:
    most_common_task_type = data_24_hours['type'].value_counts().idxmax()
except ValueError:
    most_common_task_type = "Keine Daten"
col1.metric("Laufende Einsätze", len(data[data['status'] == 'Aktiv']))
col2.metric("Einsätze in den letzten 24 Stunden", len(data_24_hours))
col3.metric("Häufigste Einsatzart", most_common_task_type)
st.divider()
st.title("Aktive Einsätze")
if len(activeData) == 0:
    st.warning("Keine aktiven Einsätze")
else:
    activeTaskTable(activeData)
    taskMapPlot(activeData)
st.divider()
st.title("Alle Einsätze der letzten 24 Stunden")
activeTaskTable(data_24_hours.sort_values('date', ascending=False))
st.divider()