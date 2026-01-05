# Sensor Research

Repository: TestScripts_SolarBoat

Author: Tim Rijks, Jochem Wansink

Project: Semester 3 Sensor Research – HAN Solarboat

Academic Year: 2025–2026

## 1. Introduction

This repository contains a collection of test and validation scripts developed for the sensor research conducted within this HAN Solarboat project. The scripts are used during semester 3 project of the Embedded Systems Engineering curriculum and support the experimental evaluation, verification, and data acquisition of onboard sensors.

The primary purpose of this repository is to provide a structured and transparent location to store these scripts.

## 2. Project Context

The Solarboat project focuses on the development and optimization of a solar-powered vessel. 
The scripts in this repository are used for data gathering and validation of various sensors that are candidates to be used in the SolarBoat project. 

## 3. Repository Structure
```
TestScripts_SolarBoat/
├── README.md                       # Repository documentation (This file)
├── scripts/                        # Sensor test scripts for Ultrasonic sensors
├── main/                           # Scripts used for gathering IMU data
├── Grafana dashboard template/     # Json export of the used dashboard 
└── Database exports/               # SQL export of the database tables
```

Some of the files listed in this github are build as a library to be usable in the future. 

Also some files are standalone while others are working together.

## 4. Requirements

Depending on the script, the following tools may be required:

 - Arduino IDE
 - Python 
 - Visual Studio Code

Required Python libraries: 
- mysql.connector
- math
- time
- serial
- openpyxl
- os

Access to target sensors via USB, serial interface, or GPIO

## 5. Database & Grafana
The grafana export is in json format so it can be imported as a new dashboard in the future.

The database has been exported as SQL-exports these can be imported in future databases that support this type of export.

## 6. Github information
The repository is available at: https://github.com/TimRijks/TestScripts_SolarBoat/tree/main

## 7. Research Integration

This repository functions as a supporting software artifact for the sensor research component of the Solarboat project. The scripts contribute directly to the data collection and validation process described in the accompanying research report.

This README is included as an appendix to provide transparency and technical context regarding the software tools used during experimentation.
