#!/usr/bin/env python3
# main python library and time modules
import bme680
import time

# this device ID
device_ID = af4eb1

# create sensor instance
# failover to second i2c address on fail
try:
    sensor = bme680.BME680(bme680.I2C_ADDR_PRIMARY)
except IOError:
    sensor = bme680.BME680(bme680.I2C_ADDR_SECONDARY)

# set sensor parameters - these increase the signal to noise ratio
sensor.set_humidity_oversample(bme680.OS_2X)
sensor.set_pressure_oversample(bme680.OS_4X)
sensor.set_temperature_oversample(bme680.OS_8X)
sensor.set_filter(bme680.FILTER_SIZE_3)
sensor.set_gas_status(bme680.ENABLE_GAS_MEAS)
sensor.set_gas_heater_temperature(320) #celcius
sensor.set_gas_heater_duration(150) #ms
sensor.select_gas_heater_profile(0)

# establish start time
start_time = time.time()
now_time = time.time()
burn_in_time = 600 #seconds

burn_in_data = []

try:
    print(start_time, ": starting burn-in")
    while now_time < start_time + burn_in_time:
        now_time = time.time()
        if sensor.get_sensor_data() and sensor.data.heat_stable:
            gas = sensor.data.gas_resistance
            burn_in_data.append(gas)
            print('Gas: {0} Ohms'.format(gas))
            time.sleep(1)
    
    gas_baseline = sum(burn_in_data[-50:]) / 50.0
    
    print("Gas baseline:", gas_baseline)
    
except KeyboardInterrupt:
    pass