#! /usr/bin/python
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
from signal import signal, SIGINT
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
COLLECTION_INTERVAL = 600
disconnected_event = asyncio.Event()


def handler(signal_recieved, frame):
    print()
    print("LOG| SIGNINT or CTRL-C  detected")
    print("LOG| Exiting gracefully")
    disconnected_event.set()
    exit(0)


def publish_sensor_data(topic:str, payload:str):
    print(f"LOG| publishing {topic:>20}: {payload.replace(',', '|')}")
    # send to mqtt
    try:
        client = mqtt.Client(protocol=mqtt.MQTTv311)
        client.connect(host=os.environ.get("BROKER_HOST","localhost"),port=int(os.environ.get("BROKER_PORT",1883)))
        client.publish(topic=topic, payload=payload.replace(" ",""))
    except Exception as err:
        print("ERR|", err)


def characteristic_callback(char, data:bytearray):
    global PREVIOUS_DATA
    time = strftime('%Y%m%d%H%M')
    char_uuid = char.uuid[4:8]
    svc_uuid = char.service_uuid.split('-')[0][4:]
    char_description = UUID_DESCRIPTORS[char_uuid]
    char_data = unpack('f',data)[0]
    if data != PREVIOUS_DATA[char_uuid]:
        publish_sensor_data(
            f"sensors/plant/{svc_uuid}",
            f"{time},{char_uuid},{char_description:<5},{char_data:.2f}"
        )
        PREVIOUS_DATA[char_uuid] = data


async def get_sensor_data(ADDRESS:str):
    signal(SIGINT, handler)

    def disconnect_callback(client:BleakClient):
        print("LOG| Running disconnect callback")
        client.stop_notify()
        client.disconnect()
        disconnected_event.set()


    async with BleakClient(ADDRESS, disconnect_callback=disconnect_callback) as client:
        svcs = await client.get_services()
        for svc in svcs:
            svc_uuid = svc.uuid.split('-')[0][4:]
            if re.match("[a-fA-F]00[\d]", svc_uuid):
                for char in svc.characteristics:
                    characteristic_callback(char, await client.read_gatt_char(char.uuid))



def main():
    prev_err = ""
    while True:
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(get_sensor_data(ADDRESS))
            sleep(COLLECTION_INTERVAL)
        except KeyboardInterrupt:
            print("LOG| ending sensor data retrieval.")
            break
        except EOFError as err:
            if err == prev_err:
                print(".")
            else:
                prev_err = err
                print("ERR|", err)
        except OSError as err:
            if err == prev_err:
                print(".")
            else:
                prev_err = err
                print("ERR|", err)
        except BleakError as err:
            if err == prev_err:
                print(".")
            else:
                prev_err = err
                print(f"ERR|{strftime('%Y%m%d%H%M')}|", err)
        except asyncio.exceptions.InvalidStateError as err:
            print("ERR|", err)
            break
        except asyncio.exceptions.TimeoutError as err:
            print("ERR|", err)
            break



if __name__ == "__main__":
    main()
