from datetime import datetime, timedelta
import json
import requests
from time import sleep
import pandas as pd
from pymongo.mongo_client import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

API_URL = os.getenv('FIRE_DEP_URL')
T_API = os.getenv('TELEGRAM_API_TOKEN')
T_ID = os.getenv('TELEGRAM_GROUP_ID')
T_URL = f"https://api.telegram.org/bot{T_API}/sendMessage?chat_id={T_ID}&text="
DEBUG = True


def db_template(
    id: str,
    status: str,
    symbol_type: str,
    type: str,
    date: str,
    info: str,
    lon: float,
    lat: float,
    city: str,
    district: str,
    street: str,
    cnt_fire_dep: int
):
    return {"id":id,
            "status":status,
            "symbol_type":symbol_type,
            "type":type,
            "date":date,
            "info":info,
            "lon":lon,
            "lat":lat,
            "city":city,
            "district":district,
            "street":street,
            "cnt_fire_dep": cnt_fire_dep
    }

type_symbol_dict = {'Brandmeldealarm': '🚨',
                    'Brand': '🔥', 
                    'Person': '👷', 
                    'Unwetter': '☁', 
                    'Verkehrsunfall': '🚗', 
                    'Fahrzeugbergung': '🚙',
                    'Öl': '🛢️',
                    'Andere': '❗'}

symbol_type_dict = dict((v,k) for k,v in type_symbol_dict.items())
type_colors = {
    'Brand': 'darkred',
    'Person': 'blue',
    'Unwetter': 'green',
    'Verkehrsunfall': 'orange',
    'Fahrzeugbergung': 'beige',
    'Brandmeldealarm': 'purple',
    'Öl': 'lightblue',
    'Andere': 'gray'
}
type_icons = {
    'Brandmeldealarm': 'fire',
    'Brand': 'fire',
    'Person': 'user',
    'Unwetter': 'cloud',
    'Verkehrsunfall': 'dashboard',
    'Fahrzeugbergung': 'car',
    'Öl': 'oil drum',
    'Andere': 'alert'
}

district_abr_full = {
    "BR": "Braunau am Inn",
    "EF": "Eferding",
    "FR": "Freistadt",
    "GM": "Gmunden",
    "GR": "Grieskirchen",
    "KI": "Kirchdorf an der Krems",
    "L": "Linz",
    "LL": "Linz-Land",
    "PE": "Perg",
    "RI": "Ried im Innkreis",
    "RO": "Rohrbach im Mühlkreis",
    "SD": "Schärding",
    "SE": "Steyr-Land",
    "SR": "Steyr",
    "UU": "Urfahr-Umgebung",
    "VB": "Vöcklabruck",
    "WE": "Wels",
    "WL": "Wels-Land"
}
district_full_abr = dict((v,k) for k,v in district_abr_full.items())

def _notifyUser(url, msg):
        requests.get(url+msg).json()

class DbMethods:
    def __init__(self, url):
        self.client = MongoClient(url)
        self.db = self.client['einsatztracker']
        self.collection = self.db['einsaetze']
    

    def dbPost(self, data: dict):
        self.collection.insert_one(db_template(**data))


    def dbGetAll(self) -> pd.DataFrame:
        return pd.DataFrame(list(self.collection.find({})))
    

    def dbGetOne(self, dbFilter: dict) -> dict:
        return self.collection.find_one(dbFilter)
    

    def dbUpdateOne(self, dbFilter: dict, newContent: dict):
        return self.collection.update_one(dbFilter, {"$set": newContent})


def getTaskType(task: dict) -> tuple:
    try:
        if "Brandmeldealarm" in task['einsatztyp']['text'].lower():
                return '🚨', 'Brandmeldealarm'
        elif "Brandmeldealarm" in task['einsatzsubtyp']['text'].lower():
            return '🚨', 'Brandmeldealarm'
        else:
            return [type_symbol_dict[task['einsatzart'].capitalize()], task['einsatzart'].capitalize()]
    except KeyError:
        for key, value in type_symbol_dict.items():
            if "Brandmeldealarm" in task['einsatztyp']['text'].lower():
                return '🚨', 'Brandmeldealarm'
            elif key.lower() in task['einsatztyp']['text'].lower():
                return value, key
            elif key.lower() in task['einsatzsubtyp']['text'].lower():
                return value, key
        return '❗', 'Andere'


def getNewTasks(url: str, debug: bool = False):
    response = requests.get(url)
    db_new_list = []
    if response.status_code != 200:
        print("API Error")
    resp_json = json.loads(response.content.decode('utf8').replace("'", '"')[9:-2])
    if "einsaetze" not in resp_json.keys():
        return []
    for _, task in resp_json['einsaetze'].items():
        data = {}
        task = task['einsatz']
        data['id'] = task['num1']
        data['status'] = 'Aktiv'
        type_symbol, type_text = getTaskType(task)
        data['symbol_type'] = type_symbol
        data['type'] = type_text
        data['date'] = datetime.strptime(task['startzeit'], '%a, %d %b %Y %H:%M:%S %z')
        data['info'] = f"{task['einsatztyp']['text'].capitalize()} | {task['einsatzsubtyp']['text'].capitalize()}"
        data['lon'] = task["wgs84"]["lng"]
        data['lat'] = task["wgs84"]["lat"]
        district, city = task['einsatzort'].split(' - ')
        data['city'] = city
        data['district'] = district
        try:
            street_list = task['adresse']['default'].split(' ')
            street_list[0] = street_list[0].capitalize()
            street_list[-2] = street_list[-2].capitalize()
            data['street'] = ' '.join(street_list)
        except:
            data['street'] = ''
        data['cnt_fire_dep'] = int(task['cntfeuerwehren'])
        db_new_list.append(data)

    return db_new_list


def updateTasks(active_tasks: list, old_tasks: pd.DataFrame, t_url: str, debug: bool = False):
    active_ids = [d["id"] for d in active_tasks]
    for id_ in old_tasks['id'].values:
        if id_ not in active_ids and old_tasks[old_tasks['id'] == id_]['status'].values[0] != 'Abgeschlossen':
            if debug:
                print(f"Task {id_} is finished")
            dbm.dbUpdateOne({'id': id_}, {'status': 'Abgeschlossen'})
            task = old_tasks[old_tasks['id'] == id_].to_dict('records')[0]
            msg = f"ABGESCHLOSSEN: {task['symbol_type']} {task['info'].split(' | ')[1]} in {task['city']} ({task['district']})\n({task['id']})"
            _notifyUser(t_url, msg)


def postNewTasks(new_tasks: list, old_tasks: pd.DataFrame, dbm: classmethod, t_url: str, debug: bool = False):
    for task in new_tasks:
        if task['id'] not in old_tasks['id'].values:
            if debug:
                print(f"New Task: {task}")
            maps_tag = f'https://maps.google.com/?q={task["lat"]},{task["lon"]}'
            city = "--" if len(task['city']) else task['city']
            msg =   f"{task['symbol_type']} {task['info'].split(' | ')[1]} in {city} ({task['district']})" + \
                    f"\nEinsatzart: {task['type']}\nEinsatz ID:{task['id']}\nFeuerwehren im Einsatz:{task['cnt_fire_dep']}\n{maps_tag}"
            _notifyUser(t_url, msg)
            dbm.dbPost(task)


def runTaskPipeline(dbm: classmethod, debug: bool = False):
    new_tasks = getNewTasks(API_URL)
    old_tasks = dbm.dbGetAll()
    postNewTasks(new_tasks, old_tasks, dbm, T_URL, debug)
    updateTasks(new_tasks, old_tasks, T_URL, debug)



if __name__ == '__main__':
    dbm = DbMethods()
    runTaskPipeline(dbm, DEBUG)