from argparse import ArgumentParser

from .helper import debug, load_config, response
from .player import Player
from .room import Map
from .verb import Action

parser = ArgumentParser(prog="txtadveng", description="text adventure engine")
parser.add_argument("story", help="yaml file with story info")
args = parser.parse_args()

config = load_config(args.story)

player = Player(**config["player"])
worldmap = Map(config["rooms"], config["start"], config["map"])
acts = Action(config["verbs"])
player.location = worldmap.get_room(worldmap.start)

response(config["intro"])
while True:
    verb, noun = acts("Action? ")
    if verb is None:
        response("sorry, i do know that command")
        continue

    if verb == "quit":
        response("thanks for playing!")
        break

    if verb == "move":
        room = worldmap.move(player.location, noun)
        if room:
            player.move(room)
        else:
            response("no room in that direction")
        continue

    if verb == "look":
        player.look(noun)
        continue

    if verb == "take":
        item, outcome = player.take(noun)
        continue

    if verb == "use":
        debug(f"using at '{noun}'")
        continue
