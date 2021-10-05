from datetime import datetime, timezone

import udi_interface
import requests
import json

from enums import BatteryLevel, DeviceStatus
from nodes import AcuriteDeviceNode

LOGGER = udi_interface.LOGGER
Custom = udi_interface.Custom


class AcuriteManager():

    def __init__(self, user, password):
        self.user = user
        self.password = password

    def login(self):
        try:
            loginHeaders = {'Content-Type': 'application/json'}
            loginData = json.dumps(
                {'email': self.user, 'password': self.password})
            loginResp = requests.post('https://marapi.myacurite.com/users/login', data=loginData, headers=loginHeaders)
            loginRespJO = loginResp.json()

            statusCode = loginResp.status_code
            if statusCode != 200:
                return None, None

            LOGGER.info('Login HTTP Status Code: {}'.format(str(statusCode)))
            LOGGER.debug(json.dumps(loginRespJO))
            accountId = loginRespJO['user']['account_users'][0]['account_id']
            tokenId = loginRespJO['token_id']
        except Exception as e:
            LOGGER.error('Failed to Login to Acurite', e)
            return None, None
        return tokenId, accountId

    def getHubDevices(self):
        tokenId, accountId = self.login()
        if tokenId is not None and accountId is not None:
            try:
                hubHeaders = {'Content-Type': 'application/json', 'X-ONE-VUE-TOKEN': tokenId}
                hubResp = requests.get('https://marapi.myacurite.com/accounts/{}/dashboard/hubs'.format(str(accountId)),
                                       headers=hubHeaders)
                hubsRespJO = hubResp.json()
                hubId = hubsRespJO['account_hubs'][0]['id']

                deviceHeaders = {'Content-Type': 'application/json', 'X-ONE-VUE-TOKEN': tokenId}
                deviceResp = requests.get(
                    'https://marapi.myacurite.com/accounts/{}/dashboard/hubs/{}'.format(str(accountId), str(hubId)),
                    headers=deviceHeaders)
                deviceRespJO = deviceResp.json()
                statusCode = deviceResp.status_code
                if statusCode != 200:
                    return None
                LOGGER.info('Got Acurite Devices')
                return deviceRespJO
            except Exception as e:
                LOGGER.error('AcuriteManager - Error in update', e)
                return None
        else:
            return None

    def convert_timedelta_min(self, duration):
        days, seconds = duration.days, duration.seconds
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        # seconds = (seconds % 60)
        return (days * 24 * 60) + (hours * 60) + minutes
