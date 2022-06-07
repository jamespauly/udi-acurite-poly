from datetime import datetime, timezone

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

        for sensor in device['sensors']:
            if sensor['sensor_code'] == 'Temperature':
                temp = sensor['last_reading_value']
                temp_uom = sensor['chart_unit']
                self.setDriver('CLITEMP', temp, True)
                LOGGER.debug('Device Name: {}, Sensor Temp: {}{}'.format(deviceName, temp, temp_uom))
            if sensor['sensor_code'] == 'Humidity':
                humidity = sensor['last_reading_value']
                humidityUOM = sensor['chart_unit']
                self.setDriver('CLIHUM', humidity, True)
                LOGGER.debug('Device Name: {}, Sensor Humidity: {}{}'.format(deviceName, humidity, humidityUOM))
            if sensor['sensor_code'] == 'Dew Point':
                dewPoint = sensor['last_reading_value']
                dewPointUOM = sensor['chart_unit']
                self.setDriver('DEWPT', dewPoint, True)
                LOGGER.debug('Device Name: {}, Sensor Dew Point: {}{}'.format(deviceName, dewPoint, dewPointUOM))
            if sensor['sensor_code'] == 'Barometric Pressure':
                barometric = sensor['last_reading_value']
                barometricUOM = sensor['chart_unit']
                self.setDriver('BARPRES', barometric, True)
                LOGGER.debug('Device Name: {}, Sensor Dew Point: {}{}'.format(deviceName, barometric, barometricUOM))
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
