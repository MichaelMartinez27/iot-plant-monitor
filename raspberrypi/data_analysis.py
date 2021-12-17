"""
Project: IoT Plant Monitor
Module:  Takes data and analyzes it for anomolies
Author:  Michael Martinez
Course:  ELEC 3520

"""
import os
from data_retriever import DataRetriever
import pandas as pd
import requests
from results_handler import send_result
from pycaret.anomaly import *
from sklearn.ensemble import IsolationForest


class PlantSensorData:
    _humidity:    float
    _temperature: float
    _soil:        float
    _light:       float

    def __init__(self,
            humidity:float=None,
            temperature:float=None,
            soil:float=None,
            light:float=None
        ) -> None:
        self._humidity = humidity
        self._temperature = temperature
        self._soil = soil
        self._light = light

    @property
    def humidity(self):
        return self._humidity

    @humidity.setter
    def humidity(self, humidity:float):
        self._humidity = humidity

    @property
    def temperature(self):
        return self._temperature

    @temperature.setter
    def temperature(self,temperature:float):
        self._temperature = temperature

    @property
    def soil(self):
        return self._soil

    @soil.setter
    def soil(self, soil:float):
        self._soil

    @property
    def light(self):
        return self._light

    @light.setter
    def light(self, light:float):
        self._light = light

    def as_df(self):
        return pd.DataFrame(self.__dict__())

    def __repr__(self):
        return f"""{
"humidity":    {self._humidity},
"temperature": {self._temperature},
"soil":        {self._soil},
"light":       {self._light}
}"""

    def __dict__(self):
        return dict(self.__repr__())

    def data_available(self):
        return {
            "humidity":    self._humidity is not None,
            "temperature": self._temperature is not None,
            "soil":        self._soil is not None,
            "light":       self._light is not None
        }


class DataAnalysis:
    _current_data:   PlantSensorData
    _current_result: float

    def __init__(self) -> None:
        self._current_data = PlantSensorData()
        self._current_result = None
        rng = np.random.RandomState(42)
        self.__model = IsolationForest(random_state=rng)
        self.__model.fit(self.get_training_data())

    @property
    def result(self) -> float:
        if not all(self.current_data.data_available().values()):
            raise ValueError("Not enough data to analyze")
        if self.result is None:
            return self.analyze_data()
        return self._current_result

    def get_training_data(self):
        response = requests.get("py-storage:5000/json")
        data = dict(response.text)
        if "ERR" not in data.keys():
            return pd.DataFrame(data).to_numpy()
        else:
            raise ValueError

    def parse_message(self, msg) -> None:
        """
        updates data based on message. If current data has all
        attributes filled, will analyze data
        """
        message = msg.split(",")
        type = msg[-2]
        value =msg[-1]
        if type == "HUMID":
            self._current_data.humidity = value
        elif type == "TEMP":
            self._current_data.temperature = value
        elif type == "SOIL":
            self._current_data.soil = value
        elif type == "LIGHT":
            self._current_data.light = value

    def analyze_data(self) -> float:
        if all(self._current_data.data_available().values()):
            self.__model.predict(self._current_data.as_df())


class DataAnalysisInterface:
    retriever: DataRetriever
    analyst: DataAnalysis

    def __init__(self) -> None:
        self.retriever = DataRetriever(os.environ.get("BROKER_HOST","localhost"),int(os.environ.get("BROKER_PORT",1883)))
        self.retriever.setup()
        self.analyst = DataAnalysis()


    def on_message(self,client, userdata, msg) -> None:
        print(f"LOG| Message received. Topic: {msg.topic}. Payload: {msg.payload.decode('utf-8')}")
        self.analyst.parse_message(msg)
        try:
            self.analyst.analyze_data()
            send_result()
            print("LOG| Data analyzed and sent to MQTT")
        except ValueError as ve:
            print("LOG|", ve)
        except Exception as err:
            print("ERR|", err)

    def send_data(self):
        print(f"ANOMOLY| {self.analyst._current_data} -> {bool(self.analyst.result)}")

    def run(self) -> None:
        self.retriever.client.on_message = self.on_message
        self.retriever.run()



if __name__ == '__main__':
    dai = DataAnalysisInterface()
    dai.run()
