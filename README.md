# MonitAir-back-end

## What is this?

This repo contains the backend for our Monitair project which we completed during our final phase of NorthCoders, Manchester

The project starts with a Raspberry Pi, paired with a Pimoroni breakout garden and Pimoroni BME680 air quality module, and a DRV8830 motor drive module (which we actually used to turn on an LED).

The /pi_program/main.py program gets the serial number of the pi before calibrating the sensor.

It then sends the data up to our server (hosted on PythonAnywhere).

## Structure
