# !/usr/bin/env python
import time
import json

import udi_interface

import nodes
from acurite import AcuriteManager

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
        self.nodesAddedCount = 0
        self.deviceCount = 0

        self.Notices = Custom(polyglot, 'notices')
        self.Parameters = Custom(polyglot, 'customparams')

        self.poly.subscribe(self.poly.CUSTOMPARAMS, self.parameterHandler)
        self.poly.subscribe(self.poly.START, self.start, address)
        self.poly.subscribe(self.poly.POLL, self.poll)
        self.poly.subscribe(self.poly.ADDNODEDONE, self.nodeHandler)

        self.poly.ready()
        self.poly.addNode(self)

    def start(self):
        self.poly.updateProfile()
        self.poly.setCustomParamsDoc()
        self.query()
        LOGGER.info('Started udi-acurite-poly NodeServer')

    def nodeHandler(self, data):
        self.nodesAddedCount += 1

    def parameterHandler(self, params):
        self.Parameters.load(params)

        userValid = False
        passwordValid = False

        acuriteUser = self.Parameters['acurite_user']
        acuritePassword = self.Parameters['acurite_password']

        if acuriteUser is not None and len(acuriteUser) > 0:
            userValid = True
        else:
            LOGGER.error('Acurite User is Blank')

        if acuritePassword is not None and len(acuritePassword) > 0:
            passwordValid = True
        else:
            LOGGER.error('Acurite Password is Blank')

        self.Notices.clear()

        if userValid and passwordValid:
            self.configured = True
            self.query()
        else:
            if not userValid:
                self.Notices['user'] = 'Acurite User must be configured.'
            if not passwordValid:
                self.Notices['password'] = 'Acurite Password must be configured.'

    def poll(self, pollType):
        if 'shortPoll' in pollType:
            LOGGER.info('shortPoll (controller)')
            self.query()
        else:
            LOGGER.info('longPoll (controller)')
            pass

    def query(self, command=None):
        self.discover()
        LOGGER.info('AcuriteController - query')

    def discover(self, *args, **kwargs):
        acuriteUser = self.Parameters['acurite_user']
        acuritePassword = self.Parameters['acurite_password']
        try:
            LOGGER.info("Starting Acurite Device Discovery")
            LOGGER.info('acurite_user: {}'.format(self.Parameters['acurite_user']))

            acuriteManager = AcuriteManager(acuriteUser, acuritePassword)
            deviceRespJO = acuriteManager.getHubDevices()

            if deviceRespJO is None:
                LOGGER.error('No Response Returned from Acurite')
                return

            for device in deviceRespJO['devices']:
                if device is not None:
                    deviceId = device['id']
                    deviceName = device['name']
                    deviceModel = device['model_code']

                    LOGGER.debug('Device Id: {}'.format(deviceId))
                    LOGGER.debug('Device Name: {}'.format(deviceName))
                    LOGGER.debug('Device JSON: {}'.format(json.dumps(device)))
                    LOGGER.debug('Controller Address: {}'.format(self.address))

                    deviceNode = self.poly.getNode(deviceId)

                    if deviceNode is None:
                        if deviceModel == 'Atlas':
                            LOGGER.debug("Creating AcuriteAtlasNode")
                            try:
                                atlas_node = nodes.AcuriteAtlasNode(self.poly, self.address, deviceId, deviceName,
                                                              device)
                                self.poly.addNode(atlas_node)
                            except Exception as ex:
                                LOGGER.error("Error Loading AcuriteAtlasNode", ex)
                                continue
                        elif deviceModel == 'LightningT':
                            LOGGER.debug("Creating AcuriteLightningTNode")
                            try:
                                lightningt_node = nodes.AcuriteLightningTNode(self.poly, self.address, deviceId, deviceName,
                                                                    device)
                                self.poly.addNode(lightningt_node)
                            except Exception as ex:
                                LOGGER.error("Error Loading AcuriteLightningTNode", ex)
                                continue
                        else:
                            LOGGER.debug("Creating AcuriteDeviceNode")
                            try:
                                device_node = nodes.AcuriteDeviceNode(self.poly, self.address, deviceId, deviceName,
                                                               device)
                                self.poly.addNode(device_node)
                            except Exception as ex:
                                LOGGER.error("Error Loading AcuriteDeviceNode", ex)
                                continue

                            self.deviceCount += 1
                    else:
                        LOGGER.info('Node {} already exists, skipping'.format(deviceId))
                        deviceNode.update(device)
            infinitePreventor = 30
            loopCount = 0
            # Wait for nodes to be created
            while self.nodesAddedCount < self.deviceCount:
                time.sleep(2)
                loopCount += 1
                if infinitePreventor == loopCount:
                    LOGGER.error("AcuriteController - Reached In Nodes Added Successful vs Nodes trying to be added. "
                                 "Nodes Added: {} ,Num of Devices trying to be added: {}".format(self.nodesAddedCount,
                                                                                                 self.deviceCount))

        except Exception as ex:
            LOGGER.error("AcuriteController - Discovery failed with error", ex)

    def delete(self):
        LOGGER.info('Deleting Acurite Node Server')

    def stop(self):
        LOGGER.info('Stopping Acurite NodeServer.')

    def remove_notices_all(self, command):
        self.Notices.clear()

    id = 'acurite'
    commands = {'QUERY': query, 'REMOVE_NOTICES_ALL': remove_notices_all, 'DISCOVER': discover}
    drivers = [{'driver': 'ST', 'value': 1, 'uom': 2}]
