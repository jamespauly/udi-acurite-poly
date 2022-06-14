from datetime import datetime, timezone
from jsonpath_ng import jsonpath
from jsonpath_ng.ext import parse

import udi_interface
from enums import DeviceStatus, BatteryLevel

LOGGER = udi_interface.LOGGER
Custom = udi_interface.Custom

class AcuriteLightningTNode(udi_interface.Node):
    def __init__(self, polyglot, primary, address, name, device):
        super(AcuriteLightningTNode, self).__init__(polyglot, primary, address, name)
        LOGGER.debug("Initialize AcuriteLightningTNode")
        self.poly.subscribe(self.poly.START, self.start, address)
        self.initDevice = device

    def start(self):
        LOGGER.debug("AcuriteLightningTNode - start")
        self.update(self.initDevice)

    def query(self):
        LOGGER.info('AcuriteLightningTNode - query')

    def convert_timedelta_min(self, duration):
        days, seconds = duration.days, duration.seconds
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        # seconds = (seconds % 60)
        return (days * 24 * 60) + (hours * 60) + minutes

    def update(self, device):
        LOGGER.debug("AcuriteLightningTNode - update")
        deviceName = device['name']
        deviceBattery = device['battery_level']
        deviceStatus = device['status_code']
        deviceLastCheckIn = device['last_check_in_at']
        self.setDriver('GV1', BatteryLevel[deviceBattery].value, True)
        self.setDriver('GV2', DeviceStatus[deviceStatus].value, True)

        jsonpath_temperature = parse("$.sensors[?sensor_code='Temperature'].last_reading_value")
        temperature_list = jsonpath_temperature.find(device)
        jsonpath_temperature_uom = parse("$.sensors[?sensor_code='Temperature'].chart_unit")
        temperature_list_uom = jsonpath_temperature_uom.find(device)
        self.setDriver('CLITEMP', temperature_list[0].value, True)
        LOGGER.debug('Device Name: {}, Sensor Temp: {} {}'.format(deviceName, temperature_list[0].value,
                                                                  temperature_list_uom[0].value))

        jsonpath_humidity = parse("$.sensors[?sensor_code='Humidity'].last_reading_value")
        humidity_list = jsonpath_humidity.find(device)
        jsonpath_humidity_uom = parse("$.sensors[?sensor_code='Humidity'].chart_unit")
        humidity_list_uom = jsonpath_humidity_uom.find(device)
        self.setDriver('CLIHUM', humidity_list[0].value, True)
        LOGGER.debug('Device Name: {}, Sensor Humidity: {} {}'.format(deviceName, humidity_list[0].value,
                                                                      humidity_list_uom[0].value))

        jsonpath_dew_point = parse("$.sensors[?sensor_code='Dew Point'].last_reading_value")
        dew_point_list = jsonpath_dew_point.find(device)
        jsonpath_dew_point_uom = parse("$.sensors[?sensor_code='Dew Point'].chart_unit")
        dew_point_list_uom = jsonpath_dew_point_uom.find(device)
        self.setDriver('DEWPT', dew_point_list[0].value, True)
        LOGGER.debug('Device Name: {}, Sensor Dew Point: {} {}'.format(deviceName, dew_point_list[0].value,
                                                                       dew_point_list_uom[0].value))

        jsonpath_barometric_pressure = parse("$.sensors[?sensor_code='Barometric Pressure'].last_reading_value")
        barometric_pressure_list = jsonpath_barometric_pressure.find(device)
        jsonpath_barometric_pressure_uom = parse("$.sensors[?sensor_code='Barometric Pressure'].chart_unit")
        barometric_pressure_list_uom = jsonpath_barometric_pressure_uom.find(device)
        self.setDriver('BARPRES', barometric_pressure_list[0].value, True)
        LOGGER.debug(
            'Device Name: {}, Sensor Barometric Pressure: {} {}'.format(deviceName,
                                                                        barometric_pressure_list[0].value,
                                                                        barometric_pressure_list_uom[0].value))

        jsonpath_feels_like = parse("$.sensors[?sensor_code='Feels Like'].last_reading_value")
        feels_like_list = jsonpath_feels_like.find(device)

        jsonpath_heat_index = parse("$.sensors[?sensor_code='Heat Index'].last_reading_value")
        heat_index_list = jsonpath_heat_index.find(device)

        if len(feels_like_list) > 0 and int(feels_like_list[0].value) > 0:
            jsonpath_feels_like_uom = parse("$.sensors[?sensor_code='Feels Like'].chart_unit")
            feels_like_list_uom = jsonpath_feels_like_uom.find(device)
            self.setDriver('GV4', feels_like_list[0].value, True)
            LOGGER.debug('Device Name: {}, Sensor Feels Like: {} {}'.format(deviceName, feels_like_list[0].value,
                                                                            feels_like_list_uom[0].value))
        elif len(heat_index_list) > 0 and int(heat_index_list[0].value) > 0:
            jsonpath_heat_index_uom = parse("$.sensors[?sensor_code='Heat Index'].chart_unit")
            heat_index_list_uom = jsonpath_heat_index_uom.find(device)
            self.setDriver('GV4', heat_index_list[0].value, True)
            LOGGER.debug('Device Name: {}, Sensor Heat Index: {} {}'.format(deviceName, heat_index_list[0].value,
                                                                            heat_index_list_uom[0].value))
        else:
            self.setDriver('GV4', 0, True)

        jsonpath_lightningStrikeCnt = parse("$.wired_sensors[?sensor_code='LightningStrikeCnt'].last_reading_value")
        lightningStrikeCnt_list = jsonpath_lightningStrikeCnt.find(device)

        if len(lightningStrikeCnt_list) > 0 and int(lightningStrikeCnt_list[0].value) > 0:
            jsonpath_lightningStrikeCnt_uom = parse("$.sensors[?sensor_code='LightningStrikeCnt'].chart_unit")
            lightningStrikeCnt_list_uom = jsonpath_lightningStrikeCnt_uom.find(device)
            self.setDriver('GV5', lightningStrikeCnt_list[0].value, True)
            LOGGER.debug(
                'Device Name: {}, Sensor Lightning Strike Count: {} {}'.format(deviceName,
                                                                               lightningStrikeCnt_list[0].value,
                                                                               lightningStrikeCnt_list_uom[0].value))

            jsonpath_lightningLastStrikeDist = parse(
                "$.sensors[?sensor_code='LightningLastStrikeDist'].last_reading_value")
            lightningLastStrikeDist_list = jsonpath_lightningLastStrikeDist.find(device)
            jsonpath_lightningLastStrikeDist_uom = parse("$.sensors[?sensor_code='LightningLastStrikeDist'].chart_unit")
            lightningLastStrikeDist_list_uom = jsonpath_lightningLastStrikeDist_uom.find(device)
            self.setDriver('GV6', lightningLastStrikeDist_list[0].value, True)
            LOGGER.debug('Device Name: {}, Sensor Lightning Last Strike Distance: {} {}'.format(deviceName,
                                                                                                lightningLastStrikeDist_list[
                                                                                                    0].value,
                                                                                                lightningLastStrikeDist_list_uom[
                                                                                                    0].value))

            jsonpath_lightningClosestStrikeDist = parse(
                "$.sensors[?sensor_code='LightningClosestStrikeDist'].last_reading_value")
            lightningClosestStrikeDist_list = jsonpath_lightningClosestStrikeDist.find(device)
            jsonpath_lightningClosestStrikeDist_uom = parse(
                "$.sensors[?sensor_code='LightningClosestStrikeDist'].chart_unit")
            lightningClosestStrikeDist_list_uom = jsonpath_lightningClosestStrikeDist_uom.find(device)
            self.setDriver('GV8', lightningClosestStrikeDist_list[0].value, True)
            LOGGER.debug('Device Name: {}, Sensor Lightning Closest Strike Distance: {} {}'.format(deviceName,
                                                                              lightningClosestStrikeDist_list[0].value,
                                                                              lightningClosestStrikeDist_list_uom[
                                                                                  0].value))
        else:
            self.setDriver('GV5', 0, True)
            self.setDriver('GV6', 0, True)
            self.setDriver('GV8', 0, True)

        try:
            if deviceLastCheckIn is not None and deviceLastCheckIn != '':
                lastCheckInDateTime = datetime.fromisoformat(deviceLastCheckIn)
                currentDateTimeInUtc = datetime.now(timezone.utc)
                deltaDateTime = currentDateTimeInUtc - lastCheckInDateTime
                numOfMins = self.convert_timedelta_min(deltaDateTime)
                self.setDriver('GV3', numOfMins, True)
            else:
                self.setDriver('GV3', 0, True)
        except Exception as ex:
            LOGGER.error('AcuriteLightningTNode - Error in update', ex)

    id = 'acuritelightningt'

    drivers = [{'driver': 'CLITEMP', 'value': 0, 'uom': '17'},
               {'driver': 'GV4', 'value': 0, 'uom': '17'}, # Heat Index / Feels Like
               {'driver': 'CLIHUM', 'value': 0, 'uom': '22'},
               {'driver': 'BARPRES', 'value': 0, 'uom': '23'},
               {'driver': 'DEWPT', 'value': 0, 'uom': '17'},
               {'driver': 'GV1', 'value': 0, 'uom': '25'}, # device battery
               {'driver': 'GV2', 'value': 0, 'uom': '25'}, # device status
               {'driver': 'GV3', 'value': 0, 'uom': '45'}, # last checkin time
               {'driver': 'GV5', 'value': 0, 'uom': '0'}, # lightning Strike Cnt
               {'driver': 'GV6', 'value': 0, 'uom': '116'}, # lightning Last Strike Dist
               {'driver': 'GV8', 'value': 0, 'uom': '116'}] # lightning Closest Strike Dist
