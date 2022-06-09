from datetime import datetime, timezone

import udi_interface
from enums import DeviceStatus, BatteryLevel

LOGGER = udi_interface.LOGGER
Custom = udi_interface.Custom

class AcuriteLightningTNode(udi_interface.Node):
    def __init__(self, polyglot, primary, address, name, device):
        super(AcuriteLightningTNode, self).__init__(polyglot, primary, address, name)
        LOGGER.debug("Initialize AcuriteLightningTNode")
        self.poly.subscribe(self.poly.START, self.start, address)
        self.initDevice = device

    def start(self):
        LOGGER.debug("AcuriteLightningTNode - start")
        self.update(self.initDevice)

    def query(self):
        LOGGER.info('AcuriteLightningTNode - query')

    def convert_timedelta_min(self, duration):
        days, seconds = duration.days, duration.seconds
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        # seconds = (seconds % 60)
        return (days * 24 * 60) + (hours * 60) + minutes

    def update(self, device):
        LOGGER.debug("AcuriteLightningTNode - update")
        deviceName = device['name']
        deviceBattery = device['battery_level']
        deviceStatus = device['status_code']
        deviceLastCheckIn = device['last_check_in_at']
        self.setDriver('GV1', BatteryLevel[deviceBattery].value, True)
        self.setDriver('GV2', DeviceStatus[deviceStatus].value, True)

        feelsLike = 0
        heatIndex = 0

        for sensor in device['sensors']:
            if sensor['sensor_code'] == 'Temperature':
                temp = sensor['last_reading_value']
                temp_uom = sensor['chart_unit']
                self.setDriver('CLITEMP', temp, True)
                LOGGER.debug('Device Name: {}, Sensor Temp: {} {}'.format(deviceName, temp, temp_uom))
            elif sensor['sensor_code'] == 'Humidity':
                humidity = sensor['last_reading_value']
                humidityUOM = sensor['chart_unit']
                self.setDriver('CLIHUM', humidity, True)
                LOGGER.debug('Device Name: {}, Sensor Humidity: {} {}'.format(deviceName, humidity, humidityUOM))
            elif sensor['sensor_code'] == 'Dew Point':
                dewPoint = sensor['last_reading_value']
                dewPointUOM = sensor['chart_unit']
                self.setDriver('DEWPT', dewPoint, True)
                LOGGER.debug('Device Name: {}, Sensor Dew Point: {} {}'.format(deviceName, dewPoint, dewPointUOM))
            elif sensor['sensor_code'] == 'Barometric Pressure':
                barometric = sensor['last_reading_value']
                barometricUOM = sensor['chart_unit']
                self.setDriver('BARPRES', barometric, True)
                LOGGER.debug(
                    'Device Name: {}, Sensor {}: {} {}'.format(deviceName, sensor['sensor_code'], barometric,
                                                               barometricUOM))
            elif sensor['sensor_code'] == 'Feels Like':
                feelsLike = sensor['last_reading_value']
                feelsLikeUOM = sensor['chart_unit']
                #self.setDriver('GV4', feelsLike, True)
                LOGGER.debug(
                    'Device Name: {}, Sensor {}: {} {}'.format(deviceName, sensor['sensor_code'], feelsLike,
                                                               feelsLikeUOM))
            elif sensor['sensor_code'] == 'Heat Index':
                heatIndex = sensor['last_reading_value']
                heatIndexUOM = sensor['chart_unit']
                #self.setDriver('GV4', heatIndex, True)
                LOGGER.debug(
                    'Device Name: {}, Sensor {}: {} {}'.format(deviceName, sensor['sensor_code'], heatIndex,
                                                               heatIndexUOM))
        if int(feelsLike) > 0:
            self.setDriver('GV4', feelsLike, True)
        elif int(feelsLike) == 0 and int(heatIndex) > 0:
            self.setDriver('GV4', heatIndex, True)
        else:
            self.setDriver('GV4', temp, True)

        for sensor in device['wired_sensors']:
            if sensor['sensor_code'] == 'LightningStrikeCnt':
                lightningStrikeCnt = sensor['last_reading_value']
                lightningStrikeCntUOM = sensor['chart_unit']
                self.setDriver('GV5', lightningStrikeCnt, True)
                LOGGER.debug(
                    'Device Name: {}, Sensor {}: {} {}'.format(deviceName, sensor['sensor_code'], lightningStrikeCnt,
                                                               lightningStrikeCntUOM))
            elif sensor['sensor_code'] == 'LightningLastStrikeDist':
                lightningLastStrikeDist = sensor['last_reading_value']
                lightningLastStrikeDistUOM = sensor['chart_unit']
                self.setDriver('GV6', lightningLastStrikeDist, True)
                LOGGER.debug(
                    'Device Name: {}, Sensor {}: {} {}'.format(deviceName, sensor['sensor_code'],
                                                               lightningLastStrikeDist,
                                                               lightningLastStrikeDistUOM))
            elif sensor['sensor_code'] == 'LightningClosestStrikeDist':
                lightningClosestStrikeDist = sensor['last_reading_value']
                lightningClosestStrikeDistUOM = sensor['chart_unit']
                self.setDriver('GV8', lightningClosestStrikeDist, True)
                LOGGER.debug(
                    'Device Name: {}, Sensor {}: {} {}'.format(deviceName, sensor['sensor_code'],
                                                               lightningClosestStrikeDist,
                                                               lightningClosestStrikeDistUOM))

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
            LOGGER.error('AcuriteLightningTNode - Error in update', ex)

    id = 'acuritelightningt'

    drivers = [{'driver': 'CLITEMP', 'value': 0, 'uom': '17'},
               {'driver': 'GV4', 'value': 0, 'uom': '17'}, # Heat Index / Feels Like
               {'driver': 'CLIHUM', 'value': 0, 'uom': '22'},
               {'driver': 'BARPRES', 'value': 0, 'uom': '23'},
               {'driver': 'DEWPT', 'value': 0, 'uom': '17'},
               {'driver': 'GV1', 'value': 0, 'uom': '25'}, # device battery
               {'driver': 'GV2', 'value': 0, 'uom': '25'}, # device status
               {'driver': 'GV3', 'value': 0, 'uom': '45'}, # last checkin time
               {'driver': 'GV5', 'value': 0, 'uom': '0'}, # lightning Strike Cnt
               {'driver': 'GV6', 'value': 0, 'uom': '116'}, # lightning Last Strike Dist
               {'driver': 'GV8', 'value': 0, 'uom': '116'}] # lightning Closest Strike Dist
