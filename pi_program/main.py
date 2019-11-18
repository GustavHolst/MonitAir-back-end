#!/usr/bin/env python3
# main python library and time modules
import bme680
import time
import requests
import statistics

# get serial /proc/cpuinfo


def getserial():
    piSerialNum = None
    try:
        cpuInfoFile = open('/proc/cpuinfo', 'r')
        for eachLine in cpuInfoFile:
            if eachLine[0:6] == 'Serial':
                piSerialNum = line[10:26]
        cpuInfoFile.close()
    except:
        piSerialNum = "error00000000000"
    print("Pi serial number: {0}".format(piSerialNum))
    return piSerialNum


device_ID = getserial()

# api endpoint
api_endpoint = "http://brejconies.pythonanywhere.com/reading/{0}".format(
    device_ID)
port = 80

print(api_endpoint)

# create sensor instance
# failover to second i2c address on fail
try:
    sensor = bme680.BME680(bme680.I2C_ADDR_PRIMARY)
except IOError:
    sensor = bme680.BME680(bme680.I2C_ADDR_SECONDARY)

# set sensor parameters - these sort the SNR
sensor.set_humidity_oversample(bme680.OS_2X)
sensor.set_pressure_oversample(bme680.OS_4X)
sensor.set_temperature_oversample(bme680.OS_8X)
sensor.set_filter(bme680.FILTER_SIZE_3)
sensor.set_gas_status(bme680.ENABLE_GAS_MEAS)

# set the TVOC heater params
sensor.set_gas_heater_temperature(320)  # celcius
sensor.set_gas_heater_duration(150)  # ms
sensor.select_gas_heater_profile(0)

# set the temperature offset
sensor.set_temp_offset(-10)

# get the temperature baseline
print("Setting temp baseline (60 sec)")
initial_temp_readings = []
for n in range(120):
    if sensor.get_sensor_data():
        print(n, sensor.data.temperature)
        initial_temp_readings.append(sensor.data.temperature)
        time.sleep(0.5)
baseline_temp = round(statistics.mean(initial_temp_readings), 3)
print("Baseline temp is {0:.2f}", baseline_temp)

# establish start time for gas sensor burn in
start_time = time.time()
now_time = time.time()
burn_in_time = 300  # seconds

# empty list for gas values
burn_in_data = []
gas_baseline = None

try:
    print(start_time, ": starting burn-in")
    while now_time - start_time < burn_in_time:
        now_time = time.time()
        if sensor.get_sensor_data() and sensor.data.heat_stable:
            gas = sensor.data.gas_resistance
            burn_in_data.append(gas)
            print('Gas resistance: {0} ohms'.format(gas))
            time.sleep(1)
    # baseline is mean final 50 vals
    gas_baseline = statistics.mean(burn_in_data[-50:])
except KeyboardInterrupt:
    pass

print("Gas baseline: {0:.2f} Ohms".format(gas_baseline))


# set ideal humidity
ideal_humidity = 40.0
# balance betw humidity and TVOC
hum_weighting = 0.25  # therefore 0.75 TVOC


while True:
    try:
        start_time = time.time()
        now_time = time.time()

        # set the delay between server POST requests
        post_interval = 10  # seconds

        # create some empty list for the averages
        temp_list = []
        pressure_list = []
        humidity_list = []
        totalQuality_list = []

        # get the readings
        while now_time < start_time + post_interval:
            if sensor.get_sensor_data():
                temp_list.append(sensor.data.temperature)
                pressure_list.append(sensor.data.pressure)
                humidity_list.append(sensor.data.humidity)
            if sensor.data.heat_stable:
                gas = sensor.data.gas_resistance
                gas_offset = gas_baseline - gas

                hum = sensor.data.humidity
                hum_offset = hum - ideal_humidity

                # Calculate hum_score as the distance from the ideal_humidity.
                if hum_offset > 0:
                    hum_score = (100 - ideal_humidity - hum_offset)
                    hum_score /= (100 - ideal_humidity)
                    hum_score *= (hum_weighting * 100)

                else:
                    hum_score = (ideal_humidity + hum_offset)
                    hum_score /= ideal_humidity
                    hum_score *= (hum_weighting * 100)

                # Calculate gas_score as the distance from the gas_baseline.
                if gas_offset > 0:
                    gas_score = (gas / gas_baseline)
                    gas_score *= (100 - (hum_weighting * 100))

                else:
                    gas_score = 100 - (hum_weighting * 100)

                # Calculate air_quality_score.
                air_quality_score = hum_score + gas_score

                time.sleep(1)
                now_time = time.time()

                totalQuality_list.append(air_quality_score)
        try:
            temp_mean = statistics.mean(temp_list)
            pressure_mean = statistics.mean(pressure_list)
            humidity_mean = statistics.mean(humidity_list)
            totalQuality_mean = statistics.mean(totalQuality_list)
        except statistics.StatisticsError:
            pass
        sendup = {'temp_mean': round(temp_mean, 2),
                  'pressure_mean': round(pressure_mean, 2),
                  'humidity_mean': round(humidity_mean, 2),
                  'totalQuality_mean': round(totalQuality_mean, 2),
                  'gas_baseline': round(gas_baseline, 2),
                  'baseline_temp': round(baseline_temp, 2),
                  'timestamp': round(now_time)
                  }

        # KEEP THESE COMMENTS
        # logFile = open('log', 'a')
        # logFile.write(str(sendup) + '\n')
        # logFile.close()

        r = requests.post(api_endpoint, json=sendup)
        print(now_time, r.status_code, r.text)
        if(r.status_code == 404):
            print("Device not registered, reattempting in 60 seconds...")
            time.sleep(60)
    except KeyboardInterrupt:
        pass
