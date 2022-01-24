import re

from .helper import response, debug
from .item import get_item
from .player import Player
from .room import Map


class Similar:
    def __init__(self, primary, synonyms):
        self.name = primary
        syns = "|".join([primary] + synonyms)
        self.pattern = re.compile(r"(" + syns + r")\s*(?P<token>.*)?")

    def __call__(self, string):
        if match := self.pattern.match(string):
            return match.group("token")
        return None


class Synonyms:
    def __init__(self, config):
        self.config = config
        for primary, synonyms in self.config.items():
            setattr(self, primary, Similar(primary, synonyms))

    def __call__(self, primary, string):
        if similar := getattr(self, primary, None):
            return similar(string)
        return None


class Adventure:
    def __init__(self, config):
        self.config = config

        self.player = Player(**self.config["player"])
        self.worldmap = Map(
            self.config["rooms"],
            self.config["start"],
            self.config["map"],
        )
        self.acts = Synonyms(self.config["synonyms"])

        self.location = self.worldmap.get_room(self.worldmap.start)

        names = "|".join(config.get("inventory", ["self"]))
        self.inventory = re.compile(r"(?P<verb>(" + names + r"))\s*(?P<nouns>.*)?")

    def _start(self):
        response(self.config["intro"])
        self.location.enter()

    def _end(self):
        pass

    @staticmethod
    def _quit():
        response("thanks for playing!")

    def _move(self, loc):
        if room := self.worldmap.move(self.location, loc):
            self.location.exit()
            self.location = room.enter()
        else:
            response("no room in that direction")

    def _look(self, name):
        # look at an item in the current room or inventory
        if (match := self.acts("inventory", name)) is not None:
            if item_name := match.group("nouns"):
                if item := get_item(self.items, item_name):
                    response(f"You look at {item_name}")
                    if outcome := item(self, "look"):
                        debug(outcome)
                    return
                response(f"Sorry, there is no '{item_name}' in your inventory.")
            elif items := self.items.keys():
                names = ", ".join(items)
                response(f"You look at the things you are carrying: {names}")
            else:
                response("You have no items right now.")

        # look around room or at specific item
        if self.acts("around", name) is not None:
            response("You look around the room again.")
            self.location.look("around")
            return

        if item := get_item(self.location.items, name):
            response(f"You look at {name}")
            if outcome := item("look"):
                debug(outcome)
            return
        response(f"Sorry, there is no item with the name '{name}' in the room.")


    def _take(self, noun):
        item, outcome = self.player.take(noun)

    def _use(self, noun):
        debug(f"using at '{noun}'")

    def run(self):
        """run the adventure"""
        self._start()
        while True:
            res = input("Action? ")
            if self.acts("quit", res) is not None:
                self._quit()
                break
            elif (loc := self.acts("move", res)) is not None:
                self._move(loc)
            elif (name := self.acts("look", res)) is not None:
                self._look(name)
            elif (noun := self.acts("take", res)) is not None:
                self._take(noun)
            elif (noun := self.acts("use", res)) is not None:
                self._use(noun)
            else:
                response("sorry, i do know that command")
        self._end()
