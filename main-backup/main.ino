#include <Adafruit_ICM20X.h>
#include <Adafruit_ICM20948.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>
#include "MadgwickFull.h"

Adafruit_ICM20948 icm;

// Gyroscope calibration offsets
float gyro_offset_x = 0, gyro_offset_y = 0, gyro_offset_z = 0;

void calibrateGyro() {
  Serial.println("Calibrating gyroscope... Keep IMU still!");
  float sum_x = 0, sum_y = 0, sum_z = 0;
  int samples = 500;
  
  for (int i = 0; i < samples; i++) {
    sensors_event_t accel, gyro, mag, temp;
    icm.getEvent(&accel, &gyro, &temp, &mag);
    
    sum_x += gyro.gyro.x;
    sum_y += gyro.gyro.y;
    sum_z += gyro.gyro.z;
    delay(5);
  }
  
  gyro_offset_x = sum_x / samples;
  gyro_offset_y = sum_y / samples;
  gyro_offset_z = sum_z / samples;
  
  Serial.println("Calibration complete!");
}

void setup() {
  Serial.begin(115200);

  if (!icm.begin_I2C()) {
    Serial.println("IMU NOT FOUND");
    while (1);
  }
  
  calibrateGyro();
}

void loop() {
  sensors_event_t accel, gyro, mag, temp;
  icm.getEvent(&accel, &gyro, &temp, &mag);

  // Apply calibration offsets
  float gyro_x = gyro.gyro.x - gyro_offset_x;
  float gyro_y = gyro.gyro.y - gyro_offset_y;
  float gyro_z = gyro.gyro.z - gyro_offset_z;

  filterUpdate(
    gyro_x, gyro_y, gyro_z,
    accel.acceleration.x, accel.acceleration.y, accel.acceleration.z,
    mag.magnetic.x, mag.magnetic.y, mag.magnetic.z
  );
  
  float yaw = atan2(2*(SEq_1*SEq_4 + SEq_2*SEq_3),
                    1 - 2*(SEq_3*SEq_3 + SEq_4*SEq_4)) * 180.0f / 3.14159265358979f;

  float pitch = -asin(2*(SEq_2*SEq_4 - SEq_1*SEq_3)) * 180.0f / 3.14159265358979f;

  float roll = atan2(2*(SEq_1*SEq_2 + SEq_3*SEq_4),
                     1 - 2*(SEq_2*SEq_2 + SEq_3*SEq_3)) * 180.0f / 3.14159265358979f;

  Serial.print(yaw);
  Serial.print(" ");
  Serial.print(pitch);
  Serial.print(" ");
  Serial.println(roll);

  // Serial.print("Accel: ");
  // Serial.print(accel.acceleration.x); Serial.print(" ");
  // Serial.print(accel.acceleration.y); Serial.print(" ");
  // Serial.println(accel.acceleration.z);
  
  // Serial.print("Gyro: ");
  // Serial.print(gyro.gyro.x); Serial.print(" ");
  // Serial.print(gyro.gyro.y); Serial.print(" ");
  // Serial.println(gyro.gyro.z);
  
  // Serial.print("Mag: ");
  // Serial.print(mag.magnetic.x); Serial.print(" ");
  // Serial.print(mag.magnetic.y); Serial.print(" ");
  // Serial.println(mag.magnetic.z);
  // Serial.println();
}