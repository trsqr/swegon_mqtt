#!/usr/bin/python
# Read data over ModBus from Swegon A/C device
#
# By default the script will submit the temperature data to MQTT broker
# You can use -p option to only print all data instead.
#
# prerequisites:
# pymodbus (pip install pymodbus)
#
# Not all fields are implemented by all machines.
#
# See reference:
# https://www.swegon.com/siteassets/_product-documents/home-ventilation/control-equipment/_fi/smartmodbusregisterfull.pdf

from pymodbus.client.sync import ModbusSerialClient as ModbusClient
from pymodbus.exceptions import ModbusIOException
import json
import paho.mqtt.client as mqtt
import time
import argparse
import sys

parser = argparse.ArgumentParser()
parser.add_argument('-p', dest='printonly', action='store_true', help="print the read values on screen only")
parser.add_argument('-T', dest='modbus_tcp', action='store_true', help="use Modbus TCP instead of serial")
parser.add_argument('-t', dest='topic', help="MQTT topic prefix, default: swegon", default="swegon")
parser.add_argument('-b', dest='broker', help="MQTT broker address, default: 127.0.0.1", default="127.0.0.1")
parser.add_argument('-m', dest='modbus_address', help="Modbus address of Swegon device, default: 16", default=16, type=int)
parser.add_argument('-d', dest='usbdev', help="USB serial device to use, default: /dev/ttyUSB0", default="/dev/ttyUSB0")
parser.add_argument('-H', dest='tcp_host', help="Modbus TCP address, default: 127.0.0.1", default="127.0.0.1")
parser.add_argument('-P', dest='tcp_port', help="Modbus TCP port, default: 502", default=502, type=int)
parser.add_argument('-B', dest='baud_rate', help="Serial baud rate, default: 38400", default=38400, type=int)


args = parser.parse_args()

UNIT_STATES = ["External stop", "User stopped", "Starting", "Normal", "Commissioning"]
VENTILATION_STATES = ["Stopped", "Away", "Home", "Boost", "Cooling"]
BYPASS_STATES = ["Closed (winter)", "Open (summer)"]

if args.modbus_tcp:
    client = ModbusClient(host=args.tcp_host, port=args.tcp_port, timeout=3)
else:
    client = ModbusClient(method='rtu', port=args.usbdev, timeout=1, baudrate=args.baud_rate)

client.connect()


swegon_ac = {}
swegon_ac["temperatures"] = {}
swegon_ac["air_quality"] = {}
swegon_ac["unit_state"] = {}
swegon_ac["fans"] = {}
swegon_ac["model"] = {}

# read modbus data
try:
    temperatures = client.read_input_registers(address=(6201-1), count=11, unit=args.modbus_address);
    time.sleep(0.2)
    machine_state = client.read_input_registers(address=(6328-1), count=16, unit=args.modbus_address);
    time.sleep(0.2)
    air_quality = client.read_input_registers(address=(6212-1), count=6, unit=args.modbus_address);
    time.sleep(0.2)
    fans = client.read_input_registers(address=(6301-1), count=6, unit=args.modbus_address);
    time.sleep(0.2)
    model_name = client.read_input_registers(address=(6008-1), count=17, unit=args.modbus_address);
    time.sleep(0.2)
    version_data = client.read_input_registers(address=(6001-1), count=7, unit=args.modbus_address);
except:
    sys.exit("Error: Could not connect to Modbus for reading the registers.")
    

# pare temperature measurements
swegon_ac["temperatures"]["fresh_air"] = (temperatures.registers[0]-2**16) / 10.0 if temperatures.registers[0] & 2**15 else temperatures.registers[0] / 10.0
swegon_ac["temperatures"]["supply_air_before_reheater"] = (temperatures.registers[1]-2**16) / 10.0 if temperatures.registers[1] & 2**15 else temperatures.registers[1] / 10.0
swegon_ac["temperatures"]["supply_air"] = (temperatures.registers[2]-2**16) / 10.0 if temperatures.registers[2] & 2**15 else temperatures.registers[2] / 10.0
swegon_ac["temperatures"]["extract_air"] = (temperatures.registers[3]-2**16) / 10.0 if temperatures.registers[3] & 2**15 else temperatures.registers[3] / 10.0
swegon_ac["temperatures"]["waste_air"] = (temperatures.registers[4]-2**16) / 10.0 if temperatures.registers[4] & 2**15 else temperatures.registers[4] / 10.0
swegon_ac["temperatures"]["room"] = (temperatures.registers[5]-2**16) / 10.0 if temperatures.registers[5] & 2**15 else temperatures.registers[5] / 10.0
swegon_ac["temperatures"]["user_panel"] = (temperatures.registers[6]-2**16) / 10.0 if temperatures.registers[6] & 2**15 else temperatures.registers[6] / 10.0
swegon_ac["temperatures"]["user_panel_2"] = (temperatures.registers[7]-2**16) / 10.0 if temperatures.registers[7] & 2**15 else temperatures.registers[7] / 10.0
swegon_ac["temperatures"]["water_radiator"] = (temperatures.registers[8]-2**16) / 10.0 if temperatures.registers[8] & 2**15 else temperatures.registers[8] / 10.0
swegon_ac["temperatures"]["preheater"] = (temperatures.registers[9]-2**16) / 10.0 if temperatures.registers[9] & 2**15 else temperatures.registers[9] / 10.0
swegon_ac["temperatures"]["external_fresh_air"] = (temperatures.registers[10]-2**16) / 10.0 if temperatures.registers[10] & 2**15 else temperatures.registers[10] / 10.0

# parse more machine state
swegon_ac["unit_state"]["defrost_state"] = machine_state.registers[0]
swegon_ac["unit_state"]["defrost_supply_forcing"] = machine_state.registers[1]
swegon_ac["unit_state"]["defrost_exhaust_forcing"] = machine_state.registers[2]
swegon_ac["unit_state"]["preheater_active"] = machine_state.registers[5]
swegon_ac["unit_state"]["summer_cooling_active"] = machine_state.registers[6]
swegon_ac["unit_state"]["fireplace_function_active"] = machine_state.registers[7]
swegon_ac["unit_state"]["central_vacuum_cleaner_function_active"] = machine_state.registers[8]
swegon_ac["unit_state"]["hood_compensation_active"] = machine_state.registers[9]
swegon_ac["unit_state"]["external_boost_control_active"] = machine_state.registers[10]
swegon_ac["unit_state"]["external_away_control_active"] = machine_state.registers[11]
swegon_ac["unit_state"]["manual_heat_exchanger_bypass"] = machine_state.registers[12]
swegon_ac["unit_state"]["automatic_heat_exchanger_bypass"] = machine_state.registers[13]
swegon_ac["unit_state"]["filter_guard_input_status"] = machine_state.registers[14]
swegon_ac["unit_state"]["hours_to_service"] = machine_state.registers[15]

# parse air quality metrics
swegon_ac["air_quality"]["co2_unfiltered"] = air_quality.registers[0]
swegon_ac["air_quality"]["co2_filtered"] = air_quality.registers[1]
swegon_ac["air_quality"]["relative_humidity"] = air_quality.registers[2]
swegon_ac["air_quality"]["absolute_humidity"] = air_quality.registers[3] / 10.0
swegon_ac["air_quality"]["absolute_humidity_setpoint"] = air_quality.registers[4] / 10.0
swegon_ac["air_quality"]["voc"] = air_quality.registers[5]

# parse fans state
swegon_ac["unit_state"]["state"] = UNIT_STATES[fans.registers[0]]
swegon_ac["unit_state"]["ventilation_speed_state"] = VENTILATION_STATES[fans.registers[1]]
swegon_ac["fans"]["supply_fan_control"] = fans.registers[2]
swegon_ac["fans"]["exhaust_fan_control"] = fans.registers[3]
swegon_ac["fans"]["supply_fan_rpm"] = fans.registers[4] * 10
swegon_ac["fans"]["exhaust_fan_rpm"] = fans.registers[5] * 10

# parse model name
swegon_ac["model"]["name"] = ''.join(map(chr,model_name.registers))
swegon_ac["model"]["name"] = swegon_ac["model"]["name"].rstrip('\0')
swegon_ac["model"]["firmware_version"] = str(version_data.registers[0]) + "." + str(version_data.registers[1]) + "." + str(version_data.registers[2])
swegon_ac["model"]["parameter_version"] = str(version_data.registers[3]) + "." + str(version_data.registers[4])
swegon_ac["model"]["modbus_version"] = str(version_data.registers[5]) + "." + str(version_data.registers[6])

# send data to MQTT broker
if not args.printonly:
   mqtt_client = mqtt.Client("paho_mqtt_client")
   mqtt_client.connect(args.broker)
#   mqtt_client.loop_start()
   for key in swegon_ac["temperatures"]:
      mqtt_client.publish(args.topic + "/temperature/" + key, swegon_ac["temperatures"][key])
   for key in swegon_ac["unit_state"]:
      mqtt_client.publish(args.topic + "/unit_state/" + key, swegon_ac["unit_state"][key])
   for key in swegon_ac["air_quality"]:
      mqtt_client.publish(args.topic + "/air_quality/" + key, swegon_ac["air_quality"][key])
   for key in swegon_ac["fans"]:
      mqtt_client.publish(args.topic + "/fans/" + key, swegon_ac["fans"][key])
   for key in swegon_ac["model"]:
      mqtt_client.publish(args.topic + "/model/" + key, swegon_ac["model"][key])
   mqtt_client.loop(timeout=5.0)
else:
   print(json.dumps(swegon_ac, indent=3, sort_keys=True))


