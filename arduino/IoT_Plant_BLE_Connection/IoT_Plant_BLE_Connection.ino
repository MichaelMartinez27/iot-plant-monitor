/*
Arduino Nano 33 BLE Getting Started
BLE peripheral with a simple greeting service that can be viewed
on a mobile phone
*/
#include <stdlib.h>
#include <ArduinoBLE.h>
#include "DHT.h"

#define DHTPIN 2
#define DHTTYPE DHT11
#define PRPIN 3

// global vars
float previousData[4] = {0,0,0,0};
float data[4];
float count = 0.0;

BLEService dataService("1101");
BLEFloatCharacteristic humidCharacteristic("2A6F", BLERead | BLENotify);
BLEFloatCharacteristic tempCharacteristic("2A6E", BLERead | BLENotify);
BLEFloatCharacteristic soilCharacteristic("272A", BLERead | BLENotify);
BLEFloatCharacteristic lightCharacteristic("2730", BLERead | BLENotify);

DHT dht(DHTPIN, DHTTYPE);

// Functions
float read_humid_sensor();
float read_temp_sensor();
float read_soil_sensor();
float read_light_sensor();
void send_sensor_data(BLEDevice central,  float data_arr[4]);
void connection_handler(BLEDevice central);


void setup() {
    Serial.begin(9600); // initialize serial communication
    while (!Serial);

    pinMode(LED_BUILTIN, OUTPUT); // initialize the built-in LED pin
    
    if (!BLE.begin()) 
    { // initialize BLE
        Serial.println("starting BLE failed!");
        while (1);
    }
    
    BLE.setLocalName("Nano33BLE");                      // Change name for connection
    BLE.setAdvertisedService(dataService);              // Advertise service    

    dataService.addCharacteristic(humidCharacteristic);
    dataService.addCharacteristic(tempCharacteristic);
    dataService.addCharacteristic(soilCharacteristic);
    dataService.addCharacteristic(lightCharacteristic);
    
    BLE.addService(dataService);                        // Add service
    
    humidCharacteristic.setValue(-1.0);                 // Set humidity initial value
    tempCharacteristic.setValue(-1.0);                  // Set temperature initial value
    soilCharacteristic.setValue(-1.0);                  // Set soil moisture initial value
    lightCharacteristic.setValue(-1.0);                 // Set light initial value

    dht.begin();                                        // Start DHT11 service
    BLE.advertise();                                    // Start advertising
    
    Serial.print("Peripheral device MAC: ");
    Serial.println(BLE.address());
    Serial.println("Waiting for connections...");
}


void loop() 
{
    BLEDevice central = BLE.central();
    
    if(central) 
    {
      connection_handler(central);
    }
}


// Functions
float read_humid_sensor()
{
  float h = dht.readHumidity();
  if(abs((int)h - (int)previousData[0]) > 5) 
  {
    previousData[0] = h;
    return h;
  }
  return previousData[0];
}


float read_temp_sensor()
{
  float t = dht.readTemperature(true);
  if(abs((int)t - (int)previousData[1]) > 1){
    previousData[1] = t;
    return t;
  }
  return previousData[1];
}


float read_soil_sensor()
{
  float s  = analogRead(A1);
  if(abs((int)s - (int)previousData[2]) > 100){
    previousData[2] = s;
    return s;
  }
  return previousData[2];
}


float read_light_sensor()
{
  float L  = analogRead(A0);
  if(abs((int)L - (int)previousData[3]) > 200){
    previousData[3] = L;
    return L;
  }
  return previousData[3];
}


void send_sensor_data(BLEDevice central, float data_arr[4])
{
    Serial.println("Sending Data...");
    Serial.print(data_arr[0]);
    Serial.print(", ");
    Serial.print(data_arr[1]);
    Serial.print(", ");
    Serial.print(data_arr[2]);
    Serial.print(", ");
    Serial.print(data_arr[3]);
    Serial.print("\n");

    // send data to reciever via BLE client
    humidCharacteristic.setValue(data_arr[0]); // Set humidity value
    tempCharacteristic.setValue(data_arr[1]);  // Set temperature value
    soilCharacteristic.setValue(data_arr[2]);  // Set soil moisture value
    lightCharacteristic.setValue(data_arr[3]); // Set light value

}


void connection_handler(BLEDevice central)
{

        Serial.print("Connected to central MAC: ");
        
        // print the central's BT address:
        Serial.println(central.address());
        
        // turn on the LED to indicate the connection:
        digitalWrite(LED_BUILTIN, HIGH);
        while (central.connected())
        {
      
          data[0] = read_humid_sensor();
          data[1] = read_temp_sensor();
          data[2] = read_soil_sensor();
          data[3] = read_light_sensor();
  
          send_sensor_data(central, data);  

          count++;
          delay(100);

        } // looping while connected
        
        // when the central disconnects, turn off the LED:
        digitalWrite(LED_BUILTIN, LOW);
        Serial.print("Disconnected from central MAC: ");
        Serial.println(central.address());
}
