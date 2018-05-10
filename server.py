#!/usr/bin/python3

import tornado.web
import tornado.ioloop
import signal
import time
import os
import sys
import logging

logger = logging.getLogger(__name__)
def setup_logging(logdir='log'):
    logger = logging.getLogger()
    if not logger.handlers:
        # Create stdout and file outputs
        stdout_handler = logging.StreamHandler(sys.stdout)
        os.makedirs(logdir, exist_ok=True)
        file_handler = logging.FileHandler("{}/debug.log".format(logdir))

        # Add a timestamp
        short_formatter = logging.Formatter(fmt="%(asctime)s UTC %(levelname)s: %(message)s",
                                            datefmt="%H:%M:%S")
        long_formatter = logging.Formatter(fmt="%(asctime)s.%(msecs)03d UTC %(levelname)s "
                                               "%(filename)s:%(lineno)d: %(message)s",
                                           datefmt="%Y-%m-%d %H:%M:%S")
        short_formatter.converter = time.gmtime
        long_formatter.converter = time.gmtime
        stdout_handler.setFormatter(short_formatter)
        file_handler.setFormatter(long_formatter)

        # File output should always be debug level. stdout is configurable.
        # The logger object itself always needs to be set to debug level or it
        # will absorb low-level logs before the handlers can decide whether to
        # log or not.
        logger.setLevel(logging.DEBUG)
        file_handler.setLevel(logging.DEBUG)
        #if verbose:
        #    stdout_handler.setLevel(logging.DEBUG)
        #else:
        stdout_handler.setLevel(logging.INFO)

        logger.addHandler(stdout_handler)
        logger.addHandler(file_handler)


class FactHandler(tornado.web.RequestHandler):
    """ catch gets, get facts"""
    def initialize(self):
        facts = get_facts()

    def get_facts():
        facts = {"test card": "test stuff here"}

    def get(self):
        logger.info("Get request {}".format(self.request.body))


def on_shutdown(sig, frame):
    """Schedules the RPE process to shut down when signal sig is received."""
    logging.warning("Received signal %s, schedule shutdown", sig)
    tornado.ioloop.IOLoop.current().add_callback(shutdown)


def main():
    setup_logging()
    fact_app = tornado.web.Application([("/facts", FactHandler), ])
    LISTEN_PORT = 8080
    fact_app.listen(LISTEN_PORT, address='127.0.0.1')
    logger.info("Listening on port %d", LISTEN_PORT)

    signal.signal(signal.SIGINT, on_shutdown)

    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
