"""
Project: IoT Plant Monitor
Module:  Gets sensor data via bluetooth and sends
         to local MQTT
Author:  Michael Martinez
Course:  ELEC 3520

"""
import os
from time import sleep, strftime
import asyncio
from bleak import BleakClient
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
    print(f"{topic:>20}: {payload.replace(',','|')}")
    # send to mqtt
    try:
        client = mqtt.Client(protocol=mqtt.MQTTv311)
        client.connect(host=os.environ.get("BROKER_HOST","localhost"),port=int(os.environ.get("BROKER_PORT",1883)))
        # Counter = 40
        # while True:
        #     client.publish(topic=topic, payload=payload)
        #     sleep(10)
        #     Counter += 2
    except Exception as err:
        print("ERR|", err)



async def get_sensor_data(ADDRESS:str):
    async with BleakClient(ADDRESS) as client:
        svcs = await client.get_services()
        while True:
            try:
                for svc in svcs:
                    if svc.description == "Serial Port":
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
            except KeyboardInterrupt:
                break


def main():
    asyncio.run(get_sensor_data(ADDRESS))


if __name__ == "__main__":
    main()
