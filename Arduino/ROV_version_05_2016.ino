
//changes:
// v0.5 changed order of motors
// v0.4 changed PWM --> Servos

#include <Servo.h> 
#include <Wire.h>
#include <SparkFun_MS5803_I2C.h>
#include <OneWire.h>
#include <DallasTemperature.h>

const char startMarker = '<';
const char endMarker = '>';
const char delimiter = ',';

byte Pins[] = {8,11,10,9,29,31,33,35};


Servo myservo[sizeof(Pins)];

MS5803 depthSensor(ADDRESS_HIGH);

#define ONE_WIRE_BUS 2  // Data wire is plugged into port 2 on the Arduino
#define TEMPERATURE_PRECISION 12 // bits of temperature precision
OneWire oneWire(ONE_WIRE_BUS); // Setup a oneWire instance to communicate with any OneWire devices (not just Maxim/Dallas temperature ICs)
DallasTemperature temperatureSensors(&oneWire); // Pass our oneWire reference to Dallas Temperature.

const byte bufferSize = 255;            //number of characters to store
const byte numData = sizeof(Pins);      //number of data elements to store
const boolean debug = false;             //debug turns on serial writes
const int loopsBeforeTempRead = 10;     //because temp read is slow do it only every n loops
const float atm = 1013.25;              //atmospheric pressure
const byte ledPin = 13;
byte ledBrightness = 0;
byte ledBrightnessStep = 1;
String inputString = "";                // a string to hold incoming data
String lastString = "";                 // last data received
int myData[numData];                    //array to hold data
int tempData[numData];                  //array to hold incoming data
boolean stringComplete = false;         // whether the string is complete
float temperature_c, pressure_abs, rho; //variables for depth sensor
int loops, temperatureInt, depthInt, depthOffset;    //variables to hold return data



void setup() {
  
  Serial.begin(9600);
  inputString.reserve(bufferSize);

  myData[0] = 90;
  myData[1] = 90;
  myData[2] = 90;
  myData[3] = 90;
  myData[4] = 70;
  myData[5] = 20;
  myData[6] = 20;
  myData[7] = 20;
  
     
  for(byte i = 0; i < sizeof(Pins); i++)  //set up servos
  {
     myservo[i].attach( Pins[i] );  
     myservo[i].write( myData[i] );
  }

  depthSensor.reset();
  depthSensor.begin(); 
  temperatureSensors.begin();
  temperatureSensors.setResolution(0, TEMPERATURE_PRECISION);

  getTemp();
  loops = loopsBeforeTempRead;
}

void loop() {
  if (stringComplete) 
  {
    processData(inputString); // inputString --> myData[] array
    
    //write Motor data to outputs
    for(byte i = 0; i < sizeof(Pins); i++) 
    { 
      myservo[i].write( myData[i] );
      delay(15);
      if (debug)
      {
        Serial.print("Writing ");
        Serial.print(myData[i]);
        Serial.print(" to Servo on Pin ");
        Serial.println(Pins[i]);
      }
    }
    
    sendData();
    
    if (--loops == 0)     //after sending data check temp after loops = 0
    {
      getTemp();          //check temp (takes time!!)
      loops = loopsBeforeTempRead;
    }
  }
  else  //do "heartbeat" LED if spare time
  {
     analogWrite(ledPin,ledBrightness);  
     ledBrightness += ledBrightnessStep; delay(1);
     if (ledBrightness < 1 || ledBrightness > 254)  ledBrightnessStep = -ledBrightnessStep;
  }
} 

void serialEvent() 
{
  while (Serial.available()) 
  {
    char inChar = (char)Serial.read();
    inputString += inChar;
    if (inChar == '\n' || (inputString.length() >= bufferSize-1) ) 
    {
      stringComplete = true;
    }
  }
}

void processData(String s)
{
  byte counter;
  lastString = s;
  
  //for(int i = 0; i < numData; i++)    //clear old data
    //myData[i] = 0;

  if ( s.indexOf(startMarker) != -1 && s.indexOf(endMarker) != -1 ) //good data
  {
    byte start = s.indexOf(startMarker);
    byte finish = s.indexOf(endMarker);
    counter = 0;
    byte marker;
    String temp = "";
    while (start < finish && counter < numData)
    {
      marker = s.indexOf(delimiter,start+1);
      
      if (marker != -1)
      {
        temp = " " + s.substring(start+1,marker);
        temp.trim();
        tempData[counter] = temp.toInt();
        if (debug) 
        { 
          Serial.print("Start: ");
          Serial.println(start);
          Serial.print("Marker: ");
          Serial.println(marker);
          Serial.println(temp);
          Serial.print("myData[");
          Serial.print(counter); 
          Serial.print("]: ");
          Serial.println( tempData[counter]); 
        }
        counter++;
        start = marker;
      }
      else  //last data point
      {
        tempData[counter] = (s.substring(start,finish)).toInt();
        if (debug) 
        { 
          Serial.print("*myData[");
          Serial.print(counter); 
          Serial.print("]: ");
          Serial.println( tempData[counter]); 
        }
        start = finish;
      }
    }
  }
  
  if (counter == numData && tempData[0] != 0 && tempData[1] != 0)
  {
    for (int i = 0; i < numData; i++)
      myData[i] = tempData[i];
  }
  inputString = "";
  stringComplete = false;
}

void getDepth()
{
    temperature_c = depthSensor.getTemperature(CELSIUS, ADC_512);
    pressure_abs = depthSensor.getPressure(ADC_4096);
    rho = 1000*(1 - (temperature_c+288.9414)/(508929.2*(temperature_c+68.12963))*pow((temperature_c-3.9863),2)); //freshwater density
    depthInt =  (int)(1000*( (100.0*(pressure_abs-atm)) / (rho*9.81) ));
}


void getTemp()
{
  temperatureSensors.requestTemperatures(); // Send the command to get temperatures
  if (debug)
  {
    Serial.print("Temperature: ");
    Serial.println(temperatureSensors.getTempCByIndex(0));
  }
  temperatureInt =  (int)(10 * temperatureSensors.getTempCByIndex(0));
}


void sendData()
{
  getDepth();
  Serial.print("< Temperature = ");
  Serial.print(temperatureInt/10.0);  //temp in C * 10
  Serial.print("C | Depth = ");
  Serial.print(depthInt/10.0);        //depth in cm * 10
  Serial.print(" cm >  <String = ");
  Serial.print(lastString);
  Serial.println(">");
}



