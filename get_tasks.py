from datetime import datetime, timedelta
import json
import requests
from time import sleep
from db_methods import *
from misc import *


def getTaskType(task: dict) -> tuple:
    try:
        return [type_symbol_dict[task['einsatzart'].capitalize()], task['einsatzart'].capitalize()]
    except KeyError:
        for key, value in type_symbol_dict.items():
            if key.lower() in task['einsatztyp']['text'].lower():
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


def updateTasks(active_tasks: list, old_tasks: pd.DataFrame, debug: bool = False):
    active_ids = [d["id"] for d in active_tasks]
    for id_ in old_tasks['id'].values:
        if id_ not in active_ids and old_tasks[old_tasks['id'] == id_]['status'].values[0] != 'Abgeschlossen':
            if debug:
                print(f"Task {id_} is finished")
            dbm.dbUpdateOne({'id': id_}, {'status': 'Abgeschlossen'})


def postNewTasks(new_tasks: list, old_tasks: pd.DataFrame, dbm: classmethod, debug: bool = False):
    for task in new_tasks:
        if task['id'] not in old_tasks['id'].values:
            if debug:
                print(f"New Task: {task}")
            dbm.dbPost(task)


def runTaskPipeline(dbm: classmethod, api_url: str, debug: bool = False):
    new_tasks = getNewTasks(api_url)
    old_tasks = dbm.dbGetAll()
    postNewTasks(new_tasks, old_tasks, dbm, debug)
    updateTasks(new_tasks, old_tasks, debug)


if __name__ == '__main__':
    DEBUG = True
    f = open("credentials.json", 'r')
    data_json = json.load(f)
    f.close()
    db_url = data_json['mongo_db']['url']
    api_url = data_json['fire_dep']['url']
    dbm = DbMethods(db_url)
    while True:
        runTaskPipeline(dbm, api_url, DEBUG)
        sleep(60)