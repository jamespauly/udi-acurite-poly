#!/usr/bin/env python
import sys
import time
import requests
import json

import udi_interface
from nodes import AcuriteDeviceNode

LOGGER = udi_interface.LOGGER
Custom = udi_interface.Custom

class AcuriteController(udi_interface.Node):
    def __init__(self, polyglot, primary, address, name):
        super(AcuriteController, self).__init__(polyglot, primary, address, name)

        self.poly = polyglot
        self.name = name
        self.primary = primary
        self.address = address
        self.configured = False
        self.node_added_count = 0

        self.Parameters = Custom(polyglot, 'customparams')

        self.poly.subscribe(self.poly.CONFIG, self.configHandler)
        self.poly.subscribe(self.poly.CUSTOMPARAMS, self.parameterHandler)
        self.poly.subscribe(self.poly.START, self.start, address)
        self.poly.subscribe(self.poly.POLL, self.poll)
        self.poly.subscribe(self.poly.ADDNODEDONE, self.nodeHandler)

        self.poly.ready()
        self.poly.addNode(self)

    def start(self):
        LOGGER.info('Started udi-acurite-poly NodeServer')
        self.discover()

    def configHandler(self, config):
        # at this time the interface should have all the nodes
        # included from the database.  Here's where we could
        # loop through those and create wrapped versions.
        # LOGGER.info('handle config = {}'.format(config))
        nodes = self.poly.getNodes()
        for n in nodes:
            LOGGER.info('Found node {} = {}'.format(n, nodes[n]))

    def nodeHandler(self, data):
        self.node_added_count += 1

    def parameterHandler(self, params):
        self.Parameters.load(params)

        userValid = False
        passwordValid = False

        if self.Parameters['acurite_user'] is not None and len(self.Parameters['acurite_user']) > 0:
            userValid = True
        else:
            LOGGER.error('Acurite User is Blank')

        if self.Parameters['acurite_password'] is not None and len(self.Parameters['acurite_password']) > 0:
            passwordValid = True
        else:
            LOGGER.error('Acurite Password is Blank')

        self.Notices.clear()

        if userValid and passwordValid:
            self.discover();
        else:
            if not userValid:
                self.Notices['user'] = 'Acurite User must be configured.'
            if not passwordValid:
                self.Notices['password'] = 'Acurite Password must be configured.'

    def poll(self, pollType):
        if 'shortPoll' in pollType:
            LOGGER.info('shortPoll (controller)')
            pass
        else:
            LOGGER.info('longPoll (controller)')
            self.query()

    def query(self):
        self.check_params()
        for node in self.nodes:
            self.nodes[node].reportDrivers()

    def discover(self, *args, **kwargs):
        try:
            self.discovery = True
            LOGGER.info("Starting Acurite Device Discovery")
            # If this is a re-discover than update=True
            #update = len(args) > 0
            loginHeaders = {'Content-Type':'application/json'}
            loginData = json.dumps({'email': self.Parameters['acurite_user'], 'password': self.Parameters['acurite_password']})
            loginResp = requests.post('https://marapi.myacurite.com/users/login', data=loginData,headers=loginHeaders)
            loginRespJO = loginResp.json()

            statusCode = loginResp.status_code
            if statusCode==200:
                self.setDriver('ST', 1)

            LOGGER.debug('Login HTTP Status Code: {}'.format(statusCode))
            accountId = loginRespJO['user']['account_users'][0]['account_id']
            # accountCity = loginRespJO['user']['account_users'][0]['account_id']['account']['city']
            # accountState = loginRespJO['user']['account_users'][0]['account_id']['account']['state_province']
            tokenId = loginRespJO['token_id']

            hubHeaders = {'Content-Type':'application/json','X-ONE-VUE-TOKEN': tokenId}
            hubResp = requests.get('https://marapi.myacurite.com/accounts/' + accountId + '/dashboard/hubs',headers=hubHeaders)
            hubsRespJO = hubResp.json()
            hubId = hubsRespJO['account_hubs'][0]['id']
            hubName = hubsRespJO['account_hubs'][0]['name']
            
            deviceHeaders = {'Content-Type':'application/json','X-ONE-VUE-TOKEN': tokenId}
            deviceResp = requests.get('https://marapi.myacurite.com/accounts/' + accountId + '/dashboard/hubs/' + hubId,headers=deviceHeaders)
            deviceRespJO = deviceResp.json()
            
            
            for device in deviceRespJO['devices']:
                if device is not None:
                    
                    deviceName = device['name']
                    deviceModel = device['model']
                    deviceBattery = device['battery_level']
                    devicePlacement = device['placement_code']
                    deviceStatus = device['status_code']
                    
                    temp = ''
                    humidity = ''
                    uom = ''
                    
                    for sensor in device['sensors']:
                        if sensor['sensor_code'] == 'Temperature':
                            temp = sensor['last_reading_value']
                            uom = sensor['chart_unit']
                        if sensor['sensor_code'] == 'Humidity':
                            humidity = sensor['last_reading_value']
                            uom = sensor['chart_unit']
                    
                    self.poly.addNode(AcuriteDeviceNode(self.poly, self.address, deviceName + '-' + deviceModel, deviceName, devicePlacement, deviceStatus, temp, humidity))

            #self.add_hub(hubId, hubName, tokenId, accountCity, accountState, accountId, update)
            #self.addNode(AcuriteMaster(self, accountId, accountId, accountId, "Acurite Access", accountCity, accountState, accountId, statusCode), update)

            
            self.discovery = False

            # for device in hubDetailRespJO['devices']:
            #     if device is not None:
            #         self.add_hub(device,update)
                    #self.addNode(AcuriteDetectedDevice(self, self.address, device['id'], device['name']))


                    # If we wanted to support other device types it would go here
        except Exception as ex:
            self.addNotice({'discovery_failed': 'Discovery failed please check logs for a more detailed error.'})
            LOGGER.error("Discovery failed with error {0}".format(ex))

        #self.addNode(TemplateNode(self, self.address, 'templateaddr', 'Template Node Name'))


    def delete(self):
        LOGGER.info('Delete Acurite Node Server')

    def stop(self):
        LOGGER.info('Stopping Acurite NodeServer.')

    id = 'acurite'
    commands = {'DISCOVER': discover}
    drivers = [{'driver': 'ST', 'value': 0, 'uom': 2}]