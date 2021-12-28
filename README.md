# swegon_mqtt
Small python script to read data from Swegon ventilation machine over Modbus and send it to MQTT broker.

Many things, such as login to MQTT are not implemented.

Description of the Modbus registers of the Swegon ventilation machines:
https://www.swegon.com/siteassets/_product-documents/home-ventilation/control-equipment/_fi/smartmodbusregisterfull.pdf

## Usage
```
usage: swegon_mqtt.py [-h] [-p] [-T] [-t TOPIC] [-b BROKER] [-m MODBUS_ADDRESS] [-d USBDEV] [-H TCP_HOST] [-P TCP_PORT] [-B BAUD_RATE]

optional arguments:
  -h, --help         show this help message and exit
  -p                 print the read values on screen only
  -T                 use Modbus TCP instead of serial
  -t TOPIC           MQTT topic prefix, default: swegon
  -b BROKER          MQTT broker address, default: 127.0.0.1
  -m MODBUS_ADDRESS  Modbus address of Swegon device, default: 16
  -d USBDEV          USB serial device to use, default: /dev/ttyUSB0
  -H TCP_HOST        Modbus TCP address, default: 127.0.0.1
  -P TCP_PORT        Modbus TCP port, default: 502
  -B BAUD_RATE       Serial baud rate, default: 38400
```

## Tested with

The script is tested with the following:
* Swegon Casa W3 + Swegon SMBG Modbus Gateway

## Examples

### MQTT broker

Data can be sent to an MQTT broker:

```
$ ./swegon_mqtt.py -m 16 -b 192.168.0.13 -t "mytest/swegon"
```

And while listening for the topic "mytest/swegon":

```
$ mosquitto_sub -v -h localhost -p 1883 -t 'mytest/swegon/#'
mytest/swegon/temperature/fresh_air 6.1
mytest/swegon/temperature/extract_air 21.4
mytest/swegon/temperature/external_fresh_air 6.1
mytest/swegon/temperature/room 21.4
mytest/swegon/temperature/water_radiator 0.0
mytest/swegon/temperature/supply_air_before_reheater 18.0
mytest/swegon/temperature/user_panel 23.4
mytest/swegon/temperature/waste_air 10.4
mytest/swegon/temperature/user_panel_2 0.0
mytest/swegon/temperature/supply_air 18.8
mytest/swegon/temperature/preheater 6.8
mytest/swegon/unit_state/manual_heat_exchanger_bypass 1
mytest/swegon/unit_state/external_boost_control_active 0
mytest/swegon/unit_state/automatic_heat_exchanger_bypass 0
mytest/swegon/unit_state/filter_guard_input_status 0
mytest/swegon/unit_state/defrost_exhaust_forcing 0
mytest/swegon/unit_state/external_away_control_active 0
mytest/swegon/unit_state/central_vacuum_cleaner_function_active 0
mytest/swegon/unit_state/state Normal
mytest/swegon/unit_state/ventilation_speed_state Home
mytest/swegon/unit_state/defrost_state 0
mytest/swegon/unit_state/hours_to_service 0
mytest/swegon/unit_state/summer_cooling_active 0
mytest/swegon/unit_state/hood_compensation_active 0
mytest/swegon/unit_state/preheater_active 0
mytest/swegon/unit_state/fireplace_function_active 0
mytest/swegon/unit_state/defrost_supply_forcing 0
mytest/swegon/air_quality/co2_filtered 0
mytest/swegon/air_quality/voc 0
mytest/swegon/air_quality/absolute_humidity 77.0
mytest/swegon/air_quality/relative_humidity 41
mytest/swegon/air_quality/co2_unfiltered 0
mytest/swegon/air_quality/absolute_humidity_setpoint 83.0
mytest/swegon/fans/exhaust_fan_control 63
mytest/swegon/fans/supply_fan_rpm 1930
mytest/swegon/fans/exhaust_fan_rpm 1940
mytest/swegon/fans/supply_fan_control 60
mytest/swegon/model/firmware_version 2.2.289
mytest/swegon/model/modbus_version 3.1
mytest/swegon/model/name W3 500W A
mytest/swegon/model/parameter_version 2.4
```

### No MQTT, only printout

The below example will connect to the Swegon Modbus Gateway over a serial (Modbus RTU) connection, assume Modbus address 16 and print out all data that is read.

```
$ ./swegon_mqtt.py -m 16 -p
{
   "air_quality": {
      "absolute_humidity": 76.0,
      "absolute_humidity_setpoint": 83.0,
      "co2_filtered": 0,
      "co2_unfiltered": 0,
      "relative_humidity": 41,
      "voc": 0
   },
   "fans": {
      "exhaust_fan_control": 63,
      "exhaust_fan_rpm": 1960,
      "supply_fan_control": 60,
      "supply_fan_rpm": 1900
   },
   "model": {
      "firmware_version": "2.2.289",
      "modbus_version": "3.1",
      "name": "W3 500W A",
      "parameter_version": "2.4"
   },
   "temperatures": {
      "external_fresh_air": 6.2,
      "extract_air": 21.4,
      "fresh_air": 6.2,
      "preheater": 6.9,
      "room": 21.4,
      "supply_air": 18.8,
      "supply_air_before_reheater": 18.0,
      "user_panel": 23.4,
      "user_panel_2": 0.0,
      "waste_air": 10.5,
      "water_radiator": 0.0
   },
   "unit_state": {
      "automatic_heat_exchanger_bypass": 0,
      "central_vacuum_cleaner_function_active": 0,
      "defrost_exhaust_forcing": 0,
      "defrost_state": 0,
      "defrost_supply_forcing": 0,
      "external_away_control_active": 0,
      "external_boost_control_active": 0,
      "filter_guard_input_status": 0,
      "fireplace_function_active": 0,
      "hood_compensation_active": 0,
      "hours_to_service": 0,
      "manual_heat_exchanger_bypass": 1,
      "preheater_active": 0,
      "state": "Normal",
      "summer_cooling_active": 0,
      "ventilation_speed_state": "Home"
   }
}
```

Hakusanat: Swegon ilmanvaihtokone iv-kone modbus kotiautomaatio
