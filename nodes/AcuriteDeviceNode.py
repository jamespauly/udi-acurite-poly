import udi_interface

LOGGER = udi_interface.LOGGER

class AcuriteDeviceNode(udi_interface.Node):
    def __init__(self, controller, primary, address, name, devicePlacement, deviceStatus, temp, humidity):
        super(AcuriteDeviceNode, self).__init__(controller, primary, address, name)
        self.devicePlacement = devicePlacement
        self.temp = temp
        self.humidity = humidity
        self.deviceStatus = deviceStatus

    def start(self):
        self.query()
        
    def query(self, command=None):
        self.update()
        
    def update(self):
        try:
            self.setDriver('GV1', self.temp)
            self.setDriver('GV2', self.humidity)
        except Exception as ex:
            LOGGER.error('AcuriteDevice Class Error in update', ex)

    id = 'acuritedevice'
    
    drivers = [{'driver': 'GV1', 'value': 0, 'uom': '17'},
                {'driver': 'GV2', 'value': 0, 'uom': '22'}]
    
    commands = {'QUERY': query}
