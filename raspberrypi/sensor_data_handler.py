"""
Project: IoT Plant Monitor
Module:  Gets sensor data via bluetooth and sends
         to local MQTT
Author:  Michael Martinez
Course:  ELEC 3520

"""
import os
import re
from time import sleep, strftime
import asyncio
from bleak import BleakClient
from bleak.exc import BleakError
from struct import *
import paho.mqtt.client as mqtt


ADDRESS = "6d:65:61:d3:ca:be"
UUID_DESCRIPTORS = {
    "2a6f":"HUMID",
    "2a6e":"TEMP",
    "272a":"SOIL",
    "2730":"LIGHT"
}
PREVIOUS_DATA = {
    "2a6f":0,
    "2a6e":0,
    "272a":0,
    "2730":0
}


def send_sensor_data(topic:str, payload:str):
    print(f"{topic:>20}: {payload.replace(',', '|')}")
    # send to mqtt
    try:
        client = mqtt.Client(protocol=mqtt.MQTTv311)
        client.connect(host=os.environ.get("BROKER_HOST","localhost"),port=int(os.environ.get("BROKER_PORT",1883)))
        client.publish(topic=topic, payload=payload)
    except Exception as err:
        print("ERR|", err)



async def get_sensor_data(ADDRESS:str):
    async with BleakClient(ADDRESS) as client:
        svcs = await client.get_services()
        print("LOG| Looking for device to connect to...")
        while True:
            for svc in svcs:
                svc_uuid = svc.uuid.split('-')[0][4:]
                if re.match("[a-fA-F]00[\d]", svc_uuid):
                    for char in svc.characteristics:
                        time = strftime('%Y%m%d%H%M')
                        char_uuid = char.uuid[4:8]
                        char_description = UUID_DESCRIPTORS[char_uuid]
                        data = await client.read_gatt_char(char.handle)
                        char_data = unpack('f',data)[0]
                        if data != PREVIOUS_DATA[char_uuid]:
                            send_sensor_data(
                                f"sensors/plant/P01",
                                f"{time},{char_uuid},{char_description:<5},{char_data:.2f}"
                            )
                            PREVIOUS_DATA[char_uuid] = data
            sleep(1)


def main():
    try:
        asyncio.run(get_sensor_data(ADDRESS))
    except KeyboardInterrupt:
        print("LOG| ending sensor data retrieval.")
    except BleakError as err:
        print("ERR|", err)
    except asyncio.exceptions.InvalidStateError as err:
        print("ERR|", err)
    except asyncio.exceptions.TimeoutError as err:
        print("ERR|", err)


if __name__ == "__main__":
    main()
