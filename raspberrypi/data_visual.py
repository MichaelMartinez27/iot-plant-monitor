from flask import Flask, render_template
from data_storage import StorageInterface
from threading import Thread
import pandas as pd
import json
import plotly
import plotly.express as px
import sys

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
            try:
                conn = self.si.store.conn
                data = pd.read_sql_query("SELECT * FROM Sensor_data", conn)
                data['value']= pd.to_numeric(data['value'])
                data['dt']= pd.to_datetime(data['dt'])
                data.dropna(axis="index",how="any",inplace=True)
                fig = px.line(data,x="dt",y="value",color="type")
                graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
                return render_template('all_plots.html', sensor="All sensors", graphJSON=graphJSON)
            except Exception as err:
                print("DBG|", err, file=sys.stdout)
                print("ERR|", err, file=sys.stderr)
                return {"ERR":"Could not recieve data. See logs for more info."}

        @app.route("/json")
        def get_all_data():
            try:
                conn = self.si.store.conn
                data = pd.read_sql_query("SELECT * FROM Sensor_data", conn)
                data['value']= pd.to_numeric(data['value'])
                data.dropna(axis="index",how="any",inplace=True)
                return data.to_dict()
            except Exception as err:
                print("DBG|", err, file=sys.stdout)
                print("ERR|", err, file=sys.stderr)
                return {"ERR":"Could not recieve data. See logs for more info."}

        @app.route("/humidity")
        def plot_humidity():
            try:
                conn = self.si.store.conn
                data = pd.read_sql_query("SELECT * FROM Sensor_data WHERE type='HUMID'", conn)
                data['value']= pd.to_numeric(data['value'])
                data['dt']= pd.to_datetime(data['dt'])
                data.dropna(axis="index",how="any",inplace=True)
                fig = px.line(data,x="dt",y="value")
                graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
                return render_template('all_plots.html', sensor="Humidity", graphJSON=graphJSON)
            except Exception as err:
                print("DBG|", err, file=sys.stdout)
                print("ERR|", err, file=sys.stderr)
                return {"ERR":"Could not recieve data. See logs for more info."}

        @app.route("/temp")
        def plot_temp():
            try:
                conn = self.si.store.conn
                data = pd.read_sql_query("SELECT * FROM Sensor_data WHERE type='TEMP'", conn)
                data['value']= pd.to_numeric(data['value'])
                data['dt']= pd.to_datetime(data['dt'])
                data.dropna(axis="index",how="any",inplace=True)
                fig = px.line(data,x="dt",y="value")
                graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
                return render_template('all_plots.html', sensor="Temperature", graphJSON=graphJSON)
            except Exception as err:
                print("DBG|", err, file=sys.stdout)
                print("ERR|", err, file=sys.stderr)
                return {"ERR":"Could not recieve data. See logs for more info."}

        @app.route("/soil")
        def plot_soil():
            try:
                conn = self.si.store.conn
                data = pd.read_sql_query("SELECT * FROM Sensor_data WHERE type='SOIL'", conn)
                data['value']= pd.to_numeric(data['value'])
                data['dt']= pd.to_datetime(data['dt'])
                data.dropna(axis="index",how="any",inplace=True)
                fig = px.line(data,x="dt",y="value")
                graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
                return render_template('all_plots.html', sensor="Soil moisture", graphJSON=graphJSON)
            except Exception as err:
                print("DBG|", err, file=sys.stdout)
                print("ERR|", err, file=sys.stderr)
                return {"ERR":"Could not recieve data. See logs for more info."}

        @app.route("/light")
        def plot_light():
            try:
                conn = self.si.store.conn
                data = pd.read_sql_query("SELECT * FROM Sensor_data WHERE type='LIGHT'", conn)
                data['value']= pd.to_numeric(data['value'])
                data['dt']= pd.to_datetime(data['dt'])
                data.dropna(axis="index",how="any",inplace=True)
                fig = px.line(data,x="dt",y="value")
                graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
                return render_template('all_plots.html', sensor="Light intesity", graphJSON=graphJSON)
            except Exception as err:
                print("DBG|", err, file=sys.stdout)
                print("ERR|", err, file=sys.stderr)
                return {"ERR":"Could not recieve data. See logs for more info."}

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
