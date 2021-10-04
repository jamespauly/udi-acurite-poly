from datetime import datetime, timezone

import udi_interface
import requests
import json

from enums import BatteryLevel, DeviceStatus
from nodes import AcuriteDeviceNode

LOGGER = udi_interface.LOGGER
Custom = udi_interface.Custom


class AcuriteManager():

    def __init__(self, polyglot):
        self.poly = polyglot
        self.Parameters = Custom(polyglot, 'customparams')

    def login(self):
        try:
            loginHeaders = {'Content-Type': 'application/json'}
            loginData = json.dumps(
                {'email': self.Parameters['acurite_user'], 'password': self.Parameters['acurite_password']})
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
                LOGGER.debug(json.dumps(deviceRespJO))
                LOGGER.info('Got Acurite Devices')

                for device in deviceRespJO['devices']:
                    if device is not None:
                        deviceId = device['id']
                        deviceName = device['name']
                        deviceBattery = self.device['battery_level']
                        deviceStatus = self.device['status_code']
                        deviceLastCheckIn = self.device['last_check_in_at']
                        temp = ''
                        humidity = ''
                        dewPoint = ''
                        barometric = ''

                        LOGGER.debug('Device Id: {}'.format(deviceId))
                        LOGGER.debug('Device Name: {}'.format(deviceName))

                        acuriteDeviceNode = self.poly.getNode(deviceId)

                        if acuriteDeviceNode is None:
                            self.poly.addNode(
                                AcuriteDeviceNode(self.poly, self.address, deviceId, deviceName))
                        else:
                            for sensor in self.device['sensors']:
                                if sensor['sensor_code'] == 'Temperature':
                                    temp = sensor['last_reading_value']
                                    temp_uom = sensor['chart_unit']
                                    LOGGER.debug(
                                        'Device Name: {}, Sensor Temp: {}{}'.format(deviceName, temp, temp_uom))
                                if sensor['sensor_code'] == 'Humidity':
                                    humidity = sensor['last_reading_value']
                                    humidityUOM = sensor['chart_unit']
                                    LOGGER.debug(
                                        'Device Name: {}, Sensor Humidity: {}{}'.format(deviceName, humidity,
                                                                                        humidityUOM))
                                if sensor['sensor_code'] == 'Dew Point':
                                    dewPoint = sensor['last_reading_value']
                                    dewPointUOM = sensor['chart_unit']
                                    LOGGER.debug(
                                        'Device Name: {}, Sensor Dew Point: {}{}'.format(deviceName, dewPoint,
                                                                                         dewPointUOM))
                                if sensor['sensor_code'] == 'Barometric Pressure':
                                    barometric = sensor['last_reading_value']
                                    barometricUOM = sensor['chart_unit']
                                    LOGGER.debug(
                                        'Device Name: {}, Sensor Dew Point: {}{}'.format(deviceName, barometric,
                                                                                         barometricUOM))

                                if deviceLastCheckIn is not None and deviceLastCheckIn != '':
                                    lastCheckInDateTime = datetime.fromisoformat(deviceLastCheckIn)
                                    currentDateTimeInUtc = datetime.now(timezone.utc)
                                    deltaDateTime = currentDateTimeInUtc - lastCheckInDateTime
                                    numOfMins = self.convert_timedelta_min(deltaDateTime)
                                    self.setDriver('GV3', numOfMins)
                                else:
                                    self.setDriver('GV3', 0)

                                acuriteDeviceNode.setDriver('CLITEMP', temp, True)
                                acuriteDeviceNode.setDriver('CLIHUM', humidity, True)
                                acuriteDeviceNode.setDriver('BARPRES', barometric, True)
                                acuriteDeviceNode.setDriver('DEWPT', dewPoint, True)
                                acuriteDeviceNode.setDriver('GV1', BatteryLevel[deviceBattery].value, True)
                                acuriteDeviceNode.setDriver('GV2', DeviceStatus[deviceStatus].value, True)

                                acuriteDeviceNode.reportDrivers()
            except Exception as e:
                LOGGER.error('AcuriteManager - Error in update', e)

        else:
            return None

    def convert_timedelta_min(self, duration):
        days, seconds = duration.days, duration.seconds
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        # seconds = (seconds % 60)
        return (days * 24 * 60) + (hours * 60) + minutes
