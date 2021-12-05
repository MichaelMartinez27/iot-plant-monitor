"""
Project: IoT Plant Monitor
Module:  Stores data from sensors into local db
Author:  Michael Martinez
Course:  ELEC 3520

"""
import os
import sqlite3 as db
from multiprocessing import Queue
from data_retriever import DataRetriever
from threading import Thread


ELEMENTS = ["HUMID","TEMP","SOIL","LIGHT"]


class StorageDB:
    conn:   db.Connection
    cursor: db.Cursor

    def __enter__(self):
        self.conn = None
        self.cursor = None

    def __init__(self, db_file) -> None:
        try:
            self.conn = db.connect(db_file, check_same_thread=False)
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
        _, _, plant = msg.topic.split("/")
        dt, sensor, datatype, value = msg.payload.decode('utf-8').split(",")
        try:
            sql = f"""
INSERT INTO Sensor_data(dt, plant_id, sensor_id, type, value)
VALUES (
    '{dt}',
    '{plant}',
    '{sensor}',
    '{datatype}',
    '{value}'
);
"""
            print(sql)
            self.cursor.execute(sql)
            self.conn.commit()
        except db.Error as err:
            print(f"ERROR|{'save_msg':^15}|", err)

    def get_sensor_data(self, element:str="all"):
        if element.lower() == "all":
            sql = "SELECT * FROM Sensor_data;"
        elif element in ELEMENTS:
            sql = f"""SELECT * 
                    FROM Sensor_data
                    WHERE type='{element}'"""
        else:
            return []
        print(sql)
        try:
            self.cursor.execute(sql)
            data = self.cursor.fetchall()
            print("DAT|", data)
            return data
        except db.Error as err:
            print(f"ERR|", err)
            return []




class StorageInterface(Thread):
    retriever: DataRetriever
    store: StorageDB
    queue: Queue

    def __init__(self) -> None:
        super().__init__()
        print("LOG| Initializing database storage")
        self.retriever = DataRetriever(
            os.environ.get("BROKER_HOST","localhost"),
            int(os.environ.get("BROKER_PORT",1883)))
        self.retriever.setup()
        self.store = StorageDB(
            os.environ.get("DB_LOCATION",
            "./local-db/data/Sensors.db"))
        print("LOG| Initialized database storage")

    def on_message(self,client, userdata, msg):
        print(f"Message received. Topic: {msg.topic}. Payload: {msg.payload.decode('utf-8')}")
        self.store.save_msg(msg)

    def run(self):
        print("LOG| Running Database Interface")
        self.store.build_schema(os.environ.get("DB_SCHEMA","./local-db/schema.sql"))
        self.retriever.client.on_message = self.on_message
        self.retriever.run()


if __name__ == '__main__':
    si = StorageInterface()
    si.run()