from datetime import datetime, timezone
from jsonpath_ng import jsonpath
from jsonpath_ng.ext import parse

import udi_interface
from enums import DeviceStatus, BatteryLevel

LOGGER = udi_interface.LOGGER
Custom = udi_interface.Custom

class AcuriteDeviceNode(udi_interface.Node):
    def __init__(self, polyglot, primary, address, name, device):
        super(AcuriteDeviceNode, self).__init__(polyglot, primary, address, name)
        LOGGER.debug("Initialize AcuriteDeviceNode")
        self.poly.subscribe(self.poly.START, self.start, address)
        self.initDevice = device

    def start(self):
        LOGGER.debug("AcuriteDeviceNode - start")
        self.update(self.initDevice)

    def query(self):
        LOGGER.debug('AcuriteDeviceNode - query')

    def convert_timedelta_min(self, duration):
        days, seconds = duration.days, duration.seconds
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        # seconds = (seconds % 60)
        return (days * 24 * 60) + (hours * 60) + minutes

    def update(self, device):
        deviceName = device['name']
        deviceBattery = device['battery_level']
        deviceStatus = device['status_code']
        deviceLastCheckIn = device['last_check_in_at']
        self.setDriver('GV1', BatteryLevel[deviceBattery].value, True)
        self.setDriver('GV2', DeviceStatus[deviceStatus].value, True)

        jsonpath_temperature = parse("$.sensors[?sensor_code='Temperature'].last_reading_value")
        temperature_list = jsonpath_temperature.find(device)
        jsonpath_temperature_uom = parse("$.sensors[?sensor_code='Temperature'].chart_unit")
        temperature_list_uom = jsonpath_temperature_uom.find(device)
        self.setDriver('CLITEMP', temperature_list[0].value, True)
        LOGGER.debug('Device Name: {}, Sensor Temp: {} {}'.format(deviceName, temperature_list[0].value, temperature_list_uom[0].value))

        jsonpath_humidity = parse("$.sensors[?sensor_code='Humidity'].last_reading_value")
        humidity_list = jsonpath_humidity.find(device)
        jsonpath_humidity_uom = parse("$.sensors[?sensor_code='Humidity'].chart_unit")
        humidity_list_uom = jsonpath_humidity_uom.find(device)
        self.setDriver('CLIHUM', humidity_list[0].value, True)
        LOGGER.debug('Device Name: {}, Sensor Humidity: {} {}'.format(deviceName, humidity_list[0].value,
                                                                  humidity_list_uom[0].value))

        jsonpath_dew_point = parse("$.sensors[?sensor_code='Dew Point'].last_reading_value")
        dew_point_list = jsonpath_dew_point.find(device)
        jsonpath_dew_point_uom = parse("$.sensors[?sensor_code='Dew Point'].chart_unit")
        dew_point_list_uom = jsonpath_dew_point_uom.find(device)
        self.setDriver('DEWPT', dew_point_list[0].value, True)
        LOGGER.debug('Device Name: {}, Sensor Dew Point: {} {}'.format(deviceName, dew_point_list[0].value,
                                                                   dew_point_list_uom[0].value))

        jsonpath_barometric_pressure = parse("$.sensors[?sensor_code='Barometric Pressure'].last_reading_value")
        barometric_pressure_list = jsonpath_barometric_pressure.find(device)
        jsonpath_barometric_pressure_uom = parse("$.sensors[?sensor_code='Barometric Pressure'].chart_unit")
        barometric_pressure_list_uom = jsonpath_barometric_pressure_uom.find(device)
        self.setDriver('BARPRES', barometric_pressure_list[0].value, True)
        LOGGER.debug(
        'Device Name: {}, Sensor Barometric Pressure: {} {}'.format(deviceName, barometric_pressure_list[0].value,
                                                                    barometric_pressure_list_uom[0].value))

        try:
            if deviceLastCheckIn is not None and deviceLastCheckIn != '':
                lastCheckInDateTime = datetime.fromisoformat(deviceLastCheckIn)
                currentDateTimeInUtc = datetime.now(timezone.utc)
                deltaDateTime = currentDateTimeInUtc - lastCheckInDateTime
                numOfMins = self.convert_timedelta_min(deltaDateTime)
                self.setDriver('GV3', numOfMins, True)
            else:
                self.setDriver('GV3', 0, True)
        except Exception as ex:
            LOGGER.error('AcuriteDeviceNode - Error in update', ex)

    id = 'acuritedevice'

    drivers = [{'driver': 'CLITEMP', 'value': 0, 'uom': '17'},
               {'driver': 'CLIHUM', 'value': 0, 'uom': '22'},
               {'driver': 'BARPRES', 'value': 0, 'uom': '23'},
               {'driver': 'DEWPT', 'value': 0, 'uom': '17'},
               {'driver': 'GV1', 'value': 0, 'uom': '25'},
               {'driver': 'GV2', 'value': 0, 'uom': '25'},
               {'driver': 'GV3', 'value': 0, 'uom': '45'}]
