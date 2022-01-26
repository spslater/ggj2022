"""Helpful methods used throughout the project"""
import logging
from sys import stdout

import yaml


def load_config(filename):
    """load the text adventure from config file"""
    with open(filename, "r", encoding="utf-8") as fp:
        return yaml.load(fp, Loader=yaml.FullLoader)


def response(*args):
    """display game response"""
    logging.info(" ".join([str(a) for a in args]))


def debug(*args):
    """display a debug message"""
    logging.debug(" ".join([str(a) for a in args]))


def set_levels(debug=None, info=None, warning=None, error=None, critical=None):
    """Set the displayed 'level name' for different level"""
    if debug is not None:
        logging.addLevelName(logging.DEBUG, debug)
    if info is not None:
        logging.addLevelName(logging.INFO, info)
    if warning is not None:
        logging.addLevelName(logging.WARNING, warning)
    if error is not None:
        logging.addLevelName(logging.ERROR, error)
    if critical is not None:
        logging.addLevelName(logging.CRITICAL, critical)


class Display:
    def __init__(self, verbosity=0):
        self.verbosity = verbosity
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler(stdout)
        handler.setFormatter(logging.Formatter("%(levelname)s %(message)s"))
        self.logger.addHandler(handler)

    # pylint: disable=invalidName
    def setVerbosity(self, value):
        """change the verbosity level for the output"""
        self.verbosity = int(value)

    def debug(self, *args, verbosity=-1, **kwargs):
        """debug level logging if it is above the current verbosity level"""
        if verbosity <= self.verbosity:
            self.logger.debug(*args, **kwargs)

    def info(self, *args, verbosity=-1, **kwargs):
        """info level logging if it is above the current verbosity level"""
        if verbosity <= self.verbosity:
            self.logger.info(*args, **kwargs)

    def warning(self, *args, verbosity=-1, **kwargs):
        """warning level logging if it is above the current verbosity level"""
        if verbosity <= self.verbosity:
            self.logger.warning(*args, **kwargs)

    def error(self, *args, verbosity=-1, **kwargs):
        """error level logging if it is above the current verbosity level"""
        if verbosity <= self.verbosity:
            self.logger.error(*args, **kwargs)

    def critical(self, *args, verbosity=-1, **kwargs):
        """critical level logging if it is above the current verbosity level"""
        if verbosity <= self.verbosity:
            self.logger.critical(*args, **kwargs)
