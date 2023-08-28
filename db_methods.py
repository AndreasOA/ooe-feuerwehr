from pymongo.mongo_client import MongoClient
import json
import pandas as pd
from db_template import db_template


class DbMethods:
    def __init__(self, url):
        self.client = MongoClient(url, sl_cert_reqs=ssl.CERT_NONE)
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


    def dbDeleteOne(self, dbFilter: dict):
        return self.collection.delete_one(dbFilter)


if __name__ == '__main__':
    f = open("credentials.json", 'r')
    data_json = json.load(f)
    f.close()
    url = data_json['mongo_db']['url']
    dbm = DbMethods(url)