#!/usr/bin/env python3
"""
Polyglot v3 node server Daikin Interface
Copyright (C) 2021 James Paul
"""
import udi_interface
import sys

LOGGER = udi_interface.LOGGER
LOG_HANDLER = udi_interface.LOG_HANDLER;

from nodes import AcuriteController, AcuriteAtlasNode, AcuriteDeviceNode

if __name__ == "__main__":
    try:
        LOGGER.debug("Staring Poly Interface")
        polyglot = udi_interface.Interface([AcuriteController, AcuriteDeviceNode, AcuriteAtlasNode])
        polyglot.start()
        control = AcuriteController(polyglot, 'controller', 'controller', 'Acurite Hub')
        polyglot.runForever()
    except (KeyboardInterrupt, SystemExit):
        polyglot.stop()
        sys.exit(0)
    except Exception as err:
        LOGGER.error('Excption: {0}'.format(err), exc_info=True)
        sys.exit(0)
