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

struct Data{
  float humidity;
  float temp;
  float soil;
  float light;
};

// global vars
struct Data previousData = {0,0,0,0};
struct Data currentData = {-1,-1,-1,-1};

BLEService dataService("A001");
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
void send_sensor_data(BLEDevice central, struct Data data);
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
    
    humidCharacteristic.setValue(currentData.humidity);                 // Set humidity initial value
    tempCharacteristic.setValue(currentData.temp);                  // Set temperature initial value
    soilCharacteristic.setValue(currentData.soil);                  // Set soil moisture initial value
    lightCharacteristic.setValue(currentData.light);                 // Set light initial value

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
  if(abs((int)h - (int)previousData.humidity) > 5) 
  {
    previousData.humidity = h;
    return h;
  }
  return previousData.humidity;
}


float read_temp_sensor()
{
  float t = dht.readTemperature(true);
  if(abs((int)t - (int)previousData.temp) > 1){
    previousData.temp = t;
    return t;
  }
  return previousData.temp;
}


float read_soil_sensor()
{
  float s  = analogRead(A1);
  if(abs((int)s - (int)previousData.soil) > 100){
    previousData.soil = s;
    return s;
  }
  return previousData.soil;
}


float read_light_sensor()
{
  float L  = analogRead(A0);
  if(abs((int)L - (int)previousData.light) > 200){
    previousData.light = L;
    return L;
  }
  return previousData.light;
}


void send_sensor_data(BLEDevice central, struct Data data)
{
    Serial.println("Sending Data...");
    Serial.print(data.humidity);
    Serial.print(", ");
    Serial.print(data.temp);
    Serial.print(", ");
    Serial.print(data.soil);
    Serial.print(", ");
    Serial.print(data.light);
    Serial.print("\n");

    // send data to reciever via BLE client
    humidCharacteristic.setValue(data.humidity); // Set humidity value
    tempCharacteristic.setValue(data.temp);  // Set temperature value
    soilCharacteristic.setValue(data.soil);  // Set soil moisture value
    lightCharacteristic.setValue(data.light); // Set light value

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
      
          currentData.humidity = read_humid_sensor();
          currentData.temp = read_temp_sensor();
          currentData.soil = read_soil_sensor();
          currentData.light = read_light_sensor();
  
          send_sensor_data(central, currentData);  

          delay(100);

        } // looping while connected
        
        // when the central disconnects, turn off the LED:
        digitalWrite(LED_BUILTIN, LOW);
        Serial.print("Disconnected from central MAC: ");
        Serial.println(central.address());
}
