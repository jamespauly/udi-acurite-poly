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

        self.Notices = Custom(polyglot, 'notices')
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
        # self.discover()

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
        for node in self.poly.nodes:
            self.poly.nodes[node].reportDrivers()

    def discover(self, *args, **kwargs):
        try:
            self.discovery = True
            LOGGER.info("Starting Acurite Device Discovery")
            LOGGER.info('acurite_user: {}'.format(self.Parameters['acurite_user']))

            loginHeaders = {'Content-Type': 'application/json'}
            loginData = json.dumps(
                {'email': self.Parameters['acurite_user'], 'password': self.Parameters['acurite_password']})
            loginResp = requests.post('https://marapi.myacurite.com/users/login', data=loginData, headers=loginHeaders)
            loginRespJO = loginResp.json()

            statusCode = loginResp.status_code
            if statusCode != 200:
                return

            LOGGER.info('Login HTTP Status Code: {}'.format(str(statusCode)))
            LOGGER.debug(json.dumps(loginRespJO))
            accountId = loginRespJO['user']['account_users'][0]['account_id']
            tokenId = loginRespJO['token_id']

            hubHeaders = {'Content-Type': 'application/json', 'X-ONE-VUE-TOKEN': tokenId}
            hubResp = requests.get('https://marapi.myacurite.com/accounts/{}/dashboard/hubs'.format(str(accountId)),
                                   headers=hubHeaders)
            hubsRespJO = hubResp.json()
            hubId = hubsRespJO['account_hubs'][0]['id']
            hubName = hubsRespJO['account_hubs'][0]['name']

            deviceHeaders = {'Content-Type': 'application/json', 'X-ONE-VUE-TOKEN': tokenId}
            deviceResp = requests.get(
                'https://marapi.myacurite.com/accounts/{}/dashboard/hubs/{}'.format(str(accountId), str(hubId)),
                headers=deviceHeaders)
            deviceRespJO = deviceResp.json()
            LOGGER.debug(json.dumps(deviceRespJO))

            LOGGER.info('Got Acurite Devices')

            for device in deviceRespJO['devices']:
                if device is not None:
                    deviceId = device['id']
                    deviceName = device['name']

                    LOGGER.debug('Device Id: {}'.format(deviceId))
                    LOGGER.debug('Device Name: {}'.format(deviceName))

                    self.poly.addNode(
                        AcuriteDeviceNode(self.poly, self.address, deviceId, deviceName,
                                          device))

        except Exception as ex:
            LOGGER.error("AcuriteController - Discovery failed with error", ex)

    def delete(self):
        LOGGER.info('Deleting Acurite Node Server')

    def stop(self):
        LOGGER.info('Stopping Acurite NodeServer.')

    def remove_notices_all(self, command):
        self.Notices.clear()

    id = 'acurite'
    commands = {'REMOVE_NOTICES_ALL': remove_notices_all, 'DISCOVER': discover}
    drivers = [{'driver': 'ST', 'value': 1, 'uom': 2}]
