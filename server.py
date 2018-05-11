#!/usr/bin/python3

from os import listdir
from os.path import isfile, join
import tornado.web
import tornado.ioloop
import random
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
        self.facts = self.get_facts()

    def get_facts(self):
        mypath = '/home/ubuntu/ram-pup/facts'
        files = {}
        for directory in os.listdir(mypath):
            dirpath = mypath + "/" + directory
            files[directory] = [join(dirpath, f) for f in listdir(dirpath) if isfile(join(dirpath, f))]
        logger.info("We have the files {}".format(files))

        facts_dict = {}
        for category, facts in files.items():
            fact_text = []
            for fact in facts:
                with open(fact, 'r') as f:
                    fact_text.append(f.read())
            facts_dict[category] = fact_text
        logger.info("We have the fact contents {}".format(facts_dict))
        # do stuff
        #vim_facts = ["test stuff here", " fact 2"]
        #other_facts = ["other stuff", " stuff 2"]
        #facts = {"vim": vim_facts, "other": other_facts}
        return facts_dict

    def get(self):
        logger.info("Get request {}".format(self.request.body))
        self.write("{}".format(self.facts))

    def get(self, *args, **kwargs):
        logger.info("Get request {} with args {} and kwargs {}".format(self.request.body, args, kwargs))
        if args[0] in self.facts.keys():
            self.write("{}".format(random.choice(self.facts[args[0]])))
        else:
            self.write("No fact pack found for {}. Please contribute at...".format(args[0]))


def shutdown(sig, frame):
    """Stop the process."""
    logging.warning("Shutting down")
    tornado.ioloop.IOLoop.current().stop()


def main():
    setup_logging()
    fact_app = tornado.web.Application([("/facts/(.*)", FactHandler), ])
    LISTEN_PORT = 8080
    fact_app.listen(LISTEN_PORT, address='127.0.0.1')
    logger.info("Listening on port %d", LISTEN_PORT)

    signal.signal(signal.SIGINT, shutdown)

    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
