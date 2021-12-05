"""
Project: IoT Plant Monitor
Module:  gets data from pub/sub service
Author:  Michael Martinez
Course:  ELEC 3520

"""
import paho.mqtt.client as  mqtt

class DataRetriever:
    client: mqtt.Client
    host:         str
    port:         int
    current_data: str
    data_read:    bool

    def __init__(self,host,port,protocol=mqtt.MQTTv311):
        self.host = host
        self.port = port
        self.client = mqtt.Client(protocol=protocol)

    def setup(self, topic="sensors/plant/#", func=None):
        def on_connect(client, userdata, flags, rc):
            print("LOG| Result from connect: {}".format(
                    mqtt.connack_string(rc)))    
            client.subscribe(topic)

        def on_subscribe(client, userdata, mid, granted_qos):    
            print(f"LOG| I've subscribed to topic {topic}")

        def on_message(client, userdata, msg):
            self.message_handler(msg, func)

        self.client.on_connect = on_connect
        self.client.on_subscribe = on_subscribe
        self.client.on_message = on_message

    def run(self):
        print(f"LOG| Attempting to subscribe to MQTT on {self.host}:{self.port}")
        self.client.connect(host=self.host,port=self.port)
        print(f"LOG| Running subscription on {self.host}:{self.port}")
        try:
            self.client.loop_forever()
        except KeyboardInterrupt:
            print("""
unsubscribing...
Goodbye!""")


if __name__ == '__main__':
    dr = DataRetriever("localhost",1883)
    dr.setup()
    dr.run()
