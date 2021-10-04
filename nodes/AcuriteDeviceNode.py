import udi_interface
from enums import DeviceStatus, BatteryLevel

LOGGER = udi_interface.LOGGER

class AcuriteDeviceNode(udi_interface.Node):
    def __init__(self, controller, primary, address, name, device):
        super(AcuriteDeviceNode, self).__init__(controller, primary, address, name)
        self.poly.subscribe(self.poly.START, self.start, address)
        self.poly.subscribe(self.poly.POLL, self.poll)
        self.device = device

    def start(self):
        self.query()
        
    def query(self):
        self.update()

    def poll(self, pollType):
        if 'shortPoll' in pollType:
            LOGGER.info('shortPoll (controller)')
            self.query()
        else:
            LOGGER.info('longPoll (controller)')
            pass
        
    def update(self):
        deviceName = self.device['name']
        deviceBattery = self.device['battery_level']
        deviceStatus = self.device['status_code']
        temp = ''
        humidity = ''
        dewPoint = ''
        barometric = ''

        for sensor in self.device['sensors']:
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
            self.setDriver('CLITEMP', temp)
            self.setDriver('CLIHUM', humidity)
            self.setDriver('BARPRES', barometric)
            self.setDriver('DEWPT', dewPoint)
            self.setDriver('GV1', BatteryLevel[deviceBattery].value)
            self.setDriver('GV2', DeviceStatus[deviceStatus].value)
        except Exception as ex:
            LOGGER.error('AcuriteDeviceNode - Error in update', ex)

    id = 'acuritedevice'
    
    drivers = [{'driver': 'CLITEMP', 'value': 0, 'uom': '17'},
                {'driver': 'CLIHUM', 'value': 0, 'uom': '22'},
               {'driver': 'BARPRES', 'value': 0, 'uom': '23'},
               {'driver': 'DEWPT', 'value': 0, 'uom': '17'},
               {'driver': 'GV1', 'value': 0, 'uom': '25'},
               {'driver': 'GV2', 'value': 0, 'uom': '25'}]
    
    commands = {'QUERY': query}
