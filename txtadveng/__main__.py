# pylint: disable=unused-import
import readline
from argparse import ArgumentParser

from . import DISPLAY as display
from .adventure import Adventure
from .helper import load_config, Display, set_levels

set_levels("?", ">")

display.setVerbosity(2)
display.debug("really debug world", verbosity=3)
display.debug("debug world", verbosity=2)
display.info("hello world", verbosity=1)
print()

parser = ArgumentParser(prog="txtadveng", description="text adventure engine")
parser.add_argument("story", help="yaml file with story info")
args = parser.parse_args()

config = load_config(args.story)
story = Adventure(config)
story.run()
