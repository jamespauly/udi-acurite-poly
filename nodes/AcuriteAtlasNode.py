from datetime import datetime, timezone
from jsonpath_ng import jsonpath
from jsonpath_ng.ext import parse

import udi_interface
from enums import DeviceStatus, BatteryLevel

LOGGER = udi_interface.LOGGER
Custom = udi_interface.Custom


class AcuriteAtlasNode(udi_interface.Node):
    def __init__(self, polyglot, primary, address, name, device):
        super(AcuriteAtlasNode, self).__init__(polyglot, primary, address, name)
        LOGGER.debug("Initialize AcuriteAtlasNode")
        self.poly.subscribe(self.poly.START, self.start, address)
        self.initDevice = device

    def start(self):
        LOGGER.debug("AcuriteAtlasNode - start")
        self.update(self.initDevice)

    def query(self):
        LOGGER.info('AcuriteAtlasNode - query')

    def convert_timedelta_min(self, duration):
        days, seconds = duration.days, duration.seconds
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        # seconds = (seconds % 60)
        return (days * 24 * 60) + (hours * 60) + minutes

    def update(self, device):
        LOGGER.debug("AcuriteAtlasNode - update")
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
            'Device Name: {}, Sensor Barometric Pressure: {} {}'.format(deviceName, barometric_pressure_list[0].value,
                                                                        barometric_pressure_list_uom[0].value))

        jsonpath_wind_direction = parse("$.sensors[?sensor_code='Wind Direction'].last_reading_value")
        wind_direction_list = jsonpath_wind_direction.find(device)
        jsonpath_wind_direction_uom = parse("$.sensors[?sensor_code='Wind Direction'].chart_unit")
        wind_direction_list_uom = jsonpath_wind_direction_uom.find(device)
        self.setDriver('WINDDIR', wind_direction_list[0].value, True)
        LOGGER.debug('Device Name: {}, Sensor Wind Direction: {} {}'.format(deviceName, wind_direction_list[0].value,
                                                                            wind_direction_list_uom[0].value))

        jsonpath_wind_speed = parse("$.sensors[?sensor_code='Wind Speed'].last_reading_value")
        wind_speed_list = jsonpath_wind_speed.find(device)
        jsonpath_wind_speed_uom = parse("$.sensors[?sensor_code='Wind Speed'].chart_unit")
        wind_speed_list_uom = jsonpath_wind_speed_uom.find(device)
        self.setDriver('SPEED', wind_speed_list[0].value, True)
        LOGGER.debug('Device Name: {}, Sensor Wind Speed: {} {}'.format(deviceName, wind_speed_list[0].value,
                                                                        wind_speed_list_uom[0].value))

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

        jsonpath_rainfall = parse("$.sensors[?sensor_code='Rainfall'].last_reading_value")
        rainfall_list = jsonpath_rainfall.find(device)
        jsonpath_rainfall_uom = parse("$.sensors[?sensor_code='Rainfall'].chart_unit")
        rainfall_list_uom = jsonpath_rainfall_uom.find(device)
        self.setDriver('RAINRT', rainfall_list[0].value, True)
        LOGGER.debug(
            'Device Name: {}, Sensor Rainfall: {} {}'.format(deviceName, rainfall_list[0].value,
                                                             rainfall_list_uom[0].value))

        jsonpath_lightintensity = parse("$.sensors[?sensor_code='LightIntensity'].last_reading_value")
        lightintensity_list = jsonpath_lightintensity.find(device)
        jsonpath_lightintensity_uom = parse("$.sensors[?sensor_code='LightIntensity'].chart_unit")
        lightintensity_list_uom = jsonpath_lightintensity_uom.find(device)
        self.setDriver('LUMIN', lightintensity_list[0].value, True)
        LOGGER.debug('Device Name: {}, Sensor LightIntensity: {} {}'.format(deviceName, lightintensity_list[0].value,
                                                                            lightintensity_list_uom[0].value))

        jsonpath_uvindex = parse("$.sensors[?sensor_code='UVIndex'].last_reading_value")
        uvindex_list = jsonpath_uvindex.find(device)
        jsonpath_uvindex_uom = parse("$.sensors[?sensor_code='UVIndex'].chart_unit")
        uvindex_list_uom = jsonpath_uvindex_uom.find(device)
        self.setDriver('UV', uvindex_list[0].value, True)
        LOGGER.debug(
            'Device Name: {}, Sensor UVIndex: {} {}'.format(deviceName, uvindex_list[0].value,
                                                            uvindex_list_uom[0].value))

        jsonpath_windspeedavg = parse("$.sensors[?sensor_code='WindSpeedAvg'].last_reading_value")
        windspeedavg_list = jsonpath_windspeedavg.find(device)
        jsonpath_windspeedavg_uom = parse("$.sensors[?sensor_code='WindSpeedAvg'].chart_unit")
        windspeedavg_list_uom = jsonpath_windspeedavg_uom.find(device)
        self.setDriver('GV7', windspeedavg_list[0].value, True)
        LOGGER.debug('Device Name: {}, Sensor WindSpeedAvg: {} {}'.format(deviceName, windspeedavg_list[0].value,
                                                                          windspeedavg_list_uom[0].value))

        jsonpath_lightningStrikeCnt = parse("$.wired_sensors[?sensor_code='LightningStrikeCnt'].last_reading_value")
        lightningStrikeCnt_list = jsonpath_lightningStrikeCnt.find(device)

        if len(lightningStrikeCnt_list) > 0 and int(lightningStrikeCnt_list[0].value) > 0:
            jsonpath_lightningStrikeCnt_uom = parse("$.wired_sensors[?sensor_code='LightningStrikeCnt'].chart_unit")
            lightningStrikeCnt_list_uom = jsonpath_lightningStrikeCnt_uom.find(device)
            self.setDriver('GV5', lightningStrikeCnt_list[0].value, True)
            LOGGER.debug(
                'Device Name: {}, Sensor Lightning Strike Count: {} {}'.format(deviceName,
                                                                               lightningStrikeCnt_list[0].value,
                                                                               lightningStrikeCnt_list_uom[0].value))

            jsonpath_lightningLastStrikeDist = parse(
                "$.wired_sensors[?sensor_code='LightningLastStrikeDist'].last_reading_value")
            lightningLastStrikeDist_list = jsonpath_lightningLastStrikeDist.find(device)
            jsonpath_lightningLastStrikeDist_uom = parse("$.wired_sensors[?sensor_code='LightningLastStrikeDist'].chart_unit")
            lightningLastStrikeDist_list_uom = jsonpath_lightningLastStrikeDist_uom.find(device)
            self.setDriver('GV6', lightningLastStrikeDist_list[0].value, True)
            LOGGER.debug('Device Name: {}, Sensor Lightning Last Strike Distance: {} {}'.format(deviceName,
                                                                                                lightningLastStrikeDist_list[
                                                                                                    0].value,
                                                                                                lightningLastStrikeDist_list_uom[
                                                                                                    0].value))

            jsonpath_lightningClosestStrikeDist = parse(
                "$.wired_sensors[?sensor_code='LightningClosestStrikeDist'].last_reading_value")
            lightningClosestStrikeDist_list = jsonpath_lightningClosestStrikeDist.find(device)
            jsonpath_lightningClosestStrikeDist_uom = parse(
                "$.wired_sensors[?sensor_code='LightningClosestStrikeDist'].chart_unit")
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
            LOGGER.error('AcuriteAtlasNode - Error in update', ex)

    id = 'acuriteatlas'

    drivers = [{'driver': 'CLITEMP', 'value': 0, 'uom': '17'},
               {'driver': 'GV4', 'value': 0, 'uom': '17'},
               {'driver': 'CLIHUM', 'value': 0, 'uom': '22'},
               {'driver': 'BARPRES', 'value': 0, 'uom': '23'},
               {'driver': 'DEWPT', 'value': 0, 'uom': '17'},
               {'driver': 'GV1', 'value': 0, 'uom': '25'},
               {'driver': 'GV2', 'value': 0, 'uom': '25'},
               {'driver': 'GV3', 'value': 0, 'uom': '45'},
               {'driver': 'WINDDIR', 'value': 0, 'uom': '14'},
               {'driver': 'SPEED', 'value': 0, 'uom': '48'},
               {'driver': 'RAINRT', 'value': 0, 'uom': '120'},
               {'driver': 'LUMIN', 'value': 0, 'uom': '36'},
               {'driver': 'UV', 'value': 0, 'uom': '71'},
               {'driver': 'GV5', 'value': 0, 'uom': '56'},
               {'driver': 'GV6', 'value': 0, 'uom': '116'},
               {'driver': 'GV8', 'value': 0, 'uom': '116'},
               {'driver': 'GV7', 'value': 0, 'uom': '48'}]
