#!/usr/bin/env python3
"""
Polyglot v3 node server Daikin Interface
Copyright (C) 2021 James Paul
"""
import udi_interface
import sys

LOGGER = udi_interface.LOGGER
LOG_HANDLER = udi_interface.LOG_HANDLER;

from nodes import AcuriteController
from nodes import AcuriteDeviceNode

import logging

if __name__ == "__main__":
    try:
        LOG_HANDLER.set_basic_config(True, logging.DEBUG)
        polyglot = udi_interface.Interface([AcuriteController, AcuriteDeviceNode])
        polyglot.start()
        control = AcuriteController(polyglot, 'controller', 'controller', 'Acurite Controller')
        polyglot.runForever()
    except (KeyboardInterrupt, SystemExit):
        polyglot.stop()
        sys.exit(0)
    except Exception as err:
        LOGGER.error('Excption: {0}'.format(err), exc_info=True)
        sys.exit(0)