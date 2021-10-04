#!/usr/bin/env python
import requests
import json

import udi_interface
from nodes import AcuriteDeviceNode
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
        self.node_added_count = 0

        self.Notices = Custom(polyglot, 'notices')
        self.Parameters = Custom(polyglot, 'customparams')

        # self.poly.subscribe(self.poly.CONFIG, self.configHandler)
        self.poly.subscribe(self.poly.CUSTOMPARAMS, self.parameterHandler)
        self.poly.subscribe(self.poly.START, self.start, address)
        self.poly.subscribe(self.poly.POLL, self.poll)
        # self.poly.subscribe(self.poly.ADDNODEDONE, self.nodeHandler)

        self.poly.ready()
        self.poly.addNode(self)

    def start(self):
        LOGGER.info('Started udi-acurite-poly NodeServer')
        self.query()
    #
    # def configHandler(self, config):
        # at this time the interface should have all the nodes
        # included from the database.  Here's where we could
        # loop through those and create wrapped versions.
        # LOGGER.info('handle config = {}'.format(config))
        # nodes = self.poly.getNodes()
        # for n in nodes:
        #     LOGGER.info('Found node {} = {}'.format(n, nodes[n]))

    # def nodeHandler(self, data):
    #     self.node_added_count += 1

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
            self.discover();
            for node in self.poly.nodes:
                if self.poly.nodes[node] is not self:
                    self.poly.nodes[node].query()
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
            self.poly.nodes[node].query()

    def discover(self, *args, **kwargs):
        try:
            acuriteManager = AcuriteManager(self.poly)
            acuriteManager.getHubDevices()

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
