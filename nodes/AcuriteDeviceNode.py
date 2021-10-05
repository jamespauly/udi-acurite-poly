from datetime import datetime, timezone

import udi_interface
from enums import DeviceStatus, BatteryLevel
from acurite import AcuriteManager

LOGGER = udi_interface.LOGGER
Custom = udi_interface.Custom

class AcuriteDeviceNode(udi_interface.Node):
    def __init__(self, polyglot, primary, address, name, device):
        super(AcuriteDeviceNode, self).__init__(polyglot, primary, address, name)
        self.poly.subscribe(self.poly.START, self.start, address)
        self.poly.subscribe(self.poly.POLL, self.poll)
        self.poly.subscribe(self.poly.CUSTOMPARAMS, self.parameterHandler)

        self.initDevice = device
        self.Parameters = Custom(polyglot, 'customparams')

    def start(self):
        self.update(self.initDevice)

    def parameterHandler(self, params):
        self.Parameters.load(params)
        
    def query(self):
        # acuriteUser = self.Parameters['acurite_user']
        # acuritePassword = self.Parameters['acurite_password']
        acuriteUser = 'jgpaul16@gmail.com'
        acuritePassword = 'zcKCh9@G4IZB'

        LOGGER.info('From node query: ' + acuriteUser)

        # acuriteManager = AcuriteManager(acuriteUser, acuritePassword)
        # deviceRespJO = acuriteManager.getHubDevices()
        #
        # for device in deviceRespJO['devices']:
        #     if device is not None:
        #         deviceId = device['id']
        #         deviceName = device['name']
        #
        #         LOGGER.debug('Device Id: {}'.format(deviceId))
        #         LOGGER.debug('Device Name: {}'.format(deviceName))
        #
        #         if self.poly.getNode(deviceId) is None:
        #             LOGGER.info('Node {} does not exists, skipping please run discover from controller'.format(deviceId))
        #         else:
        #             self.update(device)

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
        temp = ''
        humidity = ''
        dewPoint = ''
        barometric = ''

        for sensor in device['sensors']:
            if sensor['sensor_code'] == 'Temperature':
                temp = sensor['last_reading_value']
                temp_uom = sensor['chart_unit']
                LOGGER.debug('Device Name: {}, Sensor Temp: {}{}'.format(deviceName, temp, temp_uom))
            if sensor['sensor_code'] == 'Humidity':
                humidity = sensor['last_reading_value']
                humidityUOM = sensor['chart_unit']
                LOGGER.debug('Device Name: {}, Sensor Humidity: {}{}'.format(deviceName, humidity, humidityUOM))
            if sensor['sensor_code'] == 'Dew Point':
                dewPoint = sensor['last_reading_value']
                dewPointUOM = sensor['chart_unit']
                LOGGER.debug('Device Name: {}, Sensor Dew Point: {}{}'.format(deviceName, dewPoint, dewPointUOM))
            if sensor['sensor_code'] == 'Barometric Pressure':
                barometric = sensor['last_reading_value']
                barometricUOM = sensor['chart_unit']
                LOGGER.debug('Device Name: {}, Sensor Dew Point: {}{}'.format(deviceName, barometric, barometricUOM))

        try:
            if deviceLastCheckIn is not None and deviceLastCheckIn != '':
                lastCheckInDateTime = datetime.fromisoformat(deviceLastCheckIn)
                currentDateTimeInUtc = datetime.now(timezone.utc)
                deltaDateTime = currentDateTimeInUtc - lastCheckInDateTime
                numOfMins = self.convert_timedelta_min(deltaDateTime)
                self.setDriver('GV3', numOfMins)
            else:
                self.setDriver('GV3', 0)

            self.setDriver('CLITEMP', temp)
            self.setDriver('CLIHUM', humidity)
            self.setDriver('BARPRES', barometric)
            self.setDriver('DEWPT', dewPoint)
            self.setDriver('GV1', BatteryLevel[deviceBattery].value)
            self.setDriver('GV2', DeviceStatus[deviceStatus].value)

            self.reportDrivers()
        except Exception as ex:
            LOGGER.error('AcuriteDeviceNode - Error in update', ex)


    def poll(self, pollType):
        if 'shortPoll' in pollType:
            LOGGER.info('shortPoll (controller)')
            self.query()
        else:
            LOGGER.info('longPoll (controller)')
            pass


    id = 'acuritedevice'
    
    drivers = [{'driver': 'CLITEMP', 'value': 0, 'uom': '17'},
                {'driver': 'CLIHUM', 'value': 0, 'uom': '22'},
               {'driver': 'BARPRES', 'value': 0, 'uom': '23'},
               {'driver': 'DEWPT', 'value': 0, 'uom': '17'},
               {'driver': 'GV1', 'value': 0, 'uom': '25'},
               {'driver': 'GV2', 'value': 0, 'uom': '25'},
               {'driver': 'GV3', 'value': 0, 'uom': '45'}]
    
    commands = {'QUERY': query}
