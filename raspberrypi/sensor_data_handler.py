"""
Project: IoT Plant Monitor
Module:  Gets sensor data via bluetooth and sends
         to local MQTT
Author:  Michael Martinez
Course:  ELEC 3520

"""
from time import sleep
from typing import Counter
import paho.mqtt.client as mqtt


topic = "sensors/sensor/S01"


if __name__ == "__main__":
    client = mqtt.Client(protocol=mqtt.MQTTv311)
    client.connect(host="localhost", port=1883)
    Counter = 40
    while True:
        client.publish(topic=topic, payload=f"P001|{Counter}|100|ft")
        sleep(10)
        Counter += 2

