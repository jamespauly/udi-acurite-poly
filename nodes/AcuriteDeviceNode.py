from datetime import datetime, timezone

import udi_interface
from enums import DeviceStatus, BatteryLevel
from acurite import AcuriteManager

LOGGER = udi_interface.LOGGER
Custom = udi_interface.Custom

class AcuriteDeviceNode(udi_interface.Node):
    def __init__(self, controller, primary, address, name):
        super(AcuriteDeviceNode, self).__init__(controller, primary, address, name)
        self.controller = controller
        self.poly.subscribe(self.poly.START, self.start, address)
        self.poly.subscribe(self.poly.POLL, self.poll)

    def start(self):
        self.query()
        
    def query(self):
        acuriteManager = AcuriteManager(self.controller)
        acuriteManager.getHubDevices()

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
