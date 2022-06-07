from datetime import datetime, timezone

import udi_interface
from enums import DeviceStatus, BatteryLevel

LOGGER = udi_interface.LOGGER
Custom = udi_interface.Custom

class AcuriteAtlasNode(udi_interface.Node):
    def __init__(self, polyglot, primary, address, name, device):
        super(AcuriteAtlasNode, self).__init__(polyglot, primary, address, name)
        LOGGER.debug("Initialize AcuriteAtlasNode")
        self.poly.subscribe(self.poly.START, self.start, address)
        self.initDevice = device

    def start(self):
        LOGGER.debug("AcuriteAtlasNode - start")
        self.update(self.initDevice)

    def query(self):
        LOGGER.info('AcuriteAtlasNode - query')

    def convert_timedelta_min(self, duration):
        days, seconds = duration.days, duration.seconds
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        # seconds = (seconds % 60)
        return (days * 24 * 60) + (hours * 60) + minutes

    def update(self, device):
        LOGGER.debug("AcuriteAtlasNode - update")
        deviceName = device['name']
        deviceBattery = device['battery_level']
        deviceStatus = device['status_code']
        deviceLastCheckIn = device['last_check_in_at']
        self.setDriver('GV1', BatteryLevel[deviceBattery].value, True)
        self.setDriver('GV2', DeviceStatus[deviceStatus].value, True)

        feelsLike = 0

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
            elif sensor['sensor_code'] == 'Wind Direction':
                windDirection = sensor['last_reading_value']
                windDirectionUOM = 'degrees'
                self.setDriver('WINDDIR', windDirection, True)
                LOGGER.debug(
                    'Device Name: {}, Sensor {}: {} {}'.format(deviceName, sensor['sensor_code'], windDirection,
                                                               windDirectionUOM))
            elif sensor['sensor_code'] == 'Wind Speed':
                windSpeed = sensor['last_reading_value']
                windSpeedUOM = sensor['chart_unit']
                self.setDriver('SPEED', windSpeed, True)
                LOGGER.debug(
                    'Device Name: {}, Sensor {}: {} {}'.format(deviceName, sensor['sensor_code'], windSpeed,
                                                               windSpeedUOM))
            elif sensor['sensor_code'] == 'Feels Like':
                feelsLike = sensor['last_reading_value']
                feelsLikeUOM = sensor['chart_unit']
                self.setDriver('GV4', feelsLike, True)
                LOGGER.debug(
                    'Device Name: {}, Sensor {}: {} {}'.format(deviceName, sensor['sensor_code'], feelsLike,
                                                               feelsLikeUOM))
            elif sensor['sensor_code'] == 'Rainfall':
                rainfall = sensor['last_reading_value']
                rainfallUOM = sensor['chart_unit']
                self.setDriver('RAINRT', rainfall, True)
                LOGGER.debug(
                    'Device Name: {}, Sensor {}: {} {}'.format(deviceName, sensor['sensor_code'], rainfall,
                                                               rainfallUOM))
            elif sensor['sensor_code'] == 'LightIntensity':
                lightIntensity = sensor['last_reading_value']
                lightIntensityUOM = sensor['chart_unit']
                self.setDriver('LUMIN', lightIntensity, True)
                LOGGER.debug(
                    'Device Name: {}, Sensor {}: {} {}'.format(deviceName, sensor['sensor_code'], lightIntensity,
                                                               lightIntensityUOM))
            elif sensor['sensor_code'] == 'UVIndex':
                uVIndex = sensor['last_reading_value']
                uVIndexUOM = sensor['chart_unit']
                self.setDriver('UV', uVIndex, True)
                LOGGER.debug(
                    'Device Name: {}, Sensor {}: {} {}'.format(deviceName, sensor['sensor_code'], uVIndex, uVIndexUOM))

            elif sensor['sensor_code'] == 'WindSpeedAvg':
                windSpeedAvg = sensor['last_reading_value']
                windSpeedAvgUOM = sensor['chart_unit']
                self.setDriver('GV7', windSpeedAvg, True)
                LOGGER.debug(
                    'Device Name: {}, Sensor {}: {} {}'.format(deviceName, sensor['sensor_code'], windSpeedAvg,
                                                               windSpeedAvgUOM))
        if feelsLike == 0:
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
            LOGGER.error('AcuriteAtlasNode - Error in update', ex)

    id = 'acuriteatlas'

    drivers = [{'driver': 'CLITEMP', 'value': 0, 'uom': '17'},
               {'driver': 'GV4', 'value': 0, 'uom': '17'},
               {'driver': 'CLIHUM', 'value': 0, 'uom': '22'},
               {'driver': 'BARPRES', 'value': 0, 'uom': '23'},
               {'driver': 'DEWPT', 'value': 0, 'uom': '17'},
               {'driver': 'GV1', 'value': 0, 'uom': '25'},
               {'driver': 'GV2', 'value': 0, 'uom': '25'},
               {'driver': 'GV3', 'value': 0, 'uom': '45'},
               {'driver': 'WINDDIR', 'value': 0, 'uom': '14'},
               {'driver': 'SPEED', 'value': 0, 'uom': '48'},
               {'driver': 'RAINRT', 'value': 0, 'uom': '120'},
               {'driver': 'LUMIN', 'value': 0, 'uom': '36'},
               {'driver': 'UV', 'value': 0, 'uom': '71'},
               {'driver': 'GV5', 'value': 0, 'uom': '0'},
               {'driver': 'GV6', 'value': 0, 'uom': '116'},
               {'driver': 'GV7', 'value': 0, 'uom': '48'}]