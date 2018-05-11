#!/usr/bin/python3

from os import listdir
from os.path import isfile, join
from urllib.parse import parse_qs
import tornado.web
import tornado.ioloop
import random
import signal
import time
import os
import sys
import logging

COUNTER = 0

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
        stdout_handler.setLevel(logging.INFO)

        logger.addHandler(stdout_handler)
        logger.addHandler(file_handler)


class FactHandler(tornado.web.RequestHandler):
    """catch gets, get facts"""
    def initialize(self):
        self.facts = self.get_facts()

    def get_facts(self):
        logger.info("Generating list of facts from disk")
        mypath = '/home/ubuntu/ram-pup/facts'
        files = {}
        for directory in os.listdir(mypath):
            logger.debug("Getting files for dir {}".format(directory))
            dirpath = mypath + "/" + directory
            files[directory] = [join(dirpath, f) for f in listdir(dirpath) if isfile(join(dirpath, f))]
            logger.debug("Got files {} for dir {}".format(files[directory], directory))

        logger.debug("We have the files {}".format(files))

        facts_dict = {}
        for category, facts in files.items():
            fact_text = []
            for fact in facts:
                with open(fact, 'r') as f:
                    fact_text.append(f.read())
            facts_dict[category] = fact_text
        logger.debug("We have the fact contents {}".format(facts_dict))
        return facts_dict

    def get(self, *args, **kwargs):
        global COUNTER
        COUNTER += 1
        logger.debug("Incoming request {}".format(self.request.uri))
        logger.info("Request count {}".format(COUNTER))

        url_params = parse_qs(self.request.uri)
        logger.debug("parsed out args \n {} \n \n ".format(url_params))

        if 'text' in url_params.keys():
            logger.info("Request is asking for facts on {}".format(url_params['text'][0]))
            if url_params['text'][0] == "count":
                self.write("{} requests have been served since this server last catasrophilcally failed/was restarted".format(COUNTER))
                return
            if url_params['text'][0] in self.facts.keys():
                try:
                    self.write("{}".format(random.choice(self.facts[url_params['text'][0]])))
                except IndexError:
                    self.write("No facts have been submitted to this fact pack yet. :sadparrot:")
            else:
                self.write("No fact pack found for {}. Soon you will be able to contribute facts through git.".format(url_params['text'][0]))
        else:
            self.write("Current fact packs available are: {}".format([key for key in self.facts.keys()]))

def shutdown(sig, frame):
    """Stop the process."""
    logger.info("Shutting down")
    tornado.ioloop.IOLoop.current().stop()


def main():
    setup_logging()
    fact_app = tornado.web.Application([("/facts/(.*)", FactHandler), ])
    LISTEN_PORT = 8081
    fact_app.listen(LISTEN_PORT, address='0.0.0.0')
    logger.info("Listening on port %d", LISTEN_PORT)

    signal.signal(signal.SIGINT, shutdown)

    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
