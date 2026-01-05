#ifndef MADGWICK_FULL_H
#define MADGWICK_FULL_H

#include <Arduino.h>
#include <math.h>

// --- Constants ---
#define deltat 0.001f
// #define gyroMeasError 3.14159265358979f * (5.0f / 180.0f)
// #define gyroMeasDrift 3.14159265358979f * (0.2f / 180.0f)

#define gyroMeasError 3.14159265358979f * (5.0f / 180.0f)  // Reduced from 5.0
#define gyroMeasDrift 3.14159265358979f * (2.0f / 180.0f) // Reduced from 0.2
#define beta sqrt(3.0f / 4.0f) * gyroMeasError
#define zeta sqrt(3.0f / 4.0f) * gyroMeasDrift

// --- Global variables ---
extern float a_x, a_y, a_z; // accelerometer measurements
extern float w_x, w_y, w_z; // gyroscope measurements in rad/s
extern float m_x, m_y, m_z; // magnetometer measurements
extern float SEq_1, SEq_2, SEq_3, SEq_4;
extern float b_x, b_z;
extern float w_bx, w_by, w_bz;

// --- Function declaration ---
void filterUpdate(float w_x, float w_y, float w_z,
                  float a_x, float a_y, float a_z,
                  float m_x, float m_y, float m_z);

#endif
