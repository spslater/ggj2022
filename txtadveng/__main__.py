# pylint: disable=unused-import
import readline
from argparse import ArgumentParser

from .adventure import Adventure
from .helper import load_config, set_levels, DISPLAY as display

set_levels("?", "")
parser = ArgumentParser(prog="txtadveng", description="text adventure engine")
parser.add_argument("story", help="yaml file with story info")
parser.add_argument(
    "-v",
    "--verbose",
    action="count",
    default=0,
    help="set the level of output verbosity",
)
args = parser.parse_args()


display.setVerbosity(args.verbose)
display.debug("verbose level: %s", args.verbose)

config = load_config(args.story)
story = Adventure(config)
story.run()
