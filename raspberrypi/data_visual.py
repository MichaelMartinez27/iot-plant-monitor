import socket
import os
import sqlite3 as db
from flask import Flask, render_template
from data_storage import StorageInterface
from threading import Thread
import pandas as pd
import json
import plotly
import plotly.express as px

class DataVisualizer(Thread):
    si: StorageInterface
    app: Flask

    def __init__(self, si):
        super().__init__()
        self.si = si
        self.app = self.create_app()

    def create_app(self):
        app = Flask(__name__)

        @app.route("/")
        def plot_all_data():
            conn = self.si.store.conn
            data = pd.read_sql_query("SELECT * FROM Sensor_data", conn)
            data['value']= pd.to_numeric(data['value'])
            data['dt']= pd.to_datetime(data['dt'])
            fig = px.line(data,x="dt",y="value",color="type")
            graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
            return render_template('all_plots.html', sensor="All sensors", graphJSON=graphJSON)

        @app.route("/humidity")
        def plot_humidity():
            conn = self.si.store.conn
            data = pd.read_sql_query("SELECT * FROM Sensor_data WHERE type='HUMID'", conn)
            fig = px.line(data,x="dt",y="value")
            graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
            return render_template('all_plots.html', sensor="Humidity", graphJSON=graphJSON)

        @app.route("/temp")
        def plot_temp():
            conn = self.si.store.conn
            data = pd.read_sql_query("SELECT * FROM Sensor_data WHERE type='TEMP '", conn)
            fig = px.line(data,x="dt",y="value")
            graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
            return render_template('all_plots.html', sensor="Temperature", graphJSON=graphJSON)

        @app.route("/soil")
        def plot_soil():
            conn = self.si.store.conn
            data = pd.read_sql_query("SELECT * FROM Sensor_data WHERE type='SOIL '", conn)
            fig = px.line(data,x="dt",y="value")
            graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
            return render_template('all_plots.html', sensor="Soil moisture", graphJSON=graphJSON)

        @app.route("/light")
        def plot_light():
            conn = self.si.store.conn
            data = pd.read_sql_query("SELECT * FROM Sensor_data WHERE type='LIGHT'", conn)
            fig = px.line(data,x="dt",y="value")
            graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
            return render_template('all_plots.html', sensor="Light intesity", graphJSON=graphJSON)

        @app.route('/plotly')
        def notdash():
            df = pd.DataFrame({
                'Fruit': ['Apples', 'Oranges', 'Bananas', 'Apples', 'Oranges', 
                'Bananas'],
                'Amount': [4, 1, 2, 2, 4, 5],
                'City': ['SF', 'SF', 'SF', 'Montreal', 'Montreal', 'Montreal']
            })
            fig = px.bar(df, x='Fruit', y='Amount', color='City', 
            barmode='group')   
            graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
            return render_template('all_plots.html', graphJSON=graphJSON)

        return app
    
    def run(self):
        self.app.run(host="0.0.0.0",debug=True)


if __name__ == "__main__":
    try:
        si = StorageInterface()
        si.start()
        dv = DataVisualizer(si)
        dv.run()
    except Exception as err:
        print("ERR|", err)
