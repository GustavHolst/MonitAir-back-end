#!/usr/bin/env python3
# main python library and time modules
import bme680
import time
import requests
import statistics
import socket

# this device ID
device_ID = 'af4eb1'

# api endpoint
api_endpoint = "https://192.168.230.214"
socket_endpoint = "something"
portNumber = 1234

# create sensor instance
# failover to second i2c address on fail
try:
    sensor = bme680.BME680(bme680.I2C_ADDR_PRIMARY)
except IOError:
    sensor = bme680.BME680(bme680.I2C_ADDR_SECONDARY)

# establish socket with server
# serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# serversocket.bind(socket.gethostname(), portNumber)
# serversocket.listen(5)

# set sensor parameters - these increase the signal to noise ratio
sensor.set_humidity_oversample(bme680.OS_2X)
sensor.set_pressure_oversample(bme680.OS_4X)
sensor.set_temperature_oversample(bme680.OS_8X)
sensor.set_filter(bme680.FILTER_SIZE_3)
sensor.set_gas_status(bme680.ENABLE_GAS_MEAS)

sensor.set_gas_heater_temperature(320)  # celcius
sensor.set_gas_heater_duration(150)  # ms
sensor.select_gas_heater_profile(0)

print("Setting temp baseline (60 sec)")
initial_temp_readings = []
for n in range(120):
    initial_temp_readings.append(sensor.data.temperature)
    time.sleep(0.5)
baseline_temp = round(statistics.mean(initial_temp_readings), 3)


# establish start time
start_time = time.time()
now_time = time.time()
burn_in_time = 300  # seconds


# empty list for gas values
burn_in_data = []
gas_baseline = None

try:
    print(start_time, ": starting burn-in")
    while now_time < start_time + burn_in_time:
        now_time = time.time()
        if sensor.get_sensor_data() and sensor.data.heat_stable:
            gas = sensor.data.gas_resistance
            burn_in_data.append(gas)
            print('Gas: {0} Ohms'.format(gas))
            time.sleep(1)

    # baseline is mean final 50 vals
    gas_baseline = statistics.mean(burn_in_data[-50:])


except KeyboardInterrupt:
    pass

print("Gas baseline: {0:.2f} Ohms".format(gas_baseline))

while True:
    try:
        start_time = time.time()
        now_time = time.time()

        post_interval = 10  # seconds
        temp_list = []
        pressure_list = []
        humidity_list = []
        tvoc_list = []
        while now_time < start_time + post_interval:
            if sensor.get_sensor_data():
                temp_list.append(sensor.data.temperature)
                pressure_list.append(sensor.data.pressure)
                humidity_list.append(sensor.data.humidity)
            if sensor.data.heat_stable:
                tvoc_list.append(sensor.data.gas_resistance)
            time.sleep(1)
            now_time = time.time()
        try:
            temp_mean = statistics.mean(temp_list)
            pressure_mean = statistics.mean(pressure_list)
            humidity_mean = statistics.mean(humidity_list)
            tvoc_mean = statistics.mean(tvoc_list)
        except statistics.StatisticsError:
            pass
        sendup = {
            device_ID: {'temp_mean': round(temp_mean, 3),
                        'pressure_mean': round(pressure_mean, 3),
                        'humidity_mean': round(humidity_mean, 3),
                        'tvoc_mean': round(tvoc_mean, 3),
                        'gas_baseline': round(gas_baseline, 3),
                        'baseline_temp': baseline_temp,
                        'timestamp': now_time
                        }
        }
        logFile = open('log', 'a')
        logFile.write(str(sendup) + '\n')
        logFile.close()
        # r = requests.post(api_endpoint, data=sendup)

    except KeyboardInterrupt:
        pass
