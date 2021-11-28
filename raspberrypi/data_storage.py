"""
Project: IoT Plant Monitor
Module:  Stores data from sensors into local db
Author:  Michael Martinez
Course:  ELEC 3520

"""
import os
import sqlite3 as db
from multiprocessing import Process, Queue
from data_retriever import DataRetriever


class StorageDB:
    conn:   db.Connection
    cursor: db.Cursor

    def __enter__(self):
        self.conn = None
        self.cursor = None

    def __init__(self, db_file) -> None:
        try:
            self.conn = db.connect(db_file)
            self.cursor = self.conn.cursor()
            print(db.version)
        except db.Error as err:
            print(f"ERROR|{'__init__':^15}|", err)

    def __exit__(self):
        if self.conn:
            self.conn.close()
        if self.cursor:
            self.cursor.close()

    def build_schema(self,schema_file:str=None,schema_str:str=""):
        try:
            if schema_file:
                with open(schema_file,"r",encoding='utf-8') as file:
                    schema_str = file.read()
            self.cursor.executescript(schema_str)
        except db.Error as err:
            print(f"ERROR|{'build_schema':^15}|", err)

    def save_msg(self, msg):
        _, measurement_type, sensor = msg.topic.split("/")
        plant, dt, value, unit = msg.payload.decode('utf-8').split("|")
        try:
            sql = f"""
INSERT INTO Sensor_data(dt, plant_id, sensor_id, type, value, unit)
VALUES (
    '{dt}',
    '{plant}',
    '{sensor}',
    '{measurement_type}',
    '{value}',
    '{unit}'
);
"""
            print(sql)
            self.cursor.execute(sql)
            self.conn.commit()
            self.get_sensor_data()
        except db.Error as err:
            print(f"ERROR|{'save_msg':^15}|", err)

    def get_sensor_data(self):
        try:
            sql = "SELECT * FROM Sensor_data"
            print(sql)
            self.cursor.execute(sql)
            for data in self.cursor.fetchall():
                print(data)
        except db.Error as err:
            print(f"ERROR|{'get_sensor_data':^15}|", err)



class StorageInterface:
    retriever: DataRetriever
    store: StorageDB
    queue: Queue

    def __init__(self) -> None:
        self.retriever = DataRetriever(os.environ.get("BROKER_HOST","localhost"),int(os.environ.get("BROKER_PORT",1883)))
        self.retriever.setup()
        self.store = StorageDB(os.environ.get("DB_LOCATION","./local-db/data/Sensors.db"))
        self.test = "it worked again!!"

    def check_for_data(self):
        while True:
            if not self.retriever.data_read:
                self.queue.put(self.retriever.get_data())
            if not self.queue.empty():
                self.store.save_msg(self.queue.pop())

    def on_message(self,client, userdata, msg):
        print(f"Message received. Topic: {msg.topic}. Payload: {msg.payload.decode('utf-8')}")
        self.store.save_msg(msg)

    def run(self):
        self.store.build_schema(os.environ.get("DB_SCHEMA","./local-db/schema.sql"))
        self.retriever.client.on_message = self.on_message
        self.retriever.run()


if __name__ == '__main__':
    si = StorageInterface()
    si.run()