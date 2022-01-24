"""Helpful methods used throughout the project"""
import yaml


def load_config(filename):
    """load the text adventure from config file"""
    with open(filename, "r", encoding="utf-8") as fp:
        return yaml.load(fp, Loader=yaml.FullLoader)


def response(*args, **kwargs):
    """display game response"""
    print("> ", *args, **kwargs)


def debug(*args, **kwargs):
    """display a debug message"""
    print("? ", *args, **kwargs)
