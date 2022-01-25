import readline
from argparse import ArgumentParser

from .adventure import Adventure
from .helper import load_config

parser = ArgumentParser(prog="txtadveng", description="text adventure engine")
parser.add_argument("story", help="yaml file with story info")
args = parser.parse_args()

config = load_config(args.story)
story = Adventure(config)
story.run()
