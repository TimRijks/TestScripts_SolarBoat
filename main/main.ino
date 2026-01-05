#include <Adafruit_ICM20X.h>
#include <Adafruit_ICM20948.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>
#include "MadgwickAHRS.h"

// #define sampleFrequency 125 // 125hz with magneto, 400hz witout magneto, 1khz without magneto with spi
#define sampleFrequency 400 // 125hz with magneto, 400hz witout magneto, 1khz without magneto with spi

Adafruit_ICM20948 icm;
Madgwick filter;
unsigned long microsPerReading, microsPrevious;

void setup()
{
  Serial.begin(115200);

  if (!icm.begin_I2C())
  {
    Serial.println("IMU NOT FOUND");
    while (1)
      ;
  }

  filter.begin(sampleFrequency);

  icm.setAccelRange(ICM20948_ACCEL_RANGE_2_G);
  icm.setGyroRange(ICM20948_GYRO_RANGE_250_DPS);

  microsPerReading = 1000000 / sampleFrequency;
  microsPrevious = micros();
}

void loop()
{
  float ax, ay, az;
  float gx, gy, gz;
  float mx, my, mz;
  float roll, pitch, heading;
  unsigned long microsNow;
  sensors_event_t accel, gyro, mag, temp;

  microsNow = micros();
  if (microsNow - microsPrevious >= microsPerReading)
  {

    icm.getEvent(&accel, &gyro, &temp, &mag);

    ax = accel.acceleration.x / 9.81f;
    ay = accel.acceleration.y / 9.81f;
    az = accel.acceleration.z / 9.81f;
    gx = gyro.gyro.x;
    gy = gyro.gyro.y;
    gz = gyro.gyro.z;
    mx = mag.magnetic.x;
    my = mag.magnetic.y;
    mz = mag.magnetic.z;

    // Use full AHRS algorithm with magnetometer
    // filter.update(gx, gy, gz, ax, ay, az, mx, my, mz);
    filter.updateIMU(gx, gy, gz, ax, ay, az);

    roll = filter.getRoll();
    pitch = filter.getPitch();
    heading = filter.getYaw();

    Serial.print("ax:");
    Serial.print(ax, 3);
    Serial.print(",");
    Serial.print("ay:");
    Serial.print(ay, 3);
    Serial.print(",");
    Serial.print("az:");
    Serial.print(az, 3);
    Serial.print(",");
    Serial.print("gx:");
    Serial.print(gx, 3);
    Serial.print(",");
    Serial.print("gy:");
    Serial.print(gy, 3);
    Serial.print(",");
    Serial.print("gz:");
    Serial.print(gz, 3);
    Serial.print(",");
    Serial.print("mx:");
    Serial.print(mx, 2);
    Serial.print(",");
    Serial.print("my:");
    Serial.print(my, 2);
    Serial.print(",");
    Serial.print("mz:");
    Serial.print(mz, 2);
    Serial.print(",");
    Serial.print("heading:");
    Serial.print(heading, 2);
    Serial.print(",");
    Serial.print("pitch:");
    Serial.print(pitch, 2);
    Serial.print(",");
    Serial.print("roll:");
    Serial.println(roll, 2);

    microsPrevious = microsPrevious + microsPerReading;
  }
}