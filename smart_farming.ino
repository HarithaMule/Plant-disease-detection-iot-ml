#include <Wire.h>
#include <LiquidCrystal.h>
#include <DFRobot_DHT11.h>

#define GAS_SENSOR_PIN 5  // Connect MQ2 sensor digital output to pin 5
#define RELAY 4
#define BUZZER_PIN 2      // Connect buzzer to pin 2
#define DHT11_PIN 10

DFRobot_DHT11 DHT;
LiquidCrystal lcd(A0, A1, A2, A3, A4, A5);  // Initialize LCD
String uno;

void setup() {
  Serial.begin(9600);

  pinMode(GAS_SENSOR_PIN, INPUT);
  pinMode(RELAY, OUTPUT);  // Fixed: Should be OUTPUT
  pinMode(BUZZER_PIN, OUTPUT);
  
  digitalWrite(BUZZER_PIN, LOW);  // Ensure buzzer is OFF initially
  digitalWrite(RELAY, HIGH);       // Ensure relay is OFF initially

  lcd.begin(16, 2);  
  lcd.setCursor(0, 0);
  lcd.print("SMART FARMING");
  lcd.setCursor(0, 1);
  lcd.print("DISEASE DETECTION");
  delay(2000);
}

void loop() {
  DHT.read(DHT11_PIN);
  int t = DHT.temperature;
  int h = DHT.humidity;
  int gasState = digitalRead(GAS_SENSOR_PIN);  // Read Soil Moisture
  delay(1000);

  // LCD Display
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("SOIL: ");
  lcd.print(gasState);

  lcd.setCursor(0, 1);
  lcd.print("T: ");
  lcd.print(t);
  lcd.setCursor(8, 1);
  lcd.print("H: ");
  lcd.print(h);
  delay(1000);

  // Soil Moisture Alert
  if (gasState == HIGH) {  
    digitalWrite(RELAY, LOW);
    digitalWrite(BUZZER_PIN, HIGH);
    delay(1000);
    digitalWrite(BUZZER_PIN, LOW);

    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("LOW Moisture");
    lcd.setCursor(0, 1);
    lcd.print("Value Detected");
    delay(1000);
    digitalWrite(RELAY, HIGH);
  }  
  // High Temperature Alert
  else if (t > 35) {  
    digitalWrite(BUZZER_PIN, HIGH);
    delay(1000);
    digitalWrite(BUZZER_PIN, LOW);
    
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("High Temperature");
    lcd.setCursor(0, 1);
    lcd.print("Detected");
    delay(1000);
  }  
  // Normal Conditions
  else {  
    digitalWrite(BUZZER_PIN, LOW);
    delay(500);
  }
  // ✅ Corrected Serial Output
  Serial.println("T:" + String(t) + " H:" + String(h) + " S:" + String(gasState));

  delay(1000);  // Delay for stable readings
}
