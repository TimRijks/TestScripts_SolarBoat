#include <Wire.h>
#include <Adafruit_ICM20X.h>
#include <Adafruit_ICM20948.h>
#include <Adafruit_Sensor.h>
#include "MadgwickAHRS.h"

Adafruit_ICM20948 imu;
Madgwick filter;

const float imuRate = 400.0;   // Hz
const int numDataPoints = 10;  // simulatie aantal data punten (pas aan)

// =====================
// TEST/ULTRASOON DATABASE (simulatie)
// =====================
// Ultrasoon data in mm (voorbeeld, normaal uit database)
float UL_data[numDataPoints] = { 480, 480, 483, 483, 486, 486, 486, 486, 490, 490 };
float UR_data[numDataPoints] = { 480, 480, 483, 483, 486, 486, 486, 486, 490, 490 };
float UA_data[numDataPoints] = { 480, 480, 483, 483, 486, 486, 486, 486, 490, 490 };

float roll, pitch, yaw;
float h_UL, h_UR, h_UA;
float h_avg_cm;
int currentIndex = 0;


// Simuleer ultrasoon correctie op basis van roll/pitch
float correctedHeight(float distance_mm, float roll_rad, float pitch_rad) {
  float cz = cos(pitch_rad) * cos(roll_rad);
  return (distance_mm * cz) / 10.0;  // omzetting naar cm
}

// Map hoogte naar foil hoek (volgens mechanisch model)
float foilAngle(float h_cm) {
  // Clip hoogte tussen 0 en 10 cm
  h_cm = h_cm / 9;

  if (h_cm <= 0) h_cm = 0;
  if (h_cm >= 68) h_cm = 10;
  return h_cm;  // lineair 0-10 cm -> 0-10 deg
}


void setup() {
  Serial.begin(115200);
  Wire.begin();

  if (!imu.begin_I2C()) {
    Serial.println("IMU niet gevonden!");
    while (1)
      ;
  }

  filter.begin(imuRate);

  Serial.println("=== Test Foil System gestart ===");
}


void loop() {
  // ---------- IMU uitlezen ----------
  sensors_event_t accel, gyro, mag, temp;
  imu.getEvent(&accel, &gyro, &temp, &mag);

  // Madgwick update zonder magnetometer voor snelheid
  filter.updateIMU(
    gyro.gyro.x, gyro.gyro.y, gyro.gyro.z,
    accel.acceleration.x, accel.acceleration.y, accel.acceleration.z);

  roll = filter.getRollRadians();
  pitch = filter.getPitchRadians();
  yaw = filter.getYawRadians();

  // ---------- Ultrasoon simulatie ----------
  h_UL = correctedHeight(UL_data[currentIndex], roll, pitch);
  h_UR = correctedHeight(UR_data[currentIndex], roll, pitch);
  h_UA = correctedHeight(UA_data[currentIndex], roll, pitch);

  // Gemiddelde hoogte
  // h_avg_cm = (h_UL + h_UR + h_UA) / 3.0; // voor alle 3 de ultrasoon sensoren
  h_avg_cm = h_UL; // test met echte data voor 1

  // Foil hoek berekenen
  float foil_deg = foilAngle(h_avg_cm);

  // ---------- Output ----------
  Serial.print("Index: ");
  Serial.print(currentIndex);
  Serial.print(" | H_avg: ");
  Serial.print(h_avg_cm);
  Serial.print(" cm");
  Serial.print(" | Foil angle: ");
  Serial.print(foil_deg);
  Serial.println(" deg");
  Serial.print(" | Roll: ");
  Serial.print(roll * 180 / 3.14159);
  Serial.print(" | Pitch: ");
  Serial.println(pitch * 180 / 3.14159);

  // ---------- Update index ----------
  currentIndex++;
  if (currentIndex >= numDataPoints)
    while (1)
      ;

  delay(100);  // Simuleer ~10 Hz update voor ultrasoon
}
